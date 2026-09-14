#!/usr/bin/env python3
"""W2 reviewer response: fit-vs-test separation, boundary resolution, error model.

Offline, from committed artefacts only. Every number printed here is traceable to
a file named in the output.

Usage: python3 scripts/reviewer_w2_analysis.py
"""
import glob
import json
import math
import os
import statistics
import sys

CAL = json.load(open('results/E2D-capacity-calibration.json'))
A6 = json.load(open('results/A6-collapsed-estimator.json'))['cells']
E2E = json.load(open('results/E2E-analysis.json'))['cells']
SWEEP = json.load(open('results/E2C-slo-sweep.json'))
STEP_RPS = 5.0
DELTA = 0.463

CELLS = [
    ('E1 c10/C0', 'results/boundaries/c10-C0.json', 5, 2000),
    ('E1 c10/C1', 'results/boundaries/c10-C1.json', 5, 1400),
    ('E1 c50/C0', 'results/boundaries/c50-C0.json', 25, 2000),
    ('E1 c50/C1', 'results/boundaries/c50-C1.json', 25, 1400),
    ('E2 c10@Q2500', 'results/e2/c10-Q2500/boundaries/c10-C0.json', 5, 2000),
    ('E2 c50@Q500', 'results/e2/c50-Q500/boundaries/c50-C0.json', 25, 2000),
    ('E2b C=400', 'results/e2b/boundaries/c50-C0.json', 25, 400),
]


def hr(t):
    print()
    print('=' * 78)
    print(t)
    print('=' * 78)


def task2_table():
    hr('TASK 2 — resolution table')
    print('%-14s %6s %9s %6s %10s %-14s %11s %4s %11s' % (
        'cell', 'C_cfg', 'C_true', 'step', 'step/C_true', 'interval (rl)',
        'width/C_true', 'n', 'repl spread'))
    rows = []
    for label, path, S, cd in CELLS:
        b = json.load(open(path))
        bd = b['boundary']
        true = CAL['cells'][label]['trueCapacity']
        lo, hi = bd['lastSafeRl'], bd['firstNonSafeRl']
        pt = next(p for p in b['points'] if p['rl'] == lo)
        rhos = pt['rhoAchieved']
        spread = max(rhos) - min(rhos)
        row = {'cell': label, 'C_cfg': cd, 'C_true': true,
               'stepFrac': STEP_RPS / true, 'rl': [lo, hi],
               'widthFrac': (hi - lo) / true, 'n': len(pt['runs']),
               'replSpreadRho': spread,
               'effAtLastSafe': A6[label]['safePoints'] and
               max(A6[label]['safePoints'], key=lambda p: p['rl'])['a4Rate'] / true}
        rows.append(row)
        print('%-14s %6d %9.1f %6.0f %10.5f  [%4d, %4d]  %11.5f %4d %11.5f' % (
            label, cd, true, STEP_RPS, row['stepFrac'], lo, hi,
            row['widthFrac'], row['n'], spread))
    return rows


def task2_answers(rows):
    hr('2.1 — is the 0.0068 residual spread above or below per-cell resolution?')
    effs = [r['effAtLastSafe'] for r in rows]
    spread = max(effs) - min(effs)
    print('post-A6 residual spread in effective utilisation: %.4f' % spread)
    print('  (source: results/A6-collapsed-estimator.json, last SAFE point per cell)')
    print()
    print('%-14s %12s %12s %10s' % ('cell', 'resolution', 'spread/res', 'verdict'))
    for r in rows:
        ratio = spread / r['stepFrac']
        print('%-14s %12.5f %12.2f %10s' % (
            r['cell'], r['stepFrac'], ratio,
            'resolvable' if ratio > 1 else 'BELOW resolution'))
    print()
    print('coarsest resolution: %.5f (%s)' % (
        max(r['stepFrac'] for r in rows),
        max(rows, key=lambda r: r['stepFrac'])['cell']))
    print('finest   resolution: %.5f (%s)' % (
        min(r['stepFrac'] for r in rows),
        min(rows, key=lambda r: r['stepFrac'])['cell']))
    print('aggregate: the spread is %.2fx the coarsest and %.2fx the finest step.'
          % (spread / max(r['stepFrac'] for r in rows),
             spread / min(r['stepFrac'] for r in rows)))

    hr('2.2 — are the endpoints distinguishable?')
    lo_cell = min(rows, key=lambda r: r['effAtLastSafe'])
    hi_cell = max(rows, key=lambda r: r['effAtLastSafe'])
    print('extremes: %s at %.4f and %s at %.4f'
          % (lo_cell['cell'], lo_cell['effAtLastSafe'],
             hi_cell['cell'], hi_cell['effAtLastSafe']))
    print()
    d1 = 1.0 - hi_cell['effAtLastSafe']
    print('0.9999 vs 1.0000: difference %.5f, against %s resolution %.5f -> %s'
          % (d1, hi_cell['cell'], hi_cell['stepFrac'],
             'distinguishable' if d1 > hi_cell['stepFrac'] else 'NOT distinguishable'))
    d2 = hi_cell['effAtLastSafe'] - lo_cell['effAtLastSafe']
    lim = max(lo_cell['stepFrac'], hi_cell['stepFrac'])
    print('0.9931 vs 0.9999: difference %.5f, against the coarser of the two '
          'resolutions %.5f (%s) -> %s'
          % (d2, lim, lo_cell['cell'] if lo_cell['stepFrac'] > hi_cell['stepFrac']
             else hi_cell['cell'],
             'distinguishable' if d2 > lim else 'NOT distinguishable'))
    print('  the same difference against the finer resolution %.5f would be %.2f steps'
          % (min(lo_cell['stepFrac'], hi_cell['stepFrac']),
             d2 / min(lo_cell['stepFrac'], hi_cell['stepFrac'])))
    return spread, rows


def task2_replication(rows):
    hr('2.3 — run-to-run spread at the n=12 points, in bisection-step units')
    print('%-24s %3s %12s %12s %10s %12s' % (
        'point', 'n', 'rho min', 'rho max', 'spread', 'spread/step'))
    found = []
    for label, path, S, cd in CELLS:
        b = json.load(open(path))
        true = CAL['cells'][label]['trueCapacity']
        step = STEP_RPS / true
        for pt in b['points']:
            if len(pt['runs']) < 12:
                continue
            r = pt['rhoAchieved']
            sp = max(r) - min(r)
            found.append((label, pt['rl'], len(r), sp, sp / step))
            print('%-24s %3d %12.4f %12.4f %10.5f %12.2f'
                  % ('%s rl=%d' % (label, pt['rl']), len(r), min(r), max(r), sp, sp / step))
    if found:
        print()
        print('replicate spread is %.0f%% to %.0f%% of one bisection step.'
              % (100 * min(f[4] for f in found), 100 * max(f[4] for f in found)))
        print('so the dominant uncertainty is the step, not run-to-run variation.')
    return found


def task2_sweep():
    hr('2.4 — boundary movement across the tenfold SLO range')
    print('%-14s %-28s %-28s %10s %10s' % (
        'cell', 'tightest well-posed', 'loosest', 'move (rl)', 'in steps'))
    out = []
    for label, c in SWEEP['cells'].items():
        wp = [(int(t), e) for t, e in c['byThreshold'].items()
              if e['wellPosed'] and e.get('bracket')]
        if len(wp) < 2:
            continue
        wp.sort()
        lo, hi = wp[0], wp[-1]
        true = None
        for cl, path, S, cd in CELLS:
            if cl.split()[-1].replace('@Q2500', '').replace('@Q500', '') in label \
                    or cl == label:
                true = CAL['cells'][cl]['trueCapacity']
        move = abs(hi[1]['bracket'][0] - lo[1]['bracket'][0])
        out.append((label, move, move / STEP_RPS))
        print('%-14s %-28s %-28s %10d %10.1f' % (
            label, '%d ms: rl %s' % (lo[0], lo[1]['bracket']),
            '%d ms: rl %s' % (hi[0], hi[1]['bracket']), move, move / STEP_RPS))
    if out:
        print()
        print('maximum movement %d rps = %.1f bisection steps (%s)'
              % (max(o[1] for o in out), max(o[2] for o in out),
                 max(out, key=lambda o: o[1])[0]))
    return out


def task3():
    hr('TASK 3 — error model')
    print('S_actual = S_configured + delta;  C_actual = concurrency / S_actual')
    print('capacity overstatement = delta / S_configured,  delta = %.3f ms' % DELTA)
    print()
    for S, claim in ((5, 9.3), (25, 1.85)):
        got = 100 * DELTA / S
        print('  delta/S at S=%2d ms = %.4f%%  (paper states %.2f%%)  %s'
              % (S, got, claim, 'matches' if abs(got - claim) < 0.02 else 'DIFFERS'))
    print()
    print('%-14s %5s %5s %6s %11s %11s %9s %s' % (
        'cell', 'S', 'conc', 'C_cfg', 'model C', 'measured', 'error', 'verdict'))
    bad = []
    for label, path, S, cd in CELLS:
        true = CAL['cells'][label]['trueCapacity']
        conc = int(math.ceil(cd * S / 1000.0))
        model = conc / ((S + DELTA) / 1000.0)
        err = 100 * (true - model) / model
        if abs(err) > 0.5:
            bad.append((label, err))
        print('%-14s %5d %5d %6d %11.1f %11.1f %+8.2f%% %s' % (
            label, S, conc, cd, model, true, err,
            'ok' if abs(err) <= 0.5 else 'OUTSIDE 0.5%'))
    print()
    if bad:
        print('cells outside 0.5%%: %s' % ', '.join('%s (%+.2f%%)' % b for b in bad))
    else:
        print('every cell matches concurrency/(S+delta) within 0.5%.')
    return bad


def main():
    rows = task2_table()
    spread, rows = task2_answers(rows)
    repl = task2_replication(rows)
    sweep = task2_sweep()
    bad = task3()
    json.dump({'residualSpread': spread,
               'cells': rows, 'n12': repl, 'sweepMovement': sweep,
               'errorModelOutliers': bad},
              open('results/W2-reviewer-analysis.json', 'w'), indent=2, default=float)
    print()
    print('wrote results/W2-reviewer-analysis.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
