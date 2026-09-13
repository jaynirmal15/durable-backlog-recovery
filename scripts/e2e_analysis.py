#!/usr/bin/env python3
"""E2e analysis: the measured overhead, and the boundary after correcting for it.

Three ways of measuring the same per-request cost, and they do not agree:

  90% load, smooth driver   experiment 1, open-loop pacer below saturation
  saturated, smooth driver  experiment 1, closed loop
  in situ, during a drain   experiment 2, probe reset at restore and read at
                            drain completion, under the campaign's real arrival
                            process

The third is the one that acts where the boundary is set, and it is reported
against the two calibration figures rather than instead of them.

Effective utilisation is computed per run from the cycle time measured in that
same run:

    rho_eff = achieved_rate / (concurrency / mean_cycle)

using the MEAN cycle, because throughput per worker is the reciprocal of the mean.
The distribution is strongly right-skewed, so the median understates the cost and
is reported only to show the skew.

Usage: python3 scripts/e2e_analysis.py
"""
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import RESOLUTION_RPS  # noqa: E402

# Registered in E2E-PLAN addendum 1, before any boundary run.
REGISTERED = {'c10': {'sleepUs': 4537, 'conc': 10, 'ovSat': 0.4947, 'ov90': 0.5165,
                      'rhoSat': 0.9937, 'rho90': 0.9894, 'plateau': 1987.4},
              'c50': {'sleepUs': 24537, 'conc': 50, 'ovSat': 0.4914, 'ov90': 0.5114,
                      'rhoSat': 0.9989, 'rho90': 0.9981, 'plateau': 1997.7}}
C_D = 2000.0
UNCORRECTED_GAP = 0.0706


def ms(ns):
    return ns / 1e6


def run_cycle(rec):
    o = rec.get('overheadDrain')
    if not o:
        return None
    c = o.get('cycle') or {}
    if not c.get('count'):
        return None
    return {'meanMs': ms(c['meanNs']), 'n': c['count'],
            'medianMs': ms((o.get('cyclePct') or {}).get('p50Ns', 0)),
            'p90Ms': ms((o.get('cyclePct') or {}).get('p90Ns', 0)),
            'overheadMs': ms((o.get('total') or {}).get('meanNs', 0)),
            'sleepExcessMs': ms((o.get('sleepExcess') or {}).get('meanNs', 0))}


def main():
    out = {'registered': REGISTERED, 'uncorrectedGap': UNCORRECTED_GAP, 'cells': {}}

    print('=== experiment 1 calibration, and the probe control ===')
    print('%-14s %10s %12s %10s' % ('condition', 'served rps', 'overhead ms', 'probe'))
    for p in sorted(glob.glob('results/e2e/exp1-*.json')):
        d = json.load(open(p))
        o = d['overhead']
        print('%-14s %10.1f %12s %10s' % (
            d['label'], d['servedRps'],
            '%.4f' % ms(o['total']['meanNs']) if o.get('enabled') else '-',
            'on' if o.get('enabled') else 'off'))

    print()
    print('=== experiment 2: plateau gate, then the boundary ===')
    for arm, reg in REGISTERED.items():
        bpath = 'results/e2e/boundaries/%s-C0.json' % arm
        cell = {'registered': reg}
        pl = 'results/e2e/exp2-%s-plateau.json' % arm
        if os.path.exists(pl):
            d = json.load(open(pl))
            cell['plateauMeasured'] = round(d['servedRps'], 1)
            cell['plateauErrPct'] = round(100 * (d['servedRps'] - reg['plateau']) / reg['plateau'], 3)
            cell['plateauOverheadMs'] = round(ms(d['overhead']['total']['meanNs']), 4) \
                if d['overhead'].get('enabled') else None
        l99 = 'results/e2e/exp2-%s-load99.json' % arm
        if os.path.exists(l99):
            d = json.load(open(l99))
            cell['load99ServedRps'] = round(d['servedRps'], 1)
            cell['load99OverheadMs'] = round(ms(d['overhead']['total']['meanNs']), 4) \
                if d['overhead'].get('enabled') else None

        recs = [json.load(open(p)) for p in sorted(glob.glob('results/e2e/%s-*rl*-r*.json'
                                                             % ('e2e-' + arm)))]
        cyc = [run_cycle(r) for r in recs]
        cyc = [c for c in cyc if c]
        if cyc:
            cell['inSitu'] = {
                'runs': len(cyc),
                'meanCycleMs': round(statistics.median(c['meanMs'] for c in cyc), 4),
                'medianCycleMs': round(statistics.median(c['medianMs'] for c in cyc), 4),
                'overheadMs': round(statistics.median(c['overheadMs'] for c in cyc), 4),
                'sleepExcessMs': round(statistics.median(c['sleepExcessMs'] for c in cyc), 4),
                'requestsMeasured': sum(c['n'] for c in cyc),
            }
            mc = cell['inSitu']['meanCycleMs']
            cell['inSitu']['impliedCapacity'] = round(reg['conc'] / (mc / 1000.0), 1)
            cell['inSitu']['impliedRhoStar'] = round(
                cell['inSitu']['impliedCapacity'] / C_D, 4)

        if os.path.exists(bpath):
            b = json.load(open(bpath))
            bd = b['boundary']
            by = {p['rl']: p for p in b['points']}
            lo, hi = bd['lastSafeRl'], bd['firstNonSafeRl']
            cell['boundary'] = {
                'rlInterval': [lo, hi], 'endpointClass': bd['firstNonSafeClass'],
                'rhoStarInterval': bd['rhoStarInterval'],
                'rhoStarMid': round(sum(bd['rhoStarInterval']) / 2.0, 4),
                'probes': len(b['points']),
                'runs': sum(len(p['runs']) for p in b['points']),
                'spreadFlags': [p['rl'] for p in b['points']
                                if p.get('spreadExceedsResolution')],
            }
            # effective utilisation from each run's own measured cycle
            effs = []
            for r in recs:
                if r['params']['rateLimitRps'] != lo:
                    continue
                c = run_cycle(r)
                if not c:
                    continue
                run = next((x for x in by[lo]['runs'] if x['runId'] == r['runId']), None)
                if not run:
                    continue
                achieved = run['rhoAchieved'] * C_D
                effs.append(achieved * (c['meanMs'] / 1000.0) / reg['conc'])
            if effs:
                cell['boundary']['rhoEffectiveAtLastSafe'] = round(statistics.median(effs), 4)
                cell['boundary']['rhoEffectiveRange'] = [round(min(effs), 4), round(max(effs), 4)]
        out['cells'][arm] = cell

        print()
        print('--- %s ---' % arm)
        if 'plateauMeasured' in cell:
            print('  plateau      measured %.1f, predicted %.1f, error %+.2f%%  %s'
                  % (cell['plateauMeasured'], reg['plateau'], cell['plateauErrPct'],
                     'MATCHES' if abs(cell['plateauErrPct']) < 1.0 else 'DOES NOT MATCH'))
        if 'inSitu' in cell:
            s = cell['inSitu']
            print('  overhead     90%% load %.4f | saturated %.4f | IN SITU %.4f ms'
                  % (reg['ov90'], reg['ovSat'], s['overheadMs']))
            print('  cycle        mean %.4f ms, median %.4f ms (skewed), %d requests over %d runs'
                  % (s['meanCycleMs'], s['medianCycleMs'], s['requestsMeasured'], s['runs']))
            print('  in-situ implies capacity %.1f -> rho* %.4f'
                  % (s['impliedCapacity'], s['impliedRhoStar']))
        if 'boundary' in cell:
            b = cell['boundary']
            print('  boundary     rl [%d, %d] %s   rho* %s  mid %.4f'
                  % (b['rlInterval'][0], b['rlInterval'][1], b['endpointClass'],
                     b['rhoStarInterval'], b['rhoStarMid']))
            if 'rhoEffectiveAtLastSafe' in b:
                print('  measured effective utilisation at the last SAFE point: %.4f'
                      % b['rhoEffectiveAtLastSafe'])
            for name, key in [('saturated (registered)', 'rhoSat'), ('90% load', 'rho90')]:
                d = b['rhoStarMid'] - reg[key]
                print('    vs %-22s %.4f   diff %+.4f = %+.1f bisection steps'
                      % (name, reg[key], d, d / (RESOLUTION_RPS / C_D)))
            if 'inSitu' in cell:
                d = b['rhoStarMid'] - cell['inSitu']['impliedRhoStar']
                print('    vs %-22s %.4f   diff %+.4f = %+.1f bisection steps'
                      % ('in-situ prediction', cell['inSitu']['impliedRhoStar'], d,
                         d / (RESOLUTION_RPS / C_D)))

    mids = [c['boundary']['rhoStarMid'] for c in out['cells'].values() if 'boundary' in c]
    if len(mids) == 2:
        gap = abs(mids[1] - mids[0])
        out['residualGap'] = round(gap, 4)
        out['fractionRemoved'] = round(100 * (1 - gap / UNCORRECTED_GAP), 1)
        print()
        print('=== the gap ===')
        print('  uncorrected            0.0706')
        print('  predicted residual     0.0052   (registered, from saturated overhead)')
        print('  measured residual      %.4f   (%.1f%% of the uncorrected gap removed)'
              % (gap, out['fractionRemoved']))

    json.dump(out, open('results/E2E-analysis.json', 'w'), indent=2)
    print()
    print('wrote results/E2E-analysis.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
