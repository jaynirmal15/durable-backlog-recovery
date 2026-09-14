#!/usr/bin/env python3
"""Generate results/E2E-REPORT.md from results/E2E-analysis.json."""
import json
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from precision import u  # noqa: E402

D = json.load(open('results/E2E-analysis.json'))
# The matched before/after accounting. Its only job is this comparison; the
# corrected gap table below quotes it rather than restating its numbers.
W8 = json.load(open('results/W8-effect-size-accounting.json'))
# Per-point A4 utilisation for the E2e cells. Retained from the campaign; the
# consumer traces it was derived from are gitignored corpus-wide, as they are
# for every other campaign, so it cannot be re-derived from raw data -- but the
# values themselves are committed and the brackets below are computed from them.
A4 = json.load(open('results/E2E-a4.json'))
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
        e1diff = D['uncorrected']['c50'] - D['uncorrected']['c10']
        m = W8['matched']
        w('> **CORRECTED, 2026-09-15. The pair below is withdrawn; use the matched '
          'accounting that follows it.** The table as first published read '
          '*"uncorrected, E1 midpoints %.4f and %.4f | 0.0706"*. **Those two '
          'midpoints differ by %.4f, not 0.0706.** The 0.0706 is E2d\'s '
          '`rhoStarSpread` — the RANGE of rho* interval midpoints across all '
          '**seven** cells (`capacity_calibration.py:221`) — and it was being '
          'labelled here as a two-arm difference. It was also being differenced '
          'against a corrected residual computed on a different estimator, a '
          'different aggregator and a different observation interval, so the '
          'before and after were not the same quantity. See '
          '`results/METHOD-AUDIT.md` item 19.'
          % (D['uncorrected']['c10'], D['uncorrected']['c50'], e1diff))
        w('')
        w('**Withdrawn pair** — retained so the correction is legible, not for quotation:')
        w('')
        w('| | |')
        w('|---|---:|')
        w('| ~~uncorrected, E1 midpoints %.4f and %.4f~~ | ~~0.0706~~ |'
          % (D['uncorrected']['c10'], D['uncorrected']['c50']))
        w('| predicted residual (registered) | 0.0052 |')
        w('| ~~measured residual~~ | ~~%s~~ |' % u(D['residualGap']))
        w('| ~~fraction of the gap removed~~ | ~~%.1f%%~~ |' % D['fractionRemoved'])
        w('')
        w('**Matched accounting.** Each recipe applied identically to both corpora: '
          '%s; and the same against the delivery-span estimator. Generated by '
          '`scripts/effect_size_accounting.py`.' % m['recipe'])
        w('')
        w('| | uncorrected | corrected | removed |')
        w('|---|---:|---:|---:|')
        # Four decimals deliberately. precision.py scopes the resolution-matched
        # rule to a MEASURED UTILISATION at its cell's resolution; an inter-arm
        # gap is a difference between two cells and is not that quantity, on the
        # same reasoning that exempts vSLO. At three decimals 0.0032 renders as
        # 0.003 and stops being distinguishable from the withdrawn 0.0026, which
        # is the comparison this table exists to make.
        w('| inter-arm gap, in rho | %.4f | %.4f | **%.0f%%** |'
          % (m['gapRhoUncorrected'], m['gapRhoCorrected'],
             m['fractionRemovedRho']))
        w('| inter-arm gap, in throughput (rps) | %.1f | %.1f | **%.0f%%** |'
          % (m['gapRpsUncorrected'], m['gapRpsCorrected'], m['fractionRemovedRps']))
        a = W8['matchedA4']
        w('| the same, under A4 on both sides | %.4f | %.4f | **%.0f%%** |'
          % (a['gapRhoUncorrected'], a['gapRhoCorrected'],
             a['fractionRemovedRho']))
        w('')
        w('**The matched answer is estimator-dependent: %.0f%% to %.0f%%.** Both '
          'rows are matched; the withdrawn 96.3%% was not. The A4 route carries one '
          'caveat the drain-window route does not — %s.'
          % (a['fractionRemovedRho'], m['fractionRemovedRho'], a['caveat']))
        w('')
        w('The two rows agree because the denominator is the same constant on both '
          'sides; the throughput row is the one free of any utilisation estimator. '
          'The rho row is given to four decimals because an inter-arm gap is a '
          'difference between two cells, not a utilisation at one cell\'s '
          'resolution, and the resolution-matched rule of section IV covers the '
          'latter. '
          'The registered prediction was 0.0052 and 92.7% removed, so the '
          'correction removed somewhat more of the gap than registered under '
          'either estimator, not less.')
        w('')
        w('Both estimators are available on both sides. The drain-window values '
          'are retained for every point of both corpora; the delivery-span values '
          'are retained in the boundary files for E1, E2 and E2b and in '
          '`results/E2E-a4.json` for the corrected cells. Neither set can be '
          're-derived from raw data, because the consumer traces the delivery-span '
          'estimator reads are excluded from the repository corpus-wide. The '
          'routes are reported side by side rather than one being chosen.')
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
    # Both estimators' rows are now computed. The as-measured bracket comes from
    # the analysis artefact, the A4 bracket from results/E2E-a4.json, which
    # retains the per-point A4 utilisation for these cells.
    def a4_bracket(arm):
        pts = sorted((int(k.split('-')[1]), v) for k, v in A4.items()
                     if k.startswith(arm + '-'))
        safe = [p for p in pts if p[1]['class'] == 'SAFE']
        lo = max(safe)
        hi = min(p for p in pts if p[1]['class'] != 'SAFE' and p[0] > lo[0])
        return lo[1]['a4Rho'], hi[1]['a4Rho']

    A4_INSIDE = {'c10': '**in situ, 0.9974 (registered)**', 'c50': 'none'}
    AM_INSIDE = {'c10': '90% load, 0.9894 (registered)', 'c50': 'none'}
    w('| arm | estimator | bracket | candidate inside |')
    w('|---|---|---|---|')
    for arm in ('c10', 'c50'):
        lo, hi = C[arm]['bracket']['rho']
        alo, ahi = a4_bracket(arm)
        w('| %s | as-measured | [%s, %s] | %s |'
          % (arm, u(lo), u(hi), AM_INSIDE[arm]))
        w('| %s | **A4**&nbsp;[^a4] | **[%.4f, %.4f]** | %s |'
          % (arm, alo, ahi, A4_INSIDE[arm]))
    w('')
    w('[^a4]: **Provenance.** The A4 rows are computed from '
      '`results/E2E-a4.json`, which retains the per-point delivery-span '
      'utilisation for these cells; the brackets above are its last SAFE and '
      'first UNSAFE points. They are **retained measurements, not re-derivable '
      'ones**: A4 needs per-arrival timestamps from the consumer trace, the '
      'one-second `timeline` cannot supply them, and consumer traces are '
      'excluded from the repository corpus-wide (`.gitignore`: `*.jsonl`, '
      '`*.jsonl.*`). That is true of every A4 value in every campaign — E1, E2 '
      'and E2b preserve theirs inside their boundary files, and E2e, which has '
      'no boundary file, preserves its own here. Of the traces still on disk, '
      'none survives at the c10 arm\'s last SAFE point (rl=1185); in the c50 arm '
      'two of three repetitions survive at each endpoint and recomputing from '
      'those gives [1.0006, 1.0076] against the [%.4f, %.4f] retained here, a '
      'difference consistent with the missing third repetition. '
      '`results/E2E-a4.json` is written by no script in this repository and read '
      'by nothing else; it is an orphan artefact of the campaign.'
      % a4_bracket('c50'))
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
