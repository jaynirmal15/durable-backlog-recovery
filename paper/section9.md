# §9 — Threats to validity

*Draft 7 — CUT PASS, increment 6, 2026-09-20. §IX-C compressed from ~480 to
~230 words and §IX-B's resolution paragraph shortened where it restated §IV-D.
Kept: the standalone tool's missing provenance and what it costs the prospective
test, the bounded window and A9's record of the gap, both mid-campaign
corrections with their timing, the withdrawn 0.0004 claim and why it is
arithmetic rather than evidential, and the generated-table control. Moved to
S1-I: the two documentation failures in full. No number or finding changes.*
*Draft 6 — KEYED FIGURE AND TABLE REFERENCES, 2026-09-20. Every literal "Fig. N", "Figure N" and "Table N" in the body is replaced by a key (`[@fig:…]`, `[@tab:…]`) that the build renders as "Fig. N" / "Table N" from order of first appearance — the citation design, applied to floats, so numbering cannot go stale when tables are added. No other wording changed.*
*Draft 5 — W3 readability, 2026-09-20. §IX-C re-listed the four provenance
fields §IV-G already teaches. The contrast is what this subsection needs — the
standalone tool has none of them — and the contrast survives a cross-reference;
the schema does not need teaching twice. The four fields the standalone tool DOES
record stay, because they are the evidence for the absence. Approved under the
W3 rule: the second occurrence performed no local interpretive function. Science
unchanged.*
*Draft 4 — SCIENCE FROZEN. 2026-09-20. Table 4. Written against outline v8.7.
Draft 4 is three sentence-level precision edits and nothing else.
(i) "which is impossible" is struck from the A4 count. §VI states that
`C_measured` is a normalisation reference and not a physical ceiling, and that a
measured ratio may legitimately read slightly above unity — so calling a rate
above the plateau impossible silently converts the reference back into true
capacity, the terminology error this paper exists to avoid. The evidence never
needed it: the count is a pattern incompatible with treating the estimator as
physically interpretable at collapsed points. **NOTE: the same phrase sits in
the generated Table 4 and its generator (`scripts/make_table4.py:45`), which the
manuscript prints; §IX and the table must not disagree. Executor task raised.**
(ii) §IX-G no longer promises an experiment that "would answer" each question —
for the residual there is no specified design and no claim that a finer
bisection suffices. It identifies the follow-up measurement required for each.
(iii) "an analysis chain will validate the assumptions it shares with its
instrument" becomes **can**. The evidence supports the modal, not the universal,
and the outline's own wording already said "can".
Draft 3 applied three edits, then froze. (1) **The finer-bisection reasoning in Draft 2 was
wrong and is withdrawn.** I argued that a finer search alone could not settle
the residual because the effect, at 19-24% of a step, is comparable to the
denominator term of 0.09-0.80 of a step. That does not follow: a narrower step
shrinks the search component while leaving the denominator term where it is, so
the conservative threshold falls and a difference of about 1.2 steps could
become resolvable. "The denominator term remains" does not imply "more
saturation measurements are required". §IX-G now says only what holds — the
denominator term persists as a separate term any such study must carry — and
§6 draft 7 is synced to match. (2) The two mid-campaign corrections are no
longer forced into parallel chronology: the first was corrected *during* the
first contradicting probe, before it completed, so some of that probe's evidence
already existed; the second was corrected *before* the deciding probe began.
(3) The mixed-unit comparison is gone — a 215 rps bracket against a 0.0043
separation invited a units objection it did not need. The point is simply that
the bracket contained both candidates and so could not distinguish them.
Draft 2 applied the five items of the first review, kept six subsections and
took the option (ii) trim.*

*LENGTH — the arithmetic did not land where option (ii) costed it, and the
reason is worth stating. Option (ii) was costed against Draft 1 at 1,607 and
projected ~1,450. It removed 160 words as intended (§IX-D's recitation, §IX-E's
leave-one-out detail). But blockers 1 and 2 ADDED content: the two mid-campaign
readings §V-G actually promises are ~110 words longer than the A9/A10 paragraph
they replace, because each carries its own evidence and its own timing, and the
finer-bisection point added ~50. Two further compression passes returned 44 and
32 words. **Draft 2 is 1,655.** So the choice is now between accepting ~1,650
and cutting something owed. I have not cut anything owed. §IX-B (473) and §IX-C
(~490) are the two large subsections and every item in both is owed by a
forward reference from a frozen section.*

*BLOCKER 1 — FIXED, and the reviewer's reading of §V-G is correct against the
record. §V-G promises two readings made and corrected mid-campaign plus one
withdrawn claim; Draft 1 substituted A9 and A10, which are later record
corrections and are already carried by §IV and Table 1. Verified in
`results/E2E-PLAN.md`: addendum 2 claimed the bisection could not terminate;
addendum 3 corrected it on the first contradicting result, before that point
completed, and records that the queue peak had gone 7 → 18 → 111 and live p99
8 → 14 → 58 ms across the three preceding probes. Addendum 3 then declared the
saturated figure the winner and the 90%-load figure excluded; addendum 4
corrected that **before the deciding probe ran**, fixing the reading for each
outcome in advance, because the 215 rps bracket [0.9883, 0.9941] contained both
candidates. The withdrawn 0.0004 claim is a sentence of that same addendum 3.
§IX-C now carries all three.*

*BLOCKER 2 — §VI's promise weakened rather than §IX inventing a design. No
artefact anywhere specifies cells, step size or run cost for the finer-bisection
study, so I did not invent one. §6 Draft 6 drops "and states what it would cost"
from its forward reference. §IX-G instead says something the existing numbers do
support and which I think is the more useful statement: a finer search ALONE
would not settle the residual, because at 19 to 24% of a step the effect is
comparable to the denominator term of 0.09 to 0.80 of a step, which a narrower
step does not reduce. **This is new reasoning and the reviewer should check it.**
It is derived from figures already in §VI and §IX-B, not from a new measurement.*

*ALSO APPLIED: §IX-D's three kill mechanisms corrected to replication / first
additional test cell / orthogonal plateau cross-check; the blind-spot sentence
scoped to the A4 row alone; §IX-G's close widened to include additional test
cells; the clock paragraph rewritten to separate timestamp representation from
effective resolution and to drop the over-categorical claim about estimating it
from the same instrument; and the blocked harness-defect comment deleted with
its three unsourced examples, leaving the two that are sourced. Source comments
strip in W6.*

---

## 9. THREATS TO VALIDITY

### A. Construct

One synthetic downstream, on one instance type, with no real dependency, no
persistent state and no I/O. The per-request bias measured here is a property of
this implementation, this host and this Go runtime, and the paper does not offer
0.463 ms as a constant anyone else should expect to find. What generalises is
not the number but the relation: a configured capacity figure was wrong by more
than the operating margin the experiment set out to characterise, in an
instrument built for that experiment and inspected by its author.

### B. Measurement

**The probe's own distribution.** Every quoted `δ` is an untrimmed arithmetic
mean over a right-skewed per-cycle distribution — p99 is about twice p50 in
every condition measured, the maximum roughly four times it. §V-B explains why
the mean is the right statistic for a capacity model, which concerns total
worker time per request rather than a typical one; the consequence belongs here.
Every `δ` in this paper sits above the typical cycle and none describes a
representative request.

**The instrument's resolution is not established.** The probe uses the Go
runtime's monotonic clock, which represents timestamps to the nanosecond;
representation granularity is not effective resolution, and the effective
resolution on the experiment host was never measured and is not recoverable from
the records. A sub-millisecond measurement is therefore reported here without a
bound on its own quantisation error. A clock can be characterised independently,
and this one was not; no retrospective bound is supplied.

**Percentiles and means cover different populations in one condition.** Sums
accumulate over every request; percentiles come from a fixed 200,000-sample
buffer that fills in order and then stops accepting. It never bound for the four
direct figures, at 115,000 to 137,000 cycles per window. In situ it did — 232,349
cycles against 200,000 samples — so each in-situ percentile describes the opening
of its run rather than the whole of it. The in-situ means are unaffected.

**Repeatability was measured at one condition and not at the two compared.** The
90%-load and saturation figures are single 60-second windows; the in-situ figure
aggregates 18 and 15 runs whose run means span 0.0053 and 0.0040 ms, and the
load effect of 0.020 to 0.022 ms is four to five times that span. §V calls the
comparison indicative rather than decisive, and the reason belongs here: those
runs are 111 to 120 seconds under bursty arrivals, not 60-second windows under
the calibration driver, so they cannot establish that the effect is not window
scatter. The measurement that would settle it was not made.

**Resolution.** [@tab:resolution]'s per-cell figures reflect the search step
alone; the denominator's range adds 0.09 to 0.80 of a step, and read
conservatively the two add linearly, giving 1.09 to 1.80 times the quoted figure
(§IV-D). At each cell's lowest observed plateau two cells place the safe-side
estimate marginally above 1.0, which is why §VI says the boundary lies at or near
measured capacity rather than strictly below it.

**One superseded figure.** An earlier committed analysis reported 96.3% of the
inter-arm effect removed, from before-and-after values sharing neither
estimator, aggregator, observation interval nor statistic. The matched 94 to 95%
accounting in §V supersedes it.

### C. Provenance, and corrections to the record

§IV-G sets out the provenance the runner stamps on every boundary run. The
standalone tool that measures saturation plateaus stamps none of it — only a
label, an offered rate, a connection count and the measurement — and both
corrected plateau measurements and all twenty replication windows registered
under A8 come from it. **So the committed record cannot establish that the
prediction was registered before the measurements that tested it.** What it
bounds is a window, 16:31:55 to 18:50:07 UTC, containing the 17:31:47
registration; the rest of the support is the registration's forward-looking
language, its statement that no boundary run had yet started, and an uncommitted
campaign log. Addendum A9 records the gap without closing it, no claim here is
written as though it were closed, and the fix for any future campaign is to
stamp provenance in that tool.

Two readings were made mid-campaign and corrected in the registration: the first
during the first probe that contradicted it, before that probe completed; the
second before the deciding probe began, with the reading for each outcome fixed
in advance. **The withdrawn claim belongs to the second** — that a break sitting
0.0004 above a registered prediction confirmed it, when the bracket in hand
contained both candidate predictions and so could not distinguish between them,
which is what makes that proximity arithmetic rather than evidential. Two
documentation failures are recorded in Supplement S1 with what caught them. The
lesson in both is the control rather than the error: for a claim about several
items at once the authority is a generated table whose cells are checked against
their sources, not the prose in between.

### D. Claims overturned by independent checks

Three claims reached the written record and were later refuted by further
measurement. [@tab:false-findings] gives each with what it predicted, what killed it and when.
They are a different set from §VIII's candidate explanations, with a different
cause: none is a calibration artefact.

One point the table cannot carry in a cell. The third claim — that the
achieved-utilisation estimator is valid at every probed point — was refuted by a
count: 18 of 20 unsafe points reported rates above their own cell's
independently measured saturation plateau, a pattern incompatible with treating
that estimator as physically interpretable at collapsed points. The count is the
evidence, and it is resolution-independent. The per-cell inversion magnitudes are not cited, because
they sit below the resolution that would make them mean anything. That row
carries the narrower lesson of the three: an estimator cannot expose a blind
spot built into its own accounting.

What the three share is only that none was killed by the analysis that produced
it, and they were killed by three different things — one by a replication
designed to test it, one by the first additional cell that tested its claimed
generality, one by an orthogonal cross-check against a separately measured
quantity.

### E. Internal

`δ` was estimated in sample, with no cell held out. §V reports the leave-one-out
construction that tests what that costs, and its result in full.

Defects in the harness were found and fixed during the campaign, and are
reported as evidence that the checking regime operated rather than as
incidental. A spin-wait admission profile was found to amplify a transient
rejection into a sustained collapse, and was replaced. The overhead record's own
descriptive field contradicted the arithmetic of the record it was written into,
in every record it wrote, until it was corrected at the source and in all 43
affected records — after which every consuming artefact regenerated
byte-identically.

### F. External

One implementation, one instance type, one broker, one consumer cohort. No real
dependency, no persistent state, and no operational consequence measured: the
objective is a latency-and-error rule evaluated per second, not a user-visible
outcome. The boundary result is a statement about this system, and the
methodological result is what the paper offers beyond it.

### G. What remains open, and what would settle it

Two questions are left declared rather than answered, and this section
identifies the follow-up measurement required for each.

The residual disagreement between capacity regimes, which §VI declares and does
not claim, would need a finer bisection in the two regimes that produce it. A
finer search would reduce the bisection component of the resolution, while the
denominator variability reported above would remain as a separate term; any such
study would therefore have to carry that term explicitly when adjudicating the
residual. Whether it would also need more saturation measurements per cell is
not established by the present record. The ordering question
of §VII needs a different study again: a 5 rps sweep over the top 50 rps of each
corrected safe range, roughly 60 runs at n = 3, fine enough to resolve a lead of
the size the uncorrected corpus reported. Neither substitutes for the other.

The lesson of this section is not §VIII's. §VIII concludes that a campaign under
public pre-registration, with an explicit falsification protocol, could not
detect a sub-millisecond bookkeeping error from the effects it produced. This
section concludes something narrower and more actionable: independent
replication, additional test cells, orthogonal measurement and cross-estimator
checks were what overturned the claims in [@tab:false-findings], and they were necessary
precisely because an analysis chain can validate the assumptions it shares with
its instrument.
