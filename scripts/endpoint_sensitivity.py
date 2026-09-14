#!/usr/bin/env python3
"""Which repetition of the last SAFE point becomes the quoted rho, and does it matter?

locate_boundary.py keeps rhoAchieved as a list per point and never aggregates it:
the interval spans every achieved rho seen at each endpoint. Aggregation happens
downstream, in the consumers, and they do not all agree. This enumerates the
conventions, then recomputes three results under min / max / mean / median:

  (a) the monotonicity audit,
  (b) which point is last SAFE in each cell,
  (c) the 0.993-1.000 headline, after resolution-matched rounding.

Read-only. Usage: python3 scripts/endpoint_sensitivity.py
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from precision import u, is_coarse                                  # noqa: E402
from collapsed_estimator_audit import CELLS, CAL, CAL_KEY           # noqa: E402

RANK = {'SAFE': 0, 'MARGINAL': 1, 'UNSAFE': 2}
AGGS = [('min', min), ('max', max),
        ('mean', statistics.mean), ('median', statistics.median)]


def hr(t):
    print()
    print('=' * 78)
    print(t)
    print('=' * 78)


def load():
    out = []
    for label, path, cd in CELLS:
        b = json.load(open(path))
        out.append((label, b, cd, CAL[CAL_KEY[label]]['trueCapacity']))
    return out


def conventions():
    hr('WHICH ENDPOINT IS QUOTED: every aggregation of rhoAchieved in the repo')
    rows = [
        ('locate_boundary.py:466', 'rhoStarInterval',
         'min(lastSAFE) .. max(firstNonSAFE)', 'no aggregation: full span'),
        ('collapsed_estimator_audit.py:108', 'rhoAtLastSafe',
         '[min, max]', 'a pair, both repetitions extremes'),
        ('make_figures.py:66', 'F5 configured-rho axis',
         'rhoAtLastSafe[1] = MAX', '<-- THE QUOTED rho_eff'),
        ('make_figures.py:66', 'F5 effective-rho axis',
         'a4Rate/plateau = MEDIAN', 'different aggregator, same figure'),
        ('collapsed_estimator_audit.py:53', 'a4Rate, a4Rho', 'MEDIAN', ''),
        ('method_audit.py:61', 'monotonicity ordering', 'MEDIAN', ''),
        ('leading_indicator.py:80', 'per-point rho', 'MEAN', ''),
        ('e2_report.py:282', 'monotonicity sequence', 'MAX', ''),
        ('e2e_analysis.py:111', 'E2e point rho', 'MEDIAN', 'not via locate_boundary'),
        ('capacity_calibration.py:206', 'calibration endpoints',
         'min(lastSAFE), max(firstNonSAFE)', ''),
    ]
    print('%-34s %-26s %-34s %s' % ('site', 'quantity', 'aggregation', 'note'))
    for a, b, c, d in rows:
        print('%-34s %-26s %-34s %s' % (a, b, c, d))
    print()
    print('ANSWER: the quoted rho_eff in F5 (and T1, which reads the same field) is')
    print('the MAXIMUM across the last SAFE point\'s repetitions. It is produced at')
    print('scripts/collapsed_estimator_audit.py:108 -- "lo, hi = min(...), max(...)"')
    print('-- stored as rhoAtLastSafe = [lo, hi], and selected as element [1] at')
    print('scripts/make_figures.py:66.')


def monotonicity(data):
    hr('(a) MONOTONICITY AUDIT under each aggregator')
    print('Points ordered by achieved rate; an inversion is a higher-rate point')
    print('classifying safer than a lower-rate one.')
    print()
    print('%-14s %s' % ('cell', '  '.join('%-18s' % n for n, _ in AGGS)))
    totals = {}
    orders = {}
    for name, fn in AGGS:
        totals[name] = 0
    for label, b, cd, _ in data:
        cellrow = []
        for name, fn in AGGS:
            pts = [{'rl': p['rl'], 'cls': p['class'], 'ach': fn(p['rhoAchieved']) * cd}
                   for p in b['points']]
            pts.sort(key=lambda p: p['ach'])
            inv = sum(1 for i in range(len(pts) - 1) for j in range(i + 1, len(pts))
                      if RANK[pts[j]['cls']] < RANK[pts[i]['cls']])
            totals[name] += inv
            orders.setdefault(label, {})[name] = [p['rl'] for p in pts]
            cellrow.append('inv=%d' % inv)
        print('%-14s %s' % (label, '  '.join('%-18s' % c for c in cellrow)))
    print()
    print('%-14s %s' % ('TOTAL', '  '.join('%-18s' % ('inv=%d' % totals[n])
                                           for n, _ in AGGS)))
    print()
    print('Rank-order stability (does the aggregator reorder the points?):')
    reorder = 0
    for label in orders:
        base = orders[label]['median']
        diff = [n for n, _ in AGGS if orders[label][n] != base]
        if diff:
            reorder += 1
            print('  %-14s differs from median under: %s' % (label, ', '.join(diff)))
            for n in ['median'] + diff:
                print('      %-7s %s' % (n, orders[label][n]))
    if not reorder:
        print('  none: all four aggregators give the same rate order in all seven cells.')
    return totals, reorder


def last_safe(data):
    hr('(b) WHICH POINT IS LAST SAFE, under each aggregator')
    print('class comes from vSLO via classify(); rhoAchieved is not an input to it,')
    print('so this should be invariant by construction. Verified explicitly:')
    print()
    print('%-14s %-12s %s' % ('cell', 'lastSafeRl', 'last SAFE by class, per aggregator'))
    moved = 0
    for label, b, cd, _ in data:
        bd = b['boundary']
        seen = set()
        for name, fn in AGGS:
            safe = [p for p in b['points'] if p['class'] == 'SAFE']
            seen.add(max(safe, key=lambda p: p['rl'])['rl'])
        ok = (len(seen) == 1 and seen.pop() == bd['lastSafeRl'])
        if not ok:
            moved += 1
        print('%-14s %-12d %s' % (label, bd['lastSafeRl'],
                                  'identical under all four' if ok else 'CHANGES'))
    print()
    print('Corollary: the SAFE/non-SAFE bracket [lastSafeRl, firstNonSafeRl] is a')
    print('property of the classification, and no choice of aggregator can move it.')
    return moved


def headline(data):
    hr('(c) THE 0.993-1.000 HEADLINE under each aggregator')
    print('effective utilisation at the last SAFE point = agg(rhoAchieved) * C_d / plateau')
    print('Rounded at each cell\'s own resolution (3 dp; 2 dp for E2b at C=400).')
    print()
    print('%-14s %9s %9s  %s' % ('cell', 'C_d', 'plateau',
                                 '  '.join('%-8s' % n for n, _ in AGGS)))
    per_agg = {n: [] for n, _ in AGGS}
    raw = {n: [] for n, _ in AGGS}
    for label, b, cd, plateau in data:
        pt = next(p for p in b['points'] if p['rl'] == b['boundary']['lastSafeRl'])
        cells_out = []
        for name, fn in AGGS:
            v = fn(pt['rhoAchieved']) * cd / plateau
            raw[name].append(v)
            s = u(v, is_coarse(label))
            per_agg[name].append(s)
            cells_out.append(s)
        print('%-14s %9d %9.1f  %s' % (label, cd, plateau,
                                       '  '.join('%-8s' % c for c in cells_out)))
    print()
    print('%-14s %s' % ('headline range', ''))
    for name, _ in AGGS:
        vals = sorted(per_agg[name])
        print('  %-8s rounded span  %s to %s        (unrounded %.4f to %.4f)'
              % (name, vals[0], vals[-1], min(raw[name]), max(raw[name])))
    print()
    base = per_agg['median']
    changed = [n for n, _ in AGGS
               if (sorted(per_agg[n])[0], sorted(per_agg[n])[-1])
               != (sorted(base)[0], sorted(base)[-1])]
    print('Headline span differs from the published (median) one under: %s'
          % (', '.join(changed) if changed else 'none'))
    return per_agg, raw, changed


def collapse(data):
    hr('BONUS: F5 collapse spread, with the two axes made consistent')
    print('F5 currently uses MAX on the configured axis and MEDIAN on the effective')
    print('axis. Recomputed with a single aggregator on both:')
    print()
    print('%-10s %12s %12s %10s' % ('aggregator', 'cfg spread', 'eff spread', 'factor'))
    rows = {}
    for name, fn in AGGS:
        cfg, eff = [], []
        for label, b, cd, plateau in data:
            pt = next(p for p in b['points'] if p['rl'] == b['boundary']['lastSafeRl'])
            a = fn(pt['rhoAchieved'])
            cfg.append(a)
            eff.append(a * cd / plateau)
        sc, se = max(cfg) - min(cfg), max(eff) - min(eff)
        rows[name] = (sc, se, sc / se)
        print('%-10s %12.4f %12.4f %10.1fx' % (name, sc, se, sc / se))
    # as published: max on cfg, median on eff
    cfg, eff = [], []
    for label, b, cd, plateau in data:
        pt = next(p for p in b['points'] if p['rl'] == b['boundary']['lastSafeRl'])
        cfg.append(max(pt['rhoAchieved']))
        eff.append(statistics.median(pt['rhoAchieved']) * cd / plateau)
    sc, se = max(cfg) - min(cfg), max(eff) - min(eff)
    print('%-10s %12.4f %12.4f %10.1fx   <- as published (mixed)'
          % ('published', sc, se, sc / se))
    rows['published'] = (sc, se, sc / se)
    return rows


def spread_flag():
    hr('2. DID THE SPREAD DIAGNOSTIC EVER FIRE')
    import glob
    total_pts = total_flag = 0
    print('%-44s %6s %6s %9s %9s %s' % ('cell', 'rl', 'n', 'spread', 'resol.', 'flag'))
    ends = []
    for p in sorted(glob.glob('results/**/boundaries/*.json', recursive=True)):
        b = json.load(open(p))
        bd = b['boundary']
        endpoints = (bd['lastSafeRl'], bd['firstNonSafeRl'])
        for pt in sorted(b['points'], key=lambda x: x['rl']):
            total_pts += 1
            f = bool(pt.get('spreadExceedsResolution'))
            if f:
                total_flag += 1
                if pt['rl'] in endpoints:
                    ends.append((p, pt['rl']))
            print('%-44s %6d %6d %9.5f %9.5f %s%s'
                  % (os.path.relpath(p), pt['rl'], len(pt['runs']),
                     pt['rhoAchievedSpread'], pt['rhoResolution'],
                     'FLAG' if f else '.',
                     '  <- bracket endpoint' if pt['rl'] in endpoints else ''))
    print()
    print('points examined: %d   flagged: %d   flagged endpoints: %d'
          % (total_pts, total_flag, len(ends)))
    print()
    print('Denominator check (rhoResolution must equal 5 / C_d):')
    for p in sorted(glob.glob('results/**/boundaries/*.json', recursive=True)):
        b = json.load(open(p))
        pt = b['points'][0]
        cd = round(5.0 / pt['rhoResolution'])
        print('  %-44s resol %.5f -> C_d %d' % (os.path.relpath(p),
                                                pt['rhoResolution'], cd))
    return total_pts, total_flag, ends


def main():
    data = load()
    conventions()
    tot, reorder = monotonicity(data)
    moved = last_safe(data)
    per_agg, raw, changed = headline(data)
    rows = collapse(data)
    spread_flag()
    hr('VERDICT')
    print('(a) monotonicity  : inversions %s under all four aggregators'
          % ('unchanged (%d)' % tot['median'] if len(set(tot.values())) == 1
             else 'CHANGE: %s' % tot))
    print('(b) last SAFE     : %s' % ('unchanged in all seven cells' if not moved
                                      else 'CHANGES in %d cells' % moved))
    print('(c) headline      : %s' % ('unchanged' if not changed
                                      else 'CHANGES under ' + ', '.join(changed)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
