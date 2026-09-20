# §1 — Introduction

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

A durable message broker does not lose work when its consumer stops. It
accumulates it. When the consumer returns, the backlog is still there and the
live traffic never went away, so the recovering system must do two jobs at once:
serve what is arriving now, and work off what arrived while it was gone. These
compete for the same downstream capacity. Drained at full speed, the backlog
displaces live traffic, and users who were unaffected by the original outage
experience the recovery as a second one.

The operator's question is a rate. Given a downstream serving live traffic under
a latency objective, how fast may the backlog be drained without violating that
objective? Too slow and the backlog outlives the incident; too fast and the
recovery becomes the incident. The question is ordinary, it recurs in every
system built on a durable log, and it is usually answered by a number someone
chose — a concurrency limit, a batch size, a token-bucket rate — and then adjusted
after it goes wrong.

This paper measures where that boundary actually sits. In a controlled harness
with a live path and a recovery path at independently configured open-loop rates,
sharing one capacity-controlled downstream, we locate the transition between safe and
catastrophic drain by pre-registered bisection across seven experimental cells,
spanning two service times, three configured capacities, two admission limits and
four concurrency levels. **Across those seven cells the safe drain boundary lay
within 1% of measured service capacity, and was indistinguishable from capacity
itself at the experiment's resolution.** Per-cell values are given in §VI at
each cell's own resolution; no single range is quoted, because the cells do not
share a precision and a range spanning them would assert one they do not have.
Varying the latency objective produced no resolvable movement over the
well-posed sweep — 50 to 500 ms in the 5 ms arm, 100 to 500 ms in the 25 ms
arm.

<!-- claim register headline, verbatim; range from results/REVIEWER-RESPONSE-W2.md T3 -->

That result is only useful if capacity is known, and the substance of this paper
is that it was not. The downstream is a purpose-built instrument with an explicit
capacity parameter, staffed from that parameter by Little's law, built for this
study and measured by its author. It overstated its own capacity by a
per-request timing bias of `δ` = 0.463 ms — the pooled
saturation-plateau-inferred value — which corresponds to a capacity
overstatement of **9.26% at a 5 ms service time and 1.85% at 25 ms**. The safe margin being measured is under one percent. At the 5 ms
service time, the error in the figure against which that margin was expressed was
more than an order of magnitude larger than the margin itself.

An error of that relative size does not announce itself as an error. Because the
overhead is approximately constant in absolute terms, it produces a large
relative distortion at short service times and a small one at long ones, and a
distortion that varies systematically with a configuration parameter is
indistinguishable, from the outside, from a property of the system. Over three
weeks this campaign put three candidate explanations of the boundary to
registered tests, and the protocol did not treat them alike. That the boundary
depended on the **admission limit** was rejected by its own falsification
criterion, before any calibration. That it depended on **concurrency** survived
that same test — and was removed almost entirely once the instrument was
calibrated. That it depended on **service time** also survived its registered
test; the calibrated evidence undermines that reading, but the registered
statistic was never recomputed, because the corrected corpus contains no cell at
the configuration it was measured in. The falsification machinery could reject a
wrong explanation. It could not identify the timing bias from the effects that
bias produced.

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
first appear. A controller cannot safely treat configured or nominal capacity as
ground truth when its operating margin is smaller than the calibration error in
that figure; it requires a capacity estimate that has been empirically validated.
Whether that estimate is supplied by external calibration or inferred online is
not settled by this work. One measurement reported in §V bears on the question
without deciding it: the overhead is not a fixed constant but varies with offered
load, so an offline benchmark would itself have to be conducted at the load
condition that matters. Choosing between the two approaches requires a controller
comparison, which this paper does not contain.

The harness was nonetheless built on the stronger assumption. The downstream's
configured capacity parameter is exposed only on an administrative endpoint that
the consumer never reads, precisely so that a controller would be forced to infer
capacity rather than be told it — a design position taken before any
measurement. What this campaign shows is narrower than that
position but sufficient to motivate it: the figure such a controller would
otherwise have trusted could be wrong by substantially more than the operating
margin — and, in the 5 ms arm, by more than an order of magnitude. The decision was taken as a precaution; the
campaign then walked into the hazard it was guarding against.

We therefore report two things that are usually separated: a measurement, and an
account of why the measurement is hard to get right. Section II positions the
work and states plainly what is not claimed. Section III describes the harness,
its capacity model, and an error model for that capacity. Section IV sets out the
pre-registration, the boundary estimator and the experiment's resolution.
Section V presents the calibration — the overhead measured directly, then
eliminated by prediction. Section VI presents the corrected boundary. Section VII
reports which observables warn, and what the corrected data can and cannot
establish about their ordering. Section VIII returns to the three candidate
explanations, to what the calibration changed about each, and to what the
differences between the three outcomes establish. Sections IX and X give threats
to validity and conclusions.

The contributions are:

**C1 — The boundary measurement.** Seven cells, uniform 5 rps bracketing, a
pre-registered mechanical estimator, n = 3 at each original probed point, with five
last-SAFE endpoints subsequently replicated to n = 12 or n = 15. The safe boundary lies within 1% of measured
capacity and is indistinguishable from it at the experiment's resolution. No
effect of configured capacity, admission limit, concurrency, service time, or the
latency objective over the well-posed sweep was resolvable at that precision; §VI
reports one residual that is below resolution and is not claimed.

**C2 — The calibration trap.** Its magnitude and its behaviour: a per-request
overhead constant to within 4% across a fivefold service-time range and varying
with offered load, of which 99.8% is attributable to timer overrun. One
second-order finding is traced to it in full — the apparent concurrency
dependence, which survived its registered falsification and which calibration
removes by 94 to 95%. A second, the apparent service-time dependence, survived
its own registered test and is undermined by the calibrated evidence without its
registered statistic having been recomputed; §VIII states that limitation rather
than counting it as a third case. The elimination is a registered prediction rather than
a fit: correcting the emulated service time by that bias was predicted to
yield capacities of 1987.4 and 1997.7 rps in the two arms, using constants
measured by a different instrument on separate runs. The first corrected windows
were 1987.4 and 1998.1 rps; addendum A8 subsequently replicated both plateaus at
ten 60-second windows per arm, giving medians of 1988.96 and 1997.70 rps.

**C3 — What warns, and what does not.** Request timeout rate gives no advance
warning of the boundary: it never crosses its criterion before the last safe
point. That result replicates on a corrected-harness corpus collected after the
analysis statistic was frozen and independent of the choice of it. A queue-depth
lead over live p99 was observed on the uncorrected corpus, but is reported as
**exploratory**: the statistic it depends on was chosen with that data in view,
and the one independent corpus available samples too coarsely to have resolved a
lead of the size reported, in either direction. On the corrected corpus the two
signals do not separate at the available resolution: in the long-service cell the
measured observables give no warning room at all, and in the short-service cell
several give advance warning but queue depth and live p99 cross together. The
queue-depth-before-latency ordering therefore remains unresolved. §VII offers a
hypothesis with a named experiment, not a result.

**C4 — Method.** A public pre-registration with six dated amendments; three
further findings, later overturned by independent checks and reported in §IX,
retracted before publication rather than after; a regression fixture
pinning the pre-correction corpus; a provenance guard that refuses to run without
a resolvable commit; and a cross-check that caught a defect in the project's own
utilisation estimator.
