#!/usr/bin/env python3
"""E2d: is the boundary at effective utilisation 1.0, with configured C too high?

HYPOTHESIS. The downstream sizes itself as `ceil(C x S)` servers on the
assumption each turns a request round in exactly S. Given a fixed per-request
overhead `ov`, a server actually takes S+ov, so

    true capacity = C * S / (S + ov)
    rho*          = true / C = 1 / (1 + ov / S)

Short service times pay proportionally more for the same overhead, so the same
`ov` produces a low rho* in the S=5 arm and a high one in the S=25 arm. The claim
is that the boundary is always saturation and rho* differs only because C is a
differently-wrong estimate of truth in each cell.

TEST 1 estimates true capacity from archived data. TEST 2 recomputes every
boundary against it.

ESTIMATOR. True capacity is the maximum throughput the downstream sustains when
it always has work. Measured as the highest 30-second sustained served rate in
the drain window of each UNSAFE run, from the downstream's own cumulative
`served` counter.

Three weaker estimators were tried first and are kept as cross-checks, because
the choice of window changed the answer more than the choice of statistic did:

  - Endpoints across the whole drain window. Biased LOW: the backlog runs out at
    the end, the queue empties, and the server idles between requests. Those
    ticks are not measurements of capacity.
  - Endpoints while `queued >= concurrency`. Still biased low; the queue passes
    through that level on its way to empty. E2b's low ticks were all in its final
    twenty seconds.
  - Endpoints while `queued >= 5 x concurrency`. Arm-dependent in strictness --
    a queue of 50 for c10 against 250 for c50 -- which made the two arms
    incomparable, the defect it was meant to remove.

A maximum over sustained windows needs no queue threshold and cannot be dragged
down by desaturation. It can in principle be inflated by noise, but per-tick
variation inside the saturated stretch is about 0.4%, so over 30 seconds that is
under 0.1%.

Under C1 the window starts after the capacity step at t=20: earlier ticks were
served at the pre-fault capacity and belong to a different configuration.

Usage: python3 scripts/capacity_calibration.py
"""
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import RESOLUTION_RPS  # noqa: E402

WINDOW_SEC = 30.0
SETTLE_SEC = 5.0
CLAIMED_OVERHEAD_MS = 0.46

CELLS = [
    ('E1 c10/C0', ['results/c10-c0-rl*-r*.json', 'results/e1b-c10-c0-*.json'],
     'results/boundaries/c10-C0.json', 5),
    ('E1 c10/C1', ['results/c10-c1-rl*-r*.json', 'results/e1b-c10-c1-*.json'],
     'results/boundaries/c10-C1.json', 5),
    ('E1 c50/C0', ['results/c50-c0-rl*-r*.json', 'results/e1b-c50-c0-*.json'],
     'results/boundaries/c50-C0.json', 25),
    ('E1 c50/C1', ['results/c50-c1-rl*-r*.json'],
     'results/boundaries/c50-C1.json', 25),
    ('E2 c10@Q2500', ['results/e2/c10-Q2500/*-rl*-r*.json'],
     'results/e2/c10-Q2500/boundaries/c10-C0.json', 5),
    ('E2 c50@Q500', ['results/e2/c50-Q500/*-rl*-r*.json'],
     'results/e2/c50-Q500/boundaries/c50-C0.json', 25),
    ('E2b C=400', ['results/e2b/*-rl*-r*.json'],
     'results/e2b/boundaries/c50-C0.json', 25),
]


def fault_capacity(rec):
    nominal = rec['params'].get('nominalCapacity', 2000)
    for step in rec.get('capacitySchedule', []):
        if step['rate'] < nominal:
            return step['rate']
    return nominal


def window_start(rec):
    steps = [s['atSec'] for s in (rec.get('capacitySchedule') or []) if s['atSec'] > 0]
    return max([SETTLE_SEC] + [s + SETTLE_SEC for s in steps])


def max_sustained(rec):
    """Highest 30 s sustained served rate in the drain window."""
    tl = rec.get('timeline') or []
    td = rec.get('tDrainSec') or 0
    w = [p for p in tl if window_start(rec) <= p['tSec'] <= td and not p.get('contaminated')]
    best = None
    for i in range(len(w)):
        for j in range(i + 1, len(w)):
            dt = w[j]['tSec'] - w[i]['tSec']
            if dt < WINDOW_SEC:
                continue
            if dt > WINDOW_SEC + 1.5:
                break
            r = (w[j]['served'] - w[i]['served']) / dt
            if best is None or r > best:
                best = r
            break
    return best


def whole_window_endpoints(rec):
    """The naive estimator, kept as the cross-check that motivated the switch."""
    tl = rec.get('timeline') or []
    td = rec.get('tDrainSec') or 0
    w = [p for p in tl if window_start(rec) <= p['tSec'] <= td and not p.get('contaminated')]
    if len(w) < 10:
        return None
    dt = w[-1]['tSec'] - w[0]['tSec']
    return (w[-1]['served'] - w[0]['served']) / dt if dt > 0 else None


def per_tick_cv(rec):
    tl = rec.get('timeline') or []
    td = rec.get('tDrainSec') or 0
    conc = rec['params'].get('downstreamConcurrency', 1)
    r = [p['offeredRate'] for p in tl
         if window_start(rec) <= p['tSec'] <= td and p.get('queued', 0) >= 5 * conc
         and p.get('offeredRate')]
    if len(r) < 5 or not statistics.mean(r):
        return None
    return statistics.pstdev(r) / statistics.mean(r)


def main():
    out = {'windowSec': WINDOW_SEC, 'claimedOverheadMs': CLAIMED_OVERHEAD_MS, 'cells': {}}

    print('TEST 1 — true capacity from the sustained plateau at UNSAFE points')
    print()
    print('%-14s %3s %6s %5s %10s %10s %9s %8s %7s' % (
        'cell', 'S', 'C_d', 'runs', 'true cap', 'naive', 'pred@0.46', 'ov (ms)', 'CV'))
    for label, globs, bpath, S in CELLS:
        b = json.load(open(bpath))
        unsafe = {p['rl'] for p in b['points'] if p['class'] != 'SAFE'}
        caps, naive, cvs, cd = [], [], [], None
        for g in globs:
            for p in sorted(glob.glob(g)):
                rec = json.load(open(p))
                if not rec.get('timeline') or rec['params']['rateLimitRps'] not in unsafe:
                    continue
                m = max_sustained(rec)
                if not m:
                    continue
                cd = fault_capacity(rec)
                caps.append(m)
                n = whole_window_endpoints(rec)
                if n:
                    naive.append(n)
                c = per_tick_cv(rec)
                if c:
                    cvs.append(c)
        if not caps:
            continue
        true = statistics.median(caps)
        ov = S * (cd / true - 1.0)
        pred = cd * S / (S + CLAIMED_OVERHEAD_MS)
        out['cells'][label] = {
            'S': S, 'faultCapacity': cd, 'nUnsafeRuns': len(caps),
            'trueCapacity': round(true, 1),
            'trueCapacityMin': round(min(caps), 1), 'trueCapacityMax': round(max(caps), 1),
            'naiveWholeWindow': round(statistics.median(naive), 1) if naive else None,
            'perTickCV': round(statistics.median(cvs), 4) if cvs else None,
            'impliedOverheadMs': round(ov, 3),
            'predictedAt046': round(pred, 1),
            'predErrPct': round(100 * (true - pred) / pred, 3),
        }
        print('%-14s %3d %6d %5d %10.1f %10.1f %9.1f %8.3f %7.4f' % (
            label, S, cd, len(caps), true,
            statistics.median(naive) if naive else 0, pred, ov,
            statistics.median(cvs) if cvs else 0))

    ovs = [c['impliedOverheadMs'] for c in out['cells'].values()]
    out['overheadMs'] = {'min': min(ovs), 'max': max(ovs),
                         'median': round(statistics.median(ovs), 3),
                         'sd': round(statistics.pstdev(ovs), 4),
                         'cvPct': round(100 * statistics.pstdev(ovs) / statistics.mean(ovs), 2)}
    print()
    print('implied overhead: %.3f - %.3f ms, median %.3f, SD %.4f (CV %.1f%%)' % (
        min(ovs), max(ovs), statistics.median(ovs), statistics.pstdev(ovs),
        100 * statistics.pstdev(ovs) / statistics.mean(ovs)))
    errs = [abs(c['predErrPct']) for c in out['cells'].values()]
    print('every measured plateau is within %.2f%% of the value predicted at ov=0.46 ms'
          % max(errs))

    print()
    print('TEST 2 — the boundary against true capacity instead of configured C')
    print()
    print('%-14s %-20s %-22s %8s' % ('cell', 'rho* vs configured C',
                                     'rho_eff vs true cap', 'brackets 1.0'))
    for label, globs, bpath, S in CELLS:
        if label not in out['cells']:
            continue
        c = out['cells'][label]
        b = json.load(open(bpath))
        bd = b['boundary']
        by = {p['rl']: p for p in b['points']}
        lo_rho = min(by[bd['lastSafeRl']]['rhoAchieved'])
        hi_rho = max(by[bd['firstNonSafeRl']]['rhoAchieved'])
        lo_eff = lo_rho * c['faultCapacity'] / c['trueCapacity']
        hi_eff = hi_rho * c['faultCapacity'] / c['trueCapacity']
        c['rhoStarInterval'] = [round(lo_rho, 4), round(hi_rho, 4)]
        c['rhoEffInterval'] = [round(lo_eff, 4), round(hi_eff, 4)]
        c['bracketsUnity'] = bool(lo_eff <= 1.0 <= hi_eff)
        c['resolutionInEff'] = round(RESOLUTION_RPS / c['trueCapacity'], 4)
        print('%-14s [%.4f, %.4f]     [%.4f, %.4f]      %s' % (
            label, lo_rho, hi_rho, lo_eff, hi_eff, 'yes' if c['bracketsUnity'] else 'NO'))

    mids_c = [statistics.mean(c['rhoStarInterval']) for c in out['cells'].values()]
    mids_e = [statistics.mean(c['rhoEffInterval']) for c in out['cells'].values()]
    nb = [l for l, c in out['cells'].items() if not c['bracketsUnity']]
    out['collapse'] = {
        'rhoStarSpread': round(max(mids_c) - min(mids_c), 4),
        'rhoStarSD': round(statistics.pstdev(mids_c), 4),
        'rhoEffSpread': round(max(mids_e) - min(mids_e), 4),
        'rhoEffSD': round(statistics.pstdev(mids_e), 4),
        'rhoEffMedian': round(statistics.median(mids_e), 4),
        'cellsBracketingUnity': len(out['cells']) - len(nb),
        'cellsTotal': len(out['cells']),
        'notBracketing': nb,
        'worstResolutionInEff': round(max(c['resolutionInEff'] for c in out['cells'].values()), 4),
    }
    print()
    print('interval midpoints, spread across cells:')
    print('  against configured C : %.4f   (SD %.4f)' % (max(mids_c) - min(mids_c),
                                                         statistics.pstdev(mids_c)))
    print('  against true capacity: %.4f   (SD %.4f)   median %.4f' % (
        max(mids_e) - min(mids_e), statistics.pstdev(mids_e), statistics.median(mids_e)))
    print('  collapse factor: %.1fx' % ((max(mids_c) - min(mids_c)) / (max(mids_e) - min(mids_e))))
    print('  cells whose interval brackets 1.0: %d of %d%s' % (
        out['collapse']['cellsBracketingUnity'], len(out['cells']),
        '' if not nb else '   (not: %s)' % ', '.join(nb)))
    print('  coarsest 5 rps resolution in effective units: %.4f'
          % out['collapse']['worstResolutionInEff'])

    json.dump(out, open('results/E2D-capacity-calibration.json', 'w'), indent=2)
    print()
    print('wrote results/E2D-capacity-calibration.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
