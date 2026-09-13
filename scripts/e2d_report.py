#!/usr/bin/env python3
"""Generate results/E2D-REPORT.md from results/E2D-capacity-calibration.json."""
import json
import statistics

D = json.load(open('results/E2D-capacity-calibration.json'))
C = D['cells']
OV = D['overheadMs']
COL = D['collapse']


def miss(c):
    lo, hi = c['rhoEffInterval']
    return 0.0 if lo <= 1.0 <= hi else (1.0 - hi if hi < 1.0 else lo - 1.0)


def main():
    w = print
    w('# E2d — is the boundary saturation, with configured C overstating truth?')
    w('')
    w('**Analysis only, archived data. No instance.** Arithmetic as asked, no reframing.')
    w('')
    w('## Answer')
    w('')
    w('Both tests support the hypothesis.')
    w('')
    w('| | |')
    w('|---|---|')
    w('| implied per-request overhead | **%.3f - %.3f ms**, median **%.3f**, CV **%.1f%%** |'
      % (OV['min'], OV['max'], OV['median'], OV['cvPct']))
    w('| every measured plateau vs the value predicted at 0.46 ms | within **%.2f%%** |'
      % max(abs(c['predErrPct']) for c in C.values()))
    w('| spread of the boundary against configured C | %.4f |' % COL['rhoStarSpread'])
    w('| spread against measured true capacity | **%.4f** |' % COL['rhoEffSpread'])
    w('| collapse factor | **%.0fx** |' % (COL['rhoStarSpread'] / COL['rhoEffSpread']))
    w('| median effective utilisation at the boundary | **%.4f** |' % COL['rhoEffMedian'])
    w('')
    w('**Test 3 is not needed.** It was contingent on tests 1 and 2 being '
      'ambiguous. An overhead constant to 2.4%% across two service times and three '
      'capacities, and a %.0fx collapse, is not ambiguous.'
      % (COL['rhoStarSpread'] / COL['rhoEffSpread']))
    w('')

    w('## One correction to the stated prediction')
    w('')
    w('The brief predicts "~1827 at c10 and c50\'s C=2000 arms". The hypothesis does '
      'not predict a shared plateau there. True capacity is `C x S/(S+ov)`, which '
      'depends on S, so at C=2000 it is **1831 at S=5 ms** but **1964 at S=25 ms**. '
      'A shared 1827 would mean equal rho* in both arms, which is the very thing '
      'being explained. The measured values are 1829 and 1964, matching the '
      'per-arm predictions.')
    w('')

    w('## Test 1 — true capacity from the plateau at UNSAFE points')
    w('')
    w('| cell | S | C_d | runs | true capacity | predicted at 0.46 | error | implied overhead |')
    w('|---|---:|---:|---:|---:|---:|---:|---:|')
    for l, c in C.items():
        w('| %s | %d | %d | %d | **%.1f** | %.1f | %+.2f%% | **%.3f ms** |'
          % (l, c['S'], c['faultCapacity'], c['nUnsafeRuns'], c['trueCapacity'],
             c['predictedAt046'], c['predErrPct'], c['impliedOverheadMs']))
    w('')
    w('The overhead is recovered as `ov = S x (C/plateau - 1)`. It comes out constant '
      'at **%.3f ms** across S = 5 and 25 ms and C = 400, 1400 and 2000, with a '
      'standard deviation of %.4f ms.' % (OV['median'], OV['sd']))
    w('')

    w('## Test 2 — the boundary against true capacity')
    w('')
    w('| cell | rho* vs configured C | effective vs true capacity | brackets 1.0 | miss, in 5 rps steps |')
    w('|---|---|---|---|---:|')
    for l, c in C.items():
        m = miss(c)
        w('| %s | [%.4f, %.4f] | **[%.4f, %.4f]** | %s | %.2f |'
          % (l, c['rhoStarInterval'][0], c['rhoStarInterval'][1],
             c['rhoEffInterval'][0], c['rhoEffInterval'][1],
             'yes' if c['bracketsUnity'] else 'no', m / c['resolutionInEff']))
    w('')
    nb = COL['notBracketing']
    w('Five of seven intervals bracket 1.0 outright. The two that do not are both '
      'the reduced-capacity regime, and they fall short by **0.18 and 0.14 of a '
      'single 5 rps bisection step**. The boundary is located to 5 rps, so a miss of '
      'a fifth of a step is not a discrepancy the experiment can resolve.')
    w('')
    w('**Is the residual within measurement resolution?** The residual spread across '
      'cells is %.4f. One 5 rps step is %.4f in effective units for the C=2000 cells '
      'and %.4f for E2b. So the entire remaining spread is about one bisection step '
      'wide, and no cell departs from 1.0 by as much as a quarter of a step.'
      % (COL['rhoEffSpread'], min(c['resolutionInEff'] for c in C.values()),
         max(c['resolutionInEff'] for c in C.values())))
    w('')

    w('## Method note — the window decided this, not the statistic')
    w('')
    w('True capacity is the maximum throughput sustained when the server always has '
      'work, measured here as the highest 30-second sustained served rate in each '
      'UNSAFE run, from the downstream\'s own cumulative counter.')
    w('')
    w('Three narrower windows were tried first and all biased the answer the same '
      'way, because the backlog runs out at the end of a drain, the queue empties and '
      'the server idles between requests. Those ticks are not measurements of '
      'capacity:')
    w('')
    naive = [c['S'] * (c['faultCapacity'] / c['naiveWholeWindow'] - 1) for c in C.values()]
    w('| estimator | implied overhead | CV | reads as |')
    w('|---|---|---:|---|')
    w('| whole drain window, endpoints | %.3f - %.3f ms | %.0f%% | an overhead that varies by arm |'
      % (min(naive), max(naive), 100 * statistics.pstdev(naive) / statistics.mean(naive)))
    w('| max 30 s sustained | **%.3f - %.3f ms** | **%.1f%%** | a single constant |'
      % (OV['min'], OV['max'], OV['cvPct']))
    w('')
    w('`queued >= concurrency` did not fix it, because the queue passes through that '
      'level on its way to empty. `queued >= 5 x concurrency` did not either, because '
      'it means a queue of 50 for one arm and 250 for the other, making the arms '
      'incomparable in exactly the way it was meant to prevent. A maximum over '
      'sustained windows needs no queue threshold at all and cannot be dragged down '
      'by desaturation; per-tick variation inside the saturated stretch is about '
      '0.4%%, so over 30 seconds any upward noise bias is under 0.1%%.')
    w('')
    w('Under the reduced-capacity regime the window starts after the capacity step at '
      't=20. Earlier ticks were served at the pre-fault capacity and belong to a '
      'different configuration.')
    w('')
    w('## What this does not establish')
    w('')
    w('The overhead is inferred, not observed. Nothing here measures a per-request '
      'cost directly; it is the residual between configured and achieved throughput, '
      'and the constant that reconciles them happens to be stable. Any mechanism '
      'adding a fixed cost per request would fit equally well, and this data cannot '
      'name which.')
    w('')
    w('Test 3, a direct load sweep with no recovery load, is the measurement that '
      'would observe it rather than infer it. It remains unrun because the brief '
      'made it contingent on ambiguity, and there is none.')
    return 0


if __name__ == '__main__':
    main()
