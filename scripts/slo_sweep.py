#!/usr/bin/env python3
"""E2c: is rho* set by absolute service time, or by the ratio S/SLO?

E2b showed rho* tracks service time rather than concurrency. Both arms happen to
sit at a fixed S/SLO -- 5/250 = 2% and 25/250 = 10% -- so E2b cannot tell an
absolute-milliseconds effect from a ratio effect. This separates them offline by
recomputing vSLO at other SLO thresholds and asking whether the cells collapse
onto one curve against S/SLO.

METHOD. The pre-registered vSLO is: a second is violating when the live p99 over
a 5 s trailing window exceeds the SLO, OR the error rate over the same window
exceeds 1%; vSLO is violating seconds over T_full, with host-stall-contaminated
seconds removed from both numerator and denominator. Every input to that is
recorded per tick in each run's timeline -- liveP99Ms, errorRate, contaminated --
so the sweep replays the runner's own loop against a different threshold rather
than re-deriving anything from raw traces.

T_full is NOT held fixed. Stabilization requires the live p99 to sit under the
SLO for 15 consecutive seconds, so a tighter SLO delays T_full and a looser one
brings it forward. Holding T_full at its recorded value would understate the
effect of a tight threshold. The replay re-derives it.

Two consequences, both detected and reported rather than assumed away:

  - A run stops sampling once it stabilizes, so under a tight SLO the recorded
    timeline can end before a 15 s healthy streak ever forms. T_full is then not
    determinable from archived data and the run is marked INDETERMINATE. It is
    NOT silently treated as a violation.
  - The probed rl values are whatever each search happened to visit, so a
    boundary can be bracketed at a resolution coarser than the registered 5 rps,
    or fall outside the probed range entirely. Both are reported per cell.

Validation: at each cell's own recorded threshold the replay must reproduce the
recorded vSLO, vSLO_latency, vSLO_error and T_full. It does, for all 171 archived
runs. `--validate` re-runs that check.

Usage:
  python3 scripts/slo_sweep.py --validate
  python3 scripts/slo_sweep.py
"""
import argparse
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import (RESOLUTION_RPS, SAFE_MAX_VSLO, UNSAFE_MIN_REPS,  # noqa: E402
                             UNSAFE_MIN_VSLO, classify)

THRESHOLDS = [50, 100, 250, 500]
ERR_RATE = 0.01
# Pre-stated well-posedness rule, fixed before the boundaries were swept: the
# healthy system must meet the SLO with a 2x margin. Without it the SLO is not a
# recovery-headroom question, it is a question about idle latency.
BASELINE_MARGIN = 0.5

CELLS = [
    ('E1 c10/C0',    ['results/c10-c0-rl*-r*.json', 'results/e1b-c10-c0-*.json'],
     'results/boundaries/c10-C0.json', 5, 2000),
    ('E1 c10/C1',    ['results/c10-c1-rl*-r*.json', 'results/e1b-c10-c1-*.json'],
     'results/boundaries/c10-C1.json', 5, 1400),
    ('E1 c50/C0',    ['results/c50-c0-rl*-r*.json', 'results/e1b-c50-c0-*.json'],
     'results/boundaries/c50-C0.json', 25, 2000),
    ('E1 c50/C1',    ['results/c50-c1-rl*-r*.json'],
     'results/boundaries/c50-C1.json', 25, 1400),
    ('E2 c10@Q2500', ['results/e2/c10-Q2500/*-rl*-r*.json'],
     'results/e2/c10-Q2500/boundaries/c10-C0.json', 5, 2000),
    ('E2 c50@Q500',  ['results/e2/c50-Q500/*-rl*-r*.json'],
     'results/e2/c50-Q500/boundaries/c50-C0.json', 25, 2000),
    ('E2b C=400',    ['results/e2b/*-rl*-r*.json'],
     'results/e2b/boundaries/c50-C0.json', 25, 400),
]


def replay(rec, th, err_rate=ERR_RATE):
    """Re-run the runner's per-second loop against a different SLO threshold."""
    tl = rec.get('timeline') or []
    stab = rec['params'].get('stabilizeSeconds', 15)
    tdrain = rec.get('tDrainSec') or 0
    viol = viol_lat = viol_err = contam = 0
    streak = 0
    at_full = None
    for pt in tl:
        p99 = pt.get('liveP99Ms', 0.0)
        er = pt.get('errorRate', 0.0)
        cont = bool(pt.get('contaminated', False))
        lat, eb = p99 > th, er > err_rate
        if (lat or eb) and not cont:
            viol += 1
            viol_lat += 1 if lat else 0
            viol_err += 1 if eb else 0
        if cont:
            contam += 1
        drain_done = pt['tSec'] >= tdrain
        live_ok = p99 <= th and er <= err_rate and p99 > 0
        streak = streak + 1 if (drain_done and live_ok) else 0
        if drain_done and streak >= stab and at_full is None:
            at_full = (pt['tSec'], viol, viol_lat, viol_err, contam)
    if at_full is None:
        return None            # never stabilised inside the recorded timeline
    tfull, v, vl, ve, c = at_full
    den = tfull - c
    if den <= 0:
        den = tfull
    return {'tFullSec': tfull, 'vSLO': v / den, 'vSLO_latency': vl / den,
            'vSLO_error': ve / den, 'contaminated': c}


def baseline_p99(recs):
    """Live p99 in the settled window after T_full, across a cell's runs.

    Measured after stabilisation rather than inside the healthy streak: the
    streak is defined by p99 <= SLO, so any spread statistic taken inside it is
    conditioned on the very threshold under test.
    """
    v = []
    for rec in recs:
        tf = rec.get('tFullSec') or 0
        v += [pt['liveP99Ms'] for pt in (rec.get('timeline') or [])
              if pt['tSec'] > tf and pt['liveP99Ms'] > 0]
    if not v:
        return None
    return {'p50': statistics.median(v), 'max': max(v), 'n': len(v)}


def load_cell(globs, boundary_path):
    recs, rho = [], {}
    for g in globs:
        for p in sorted(glob.glob(g)):
            r = json.load(open(p))
            if r.get('timeline'):
                recs.append(r)
    if os.path.exists(boundary_path):
        b = json.load(open(boundary_path))
        for pt in b['points']:
            for run in pt['runs']:
                rho[run['runId']] = run['rhoAchieved']
    return recs, rho


def bracket(points):
    """[highest SAFE, lowest non-SAFE above it] among probed rates."""
    safe = sorted(rl for rl, c in points.items() if c == 'SAFE')
    if not safe:
        return None, 'every probed point is non-SAFE'
    lo = safe[-1]
    above = sorted(rl for rl, c in points.items() if rl > lo and c != 'SAFE')
    if not above:
        return None, 'every probed point is SAFE'
    return (lo, above[0]), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--validate', action='store_true')
    a = ap.parse_args()

    cells = {}
    for label, globs, bpath, S, C in CELLS:
        recs, rho = load_cell(globs, bpath)
        cells[label] = {'recs': recs, 'rho': rho, 'S': S, 'C': C}

    if a.validate:
        bad = n = 0
        for label, d in cells.items():
            for rec in d['recs']:
                out = replay(rec, rec['params']['sloP99Ms'])
                n += 1
                if out is None:
                    bad += 1
                    print('  %s: no T_full at its own threshold' % rec['runId'])
                    continue
                for k in ('vSLO', 'vSLO_latency', 'vSLO_error'):
                    if abs(out[k] - rec[k]) > 0.005:
                        bad += 1
                        print('  %s %s recorded %.4f replayed %.4f'
                              % (rec['runId'], k, rec[k], out[k]))
                        break
                else:
                    if abs(out['tFullSec'] - rec['tFullSec']) > 1.01:
                        bad += 1
                        print('  %s tFull recorded %.1f replayed %.1f'
                              % (rec['runId'], rec['tFullSec'], out['tFullSec']))
        print('validated %d runs, %d mismatches' % (n, bad))
        return 0 if bad == 0 else 1

    out = {'thresholds': THRESHOLDS, 'baselineMargin': BASELINE_MARGIN, 'cells': {}}
    for label, d in cells.items():
        base = baseline_p99(d['recs'])
        cell = {'S': d['S'], 'C': d['C'], 'baselineP99': base, 'byThreshold': {}}
        for th in THRESHOLDS:
            wellposed = base is not None and base['p50'] <= BASELINE_MARGIN * th
            pts, indet = {}, {}
            for rec in d['recs']:
                rl = rec['params']['rateLimitRps']
                r = replay(rec, th)
                if r is None:
                    indet.setdefault(rl, 0)
                    indet[rl] += 1
                    continue
                pts.setdefault(rl, []).append(r['vSLO'])
            classes = {}
            for rl, vs in pts.items():
                classes[rl] = 'INDETERMINATE' if rl in indet else classify(vs)
            for rl in indet:
                classes.setdefault(rl, 'INDETERMINATE')
            br, why = bracket({k: v for k, v in classes.items() if v != 'INDETERMINATE'})
            entry = {'wellPosed': wellposed, 'sOverSlo': d['S'] / float(th),
                     'classes': {str(k): v for k, v in sorted(classes.items())},
                     'vSLO': {str(k): [round(x, 4) for x in v] for k, v in sorted(pts.items())},
                     'indeterminate': {str(k): v for k, v in sorted(indet.items())}}
            if br:
                lo, hi = br
                rl_all = sorted(classes)
                rhos_lo = [d['rho'][r['runId']] for r in d['recs']
                           if r['params']['rateLimitRps'] == lo and r['runId'] in d['rho']]
                rhos_hi = [d['rho'][r['runId']] for r in d['recs']
                           if r['params']['rateLimitRps'] == hi and r['runId'] in d['rho']]
                entry['bracket'] = [lo, hi]
                entry['bracketWidthRps'] = hi - lo
                entry['atRegisteredResolution'] = (hi - lo) <= RESOLUTION_RPS
                if rhos_lo and rhos_hi:
                    entry['rhoStarInterval'] = [min(rhos_lo), max(rhos_hi)]
                    entry['rhoStarMid'] = round((min(rhos_lo) + max(rhos_hi)) / 2.0, 4)
            else:
                entry['bracket'] = None
                entry['whyNotBracketed'] = why
                rl_all = sorted(classes)
                # Name exact rates on the registered 5 rps grid, not a percentage
                # step: these are meant to be run as-is.
                if why.startswith('every probed point is non-SAFE'):
                    cands = [rl_all[0] - k * RESOLUTION_RPS for k in (1, 2, 3)]
                    entry['wouldBracket'] = {
                        'direction': 'below',
                        'lowestProbed': rl_all[0],
                        'probe': cands,
                        'note': 'the boundary is below every rate this cell probed; '
                                'run these three and the highest SAFE of them brackets '
                                'it against rl=%d' % rl_all[0]}
                else:
                    cands = [rl_all[-1] + k * RESOLUTION_RPS for k in (1, 2, 3)]
                    entry['wouldBracket'] = {
                        'direction': 'above',
                        'highestProbed': rl_all[-1],
                        'probe': cands,
                        'note': 'the boundary is above every rate this cell probed'}
            cell['byThreshold'][str(th)] = entry
        out['cells'][label] = cell

    json.dump(out, open('results/E2C-slo-sweep.json', 'w'), indent=2)
    print('wrote results/E2C-slo-sweep.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
