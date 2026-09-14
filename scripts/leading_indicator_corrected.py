#!/usr/bin/env python3
"""A7: the E1 leading-indicator analysis, unchanged, over the corrected corpus.

Registered in PRE-REGISTRATION.md A7 (939902d) before this was run.

NOTHING ABOUT THE ANALYSIS CHANGES. METRICS, WARN_SIGMA, the median noise
statistic and `analyse()` are imported from scripts/leading_indicator.py rather
than copied, so they cannot drift. The only thing supplied here is a reader for
the corrected-harness corpus, whose records live under results/e2e/ instead of
results/.

Usage: python3 scripts/leading_indicator_corrected.py
"""
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from leading_indicator import (METRICS, WARN_SIGMA, analyse,  # noqa: E402
                               drain_inflight_mean)

DEEP = 50.0   # E1B-PLAN.md, 09e41e5 — frozen, not changed here
CELLS = {'corrected c10': 'results/e2e/e2e-c10-c0-rl%d-r*.json',
         'corrected c50': 'results/e2e/e2e-c50-c0-rl%d-r*.json'}


def extract_path(path):
    """Identical fields to leading_indicator.extract, from an explicit path."""
    rec = json.load(open(path))
    s = rec['supplementary']
    return {
        'p50': float(s['drainLiveP50Ms']),
        'p90': float(s['drainLiveP90Ms']),
        'p99': float(s['drainLiveP99Ms']),
        'qMean': float(s['drainQueueDepthMean']),
        'ifMean': drain_inflight_mean(rec),
        'timeout': float(s['drainTimeoutRate']),
        'vSLO': rec['vSLO'],
        'rho': None,
    }


def collect_corrected(pattern):
    """SAFE points only, ordered by achieved rate — the same shape collect() returns."""
    rates = sorted({int(p.split('-rl')[1].split('-r')[0])
                    for p in glob.glob(pattern % 0 if '%d' not in pattern else
                                       pattern.replace('%d', '*'))})
    pts = []
    for rl in rates:
        paths = sorted(glob.glob(pattern.replace('%d', str(rl))))
        per = [extract_path(p) for p in paths]
        if not per:
            continue
        if max(r['vSLO'] for r in per) > 0.01:      # SAFE only, unchanged rule
            continue
        row = {'rl': rl, 'n': len(per), 'rho': float(rl)}
        for key, _, _, _ in METRICS:
            vals = [r[key] for r in per]
            row[key] = {'mean': statistics.mean(vals),
                        'sd': statistics.pstdev(vals) if len(vals) > 1 else 0.0,
                        'vals': vals}
        pts.append(row)
    pts.sort(key=lambda r: r['rl'])
    return pts


def main():
    out = {'warnSigma': WARN_SIGMA, 'deepThreshold': DEEP, 'cells': {}}
    print('A7 — leading-indicator analysis over the corrected-harness corpus')
    print('statistic, threshold and criterion all unchanged (A7, 939902d)')
    print()
    for label, pat in CELLS.items():
        pts = collect_corrected(pat)
        print('=' * 74)
        print('%s — %d SAFE points: rl %s'
              % (label, len(pts), ', '.join(str(p['rl']) for p in pts)))
        print('=' * 74)
        if len(pts) < 2:
            print('  too few SAFE points to analyse')
            continue
        cell = {'safeRates': [p['rl'] for p in pts], 'metrics': {}}
        print('%-18s %8s %12s %8s %12s %s'
              % ('metric', 'noise', 'first warn rl', 'room', 'total sigma', 'crosses?'))
        for key, lab, unit, floor in METRICS:
            res = analyse(pts, key, floor)
            if res is None:
                continue
            rl_at = res.get('firstWarningRl')
            room = res.get('warningRoomPoints')
            cell['metrics'][key] = {'label': lab, 'noise': res['noise'],
                                    'firstWarnRl': rl_at, 'warningRoomPoints': room,
                                    'totalSigma': res['totalSigma'],
                                    'perPoint': [{'rl': pts[i]['rl'],
                                                  'mean': p['mean'],
                                                  'riseSigma': p['riseSigma']}
                                                 for i, p in enumerate(res['perPoint'])]}
            print('%-18s %8.3f %12s %8s %12.2f %s'
                  % (lab, res['noise'],
                     rl_at if rl_at else 'never',
                     room if room is not None else '-', res['totalSigma'],
                     'YES' if res['totalSigma'] >= WARN_SIGMA else 'no'))
        # the DEEP criterion, applied to queue depth only, unchanged
        qd = [(p['rl'], p['qMean']['mean']) for p in pts]
        deep_rl = next((rl for rl, v in qd if v >= DEEP), None)
        cell['queueDeepCrossRl'] = deep_rl
        print()
        print('  queue depth vs the frozen DEEP threshold (%.0f req):' % DEEP)
        for rl, v in qd:
            print('     rl=%-5d qMean %8.2f  %s' % (rl, v, 'CROSSES' if v >= DEEP else '-'))
        print('  DEEP crossed within the SAFE range: %s'
              % ('at rl=%d' % deep_rl if deep_rl else 'NO'))
        out['cells'][label] = cell
        print()
    json.dump(out, open('results/A7-leading-indicator-corrected.json', 'w'), indent=2)
    print('wrote results/A7-leading-indicator-corrected.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
