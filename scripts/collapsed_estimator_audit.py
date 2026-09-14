#!/usr/bin/env python3
"""A6: how far does A4 over-read on collapsed runs, and does any conclusion move?

A4 measures the recovery rate over the span the traffic occupied. On a collapsed
run that span excludes stalled intervals, so the rate is inflated. The defect was
found in E2e by cross-checking A4 against each cell's measured saturation
plateau, not by A4's own validation, which only ever covered SAFE points.

Nothing can sustain more than it can serve, so an A4 achieved rate above a cell's
plateau is demonstrably wrong rather than merely suspect. This quantifies that
per point, then recomputes every conclusion that rests on an UNSAFE endpoint.

Usage: python3 scripts/collapsed_estimator_audit.py
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CAL = json.load(open('results/E2D-capacity-calibration.json'))['cells']
CELLS = [
    ('E1 c10/C0', 'results/boundaries/c10-C0.json', 2000),
    ('E1 c10/C1', 'results/boundaries/c10-C1.json', 1400),
    ('E1 c50/C0', 'results/boundaries/c50-C0.json', 2000),
    ('E1 c50/C1', 'results/boundaries/c50-C1.json', 1400),
    ('E2 c10@Q2500', 'results/e2/c10-Q2500/boundaries/c10-C0.json', 2000),
    ('E2 c50@Q500', 'results/e2/c50-Q500/boundaries/c50-C0.json', 2000),
    ('E2b C=400', 'results/e2b/boundaries/c50-C0.json', 400),
]
CAL_KEY = {'E1 c10/C0': 'E1 c10/C0', 'E1 c10/C1': 'E1 c10/C1',
           'E1 c50/C0': 'E1 c50/C0', 'E1 c50/C1': 'E1 c50/C1',
           'E2 c10@Q2500': 'E2 c10@Q2500', 'E2 c50@Q500': 'E2 c50@Q500',
           'E2b C=400': 'E2b C=400'}


def main():
    out = {'cells': {}}
    print('=== 1. REACH: A4 achieved rate at every UNSAFE point vs the cell plateau ===')
    print()
    print('%-14s %6s %5s %10s %10s %9s %9s %s' % (
        'cell', 'rl', 'n', 'A4 rate', 'plateau', 'excess', 'in rho', 'verdict'))
    total = bad = 0
    for label, path, cd in CELLS:
        b = json.load(open(path))
        plateau = CAL[CAL_KEY[label]]['trueCapacity']
        cell = {'C_d': cd, 'plateau': plateau, 'ceiling': round(plateau / cd, 4),
                'unsafePoints': [], 'safePoints': []}
        for pt in sorted(b['points'], key=lambda p: p['rl']):
            rates = [r * cd for r in pt['rhoAchieved']]
            med = statistics.median(rates)
            rec = {'rl': pt['rl'], 'n': len(pt['runs']), 'class': pt['class'],
                   'a4Rate': round(med, 1),
                   'a4Rho': round(statistics.median(pt['rhoAchieved']), 4),
                   'excessRps': round(med - plateau, 1),
                   'excessRho': round((med - plateau) / cd, 4)}
            if pt['class'] == 'SAFE':
                cell['safePoints'].append(rec)
                continue
            cell['unsafePoints'].append(rec)
            total += 1
            impossible = med > plateau
            if impossible:
                bad += 1
            print('%-14s %6d %5d %10.1f %10.1f %+9.1f %+9.4f %s' % (
                label, pt['rl'], len(pt['runs']), med, plateau,
                med - plateau, (med - plateau) / cd,
                'IMPOSSIBLE' if impossible else 'within plateau'))
        out['cells'][label] = cell
    print()
    print('UNSAFE points: %d.  A4 rate above the cell plateau: %d (%.0f%%).'
          % (total, bad, 100.0 * bad / total))
    out['unsafeTotal'] = total
    out['unsafeImpossible'] = bad

    ex = [p['excessRho'] for c in out['cells'].values() for p in c['unsafePoints']
          if p['excessRho'] > 0]
    if ex:
        print('Excess where positive: %+.4f to %+.4f rho, median %+.4f.'
              % (min(ex), max(ex), statistics.median(ex)))
        widths = []
        for label, path, cd in CELLS:
            b = json.load(open(path))
            i = b['boundary']['rhoStarInterval']
            widths.append(i[1] - i[0])
        print('Reported interval widths: %.4f to %.4f. The inflation is %.1fx to %.1fx '
              'a whole interval.' % (min(widths), max(widths),
                                     min(ex) / max(widths), max(ex) / min(widths)))
        out['excessRhoRange'] = [min(ex), max(ex)]
        out['intervalWidthRange'] = [round(min(widths), 4), round(max(widths), 4)]

    print()
    print('=== 2. CORRECTED REPORTING ===')
    print()
    print('Rate interval is what the bisection resolved and is unaffected.')
    print('Achieved utilisation is reported at the last SAFE point only.')
    print('The ceiling is a property of the cell, not a measurement of a point.')
    print()
    print('%-14s %-14s %-22s %-10s %s' % (
        'cell', 'rl interval', 'rho at last SAFE', 'ceiling', 'headroom to ceiling'))
    for label, path, cd in CELLS:
        b = json.load(open(path))
        bd = b['boundary']
        c = out['cells'][label]
        last = max((p for p in c['safePoints']), key=lambda p: p['rl'])
        pt = next(p for p in b['points'] if p['rl'] == last['rl'])
        lo, hi = min(pt['rhoAchieved']), max(pt['rhoAchieved'])
        c['reported'] = {
            'rlInterval': [bd['lastSafeRl'], bd['firstNonSafeRl']],
            'lastSafeRl': last['rl'],
            'rhoAtLastSafe': [round(lo, 4), round(hi, 4)],
            'ceiling': c['ceiling'],
            'headroomToCeiling': round(c['ceiling'] - hi, 4),
        }
        print('%-14s [%4d, %4d]   [%.4f, %.4f]       %.4f     %+.4f' % (
            label, bd['lastSafeRl'], bd['firstNonSafeRl'], lo, hi, c['ceiling'],
            c['ceiling'] - hi))

    json.dump(out, open('results/A6-collapsed-estimator.json', 'w'), indent=2)
    print()
    print('wrote results/A6-collapsed-estimator.json')
    return 0




def conclusions():
    """3. Does any conclusion move under the corrected reporting?

    Corrected interval = [achieved rho at the last SAFE point, the cell ceiling].
    The lower end is measured where A4 is valid; the upper end is a property of
    the cell. Where the last SAFE point already sits at the ceiling the interval
    is degenerate, which is itself a finding: rho* is pinned at saturation.
    """
    A = json.load(open('results/A6-collapsed-estimator.json'))['cells']

    def iv(label):
        r = A[label]['reported']
        return r['rhoAtLastSafe'][1], r['ceiling']

    def orig(path):
        return json.load(open(path))['boundary']['rhoStarInterval']

    print()
    print('=== 3. DOES ANY CONCLUSION MOVE? ===')
    print()
    print('Corrected interval = [rho at last SAFE, cell ceiling].')
    print()
    print('%-14s %-22s %-22s %s' % ('cell', 'as reported (A4)', 'corrected', 'note'))
    for label, path, cd in CELLS:
        o = orig(path)
        lo, hi = iv(label)
        deg = hi <= lo
        print('%-14s [%.4f, %.4f]      [%.4f, %.4f]      %s' % (
            label, o[0], o[1], lo, hi,
            'DEGENERATE: last SAFE already at the ceiling' if deg else ''))

    print()
    print('(a) capacity invariance: does C0 overlap C1 within an arm?')
    for arm, c0, c1 in [('c10', 'E1 c10/C0', 'E1 c10/C1'), ('c50', 'E1 c50/C0', 'E1 c50/C1')]:
        a, b = iv(c0), iv(c1)
        al, ah = min(a), max(a)
        bl, bh = min(b), max(b)
        ov = al <= bh and bl <= ah
        print('    %-4s C0 [%.4f, %.4f]  C1 [%.4f, %.4f]  -> %s'
              % (arm, al, ah, bl, bh, 'OVERLAP, survives' if ov else 'NO OVERLAP, CHANGES'))

    print()
    print('(b) the concurrency gap between the arms')
    for name, f in [('as reported, interval midpoints',
                     lambda l: sum(orig(dict((c[0], c[1]) for c in CELLS)[l])) / 2),
                    ('corrected, last SAFE rho',
                     lambda l: A[l]['reported']['rhoAtLastSafe'][1]),
                    ('corrected, interval midpoints',
                     lambda l: sum(iv(l)) / 2)]:
        g = f('E1 c50/C0') - f('E1 c10/C0')
        print('    %-32s c10 %.4f  c50 %.4f  gap %.4f' % (name, f('E1 c10/C0'),
                                                          f('E1 c50/C0'), g))

    print()
    print('(c) E2 cap swap: rate intervals, unaffected by the estimator')
    for a, e1, e2 in [('c10', 'E1 c10/C0', 'E2 c10@Q2500'), ('c50', 'E1 c50/C0', 'E2 c50@Q500')]:
        p, q = A[e1]['reported']['rlInterval'], A[e2]['reported']['rlInterval']
        print('    %-4s E1 %s  E2 %s  -> %s' % (a, p, q, 'identical' if p == q else 'DIFFER'))
    print('    f_c10 on last SAFE rho: (%.4f - %.4f) / 0.0693 = %+.3f'
          % (A['E2 c10@Q2500']['reported']['rhoAtLastSafe'][1],
             A['E1 c10/C0']['reported']['rhoAtLastSafe'][1],
             (A['E2 c10@Q2500']['reported']['rhoAtLastSafe'][1]
              - A['E1 c10/C0']['reported']['rhoAtLastSafe'][1]) / 0.0693))

    print()
    print('(d) E2b: does S still govern?')
    r10 = A['E1 c10/C0']['reported']['rhoAtLastSafe'][1]
    r50 = A['E1 c50/C0']['reported']['rhoAtLastSafe'][1]
    rb = A['E2b C=400']['reported']['rhoAtLastSafe'][1]
    h = (rb - r10) / (r50 - r10)
    print('    on last SAFE rho: h = (%.4f - %.4f) / (%.4f - %.4f) = %.3f -> %s'
          % (rb, r10, r50, r10, h,
             'S GOVERNS' if h >= 0.75 else ('CONCURRENCY' if h <= 0.25 else 'INTERMEDIATE')))
    m10, m50, mb = sum(iv('E1 c10/C0')) / 2, sum(iv('E1 c50/C0')) / 2, sum(iv('E2b C=400')) / 2
    h2 = (mb - m10) / (m50 - m10)
    print('    on interval midpoints: h = %.3f -> %s'
          % (h2, 'S GOVERNS' if h2 >= 0.75 else ('CONCURRENCY' if h2 <= 0.25 else 'INTERMEDIATE')))

    print()
    print('(e) E2d: the collapse to effective utilisation ~1.0')
    effs, confs = [], []
    for label, path, cd in CELLS:
        c = A[label]
        last = max(c['safePoints'], key=lambda p: p['rl'])
        e = last['a4Rate'] / c['plateau']
        effs.append(e)
        confs.append(last['a4Rho'])
        print('    %-14s effective at last SAFE = %.1f / %.1f = %.4f'
              % (label, last['a4Rate'], c['plateau'], e))
    sp = max(effs) - min(effs)
    # CORRECTED 2026-09-15. This factor previously divided E2d's published
    # rhoStarSpread, 0.0706, by the spread above. That numerator is the range of
    # INTERVAL MIDPOINTS, each of which averages the last SAFE endpoint with a
    # collapsed non-SAFE one -- the values this very amendment rules invalid --
    # while the denominator had already been recomputed from SAFE points only.
    # Numerator and denominator are now on the same footing: both are the range
    # across cells of a quantity read at the last SAFE point. The factor moves
    # from 10.4x to 10.5x, so nothing downstream changes.
    spc = max(confs) - min(confs)
    print('    corrected spread %.4f (was 0.0033 using UNSAFE endpoints)' % sp)
    print('    against configured C, SAFE points only: %.4f' % spc)
    print('    collapse factor %.4f / %.4f = %.1fx  (E2d reported 21.4x)'
          % (spc, sp, spc / sp))
    print('    CORRECTION: the numerator was 0.0706, E2d\'s midpoint-based spread,')
    print('    which carries the collapsed endpoints this amendment rules invalid.')
    print('    Recomputed from SAFE points only it is %.4f, and the factor %.1fx'
          % (spc, spc / sp))
    print('    rather than %.1fx. Immaterial; made consistent with A6\'s own rule.'
          % (0.0706 / sp))
    print('    every cell sits BELOW 1.0, at %.4f to %.4f: the boundary is at or just'
          % (min(effs), max(effs)))
    print('    under saturation, but the "interval brackets 1.0" phrasing does not survive,')
    print('    since it depended on the inflated UNSAFE endpoint.')
    return 0


if __name__ == '__main__':
    # conclusions() re-derives the (a)-(e) block quoted in results/A6-REPORT.md.
    # It was unreachable until 2026-09-15, which is why that block had to be
    # pasted by hand. Default behaviour is unchanged so the JSON artefact
    # regenerates byte-identically.
    if '--conclusions' in sys.argv:
        sys.exit(conclusions())
    sys.exit(main())
