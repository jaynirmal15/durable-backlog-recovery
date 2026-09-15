#!/usr/bin/env python3
"""A8: repeatability of the corrected saturation plateaus.

Reads the twenty replicated windows in results/a8/ and answers the readings
registered in PRE-REGISTRATION.md addendum A8, commit 590d1cc, exactly as that
addendum states them. Nothing here interprets beyond those readings.

Usage: python3 scripts/a8_repeatability.py
"""
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

E2E = json.load(open('results/E2E-analysis.json'))

# Plateaus implied by the registered constants. Both are exact arithmetic
# consequences of constants registered in E2E-PLAN addendum 1; neither was
# itself registered as a plateau (A8 says so explicitly).
SLEEP_MS = {'c10': 4.537, 'c50': 24.537}
CONC = {'c10': 10, 'c50': 50}
OV_SAT = {'c10': 0.4947, 'c50': 0.4914}     # registered constant
OV_90 = {'c10': 0.5165, 'c50': 0.5114}      # rival registered constant
ORIGINAL = {'c10': 'results/e2e/exp2-c10-plateau.json',
            'c50': 'results/e2e/exp2-c50-plateau.json'}


def implied(arm, ov):
    return CONC[arm] / ((SLEEP_MS[arm] + ov) / 1000.0)


def hinges(v):
    """Tukey hinges: medians of the halves, median included for odd n."""
    v = sorted(v)
    n = len(v)
    lo = statistics.median(v[:(n + 1) // 2])
    hi = statistics.median(v[n // 2:])
    return lo, hi


def hr(t):
    print()
    print('=' * 78)
    print(t)
    print('=' * 78)


def main():
    out = {'registration': {'addendum': 'A8', 'commit': '590d1cc'},
            'buildCommit': 'c7f5835b2b06e59bd29239ea352451e040cf12a5', 'arms': {}}

    hr('THE TWENTY WINDOWS')
    data = {}
    for arm in ('c10', 'c50'):
        rows = []
        for f in sorted(glob.glob('results/a8/a8-%s-plateau-w*.json' % arm),
                        key=lambda p: int(p.split('-w')[-1].split('.')[0])):
            d = json.load(open(f))
            rows.append(d)
        data[arm] = rows
        print()
        print('--- %s  (S = %.3f ms, %d workers)' % (arm, SLEEP_MS[arm], CONC[arm]))
        print('    %-4s %12s %8s %10s %10s' % ('w', 'servedRps', 'window', 'rejected', 'timedOut'))
        for i, d in enumerate(rows, 1):
            print('    %-4d %12.4f %8.4f %10d %10d'
                  % (i, d['servedRps'], d['windowSec'], d['rejected'], d['timedOut']))

    hr('PER ARM: MEDIAN, RANGE, IQR')
    print('%-5s %3s %11s %11s %11s %9s %11s %11s %9s'
          % ('arm', 'n', 'min', 'median', 'max', 'range', 'lower hinge',
             'upper hinge', 'IQR'))
    for arm in ('c10', 'c50'):
        v = sorted(d['servedRps'] for d in data[arm])
        lo, hi = hinges(v)
        med = statistics.median(v)
        spread = v[-1] - v[0]
        print('%-5s %3d %11.4f %11.4f %11.4f %9.4f %11.4f %11.4f %9.4f'
              % (arm, len(v), v[0], med, v[-1], spread, lo, hi, hi - lo))
        out['arms'][arm] = {
            'n': len(v), 'windows': [round(x, 4) for x in v],
            'min': round(v[0], 4), 'median': round(med, 4), 'max': round(v[-1], 4),
            'spread': round(spread, 4), 'lowerHinge': round(lo, 4),
            'upperHinge': round(hi, 4), 'iqr': round(hi - lo, 4),
            'sd': round(statistics.pstdev(v), 4),
        }

    hr('READING 1 — SHORT ARM (S = 5 ms)')
    arm = 'c10'
    v = sorted(d['servedRps'] for d in data[arm])
    reg, riv = implied(arm, OV_SAT[arm]), implied(arm, OV_90[arm])
    inside_reg = v[0] <= reg <= v[-1]
    inside_riv = v[0] <= riv <= v[-1]
    print('observed spread            [%.4f, %.4f]   width %.4f rps'
          % (v[0], v[-1], v[-1] - v[0]))
    print('registered constant implies %.4f rps   inside the spread: %s'
          % (reg, 'YES' if inside_reg else 'NO'))
    print('rival constant implies      %.4f rps   inside the spread: %s'
          % (riv, 'YES' if inside_riv else 'NO'))
    print('separation                  %.4f rps' % (reg - riv))
    print()
    if inside_reg and not inside_riv:
        verdict = ('OUTCOME 1: the short-arm prediction DISCRIMINATED. The value '
                   'implied by the registered constant lies within the observed '
                   'spread and the rival lies outside it.')
    elif inside_reg and inside_riv:
        verdict = ('OUTCOME 2: the short arm DID NOT DISCRIMINATE. Both implied '
                   'values lie within the observed spread. The plateau prediction '
                   'is a consistency check with no discriminating power in either '
                   'arm, and the candidate table loses its claim to have tested '
                   'anything.')
    else:
        verdict = ('OUTCOME 3: the prospective prediction FAILED ON REPLICATION. '
                   'The value implied by the registered constant lies outside the '
                   'observed spread.')
    print(verdict)
    out['shortArm'] = {'spread': [round(v[0], 4), round(v[-1], 4)],
                       'registeredImplied': round(reg, 4), 'rivalImplied': round(riv, 4),
                       'registeredInside': inside_reg, 'rivalInside': inside_riv,
                       'outcome': verdict.split(':')[0], 'verdict': verdict}

    hr('READING 2 — LONG ARM (S = 25 ms)')
    arm = 'c50'
    v = sorted(d['servedRps'] for d in data[arm])
    reg, riv = implied(arm, OV_SAT[arm]), implied(arm, OV_90[arm])
    sep = reg - riv
    spread = v[-1] - v[0]
    print('two implied plateaus        %.4f and %.4f, separated by %.4f rps'
          % (reg, riv, sep))
    print('observed spread             %.4f rps' % spread)
    print()
    if spread > sep:
        lv = ('The observed spread EXCEEDS the separation. The registered '
              'prediction for this arm is CONFIRMED: the long arm cannot '
              'discriminate the two constants, as the manuscript already states.')
    else:
        lv = ('The observed spread is BELOW the separation. The long arm does '
              'discriminate after all, and the manuscript\'s current wording is '
              'too weak and will be corrected.')
    print(lv)
    out['longArm'] = {'registeredImplied': round(reg, 4), 'rivalImplied': round(riv, 4),
                      'separation': round(sep, 4), 'spread': round(spread, 4),
                      'spreadExceedsSeparation': spread > sep, 'verdict': lv}

    hr('READING 3 — THE ORIGINAL SINGLE WINDOW AGAINST THE REPLICATED MEDIAN')
    print('%-5s %14s %14s %11s %11s %s'
          % ('arm', 'original', 'median of 10', 'difference', 'spread', 'finding'))
    out['original'] = {}
    for arm in ('c10', 'c50'):
        o = json.load(open(ORIGINAL[arm]))['servedRps']
        v = sorted(d['servedRps'] for d in data[arm])
        med = statistics.median(v)
        diff = med - o
        spread = v[-1] - v[0]
        flag = abs(diff) > spread
        print('%-5s %14.4f %14.4f %11.4f %11.4f %s'
              % (arm, o, med, diff, spread,
                 'EXCEEDS THE SPREAD' if flag else 'within the spread'))
        out['original'][arm] = {'originalSingleWindow': round(o, 4),
                                'replicatedMedian': round(med, 4),
                                'difference': round(diff, 4),
                                'spread': round(spread, 4),
                                'differenceExceedsSpread': flag,
                                'originalRankInTen': sum(1 for x in v if x < o),
                                'withinReplicatedRange': v[0] <= o <= v[-1]}
    print()
    for arm in ('c10', 'c50'):
        r = out['original'][arm]
        below = r['originalRankInTen']
        print('  %-4s %d of the ten replicated windows fall below the original, %d '
              'above it.' % (arm, below, 10 - below))

    json.dump(out, open('results/A8-plateau-repeatability.json', 'w'), indent=2)
    print()
    print('wrote results/A8-plateau-repeatability.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
