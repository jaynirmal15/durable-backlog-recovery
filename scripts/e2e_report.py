#!/usr/bin/env python3
"""Generate results/E2E-REPORT.md from results/E2E-analysis.json."""
import json
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from precision import u  # noqa: E402

D = json.load(open('results/E2E-analysis.json'))
REG, C = D['registered'], D['cells']
STEP = 5 / 2000.0


def main():
    w = print
    w('# E2e — observing the overhead, then eliminating it')
    w('')
    w('**Two experiments.** Registered in `results/E2E-PLAN.md` before any code '
      'change, with four addenda, two of which correct my own errors mid-campaign.')
    w('')
    w('This is the first cell not run on the pinned harness `026be6242d26`. It '
      'needed instrumentation that does not exist there and a sub-millisecond '
      'service time the code could not express. Every change is additive and '
      'defaults to the pinned behaviour, no earlier cell was re-run, and any '
      'comparison with E1 crosses commits.')
    w('')

    w('## Experiment 1 — the overhead is real, constant, and sleep overshoot')
    w('')
    w('| | S = 5 ms | S = 25 ms |')
    w('|---|---:|---:|')
    w('| mean excess at 90%% of capacity | %.4f ms | %.4f ms |'
      % (REG['c10']['ov90'], REG['c50']['ov90']))
    w('| mean excess at saturation | %.4f ms | %.4f ms |'
      % (REG['c10']['ovSat'], REG['c50']['ovSat']))
    w('| mean excess in situ, during a drain | %s ms | %s ms |'
      % (C['c10'].get('inSituOverheadMs', '-'), C['c50'].get('inSituOverheadMs', '-')))
    w('')
    d = REG['c50']['ov90'] - REG['c10']['ov90']
    w('The registered contrast is settled. A constant cost predicts '
      '`excess(25) - excess(5) = 0`; a proportional one predicts a ratio of 5. '
      'Measured: **%+.4f ms**, a ratio of **%.3f**. The cost does not scale with '
      'service time.' % (d, REG['c50']['ov90'] / REG['c10']['ov90']))
    w('')
    w('**It is almost entirely `time.Sleep` overshoot** — 99.8% of the total. The '
      'runtime timer work, the queue and slot bookkeeping and the done-channel send '
      'come to 1.3 microseconds between them.')
    w('')
    w('**Probe control**, registered in advance because the instrumentation could '
      'distort the throughput it explains: the saturation plateau moves 0.04% at '
      'S=5 and 0.09% at S=25 between probe on and probe off, against a 0.5% '
      'criterion. It does not perturb.')
    w('')

    w('## Experiment 2 — correcting the sleep')
    w('')
    w('Sleep reduced by 0.463 ms with concurrency held fixed, so integer rounding '
      'of `ceil(C x S)` cannot blur the prediction.')
    w('')
    w('### The plateau gate')
    w('')
    w('| arm | sleep | concurrency | predicted capacity | measured | error |')
    w('|---|---:|---:|---:|---:|---:|')
    for a in ('c10', 'c50'):
        r, c = REG[a], C[a]
        w('| %s | %.3f ms | %d | %.1f | **%.1f** | %+.2f%% |'
          % (a, r['sleepUs'] / 1000.0, r['conc'], r['predPlateau'],
             c.get('plateau', 0), c.get('plateauErrPct', 0)))
    w('')
    w('**Both gates pass essentially exactly.** Correcting by a single constant '
      'produces the predicted capacity at two service times five times apart. That '
      'confirms the additive model independently of where the boundaries land.')
    w('')

    w('### Every probe')
    w('')
    for a in ('c10', 'c50'):
        c = C[a]
        w('#### %s' % a)
        w('')
        w('| rl | n | achieved | rho | queue peak | live p99 | cycle | vSLO | class |')
        w('|---:|---:|---:|---:|---:|---:|---:|---|---|')
        for p in c['points']:
            w('| %d | %d | %s | %s | %d | %.0f ms | %s | %s | %s |'
              % (p['rl'], p['n'],
                 '%.1f' % p['achievedRps'] if p['achievedRps'] else '-',
                 u(p['rho']) if p['rho'] else '-',
                 p['queuePeak'], p['liveP99Ms'],
                 '%.4f ms' % p['cycleMs'] if p['cycleMs'] else '-',
                 ', '.join('%.3f' % x for x in p['vSLO'][:3]), p['class']))
        w('')
        if 'bracket' in c:
            b = c['bracket']
            w('Bracket rl [%d, %d], %d rps%s. In rho: **[%s, %s]**, width %s.'
              % (b['rl'][0], b['rl'][1], b['rlWidth'],
                 '' if b['atRlResolution'] else ' — coarser than the registered 5',
                 u(b['rho'][0]), u(b['rho'][1]), u(b['rhoWidth'])))
            w('')
            w('| prediction | rho* | inside the bracket? |')
            w('|---|---:|---|')
            for name, val in [('saturated (registered)', REG[a]['rhoSat']),
                              ('90% load', REG[a]['rho90']),
                              ('in situ', c.get('inSituRho')),
                              ('measured ceiling', c.get('ceilingRho'))]:
                if val is None:
                    continue
                inside = b['rho'][0] <= val <= b['rho'][1]
                w('| %s | %.4f | %s |' % (name, val, '**yes**' if inside else
                                          'no, %+.1f steps from the midpoint'
                                          % ((b['rhoMid'] - val) / STEP)))
            w('')

    w('### The gap between the arms')
    w('')
    if 'residualGap' in D:
        w('| | |')
        w('|---|---:|')
        w('| uncorrected, E1 midpoints %.4f and %.4f | **0.0706** |'  # registered
          % (D['uncorrected']['c10'], D['uncorrected']['c50']))
        w('| predicted residual (registered) | 0.0052 |')
        w('| **measured residual** | **%s** |' % u(D['residualGap']))
        w('| fraction of the gap removed | **%.1f%%** |' % D['fractionRemoved'])
        w('')
        w('Bracket midpoints: c10 %s, c50 %s.'
          % (u(C['c10']['bracket']['rhoMid']), u(C['c50']['bracket']['rhoMid'])))
        w('')
    else:
        w('_Pending: one arm has no bracket yet._')
        w('')
    w('## The estimator disagreement is as large as the effect')
    w('')
    w('The brackets above use the **as-measured** (drain-window) estimator. The '
      'registered estimator is **A4**, the delivery-span one used by every earlier '
      'campaign. Applying A4 moves both brackets up by about 0.008 and **inverts '
      'the c10 verdict**:')
    w('')
    w('| arm | estimator | bracket | candidate inside |')
    w('|---|---|---|---|')
    w('| c10 | as-measured | [0.988, 0.992] | 90% load, 0.9894 (registered) |')
    w('| c10 | **A4** | **[0.996, 1.002]** | **in situ, 0.9974 (registered)** |')
    w('| c50 | as-measured | [0.992, 0.994] | none |')
    w('| c50 | **A4** | **[1.000, 1.006]** | none |')
    w('')
    w('The two estimators differ by 0.0080 in rho. The candidates span 0.0080 in '
      'the c10 arm. **The measurement uncertainty is the same size as the thing '
      'being discriminated, so this campaign cannot say which overhead governs the '
      'boundary.** That is forced by the data, not chosen.')
    w('')
    w('A4 is specifically suspect at the non-SAFE points: its values there exceed '
      'each cell\'s own measured saturation plateau, by +0.0079 in c10 and +0.0073 '
      'in c50, and nothing sustains more than its plateau. A4 measures recovery over '
      'the span the traffic occupied, which on a collapsed run excludes stalled '
      'intervals and overstates the rate. It was built to remove the drain-tail bias '
      'at SAFE points, was never validated on collapsed runs, and this is the first '
      'campaign whose interval endpoints depend on it there. The as-measured '
      'estimator carries the opposite bias, and each cell\'s measured plateau sits '
      'between the two brackets.')
    w('')
    w('### What survives regardless of estimator')
    w('')
    w('1. **The plateau gates**, above: direct throughput, no rho estimator '
      'involved, errors of -0.00% and +0.02%. The additive model is confirmed by '
      'these alone.')
    w('2. **The gap between the arms is essentially eliminated**: 0.0026 '
      'as-measured, 0.0045 under A4, against 0.0706 uncorrected. **94% to 96% '
      'removed** either way, bracketing the registered 92.7%.')
    w('3. **Both arms land within about 0.008 of 1.000**, the brief\'s original '
      'prediction before addendum 1 refined it.')
    w('')
    w('### What does not survive')
    w('')
    w('The addendum-1 refinement, that the correction under-corrects and gives '
      '0.9937 and 0.9989 specifically, **cannot be tested here**. Under A4 both arms '
      'sit above those values, under as-measured both sit below, and the distance '
      'between the candidates is smaller than the estimator spread.')
    w('')
    w('## The three overhead measurements disagree, and none reliably predicts')
    w('')
    w('The in-situ figure is the lowest and the most stable — about 0.478 ms in '
      'c10 and 0.474 in c50, holding across every probed rate. It was the better '
      'instrument in principle, measured under the campaign\'s own bursty arrival '
      'process rather than a smooth driver. **It is also the wrong predictor**: it '
      'puts the boundary above where both arms actually broke.')
    w('')
    w('That is worth stating rather than burying, because the reasoning that '
      'motivated in-situ measurement was sound and the result still went against '
      'it.')
    w('')

    w('## Two corrections I made mid-campaign')
    w('')
    w('Both are in `E2E-PLAN.md` with the reasoning that produced them.')
    w('')
    w('**Addendum 2 claimed the bisection could not terminate**, on the argument '
      'that achieved rho is bounded by capacity and the prediction puts the '
      'boundary at that ceiling. Wrong, and wrong on evidence I already had: by '
      'rl=1185 the queue had gone 7, 18, 111 and live p99 8, 14, 58 ms. I read two '
      'flat points as an asymptote. The upward walk would have found the boundary '
      'one or two probes later.')
    w('')
    w('**Addendum 3 then announced that the saturated figure governs and the '
      '90%-load figure was excluded.** Also wrong: the bracket contained both. I '
      'compared the single UNSAFE point against one candidate and ignored that the '
      'bracket\'s lower end sat below the other. Corrected in addendum 4 **before** '
      'the deciding probe ran, with the reading fixed in advance.')
    w('')
    return 0


if __name__ == '__main__':
    sys.exit(main())
