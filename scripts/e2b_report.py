#!/usr/bin/env python3
"""Generate results/E2B-REPORT.md from the boundary file and run records.

One cell, one question: at concurrency 10 with c50's service time and cap-in-ms,
is rho* c10-like or c50-like? Every number computed here; nothing typed in.

Runs against a partial campaign, printing pending rather than omitting.

Usage: python3 scripts/e2b_report.py > results/E2B-REPORT.md
"""
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bimodality import shape  # noqa: E402

BOUNDARY = 'results/e2b/boundaries/c50-C0.json'
RECORDS = 'results/e2b'
# Registered in E2B-PLAN.md before the instance was started.
RHO10, RHO50 = 0.9137, 0.9826
D = round(RHO50 - RHO10, 4)
DEEP = 50
CAP, C, LAMBDA_L, S_MS = 500, 400, 200, 25


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def verdict(h):
    """E2B-PLAN, with the dead band registered before any data existed."""
    if h is None:
        return None
    if -0.25 <= h <= 0.25:
        return 'CONCURRENCY GOVERNS'
    if 0.75 <= h <= 1.25:
        return 'S GOVERNS'
    if h < -0.25 or h > 1.25:
        return 'OFF-SCALE'
    return 'INTERMEDIATE'


def main():
    b = load(BOUNDARY)
    recs = sorted(glob.glob(os.path.join(RECORDS, '*-rl*-r*.json')))
    out = []
    w = out.append

    w('# E2b — concurrency or service time?')
    w('')
    w('**Data only.** Readings registered in `results/E2B-PLAN.md` before the '
      'instance was started. Go harness pinned at `026be6242d26`, the commit used '
      'by E1, E1B and E2.')
    w('')
    w('## The condition')
    w('')
    w('| | value | matches |')
    w('|---|---:|---|')
    w('| C | %d | neither — E1 and E2 ran at 2000 |' % C)
    w('| S | %d ms | **c50** |' % S_MS)
    w('| lambda_L | %d | lambda_L/C = 0.5, as everywhere |' % LAMBDA_L)
    w('| concurrency | 10 | **c10** |')
    w('| queue cap | %d | derived, not forced |' % CAP)
    w('| cap-in-ms | 1250 | **c50** |')
    w('')
    if recs:
        p = json.load(open(recs[0]))['params']
        ok = sum(1 for r in recs
                 if json.load(open(r))['params']['downstreamQueueCap'] == CAP
                 and json.load(open(r))['params']['downstreamServiceTimeMs'] == S_MS
                 and json.load(open(r))['params']['downstreamConcurrency'] == 10
                 and json.load(open(r))['params']['nominalCapacity'] == C
                 and json.load(open(r))['params']['liveRatePerSec'] == LAMBDA_L)
        w('Asserted on every one of the %d records: cap %s, S %s ms, concurrency %s, '
          'C %s, lambda_L %s. Conforming: **%d of %d**.'
          % (len(recs), p['downstreamQueueCap'], p['downstreamServiceTimeMs'],
             p['downstreamConcurrency'], p['nominalCapacity'], p['liveRatePerSec'],
             ok, len(recs)))
        w('')
        w('The record field `concurrencyArm` reads `c50`. That names the **service '
          'time**, not the concurrency, which is %s here. The arm labels were named '
          'for the concurrency each arm has at C=2000.' % p['downstreamConcurrency'])
        w('')

    w('## Result')
    w('')
    if not b:
        w('_Boundary search in progress._')
        w('')
    else:
        bd = b['boundary']
        i = bd['rhoStarInterval']
        m = (i[0] + i[1]) / 2.0
        h = (m - RHO10) / D
        w('| | |')
        w('|---|---|')
        w('| rl interval | **[%d, %d]** %s |' % (bd['lastSafeRl'], bd['firstNonSafeRl'],
                                                 bd['firstNonSafeClass']))
        w('| rho* interval (A4) | **[%.4f, %.4f]** |' % (i[0], i[1]))
        w('| width | %.4f |' % (i[1] - i[0]))
        w('| midpoint | %.4f |' % m)
        w('| probes / runs | %d / %d |' % (len(b['points']),
                                           sum(len(p['runs']) for p in b['points'])))
        w('| spread-diagnostic flags | %s |'
          % ([p['rl'] for p in b['points'] if p.get('spreadExceedsResolution')] or 'none'))
        w('')
        w('```')
        w('h = (rho* - rho10) / D = (%.4f - %.4f) / %.4f = %+.3f' % (m, RHO10, D, h))
        w('```')
        w('')
        w('| hypothesis | predicted rho* | predicted rl | distance from observed |')
        w('|---|---:|---:|---:|')
        for name, rho in [('c10-like: concurrency governs', RHO10),
                          ('c50-like: S governs', RHO50)]:
            w('| %s | %.4f | %d | %+.4f |'
              % (name, rho, round((rho * C - LAMBDA_L) / 5) * 5, m - rho))
        w('')
        w('### Registered verdict: **%s**' % verdict(h))
        w('')
        w('Bands fixed in E2B-PLAN before the instance was started: concurrency for '
          '`-0.25 <= h <= 0.25`, S for `0.75 <= h <= 1.25`, intermediate between, '
          'off-scale outside. The dead band was registered in advance, which is the '
          'E2 defect corrected rather than repeated.')
        w('')
        w('At C=%d the 5 rps resolution is a rho resolution of %.4f, so **h resolves '
          'to about +/-%.2f**. The two hypotheses are %.1f quanta apart, which is why '
          'this reading holds; a finer reading within the intermediate band would not, '
          'and none is offered.'
          % (C, 5.0 / C, (5.0 / C) / D, D / (5.0 / C)))
        w('')
        w('### Every probed point')
        w('')
        w('| rl | nominal rho | class | n | vSLO per rep | rho (A4) | median rec rps |')
        w('|---:|---:|---|---:|---|---|---:|')
        for pt in sorted(b['points'], key=lambda x: x['rl']):
            rec = [r.get('recoveryAchievedRps') for r in pt['runs']]
            rec = [x for x in rec if x is not None]
            rhos = pt['rhoAchieved']
            mark = '**' if pt['rl'] in (bd['lastSafeRl'], bd['firstNonSafeRl']) else ''
            w('| %s%d%s | %.4f | %s | %d | %s | %s | %s |'
              % (mark, pt['rl'], mark, (LAMBDA_L + pt['rl']) / float(C), pt['class'],
                 len(pt['runs']),
                 ', '.join('%.4f' % v for v in pt['vSLO'][:6])
                 + (' ...' if len(pt['vSLO']) > 6 else ''),
                 '%.4f-%.4f' % (min(rhos), max(rhos)) if len(set(rhos)) > 1
                 else '%.4f' % rhos[0],
                 '%.1f' % statistics.median(rec) if rec else 'n/a'))
        w('')
        firsts = {}
        for pth in recs:
            r = json.load(open(pth))
            firsts.setdefault(r['params']['rateLimitRps'], []).append(r['startedAt'])
        seq = [rl for _, rl in sorted((min(v), rl) for rl, v in firsts.items())]
        w('Probe order from run timestamps: %s.' % ' -> '.join(str(x) for x in seq))
        w('')

    # ---- occupancy, DEEP, and cap binding ------------------------------
    if b:
        rl = b['boundary']['lastSafeRl']
        q, v, pk = [], [], []
        for pth in sorted(glob.glob(os.path.join(RECORDS, '*-rl%d-r*.json' % rl))):
            r = json.load(open(pth))
            q.append(r['supplementary']['drainQueueDepthMean'])
            pk.append(r['supplementary']['drainQueueDepthPeak'])
            v.append(r['vSLO'])
        w('## Occupancy and depth at the last SAFE point (rl=%d)' % rl)
        w('')
        if len(q) < 4:
            w('_Replication in progress: %d of 12 runs._' % len(q))
            w('')
        else:
            sh = shape(q)
            deep = sum(1 for x in q if x >= DEEP)
            w('| | |')
            w('|---|---|')
            w('| n | %d |' % len(q))
            w('| DEEP (`drainQueueDepthMean` >= %d) | **%d/%d** |' % (DEEP, deep, len(q)))
            w('| median qMean | %.2f (%.2f%% of cap %d) |'
              % (sh['median'], 100.0 * sh['median'] / CAP, CAP))
            w('| gapRatio / dipGap / BC | %s / %s / %s |'
              % (sh['gapRatio'], sh['dipGap'], sh['bimodalityCoefficient']))
            w('| max vSLO | %.4f |' % max(v))
            w('')
            w('Sorted: %s' % ' '.join('%.1f' % x for x in sorted(q)))
            w('')
        # cap binding, requested in the brief
        w('### Does the queue peak bind the cap at any SAFE point?')
        w('')
        w('E2\'s null has a candidate mechanism: across all six cells measured '
          'before this one, the median queue peak at the last SAFE point sat below '
          'the cap, 1.5%% to 50.6%% of it. The brief asks for the same check at a '
          'fifth of the absolute rate.')
        w('')
        w('| rl | class | n | cap | median peak | %% of cap | max peak | %% of cap | reaches cap |')
        w('|---:|---|---:|---:|---:|---:|---:|---:|---|')
        by = {}
        for pth in recs:
            r = json.load(open(pth))
            d = by.setdefault(r['params']['rateLimitRps'], {'pk': [], 'v': []})
            d['pk'].append(r['supplementary']['drainQueueDepthPeak'])
            d['v'].append(r['vSLO'])
        any_safe_binds = False
        for rate in sorted(by):
            d = by[rate]
            safe = max(d['v']) <= 0.01
            mp, xp = statistics.median(d['pk']), max(d['pk'])
            if safe and xp >= CAP:
                any_safe_binds = True
            w('| %d | %s | %d | %d | %.1f | %.1f%% | %d | %.1f%% | %s |'
              % (rate, 'SAFE' if safe else 'non-SAFE', len(d['pk']), CAP, mp,
                 100.0 * mp / CAP, xp, 100.0 * xp / CAP,
                 '**yes**' if xp >= CAP else 'no'))
        w('')
        w('**%s**' % ('At least one SAFE point reaches the cap, so the cap is a '
                      'binding constraint here and E2\'s non-binding-cap mechanism '
                      'does not carry over unchanged to C=400.' if any_safe_binds else
                      'No SAFE point reaches the cap. The cap is not a binding '
                      'constraint where the boundary is set, as in all six earlier '
                      'cells, now confirmed at a fifth of the absolute rate.'))
        w('')

    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
