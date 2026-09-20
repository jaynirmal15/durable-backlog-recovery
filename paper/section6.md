# §6 — The corrected boundary

*Draft 8 — W3 readability, 2026-09-20. One edit, and it is a compression rather
than a deletion. The `[ρ_safe, 1]` sentence is 0.92-similar to §IV's, but its
second occurrence does local interpretive work: it sits exactly where a reader
who has just met 1.0002 would otherwise construct the interval §IV forbids. It
is now a subordinate clause of the sentence that reports 1.0002, which keeps the
guard at the point of temptation while removing the standalone restatement.
Approved under the W3 rule: a repetition is removable only when its second
occurrence performs no local interpretive function. Science unchanged.*
*Draft 7 — one-clause resync, 2026-09-20. Draft 6 promised that §IX gives "why a
finer search alone would not" resolve the residual. That reasoning was withdrawn
at §9 draft 3 as unsupported — a narrower search step shrinks the search
component of the resolution while leaving the denominator term in place, so it
may well make the residual resolvable. The clause now says what §IX actually
establishes. Only that clause changed.*
*Draft 6 — one-clause weakening, 2026-09-20. §VI-E promised that "§IX names the
finer-bisection study that would be required to resolve them, and states what it
would cost." No artefact specifies that study's cells, step size or run count,
and §IX will not invent them, so the promise of specificity is withdrawn rather
than met with a fabricated design. §IX-E now says §IX identifies the study, and
§IX-G adds what the existing numbers do support: a finer search alone would not
settle the residual. Only that clause changed.*
*Draft 5. 2026-09-20. One-sentence sync. §VI-D's service-time bullet called the
arm separation "one of the three retracted findings of §VIII". §VIII no longer
carries three retracted findings: the admission limit was never a finding, and
the service-time result's registered statistic was never recomputed, so it is
not retracted either. The bullet now points at what §VIII actually establishes
for this row. Only that sentence changed; the science is unaltered.*
*Draft 4. 2026-09-20. Manuscript tables renumbered into citation order; the
resolution table is Table 2. Mechanical, no science change.*
*Draft 3. 2026-09-19. Outline budget 2,000 words. F5, T3.
Draft 3: the "11% to 17%" excess was median-derived — copied from a hand-written
table in REVIEWER-RESPONSE-W2 without re-deriving under the frozen maximum. It
is 19% to 24%. Verified all four pairs against the widened per-cell thresholds
before stating the conservative-reading conclusion. Three editorial fixes.*
*Draft 2. 2026-09-19. Outline budget 2,000 words. F5, T3.
Draft 2 rebuilds on the MAXIMUM numerator, which frozen §IV names and which
Draft 1 silently replaced with a median — the error was mine, and it had
propagated into F5 before review caught it. Also: the delivery-span interval
whose upper end was a collapsed point is replaced by the probed-rate bracket
§IV permits; per-cell values are at per-cell precision with derived differences
labelled as derived; the collapse factor is dropped in favour of detectability;
the C0/C1 count is corrected from the artefact; concurrency is four levels; and
the SLO count is cell–threshold pairs, not cells. Rounding is no longer offered
as evidence of non-resolvability. Source comments strip in W6.*

---

## 6. THE CORRECTED BOUNDARY

### A. What is reported, and against which denominator

For each cell the search returns a bracket in probed recovery rate: the last
rate classified SAFE and the first classified non-SAFE, five requests per second
apart. Every cell reached that resolution, every first non-SAFE point was UNSAFE
rather than MARGINAL, and no cell terminated early.

The quantity reported per cell is **`ρ_eff,safe`**: the achieved rate at the
*last SAFE point*, divided by that cell's measured capacity, exactly as §IV
defines both. Where a single scalar is required the numerator is the maximum
achieved rate across all of that point's repetitions, which §IV names and
justifies as a defined safe-side quantity; the denominator is the median across
that cell's saturation runs. The two are different aggregators over different
populations, and the paper does not let them drift into one another.

`ρ_eff,safe` is computed at SAFE points only. No utilisation is assigned to a
collapsed upper endpoint — §IV forbids it, and the boundary is therefore
reported as a rate bracket rather than as a utilisation interval.

`C_measured` is a normalisation reference, not a ceiling. Both numerator and
denominator are measurements, so a ratio may read slightly above 1.0 without
implying service beyond a physical bound, and two cells do: they reach 1.0002,
about a fifth of a bisection step above unity and below what the experiment can
resolve — which is why no `[ρ_safe, 1]` interval is constructed and no cell is
called degenerate or pinned at saturation.

### B. The boundary across seven cells

The seven cells span two service times (5 and 25 ms), three configured
capacities (400, 1400, 2000), two admission limits and four concurrency levels
(7, 10, 35 and 50 workers). Table 2 gives each cell at its own resolution.

**The safe drain boundary lies at or near measured service capacity,
indistinguishable from it at the experiment's resolution, in every cell.** No
range spanning the seven is quoted: they do not share a precision, and a range
would assert one they do not have. Per-cell values are in Table 2.

The unrounded analysis puts the difference between the two extreme cells at
0.0071. That is a derived difference, not a per-cell reported utilisation, and
it is smaller than the bisection step of the cell at one end of it — 0.0127 at
E2b, whose configured capacity is 400 rather than 2000.

**Comparing any two cells is limited by the coarser of the two resolutions.**
Across all twenty-one pairs, seventeen fall below that limit. The four that
exceed it do so by 1.19× to 1.24× — a quarter of a step at most — and all four
are comparisons between the two capacity regimes. Of the ten C0-versus-C1 pairs,
six are below the limit and four above it; the four above are the only pairs in
the whole set that exceed their threshold at all.

Two consequences are stated because a reader would otherwise derive them.

**The two cells that define the extreme difference do not exceed the applicable
resolution threshold.** Their difference of 0.0071 sits inside E2b's own step of
0.0127. The figure quoted as the residual is smaller than the resolution of one
of the two cells producing it.

**The highest cells are not distinguishable from unity.** Their excess above 1.0
is about a fifth of a bisection step. The paper therefore says the boundary lies
at or near measured capacity, and does not say it lies strictly below.

### C. What the correction changed, and what it did not

Figure 5 plots each cell's last SAFE point twice: against the configured
parameter, and against the capacity that cell was measured to have. Against the
configured value the seven span **0.0719**. Against measured capacity they span
**0.0071**.

The reportable statement is about detectability, not about a ratio. **Before the
correction the spread across cells was resolvable; after it, the spread falls
below the resolution of the coarsest cell involved.** No collapse factor is
quoted: a ratio between two resolution-limited quantities carries an uncertainty
question of its own, and the detectability statement is what the data support.

Both axes use the maximum, as §IV requires. An earlier build took a maximum on
one axis and a median on the other, which mixed statistics inside a comparison;
that is corrected here and in the figure.

**Figure 5 and the effect-size accounting in §V-F are not the same result.**
Figure 5 re-divides *the same measured boundaries* by a different denominator —
an accounting change, across seven cells. §V-F compares an uncorrected harness
against a *physically corrected* one, in two cells, on the drain-window
estimator. Taking Figure 5's two C0 cells alone makes the difference concrete:
the derived gap between them is 0.0696 against the configured parameter and
0.0019 against measured capacity, while correcting the harness itself leaves
0.0043 under the matched estimator. All four are derived differences from the
unrounded analysis, not per-cell reported values.

Re-normalising therefore closes the inter-arm gap further than correcting the
instrument does. That is not the comfortable reading and it is not evidence that
the correction was unnecessary: it says the apparent arm separation was largely
an artefact of the denominator, and that what survives the physical correction
is a residual the accounting alone does not reach. Both are reported with their
estimators and populations named, and neither is offered as a version of the
other.

### D. What does not move the boundary

**Configured capacity.** Six of the ten comparisons spanning the C0 and C1
regimes fall below their resolution limit; the remaining four exceed it by 19%
to 24% of one step.

**Admission limit.** E2 c10@Q2500 and E1 c10/C0 share a service time and a
concurrency and differ only in queue cap. Their probed-rate brackets are
identical: [825, 830] rps in both.

**Concurrency.** Across the four concurrency levels probed, no
concurrency-associated difference is resolved after normalisation by measured
capacity.

**Service time.** The 5 ms and 25 ms arms separate sharply against the
configured parameter and fall within resolution of one another against measured
capacity. §VIII sets out why the calibrated evidence undermines the reading that
service time governs the boundary, and why the registered statistic that
affirmed that reading was nonetheless never re-adjudicated.

**The latency objective, over the range where the question is well posed.** The
sweep evaluated thresholds of 50, 100, 250 and 500 ms. A rule fixed before the
sweep ran admits a cell–threshold pair only where the healthy baseline live p99
is at most half the threshold; below that margin the objective is a question
about idle latency rather than about recovery headroom. **Four pairs are
excluded, all of them the 25 ms cells at 50 ms**, whose 34 ms healthy baseline
is 68% of that threshold. The 5 ms cells, with a 7 ms baseline, are well posed
throughout.

The evidence therefore spans a tenfold change in the short arm and a fivefold
one, 100 to 500 ms, in the long arm. Over those ranges `ρ*` moves by 0.006 in
the short arm and 0.004 in the long one, across eleven well-posed cell–threshold
pairs in each arm — the pairs that are both well posed and bracketed, of twelve
well-posed in each.

The largest movement any cell shows under the full range is 10 rps, at
E1 c10/C0, which is 0.0055 of that cell's measured capacity. The difference
between the extreme cells is 0.0071. **The disagreement between seven
configurations and the movement produced by changing an arbitrary methodological
parameter are comparable in magnitude** — neither is resolved by this
experiment, and no ratio between them is quoted.

What the objective has little leverage over is visible in the data: the
transition is a cliff rather than a slope. At E1 c10/C1 the three repetitions at
the last SAFE point give vSLO of 0.000, 0.000 and 0.000, and one 5 rps step
later they give 0.630, 0.494 and 0.734. A transition that completes inside a
single search step is one a threshold change is observed not to reposition, over
the range tested.

### E. The residual, declared and not claimed

The 0.0071 difference is reported because suppressing it would be worse than
reporting it, not because it is a finding. Two facts prevent it from being one.

It is smaller than the bisection step of the cell at one end of it. And the pair
that produces it does not exceed the applicable resolution threshold, nor does
any pair except the four that clear theirs by 19% to 24%.

Reported per-cell precision reflects the search step alone. §IV records that the
denominator carries its own variability, that the two are reported separately
rather than combined, and that read conservatively they add linearly to between
1.09 and 1.80 times the quoted figure. Including the separately measured
denominator variability widens the applicable resolution threshold; none of the
four pairwise differences remains resolved under that conservative reading.

What the seven cells support is a statement about location rather than about
ordering. The safe drain boundary lies at or near measured service capacity in
every configuration probed, and the differences between those configurations are
not resolved by this experiment. §IX identifies the finer-bisection study that
would be required to probe these differences, and notes that the denominator
variability would remain a separate resolution term.
