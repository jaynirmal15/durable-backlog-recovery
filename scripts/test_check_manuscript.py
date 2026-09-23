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


class MissingEndBound(unittest.TestCase):
    """The defect class: a slice whose end bound falls back to end-of-file.

    It shipped once -- 726 words of drafting notes typeset inside reference
    [14] on page 20 of the published article -- so every parser that had the
    shape now raises instead of falling back, and every one of those raises is
    asserted here. The rule is one line: A MISSING END BOUND RAISES.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='bounds-')
        for d in ('paper', 'figures'):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(self.tmp, d))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def strip_rule(self, rel):
        """Remove the own-line `---` that bounds a file's header."""
        p = os.path.join(self.tmp, rel)
        lines = open(p, encoding='utf-8').read().split('\n')
        for i, l in enumerate(lines):
            if l.strip() == '---':
                del lines[i]
                break
        open(p, 'w', encoding='utf-8').write('\n'.join(lines))
        return p

    def test_body_of_raises_when_the_header_has_no_end(self):
        p = self.strip_rule(os.path.join('paper', 'section5.md'))
        lines = open(p, encoding='utf-8').readlines()
        with self.assertRaises(C.ScopeError):
            C.body_of(lines, True, p)

    def test_body_of_still_returns_whole_files_that_have_no_header(self):
        # skip_header=False is a stated choice, not a fallback: figures/ and
        # scripts/ files carry no change log. It must keep working.
        lines = ['one\n', 'two\n']
        self.assertEqual(len(C.body_of(lines, False)), 2)

    def test_reference_blocks_bounds_the_last_entry(self):
        blocks, problems = C.reference_blocks()
        self.assertEqual(problems, [])
        self.assertEqual(len(blocks), 14)
        sizes = [len(b) for _, b in blocks]
        # The bug made the last entry 4,719 characters against a 1,020 max.
        self.assertLess(sizes[-1], 1200, 'last entry ran past its own end')
        self.assertLess(max(sizes), 1200)

    def test_reference_blocks_raises_when_nothing_closes_the_last_entry(self):
        p = os.path.join(self.tmp, 'paper', 'references.md')
        t = open(p, encoding='utf-8').read()
        cut = t.rindex('\n**[14]**')
        # Keep the entries, delete every own-line --- and ## below them.
        head, tail = t[:cut], t[cut:]
        tail = '\n'.join(l for l in tail.split('\n')
                         if l.strip() != '---' and not l.startswith('## '))
        open(p, 'w', encoding='utf-8').write(head + tail)
        old = C.PAPER
        C.PAPER = os.path.join(self.tmp, 'paper')
        try:
            with self.assertRaises(C.ScopeError):
                C.reference_blocks()
        finally:
            C.PAPER = old

    def test_plan_sync_bounds_the_last_plan(self):
        import re as _re
        o = open(os.path.join(ROOT, 'paper', 'OUTLINE.md'), encoding='utf-8').read()
        heads = list(_re.finditer(r'^## \u00a7(\d{1,2}) [^\n]*$', o, _re.M))
        allh = [m.start() for m in _re.finditer(r'^## ', o, _re.M)]
        last = heads[-1]
        after = [s for s in allh if s > last.start()]
        self.assertTrue(after, 'the last plan must be closed by another ## ')
        # Unbounded it ran 9,566 characters to end of file.
        self.assertLess(after[0] - last.start(), 3000)

    def test_plan_sync_raises_when_the_last_plan_is_the_last_heading(self):
        p = os.path.join(self.tmp, 'paper', 'OUTLINE.md')
        t = open(p, encoding='utf-8').read()
        import re as _re
        heads = list(_re.finditer(r'^## \u00a7(\d{1,2}) [^\n]*$', t, _re.M))
        tail = t[heads[-1].start():]
        tail = '\n'.join(l for l in tail.split('\n') if not l.startswith('## ')
                         or l.startswith('## \u00a7'))
        open(p, 'w', encoding='utf-8').write(t[:heads[-1].start()] + tail)
        old = C.PAPER
        C.PAPER = os.path.join(self.tmp, 'paper')
        try:
            with self.assertRaises(C.ScopeError):
                C.plan_sync()
        finally:
            C.PAPER = old


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




class CrossReferenceCase(unittest.TestCase):
    """Check 6: literal float references and dangling section references.

    The defect it was written for shipped. SS-VI-C said "Table 8" through the
    cut pass, the deposit and a published Zenodo record, because check 5 looks
    only at keyed references and a literal is the one kind that can go stale.
    Three more had gone the same way in Supplement S1's headings. Each test
    plants one of those four shapes.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='checkxref-')
        for d in ('paper', 'figures'):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(self.tmp, d))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def read(self, rel):
        with open(os.path.join(self.tmp, rel), encoding='utf-8') as fh:
            return fh.read()

    def edit(self, rel, old, new):
        text = self.read(rel)
        self.assertEqual(text.count(old), 1,
                         'fixture drift: %r appears %d times in %s'
                         % (old, text.count(old), rel))
        with open(os.path.join(self.tmp, rel), 'w', encoding='utf-8') as fh:
            fh.write(text.replace(old, new))

    def problems(self):
        return '\n'.join('%s %s' % p for p in C.cross_references(self.tmp))

    def test_clean_tree_is_clean(self):
        self.assertEqual(C.cross_references(self.tmp), [])

    def test_literal_float_reference_is_reported(self):
        self.edit(os.path.join('paper', 'section6.md'),
                  'The factors that appear in §IX-D and Supplement',
                  'The factors that appear in Table 8 and Supplement')
        self.assertIn('literal float reference', self.problems())

    def test_section_that_does_not_exist_is_reported(self):
        self.edit(os.path.join('paper', 'section6.md'),
                  'The reportable statement is about detectability',
                  'As §XI shows. The reportable statement is about detectability')
        self.assertIn('no section XI', self.problems())

    def test_subsection_removed_by_the_cut_is_reported(self):
        self.edit(os.path.join('paper', 'section6.md'),
                  'The reportable statement is about detectability',
                  'As §V-G shows. The reportable statement is about detectability')
        self.assertIn('§V-G', self.problems())

    def test_marker_exempts_historical_text(self):
        self.edit(os.path.join('paper', 'section6.md'),
                  'The factors that appear in §IX-D and Supplement',
                  '<!-- xref-ok: quoting the retired number -->\n'
                  'The factors that appear in Table 8 and Supplement')
        self.assertEqual(C.cross_references(self.tmp), [])

    def test_apparatus_in_the_captions_file_is_not_scanned(self):
        # The header legitimately says "Fig. 2" while explaining the keying
        # rule. Scanning it would force an exemption on apparatus, which is how
        # a check stops meaning anything.
        self.assertNotIn('CAPTIONS.md', self.problems())


class RetiredAggregatePhrases(unittest.TestCase):
    """B1: "within 1%" and "within 0.7%" as seven-cell formulations.

    SS-VI-B's own policy sentence forbids a range spanning the seven cells, and
    four places asserted one anyway. Both adversarial reviews found it
    independently, which is what a phrase list is for.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='checkagg-')
        shutil.copytree(os.path.join(ROOT, 'paper'),
                        os.path.join(self.tmp, 'paper'))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.path = os.path.join(self.tmp, 'paper', 'section10.md')

    def plant(self, text, marker=''):
        with open(self.path, encoding='utf-8') as fh:
            body = fh.read()
        old = 'lay at or near measured service'
        self.assertEqual(body.count(old), 1)
        with open(self.path, 'w', encoding='utf-8') as fh:
            fh.write(body.replace(old, marker + text))

    def test_retired_phrases_are_in_the_list(self):
        listed = [p for p, _ in C.WITHDRAWN]
        self.assertIn('within 1%', listed)
        self.assertIn('within 0.7%', listed)

    def test_live_occurrence_fails(self):
        self.plant('lay within 1% of measured service')
        hits = C.phrase_hits(self.path, True)
        self.assertTrue(any(h[2] == 'within 1%' for h in hits), hits)

    def test_marked_historical_occurrence_passes(self):
        self.plant('lay within 1% of measured service',
                   '<!-- withdrawn-quote-ok: historical -->\n')
        hits = C.phrase_hits(self.path, True)
        self.assertFalse([h for h in hits if h[2] == 'within 1%'], hits)




class SemanticRegistryCase(unittest.TestCase):
    """Check 7: a registered value may appear only where its key is named.

    All three mechanical defects of these two review passes were the same
    failure -- a value staying numerically correct while crossing an estimator,
    population, denominator or operation boundary. These tests plant that
    crossing in each of the shapes it actually took.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='checksem-')
        for d in ('paper', 'figures'):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(self.tmp, d))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def read(self, rel):
        with open(os.path.join(self.tmp, rel), encoding='utf-8') as fh:
            return fh.read()

    def edit(self, rel, old, new):
        text = self.read(rel)
        self.assertEqual(text.count(old), 1,
                         'fixture drift: %r appears %d times in %s'
                         % (old, text.count(old), rel))
        with open(os.path.join(self.tmp, rel), 'w', encoding='utf-8') as fh:
            fh.write(text.replace(old, new))

    def problems(self):
        return '\n'.join('%s %s' % p for p in C.semantic_registry(self.tmp))

    def test_clean_tree_is_clean(self):
        self.assertEqual(C.semantic_registry(self.tmp), [])

    def test_a_delta_without_its_load_condition_is_reported(self):
        self.edit(SEC5, '| at saturation | 0.4947 ms | 0.4914 ms |',
                  '| the other pair | 0.4947 ms | 0.4914 ms |')
        self.assertIn('0.4947 appears without naming its condition',
                      self.problems())

    def test_a_gap_whose_row_loses_its_estimator_is_reported(self):
        # The row is read against its own header, not against the whole table.
        # Grouped, the delivery-span row would have excused this one.
        self.edit(SEC5, '| drain-window, utilisation | 0.0670 | 0.0032 | 95% |',
                  '| utilisation | 0.0670 | 0.0032 | 95% |')
        blob = self.problems()
        self.assertIn('0.0670 appears without naming its estimator', blob)
        self.assertIn('0.0032 appears without naming its estimator', blob)

    def test_the_crossed_partition_is_reported(self):
        # Exactly the A5 defect as it shipped: 1.29 us printed as the
        # complement of 99.81% without saying the timer sits outside delta.
        self.edit(SEC5,
                  'The timer read is measured\noutside `\u03b4`; adding it brings '
                  'those remainders to 1.29 and 1.38 \u00b5s.',
                  'Queue and slot bookkeeping and the completion signal\n'
                  'contribute 1.29 and 1.38 \u00b5s.')
        self.assertIn('1.29 and 1.38', self.problems())

    def test_marker_exempts_a_displayed_calculation(self):
        self.assertNotIn('semantic-ok', self.problems())
        self.assertEqual(C.semantic_registry(self.tmp), [])

    def test_table_rows_are_read_against_their_own_header(self):
        paras = C.paragraphs_of([(1, '| a | b |\n'), (2, '|---|---|\n'),
                                 (3, '| x | 1 |\n'), (4, '| y | 2 |\n')])
        bodies = [p for p in paras if len(p) == 2]
        self.assertEqual(len(bodies), 2)
        for p in bodies:
            self.assertEqual(p[0][0], 1)


class RegisteredTextIsOutOfPhraseScope(unittest.TestCase):
    """The three registered addenda are immutable, so the phrase list skips them.

    Marking live registered prose `withdrawn-quote-ok` would label it a
    historical quotation, which it is not. A stated scope is auditable; a false
    label is not.
    """

    def test_registration_files_are_not_phrase_targets(self):
        names = [os.path.basename(p) for p, _ in C.targets()]
        for reg in C.REGISTERED:
            self.assertNotIn(reg, names)

    def test_they_still_exist_and_still_contain_the_retired_word(self):
        # If this stops being true the exclusion is dead weight and should go.
        path = os.path.join(ROOT, 'paper', 'A8-registration.md')
        self.assertTrue(os.path.isfile(path))
        with open(path, encoding='utf-8') as fh:
            self.assertIn('prospective', fh.read())


if __name__ == '__main__':
    unittest.main(verbosity=2)
