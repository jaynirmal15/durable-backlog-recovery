#!/usr/bin/env python3
"""Unit tests for the pre-registered classification and bisection rules.

These assert PRE-REGISTRATION.md sections 2 and 3 against synthetic vSLO
tables, so any change to the estimator breaks a test rather than quietly
changing where the boundary lands.

  python3 scripts/test_locate_boundary.py        (or: python3 -m unittest)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import (  # noqa: E402
    RESOLUTION_RPS, bisect_step, classify, downward_step, plan, upward_step,
)


class TestClassify(unittest.TestCase):
    """Section 2: SAFE / UNSAFE / MARGINAL."""

    def test_all_clean_is_safe(self):
        self.assertEqual(classify([0.0, 0.0, 0.0]), 'SAFE')

    def test_at_the_safe_threshold_is_safe(self):
        self.assertEqual(classify([0.01, 0.01, 0.01]), 'SAFE')

    def test_one_run_just_over_the_safe_threshold_is_not_safe(self):
        # 0.011 > 0.01 but nothing exceeds 0.05, so MARGINAL, not SAFE.
        self.assertEqual(classify([0.0, 0.0, 0.011]), 'MARGINAL')

    def test_two_runs_over_the_unsafe_threshold_is_unsafe(self):
        self.assertEqual(classify([0.0, 0.06, 0.07]), 'UNSAFE')

    def test_unsafe_beats_safe_even_with_a_clean_third_run(self):
        # The dangerous case: averaging these gives 0.28 and hides that two of
        # three runs collapsed. The rule must not average.
        self.assertEqual(classify([0.0, 0.42, 0.40]), 'UNSAFE')

    def test_one_collapsed_run_alone_is_marginal(self):
        # Disagreement, not a verdict. One run over 0.05 is not enough.
        self.assertEqual(classify([0.0, 0.0, 0.9]), 'MARGINAL')

    def test_exactly_at_the_unsafe_threshold_is_not_unsafe(self):
        # 0.05 is not > 0.05; these are MARGINAL because they exceed 0.01.
        self.assertEqual(classify([0.05, 0.05, 0.05]), 'MARGINAL')

    def test_between_the_thresholds_is_marginal(self):
        self.assertEqual(classify([0.02, 0.03, 0.04]), 'MARGINAL')

    def test_the_historical_855_case_is_marginal(self):
        # Phase 1 rl=855: mean 0.006, one run 0.013. Reported as a "marginal
        # band" then; the rule now says MARGINAL explicitly rather than SAFE.
        self.assertEqual(classify([0.0, 0.005, 0.013]), 'MARGINAL')

    def test_two_repetitions_still_classify(self):
        self.assertEqual(classify([0.0, 0.0]), 'SAFE')
        self.assertEqual(classify([0.9, 0.9]), 'UNSAFE')

    def test_empty_input_is_an_error(self):
        with self.assertRaises(ValueError):
            classify([])


class TestBisectStep(unittest.TestCase):
    """Section 3: midpoints, 5 rps rounding, and the stopping rule."""

    def test_midpoint_is_rounded_to_five(self):
        self.assertEqual(bisect_step(840, 900), 870)
        self.assertEqual(bisect_step(840, 870), 855)

    def test_odd_interval_rounds_to_a_multiple_of_five(self):
        mid = bisect_step(841, 900)
        self.assertEqual(mid % RESOLUTION_RPS, 0)
        self.assertTrue(841 < mid < 900)

    def test_stops_at_the_resolution_floor(self):
        self.assertIsNone(bisect_step(840, 845))
        self.assertIsNone(bisect_step(840, 840))

    def test_six_rps_interval_still_probes(self):
        mid = bisect_step(840, 846)
        self.assertIsNotNone(mid)
        self.assertTrue(840 < mid < 846)

    def test_midpoint_stays_strictly_inside(self):
        for lo, hi in [(100, 107), (380, 390), (290, 300), (1, 9)]:
            mid = bisect_step(lo, hi)
            if mid is not None:
                self.assertTrue(lo < mid < hi, '%d not inside (%d,%d)' % (mid, lo, hi))

    def test_upward_step_is_ten_percent_rounded_to_five(self):
        self.assertEqual(upward_step(840), 925)   # +84.0 -> 85 on the 5 rps grid
        self.assertEqual(upward_step(380), 420)   # +38.0 -> 40
        self.assertEqual(upward_step(290), 320)   # +29.0 -> 30
        self.assertEqual(upward_step(10), 15)     # +1.0 -> 0, raised to the 5 rps floor


class TestDownwardExtension(unittest.TestCase):
    """Amendment A2: an anchor that is not SAFE becomes the ceiling."""

    @staticmethod
    def oracle(last_safe):
        return lambda rl: 'SAFE' if rl <= last_safe else 'UNSAFE'

    def test_downward_step_is_ten_percent_rounded_to_five(self):
        self.assertEqual(downward_step(840), 755)
        self.assertEqual(downward_step(380), 340)
        self.assertEqual(downward_step(10), 5)

    def test_downward_step_never_goes_below_the_floor(self):
        self.assertGreaterEqual(downward_step(5), RESOLUTION_RPS)

    def test_non_safe_anchor_descends_and_brackets(self):
        # The c50 case the 2026-08-19 notes predict: the Phase 1 anchor does not
        # survive the fix, so the search must go down before it can bracket.
        seq, lo, hi = plan(380, oracle=self.oracle(300))
        self.assertEqual(seq[0]['phase'], 'anchor')
        self.assertEqual(seq[0]['class'], 'UNSAFE')
        self.assertTrue(any(p['phase'] == 'downward' for p in seq))
        self.assertLessEqual(hi - lo, RESOLUTION_RPS)
        self.assertTrue(lo <= 300 < hi, 'boundary 300 not bracketed by [%s,%s]' % (lo, hi))

    def test_anchor_far_above_the_boundary_still_converges(self):
        seq, lo, hi = plan(840, oracle=self.oracle(290))
        self.assertLessEqual(hi - lo, RESOLUTION_RPS)
        self.assertTrue(lo <= 290 < hi)

    def test_marginal_anchor_also_descends(self):
        o = lambda rl: 'MARGINAL' if rl == 380 else ('SAFE' if rl <= 340 else 'UNSAFE')
        seq, lo, hi = plan(380, oracle=o)
        self.assertEqual(seq[0]['class'], 'MARGINAL')
        self.assertIsNotNone(lo)
        self.assertLessEqual(hi - lo, RESOLUTION_RPS)

    def test_no_safe_point_anywhere_yields_no_floor(self):
        seq, lo, hi = plan(100, oracle=lambda rl: 'UNSAFE', max_probes=8)
        self.assertIsNone(lo)

    def test_safe_anchor_does_not_descend(self):
        seq, lo, hi = plan(840, hi=900, oracle=self.oracle(865))
        self.assertFalse(any(p['phase'] in ('anchor', 'downward') for p in seq))


class TestSearchPlan(unittest.TestCase):
    """Section 3 end to end, against an oracle that knows the true boundary."""

    @staticmethod
    def oracle_with_boundary(last_safe, marginal=()):
        def f(rl):
            if rl in marginal:
                return 'MARGINAL'
            return 'SAFE' if rl <= last_safe else 'UNSAFE'
        return f

    def test_converges_to_the_true_boundary(self):
        seq, lo, hi = plan(840, hi=900, oracle=self.oracle_with_boundary(865))
        self.assertLessEqual(hi - lo, RESOLUTION_RPS)
        self.assertTrue(lo <= 865 < hi, 'boundary 865 not bracketed by [%d,%d]' % (lo, hi))

    def test_marginal_lowers_the_ceiling(self):
        # 855 is MARGINAL; it must end up inside the interval (i.e. at or above
        # the ceiling), never treated as a safe floor.
        seq, lo, hi = plan(840, hi=870, oracle=self.oracle_with_boundary(869, marginal=(855,)))
        self.assertLessEqual(lo, 855)
        self.assertLessEqual(hi, 870)
        classes = {p['rl']: p['class'] for p in seq}
        if 855 in classes:
            self.assertEqual(classes[855], 'MARGINAL')
            self.assertLessEqual(hi, 855)

    def test_upward_search_finds_a_ceiling(self):
        seq, lo, hi = plan(840, hi=None, oracle=self.oracle_with_boundary(1000))
        self.assertIsNotNone(hi)
        self.assertTrue(any(p['phase'] == 'upward' for p in seq))
        self.assertLessEqual(hi - lo, RESOLUTION_RPS)
        self.assertTrue(lo <= 1000 < hi)

    def test_terminates_and_stays_bounded(self):
        seq, lo, hi = plan(100, hi=1000, oracle=self.oracle_with_boundary(437))
        self.assertLess(len(seq), 24)
        self.assertLessEqual(hi - lo, RESOLUTION_RPS)
        self.assertTrue(lo <= 437 < hi)

    def test_every_probe_is_a_multiple_of_five(self):
        seq, _, _ = plan(840, hi=1000, oracle=self.oracle_with_boundary(913))
        for p in seq:
            self.assertEqual(p['rl'] % RESOLUTION_RPS, 0, 'probe %d is not on the 5 rps grid' % p['rl'])

    def test_dry_run_plan_shows_the_first_probe_only(self):
        seq, lo, hi = plan(840, hi=None, oracle=None)
        self.assertEqual(len(seq), 1)
        self.assertEqual(seq[0]['phase'], 'upward')
        self.assertIsNone(seq[0]['class'])

    def test_all_safe_within_the_probe_budget_gives_no_ceiling(self):
        seq, lo, hi = plan(100, hi=None, oracle=lambda rl: 'SAFE', max_probes=5)
        self.assertIsNone(hi)


if __name__ == '__main__':
    unittest.main(verbosity=2)
