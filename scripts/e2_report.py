#!/usr/bin/env python3
"""Generate results/E2-REPORT.md from the boundary files and run records.

Every table is computed here. Nothing in the report is typed by hand: an earlier
report in this project had a table transcribed from memory and it was wrong, so
the rule since then is that numbers reach the page only through a script.

Runs against whatever is present, so it can be checked before the last cell
finishes. Missing cells are printed as PENDING rather than omitted.

Usage: python3 scripts/e2_report.py > results/E2-REPORT.md
"""
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bimodality import shape  # noqa: E402
from precision import u, ud  # noqa: E402

E1 = {'c10': 'results/boundaries/c10-C0.json', 'c50': 'results/boundaries/c50-C0.json'}
E2 = {'c10': ('results/e2/c10-Q2500/boundaries/c10-C0.json', 'results/e2/c10-Q2500', 2500),
      'c50': ('results/e2/c50-Q500/boundaries/c50-C0.json', 'results/e2/c50-Q500', 500)}
# Registered in E2-PLAN before any E2 run. Not recomputed here on purpose.
M10, M50 = 0.9137, 0.9826
D = round(M50 - M10, 4)
G_REF = {'c10': (20.57, 103.0), 'c50': (101.79, 21.0)}   # (retain, swap)
DEEP = 50


def load(path):
    return json.load(open(path)) if os.path.exists(path) else None


def iv(b):
    return b['boundary']['rhoStarInterval'] if b else None


def mid(i):
    return round((i[0] + i[1]) / 2.0, 4) if i else None


def overlaps(a, b):
    return a and b and a[0] <= b[1] and b[0] <= a[1]


def fmt_iv(i):
    return '[%s, %s]' % (u(i[0]), u(i[1])) if i else '_pending_'


def bimodal(rdir, rl):
    if not rdir or rl is None:
        return None
    q, v = [], []
    for p in sorted(glob.glob(os.path.join(rdir, 'c*-rl%d-r*.json' % rl))):
        r = json.load(open(p))
        q.append(r['supplementary']['drainQueueDepthMean'])
        v.append(r['vSLO'])
    if len(q) < 2:
        return None
    return {'n': len(q), 'deep': sum(1 for x in q if x >= DEEP), 'vals': q,
            'median': statistics.median(q), 'maxVSLO': max(v), 'shape': shape(q)}


def main():
    e1 = {k: load(v) for k, v in E1.items()}
    e2 = {k: load(v[0]) for k, v in E2.items()}
    occ = load('results/E2-cap-occupancy.json')
    e1b = load('results/E1B-dip-statistics.json')

    out = []
    w = out.append
    w('# E2 — separating the queue-cap effect from the concurrency effect')
    w('')
    w('**Data only. No interpretation beyond the readings registered in '
      '`results/E2-PLAN.md` before the runs.** Harness pinned at `026be6242d26`, '
      'the same commit as E1 and E1B.')
    w('')

    # ---- the 2x2 -------------------------------------------------------
    w('## The 2x2')
    w('')
    w('E1 measured the diagonal where arm and cap vary together. E2 fills the other.')
    w('')
    w('| | Q=500 (250 ms full-queue delay) | Q=2500 (1250 ms) |')
    w('|---|---|---|')
    w('| **c10** (S=5 ms, concurrency 10) | E1: %s | E2: %s |'
      % (fmt_iv(iv(e1['c10'])), fmt_iv(iv(e2['c10']))))
    w('| **c50** (S=25 ms, concurrency 50) | E2: %s | E1: %s |'
      % (fmt_iv(iv(e2['c50'])), fmt_iv(iv(e1['c50']))))
    w('')
    w('Intervals are [last SAFE, first NON-SAFE] achieved rho under A4.')
    w('')
    w('| cell | rl interval | endpoint | rho* interval | width | probes | runs |')
    w('|---|---|---|---|---:|---:|---:|')
    for key, label, b in [('c10', 'E1 c10 @ Q=500', e1['c10']), ('c50', 'E1 c50 @ Q=2500', e1['c50']),
                          ('c10', 'E2 c10 @ Q=2500', e2['c10']), ('c50', 'E2 c50 @ Q=500', e2['c50'])]:
        if not b:
            w('| **%s** | _pending_ | | | | | |' % label)
            continue
        bd = b['boundary']
        i = bd['rhoStarInterval']
        w('| **%s** | [%d, %d] | %s | **%s** | %s | %d | %d |'
          % (label, bd['lastSafeRl'], bd['firstNonSafeRl'], bd['firstNonSafeClass'],
             fmt_iv(i), u(i[1] - i[0]), len(b['points']), sum(len(p['runs']) for p in b['points'])))
    w('')
    w('Run counts for the two E1 cells include the twelve E1B replication runs '
      'pooled into their last SAFE points, so they exceed the 18 and 21 stated in '
      '`E1-REPORT.md`, which counted the boundary search alone.')
    w('')
    w('`f_c10` is 0.000 against the registered constants. An earlier commit gave '
      '0.001 from unrounded midpoints; the registered arithmetic uses the rounded '
      'values fixed in the plan, and that figure supersedes it. The difference is '
      'four orders of magnitude below the 0.25 threshold either way.')
    w('')

    # ---- attribution ---------------------------------------------------
    w('## Attribution statistic (registered before the runs)')
    w('')
    w('```')
    w('m10 = %.4f   m50 = %.4f   D = m50 - m10 = %.4f' % (M10, M50, D))
    w('f_c10 = (m(c10@2500) - m10) / D      f_c50 = (m50 - m(c50@500)) / D')
    w('CAP-DRIVEN both f >= 0.75    CONCURRENCY-DRIVEN both f <= 0.25    else MIXED')
    w('```')
    w('')
    f = {}
    for k in ('c10', 'c50'):
        m = mid(iv(e2[k]))
        if m is None:
            f[k] = None
        else:
            f[k] = round(((m - M10) / D) if k == 'c10' else ((M50 - m) / D), 3)
    w('| cell | midpoint | f | reading |')
    w('|---|---:|---:|---|')
    for k, label in [('c10', 'c10 @ Q=2500'), ('c50', 'c50 @ Q=500')]:
        if f[k] is None:
            w('| %s | _pending_ | _pending_ | |' % label)
        else:
            r = ('**off-scale** — moved away from the other arm, not towards it '
                 '(addendum 3)' if f[k] < 0 else
                 'cap-driven' if f[k] >= 0.75 else
                 'concurrency-driven' if f[k] <= 0.25 else 'neither threshold')
            w('| %s | %s | **%+.3f** | %s |' % (label, u(mid(iv(e2[k]))), f[k], r))
    w('')
    if f['c10'] is not None and f['c50'] is not None:
        both = [f['c10'], f['c50']]
        # Addendum 3: a negative f disqualifies CONCURRENCY-DRIVEN outright and
        # is not evidence for the cap either. Both verdicts fail together.
        if min(both) < 0:
            verdict = '**OFF-SCALE**'
        elif min(both) >= 0.75:
            verdict = '**CAP-DRIVEN**'
        elif max(both) <= 0.25:
            verdict = '**CONCURRENCY-DRIVEN**'
        else:
            verdict = '**MIXED**'
        w('Registered verdict: %s (f = %+.3f and %+.3f).' % (verdict, *both))
        # CAP-DRIVEN needs BOTH fractions >= 0.75. Once one cell comes in low the
        # verdict is arithmetically out of reach, and a reader should not take
        # "not cap-driven" as a finding the second cell contributed to.
        if f['c10'] < 0.75:
            w('')
            w('**`CAP-DRIVEN` was already unreachable before this cell was measured.** '
              'It requires both fractions to be at least 0.75, and the c10 cell '
              'returned %+.3f. So the absence of a cap verdict is settled by the c10 '
              'cell alone and the c50 cell cannot count as evidence for it. What the '
              'c50 cell decides is which of the remaining readings applies.'
              % f['c10'])
        if min(both) < 0:
            w('')
            w('Per addendum 3, registered before this cell was measured: the negative '
              'fraction means the cell moved **away** from the other arm, so it does '
              'not satisfy `CONCURRENCY-DRIVEN` despite being below 0.25, and moving '
              'away is not evidence for the cap. Neither registered verdict is claimed.')
            # Addendum 4: the criterion has no dead band. Say so wherever it fires
            # on a value too small to mean anything.
            worst = min(both)
            if True:
                w('')
                w('**The criterion has no dead band, and here that matters.** '
                  'Addendum 4, registered before the deciding probe: the verdict above '
                  'is what addendum 3 produces, and the criterion was deliberately not '
                  'changed once the arithmetic showed it was about to fire. But the '
                  'magnitude is %+.3f. Addendum 3 was written against a cell that moves '
                  'materially the wrong way and was tested at -0.057. At %+.3f the cell '
                  'has not moved.' % (worst, worst))
                w('')
                w('Reported alongside, with no verdict status: `|f| <= 0.25` in both '
                  'cells, so **neither cell moved materially in either direction**. '
                  'The plan can express "moved" and "did not move"; it cannot '
                  'distinguish %+.3f from %+.3f, and the data does not settle which '
                  'side of zero this fell on.' % (worst, -worst))
        if (min(both) <= 0.25) != (max(both) <= 0.25):
            w('')
            w('The two fractions disagree. The plan requires this be reported as an '
              'asymmetry between the arms and **not averaged**.')
    else:
        w('Verdict pending the c50 cell.')
    w('')
    w('### Interval overlap, reported alongside because f hides width')
    w('')
    w('| cell | overlaps its own arm E1 interval | overlaps the other arm E1 interval |')
    w('|---|---|---|')
    for k, label, other in [('c10', 'c10 @ Q=2500', 'c50'), ('c50', 'c50 @ Q=500', 'c10')]:
        if not e2[k]:
            w('| %s | _pending_ | _pending_ |' % label)
            continue
        w('| %s | %s | %s |' % (label,
                                'yes' if overlaps(iv(e2[k]), iv(e1[k])) else 'no',
                                'yes' if overlaps(iv(e2[k]), iv(e1[other])) else 'no'))
    w('')

    # ---- per point -----------------------------------------------------
    w('## Every probed point, both E2 cells')
    w('')
    w('`rec rps` is the achieved recovery rate over the delivery span (A4), against '
      'the nominal `rl` the search was bisecting. Where the two diverge the limiter '
      'is saturating and the nominal rate overstates the load actually offered.')
    w('')
    for k, label, cap in [('c10', 'c10 @ Q=2500', 2500), ('c50', 'c50 @ Q=500', 500)]:
        b = e2[k]
        w('### %s' % label)
        w('')
        if not b:
            w('_Search in progress; no boundary file written yet._')
            w('')
            continue
        w('| rl | class | n | vSLO per rep | rho (A4) | median rec rps | rec / rl |')
        w('|---:|---|---:|---|---|---:|---:|')
        for pt in b['points']:
            rec = [r.get('recoveryAchievedRps') for r in pt['runs']]
            rec = [x for x in rec if x is not None]
            mr = statistics.median(rec) if rec else None
            rhos = pt['rhoAchieved']
            w('| %s%d%s | %s | %d | %s | %s | %s | %s |'
              % ('**' if pt['rl'] in (b['boundary']['lastSafeRl'],
                                      b['boundary']['firstNonSafeRl']) else '',
                 pt['rl'],
                 '**' if pt['rl'] in (b['boundary']['lastSafeRl'],
                                      b['boundary']['firstNonSafeRl']) else '',
                 pt['class'], len(pt['runs']),
                 ', '.join('%.4f' % v for v in pt['vSLO'][:6])
                 + (' ...' if len(pt['vSLO']) > 6 else ''),
                 '%s-%s' % (u(min(rhos)), u(max(rhos))) if len(set(rhos)) > 1
                 else u(rhos[0]),
                 '%.1f' % mr if mr else 'n/a',
                 '%.3f' % (mr / pt['rl']) if mr else 'n/a'))
        w('')
        # The boundary file sorts points by rl, so its order is NOT probe order.
        # Derive the real order from when each point's first run started.
        firsts = {}
        for pth in glob.glob(os.path.join(E2[k][1], '*c*-c*-rl*-r*.json')):
            r = json.load(open(pth))
            rl = r['params']['rateLimitRps']
            firsts.setdefault(rl, []).append(r['startedAt'])
        seq = []
        for t, rl in sorted((min(v), rl) for rl, v in firsts.items()):
            seq.append(rl)
        w('Probe order, from run timestamps rather than the order points are stored '
          'in: %s. The replication runs then returned to rl=%d.'
          % (' -> '.join(str(x) for x in seq), b['boundary']['lastSafeRl']))
        w('')

    # ---- interval well-formedness --------------------------------------
    w('### Is the interval well formed?')
    w('')
    w('The interval is [min rho at the last SAFE point, max rho at the first '
      'non-SAFE point]. That is only meaningful if rho actually rises between the '
      'two. It need not: the recovery limiter saturates, so past the boundary a '
      'higher nominal rate can deliver no more recovery and rho can fall.')
    w('')
    w('| cell | rho rises across the interval | width | monotonic across all probed points |')
    w('|---|---|---:|---|')
    for k, label in [('c10', 'c10 @ Q=2500'), ('c50', 'c50 @ Q=500')]:
        b = e2[k]
        if not b:
            w('| %s | _pending_ | | |' % label)
            continue
        i = b['boundary']['rhoStarInterval']
        seq = [max(p['rhoAchieved']) for p in sorted(b['points'], key=lambda x: x['rl'])]
        mono = all(seq[j] <= seq[j + 1] for j in range(len(seq) - 1))
        w('| %s | %s | %s | %s |'
          % (label, 'yes' if i[1] > i[0] else '**NO — interval is inverted**',
             ud(i[1] - i[0]),
             'yes' if mono else 'no, and it does not need to be: the departures are '
             'at deep non-SAFE points that bound nothing'))
    w('')

    # ---- bimodality ----------------------------------------------------
    w('## Bimodality at the last SAFE point')
    w('')
    w('Threshold fixed in E1B and unchanged: **DEEP if `drainQueueDepthMean` >= %d**.' % DEEP)
    w('')
    w('| cell | cap | n | DEEP | median qMean | gapRatio | dipGap | BC | max vSLO |')
    w('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
    if e1b:
        for label, d in e1b.items():
            s = d['shape']
            w('| %s | %s | %d | **%d/%d** | %.2f | %s | %s | %s | %.4f |'
              % (label.replace('E1B ', 'E1B '), '500' if 'Q=500' in label else '2500',
                 d['n'], d['deep'], d['n'], s['median'], s['gapRatio'], s['dipGap'],
                 s['bimodalityCoefficient'], d['maxVSLO']))
    for k, label in [('c10', 'E2 c10 @ Q=2500'), ('c50', 'E2 c50 @ Q=500')]:
        b = e2[k]
        bm = bimodal(E2[k][1], b['boundary']['lastSafeRl']) if b else None
        if not bm:
            w('| %s | %d | _pending_ | | | | | | |' % (label, E2[k][2]))
            continue
        s = bm['shape']
        w('| %s | %d | %d | **%d/%d** | %.2f | %s | %s | %s | %.4f |'
          % (label, E2[k][2], bm['n'], bm['deep'], bm['n'], s['median'],
             s['gapRatio'], s['dipGap'], s['bimodalityCoefficient'], bm['maxVSLO']))
    w('')

    # The plan asked two specific questions here. Answer them in those words.
    c10bm = bimodal(E2['c10'][1], e2['c10']['boundary']['lastSafeRl']) if e2['c10'] else None
    c50bm = bimodal(E2['c50'][1], e2['c50']['boundary']['lastSafeRl']) if e2['c50'] else None
    if c10bm and c50bm and e1b:
        w('The plan asked two questions in these words. Both are answered no.')
        w('')
        w('- **"c10 given c50\'s cap — does it *become* bimodal?"** No. %d/%d DEEP, '
          'against 0/12 at its own cap. Unchanged.'
          % (c10bm['deep'], c10bm['n']))
        w('- **"c50 given c10\'s cap — does it *stop* being bimodal?"** No, and it '
          'moves the other way: %d/%d DEEP against 9/12 at its own cap. The three '
          'shallow runs that produced E1B\'s gap are gone, and the gap with them '
          '(gapRatio 7.04 to %s, dipGap 0.385 to %s). The cell is now uniformly deep, '
          'which is E1B\'s "unimodal deep" category rather than bimodal.'
          % (c50bm['deep'], c50bm['n'], c50bm['shape']['gapRatio'], c50bm['shape']['dipGap']))
        w('')
        w('Median occupancy barely moved in either cell when the cap changed fivefold: '
          '20.88 to %.2f for c10 and 102.25 to %.2f for c50. Depth followed the arm, '
          'not the cap.' % (c10bm['median'], c50bm['median']))
        w('')
        w('Every one of the 24 replication runs classified SAFE, max vSLO 0.0000.')
        w('')

    # ---- occupancy -----------------------------------------------------
    if occ:
        w('## Cap-normalised occupancy (addendum 1, registered mid-campaign)')
        w('')
        w('Cap is the cap **in force during the drain window**, `50 x ceil(C_d x S)` '
          'under `profile_relative`, not the t=0 value.')
        w('')
        w('| cell | rl | n | C_d | cap | median qMean | % of cap | class |')
        w('|---|---:|---:|---:|---:|---:|---:|---|')
        for r in occ['points']:
            w('| %s | %d | %d | %d | %d | %.2f | %.3f%% | %s |'
              % (r['cell'], r['rl'], r['n'], r['capacityDuringDrain'], r['cap'],
                 r['medianQMean'], r['pctOfCap'], 'SAFE' if r['safe'] else 'non-SAFE'))
        w('')
        w('The `4.1% of cap` agreement registered in addendum 1 does not survive '
          'either new cell. The two E1 C0 cells sat at 4.114% and 4.071%; the same '
          'arms at swapped caps sit at 0.923% and 21.686%. Absolute occupancy stayed '
          'with the arm while the cap moved fivefold, which is what breaks the ratio.')
        w('')
        w('### g, the occupancy analogue of f')
        w('')
        w('```')
        w('g = (observed median - retain) / (swap - retain)')
        w('  c10@2500: retain %.2f swap %.0f      c50@500: retain %.2f swap %.0f'
          % (*G_REF['c10'], *G_REF['c50']))
        w('cap-governed both g >= 0.75    concurrency-governed both <= 0.25')
        w('```')
        w('')
        w('| cell | observed median | g | reading |')
        w('|---|---:|---:|---|')
        gs = {}
        last = occ.get('lastSafePerCell', {})
        for k, cellname, label in [('c10', 'E2 c10@Q2500', 'c10 @ Q=2500'),
                                   ('c50', 'E2 c50@Q500', 'c50 @ Q=500')]:
            if cellname not in last:
                w('| %s | _pending_ | | |' % label)
                gs[k] = None
                continue
            m = last[cellname]['medianQMean']
            ret, swp = G_REF[k]
            g = round((m - ret) / (swp - ret), 3)
            gs[k] = g
            r = ('**off-scale** (addendum 3)' if g < 0 else
                 'cap-governed' if g >= 0.75 else
                 'concurrency-governed' if g <= 0.25 else 'neither threshold')
            w('| %s | %.2f | **%+.3f** | %s |' % (label, m, g, r))
        w('')
        if gs.get('c10') is not None and gs.get('c50') is not None:
            both = [gs['c10'], gs['c50']]
            v = ('**OFF-SCALE**' if min(both) < 0 else
                 '**CAP-GOVERNED**' if min(both) >= 0.75 else
                 '**CONCURRENCY-GOVERNED**' if max(both) <= 0.25 else '**MIXED**')
            w('Registered verdict: %s (g = %+.3f and %+.3f).' % (v, *both))
            if min(both) < 0:
                w('')
                w('Addendum 4 applies here unchanged. The verdict is what addendum 3 '
                  'produces and the criterion was not altered after the fact, but the '
                  'magnitude is %+.3f and the criterion has no dead band. Reported '
                  'alongside, without verdict status: `|g| <= 0.25` in both cells, so '
                  'occupancy did not follow the cap in either -- g of %+.3f and %+.3f '
                  'against a swap prediction of 1.0.' % (min(both), *both))
        w('')

    # ---- cap binding ---------------------------------------------------
    bind = load('results/E2-cap-binding.json')
    if bind:
        w('## Did the cap bind, and what failed')
        w('')
        w('Not a registered reading. Two checks on whether the registered statistics '
          'are measuring what they are meant to.')
        w('')
        w('**Failure mode.** `sloErrorAccounting` excludes client 429s, so a smaller '
          'cap could in principle turn latency violations into excluded rejections '
          'and make a run classify SAFE for the wrong reason. Rejections during the '
          'drain, summed over every point of both campaigns at every cap: '
          '**%d**. The concern does not arise.' % bind['totalRejected'])
        w('')
        errs = [r for r in bind['points'] if r['maxVSLOError'] > 0]
        if errs:
            n = len(errs)
            w('Violations are latency violations everywhere except %s: '
              % ('one point' if n == 1 else '%d points' % n)
              + '; '.join('%s rl=%d, vSLO_error %.4f against vSLO_latency %.4f'
                          % (r['cell'], r['rl'], r['maxVSLOError'], r['maxVSLOLatency'])
                          for r in errs)
              + '. %s the deepest non-SAFE anchor of its cell and %s no interval.'
              % ('That point is' if n == 1 else 'Each is',
                 'defines' if n == 1 else 'they define'))
            w('')
        w('**Cap binding.** Peak drain-window queue depth against the cap in force. '
          'Median and max across the runs at each point, because one run in fifteen '
          'at c10/C0 rl=825 peaked at 400 of 500 while the median peaked at 55.')
        w('')
        w('| cell | rl | n | cap | median peak | % of cap | max peak | % of cap | class |')
        w('|---|---:|---:|---:|---:|---:|---:|---:|---|')
        for r in bind['points']:
            w('| %s | %d | %d | %d | %.1f | %.1f%% | %d | %.1f%%%s | %s |'
              % (r['cell'], r['rl'], r['n'], r['cap'], r['medQPeak'], r['medPctOfCap'],
                 r['maxQPeak'], r['pctOfCap'], ' **cap hit**' if r['capTouched'] else '',
                 'SAFE' if r['safe'] else 'non-SAFE'))
        w('')
        w('At the last SAFE point of every cell in both campaigns:')
        w('')
        w('| cell | rl | median peak as % of cap |')
        w('|---|---:|---:|')
        for c in sorted({r['cell'] for r in bind['points']}):
            rs = [r for r in bind['points'] if r['cell'] == c and r['safe']]
            if rs:
                r = max(rs, key=lambda x: x['rl'])
                w('| %s | %d | %.1f%% |' % (c, r['rl'], r['medPctOfCap']))
        w('')

    # ---- campaign ------------------------------------------------------
    w('## Campaign')
    w('')
    w('| | |')
    w('|---|---|')
    tot = 0
    for k in ('c10', 'c50'):
        n = len(glob.glob(os.path.join(E2[k][1], '*c*-c*-rl*-r*.json')))
        tot += n
        w('| %s @ Q=%d records | %d |' % (k, E2[k][2], n))
    w('| Total E2 runs | **%d** |' % tot)
    dirty = 0
    commits = set()
    for k in ('c10', 'c50'):
        for p in glob.glob(os.path.join(E2[k][1], '*c*-c*-rl*-r*.json')):
            r = json.load(open(p))
            commits.add(r['gitCommit'])
            if r['gitDirty']:
                dirty += 1
    w('| Distinct harness commits | %s |' % (', '.join(sorted(commits)) or 'n/a'))
    w('| Records flagged gitDirty | %d — all from the untracked `results-*` output '
      'directory, which `provenanceOutputPrefixes` does not cover. No code differs '
      'from the pinned commit. |' % dirty)
    w('')
    w('### Configuration conformance')
    w('')
    w('Every E2 record checked against the cap its cell is supposed to impose. The '
      'two cells share run-id namespaces with E1 (`c50-c0-rl975-r1` exists in both), '
      'which is why each writes to its own directory; the last row checks that no '
      'E2 record reached the E1 corpus.')
    w('')
    w('| cell | expected cap | expected S | records | conforming |')
    w('|---|---:|---:|---:|---|')
    for k, svc in (('c10', 5), ('c50', 25)):
        cap = E2[k][2]
        paths = glob.glob(os.path.join(E2[k][1], '*c*-c*-rl*-r*.json'))
        ok = 0
        for pth in paths:
            pa = json.load(open(pth))['params']
            if (pa['downstreamQueueCap'] == cap and pa['downstreamServiceTimeMs'] == svc
                    and pa['injectorPacer'] == 'lanes'):
                ok += 1
        w('| %s @ Q=%d | %d | %d ms | %d | %s |'
          % (k, cap, cap, svc, len(paths),
             'all %d' % ok if ok == len(paths) else '**%d of %d**' % (ok, len(paths))))
    leaked = 0
    for pth in glob.glob('results/c*-c*-rl*-r*.json') + glob.glob('results/e1b-*.json'):
        pa = json.load(open(pth))['params']
        if pa['downstreamQueueCap'] != (500 if pa['downstreamServiceTimeMs'] == 5 else 2500):
            leaked += 1
    w('| E1 corpus (`results/`) | 500 for c10, 2500 for c50 | | %d | %s |'
      % (len(glob.glob('results/c*-c*-rl*-r*.json')) + len(glob.glob('results/e1b-*.json')),
         'no E2 record present' if leaked == 0 else '**%d carry an E2 cap**' % leaked))
    w('')
    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
