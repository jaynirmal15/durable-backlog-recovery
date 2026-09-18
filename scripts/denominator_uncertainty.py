#!/usr/bin/env python3
"""Uncertainty in C_measured, the denominator of rho_eff,safe.

Section 4 characterises the numerator (bisection step, repetition spread, n=12,
four aggregators) and is silent on the denominator. C_measured is the median of
the per-run maximum 30 s sustained served rate at that cell's UNSAFE points --
an estimate over several runs, not a constant. This reports how many such
measurements exist per cell, their spread, and what propagating the observed
extremes does to rho_eff,safe, in the same units as that cell's bisection
resolution.

Read-only. Usage: python3 scripts/denominator_uncertainty.py
"""
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capacity_calibration import CELLS, max_sustained, fault_capacity, RESOLUTION_RPS  # noqa: E402
from precision import is_coarse                                                        # noqa: E402

A6 = json.load(open('results/A6-collapsed-estimator.json'))['cells']
CAL = json.load(open('results/E2D-capacity-calibration.json'))['cells']


def hr(t):
    print()
    print('=' * 78)
    print(t)
    print('=' * 78)


def plateau_measurements(label, globs, bpath):
    """Every per-run plateau estimate that feeds this cell's C_measured."""
    b = json.load(open(bpath))
    unsafe = {p['rl'] for p in b['points'] if p['class'] != 'SAFE'}
    rows = []
    for g in globs:
        for p in sorted(glob.glob(g)):
            rec = json.load(open(p))
            if not rec.get('timeline') or rec['params']['rateLimitRps'] not in unsafe:
                continue
            m = max_sustained(rec)
            if m is None:
                continue
            rows.append({'runId': rec['runId'], 'rl': rec['params']['rateLimitRps'],
                         'plateau': m, 'C_d': fault_capacity(rec)})
    rows.sort(key=lambda r: r['plateau'])
    return rows


def main():
    out = {'windowSec': 30.0, 'cells': {}}

    hr('1. HOW MANY PLATEAU MEASUREMENTS EXIST, AND FROM WHICH RUNS')
    print('C_measured = median of the per-run maximum 30 s sustained served rate,')
    print('over every UNSAFE run of that cell. One estimate per run.')
    print()
    data = {}
    for label, globs, bpath, S in CELLS:
        rows = plateau_measurements(label, globs, bpath)
        data[label] = rows
        print('--- %s   %d measurements, from %d UNSAFE rates'
              % (label, len(rows), len({r['rl'] for r in rows})))
        for r in rows:
            print('      %-28s rl=%-5d %10.2f rps' % (r['runId'], r['rl'], r['plateau']))

    hr('2. SPREAD ACROSS THE MEASUREMENTS')
    print('%-14s %5s %11s %11s %11s %9s %8s' % (
        'cell', 'n', 'min', 'median', 'max', 'range', 'range/C'))
    for label, globs, bpath, S in CELLS:
        rows = data[label]
        v = [r['plateau'] for r in rows]
        med = statistics.median(v)
        rng = max(v) - min(v)
        print('%-14s %5d %11.2f %11.2f %11.2f %9.2f %7.2f%%'
              % (label, len(v), min(v), med, max(v), rng, 100 * rng / med))
        out['cells'][label] = {
            'n': len(v), 'min': round(min(v), 2), 'median': round(med, 2),
            'max': round(max(v), 2), 'rangeRps': round(rng, 2),
            'rangeFracPct': round(100 * rng / med, 3),
            'sdRps': round(statistics.pstdev(v), 2) if len(v) > 1 else 0.0,
            'runs': [{'runId': r['runId'], 'rl': r['rl'],
                      'plateau': round(r['plateau'], 2)} for r in rows],
        }
        # committed value must match
        assert abs(round(med, 1) - CAL[label]['trueCapacity']) < 0.05, label

    hr('3. PROPAGATING THE OBSERVED EXTREMES INTO rho_eff,safe')
    print('rho_eff,safe = R_ach,lastSAFE / C_measured, with R_ach held at the')
    print('published value (A4 median at the last SAFE point).')
    print('Bisection resolution in these units is 5 / C_measured.')
    print()
    print('%-14s %10s %9s %9s %9s %9s %9s %7s' % (
        'cell', 'R_ach', 'at Cmax', 'at Cmed', 'at Cmin', 'span', 'resol.',
        'span/res'))
    worst = 0.0
    for label, globs, bpath, S in CELLS:
        rows = data[label]
        v = [r['plateau'] for r in rows]
        med = statistics.median(v)
        a6 = A6[label]
        last = max(a6['safePoints'], key=lambda p: p['rl'])
        R = last['a4Rate']
        lo_eff, mid_eff, hi_eff = R / max(v), R / med, R / min(v)
        span = hi_eff - lo_eff
        res = RESOLUTION_RPS / med
        worst = max(worst, span / res)
        print('%-14s %10.1f %9.4f %9.4f %9.4f %9.4f %9.4f %6.2fx'
              % (label, R, lo_eff, mid_eff, hi_eff, span, res, span / res))
        out['cells'][label].update({
            'R_achLastSafe': R, 'rhoEffAtCmax': round(lo_eff, 4),
            'rhoEffAtCmedian': round(mid_eff, 4), 'rhoEffAtCmin': round(hi_eff, 4),
            'rhoEffSpan': round(span, 4), 'resolutionInEff': round(res, 4),
            'spanOverResolution': round(span / res, 3),
        })
    print()
    print('Worst case: the denominator range moves rho_eff,safe by %.2f bisection'
          % worst)
    print('steps. A span/res of 1.00 means denominator variability alone is exactly')
    print('as large as the search resolution the paper quotes.')

    hr('4. DOES THE QUOTED PER-CELL RESOLUTION INCLUDE THIS?')
    print('capacity_calibration.py:213 computes')
    print('    resolutionInEff = RESOLUTION_RPS / trueCapacity')
    print('i.e. the 5 rps search step divided by the MEDIAN plateau. It is the')
    print('search step alone. Denominator variability is not in it.')
    print()
    print('%-14s %11s %13s %13s %12s' % ('cell', 'quoted res', 'denom. span',
                                         'span/res', 'linearBound'))
    for label, globs, bpath, S in CELLS:
        c = out['cells'][label]
        res, span = c['resolutionInEff'], c['rhoEffSpan']
        comb = (res ** 2 + span ** 2) ** 0.5
        # SUPERSEDED. Kept under a new name rather than deleted: it is in a
        # committed artefact and earlier analysis may have read it. Quadrature
        # treats its two terms as independent variances; neither is one. The
        # search-grid width is deterministic and the plateau range is an
        # observed extreme-to-extreme span, so nothing in the design licenses
        # combining them that way.
        c['supersededCombinedQuadrature'] = round(comb, 4)
        c['supersededCombinedQuadratureNote'] = (
            'Superseded by linearBound. Quadrature treats the search-grid width '
            'and the observed plateau range as independent variances; the first '
            'is a deterministic grid step and the second an observed range, '
            'neither is a variance, and nothing in the design licenses adding '
            'them in quadrature. linearBound adds them directly, in units of the '
            'search resolution. Retained, not deleted, because it appeared in a '
            'committed artefact.')
        # The bound the manuscript uses: search step plus the observed
        # denominator span, added linearly, in units of the search resolution.
        c['linearBound'] = round(1 + c['spanOverResolution'], 3)
        print('%-14s %11.4f %13.4f %12.3fx %11.3fx'
              % (label, res, span, c['spanOverResolution'], c['linearBound']))
    print()
    print('linearBound = 1 + span/resolution: the search step and the observed')
    print('denominator span added directly, as a multiple of the quoted resolution.')
    print('It replaces the quadrature combination, which treated a deterministic')
    print('grid width and an observed range as though they were variances.')

    json.dump(out, open('results/W7-denominator-uncertainty.json', 'w'), indent=2)
    print()
    print('wrote results/W7-denominator-uncertainty.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
