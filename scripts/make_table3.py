#!/usr/bin/env python3
"""Candidate explanations of the boundary: the explanation, its registered
falsification, the pre-calibration outcome, and what calibration changed.

Article float tab:candidates, written against outline v8.7. The printed
number is assigned by the build from order of first appearance and is not
recorded here -- the key is the identity. The three rows have three
DIFFERENT standings and the asymmetry is the point: one was rejected by its own
criterion before calibration, one was affirmed and then no longer resolved once
the boundary was expressed against measured capacity, and one was affirmed with
its registered statistic never recomputed. Column 1 is "Candidate explanation",
never "Apparent finding" -- the admission limit was explicitly not a finding.
<!-- withdrawn-quote-ok: prohibition in the docstring -->

Distinct from figures/T4-false-findings.md, whose key is tab:false-findings.

Every quotation is verified against the committed file at the commit named in
the row before anything is printed, so no cell is written from memory. Numbers
come from the artefacts named beside them. No table number is assigned.

Usage: python3 scripts/make_table3.py > figures/T3-candidate-explanations.md
"""
import json
import subprocess
import sys

E2E = json.load(open('results/E2E-analysis.json'))
W8 = json.load(open('results/W8-effect-size-accounting.json'))

# (commit, path, fragment). commit=None means check the working copy: the
# reports are regenerated artefacts and their wording tracks their generators,
# whereas the plans are registration-grade and are pinned to the commit that
# registered them.
# THE OPERAND IS THE UNROUNDED MIDPOINT, NOT THE ROUNDED ONE. E2B-REPORT's
# summary table prints the interval as [0.97, 0.99] and its midpoint as 0.98;
# the generated boundary artefact it was written from says [0.975, 0.9875],
# midpoint 0.98125. h = +0.980 follows from the unrounded midpoint and NOT
# from 0.98, which yields 0.962. Printing a rounded operand beside an
# unrounded result made the article state a false identity. Both operands are
# read from the artefact here so the identity cannot drift again.
_E2B = json.load(open('results/e2b/boundaries/c50-C0.json'))['boundary']
_IV = _E2B['rhoStarInterval']
RHO_STAR_E2B = (_IV[0] + _IV[1]) / 2.0
RHO10, D_E1 = 0.9137, 0.0689                 # E2B-PLAN.md at a741d68
H_E2B = (RHO_STAR_E2B - RHO10) / D_E1
assert _IV == [0.975, 0.9875], _IV
assert abs(RHO_STAR_E2B - 0.98125) < 1e-9, RHO_STAR_E2B
assert round(H_E2B, 3) == 0.980, H_E2B      # the registered verdict, unchanged
assert round((0.98 - RHO10) / D_E1, 3) == 0.962   # what the rounded operand gives

QUOTES = {
    'D':        ('c823393', 'results/E2-PLAN.md',   'D   = m50 - m10 = 0.0689'),
    'conc_crit':('c823393', 'results/E2-PLAN.md',   '**CONCURRENCY-DRIVEN** | both `f ≤ 0.25`'),
    'cap_crit': ('c823393', 'results/E2-PLAN.md',   '**CAP-DRIVEN** | both `f ≥ 0.75`'),
    'f_verdict':(None,      'results/E2-REPORT.md', 'Registered verdict: **OFF-SCALE** (f = +0.000 and -0.006).'),
    'f_nomove': (None,      'results/E2-REPORT.md', 'neither cell moved materially in either direction'),
    'h_crit':   ('a741d68', 'results/E2B-PLAN.md',  '**h >= 0.75** | **S GOVERNS.**'),
    'h_value':  (None,      'results/E2B-REPORT.md','h = (rho* - rho10) / D = (0.98 - 0.9137) / 0.0689 = +0.980'),
    'a6_conc':  ('c3aee75', 'PRE-REGISTRATION.md',  '| concurrency gap | 0.0689 | 0.0688–0.0698 | **survives** |'),
    'a6_cap':   ('c3aee75', 'PRE-REGISTRATION.md',  '| E2 cap swap | identical intervals, f = 0.001 | identical rate intervals, f = 0.000 | **survives, and is stronger** — rate is estimator-independent |'),
    'a6_h':     ('c3aee75', 'PRE-REGISTRATION.md',  '| E2b, S governs | h = 0.980 | h = 0.895–0.945 | **survives** |'),
    # The pre-E2 status of the cap hypothesis, in the tree as it stood when E2
    # was registered. Held open, never asserted as a result.
    'cap_open': ('c823393', 'STATUS.md',
                 'That is a competing\nexplanation for the concurrency effect and is not yet ruled out.'),
}


def verify():
    """Every fragment must be present at its commit, or nothing is printed."""
    bad = []
    for key, (commit, path, frag) in QUOTES.items():
        if commit is None:
            body = open(path, encoding='utf-8').read()
            where = path
        else:
            try:
                body = subprocess.run(['git', 'show', '%s:%s' % (commit, path)],
                                      capture_output=True, text=True,
                                      check=True).stdout
            except subprocess.CalledProcessError:
                bad.append('%s: cannot read %s at %s' % (key, path, commit))
                continue
            where = '%s at %s' % (path, commit)
        if frag not in body:
            bad.append('%s: fragment absent from %s' % (key, where))
    if bad:
        for b in bad:
            print('QUOTE CHECK FAILED — %s' % b, file=sys.stderr)
        raise SystemExit(1)


def main():
    verify()
    c10, c50 = E2E['cells']['c10'], E2E['cells']['c50']
    m, a4 = W8['matched'], W8['matchedA4']

    print('# Candidate explanations of the boundary, and what calibration '
          'changed about each')
    print()
    print('Three candidate explanations of the boundary, each registered with '
          'its falsification criterion before the data that tested it were '
          'collected. One was rejected by its own criterion before calibration; '
          'of the two that survived, one was almost entirely removed when the '
          'boundary was expressed against measured service capacity, and the '
          'other\'s registered statistic was never recomputed. Generated by '
          '`scripts/make_table3.py`. Every quotation is verified '
          'before the table is written: quotations from the plans and from A6 '
          'against the committed file at the commit named, quotations from the '
          'reports against the working copy, because the reports are regenerated '
          'artefacts whose wording tracks their generators. Numbers come from the '
          'artefacts named in the sources below. This is a different set from '
          '`figures/T4-false-findings.md`, whose key is `tab:false-findings`.')
    print()
    # The build sets ONLY the pipe table that follows this marker. The
    # "Sources, cell by cell" table below is artefact documentation and carries
    # no marker, so it cannot reach the article.
    print('<!-- table:tab:candidates -->')
    # THREE COLUMNS, per the Draft 4 ruling. The old pre- and post-calibration
    # columns are merged into one "Standing after calibration" cell whose first
    # sentence is the standing itself, because the three standings are
    # ASYMMETRIC and that asymmetry is the table's point: one was rejected
    # before calibration, one was dissolved by it, and one was affirmed before
    # it and never re-adjudicated. Every number, commit and registered
    # criterion from the four-column version is retained.
    print('| Candidate explanation | Registered test | '
          'Standing after calibration |')
    print('|---|---|---|')

    print('| **The boundary depended on concurrency.** The two E1 arms separated '
          'by `D = m50 - m10 = 0.0689` in safe utilisation, 0.9137 at concurrency '
          '10 against 0.9826 at concurrency 50. '
          '| Swap the admission limits across the arms and score the fraction of '
          '`D` that moves with the cap: **CONCURRENCY-DRIVEN** requires both '
          '`f ≤ 0.25` (E2 plan, `c823393`). '
          '| **Confirmed before calibration, and no longer resolved after it.** '
          '`f = +0.000` and `-0.006`: neither cell moved toward the other arm, so '
          'the gap did not follow the cap (E2 report). Measured after the '
          'correction on those same two arms, under one recipe applied to both '
          'corpora, the inter-arm gap falls from **%.4f to %.4f** (%.0f%% removed) '
          'on the drain-window estimator and from %.4f to %.4f (%.0f%% removed) on '
          'the delivery-span one — %.1f rps to %.1f rps in throughput terms. '
          '**94–95%% of the separation is removed.** |'
          % (m['gapRhoUncorrected'], m['gapRhoCorrected'], m['fractionRemovedRho'],
             a4['gapRhoUncorrected'], a4['gapRhoCorrected'], a4['fractionRemovedRho'],
             m['gapRpsUncorrected'], m['gapRpsCorrected']))

    print('| **The boundary depended on the admission limit.** The E1 arms had '
          'been run at different queue caps — 500 at concurrency 10, 2500 at '
          'concurrency 50 — so the cap was a live explanation of `D`. '
          '| The same swap, scored the other way: **CAP-DRIVEN** requires both '
          '`f ≥ 0.75` (E2 plan, `c823393`). '
          '| **Rejected before calibration, by its own registered criterion.** '
          'Registered verdict OFF-SCALE, `f = +0.000` and `-0.006`; `CAP-DRIVEN` '
          'was unreachable once the first cell returned +0.000, and neither cell '
          'moved materially in either direction (E2 report). **No '
          'post-calibration evidence, and none possible:** the corrected corpus '
          'ran only the original diagonal — c10 at cap 500, c50 at cap 2500 — so '
          'no post-calibration value of `f` exists. The correction has nothing to '
          'dissolve here; the campaign had eliminated the cap before the bias was '
          'known. |')

    print('| **Service time governed the boundary.** With concurrency and service '
          'time separated at `C = 400`, ρ* landed c50-like rather than c10-like. '
          '| Score ρ* against the two E1 midpoints: `h = (ρ*_E2b − ρ10) / D`, '
          'where **`h ≥ 0.75` reads S GOVERNS** and `h ≤ 0.25` reads concurrency '
          'governs (E2b plan, `a741d68`, with a dead band registered in advance). '
          '| **Affirmed before calibration, and not re-adjudicated after it.** '
          '`h = (%.5f − 0.9137) / 0.0689 = %+.3f` (E2b report; ρ* is the '
          'unrounded midpoint of the boundary interval [0.975, 0.9875], which '
          'that report\'s summary table rounds to 0.98), at the S-governs '
          % (RHO_STAR_E2B, H_E2B) +
          'end of the scale. `h` is defined relative to the E1 arm separation, '
          'which was measured against the configured capacity parameter. Two '
          'later results undermine the S-governs reading without recomputing '
          '`h`: physically correcting the harness removes most of the separation '
          'between those same two arms (W8 matched accounting), and expressing '
          'seven cells against measured capacity resolves no service-time '
          'difference at all. **The exact registered `h` was never recomputed: no '
          '`C = 400` cell exists on the corrected harness.** |')

    print()
    print('## Sources, cell by cell')
    print()
    print('| row | cell | artefact |')
    print('|---|---|---|')
    rows = [
        ('1', 'candidate explanation', '`results/E2-PLAN.md` at `c823393`, the attribution statistic fixed before the runs; midpoints from E1'),
        ('1', 'registered challenge', '`results/E2-PLAN.md` at `c823393`'),
        ('1', 'pre-calibration outcome', '`results/E2-REPORT.md`'),
        ('1', 'post-calibration', '`results/W8-effect-size-accounting.json`, `matched` and `matchedA4`, from `results/E2E-analysis.json`'),
        ('2', 'candidate explanation', '`results/E2-PLAN.md` at `c823393`, the 2x2 showing E1\'s two caps'),
        ('2', 'registered challenge', '`results/E2-PLAN.md` at `c823393`'),
        ('2', 'pre-calibration outcome', '`results/E2-REPORT.md`'),
        ('2', 'post-calibration', '**none — see the gaps below**'),
        ('3', 'candidate explanation', '`results/E2B-PLAN.md` at `a741d68`'),
        ('3', 'registered challenge', '`results/E2B-PLAN.md` at `a741d68`'),
        ('3', 'pre-calibration outcome', '`results/E2B-REPORT.md`'),
        ('3', 'post-calibration', '**none — see the gaps below**'),
    ]
    for r in rows:
        print('| %s | %s | %s |' % r)

    print()
    print('## A6 is a different correction')
    print()
    print('A6 is the **estimator** correction and is not the calibration '
          'correction; the two are days apart and easy to conflate. A6 changed '
          'no candidate explanation\'s standing, as its own conclusions table '
          'records. A6\'s registered rows, at `c3aee75`:')
    print()
    for k in ('a6_conc', 'a6_cap', 'a6_h'):
        print('> %s' % QUOTES[k][2])
    print()
    print('What A6 established is that the A4 estimator **over-reads at '
          'collapsed points**, and the response was to stop reporting '
          'utilisation at those points rather than to re-estimate them: A6 '
          'recomputed utilisation at SAFE points only. The calibration '
          'correction is a different operation — it reduced the configured sleep '
          'by the measured per-request overhead and re-ran the two boundaries — '
          'and it is what changed the interpretation of the two affirmed rows.')

    print()
    print('## Was the admission limit ever a finding?')
    print()
    print('**No.** Searching the plans, reports, notes and commit messages in the '
          'tree as it stood when E2 was registered (`c823393`, 2026-09-12 '
          '10:46 -0400, three hours before the first E2 run at 15:01:44Z) finds no '
          'written result asserting that the admission limit governs the boundary. '
          'The only assertions are the arithmetic identity that a full graceful '
          'queue equals the SLO at `S = 5 ms`, and the statement that this is a '
          'candidate explanation. `STATUS.md` at that commit:')
    print()
    print('> %s' % ' '.join(QUOTES['cap_open'][2].split()))
    print()
    print('So row 2 is not a retracted finding. It is a registered falsification '
          'that succeeded, and it is the contrast case: the one hypothesis of the '
          'three that the campaign eliminated by itself, before the bias was '
          'known.')
    print()
    print('## Gaps, named rather than filled')
    print()
    print('**Neither `f` nor `h` has a post-calibration value.** The corrected '
          'corpus is two cells: c10 at `S = 5 ms`, concurrency 10, queue cap 500, '
          'and c50 at `S = 25 ms`, concurrency 50, queue cap 2500, both at '
          '`C = 2000`. Across its 33 boundary runs there is no cell with swapped '
          'caps and none at `C = 400`. Row 1 is the only row whose registered '
          'quantity was re-measured after the correction; rows 2 and 3 say so '
          'rather than reasoning to a value.')
    print()
    print('**The three rows do not have the same standing, and the statuses '
          'differ accordingly.** Row 1 was affirmed and then dissolved by '
          'measurement. Row 3 was affirmed, and its interpretation is superseded '
          'by row 1 without its own statistic being recomputed. Row 2 was refuted '
          'by its own registered criterion before the bias was known, and was '
          'never asserted as a finding in the first place.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
