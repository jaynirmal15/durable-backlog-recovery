#!/usr/bin/env python3
"""Leave-one-out test of the per-request overhead constant.

The correction constant is the median of seven per-cell estimates, and no cell
was held out (W2 task 1.3). This asks whether the constant generalises across the
existing corpus: for each cell in turn, estimate delta from the other six, predict
the held-out cell's saturation plateau, and report the error. Nothing is retuned.

Prediction:  C_pred = C_d * S / (S + delta_LOO)
             equivalently concurrency / (S + delta_LOO), which is used here
             because concurrency is the integer the downstream actually runs.

Error is reported in rps and as a fraction of that cell's 5 rps bisection step,
which is the unit in which the boundary is resolved.

Source: results/E2D-capacity-calibration.json. No new runs.

Usage: python3 scripts/loo_overhead.py
"""
import json
import math
import statistics
import sys

CAL = json.load(open('results/E2D-capacity-calibration.json'))['cells']
STEP_RPS = 5.0


def main():
    cells = []
    for label, c in CAL.items():
        cells.append({'cell': label, 'S': c['S'], 'C_d': c['faultCapacity'],
                      'plateau': c['trueCapacity'], 'ov': c['impliedOverheadMs'],
                      'conc': int(math.ceil(c['faultCapacity'] * c['S'] / 1000.0))})

    full = statistics.median([c['ov'] for c in cells])
    print('all-seven median delta: %.4f ms  (the constant the paper uses)' % full)
    print()
    print('%-14s %5s %5s %10s %10s %11s %10s %9s %9s' % (
        'held out', 'S', 'conc', 'delta_LOO', 'predicted', 'measured',
        'error rps', 'err/step', 'err %'))
    rows = []
    for i, c in enumerate(cells):
        others = [x['ov'] for j, x in enumerate(cells) if j != i]
        d = statistics.median(others)
        pred = c['conc'] / ((c['S'] + d) / 1000.0)
        err = c['plateau'] - pred
        rows.append({'cell': c['cell'], 'S': c['S'], 'conc': c['conc'],
                     'deltaLOO': round(d, 4), 'predicted': round(pred, 1),
                     'measured': c['plateau'], 'errorRps': round(err, 2),
                     'errorSteps': round(err / STEP_RPS, 3),
                     'errorPct': round(100 * err / pred, 3)})
        print('%-14s %5d %5d %10.4f %10.1f %11.1f %+10.2f %+9.3f %+8.3f%%' % (
            c['cell'], c['S'], c['conc'], d, pred, c['plateau'], err,
            err / STEP_RPS, 100 * err / pred))

    worst = max(rows, key=lambda r: abs(r['errorRps']))
    worst_step = max(rows, key=lambda r: abs(r['errorSteps']))
    print()
    print('worst absolute error : %+.2f rps  (%s)' % (worst['errorRps'], worst['cell']))
    print('worst in step units  : %+.3f steps (%s)' % (worst_step['errorSteps'],
                                                       worst_step['cell']))
    print('worst relative error : %+.3f%%   (%s)'
          % (max(rows, key=lambda r: abs(r['errorPct']))['errorPct'],
             max(rows, key=lambda r: abs(r['errorPct']))['cell']))
    print('RMS error            : %.2f rps'
          % (sum(r['errorRps'] ** 2 for r in rows) / len(rows)) ** 0.5)
    print('delta_LOO range      : %.4f to %.4f ms (all-seven median %.4f)'
          % (min(r['deltaLOO'] for r in rows), max(r['deltaLOO'] for r in rows), full))
    print()
    print('Every held-out prediction lands within %.2f of one bisection step.'
          % max(abs(r['errorSteps']) for r in rows))

    json.dump({'allSevenMedian': full, 'stepRps': STEP_RPS, 'cells': rows,
               'worstAbsRps': worst['errorRps'], 'worstSteps': worst_step['errorSteps'],
               'rmsRps': round((sum(r['errorRps'] ** 2 for r in rows) / len(rows)) ** 0.5, 3)},
              open('results/W2-leave-one-out.json', 'w'), indent=2)
    print('wrote results/W2-leave-one-out.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
