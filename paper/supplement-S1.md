# Supplement S1 — Protocol and provenance record

*Supplementary material to "Measuring the Safe Drain Boundary for Durable Backlog
Recovery Under a Live Latency Objective". Every item here is cited from the
article, which states each item's consequence; this document gives the full
record. Text moved from the article is reproduced unchanged.*

---

## S1-A. Provenance (full text of the article's former §IV-G)

Early in the project 137 of 140 run records carried the string `"unknown"` in
place of a commit hash, because the function resolving it swallowed its error on
an unborn HEAD. The runner now refuses to start without a resolvable commit.
That guard covers the runner's own records — every boundary run carries a commit,
a branch, a dirty flag and a start time. It does not cover the standalone saturation tool
that measures plateaus, which stamps no provenance of any kind; §V states what
that costs and §IX carries it. No
run reported in this paper lacks a commit.

One provenance gap remains and is reported rather than closed. The search driver
records its results but not its own invocation, so the arguments that produced a
cell's probe set are recoverable only by replaying the committed planner against
the observed classifications. **All seven cells reconstruct exactly**, each with
no supplied ceiling. One required care: in E1 c10/C1 two SAFE points lie below
the floor the descent located, and they carry a run-id prefix identifying them
as probes from the replication campaign rather than the original search, which
the artefact does record. Replaying the planner on the original campaign's rates
alone reproduces that cell's probe set exactly.

What is not recoverable is the command line itself. The gap is therefore in the
reproducibility of probe *selection*, not in the measurements: for every cell,
all probed rates, all repetitions, all classifications and the terminal 5 rps
bracket are retained and used, no run carries an exclusion reason, and none is
absent from its cell's analysis — the search driver raises rather than
continuing if a run is invalid, so a silently dropped run is not a state it can
reach. Adding an argument echo would prevent a recurrence and would recover
nothing retrospectively; the driver is left unaltered, because changing a frozen
instrument after its campaigns have closed is the practice this section exists
to avoid.

## S1-B. Amendments (full text of the article's former §IV-H, with Table S1)

All ten amendments and record corrections are listed in [@tab:s1-amendments] with their commits; the article glosses the seven that
later sections cite.

<!-- caption:tab:s1-amendments:start -->
Amendments to the pre-registration, the A7 registered
re-analysis, the A8 registered replication and the two record corrections. The
two right-hand columns separate registration *before the data existed* from
registration *before the analysis was run*; they are different claims and only
the first is prospective registration. They do not apply to a record correction,
which governs neither, and those rows read N/A rather than being forced into a
category they do not belong to.
<!-- caption:tab:s1-amendments:end -->

<!-- table:tab:s1-amendments:s1 -->
| # | Date | Commit | Change | Predates governed data | Predates governed analysis |
|---|---|---|---|---|---|
| A1 | 2026-09-11 | `e5bf303` | Interval's upper end is the first NON-SAFE point, which may be MARGINAL, not the first UNSAFE point | Yes | Yes |
| A2 | 2026-09-11 | `1fe9de3` | A non-SAFE anchor extends the search downward instead of aborting for a hand-chosen anchor | Yes | Yes |
| A3 | 2026-09-11 | `699e105`, `25583c7` | Live injector moves from a tick-dropping timer to lanes | Yes | Yes |
| A4 | 2026-09-11 | `d5ea89d`, `ddd428d` | Achieved recovery rate measured over the delivery span, not the drain window | **Partly** — the first boundary's traces (c10/C0) already existed and were recomputed; registered before the remaining E1 cells | Yes |
| A5 | 2026-09-12 | `fe36734` | Leading-indicator noise scale changed from mean to median | **No** | **No** — chosen with the numbers in view |
| A6 | 2026-09-13 | `c3aee75` | A4 is not valid at collapsed points; utilisation is not reported there | **No** | **No** |
| A7 | 2026-09-14 | `939902d` | *Registered re-analysis, not an amendment.* The frozen leading-indicator criterion and statistic, re-run over the corrected-harness corpus | **No** — that corpus already existed | **Yes** — criterion, statistic and prediction all frozen before the re-analysis |
| A8 | 2026-09-14 | `590d1cc` | *Registered replication, not an amendment.* Repeatability of the two corrected saturation plateaus: ten 60-second windows per arm, median convention, with both arms' readings fixed in advance. No registered constant, no plateau estimator and no analysis path is changed by it | **Yes** — the twenty windows were collected afterwards | **Yes** |
| A9 | 2026-09-19 | `9caf476` | *Record correction, not an amendment.* A8's short-arm reading states that neither plateau figure was itself registered as a plateau; `67c448b` tabulates both and gates the boundary read on them, so that statement is wrong. No A8 criterion, datum or result depends on it | **N/A** — governs no data | **N/A** — governs no analysis |
| A10 | 2026-09-19 | `51026cc` | *Record correction, not an amendment.* A6 reports the E2d collapse factor as 10.3×, computed from a midpoint numerator against a SAFE-only denominator; matched on the SAFE side it is 10.5×. The denominator, the direction and A6's verdict are unchanged | **N/A** — governs no data | **N/A** — governs no analysis |

A7 is a registered re-analysis of an already-collected corpus, not a prospective
registration, and the two columns are separated so that the distinction cannot
be read the other way.

A8 is neither an amendment nor a re-analysis. It changes no rule and revisits no
existing data: it registers a *new* measurement — the window-to-window
repeatability of two plateaus the campaign had measured once each — before that
measurement was taken, and fixes in advance what each possible outcome would
mean, including the outcome that would have removed a prospective claim §V
currently makes. It is prospective in the same strict sense as A1 through A3,
and appears last only because it postdates the measurement campaign it bears
on. Its result is reported in §V-D.

A9 and A10 are a third kind again: **record corrections**. Each fixes a factual
misstatement in the text of an earlier registration, and neither changes a rule,
an estimator, a datum or a conclusion. They exist because this registration is
immutable once its commit is cited, so a correction takes the form of a dated
addendum with the original left standing — and because applying that rule only
when a correction is convenient would cost more than the addenda do. A9's error
understated what had been registered; A10's makes a reported factor 2% larger.
The second direction warrants more scrutiny than the first, and §IX gives both
in full.

<!-- all ten verified against git log; audit in results/METHOD-AUDIT.md -->

A1 through A3 were registered before any data governed by this registration were
collected — an earlier phase of the project had produced data, which is what
motivated the protocol — and require no further comment. A8 is described above;
the remaining four do.

**A4** replaced an estimator, not an instrument. Chronologically it was
registered during E1, after the traces for the first boundary (c10/C0) already
existed and before the remaining E1 cells were collected; it was then applied
retrospectively to those first traces. The original measure divided an
exact backlog by a window padded with the drain detector's confirmation tail,
which injected run-to-run noise the rate limiter had not produced. Measuring
instead over the span the recovery traffic actually occupied removes that tail.
It was applied to already-recorded traces and required no run to be repeated.

**A5 is the one amendment in this document made with the numbers already in
view, and it changes an answer.** The registration says so in those terms and
documents it at length precisely because it is the most attackable step in the
leading-indicator analysis. It is reported here on the same basis: a reader
should be able to attack it with the evidence in front of them.

**A7 attempts to repair that, and does not succeed.** A5 froze the statistic on
12 September at 07:31 UTC, having been chosen on the E1 corpus collected five
hours earlier — and the leading-indicator analysis reads only that corpus. A7
therefore registered, before running anything, a re-analysis of the same frozen
criterion and the same frozen statistic over the corrected-harness corpus, which
was collected 34 hours after A5 froze and played no part in choosing it, together
with the prediction to be tested. The registration preceded the analysis by
commit timestamp.

The prediction did not replicate. The timeout component held cleanly. The
ordering component did not: queue depth and live p99 first move at the same
probed point in both corrected cells. **The registered limitation is what
decides the interpretation.** E1's safe grids are sampled at 5–10 rps where they
are finest; the corrected cells at 60 and 100 rps. A lead of the 10–25 rps that
E1 reported is below the corrected corpus's resolution by construction, so that
corpus could not have replicated the ordering in either direction. The honest
statement is the stronger one: the ordering is unreplicated, and the only
independent corpus available was incapable of adjudicating it. §VII reports it
as exploratory on those grounds and on A5's chronology independently.

**A6** records that A4 is valid at safe points but over-reads at collapsed ones,
where the recovery traffic's occupied span is not the drain. Eighteen of twenty
unsafe points reported achieved rates above their own saturation plateau — a
count, not a magnitude, and therefore not a judgement about resolution. The
defect was caught by a cross-check of the estimator against the plateau rather
than by inspection, and utilisation is no longer reported at collapsed points.
Its consequences for the reported intervals are set out in §IX.

## S1-C. Reproducibility (full text of the article's former §IV-I)

The harness, the pre-registration with all six amendments, the A7 registered
re-analysis, the A8 registered replication and the A9 and A10 record
corrections, every run record and per-request trace — the traces are archived
with the dataset rather than held in the repository, so delivery-span
quantities are checkable against their artefacts from the repository alone but
re-derivable from raw observations only with the deposit — the analysis code, the figure generators and the regression
fixture are archived under DOI `10.5281/zenodo.22761131`. Every reported artefact regenerates
byte-identically from the committed data by running its own script, and a
manifest records a SHA-256 for each file together with the commit the package
was built from.

That property was verified rather than assumed, and verifying it found a
counter-example. The data artefacts reproduced byte-identically throughout; the
figures did not, because the plotting library stamps a wall-clock creation time
into each file, so two runs over unchanged inputs produced different bytes with
identical drawn content. The metadata is now suppressed and determinism is
verified over consecutive runs, with the rendered marks confirmed unchanged
against the committed versions. The claim as stated held for the artefacts it
had been checked against and not for the ones it had not, which is the ordinary
way such claims fail.

## S1-D. The capacity model, pictured (the article's former Fig. 2)

[@fig:capacity-model] pictures the relation equations (4)–(6) state
algebraically: the harness staffs its pool on the assumption that a worker
turns a request round in exactly the emulated service time, each worker in fact
pays a fixed additional cost per request, and because that cost is additive
rather than proportional it consumes a larger share of a short service time
than a long one. The figure carries no measured result, which is why the
article states the relation in equations and keeps the picture here.

<!-- figure:fig:capacity-model:F2-capacity-model.pdf:s1 -->

## S1-E. Per-cell resolution in full (the article's Table 2, all columns)

The article's resolution table is compacted to the three quantities its
argument uses: the boundary bracket, the normalised per-cell resolution and the
safe utilisation. [@tab:resolution-full] is the same seven cells with every
column the generator produces, so that a reader checking the resolution
discipline against the artefacts has the configured and measured capacities,
the raw bisection step, the bracket width, the repetition count, the replicate
spread and the measured capacity's own range in one place.

## S1-F. The objective and the search (full text of the article's former §IV-B and §IV-C)

*Reproduced unchanged except that the article's figure keys are written out as figure names, because a supplement cannot number the article's floats.*

The objective is evaluated per one-second window over the drain window, on live
traffic only. A window is a *latency breach* if live p99 exceeds 250 ms, an
*error breach* if the live error rate exceeds 1%, and a *violating second* if
either holds. `vSLO` is the fraction of violating seconds.

Live traffic means injector-direct requests only. Two exclusions apply, both
registered in advance, and both are reported here with their exercised extent
because an outcome-dependent exclusion in a saturation experiment deserves
scrutiny.

Status 429 is an injector-side drop rather than a downstream signal and is
excluded from error accounting. The concern this invites is real: an injector
that drops more as load rises would starve the downstream and make a run look
artificially safe. **No run recorded a single injector-side drop** — zero across
the 171 runs of the seven-cell boundary corpus. The registered ±1% delivery guard checks warm-up rather than the
drain, so in-drain delivery was measured separately: the worst sustained deficit
among SAFE runs is 0.0099%, a hundredth of one percent, and delivery is
marginally *better* in UNSAFE runs than in SAFE ones — the opposite of the
direction that would flatter the result.

Seconds flagged by the host-stall detector are excluded from both numerator and
denominator, with the unexcluded value recorded as `vSLO_raw`. A second is
flagged only when four conditions hold at once: live 1 s p99 at or above five
times its rolling healthy baseline, recovery 1 s p99 at or above five times its
own, downstream queue depth **at or below five requests**, and a maximum
inter-sample gap in the request stream exceeding 150 ms; each flagged second
also contaminates the following five. The third condition is why genuine
overload cannot trigger it — at a collapsed point the queue is deep by
definition. **It never fired**: zero seconds were excluded across the 171-run seven-cell
boundary corpus, and
no classification differs under `vSLO_raw`. It is therefore an untested
safeguard, and what that establishes is not that the detector works but that no
result in this paper depends on it.

`vSLO_latency`, `vSLO_error` and `vSLO_both` are reported in every table and
identify *which* failure mode produced a violation. They do not address
sub-threshold degradation, and are not claimed to: a second at p99 = 249 ms is
non-violating under all four measures. Continuous live p99 and queue-depth
series are therefore retained separately, and it is those that §VII uses. The
registration states — before any data — that `vSLO` alone is not a sufficient
safety statistic, because it saturates deep in collapse and is blind to
degraded-but-passing traffic at the other edge; the decomposition addresses the
first of those, the continuous series the second.

Each probed rate is run **n = 3** times and classified from those three `vSLO`
values alone:

- **SAFE** — `vSLO ≤ 0.01` in all three repetitions.
- **UNSAFE** — `vSLO > 0.05` in at least two repetitions.
- **MARGINAL** — anything else.

The three classes are exhaustive and mutually exclusive. **Repetition
disagreement is never averaged**, and this applies to rate as well as to `vSLO`.
No single achieved rate is assigned to a probed point: the point retains all
three, and the reported interval spans every achieved ρ observed at each
endpoint, so disagreement between repetitions widens the interval rather than
being collapsed into a mean or a median. Disagreement across repetitions is itself the
signal that an operating point is unstable, which is the property the collapsed
regime has, and the mean of three `vSLO` values is not computed and appears in
no table.

The search additionally raises a registered diagnostic whenever the achieved-ρ
spread across repetitions at a point exceeds the search resolution, on the
grounds that bisection would then be resolving finer than its own instrument.
**It never fired** — zero of forty points across all seven boundary files,
endpoints included; the worst point sits at 40% of its own resolution.

**Two qualifications, both of which narrow that statement.** First, where a
single figure is nonetheless required — the per-cell value plotted in the article's collapse figure —
it is the maximum achieved ρ across the last SAFE point's repetitions. The
choice is semantic before it is statistical: a point is classified SAFE only if
**all three** repetitions satisfy the SAFE criterion, so the maximum is the
highest empirically demonstrated safe throughput among repetitions at the
terminal SAFE point. It is a defined safe-side quantity rather than the most
favourable of several candidates.

It is also immaterial. Recomputing under minimum, maximum, mean and median
leaves the monotonicity audit, the identity of the last SAFE point in every
cell, and the reported values after resolution-matched rounding all unchanged,
because the largest within-point spread anywhere in the campaign is 0.0010, or
two requests per second — below both the rounding step and the search
resolution.

Second, the scope of that statement has to be given exactly, because two
distinct corpora appear in this paper.

**The seven cells** — four from E1, two from E2, one from E2b; forty probed
points, 171 runs — are the boundary result, and they are self-contained. Each
cell's denominator comes from that cell's own saturation runs. Every one of the
171 repetitions retains its own achieved rate, so the no-aggregation rule, the
spread diagnostic and the aggregator sensitivity all apply to them, and to
the article's collapse figure, which plots these cells and only these cells.

**The two corrected-harness cells** were not produced by this search. They were
assembled directly from run records by a separate analysis path that stored one
median ρ per point. The per-repetition rates have since been recovered from the
33 retained run records — every record carries the quantities the estimator
needs, and the reconstruction reproduces all eleven committed medians exactly —
so this is no longer a limitation of the corpus. They support the predict-and-eliminate result of §V, two of the
four bars in the article's plateau figure, the signal series of §VII, and the re-analysis registered
as A7. **They are not members of the seven and contribute to no seven-cell
number.**

The limitation therefore falls on the corrected cells and not on the boundary
result: the repetition-level sensitivity reported above covers §VI's central
comparison, and does not cover §V's brackets, the article's plateau figure's corrected bars, §VII or
A7. The recovered per-repetition rates change nothing: the
predict-and-eliminate verdict is identical under all four aggregators, and the
A7 ordering is unchanged. Their per-point spread of 2.1 to 7.1 rps would flag
against the registered 5 rps constant, but those searches resolved to 55 and 65
rps rather than 5, so against the resolution actually achieved the spread is
eight to ten times smaller than the step — more headroom than anywhere in the
seven-cell corpus. The one difference that remains is estimator: the seven
measure over the delivery span under A4, the corrected cells over the drain
window as measured. the article's plateau figure places both side by side, which is legitimate
because predicted against measured plateau is a direct throughput comparison
with no ρ estimator involved, but its caption must say so.

The initial bracket is constructed rather than assumed. A ceiling may be
supplied; if it is not, the first candidate is the anchor raised by ten percent,
rounded to 5 rps, and stepped again while it continues to classify SAFE. Every
candidate — supplied or stepped — is freshly probed at the campaign's own
repetition count before it is used, on every harness and without exception, so
every rate appearing in a boundary file was actually run. A supplied ceiling
that classifies SAFE is demoted to the floor and the upward search restarts from
it. The downward search has the 5 rps resolution floor as its terminating guard;
the upward search has no probe budget and no equivalent guard, an asymmetry that
did not arise in this campaign but is a defect in the procedure rather than a
property of the results.

The search then bisects between the last-SAFE anchor and the first-non-SAFE
ceiling. Midpoints are rounded to the nearest 5 rps. A SAFE midpoint becomes the new
floor; an UNSAFE **or MARGINAL** midpoint becomes the new ceiling, so marginal
behaviour lies inside the reported interval rather than below it. The anchor is
probed first and, if it does not classify SAFE, the search steps downward rather
than assuming a floor (amendment A2). Anchors inherited from an earlier phase do
not count, because those points were measured on the defective harness.

**The search stops when the bracket is 5 rps wide, and the registration states
that 5 rps is the resolution floor and that no claim is made below it.**

Bisection presupposes that safety is non-increasing in offered load, and the
search terminates at the first non-SAFE classification. The two misclassification
errors are not symmetric in their consequences. A spuriously **non-SAFE** point
truncates the search conservatively, moving the reported last-SAFE point
downward and therefore *away* from capacity — it costs the headline rather than
supporting it. The consequential error is the opposite one: a spuriously
**SAFE** point above the true boundary moves the safe-side estimate upward,
toward the claim the paper makes. Requiring all three repetitions to satisfy the
SAFE criterion, against two of three for UNSAFE, makes that classification
deliberately the stringent one. The monotonicity assumption is nonetheless
audited rather than assumed, and the audit needs its own rule, because a point
retains three achieved rates and cannot be ordered by all three at once. The
audit therefore proceeds at the point level using a single achieved rate per
point, and was repeated under each of the four candidate aggregators — minimum,
maximum, mean and median. The rank order of points within a cell is identical
under all four, so the audit reads the same input in every case. **No inversion
occurred in any of the seven cells, under any aggregator**, where an inversion
means a higher-rate point classifying safer than a lower-rate one.

Two facts bound what that audit establishes. First, it can speak only for the
forty points that were probed; bisection does not sample what it does not
choose. Second, **no point in the study ever classified MARGINAL** — the forty
points divide as twenty SAFE and twenty UNSAFE. The MARGINAL class, and
amendment A1 which governs its treatment as a ceiling, were therefore never
exercised on any reported result. They are retained in the protocol as
registered, not as machinery that shaped an outcome.

One bracket is weaker than the rest and is named rather than averaged into the
others. In E1 c10/C0 the last SAFE point reports three zero `vSLO` values and the
first UNSAFE point reports 0.077, 0.000 and 0.135 — one replicate at exactly
zero. Under the registered rule this is UNSAFE, since two of three exceed 0.05.
The disagreement is not a defect in the classification but the instability the
registration anticipated at an unstable operating point, and it is reported as
such.

## S1-G. Admission and the configured-capacity endpoint (from the article's former §III-C)

*The article keeps equation (3) and the cancellation argument; the implementation detail and the endpoint history are here, unchanged.*

Under the graceful profile the admission limit is `queueCap = 50 · c`; and under the *cliff* profile it is `2 · c`, returning an immediate rejection
once full. The queue channel itself is allocated at four times the admission
limit; admission is enforced by a token pool rather than by channel capacity, so
the limit can be changed without reallocating.

<!-- downstream/main.go queueCapFor(), NewServer(), fullQueueDelayMs() -->

The time to traverse a full queue is the admission limit divided by the service
rate. Under the intended occupancy model the service rate is `c / S` and the
traversal time is `50 · S` — 250 ms at `S = 5` ms. Under the corrected occupancy
model of §III-D the service rate is `c / (S + δ)` and the traversal time is
`50 · (S + δ)`. In both cases the worker count cancels. **The admission rule
therefore cannot by itself produce a capacity-dependent or concurrency-dependent
queue-delay scale, under either the intended model or the corrected one** — a
point §VIII returns to, since one of the candidate explanations proposed exactly
that mechanism.

One separation is deliberate and load-bearing. The configured capacity parameter
is exposed only on an administrative endpoint, which the consumer never reads.
The harness was built so that a recovery controller could not rely on the
configured capacity parameter and would have to operate from observations
instead. The results later justify distrust of that configured value, while not
determining whether a validated estimate should be supplied offline or inferred
online — a distinction §I leaves open and this paper does not settle. The
decision was taken before any measurement, for a reason narrower than the one
that ultimately justified it.

It is worth recording that the endpoint's response field is named `trueCapacity`,
<!-- withdrawn-quote-ok: quoting the harness specification as a primary source, to contradict it -->
and the specification describes it as exposing true capacity. It does not: it
returns `C_config`. The name is itself a residue of the assumption this paper
falsifies, and it is preserved unaltered in the archived artefact.

## S1-H. The corrected corpus in detail (full text of the article's former §VII-C and §VII-D)

*Reproduced unchanged except that the article's figure key is written out as a figure name.*

### S1-H.1 The corrected corpus: warning without ordering

The corrected corpus answers differently in each of its two cells, and the two
answers together are the result.

In the corrected **long-service** cell there is no warning room at all. Mean queue
depth, all three live latency percentiles and mean in-flight requests first cross
at `rl` 1210, which is the last safe point. On that cell the leading-indicator
framing has nothing to lead with.

In the corrected **short-service** cell there is warning room but no resolved
ordering. Mean queue depth, live p99, live p90 and mean in-flight all first cross
at `rl` 1075, with the last safe point at 1185 still ahead of them — one probe
point, roughly 110 requests per second of safe operating range after the first
crossing. Only live p50 crosses with no room, and only timeout rate never
crosses. But those four cross *together*: what is absent in this cell is the
ordering, not the warning.

**The corrected corpus therefore does not reproduce the queue-before-latency
ordering at its available resolution. It does not show that no metric gives
advance warning.** Those are
different claims and this section keeps them apart.

One further observation belongs here, with its quantity named. In the
short-service cell the *mean* drain queue depth never reaches its DEEP threshold
anywhere inside the safe range, peaking at 23.1 requests against 50. That is a
statement about the mean; the article's signal figure plots the queue *peak*, which behaves
differently and is discussed below.

A possible explanation suggests itself, and is offered as a hypothesis rather
than as a finding. The corrected corpus samples coarsely near the boundary — 60
and 100 requests per second between safe points, against E1 margins of 10 to 25 —
so it may leave too little resolution to distinguish the relative *onset* of
queue depth and live latency even where both give advance warning. Under that
hypothesis a lead of E1's size would disappear below this corpus's sampling
resolution. Whether the original separation was itself related to the calibration
error remains untested.

**This is not a fourth retracted finding, and the evidence here does not support
making it one.** It is a hypothesis with a named experiment: a 5 requests per
second sweep across the top 50 of each corrected cell's safe range, about sixty
runs at n = 3, which would resolve a lead of E1's size in either direction.
§IX records it as the study that would settle the question.

### S1-H.2 What the figure shows, and why it is unaffected

the article's signal figure plots drain queue peak and live tail latency across the corrected
short-service cell as utilisation approaches its boundary. Both rise across the
sampled safe range — the queue peak from 7 requests to 111, live p99 from 8 ms to
58 — and both then change sharply at the transition between the final SAFE point
and the following non-SAFE one: the queue reaches its cap of 500 and live p99
rises to 508 ms. **That interval is 55 requests per second, not 5.** The
corrected-harness searches did not resolve at the seven-cell corpus's 5 rps step;
§IV records their achieved resolutions as 55 and 65 rps, and they are not members
of the seven-cell boundary corpus.

The figure is unaffected by the downgrade in §VII-B, and the reason is worth
stating. Its pipeline uses no noise statistic anywhere — it reads utilisation,
queue peak, live p99 and the classification directly — so it never depended on
the quantity A5 chose or A7 re-examined. A figure that survives a downgrade
because it never rested on the downgraded thing is evidence about the figure, not
a coincidence.

What §VII does **not** claim is that latency warns last, or that either signal is
the right one to build a controller on. §II establishes live latency as a
literature-grounded comparator, which is what makes these observations about a
signal the literature already uses. This section reports only that on this
harness, at
this resolution, timeout rate never warns; the queue-depth lead observed on E1 is
unreplicated and unresolvable on the available data; and on the corrected corpus
some observables do give advance warning in one cell, but queue depth does not
lead live p99 at the resolution available.

## S1-I. Two documentation failures (full text from the article's former §IX-C)

Two documentation failures belong here, recorded for what caught them. An
incorrect reading of the corrected-corpus figure propagated through report
prose, a caption, the title drawn inside the figure itself and an early section
draft, because each layer was written from the previous summary rather than from
the data, while the registered analysis's own table contradicted it throughout.
Separately, a summary generalised one evidentiary pattern across three candidate
explanations; generating the table meant to display them, with every quotation
asserted against its source, showed that one had been refuted before calibration
and another had no like-for-like post-calibration test. Neither is an
experimental finding, and the lesson is the control rather than the error: for a
claim about several items at once the authority is a generated table whose cells
are checked against their sources, not the prose in between.

## S1-J. Provenance of the campaign itself (the article's former §V-G)

Two readings were made and corrected mid-campaign, both recorded in the
registration, and one earlier claim — that a break within 0.0004 of a registered
prediction confirmed the saturated figure — is withdrawn, the bracket having
contained both candidates at a resolution that could not support the agreement.
Section IX and the registration give all three in full.
