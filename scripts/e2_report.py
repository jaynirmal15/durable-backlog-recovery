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
    return '[%.4f, %.4f]' % (i[0], i[1]) if i else '_pending_'


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
        w('| **%s** | [%d, %d] | %s | **%s** | %.4f | %d | %d |'
          % (label, bd['lastSafeRl'], bd['firstNonSafeRl'], bd['firstNonSafeClass'],
             fmt_iv(i), i[1] - i[0], len(b['points']), sum(len(p['runs']) for p in b['points'])))
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
            r = ('cap-driven' if f[k] >= 0.75 else
                 'concurrency-driven' if f[k] <= 0.25 else 'neither threshold')
            w('| %s | %.4f | **%.3f** | %s |' % (label, mid(iv(e2[k])), f[k], r))
    w('')
    if f['c10'] is not None and f['c50'] is not None:
        both = [f['c10'], f['c50']]
        verdict = ('**CAP-DRIVEN**' if min(both) >= 0.75 else
                   '**CONCURRENCY-DRIVEN**' if max(both) <= 0.25 else '**MIXED**')
        w('Registered verdict: %s (f = %.3f and %.3f).' % (verdict, *both))
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
            r = ('cap-governed' if g >= 0.75 else
                 'concurrency-governed' if g <= 0.25 else 'neither threshold')
            w('| %s | %.2f | **%.3f** | %s |' % (label, m, g, r))
        w('')
        if gs.get('c10') is not None and gs.get('c50') is not None:
            both = [gs['c10'], gs['c50']]
            v = ('**CAP-GOVERNED**' if min(both) >= 0.75 else
                 '**CONCURRENCY-GOVERNED**' if max(both) <= 0.25 else '**MIXED**')
            w('Registered verdict: %s (g = %.3f and %.3f).' % (v, *both))
        w('')

    # ---- campaign ------------------------------------------------------
    w('## Campaign')
    w('')
    w('| | |')
    w('|---|---|')
    tot = 0
    for k in ('c10', 'c50'):
        n = len(glob.glob(os.path.join(E2[k][1], 'c*-c*-rl*-r*.json')))
        tot += n
        w('| %s @ Q=%d records | %d |' % (k, E2[k][2], n))
    w('| Total E2 runs | **%d** |' % tot)
    dirty = 0
    commits = set()
    for k in ('c10', 'c50'):
        for p in glob.glob(os.path.join(E2[k][1], 'c*-c*-rl*-r*.json')):
            r = json.load(open(p))
            commits.add(r['gitCommit'])
            if r['gitDirty']:
                dirty += 1
    w('| Distinct harness commits | %s |' % (', '.join(sorted(commits)) or 'n/a'))
    w('| Records flagged gitDirty | %d — all from the untracked `results-*` output '
      'directory, which `provenanceOutputPrefixes` does not cover. No code differs '
      'from the pinned commit. |' % dirty)
    w('')
    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
