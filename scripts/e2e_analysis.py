#!/usr/bin/env python3
"""E2e analysis: the overhead measured three ways, and the corrected boundary.

Works from run records rather than boundary files. The bisection was abandoned
mid-campaign (E2E-PLAN addendum 2, corrected by addendum 3) and replaced by
direct probes, so the bracket is computed here from the same SAFE/UNSAFE rules
locate_boundary applies.

Three measurements of one per-request cost, which do not agree:

  90% load, smooth driver    experiment 1, open-loop pacer below saturation
  saturated, smooth driver   experiment 1, closed loop
  in situ, during the drain  experiment 2, probe reset at restore, read at drain

Only the saturated figure predicts where the cell actually breaks. The in-situ
figure is the better instrument in principle and the wrong predictor in practice,
and both are reported.

Usage: python3 scripts/e2e_analysis.py
"""
import collections
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import RESOLUTION_RPS, classify  # noqa: E402

C_D = 2000.0
UNCORRECTED = {'c10': 0.9137, 'c50': 0.9826}      # E1 midpoints, uncorrected
UNCORRECTED_GAP = 0.0706
# Registered in E2E-PLAN addendum 1, before any boundary run.
REG = {'c10': {'sleepUs': 4537, 'conc': 10, 'svcMs': 5,
               'ovSat': 0.4947, 'ov90': 0.5165, 'rhoSat': 0.9937, 'rho90': 0.9894,
               'predPlateau': 1987.4},
       'c50': {'sleepUs': 24537, 'conc': 50, 'svcMs': 25,
               'ovSat': 0.4914, 'ov90': 0.5114, 'rhoSat': 0.9989, 'rho90': 0.9981,
               'predPlateau': 1997.7}}


def ms(ns):
    return ns / 1e6


def achieved(rec):
    """Total delivered rate over the drain: live issue rate plus recovery."""
    td = rec.get('tDrainSec') or 0
    if td <= 0:
        return None
    inj = [p['injRate'] for p in (rec.get('timeline') or [])
           if p['tSec'] <= td and p.get('injRate')]
    if not inj:
        return None
    return rec['backlogAtRestore'] / td + statistics.median(inj)


def main():
    out = {'registered': REG, 'uncorrected': UNCORRECTED, 'cells': {}}

    print('=== experiment 1: calibration and the probe control ===')
    print('%-14s %11s %13s %7s' % ('condition', 'served rps', 'overhead ms', 'probe'))
    for p in sorted(glob.glob('results/e2e/exp1-*.json')):
        d = json.load(open(p))
        o = d['overhead']
        print('%-14s %11.1f %13s %7s' % (
            d['label'], d['servedRps'],
            '%.4f' % ms(o['total']['meanNs']) if o.get('enabled') else '-',
            'on' if o.get('enabled') else 'off'))
    for s in ('s5', 's25'):
        try:
            on = json.load(open('results/e2e/exp1-%s-sat-on.json' % s))['servedRps']
            off = json.load(open('results/e2e/exp1-%s-sat-off.json' % s))['servedRps']
            print('  probe control %-4s off %.1f on %.1f  delta %+.2f%%  %s'
                  % (s, off, on, 100 * (on - off) / off,
                     'PASS' if abs(on - off) / off < 0.005 else 'FAIL'))
        except Exception:
            pass

    print()
    print('=== experiment 2: plateau gate, probes, and the bracket ===')
    for arm, reg in REG.items():
        cell = {'registered': reg}
        pl = 'results/e2e/exp2-%s-plateau.json' % arm
        if os.path.exists(pl):
            d = json.load(open(pl))
            cell['plateau'] = round(d['servedRps'], 1)
            cell['plateauErrPct'] = round(100 * (d['servedRps'] - reg['predPlateau'])
                                          / reg['predPlateau'], 3)
            cell['ceilingRho'] = round(d['servedRps'] / C_D, 4)

        by = collections.defaultdict(list)
        for p in sorted(glob.glob('results/e2e/e2e-%s-c0-rl*-r*.json' % arm)):
            by[json.load(open(p))['params']['rateLimitRps']].append(json.load(open(p)))
        pts = []
        for rl in sorted(by):
            rs = by[rl]
            v = [r['vSLO'] for r in rs]
            ach = [a for a in (achieved(r) for r in rs) if a]
            cy = [ms((r.get('overheadDrain', {}).get('cycle') or {}).get('meanNs', 0))
                  for r in rs]
            ov = [ms((r.get('overheadDrain', {}).get('total') or {}).get('meanNs', 0))
                  for r in rs]
            cy = [x for x in cy if x]
            ov = [x for x in ov if x]
            pts.append({
                'rl': rl, 'n': len(rs), 'class': classify(v),
                'vSLO': [round(x, 4) for x in v],
                'achievedRps': round(statistics.median(ach), 1) if ach else None,
                'rho': round(statistics.median(ach) / C_D, 4) if ach else None,
                'queuePeak': max(r['supplementary']['drainQueueDepthPeak'] for r in rs),
                'liveP99Ms': max(r['supplementary']['drainLiveP99Ms'] for r in rs),
                'cycleMs': round(statistics.median(cy), 4) if cy else None,
                'overheadMs': round(statistics.median(ov), 4) if ov else None,
            })
        cell['points'] = pts
        safe = [p for p in pts if p['class'] == 'SAFE']
        uns = [p for p in pts if p['class'] == 'UNSAFE']
        if safe and uns:
            lo = max(safe, key=lambda p: p['rl'])
            above = [p for p in uns if p['rl'] > lo['rl']]
            if above:
                hi = min(above, key=lambda p: p['rl'])
                cell['bracket'] = {
                    'rl': [lo['rl'], hi['rl']], 'rlWidth': hi['rl'] - lo['rl'],
                    'rho': [lo['rho'], hi['rho']],
                    'rhoWidth': round(hi['rho'] - lo['rho'], 4),
                    'rhoMid': round((lo['rho'] + hi['rho']) / 2.0, 4),
                    'atRlResolution': (hi['rl'] - lo['rl']) <= RESOLUTION_RPS,
                }
        insitu = [p['overheadMs'] for p in pts if p['overheadMs']]
        if insitu:
            cell['inSituOverheadMs'] = round(statistics.median(insitu), 4)
            cell['inSituCapacity'] = round(
                reg['conc'] / (statistics.median([p['cycleMs'] for p in pts if p['cycleMs']])
                               / 1000.0), 1)
            cell['inSituRho'] = round(cell['inSituCapacity'] / C_D, 4)
        out['cells'][arm] = cell

        print()
        print('--- %s (sleep %d us, concurrency %d) ---' % (arm, reg['sleepUs'], reg['conc']))
        if 'plateau' in cell:
            print('  plateau gate: measured %.1f, predicted %.1f, error %+.2f%%  %s'
                  % (cell['plateau'], reg['predPlateau'], cell['plateauErrPct'],
                     'PASS' if abs(cell['plateauErrPct']) < 1.0 else 'FAIL'))
        print('  %6s %3s %10s %8s %8s %8s %9s %-22s %s'
              % ('rl', 'n', 'achieved', 'rho', 'qPeak', 'liveP99', 'cycle ms', 'vSLO', 'class'))
        for p in pts:
            print('  %6d %3d %10s %8s %8d %8.0f %9s %-22s %s'
                  % (p['rl'], p['n'],
                     '%.1f' % p['achievedRps'] if p['achievedRps'] else '-',
                     '%.4f' % p['rho'] if p['rho'] else '-',
                     p['queuePeak'], p['liveP99Ms'],
                     '%.4f' % p['cycleMs'] if p['cycleMs'] else '-',
                     ', '.join('%.3f' % x for x in p['vSLO'][:3]), p['class']))
        if 'bracket' in cell:
            b = cell['bracket']
            print('  bracket rl [%d, %d] (%d rps%s) -> rho [%.4f, %.4f] width %.4f mid %.4f'
                  % (b['rl'][0], b['rl'][1], b['rlWidth'],
                     '' if b['atRlResolution'] else ', coarser than %d' % RESOLUTION_RPS,
                     b['rho'][0], b['rho'][1], b['rhoWidth'], b['rhoMid']))
            step = RESOLUTION_RPS / C_D
            for name, val in [('saturated (registered)', reg['rhoSat']),
                              ('90% load', reg['rho90']),
                              ('in situ', cell.get('inSituRho')),
                              ('measured ceiling', cell.get('ceilingRho'))]:
                if val is None:
                    continue
                inside = b['rho'][0] <= val <= b['rho'][1]
                print('    %-22s %.4f  %s' % (
                    name, val,
                    'INSIDE the bracket' if inside
                    else 'outside, by %+.4f = %+.1f steps'
                         % (b['rhoMid'] - val, (b['rhoMid'] - val) / step)))
        if 'inSituOverheadMs' in cell:
            print('  overhead: 90%% load %.4f | saturated %.4f | in situ %.4f ms'
                  % (reg['ov90'], reg['ovSat'], cell['inSituOverheadMs']))

    print()
    print('=== the gap between the arms ===')
    mids = {a: c['bracket']['rhoMid'] for a, c in out['cells'].items() if 'bracket' in c}
    if len(mids) == 2:
        gap = abs(mids['c50'] - mids['c10'])
        out['residualGap'] = round(gap, 4)
        # SUPERSEDED, kept at its original position under a new name rather than
        # deleted: it is in a committed artefact. It divides a two-cell gap on
        # the drain-window estimator by UNCORRECTED_GAP, a seven-cell range on
        # A4, so its before and after are not the same quantity.
        out['supersededFractionRemoved'] = round(100 * (1 - gap / UNCORRECTED_GAP), 1)
        out['supersededFractionRemovedNote'] = (
            'Superseded by the matched 94-95% accounting in '
            'results/W8-effect-size-accounting.json. This value divides a '
            'two-cell gap on the drain-window estimator by 0.0706, which is '
            'the range of A4 interval midpoints across all seven cells, so its '
            'before and after were computed on unmatched estimators, '
            'aggregators, observation intervals and statistics. Retained, not '
            'deleted, because it appeared in a committed artefact.')
        out['residualGapNote'] = (
            'The difference between the c50 and c10 bracket midpoints of the '
            'corrected cells, on the drain-window estimator. Correctly computed '
            'as that. It is NOT the matched corrected residual: that uses the '
            'last SAFE point on both sides and is 0.0032 (drain-window) or '
            '0.0043 (A4), in results/W8-effect-size-accounting.json.')
        # A pointer, not a copy: W8 is computed by effect_size_accounting.py,
        # which reads this file, so recomputing its figures here would create a
        # second source of truth and a regeneration cycle.
        out['matchedAccounting'] = {
            'file': 'results/W8-effect-size-accounting.json',
            'writtenBy': 'scripts/effect_size_accounting.py',
            'drainWindow': ['matched.gapRhoUncorrected', 'matched.gapRhoCorrected',
                            'matched.gapRpsUncorrected', 'matched.gapRpsCorrected',
                            'matched.fractionRemovedRho', 'matched.fractionRemovedRps'],
            'deliverySpanA4': ['matchedA4.gapRhoUncorrected',
                               'matchedA4.gapRhoCorrected',
                               'matchedA4.fractionRemovedRho', 'matchedA4.caveat'],
            'note': 'The matched before/after accounting of the inter-arm gap. '
                    'Named here, not copied, so there is one source of truth '
                    'and no regeneration cycle.',
        }
        print('  uncorrected        %.4f  (c10 %.4f, c50 %.4f)'
              % (UNCORRECTED_GAP, UNCORRECTED['c10'], UNCORRECTED['c50']))
        print('  predicted residual 0.0052  (registered)')
        print('  measured residual  %.4f  -> %.1f%% of the gap removed '
              '(SUPERSEDED: unmatched; see results/W8-effect-size-accounting.json)'
              % (gap, out['supersededFractionRemoved']))
    else:
        print('  pending: %s' % ', '.join(a for a in REG if a not in mids))

    json.dump(out, open('results/E2E-analysis.json', 'w'), indent=2)
    print()
    print('wrote results/E2E-analysis.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
