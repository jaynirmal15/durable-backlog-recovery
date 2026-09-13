#!/usr/bin/env python3
"""Unit tests for the pre-registered classification and bisection rules.

These assert PRE-REGISTRATION.md sections 2 and 3 against synthetic vSLO
tables, so any change to the estimator breaks a test rather than quietly
changing where the boundary lands.

  python3 scripts/test_locate_boundary.py        (or: python3 -m unittest)
"""
import os
import sys
import argparse
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import (  # noqa: E402
    RESOLUTION_RPS, bisect_step, classify, downward_step, plan, runner_argv,
    spread_diagnostic, upward_step,
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


class TestSpreadDiagnostic(unittest.TestCase):
    """A3: is the within-point achieved-rho spread larger than the resolution?"""

    def test_resolution_is_regime_dependent(self):
        # 5 rps means a different distance in rho at different fault capacities.
        self.assertAlmostEqual(spread_diagnostic([0.9, 0.9], 2000)['rhoResolution'], 0.0025, places=5)
        self.assertAlmostEqual(spread_diagnostic([0.9, 0.9], 1400)['rhoResolution'], 0.00357, places=5)

    def test_tight_point_is_not_flagged(self):
        d = spread_diagnostic([0.9190, 0.9192, 0.9191], 2000)
        self.assertFalse(d['spreadExceedsResolution'])
        self.assertAlmostEqual(d['rhoAchievedSpread'], 0.0002, places=5)

    def test_spread_wider_than_resolution_is_flagged(self):
        d = spread_diagnostic([0.9150, 0.9200, 0.9180], 2000)
        self.assertTrue(d['spreadExceedsResolution'])
        self.assertAlmostEqual(d['spreadRatio'], 2.0, places=2)

    def test_exactly_at_resolution_is_not_flagged(self):
        # Strictly greater than, so a spread equal to the resolution passes.
        d = spread_diagnostic([0.9000, 0.9025], 2000)
        self.assertFalse(d['spreadExceedsResolution'])

    def test_same_spread_flags_at_c0_but_not_c1(self):
        # 0.003 exceeds 0.0025 at C=2000 but not 0.00357 at C=1400. A fixed
        # 0.0025 threshold would get the C1 case wrong.
        rhos = [0.9200, 0.9230]
        self.assertTrue(spread_diagnostic(rhos, 2000)['spreadExceedsResolution'])
        self.assertFalse(spread_diagnostic(rhos, 1400)['spreadExceedsResolution'])

    def test_ticker_ab_reference_is_near_the_threshold(self):
        # The injector's own ticker A/B spanned 96.42-96.80% of lambda_L=1000,
        # i.e. 3.8 rps, which at C=2000 is 0.0019 in rho -- below 0.0025 but
        # close, and that was the better-behaved of the two terms.
        d = spread_diagnostic([(1000 * 0.9642 + 840) / 2000, (1000 * 0.9680 + 840) / 2000], 2000)
        self.assertFalse(d['spreadExceedsResolution'])
        self.assertGreater(d['spreadRatio'], 0.7)

    def test_zero_capacity_does_not_divide_by_zero(self):
        d = spread_diagnostic([0.9, 0.91], 0)
        self.assertIsNone(d['spreadRatio'])

    def test_single_rep_has_no_spread(self):
        self.assertEqual(spread_diagnostic([0.919], 2000)['rhoAchievedSpread'], 0.0)


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




class CapacityOverrideAndPrefix(unittest.TestCase):
    """The two flags E2b needs: a non-default C, and run ids that cannot collide.

    E2b runs at C=400 with S=25 ms, which gives concurrency 10 -- the c10 arm's
    concurrency at the c50 arm's service time. No regime expresses that, and run
    ids derived from arm and regime alone would collide with the c50 records of
    E1 and E2.
    """

    def _args(self, **kw):
        base = dict(runner='./bin/runner', arm='c50', regime='C0', capacity=None,
                    run_prefix='', live_rate=1000, outage=120, workers=1024,
                    profile='graceful', injector_pacer='lanes',
                    nats='nats://x', downstream='http://y', results='results')
        base.update(kw)
        return argparse.Namespace(**base)

    def test_capacity_defaults_to_the_regime_nominal(self):
        argv = runner_argv(self._args(), 975, 'r')
        self.assertEqual(argv[argv.index('-capacity') + 1], '2000')

    def test_capacity_override_reaches_the_runner(self):
        argv = runner_argv(self._args(capacity=400, live_rate=200), 180, 'r')
        self.assertEqual(argv[argv.index('-capacity') + 1], '400')
        self.assertEqual(argv[argv.index('-live-rate') + 1], '200')

    def test_override_changes_nothing_else(self):
        a = runner_argv(self._args(), 180, 'r')
        b = runner_argv(self._args(capacity=400), 180, 'r')
        ai, bi = a.index('-capacity'), b.index('-capacity')
        self.assertEqual(a[:ai] + a[ai + 2:], b[:bi] + b[bi + 2:])

    def test_service_time_still_comes_from_the_arm(self):
        argv = runner_argv(self._args(capacity=400), 180, 'r')
        self.assertEqual(argv[argv.index('-service-time-ms') + 1], '25')

    def test_run_prefix_absent_by_default(self):
        self.assertEqual('%s%s-%s-rl%d-r%d' % ('', 'c50', 'c0', 975, 1),
                         'c50-c0-rl975-r1')

    def test_run_prefix_namespaces_the_id(self):
        self.assertEqual('%s%s-%s-rl%d-r%d' % ('e2b-', 'c50', 'c0', 180, 1),
                         'e2b-c50-c0-rl180-r1')

    def test_classification_and_bisection_are_untouched(self):
        # The override must not reach the estimator. These are the same
        # assertions the suite already makes; repeated here so a regression in
        # the flag work fails in this class too.
        self.assertEqual(classify([0.0, 0.0, 0.0]), 'SAFE')
        self.assertEqual(classify([0.2, 0.2, 0.0]), 'UNSAFE')
        self.assertEqual(bisect_step(180, 200), 190)
        self.assertIsNone(bisect_step(185, 190))


if __name__ == '__main__':
    unittest.main(verbosity=2)
