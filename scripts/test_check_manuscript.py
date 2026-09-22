#!/usr/bin/env python3
"""Failure tests for check 5, the keyed figure and table references.

WHY THESE EXIST. Check 5 was written because check 4 -- the citation markers --
matched [@key] with a character class that excludes the colon, so every
[@fig:...] and [@tab:...] fell through it in silence. The keyed float pass was
unvalidated and nothing said so. A check added to fix a silent gap is worth
nothing until its failure modes are exercised, because the failure that matters
is the one where the check prints "clean." over a real defect.

Each test copies the live tree, breaks exactly one thing, and asserts that the
specific breakage is reported. The clean tree is asserted clean first, so a test
that passes because the tree was already broken cannot hide here.

  python3 scripts/test_check_manuscript.py
"""
import os
import re
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_manuscript as C  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTIONS = os.path.join('figures', 'CAPTIONS.md')
SEC4 = os.path.join('paper', 'section4.md')
SEC5 = os.path.join('paper', 'section5.md')
T2 = os.path.join('figures', 'T2-resolution.md')
S1 = 'supplement-S1.md'


class FloatKeyCase(unittest.TestCase):
    """A scratch copy of paper/ and figures/, broken one way at a time."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='checkman-')
        for d in ('paper', 'figures'):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(self.tmp, d))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    # -- helpers ----------------------------------------------------------
    def run_check(self):
        return C.float_keys(self.tmp)[0]

    def read(self, rel):
        with open(os.path.join(self.tmp, rel), encoding='utf-8') as fh:
            return fh.read()

    def write(self, rel, text):
        with open(os.path.join(self.tmp, rel), 'w', encoding='utf-8') as fh:
            fh.write(text)

    def edit(self, rel, old, new, count=1):
        text = self.read(rel)
        self.assertEqual(text.count(old), count,
                         'fixture drift: %r appears %d times in %s, expected %d'
                         % (old, text.count(old), rel, count))
        self.write(rel, text.replace(old, new))

    def assertReports(self, needle):
        problems = self.run_check()
        blob = '\n'.join('%s %s' % p for p in problems)
        self.assertTrue(problems, 'expected a problem, got none')
        self.assertIn(needle, blob)
        return blob

    # -- the baseline -----------------------------------------------------
    def test_the_live_tree_is_clean(self):
        # Every test below asserts a break against THIS. If the tree were
        # already failing, each of them would pass for the wrong reason.
        self.assertEqual(self.run_check(), [])

    # -- key -> caption ---------------------------------------------------
    def test_key_with_no_caption_block(self):
        self.edit(CAPTIONS, '<!-- caption:fig:signals:start -->',
                  '<!-- caption:fig:typo-here:start -->')
        self.edit(CAPTIONS, '<!-- caption:fig:signals:end -->',
                  '<!-- caption:fig:typo-here:end -->')
        blob = self.assertReports('no caption block carries that key')
        self.assertIn('[@fig:signals]', blob)

    def test_two_caption_blocks_for_one_key(self):
        text = self.read(CAPTIONS)
        text += ('\n<!-- caption:tab:accounting:start -->\nA second one.\n'
                 '<!-- caption:tab:accounting:end -->\n')
        self.write(CAPTIONS, text)
        self.assertReports('has 2 caption blocks')

    def test_caption_that_never_closes(self):
        self.edit(CAPTIONS, '<!-- caption:tab:candidates:end -->',
                  '<!-- caption:tab:candidates:done -->')
        self.assertReports('never properly')

    # -- scopes: the article and Supplement S1 ----------------------------
    def test_the_s1_floats_are_not_counted_in_the_article_census(self):
        # The ruled census is the ARTICLE's. S1's three floats must not leak
        # into it, or moving a float to the supplement would look like losing
        # one -- which is exactly what the cut pass does on purpose.
        problems, order, floats, counts = C.float_keys(self.tmp)
        self.assertEqual(problems, [])
        self.assertEqual(counts['article'], (C.FLOAT_FIGURES, C.FLOAT_TABLES))
        self.assertEqual(counts['s1'], (1, 2))

    def test_the_article_may_not_reference_an_s1_float(self):
        # A cross-document reference would print a number the article does not
        # assign. §III's removed Fig. 2 reference is the live instance: put it
        # back and the checker must object rather than silently numbering it.
        self.edit(os.path.join('paper', 'section3.md'),
                  'The worker\'s cycle, however, is longer than the service time it',
                  'The worker\'s cycle ([@fig:capacity-model]), however, is longer '
                  'than the service time it')
        self.assertReports('cannot number the other')

    def test_s1_may_not_reference_an_article_float(self):
        self.edit(os.path.join('paper', S1),
                  '## S1-C.',
                  'See [@tab:accounting].\n\n## S1-C.')
        self.assertReports('cannot number the other')

    def test_dropping_the_s1_suffix_moves_a_float_into_the_article(self):
        # The suffix IS the declaration. Losing it must break the census, not
        # pass quietly with eight article tables again.
        self.edit(os.path.join('paper', S1),
                  '<!-- table:tab:s1-amendments:s1 -->',
                  '<!-- table:tab:s1-amendments -->')
        blob = self.assertReports('census')
        self.assertIn('the article has 8 tables', blob)

    def test_caption_nobody_references(self):
        text = self.read(CAPTIONS)
        text += ('\n<!-- caption:tab:orphan:start -->\nNobody cites this.\n'
                 '<!-- caption:tab:orphan:end -->\n'
                 '<!-- table:tab:orphan -->\n| a |\n|---|\n| b |\n')
        self.write(CAPTIONS, text)
        self.assertReports('nothing references')

    # -- key -> float -----------------------------------------------------
    def test_key_with_no_float(self):
        self.edit(T2, '<!-- table:tab:resolution -->', '')
        blob = self.assertReports('no float carries that key')
        self.assertIn('[@tab:resolution]', blob)

    def test_two_floats_for_one_key(self):
        self.edit(T2, '<!-- table:tab:resolution -->',
                  '<!-- table:tab:resolution -->\n| x |\n|---|\n'
                  '<!-- table:tab:resolution -->')
        self.assertReports('has 2 floats')

    def test_figure_bound_to_a_file_that_is_not_there(self):
        self.edit(CAPTIONS, 'F5-collapse.pdf', 'F5-collapse-v2.pdf')
        self.assertReports('is not in figures/')

    def test_table_marker_not_followed_by_a_table(self):
        self.edit(SEC5, '<!-- table:tab:accounting -->',
                  '<!-- table:tab:accounting -->\n\nA stray paragraph.\n')
        self.assertReports('not followed by a pipe table')

    # -- float -> prose ---------------------------------------------------
    def test_float_nobody_references(self):
        # T3's "Sources, cell by cell" table is the real instance of this
        # class: artefact documentation that must stay out of the article. It
        # is excluded by carrying no marker. Give it one and the check objects.
        self.edit(os.path.join('figures', 'T3-candidate-explanations.md'),
                  '## Sources, cell by cell',
                  '## Sources, cell by cell\n\n<!-- table:tab:sources -->')
        self.assertReports('an unreferenced float has no number to print')

    # -- the census -------------------------------------------------------
    def test_losing_a_table_fails_the_census(self):
        self.edit(SEC5, '<!-- table:tab:a8-replication -->', '')
        blob = self.assertReports('census')
        self.assertIn('the article has 6 tables', blob)

    def test_losing_a_figure_fails_the_census(self):
        self.edit(CAPTIONS, '<!-- figure:fig:overhead:F3-overhead-measured.pdf -->', '')
        blob = self.assertReports('census')
        self.assertIn('the article has 4 figures', blob)

    # -- markers are syntax, not substrings (item 37) ----------------------
    def test_a_marker_named_in_prose_is_not_a_marker(self):
        # The defect this project has now committed three times: a mechanism
        # defeated by the sentence describing it. A paragraph that names the
        # marker must not create a float.
        self.edit(SEC5, '<!-- table:tab:accounting -->',
                  'The build selects it with a <!-- table:tab:invented --> '
                  'marker.\n\n<!-- table:tab:accounting -->')
        problems = self.run_check()
        self.assertEqual(problems, [],
                         'a marker named inside a sentence was counted: %s'
                         % problems)

    def test_an_indented_marker_still_counts(self):
        # Own-line means own line, not column zero: leading whitespace is
        # still a marker, and dropping it would be a silent under-count.
        self.edit(SEC5, '<!-- table:tab:accounting -->',
                  '  <!-- table:tab:accounting -->')
        self.assertEqual(self.run_check(), [])


class WhyCheckFiveExists(unittest.TestCase):
    """The gap that motivated it, asserted rather than described."""

    def test_check_four_still_ignores_colon_keys(self):
        # Not a defect to fix in check 4: [@fig:...] is a DIFFERENT namespace
        # from [@little]. This asserts the boundary, so that if someone later
        # widens check 4's character class, the overlap is noticed here.
        pat = re.compile(r'\[@([A-Za-z0-9][A-Za-z0-9._-]*)\]')
        self.assertIsNone(pat.search('[@fig:harness]'))
        self.assertIsNotNone(pat.search('[@little]'))

    def test_check_five_claims_exactly_the_colon_keys(self):
        pat = re.compile(r'\[@((?:fig|tab):[A-Za-z0-9][A-Za-z0-9._-]*)\]')
        self.assertEqual(pat.search('[@tab:resolution]').group(1),
                         'tab:resolution')
        self.assertIsNone(pat.search('[@little]'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
