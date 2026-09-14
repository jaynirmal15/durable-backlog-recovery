#!/usr/bin/env python3
"""Matched before/after accounting for the inter-arm gap. Its only job.

Section 5 states 0.0706 uncorrected against 0.0026 corrected, "94-96% removed".
The two numbers come from different analysis paths. This establishes what each
one actually is, whether they are matched on numerator definition, denominator,
aggregator and observation interval, and -- since they are not -- recomputes the
comparison under one recipe applied identically to both corpora.

The matched recipe, chosen to be computable on both sides without changing any
historical estimator:

    numerator     achieved rate at the LAST SAFE point only (A6: the estimator
                  is invalid at collapsed points, so no UNSAFE endpoint enters)
    estimator     drain-window as-measured, on both sides
    aggregator    median across repetitions
    denominator   configured C = 2000
    interval      the drain window, on both sides
    comparison    c10 arm against c50 arm, one cell each, matched conditions
                  (C0, lambda_L = 1000, C = 2000)

Read-only. Usage: python3 scripts/effect_size_accounting.py
"""
import collections
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_analysis import achieved, C_D                 # noqa: E402
from locate_boundary import classify                   # noqa: E402

A4E2E = json.load(open('results/E2E-a4.json'))
CAL = json.load(open('results/E2D-capacity-calibration.json'))
E2E = json.load(open('results/E2E-analysis.json'))
SEVEN = [
    ('E1 c10/C0', 'results/boundaries/c10-C0.json'),
    ('E1 c10/C1', 'results/boundaries/c10-C1.json'),
    ('E1 c50/C0', 'results/boundaries/c50-C0.json'),
    ('E1 c50/C1', 'results/boundaries/c50-C1.json'),
    ('E2 c10@Q2500', 'results/e2/c10-Q2500/boundaries/c10-C0.json'),
    ('E2 c50@Q500', 'results/e2/c50-Q500/boundaries/c50-C0.json'),
    ('E2b C=400', 'results/e2b/boundaries/c50-C0.json'),
]


def hr(t):
    print()
    print('=' * 78)
    print(t)
    print('=' * 78)


def last_safe(bpath):
    b = json.load(open(bpath))
    lo = b['boundary']['lastSafeRl']
    return b, next(p for p in b['points'] if p['rl'] == lo)


def e2e_last_safe(arm):
    by = collections.defaultdict(list)
    for p in sorted(glob.glob('results/e2e/e2e-%s-c0-rl*-r*.json' % arm)):
        rec = json.load(open(p))
        by[rec['params']['rateLimitRps']].append(rec)
    safe = [(rl, rs) for rl, rs in by.items()
            if classify([r['vSLO'] for r in rs]) == 'SAFE']
    rl, rs = max(safe, key=lambda x: x[0])
    return rl, [achieved(r) for r in rs]


def main():
    out = {}

    hr('1. WHAT EACH PUBLISHED NUMBER ACTUALLY IS')
    mids = {}
    for label, path in SEVEN:
        b = json.load(open(path))
        iv = b['boundary']['rhoStarInterval']
        mids[label] = (iv[0] + iv[1]) / 2
    spread = max(mids.values()) - min(mids.values())
    hi = max(mids, key=mids.get)
    lo = min(mids, key=mids.get)
    print('0.0706 -- traced to capacity_calibration.py:221,')
    print('    rhoStarSpread = max(midpoints) - min(midpoints) over ALL SEVEN cells.')
    print('    recomputed: %.4f   (max %s %.4f, min %s %.4f)'
          % (spread, hi, mids[hi], lo, mids[lo]))
    print('    It is a RANGE over seven heterogeneous cells, not a two-arm gap.')
    print()
    print('    Each midpoint = (min(rho at last SAFE), max(rho at first non-SAFE)) / 2,')
    print('    under A4, so every one of them includes a COLLAPSED endpoint --')
    print('    exactly the values A6 ruled invalid.')
    print()
    print('    E2E-REPORT.md:79 labels 0.0706 "E1 midpoints 0.9137 and 0.9826".')
    print('    Those two midpoints differ by %.4f, not 0.0706. The label is wrong;'
          % (mids['E1 c50/C0'] - mids['E1 c10/C0']))
    print('    the number is the seven-cell range.')
    print()
    g = E2E['cells']
    print('0.0026 -- the difference between TWO cells\' bracket midpoints,')
    print('    c50 %.4f minus c10 %.4f = %.4f,'
          % (g['c50']['bracket']['rhoMid'], g['c10']['bracket']['rhoMid'],
             g['c50']['bracket']['rhoMid'] - g['c10']['bracket']['rhoMid']))
    print('    under the DRAIN-WINDOW estimator, median aggregator.')
    out['published'] = {
        'uncorrected': 0.0706, 'uncorrectedIs': 'range of rho* midpoints over seven cells, A4',
        'corrected': round(g['c50']['bracket']['rhoMid'] - g['c10']['bracket']['rhoMid'], 4),
        'correctedIs': 'difference of two bracket midpoints, drain-window',
    }

    hr('2. ARE THEY MATCHED?')
    rows = [
        ('numerator definition', 'interval midpoint (SAFE and non-SAFE endpoints)',
         'interval midpoint (SAFE and non-SAFE endpoints)', 'matched'),
        ('estimator', 'A4, delivery span', 'drain-window as-measured', 'NOT MATCHED'),
        ('observation interval', 'the delivery span', 'tDrainSec', 'NOT MATCHED'),
        ('aggregator', 'min at one end, max at the other', 'median at both ends',
         'NOT MATCHED'),
        ('denominator', 'configured C (2000/1400/400)', 'configured C (2000)',
         'partially - three different C values on one side'),
        ('statistic', 'RANGE over seven cells', 'DIFFERENCE between two cells',
         'NOT MATCHED'),
        ('collapsed endpoints', 'included (A6-invalid)', 'included', 'matched, both invalid'),
    ]
    print('%-22s %-34s %-32s %s' % ('dimension', 'uncorrected 0.0706',
                                    'corrected 0.0026', 'verdict'))
    for a, b, c, d in rows:
        print('%-22s %-34s %-32s %s' % (a, b, c, d))
    print()
    print('Four dimensions are not matched, and one of them is the statistic itself.')
    print('The estimator mismatch alone is worth 0.0080 in rho by this campaign\'s')
    print('own measurement (E2E-REPORT), three times the corrected residual.')

    hr('3. CAN THE COMPARISON BE DONE UNDER A4 ON BOTH SIDES?')
    print('Yes. results/E2E-a4.json retains the per-point delivery-span utilisation')
    print('for the corrected cells, so both routes are available and both are run.')
    print()
    need = {}
    for arm in ('c10', 'c50'):
        rl, _ = e2e_last_safe(arm)
        traces = glob.glob('results/e2e/e2e-%s-c0-rl%d-r*-consumer.jsonl*' % (arm, rl))
        need[arm] = (rl, len(traces))
        print('  E2e %-4s last SAFE rl=%-5d  A4 retained: %.4f   consumer traces '
              'still on disk: %d'
              % (arm, rl, A4E2E['%s-%d' % (arm, rl)]['a4Rho'], len(traces)))
    print()
    print('The retained values cannot be RE-DERIVED: A4 needs per-arrival timestamps')
    print('from the consumer trace, traces are gitignored corpus-wide, and none')
    print('survives at the c10 arm\'s last SAFE point. That is true of every A4')
    print('value in every campaign -- E1, E2 and E2b preserve theirs in their')
    print('boundary files. One caveat specific to this side: E2E-a4.json stores a')
    print('single value per point with no per-repetition list, so the AGGREGATOR on')
    print('the corrected side of the A4 route cannot be verified to be the median.')
    out['a4Feasible'] = {a: {'lastSafeRl': v[0], 'tracesOnDisk': v[1],
                             'a4RhoRetained': A4E2E['%s-%d' % (a, v[0])]['a4Rho']}
                         for a, v in need.items()}

    hr('4. THE MATCHED COMPARISON')
    print('Last SAFE point only, drain-window estimator, median, configured C=2000,')
    print('c10 arm against c50 arm under matched conditions (C0, lambda_L=1000).')
    print()
    print('%-28s %6s %12s %10s' % ('cell', 'rl', 'rate (rps)', 'rho'))
    unc = {}
    for label, path, arm in [('E1 c10/C0', 'results/boundaries/c10-C0.json', 'c10'),
                             ('E1 c50/C0', 'results/boundaries/c50-C0.json', 'c50')]:
        b, pt = last_safe(path)
        dw = pt.get('rhoAchievedDrainWindow')
        assert dw, label
        rho = statistics.median(dw)
        unc[arm] = {'rl': pt['rl'], 'rho': rho, 'rate': rho * 2000.0, 'n': len(dw)}
        print('%-28s %6d %12.1f %10.4f' % ('uncorrected ' + label, pt['rl'],
                                           rho * 2000.0, rho))
    cor = {}
    for arm in ('c10', 'c50'):
        rl, rates = e2e_last_safe(arm)
        r = statistics.median(rates)
        cor[arm] = {'rl': rl, 'rho': r / C_D, 'rate': r, 'n': len(rates)}
        print('%-28s %6d %12.1f %10.4f' % ('corrected E2e ' + arm, rl, r, r / C_D))

    gu_rho = unc['c50']['rho'] - unc['c10']['rho']
    gc_rho = cor['c50']['rho'] - cor['c10']['rho']
    gu_rps = unc['c50']['rate'] - unc['c10']['rate']
    gc_rps = cor['c50']['rate'] - cor['c10']['rate']
    print()
    print('%-34s %12s %12s %10s' % ('', 'uncorrected', 'corrected', 'removed'))
    print('%-34s %12.4f %12.4f %9.1f%%'
          % ('inter-arm gap, in rho', gu_rho, gc_rho, 100 * (1 - gc_rho / gu_rho)))
    print('%-34s %12.1f %12.1f %9.1f%%'
          % ('inter-arm gap, in rps (throughput)', gu_rps, gc_rps,
             100 * (1 - gc_rps / gu_rps)))
    out['matched'] = {
        'recipe': 'last SAFE point, drain-window, median, C=2000, c10 vs c50, C0',
        'uncorrected': {k: {kk: round(vv, 4) for kk, vv in v.items()}
                        for k, v in unc.items()},
        'corrected': {k: {kk: round(vv, 4) for kk, vv in v.items()}
                      for k, v in cor.items()},
        'gapRhoUncorrected': round(gu_rho, 4), 'gapRhoCorrected': round(gc_rho, 4),
        'gapRpsUncorrected': round(gu_rps, 1), 'gapRpsCorrected': round(gc_rps, 1),
        'fractionRemovedRho': round(100 * (1 - gc_rho / gu_rho), 1),
        'fractionRemovedRps': round(100 * (1 - gc_rps / gu_rps), 1),
    }

    hr('4b. THE SAME COMPARISON UNDER A4 ON BOTH SIDES')
    ua, ca = {}, {}
    for arm, path in (('c10', 'results/boundaries/c10-C0.json'),
                      ('c50', 'results/boundaries/c50-C0.json')):
        b, pt = last_safe(path)
        ua[arm] = statistics.median(pt['rhoAchieved'])
        rl, _ = e2e_last_safe(arm)
        ca[arm] = A4E2E['%s-%d' % (arm, rl)]['a4Rho']
        print('  %-4s uncorrected %.4f (median of %d reps)   corrected %.4f'
              % (arm, ua[arm], len(pt['rhoAchieved']), ca[arm]))
    gu_a4 = ua['c50'] - ua['c10']
    gc_a4 = ca['c50'] - ca['c10']
    print()
    print('  gap %.4f -> %.4f, %.1f%% removed' % (gu_a4, gc_a4,
                                                  100 * (1 - gc_a4 / gu_a4)))
    out['matchedA4'] = {
        'recipe': 'last SAFE point, A4 delivery span, C=2000, c10 vs c50, C0',
        'caveat': 'the corrected side stores one value per point, so its '
                  'aggregator is not recorded and cannot be matched to the median '
                  'used on the uncorrected side',
        'gapRhoUncorrected': round(gu_a4, 4), 'gapRhoCorrected': round(gc_a4, 4),
        'fractionRemovedRho': round(100 * (1 - gc_a4 / gu_a4), 1),
    }

    hr('5. THE MATCHED FIGURE AGAINST THE PUBLISHED ONE')
    print('%-46s %10s %10s %9s' % ('accounting', 'before', 'after', 'removed'))
    print('%-46s %10.4f %10.4f %8.1f%%'
          % ('published (unmatched: 7-cell range vs 2-cell gap)', 0.0706, 0.0026,
             100 * (1 - 0.0026 / 0.0706)))
    print('%-46s %10.4f %10.4f %8.1f%%'
          % ('matched, in rho', gu_rho, gc_rho, 100 * (1 - gc_rho / gu_rho)))
    print('%-46s %10.1f %10.1f %8.1f%%'
          % ('matched, in rps', gu_rps, gc_rps, 100 * (1 - gc_rps / gu_rps)))
    print('%-46s %10.4f %10.4f %8.1f%%'
          % ('matched, under A4 on both sides', gu_a4, gc_a4,
             100 * (1 - gc_a4 / gu_a4)))
    print()
    print('The matched answer is estimator-dependent: %.1f%% under A4, %.1f%% under'
          % (100 * (1 - gc_a4 / gu_a4), 100 * (1 - gc_rho / gu_rho)))
    print('the drain-window estimator. Both are matched; neither is the published')
    print('96.3%, which differenced a seven-cell range against a two-cell gap.')
    print()
    print('A6 note: the collapse factor in A6-REPORT is 0.0706 / 0.0068. Its')
    print('denominator was recomputed from SAFE points only, as A6 requires; its')
    print('numerator was not, and still carries the collapsed endpoints A6 ruled')
    print('invalid. The safe-side seven-cell range is:')
    safe_mids = {}
    for label, path in SEVEN:
        b, pt = last_safe(path)
        safe_mids[label] = statistics.median(pt['rhoAchieved'])
    ss = max(safe_mids.values()) - min(safe_mids.values())
    print('    %.4f (A4, SAFE points only) against 0.0706 as published.' % ss)
    print('    Collapse factor becomes %.1fx rather than %.1fx.'
          % (ss / 0.0068, 0.0706 / 0.0068))
    out['a6CollapseNumerator'] = {'publishedRange': 0.0706,
                                  'safeSideRange': round(ss, 4),
                                  'factorPublished': round(0.0706 / 0.0068, 1),
                                  'factorSafeSide': round(ss / 0.0068, 1)}

    json.dump(out, open('results/W8-effect-size-accounting.json', 'w'), indent=2)
    print()
    print('wrote results/W8-effect-size-accounting.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
