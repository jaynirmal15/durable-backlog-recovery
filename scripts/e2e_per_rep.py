#!/usr/bin/env python3
"""Recover the per-repetition achieved rates the E2e analysis discards.

results/E2E-analysis.json stores one median rate per point. The 33 run records
retain every input that median was computed from, so the list is recoverable
exactly, under the estimator those cells actually used -- the drain-window
as-measured one, backlogAtRestore / tDrainSec + median(injRate), which is what
e2e_analysis.achieved() computes. Nothing here changes the estimator.

The recomputation is checked against the committed medians before anything is
reported from it.

Usage: python3 scripts/e2e_per_rep.py
"""
import collections
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_analysis import achieved, C_D                   # noqa: E402
from locate_boundary import RESOLUTION_RPS, classify     # noqa: E402

E2E = json.load(open('results/E2E-analysis.json'))
AGGS = [('min', min), ('max', max),
        ('mean', statistics.mean), ('median', statistics.median)]


def hr(t):
    print()
    print('=' * 78)
    print(t)
    print('=' * 78)


def collect(arm):
    by = collections.defaultdict(list)
    for p in sorted(glob.glob('results/e2e/e2e-%s-c0-rl*-r*.json' % arm)):
        rec = json.load(open(p))
        by[rec['params']['rateLimitRps']].append(rec)
    pts = []
    for rl in sorted(by):
        rs = by[rl]
        rows = [{'runId': r['runId'], 'rate': achieved(r),
                 'backlog': r['backlogAtRestore'], 'tDrainSec': r['tDrainSec']}
                for r in rs]
        missing = [x['runId'] for x in rows if x['rate'] is None]
        rows = [x for x in rows if x['rate'] is not None]
        pts.append({'rl': rl, 'n': len(rs), 'class': classify([r['vSLO'] for r in rs]),
                    'rows': rows, 'missing': missing})
    return pts


def main():
    out = {'estimator': 'drain-window as-measured: backlogAtRestore / tDrainSec '
                        '+ median(injRate over the drain window). Identical to '
                        'e2e_analysis.achieved(); not A4.',
           'C_d': C_D, 'cells': {}}

    hr('1. ARE THE INPUTS PRESENT IN ALL 33 RECORDS')
    need = ['backlogAtRestore', 'tDrainSec', 'timeline']
    files = sorted(glob.glob('results/e2e/e2e-*-r*.json'))
    bad = []
    for f in files:
        r = json.load(open(f))
        miss = [k for k in need if not r.get(k)]
        inj = [p for p in (r.get('timeline') or []) if p.get('injRate')]
        if miss or not inj:
            bad.append((os.path.basename(f), miss, len(inj)))
    print('records examined: %d' % len(files))
    print('records missing any of %s, or with no injRate samples: %d'
          % (need, len(bad)))
    for x in bad:
        print('   ', x)
    if bad:
        print()
        print('RECONSTRUCTION NOT POSSIBLE for the records above.')
        return 1
    print('All inputs present. The estimator is reproducible without change.')

    hr('2. RECOMPUTED PER-REPETITION RATES, CHECKED AGAINST THE COMMITTED MEDIANS')
    ok = True
    for arm in ('c10', 'c50'):
        pts = collect(arm)
        committed = {p['rl']: p for p in E2E['cells'][arm]['points']}
        print()
        print('--- %s' % arm)
        print('%6s %-8s %3s %-34s %9s %9s %s'
              % ('rl', 'class', 'n', 'per-repetition rates (rps)', 'median',
                 'committed', 'match'))
        cell = []
        for p in pts:
            v = sorted(x['rate'] for x in p['rows'])
            med = round(statistics.median(v), 1)
            c = committed[p['rl']]
            match = (med == c['achievedRps'] and p['class'] == c['class'])
            ok = ok and match
            print('%6d %-8s %3d %-34s %9.1f %9.1f %s'
                  % (p['rl'], p['class'], p['n'],
                     ', '.join('%.1f' % x for x in v), med, c['achievedRps'],
                     'yes' if match else 'NO'))
            cell.append({'rl': p['rl'], 'class': p['class'], 'n': p['n'],
                         'achievedRps': [round(x, 2) for x in v],
                         'rho': [round(x / C_D, 4) for x in v],
                         'median': med,
                         'committedMedian': c['achievedRps'],
                         'matchesCommitted': match,
                         'runs': [{'runId': x['runId'], 'rate': round(x['rate'], 2)}
                                  for x in sorted(p['rows'], key=lambda y: y['rate'])]})
        out['cells'][arm] = {'points': cell}
    print()
    print('every recomputed median reproduces the committed value: %s'
          % ('YES' if ok else 'NO'))
    if not ok:
        return 1

    hr('3. PER-REPETITION SPREAD, PER POINT')
    print('Compared against the A3 rule the seven cells are held to: a point whose')
    print('achieved-rho spread exceeds RESOLUTION_RPS / C_d = %.5f is resolving'
          % (RESOLUTION_RPS / C_D))
    print('finer than its own instrument.')
    print()
    print('%-5s %6s %-8s %10s %10s %10s %9s %s'
          % ('arm', 'rl', 'class', 'min', 'max', 'spread', 'in rho', 'A3 flag'))
    flagged = []
    for arm in ('c10', 'c50'):
        for p in out['cells'][arm]['points']:
            v = p['achievedRps']
            spread = max(v) - min(v)
            in_rho = spread / C_D
            flag = in_rho > RESOLUTION_RPS / C_D
            if flag:
                flagged.append((arm, p['rl'], p['class'], round(in_rho, 5)))
            p['spreadRps'] = round(spread, 2)
            p['rhoAchievedSpread'] = round(in_rho, 5)
            p['rhoResolution'] = round(RESOLUTION_RPS / C_D, 5)
            p['spreadExceedsResolution'] = flag
            print('%-5s %6d %-8s %10.2f %10.2f %10.2f %9.5f %s'
                  % (arm, p['rl'], p['class'], min(v), max(v), spread, in_rho,
                     'FLAG' if flag else '.'))
    print()
    print('points flagged: %d of %d'
          % (len(flagged), sum(len(out['cells'][a]['points']) for a in out['cells'])))
    for x in flagged:
        print('   ', x)
    out['a3'] = {'flagged': flagged,
                 'rhoResolution': round(RESOLUTION_RPS / C_D, 5)}

    hr('4. DOES THE PREDICT-AND-ELIMINATE RESULT MOVE?')
    print('The bracket is [rho at the last SAFE point, rho at the first UNSAFE')
    print('point above it]. Recomputed under each aggregator:')
    print()
    print('%-5s %-10s %18s %9s %9s' % ('arm', 'aggregator', 'bracket', 'width', 'mid'))
    out['bracketSensitivity'] = {}
    for arm in ('c10', 'c50'):
        pts = out['cells'][arm]['points']
        safe = [p for p in pts if p['class'] == 'SAFE']
        uns = [p for p in pts if p['class'] == 'UNSAFE']
        lo = max(safe, key=lambda p: p['rl'])
        hi = min([p for p in uns if p['rl'] > lo['rl']], key=lambda p: p['rl'])
        rows = {}
        for name, fn in AGGS:
            a, b = fn(lo['rho']), fn(hi['rho'])
            rows[name] = {'bracket': [round(a, 4), round(b, 4)],
                          'width': round(b - a, 4), 'mid': round((a + b) / 2, 4)}
            print('%-5s %-10s   [%.4f, %.4f] %9.4f %9.4f'
                  % (arm, name, a, b, b - a, (a + b) / 2))
        comm = E2E['cells'][arm]['bracket']
        print('%-5s %-10s   [%.4f, %.4f] %9.4f %9.4f   <- committed'
              % (arm, 'published', comm['rho'][0], comm['rho'][1],
                 comm['rhoWidth'], comm['rhoMid']))
        out['bracketSensitivity'][arm] = rows

    hr('5. DOES A7 MOVE?')
    print('leading_indicator_corrected.py orders the SAFE points by achieved rho')
    print('and reads six per-run metrics that are not rho. Only the ORDER of the')
    print('SAFE points could change. Under each aggregator:')
    print()
    for arm in ('c10', 'c50'):
        safe = [p for p in out['cells'][arm]['points'] if p['class'] == 'SAFE']
        base = None
        for name, fn in AGGS:
            order = [p['rl'] for p in sorted(safe, key=lambda p: fn(p['rho']))]
            base = base or order
            print('  %-5s %-8s %s%s' % (arm, name, order,
                                        '' if order == base else '   <- DIFFERS'))
    print()
    print('A7 reads p50/p90/p99/qMean/ifMean/timeout per run; none is a function')
    print('of the rate estimator, so identical ordering means an identical result.')

    json.dump(out, open('results/W7-e2e-per-repetition.json', 'w'), indent=2)
    print()
    print('wrote results/W7-e2e-per-repetition.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
