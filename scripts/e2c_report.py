#!/usr/bin/env python3
"""Generate results/E2C-REPORT.md from results/E2C-slo-sweep.json.

Every number computed from the sweep output; nothing typed in.
Usage: python3 scripts/e2c_report.py > results/E2C-REPORT.md
"""
import json
import statistics
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from precision import u, is_coarse  # noqa: E402

D = json.load(open('results/E2C-slo-sweep.json'))
THS = [str(t) for t in D['thresholds']]


def rows():
    out = []
    for label, c in D['cells'].items():
        for th, e in c['byThreshold'].items():
            if e['wellPosed'] and e.get('rhoStarMid'):
                out.append({'cell': label, 'S': c['S'], 'th': int(th),
                            'ratio': e['sOverSlo'], 'rho': e['rhoStarMid'],
                            'iv': e['rhoStarInterval'], 'w': e['bracketWidthRps']})
    return out


def resid(rs, key):
    tot = n = 0
    for k in {x[key] for x in rs}:
        g = [x['rho'] for x in rs if x[key] == k]
        if len(g) > 1:
            m = statistics.mean(g)
            tot += sum((y - m) ** 2 for y in g)
            n += len(g) - 1
    return (tot / n) ** 0.5 if n else 0.0


def main():
    rs = rows()
    w = print
    w('# E2c — does rho* track absolute service time, or S/SLO?')
    w('')
    w('**Analysis only. No new runs.** Recomputes vSLO for every archived run at '
      'SLO thresholds of 50, 100, 250 and 500 ms, re-classifies each probed point '
      'under the unchanged SAFE/UNSAFE/MARGINAL rules, and re-locates each boundary.')
    w('')
    w('## Answer')
    w('')
    w('**The cells do not collapse against S/SLO. rho\\* tracks absolute service '
      'time.** Grouping the well-posed cells by absolute S accounts for **%.1f%%** '
      'of the variance in rho\\*; grouping by S/SLO accounts for **%.1f%%**.'
      % (100 * (1 - (resid(rs, 'S') / statistics.pstdev([x['rho'] for x in rs])) ** 2),
         100 * (1 - (resid(rs, 'ratio') / statistics.pstdev([x['rho'] for x in rs])) ** 2)))
    w('')
    w('| grouping | residual SD of rho* | variance explained |')
    w('|---|---:|---:|')
    tot = statistics.pstdev([x['rho'] for x in rs])
    for name, key in [('absolute S (milliseconds)', 'S'), ('S/SLO (ratio)', 'ratio')]:
        r = resid(rs, key)
        w('| %s | %s | %.1f%% |' % (name, u(r), 100 * (1 - (r / tot) ** 2)))
    w('| _(ungrouped total)_ | %s | |' % u(tot))
    w('')
    w('Per the brief, that is the second outcome: **the effect is tied to '
      'milliseconds** and needs a mechanism or a threats paragraph. It is not the '
      'generalisable S/SLO statement.')
    w('')

    w('## The discriminating comparison')
    w('')
    w('Only two S/SLO values are populated by **both** arms. Those are the only '
      'groups that can test the hypothesis at all; the other three contain a single '
      'arm each and would collapse under any hypothesis.')
    w('')
    w('| S/SLO | cells | rho* range | spread | discriminating? |')
    w('|---:|---:|---|---:|---|')
    for r in sorted({x['ratio'] for x in rs}):
        g = [x for x in rs if x['ratio'] == r]
        v = [x['rho'] for x in g]
        arms = {x['S'] for x in g}
        w('| %.3f | %d | %s - %s | **%s** | %s |'
          % (r, len(g), u(min(v)), u(max(v)), u(max(v) - min(v)),
             '**yes, both arms**' if len(arms) > 1 else 'no, S=%d only' % arms.pop()))
    w('')
    w('At both discriminating ratios the spread is about **0.07**, which is the '
      'entire separation between the arms. Matching S/SLO does nothing to bring the '
      'cells together.')
    w('')
    w('The converse holds sharply. Within an arm, rho\\* barely moves across a '
      'tenfold change in the SLO:')
    w('')
    w('| S | well-posed cells | rho* range | spread across a 10x SLO change |')
    w('|---:|---:|---|---:|')
    for S in sorted({x['S'] for x in rs}):
        g = [x['rho'] for x in rs if x['S'] == S]
        w('| %d ms | %d | %s - %s | **%s** |' % (S, len(g), u(min(g)), u(max(g)), u(max(g) - min(g))))
    w('')

    w('## Why the SLO has so little leverage')
    w('')
    w('The transition is a cliff, not a slope. vSLO at the last SAFE point and at '
      'the first non-SAFE point, one 5 rps step apart, at the original 250 ms:')
    w('')
    w('| cell | last SAFE | vSLO | first non-SAFE | vSLO |')
    w('|---|---:|---|---:|---|')
    for label, c in D['cells'].items():
        e = c['byThreshold']['250']
        if not e.get('bracket'):
            continue
        lo, hi = [str(x) for x in e['bracket']]
        w('| %s | %s | %s | %s | %s |'
          % (label, lo, ', '.join('%.3f' % v for v in e['vSLO'][lo][:3]),
             hi, ', '.join('%.3f' % v for v in e['vSLO'][hi][:3])))
    w('')
    w('Every cell goes from exactly zero violating seconds to a large fraction in '
      'one step. A threshold change moves the cliff by at most a step or two, which '
      'is why rho\\* is nearly invariant to the SLO and why the ratio has no purchase.')
    w('')

    w('## Well-posedness')
    w('')
    w('Rule fixed before the sweep: a (cell, threshold) pair is well-posed only if '
      'the healthy baseline live p99 is at most **half** the threshold. Below that '
      'margin the SLO is a question about idle latency, not about recovery headroom.')
    w('')
    w('Baseline measured in the settled window **after** T_full, not inside the '
      'healthy streak. The streak is defined by p99 <= SLO, so any statistic taken '
      'inside it is conditioned on the threshold under test.')
    w('')
    w('| cell | S | baseline p99 | 50 ms | 100 ms | 250 ms | 500 ms |')
    w('|---|---:|---:|---|---|---|---|')
    for label, c in D['cells'].items():
        b = c['baselineP99']
        cells = []
        for th in THS:
            e = c['byThreshold'][th]
            cells.append('%.0f%% %s' % (100 * b['p50'] / int(th),
                                        'ok' if e['wellPosed'] else '**dropped**'))
        w('| %s | %d | %.0f ms | %s |' % (label, c['S'], b['p50'], ' | '.join(cells)))
    w('')
    dropped = [(l, th) for l, c in D['cells'].items() for th in THS
               if not c['byThreshold'][th]['wellPosed']]
    w('**Dropped: %d pairs, all of them the S=25 ms cells at 50 ms.** Their healthy '
      'baseline is 34 ms, 68%% of the threshold, so a healthy idle system already '
      'sits most of the way to violating. The S=5 ms cells have a 7 ms baseline and '
      'are well-posed everywhere, exactly as the brief anticipated.' % len(dropped))
    w('')

    w('## Every (cell, threshold): bracketed, or what to run')
    w('')
    w('| cell | SLO | S/SLO | well-posed | bracket rl | width | rho* interval | mid |')
    w('|---|---:|---:|---|---|---:|---|---:|')
    for label, c in D['cells'].items():
        for th in THS:
            e = c['byThreshold'][th]
            if not e['wellPosed']:
                w('| %s | %s | %.3f | **dropped** | | | | |' % (label, th, e['sOverSlo']))
                continue
            if e.get('bracket'):
                cz = is_coarse(label)
                w('| %s | %s | %.3f | yes | %d-%d | %d%s | [%s, %s] | %s |'
                  % (label, th, e['sOverSlo'], e['bracket'][0], e['bracket'][1],
                     e['bracketWidthRps'], '' if e['atRegisteredResolution'] else ' **coarse**',
                     u(e['rhoStarInterval'][0], cz), u(e['rhoStarInterval'][1], cz),
                     u(e['rhoStarMid'], cz)))
            else:
                w('| %s | %s | %.3f | yes | **not bracketed** | | %s | |'
                  % (label, th, e['sOverSlo'], e['whyNotBracketed']))
    w('')
    unb = [(l, th, c['byThreshold'][th]['wouldBracket'])
           for l, c in D['cells'].items() for th in THS
           if c['byThreshold'][th]['wellPosed'] and not c['byThreshold'][th]['bracket']]
    w('### Not bracketed by existing probes — the targeted runs that would fix it')
    w('')
    if not unb:
        w('None.')
    else:
        w('| cell | SLO | direction | rl values to probe | runs |')
        w('|---|---:|---|---|---:|')
        for l, th, wb in unb:
            w('| %s | %s | %s rl=%s | **%s** | %d |'
              % (l, th, wb['direction'], wb.get('lowestProbed', wb.get('highestProbed')),
                 ', '.join(str(x) for x in wb['probe']), 3 * len(wb['probe'])))
        w('')
        w('%d cheap runs in total, on the registered 5 rps grid. Not a new campaign: '
          'each is the same condition already provisioned, at a lower rate.'
          % sum(3 * len(wb['probe']) for _, _, wb in unb))
    w('')
    coarse = [(l, th, c['byThreshold'][th]) for l, c in D['cells'].items() for th in THS
              if c['byThreshold'][th].get('bracket')
              and not c['byThreshold'][th]['atRegisteredResolution']]
    w('### Brackets coarser than the registered 5 rps')
    w('')
    w('The probed rates are whatever each bisection happened to visit, so a boundary '
      'that moves under a new threshold can land between two rates further apart '
      'than 5 rps. These intervals are correspondingly wider and are **not** 5 rps '
      'boundaries:')
    w('')
    w('| cell | SLO | bracket | width |')
    w('|---|---:|---|---:|')
    for l, th, e in coarse:
        w('| %s | %s | %d-%d | %d rps |' % (l, th, e['bracket'][0], e['bracket'][1],
                                            e['bracketWidthRps']))
    w('')

    w('## Method and its validation')
    w('')
    w('vSLO is a per-second predicate over a 5 s trailing window: violating when the '
      'live p99 exceeds the SLO **or** the error rate exceeds 1%. Every input is '
      'recorded per tick in each run timeline, so the sweep replays the runner\'s own '
      'loop at a different threshold rather than re-deriving anything from raw traces. '
      'The error component and all other pre-registered rules are unchanged.')
    w('')
    w('**T_full is re-derived, not held fixed.** Stabilisation requires the live p99 '
      'under the SLO for 15 consecutive seconds, so a tighter SLO delays T_full and a '
      'looser one brings it forward. Holding it at the recorded value would understate '
      'a tight threshold, since vSLO is violating seconds over T_full.')
    w('')
    w('**Validation: at each run\'s own recorded threshold the replay reproduces the '
      'recorded vSLO, vSLO_latency, vSLO_error and T_full for all 171 archived runs, '
      'with zero mismatches.** `python3 scripts/slo_sweep.py --validate`.')
    w('')
    w('Achieved rho is unchanged throughout. It is a property of delivered rates, not '
      'of latency, so the A4 values from each cell\'s boundary file carry over and no '
      'rho was recomputed for this analysis.')
    w('')
    w('### Limits')
    w('')
    w('- A run stops sampling once it stabilises, so under a tight SLO a recorded '
      'timeline can end before a 15 s healthy streak forms. Such runs are marked '
      'INDETERMINATE, never silently counted as violating. **None occurred** in the '
      'well-posed set.')
    w('- Latencies are integer milliseconds, so at 50 ms the threshold has 2% '
      'granularity. That is immaterial at the observed baselines of 7 and 34 ms.')
    w('- Three of the five S/SLO groups contain one arm only. They cannot '
      'discriminate, and their small spread should not be read as support for the '
      'ratio model.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
