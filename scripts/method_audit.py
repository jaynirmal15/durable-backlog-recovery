#!/usr/bin/env python3
"""Method-section audit: monotonicity, denominators, exclusions, guards, coverage.

Every answer comes from committed artefacts. Read-only.

Usage: python3 scripts/method_audit.py
"""
import collections
import glob
import json
import os
import statistics
import sys

CELLS = [
    ('E1 c10/C0', 'results/boundaries/c10-C0.json', ['results/c10-c0-rl*-r*.json',
                                                     'results/e1b-c10-c0-*.json'], 2000),
    ('E1 c10/C1', 'results/boundaries/c10-C1.json', ['results/c10-c1-rl*-r*.json',
                                                     'results/e1b-c10-c1-*.json'], 1400),
    ('E1 c50/C0', 'results/boundaries/c50-C0.json', ['results/c50-c0-rl*-r*.json',
                                                     'results/e1b-c50-c0-*.json'], 2000),
    ('E1 c50/C1', 'results/boundaries/c50-C1.json', ['results/c50-c1-rl*-r*.json'], 1400),
    ('E2 c10@Q2500', 'results/e2/c10-Q2500/boundaries/c10-C0.json',
     ['results/e2/c10-Q2500/*-rl*-r*.json'], 2000),
    ('E2 c50@Q500', 'results/e2/c50-Q500/boundaries/c50-C0.json',
     ['results/e2/c50-Q500/*-rl*-r*.json'], 2000),
    ('E2b C=400', 'results/e2b/boundaries/c50-C0.json',
     ['results/e2b/*-rl*-r*.json'], 400),
]
RANK = {'SAFE': 0, 'MARGINAL': 1, 'UNSAFE': 2}


def records(globs):
    out = []
    for g in globs:
        for p in sorted(glob.glob(g)):
            r = json.load(open(p))
            if r.get('runId'):
                out.append(r)
    return out


def hr(t):
    print()
    print('=' * 78)
    print(t)
    print('=' * 78)


def item1():
    hr('1. MONOTONICITY AUDIT')
    print('Points ordered by ACHIEVED rate (A4), with nominal rl alongside.')
    print('An inversion is a higher-achieved-rate point classifying safer than a')
    print('lower-achieved-rate one.')
    total_inv = 0
    marg = 0
    for label, bpath, globs, cd in CELLS:
        b = json.load(open(bpath))
        pts = []
        for pt in b['points']:
            ach = statistics.median(pt['rhoAchieved']) * cd
            pts.append({'rl': pt['rl'], 'cls': pt['class'], 'ach': ach,
                        'n': len(pt['runs']),
                        'vslo': pt['vSLO']})
        pts.sort(key=lambda p: p['ach'])
        inv = []
        for i in range(len(pts) - 1):
            for j in range(i + 1, len(pts)):
                if RANK[pts[j]['cls']] < RANK[pts[i]['cls']]:
                    inv.append((pts[i], pts[j]))
        total_inv += len(inv)
        bd = b['boundary']
        endpoints = (bd['lastSafeRl'], bd['firstNonSafeRl'])
        end_marg = [p for p in pts if p['rl'] in endpoints and p['cls'] == 'MARGINAL']
        marg += len(end_marg)
        print()
        print('--- %s   bracket rl [%d, %d]' % (label, endpoints[0], endpoints[1]))
        print('    %8s %6s %4s %-9s %s' % ('achieved', 'rl', 'n', 'class', 'vSLO'))
        for p in pts:
            mark = ' <-' if p['rl'] in endpoints else ''
            print('    %8.1f %6d %4d %-9s %s%s'
                  % (p['ach'], p['rl'], p['n'], p['cls'],
                     ', '.join('%.3f' % v for v in p['vslo'][:3]), mark))
        print('    inversions: %d%s' % (len(inv),
              '' if not inv else '  ' + '; '.join('rl=%d(%s) below rl=%d(%s)'
                                                  % (a['rl'], a['cls'], c['rl'], c['cls'])
                                                  for a, c in inv)))
        print('    terminal endpoint decided by a MARGINAL: %s'
              % ('YES' if end_marg else 'no'))
    print()
    print('TOTAL inversions across all seven cells: %d' % total_inv)
    print('Terminal endpoints decided by a MARGINAL: %d' % marg)
    return total_inv, marg


def item4():
    hr('4. HOST-STALL EXCLUSION')
    rows = []
    for label, bpath, globs, cd in CELLS:
        b = json.load(open(bpath))
        cls = {pt['rl']: pt['class'] for pt in b['points']}
        for r in records(globs):
            rl = r['params']['rateLimitRps']
            if rl not in cls:
                continue
            rows.append({'cell': label, 'rl': rl, 'cls': cls[rl],
                         'runId': r['runId'],
                         'stall': r.get('stallSeconds', 0),
                         'contam': r.get('contaminatedSeconds', 0),
                         'vslo': r['vSLO'], 'raw': r.get('vSLO_raw', r['vSLO']),
                         'tfull': r.get('tFullSec', 0)})
    by = collections.Counter()
    secs = collections.Counter()
    runs_any = collections.Counter()
    for x in rows:
        by[x['cls']] += 1
        secs[x['cls']] += x['contam']
        if x['contam'] > 0:
            runs_any[x['cls']] += 1
    print('%-10s %6s %10s %14s %12s' % ('class', 'runs', 'w/ excl', 'excluded s', 'as %% of T_full'))
    for c in ('SAFE', 'MARGINAL', 'UNSAFE'):
        if not by[c]:
            continue
        tf = sum(x['tfull'] for x in rows if x['cls'] == c)
        print('%-10s %6d %10d %14.0f %11.3f%%'
              % (c, by[c], runs_any[c], secs[c], 100 * secs[c] / tf if tf else 0))
    tot = sum(secs.values())
    print('total excluded: %.0f seconds across %d runs of %d'
          % (tot, sum(runs_any.values()), len(rows)))
    print()
    print('Would any classification change using vSLO_raw instead?')
    print('%-14s %6s %-9s %-9s %s' % ('cell', 'rl', 'as filtered', 'as raw', 'changed?'))
    changed = 0
    for label, bpath, globs, cd in CELLS:
        b = json.load(open(bpath))
        recs = records(globs)
        for pt in b['points']:
            raw = [r['vSLO_raw'] for r in recs
                   if r['params']['rateLimitRps'] == pt['rl'] and 'vSLO_raw' in r]
            if not raw:
                continue
            n_uns = sum(1 for v in raw if v > 0.05)
            new = 'UNSAFE' if n_uns >= 2 else ('SAFE' if all(v <= 0.01 for v in raw)
                                               else 'MARGINAL')
            if new != pt['class']:
                changed += 1
                print('%-14s %6d %-9s %-9s CHANGED' % (label, pt['rl'], pt['class'], new))
    if not changed:
        print('  no point in any cell changes classification under vSLO_raw.')
    return tot, changed


def item5():
    hr('5. INJECTOR 429s AND DELIVERY DEFICIT')
    rows = []
    for label, bpath, globs, cd in CELLS:
        b = json.load(open(bpath))
        cls = {pt['rl']: pt['class'] for pt in b['points']}
        for r in records(globs):
            p = r['params']
            rl = p['rateLimitRps']
            if rl not in cls:
                continue
            issued = p.get('injectorIssued', 0)
            completed = p.get('injectorCompleted', 0)
            drops = p.get('injectorDrops429', 0)
            acc = p.get('warmupInjectorAccuracy')
            rows.append({'cell': label, 'cls': cls[rl], 'rl': rl, 'runId': r['runId'],
                         'issued': issued, 'completed': completed, 'drops': drops,
                         'deficit': (1 - completed / issued) if issued else 0,
                         'acc': acc})
    print('%-10s %6s %12s %12s %14s %14s'
          % ('class', 'runs', 'total 429s', 'max 429s', 'max deficit', 'worst accuracy'))
    for c in ('SAFE', 'MARGINAL', 'UNSAFE'):
        g = [x for x in rows if x['cls'] == c]
        if not g:
            continue
        accs = [x['acc'] for x in g if x['acc'] is not None]
        print('%-10s %6d %12d %12d %13.4f%% %13.4f%%'
              % (c, len(g), sum(x['drops'] for x in g), max(x['drops'] for x in g),
                 100 * max(x['deficit'] for x in g),
                 100 * min(accs) if accs else float('nan')))
    print()
    worst = sorted([x for x in rows if x['cls'] == 'SAFE'],
                   key=lambda x: -x['deficit'])[:5]
    print('SAFE runs with the largest delivery deficit:')
    for x in worst:
        print('  %-26s %-14s deficit %.4f%%  429s %d  warmup accuracy %.4f%%'
              % (x['runId'], x['cell'], 100 * x['deficit'], x['drops'],
                 100 * x['acc'] if x['acc'] else float('nan')))
    return rows


def item6():
    hr('6. n=12 COVERAGE')
    print('%-14s %6s %4s %-9s %s' % ('cell', 'rl', 'n', 'class', 'is a terminal endpoint?'))
    cov = []
    for label, bpath, globs, cd in CELLS:
        b = json.load(open(bpath))
        bd = b['boundary']
        ends = (bd['lastSafeRl'], bd['firstNonSafeRl'])
        has = False
        for pt in b['points']:
            if len(pt['runs']) >= 12:
                has = True
                which = ('last SAFE' if pt['rl'] == ends[0]
                         else 'first NON-SAFE' if pt['rl'] == ends[1] else 'no')
                print('%-14s %6d %4d %-9s %s' % (label, pt['rl'], len(pt['runs']),
                                                 pt['class'], which))
                cov.append((label, pt['rl'], which))
        if not has:
            print('%-14s %6s %4s %-9s %s' % (label, '-', '-', '-', 'NO n>=12 POINT'))
            cov.append((label, None, None))
    cells_with = len({c[0] for c in cov if c[1]})
    ends_cov = len([c for c in cov if c[2] and c[2] != 'no'])
    print()
    print('cells with an n>=12 point: %d of %d' % (cells_with, len(CELLS)))
    print('n>=12 points that ARE a terminal bracket endpoint: %d' % ends_cov)
    print('first NON-SAFE endpoints at n>=12: %d'
          % len([c for c in cov if c[2] == 'first NON-SAFE']))
    return cov


def main():
    item1()
    item4()
    item5()
    item6()
    return 0


if __name__ == '__main__':
    sys.exit(main())
