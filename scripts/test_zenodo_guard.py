#!/usr/bin/env python3
"""Tests for the two gates on the published record: --plan-only and --publish-edit.

WHAT THESE PROTECT. A published Zenodo record cannot be deleted and its files
cannot be changed outside a 30-day window, so the cost of a wrong publish is
permanent. --publish-edit is the only publish path in the deposit script and
refuses on seven conditions; --plan-only exists because two of those seven are
post-upload facts and so cannot gate anything before the upload.

THE PROPERTY THAT MATTERS MOST is the one asserted last here: running
--plan-only must not make --publish-edit easier. A review step that unlocks
something is a step people learn to skip, and a gate that can be satisfied by
running a command is not a gate.

  python3 scripts/test_zenodo_guard.py
"""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zenodo_deposit as Z  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FakeAPI(object):
    """Stands in for Zenodo. Records every verb it is asked for."""

    def __init__(self, state='done', files=None):
        self.calls = []
        self.state = state
        self.files = files if files is not None else [
            {'filename': k, 'filesize': n, 'checksum': 'md5:%032x' % i}
            for i, (k, n) in enumerate(
                [('README.md', 10), ('LICENSE', 11),
                 ('PRE-REGISTRATION.md', 12), ('MANIFEST.json', 13),
                 ('article.pdf', 14), ('supplement-S1.pdf', 15),
                 ('pkg.zip', 16)])]

    def __call__(self, url, token, method='GET', **kw):
        self.calls.append((method, url.split('?')[0].rsplit('/api', 1)[-1]))
        if Z.READ_ONLY[0] and method != 'GET':
            raise Z.WouldWrite('%s attempted in a read-only mode' % method)
        if url.endswith('/files'):
            return 200, self.files
        return 200, {'state': self.state, 'submitted': self.state != 'unsubmitted',
                     'doi': '10.5281/zenodo.99', 'created': '2026-09-23',
                     'metadata': {'publication_date': '2026-09-23'}}


class PlanOnly(unittest.TestCase):

    def setUp(self):
        self.real = Z.request
        self.api = FakeAPI()
        Z.request = self.api
        self.addCleanup(lambda: setattr(Z, 'request', self.real))
        self.addCleanup(lambda: Z.READ_ONLY.__setitem__(0, False))
        self.stage = os.path.join(ROOT, 'scripts')       # any real directory
        self.archive = os.path.abspath(__file__)         # any real file

    def run_plan(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = Z.plan_only(Z.LIVE, 'tok', 99, self.stage, self.archive)
        return rc, buf.getvalue()

    def test_it_issues_get_and_nothing_else(self):
        rc, out = self.run_plan()
        verbs = {m for m, _ in self.api.calls}
        self.assertTrue(self.api.calls, 'it made no request at all')
        self.assertEqual(verbs, {'GET'}, 'a non-GET verb was issued: %s' % verbs)

    def test_a_write_inside_it_raises_rather_than_falling_through(self):
        # The guard is in request(), so a write added to this mode later --
        # by someone who did not read its docstring -- cannot reach the wire.
        Z.READ_ONLY[0] = True
        with self.assertRaises(Z.WouldWrite):
            Z.request(Z.LIVE + '/deposit/depositions/99/actions/publish',
                      'tok', 'POST')
        Z.READ_ONLY[0] = False

    def test_the_flag_is_cleared_even_if_the_plan_raises(self):
        def boom(*a, **k):
            raise RuntimeError('mid-plan failure')
        Z.request = boom
        with self.assertRaises(RuntimeError):
            Z.plan_only(Z.LIVE, 'tok', 99, self.stage, self.archive)
        self.assertFalse(Z.READ_ONLY[0],
                         'read-only leaked past a failure and would block writes')

    def test_it_always_exits_non_zero(self):
        rc, out = self.run_plan()
        self.assertNotEqual(rc, 0, 'plan-only must never read as success')

    def test_it_prints_every_key_with_both_sides_and_a_verdict(self):
        rc, out = self.run_plan()
        for key in ('README.md', 'LICENSE', 'PRE-REGISTRATION.md',
                    'MANIFEST.json', 'article.pdf', 'supplement-S1.pdf'):
            self.assertIn(key, out, '%s missing from the plan' % key)
        self.assertIn('live', out)
        self.assertIn('staged', out)
        self.assertIn('would be replaced', out)

    def test_it_writes_nothing_to_disk(self):
        before = {}
        for d in (ROOT, os.path.join(ROOT, 'scripts')):
            before[d] = sorted(os.listdir(d))
        self.run_plan()
        for d, names in before.items():
            self.assertEqual(sorted(os.listdir(d)), names,
                             'plan-only created or removed a file in %s' % d)


class PlanOnlyUnlocksNothing(unittest.TestCase):
    """The property the whole design rests on."""

    def setUp(self):
        self.real = Z.request
        self.addCleanup(lambda: setattr(Z, 'request', self.real))
        self.addCleanup(lambda: Z.READ_ONLY.__setitem__(0, False))
        self.stage = os.path.join(ROOT, 'scripts')
        self.archive = os.path.abspath(__file__)

    def test_publish_edit_still_refuses_after_plan_only_has_run(self):
        api = FakeAPI(state='done')          # published, no edit open
        Z.request = api
        buf = io.StringIO()
        with redirect_stdout(buf):
            Z.plan_only(Z.LIVE, 'tok', 99, self.stage, self.archive)
            rc = Z.publish_edit(Z.LIVE, 'tok', 99, '10.5281/zenodo.99',
                                self.stage, self.archive, confirm=True)
        out = buf.getvalue()
        self.assertNotEqual(rc, 0,
                            'publish_edit succeeded after plan_only ran')
        self.assertIn('REFUSED', out)
        self.assertIn('inprogress', out,
                      'it must still refuse on the state condition')

    def test_plan_only_leaves_no_state_for_publish_edit_to_find(self):
        # No flag file, no cache, no module-level memo: the only thing
        # plan_only may leave behind is the cleared READ_ONLY flag.
        api = FakeAPI(state='done')
        Z.request = api
        before = {k: v for k, v in vars(Z).items()
                  if not k.startswith('__') and not callable(v)}
        with redirect_stdout(io.StringIO()):
            Z.plan_only(Z.LIVE, 'tok', 99, self.stage, self.archive)
        after = {k: v for k, v in vars(Z).items()
                 if not k.startswith('__') and not callable(v)}
        self.assertEqual(set(before), set(after),
                         'plan_only introduced module state')
        self.assertFalse(Z.READ_ONLY[0])


class PublishEditRefuses(unittest.TestCase):

    def setUp(self):
        self.real = Z.request
        self.addCleanup(lambda: setattr(Z, 'request', self.real))
        self.stage = os.path.join(ROOT, 'scripts')
        self.archive = os.path.abspath(__file__)

    def refuse(self, **kw):
        Z.request = FakeAPI(**kw)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = Z.publish_edit(Z.LIVE, 'tok', 99, '10.5281/zenodo.99',
                                self.stage, self.archive, confirm=True)
        return rc, buf.getvalue()

    def test_refuses_an_unpublished_draft(self):
        rc, out = self.refuse(state='unsubmitted')
        self.assertNotEqual(rc, 0)
        self.assertIn('never been published', out)

    def test_refuses_when_no_edit_is_open(self):
        rc, out = self.refuse(state='done')
        self.assertNotEqual(rc, 0)
        self.assertIn('inprogress', out)

    def test_refuses_a_wrong_doi_even_with_confirm(self):
        Z.request = FakeAPI(state='inprogress')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = Z.publish_edit(Z.LIVE, 'tok', 99, '10.5281/zenodo.WRONG',
                                self.stage, self.archive, confirm=True)
        self.assertNotEqual(rc, 0)
        self.assertIn('expect-doi', buf.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=2)
