# §1 — Introduction

*Draft 21 — FINAL REVISION, 2026-09-23. C2 leads with the unresolved residual: calibration reduced the concurrency-associated separation to a residual below the corrected search resolution, and 94–95% is named as a point-estimate reduction rather than a resolved magnitude. C2's prospectivity claim is demoted to data independence — the predictions appear in the registration, but the plateau records carry no file-level timestamp, and §IX-C holds that gap. §I's three-candidate sentence follows.*

*Draft 20 — TWO-REVIEW REVISION, 2026-09-23. B1: the claim-register headline and C1 retire "within 1%" as a seven-cell formulation, which §VI-B's own policy sentence forbids. B3: the contributions heading now reads "main results and methodological contributions", C1 is renamed "Boundary characterization", and one sentence records that the campaign preregistered the search procedure, not a boundary location. B4: the controller prescription is scoped to this harness. No number changes.*

*Draft 19 — CUT PASS, increment 3, 2026-09-20. §I compressed from ~1,595 to
1,261 words (measured; the ~1,150 aimed at was not reached). Verbatim and unchanged: the claim-register headline and
scale-mismatch statements, the paragraph stating the 0.463 ms bias and the 9.26% /
1.85% overstatement, C1 and C4, and C2's prediction and replication numbers.
Compressed: the opening, the three-candidate paragraph (which §VIII tells in
full), the control-consequence and design-position paragraphs (merged), the
roadmap, and C3's per-cell detail (given in §VII). No number or finding changes.*
*Draft 19.1 — APPROVED by review with four fixes, then frozen: "overstated its own capacity by a per-request timing bias" → "because of" (a time is not a capacity overstatement); "the overhead" qualified as "this per-request timing bias" and "the per-request bias" (δ varies with load, so it is never an unqualified "the overhead"); the withdrawn controller-comparison claim replaced by "the present experiments do not adjudicate between the two"; and C2's "the elimination is a registered prediction" → "the correction was tested by a registered prediction rather than fitted to the corrected runs", since the 94–95% removal comes from matched accounting, not from the prediction.*
*Draft 18 — CITATION MARKERS ONLY, 2026-09-20. Keyed markers `[@key]` inserted at the first mention of Little's law. **No prose changed**; each marker attaches to a sentence the frozen draft already carries. Keys render to IEEE numbers by order of first appearance in a separate mechanical pass after review.*
*Draft 17 — one-clause sync, 2026-09-20. C4 said "three findings retracted
before publication rather than after" without saying which three. The draft note
knew they were §IX's independent-check set and not the three candidate
explanations the reader had met two paragraphs earlier; the reader did not. C4
now names them. Mechanical.*
*Draft 16 — one-sentence sync, 2026-09-20. The roadmap still said "Section VIII
returns to the three retracted findings and what each of them cost", which is
the framing Draft 15 removed from the body of this same section: only one of the
three is a retracted finding of that kind, the admission limit was never a
finding at all, and §VIII no longer tells three matching stories. Only that
sentence changed; nothing else in Draft 15 is touched. C4's "three findings
retracted before publication" is NOT this trio — it is the independent-check set
(bimodality, the occupancy rule, A4's universal validity) that §IX carries, all
three of which were genuinely retracted — and it stands.*
*Draft 15 — REOPENED, then re-frozen. 2026-09-20.
Draft 15 is a SUBSTANTIVE correction, not a sync. Source-asserted table
generation showed that of the three "successive findings", only concurrency has
the full chain — registered challenge, survived, directly dissolved by
calibration. The admission-limit hypothesis was REFUTED by its own registered
test before calibration; it never survived. Service time was affirmed, but its
registered statistic was never recomputed after calibration and the corrected
corpus has no C = 400 cell to recompute it in. C2 is narrowed accordingly and
the scale-mismatch claim goes singular. The old three-case rhetoric is not
preserved for sounding stronger.*
*Draft 14 —
Draft 14: C3's corrected-harness summary collapsed warning and ordering into one
claim, and §VII draft 5 found that four metrics DO warn with room in the
short-service cell. C3 now states the two-cell result and drops the old
precursor-room hypothesis, which the same cell contradicts. Mechanical sync.*
*Draft 13 —
Draft 13: draft 12's δ-provenance edit inverted a meaning — it made the false
findings "artefacts of that same correction" when they were artefacts of the
BIAS. Bias and correction are now named as distinct things throughout.*
*Draft 12 —
Draft 12: four mechanical syncs after §6 froze — concurrency is four levels not
three; C1's tenfold clause scoped to the well-posed sweep; C1's replication
counts corrected to match §IV draft 22 (five last-SAFE endpoints at n = 12 or
15); C2 no longer ends on the single-window pair, which §V treats as historical.
The correction's δ carries its provenance at first use.*
*Draft 11 —
Draft 11: the SLO sentence is scoped to the well-posed sweep. A rule fixed before
the sweep excludes four cell-threshold pairs, all the 25 ms cells at 50 ms, so
the evidence spans tenfold in the short arm and fivefold in the long one. §VI
carries the detail. Mechanical.*
*Draft 10 —
Draft 10: "independently rate-controlled" -> "independently configured open-loop
rates", so the harness description does not collide with the controller discussion
later in this section. Mechanical; §3 draft 10 carries the full statement.*
*Draft 9 — Sept 14 2026. Target 1,200 words; this draft is 1,250. No figure.
Draft 9: "reverse" -> "invalidate" in the scale-mismatch claim — after A7 the
signal conclusion became unsupported rather than reversed. Draft 8: the numeric range is withdrawn from the headline — its lower endpoint
comes from the one cell restricted to two decimals, so the range mixed
precisions. Draft 7: C3 rewritten after addendum A7 — the queue-depth lead does not
replicate and is now exploratory; the timeout result does replicate. Draft 5: second order-of-magnitude sentence scoped to the 5 ms arm; section
frozen. Draft 4: first order-of-magnitude claim scoped. Draft 3: "statistically" dropped; admin endpoint described as the
configured parameter, not true capacity; pre-registration chronology made
mechanical; "constant" bias -> service-time-independent.
Claim-register wording used verbatim where marked. Source comments strip in W6.*

---

## I. INTRODUCTION

A durable message broker does not lose work when its consumer stops; it
accumulates it. When the consumer returns, the backlog and the live traffic
compete for the same downstream capacity. Drained at full speed, the backlog
displaces live traffic, and users who were unaffected by the original outage
experience the recovery as a second one. The operator's question is therefore a
rate: how fast may the backlog be drained without violating the live latency
objective? The question recurs in every system built on a durable log, and it is
usually answered by a number someone chose — a concurrency limit, a batch size, a
token-bucket rate — and then adjusted after it goes wrong.

This paper measures where that boundary actually sits. In a controlled harness
with a live path and a recovery path at independently configured open-loop rates,
sharing one capacity-controlled downstream, we locate the transition between safe and
catastrophic drain by pre-registered bisection across seven experimental cells,
spanning two service times, three configured capacities, two admission limits and
four concurrency levels. **Across those seven cells the safe drain boundary lay
at or near measured service capacity, and was indistinguishable from it at each
cell's experimental resolution.** Per-cell values are given in §VI, each at its
own cell's resolution. Varying the latency objective produced no resolvable
movement over the well-posed sweep — 50 to 500 ms in the 5 ms arm, 100 to 500 ms
in the 25 ms arm.

<!-- claim register headline, verbatim; range from results/REVIEWER-RESPONSE-W2.md T3 -->

That result is only useful if capacity is known, and the substance of this paper
is that it was not. The downstream is a purpose-built instrument with an explicit
capacity parameter, staffed from that parameter by Little's law [@little], built for this
study and measured by its author. It overstated its own capacity because of a
per-request timing bias of `δ` = 0.463 ms — the pooled
saturation-plateau-inferred value — which corresponds to a capacity
overstatement of **9.26% at a 5 ms service time and 1.85% at 25 ms**. The safe margin being measured is under one percent. At the 5 ms
service time, the error in the figure against which that margin was expressed was
more than an order of magnitude larger than the margin itself.

An error of that relative size does not announce itself as an error. Because this
per-request timing bias is approximately constant in absolute terms, it distorts short service
times far more than long ones, and a distortion that varies systematically with a
configuration parameter looks, from the outside, like a property of the system.
Of three candidate explanations of the boundary put to registered tests, the
**admission limit** was rejected by its own falsification criterion before any
calibration; **concurrency** survived that test and was reduced to a residual
below the corrected search resolution once the instrument was corrected; **service time** survived its test and is
undermined, though not re-adjudicated, by the calibrated evidence (§VIII). The
falsification machinery could reject a wrong explanation. It could not identify
the timing bias from the effects that bias produced.

The general form of the observation is this. **When the safety margin being
characterised is sub-percent, a small and approximately service-time-independent
per-request timing bias can exceed the phenomenon under study, generate a stable
but false second-order effect, survive deliberate falsification, and invalidate
conclusions about which signals are usable for control.** The mechanism in this harness is a runtime timer overrun,
and that particular cause is uninteresting; what is interesting is that a campaign
operating under a public pre-registration, with an explicit falsification
protocol and a standing commitment to retract, could not detect a
sub-millisecond bookkeeping error from its consequences alone. It was found by
measuring the instrument, not by reasoning about the results.

<!-- claim register, scale-mismatch statement, verbatim -->

The consequence for recovery control is specific, and narrower than it may
first appear. In this harness, interpreting a sub-percent recovery margin
required a capacity reference validated against observed throughput rather than
the configured parameter; more generally, a configured capacity figure should
not be treated as ground truth when its calibration error is unknown or
comparable to the operating margin. Whether that estimate is supplied by external calibration or inferred online is
not settled by this work: the per-request bias varies with offered load (§V), so
an offline benchmark would itself have to be run at the load condition that
matters, and the present experiments do not adjudicate between the two. The harness was built on the stronger assumption — its configured
capacity is exposed only on an administrative endpoint the consumer never reads,
so that a controller would have to infer capacity rather than be told it — and
the campaign then walked into the hazard that precaution guarded against.

Section II positions the work and states what is not claimed. Section III
describes the harness and its capacity error model; Section IV the
pre-registration, estimator and resolution; Section V the calibration; and
Section VI the corrected boundary. Section VII reports which observables warn,
Section VIII returns to the three candidate explanations, and Sections IX and X
give threats to validity and conclusions.

The paper's main results and methodological contributions are:

**C1 — Boundary characterization.** Seven cells, uniform 5 rps bracketing, a
pre-registered mechanical estimator, n = 3 at each original probed point, with five
last-SAFE endpoints subsequently replicated to n = 12 or n = 15. The safe boundary
lies at or near measured capacity and is indistinguishable from it at each cell's
own experimental resolution. No effect of configured capacity, admission limit,
concurrency, service time, or the latency objective over the well-posed sweep was
resolvable at those resolutions; §VI reports one residual that remains below the
applicable resolution and is not claimed. The seven-cell campaign preregistered
the boundary-search procedure and tests of configuration dependence, not an
absolute boundary location relative to measured capacity; the near-capacity
location is therefore a measured descriptive result rather than confirmation of
a preregistered location prediction.

**C2 — The calibration trap.** A per-request overhead constant to within 4%
across a fivefold service-time range, varying with offered load, and 99.8%
attributable to timer overrun. One
second-order finding is traced to it in full — the apparent concurrency
dependence, which survived its registered falsification. Calibration reduced that
previously resolved concurrency-associated separation to a residual below the
corrected search resolution. Under matched last-SAFE accounting, the point
estimates correspond to a 94–95% reduction depending on estimator; that
percentage describes the measured point estimates, not a resolved residual
effect. A second finding, the apparent service-time dependence, survived
its own registered test and is undermined by the calibrated evidence without its
registered statistic having been recomputed; §VIII states that limitation rather
than counting it as a third case. The correction was checked against plateau
predictions derived from independently measured timing constants rather than
fitted to the corrected runs: correcting the emulated service time by that bias
was predicted to yield capacities of 1987.4 and 1997.7 rps in the two arms.
Those predictions appear in the registration, but the committed plateau records
do not establish whether the registration preceded the measurements; §IX-C
records that provenance gap. The first corrected windows
were 1987.4 and 1998.1 rps; addendum A8 subsequently replicated both plateaus at
ten 60-second windows per arm, giving medians of 1988.96 and 1997.70 rps.

**C3 — What warns, and what does not.** Request timeout rate gives no advance
warning of the boundary: it never crosses its criterion before the last safe
point, and that result replicates on a corrected-harness corpus collected after
the analysis statistic was frozen. A queue-depth lead over live p99, observed on
the uncorrected corpus, is reported as **exploratory**: the statistic it depends
on was chosen with that data in view, and the one independent corpus available
samples too coarsely to have resolved a lead of that size in either direction. On
the corrected corpus the two signals do not separate at the available resolution,
so the queue-depth-before-latency ordering remains unresolved. §VII offers a
hypothesis with a named experiment, not a result.

**C4 — Method.** A public pre-registration with six dated amendments; three
further findings, later overturned by independent checks and reported in §IX,
retracted before publication rather than after; a regression fixture
pinning the pre-correction corpus; a provenance guard that refuses to run without
a resolvable commit; and a cross-check that caught a defect in the project's own
utilisation estimator.
