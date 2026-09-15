#!/usr/bin/env python3
"""Measurement characterisation of the direct timing probe, and of the
plateau-inferred delta estimates. Section 5 needs both before it can freeze.

Everything here is read out of committed records. Where a quantity is not in
them, it is named as not recoverable rather than estimated.

Usage: python3 scripts/probe_characterisation.py
"""
import collections
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CAL = json.load(open('results/E2D-capacity-calibration.json'))
E2E = json.load(open('results/E2E-analysis.json'))
MS = 1e6


def hr(t):
    print()
    print('=' * 78)
    print(t)
    print('=' * 78)


def ov_rows():
    """The six delta estimates, each with the block it came from."""
    rows = []
    for s, arm in (('5', 'c10'), ('25', 'c50')):
        for cond, f in (('90% load', 'exp1-s%s-load90.json' % s),
                        ('saturation', 'exp1-s%s-sat-on.json' % s)):
            d = json.load(open('results/e2e/' + f))
            rows.append({'S': s, 'arm': arm, 'cond': cond, 'src': f,
                         'ov': d['overhead'], 'windowSec': d['windowSec'],
                         'served': d.get('servedRps')})
    # in situ: one overheadDrain block per run, over that run's drain window
    for s, arm in (('5', 'c10'), ('25', 'c50')):
        recs = []
        for p in sorted(glob.glob('results/e2e/e2e-%s-c0-rl*-r*.json' % arm)):
            r = json.load(open(p))
            o = r.get('overheadDrain') or {}
            if o.get('enabled') and (o.get('total') or {}).get('meanNs'):
                recs.append((r['runId'], o, r.get('tDrainSec')))
        rows.append({'S': s, 'arm': arm, 'cond': 'in situ', 'src': 'overheadDrain',
                     'runs': recs})
    return rows


def item1():
    hr('1. THE DIRECT TIMING PROBE — six delta estimates')
    print('Clock: every component is a difference of two time.Now() readings')
    print('(downstream/main.go:405-412). Go carries a monotonic reading inside')
    print('time.Time and Sub() uses it, so these are CLOCK_MONOTONIC intervals,')
    print('nominal resolution 1 ns.')
    print()
    print('Sampling for percentiles: ovSample() writes into a fixed buffer of')
    print('OVERHEAD_SAMPLES slots (default 200000) at index ovSampIdx++ and DROPS')
    print('everything past the end (downstream/main.go:305-309). It is FIRST-N')
    print('TRUNCATION, not a reservoir: where count > samples, the percentiles')
    print('describe the first N cycles of the window, not a random sample of it.')
    print('Means, counts and maxima are over every cycle.')
    print()
    print('%-5s %-11s %10s %9s %10s %10s %10s %10s %10s'
          % ('arm', 'condition', 'cycles', 'window s', 'mean ms', 'p50 ms',
             'p90 ms', 'p99 ms', 'p99.9 ms'))
    out = []
    rows = ov_rows()
    for r in rows:
        if r['cond'] == 'in situ':
            continue
        o = r['ov']
        t, p = o['total'], o['totalPct']
        out.append({'arm': r['arm'], 'cond': r['cond'], 'count': t['count'],
                    'samples': o['samples'], 'windowSec': round(r['windowSec'], 2),
                    'meanMs': t['meanNs'] / MS, 'p50Ms': p['p50Ns'] / MS,
                    'p90Ms': p['p90Ns'] / MS, 'p99Ms': p['p99Ns'] / MS,
                    'p999Ms': p['p999Ns'] / MS, 'maxMs': t['maxNs'] / MS,
                    'src': r['src']})
        print('%-5s %-11s %10d %9.2f %10.4f %10.4f %10.4f %10.4f %10.4f'
              % (r['arm'], r['cond'], t['count'], r['windowSec'], t['meanNs'] / MS,
                 p['p50Ns'] / MS, p['p90Ns'] / MS, p['p99Ns'] / MS, p['p999Ns'] / MS))
    # in situ
    for r in rows:
        if r['cond'] != 'in situ':
            continue
        tot = [o['total']['meanNs'] / MS for _, o, _ in r['runs']]
        cnt = sum(o['total']['count'] for _, o, _ in r['runs'])
        p50 = [o['totalPct']['p50Ns'] / MS for _, o, _ in r['runs']]
        p99 = [o['totalPct']['p99Ns'] / MS for _, o, _ in r['runs']]
        win = [d for _, _, d in r['runs'] if d]
        # The published figure is E2E-analysis's own median-of-point-medians;
        # quote it rather than a second recomputation of the same thing.
        pub = E2E['cells'][r['arm']]['inSituOverheadMs']
        out.append({'arm': r['arm'], 'cond': 'in situ', 'count': cnt,
                    'nRuns': len(r['runs']), 'windowSecRange': [min(win), max(win)],
                    'publishedMs': pub,
                    'runMeansMs': sorted(round(x, 4) for x in tot),
                    'medianOfRunP50Ms': statistics.median(p50),
                    'medianOfRunP99Ms': statistics.median(p99),
                    'src': 'overheadDrain across %d runs' % len(r['runs'])})
        print('%-5s %-11s %10d %9s %10.4f %10.4f %10s %10.4f %10s'
              % (r['arm'], 'in situ', cnt,
                 '%.0f-%.0f' % (min(win), max(win)), pub,
                 statistics.median(p50), '-', statistics.median(p99), '-'))

    print()
    print('WHICH STATISTIC IS THE REPORTED VALUE')
    print('  90% load and saturation: the arithmetic MEAN over every cycle in the')
    print('    window (ovTotal.report() -> sum/count). Not trimmed, not a median.')
    print('  in situ: a MEDIAN OF MEDIANS OF MEANS. e2e_analysis.py takes each')
    print('    run\'s overheadDrain.total.meanNs (a mean), medians the three')
    print('    repetitions at a point, then medians across the points of the arm.')
    print()
    print('DISPERSION')
    print('  The records carry p50, p90, p99 and p99.9 for total, sleepExcess and')
    print('  cycle. They do NOT carry p25 or p75, so the INTERQUARTILE RANGE IS')
    print('  NOT RECOVERABLE from committed data. Percentiles below are what exist.')
    print()
    print('SKEW — mean against median, and the upper tail')
    print()
    print('%-5s %-11s %10s %10s %9s %10s %10s'
          % ('arm', 'condition', 'mean ms', 'p50 ms', 'mean/p50', 'p99/p50', 'max ms'))
    for r in out:
        if r['cond'] == 'in situ':
            continue
        print('%-5s %-11s %10.4f %10.4f %9.3f %10.2f %10.4f'
              % (r['arm'], r['cond'], r['meanMs'], r['p50Ms'],
                 r['meanMs'] / r['p50Ms'], r['p99Ms'] / r['p50Ms'], r['maxMs']))
    print()
    print('The mean exceeds the median in every condition and the 99th percentile')
    print('is about twice the median, with maxima three to four times it. The')
    print('distribution is RIGHT-SKEWED, and every reported delta is a MEAN over')
    print('that skewed distribution -- it sits above the typical cycle.')
    return out


def item2():
    hr('2. THE PROBE-ON/OFF INTRUSION TEST')
    print('%-6s %-9s %12s %11s %10s'
          % ('S', 'probe', 'servedRps', 'windowSec', 'records'))
    res = {}
    for s in ('5', '25'):
        pair = {}
        for state in ('on', 'off'):
            fs = sorted(glob.glob('results/e2e/exp1-s%s-sat-%s*.json' % (s, state)))
            d = json.load(open(fs[0]))
            pair[state] = d
            print('%-6s %-9s %12.1f %11.5f %10d'
                  % ('S=' + s, state, d['servedRps'], d['windowSec'], len(fs)))
        shift = 100 * (pair['on']['servedRps'] - pair['off']['servedRps']) \
            / pair['off']['servedRps']
        res[s] = {'onRps': pair['on']['servedRps'], 'offRps': pair['off']['servedRps'],
                  'shiftPct': round(shift, 4),
                  'windowSecOn': pair['on']['windowSec'],
                  'windowSecOff': pair['off']['windowSec'],
                  'recordsPerState': 1}
        print('        shift %+.4f%%' % shift)
    print()
    print('ONE window per state per arm. windowSec ~60 s in all four records, and')
    print('there is exactly ONE sat-on and ONE sat-off record for each S.')
    print('**The control is SINGLE-SHOT: n = 1 versus n = 1, four measurements in')
    print('total.** No repetition exists, so no dispersion can be attached to the')
    print('0.04% and 0.09% shifts and they cannot be compared against the')
    print('window-to-window variability of the plateau itself, which is also')
    print('unmeasured for these cells (METHOD-AUDIT item 17).')
    return res


def item3():
    hr('3. THE SEVEN PLATEAU-INFERRED DELTA ESTIMATES')
    print('delta inferred per cell from its own measured plateau:')
    print('    delta = S * (C_configured / C_measured - 1)')
    print('(capacity_calibration.py:165). The paper quotes only their median.')
    print()
    print('%-14s %5s %9s %11s %11s'
          % ('cell', 'S ms', 'C_conf', 'C_measured', 'implied delta ms'))
    vals = []
    for label, c in CAL['cells'].items():
        vals.append((label, c['impliedOverheadMs']))
        print('%-14s %5d %9d %11.1f %11.3f'
              % (label, c['S'], c['faultCapacity'], c['trueCapacity'],
                 c['impliedOverheadMs']))
    v = sorted(x for _, x in vals)
    n = len(v)
    # Tukey hinges: medians of the lower and upper halves, median included for odd n
    lo = statistics.median(v[:n // 2 + 1])
    hi = statistics.median(v[n // 2:])
    print()
    print('  n            %d' % n)
    print('  min          %.3f  (%s)' % (v[0], min(vals, key=lambda x: x[1])[0]))
    print('  max          %.3f  (%s)' % (v[-1], max(vals, key=lambda x: x[1])[0]))
    print('  range        %.3f ms  (%.1f%% of the median)'
          % (v[-1] - v[0], 100 * (v[-1] - v[0]) / statistics.median(v)))
    print('  median       %.3f  <- the value the correction used' % statistics.median(v))
    print('  mean         %.3f' % statistics.mean(v))
    print('  lower hinge  %.3f' % lo)
    print('  upper hinge  %.3f' % hi)
    print('  IQR          %.3f ms  (Tukey hinges; n=7 so this is a coarse summary)'
          % (hi - lo))
    print('  SD           %.4f   CV %.2f%%'
          % (statistics.pstdev(v), 100 * statistics.pstdev(v) / statistics.mean(v)))
    print()
    print('Split by arm, which is where the structure is:')
    for s, name in ((5, 'S = 5 ms'), (25, 'S = 25 ms')):
        g = [x for lab, x in vals if CAL['cells'][lab]['S'] == s]
        print('  %-10s n=%d  %s  median %.3f'
              % (name, len(g), ', '.join('%.3f' % x for x in sorted(g)),
                 statistics.median(g)))
    print()
    s5 = sorted(x for lab, x in vals if CAL['cells'][lab]['S'] == 5)
    s25 = sorted(x for lab, x in vals if CAL['cells'][lab]['S'] == 25)
    print('**The two arms do not overlap.** Every S = 5 cell is at or above %.3f'
          % min(s5))
    print('and every S = 25 cell is at or below %.3f. The seven are not one' % max(s25))
    print('population of a constant: they separate perfectly by service time, which')
    print('is the per-arm structure section V-D already reports as a 4% gap. The')
    print('within-arm spreads are %.3f (S=5, n=3) and %.3f (S=25, n=4).'
          % (max(s5) - min(s5), max(s25) - min(s25)))
    print()
    print('The seven inferred corrections span %.3f ms, %.0f%% of their own median.'
          % (v[-1] - v[0], 100 * (v[-1] - v[0]) / statistics.median(v)))
    print('The leave-one-out test shows the MODEL is stable against that spread;')
    print('it does not show the inputs are tight, and they are not.')
    return {'values': dict(vals), 'sorted': v, 'min': v[0], 'max': v[-1],
            'range': round(v[-1] - v[0], 4), 'median': statistics.median(v),
            'mean': round(statistics.mean(v), 4), 'lowerHinge': lo, 'upperHinge': hi,
            'iqr': round(hi - lo, 4), 'sd': round(statistics.pstdev(v), 4)}


def main():
    out = {'probe': item1(), 'intrusion': item2(), 'inferredDelta': item3()}
    json.dump(out, open('results/W9-probe-characterisation.json', 'w'), indent=2)
    print()
    print('wrote results/W9-probe-characterisation.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
