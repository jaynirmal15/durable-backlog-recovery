# §4 — Method

*Draft 24 — KEYED FIGURE AND TABLE REFERENCES, 2026-09-20. Every literal "Fig. N", "Figure N" and "Table N" in the body is replaced by a key (`[@fig:…]`, `[@tab:…]`) that the build renders as "Fig. N" / "Table N" from order of first appearance — the citation design, applied to floats, so numbering cannot go stale when tables are added. Table 1's caption paragraph is now delimited as `caption:tab:amendments` and its literal "**TABLE 1** —" prefix removed, since the build numbers tables. No other wording changed.*
*Draft 23 — FROZEN.
Draft 23: manuscript tables renumbered into citation order (§4, §6, §8, §9), so
the resolution table is Table 2, not Table 3. Mechanical; the generated
artefact keeps its filename until the W5 rename.*
*Draft 22 —
Draft 22: §IV-H said the per-cell maximum is taken "across that point's three
repetitions". Five of the seven last-SAFE points carry twelve or fifteen, and
§IV's own "two cells reach 1.0002" holds only over all of them — over the first
three, neither cell exceeds 1.0. The sentence contradicted a number two pages
later. Corrected to say what the analysis does.*
*Draft 21 —
Draft 21: T1 gains A9 `9caf476` and A10 `51026cc`, both record corrections whose
temporal columns read N/A because they govern neither data nor analysis; the
count and the reproducibility statement follow. Mechanical, as A8's row was.*
*Draft 20 —
Draft 20: the provenance field list names all four, matching A9 and §V.*
*Draft 19 —
Draft 19: the provenance-guard paragraph now says which records the guard covers.
It governs the runner; the standalone saturation tool stamps nothing, and §V and
§IX carry the consequence.*
*Draft 18 —
Draft 18: `C_measured` given one definition in both §IV-D and §IV-E — median
across a cell's saturation runs of each run's maximum 30-second sustained served
rate — since it is the headline's normalisation denominator and was described two
ways; and the untested-safeguard sentence reworded.*
*Draft 17 —
Draft 17: the quadrature sentence no longer refers to "an earlier draft" — an
unpublished draft is not a thing a reader can check, and the point stands without
it.*
*Draft 16 —
Draft 16: the quadrature combination is withdrawn — a deterministic search-grid
width and an observed range are not variances and this section declines that
interpretation everywhere else; the two terms are now reported separately with a
linear conservative bound. Three scope fixes: "ceiling", the directional "just
below", the over-broad "one step" and "all 171 runs".*
*Draft 15 — Sept 14 2026. Budget raised to ~2,000 words. Table T1.
Draft 15: the reserved DOI replaces the placeholder. Mechanical; the deposit is
still uploaded and published at W6 from the frozen commit.
Draft 14: two mechanical defects, no scientific reopening — the amendment-count
sentence did not account for A8 having been discussed already, and
"per-request trace" appeared twice in the reproducibility paragraph.
Draft 13: mechanically reopened to add A8. Frozen draft 12 said six amendments
and one re-analysis were "all" the registration carries; A8 was registered after
that draft froze and §V now rests on its result, so the count, Table 1 and the
reproducibility statement were factually incomplete. Nothing else changed.
Draft 12: reproducibility statement notes that traces live in the deposit, not
the repository. Draft 11: reproducibility statement qualified — figures were not byte-identical
until non-deterministic PDF metadata was suppressed. Draft 10: denominator uncertainty characterised and its omission from the
quoted resolution recorded; E2e per-repetition rates recovered, limitation
discharged. Draft 9: dataset map corrected — the lossy corpus is E2e, NOT the seven cells
behind F5; all seven provenance-reconstruct. Draft 8: C_measured is a normalisation reference rather than a ceiling — no
[rho_safe, 1] interval, nothing called degenerate; monotonicity audit given its
own rule; withdrawn range removed from prose. Draft 7: aggregation scoped (E2e is not produced by the search), initial
bracket construction documented, E1 c10/C1 provenance gap disclosed. Draft 6: no-aggregation rule stated, host-stall conditions given, true->measured
capacity, "confirmatory" dropped. Two items still open (which endpoint is
quoted; initial bracket construction). Draft 5 fixed A7's temporal classification, corrects the misclassification-bias
direction, formalises rho_config / rho_eff, and justifies the differing
averaging intervals. Draft 4 closed all nine reviewer items against `results/METHOD-AUDIT.md` and
addendum A7. C3 is exploratory; the decision not to run a finer sweep to settle
it is recorded in the outline.
Source comments strip in W6.*

---

## 4. METHOD

### A. Why the protocol is mechanical

The estimator below was registered because an earlier phase of this project had
already failed in a specific way: three separate quantities had been reported to
more precision than the measurement supported. The registration states this as
its own motivation. Its purpose is that the boundary be decided by a rule fixed
in advance rather than by inspecting traces, and it was committed before any data governed
by it were collected.

<!-- PRE-REGISTRATION.md preamble; commit 371e477, registered 2026-09-11 -->

The document is referenced by commit hash and is immutable: no rule in it may be
changed once that hash is cited. Corrections take the form of dated amendments
appended to it, with the original text left intact and the reason stated, and an
amendment made after results were opened is marked as such. Six amendments, one registered re-analysis, one registered replication and two
record corrections were made. All ten are listed in [@tab:amendments]; four are discussed
below.

### B. The service level objective

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

### C. Point classification and the search

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
single figure is nonetheless required — the per-cell value plotted in [@fig:collapse] —
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
[@fig:collapse], which plots these cells and only these cells.

**The two corrected-harness cells** were not produced by this search. They were
assembled directly from run records by a separate analysis path that stored one
median ρ per point. The per-repetition rates have since been recovered from the
33 retained run records — every record carries the quantities the estimator
needs, and the reconstruction reproduces all eleven committed medians exactly —
so this is no longer a limitation of the corpus. They support the predict-and-eliminate result of §V, two of the
four bars in [@fig:plateau], the signal series of §VII, and the re-analysis registered
as A7. **They are not members of the seven and contribute to no seven-cell
number.**

The limitation therefore falls on the corrected cells and not on the boundary
result: the repetition-level sensitivity reported above covers §VI's central
comparison, and does not cover §V's brackets, [@fig:plateau]'s corrected bars, §VII or
A7. The recovered per-repetition rates change nothing: the
predict-and-eliminate verdict is identical under all four aggregators, and the
A7 ordering is unchanged. Their per-point spread of 2.1 to 7.1 rps would flag
against the registered 5 rps constant, but those searches resolved to 55 and 65
rps rather than 5, so against the resolution actually achieved the spread is
eight to ten times smaller than the step — more headroom than anywhere in the
seven-cell corpus. The one difference that remains is estimator: the seven
measure over the delivery span under A4, the corrected cells over the drain
window as measured. [@fig:plateau] places both side by side, which is legitimate
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

### D. Resolution, and why the headline is phrased as it is

That floor is the paper's precision discipline, and it was registered rather than
adopted afterwards. The registration further states that quoting a value to more
significant figures than the interval width supports is a protocol violation.

At a capacity near 2000 rps one 5 rps step is approximately 0.25% of capacity.
Per-cell resolution varies with capacity and is tabulated with each boundary;
the coarsest cell resolves to 0.0127 in utilisation.

Two sources of uncertainty enter the reported ratio, and both are characterised.

In the **numerator**, replicate spread at points carrying n = 12 is at most 24%
of one step, so where that replication exists the step — not run-to-run
variation — dominates. **That bound is scoped and does not generalise to the whole
campaign.** Five of seven cells carry a replicated point; every one of them is a
last-SAFE endpoint and none is a first-non-SAFE endpoint, and both
reduced-capacity cells are replicated at n = 3 only. The 24% figure therefore
bounds safe-side variability in five cells, and no claim is made about
variability at non-SAFE endpoints or in the two unreplicated cells.

<!-- results/REVIEWER-RESPONSE-W2.md task 2; T3 in §VI -->

In the **denominator**, `C_measured` is the median, across a cell's 6 to 15
saturation runs, of each run's maximum 30-second sustained served rate taken from
the downstream's own served counter — one such measurement per collapsed run. Its range spans 0.10% to 0.24% of
capacity, which propagates to between 0.09 and 0.80 of that cell's bisection
step — smaller than the search step in every cell, but not negligible in the
widest. The two terms are reported separately rather than combined. They are different
kinds of quantity — a deterministic search-grid width and an observed range over
repeated measurements — and nothing in this design licenses adding them as though
they were variances, which would import the probabilistic interpretation the rest
of this section is at pains to avoid.
Read conservatively they add linearly, in which case the quoted per-cell
resolution understates the figure a reader should use by between 1.09× and
1.80×, the upper end reached only in the cell whose denominator spread is
widest.

**The quoted per-cell resolution is the search step alone**, and §IX records
that omission. One consequence is worth stating rather than leaving implicit: at
the lowest plateau observed in each cell, two cells place the safe-side estimate
marginally above 1.0. The statement the data support is that the boundary sits
at or near measured capacity, indistinguishable from it at the
experiment's resolution — not that every cell lies strictly below it. That
strict form fails for two independent reasons, the numerator aggregator and the
denominator spread, which is why it is not used anywhere in this paper.

Every reported value is therefore quoted at the resolution of its own cell:
three decimals where the step permits, two in the coarsest cell, and never four.
This is why §VI reports the corrected boundaries as indistinguishable *at the
experiment's resolution* rather than as equal, and why no
boundary comparison rests on a difference smaller than one cell's
boundary-search resolution. Registered values are reproduced
verbatim at whatever precision they were registered, and may therefore carry more
digits than the surrounding analysis supports; re-rounding them would falsify the
record of what was predicted.

### E. What a boundary is, and what is quoted

A6 forbids reporting achieved utilisation at collapsed points (§IV-H), which
raises a question the reader must not have to infer: if the upper endpoint of a
bracket may be collapsed, in what space is the boundary reported, and what is
the single number quoted in §VI?

Two objects are reported, and only two.

**The boundary bracket, in rate.** `[R_lastSAFE, R_firstNonSAFE]` — what the
bisection actually resolved, and which no utilisation estimator touches.

**A safe-side normalised estimate**, `ρ_eff,safe = R_ach,lastSAFE / C_measured`,
computed at SAFE points only, where the estimator was built and validated. Where
a single per-cell scalar is required the numerator is the maximum achieved rate
across **all** of that point's repetitions — three at a point visited once by the
search, and twelve or fifteen at the five points that were replicated. The
distinction matters for the two cells that read above 1.0 below: over all
repetitions they reach 1.0002, and over the first three neither exceeds 1.0.
§IV-C reports the sensitivity of the aggregator choice.

**`C_measured` is a normalisation reference, not an imposed ceiling.** It is an
empirical plateau estimate — the median across a cell's saturation runs of each
run's maximum 30-second sustained served rate from the downstream's own counter,
as §IV-D defines it — and both numerator and denominator are measurements. A safe-side ratio may therefore read slightly above 1.0 without
implying service beyond a known physical bound, and two cells do: under the
named aggregator they reach 1.0002. The excess corresponds to approximately one
fifth of a bisection step and is therefore below the experiment's resolving
capability.

**No `[ρ_safe, 1]` interval is constructed**, and no cell is described as
degenerate or as pinned at saturation. Amendment A6, quoted verbatim where it is
quoted, frames the corrected report as an interval running up to a cell ceiling;
that framing assumes `C_measured` bounds the achieved rate from above, which the
data do not support in every cell. The registered text stands as the record of
what was decided on 13 September. The reporting form used here is narrower:
a rate bracket, and a normalised safe-side scalar whose distance from 1.0 is
read against the cell's own resolution.

**No achieved utilisation is manufactured for a collapsed upper endpoint.** The
per-cell value in §VI is the last SAFE point's, not a bracket midpoint, not an
interpolation, and not derived from any non-SAFE run. The claim it supports is
about how closely the boundary is approached from below.

Two denominators are in use, they are never mixed within a table, and they are
given distinct symbols because the paper carries four capacity quantities:

    ρ_config = ( λ_L,ach + R_ach ) / C_config                               (7)
    ρ_eff    = ( λ_L,ach + R_ach ) / C_measured                             (8)

Boundary files report `ρ_config`, following the registered definition of
achieved ρ. **The collapse figures of §VI are `ρ_eff`**, which is what makes
them a statement about measured service capacity rather than about the
configured parameter. They are reported per cell at each cell's own resolution
in [@tab:resolution]; no range spanning the cells is quoted, because the cells do not
share a precision. Predicted plateaus are `C_model`. `C_staffed` is
not a distinct quantity in this campaign: `ceil(C_config · S)` is exact in all
seven cells, so `C_staffed` equals `C_config` identically. Each cell's
measured-capacity reference ratio is
`C_measured / C_config`. Every figure and table names its denominator at the
point of use, and [@fig:collapse] names one per axis.

### F. Achieved rates, never nominal

Every utilisation in this work is computed from measured delivered rates. The
live component is taken from the injector's own issue counter over the drain
window rather than the configured rate, and the recovery component from messages
acknowledged over the delivery span rather than the configured limit.

The two components are averaged over different intervals, which requires
justification rather than assumption. Only recovery traffic ends before the drain
detector's confirmation tail, which is what A4 removes; live injection continues
at a constant paced rate throughout, and its measured delivery deficit over SAFE
runs never exceeds 0.0099%. Changing the live component's averaging interval
therefore cannot materially alter the numerator, and the registered estimator is
retained rather than adjusted for symmetry.

This distinction is not cosmetic. Nominal and achieved utilisation differ by
0.005 to 0.011 in this harness — between 0.7 and 1.6 times the transition width —
so the choice changes conclusions. It also changes orderings: in the E2 c10 cell
the nominal rates 865, 905 and 845 correspond to achieved rates of 1841.4, 1841.8
and 1842.2 respectively. Auditing monotonicity against nominal rate would have
concealed that reordering entirely. Nominal values may appear in a table only in a
column explicitly labelled nominal, adjacent to the achieved column.

Delivery accuracy is itself part of the instrument. The live injector originally
used a tick-dropping timer that under-delivered to 96.4–96.8% of its configured
rate on the target instance type; it was replaced with a lane-based pacer
(amendment A3) before any reported data was collected. Two runs aborted on the
delivery guard before that change and are recorded as not data.

### G. Provenance

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

### H. Amendments

<!-- caption:tab:amendments:start -->
Amendments to the pre-registration, the A7 registered
re-analysis, the A8 registered replication and the two record corrections. The
two right-hand columns separate registration *before the data existed* from
registration *before the analysis was run*; they are different claims and only
the first is prospective registration. They do not apply to a record correction,
which governs neither, and those rows read N/A rather than being forced into a
category they do not belong to.
<!-- caption:tab:amendments:end -->

<!-- table:tab:amendments -->
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

### I. Reproducibility

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

<!-- repo commit, pre-registration 371e477, Zenodo DOI 10.5281/zenodo.22761131
     (deposition 22761131, reserved 2026-09-14, empty draft; files uploaded and
     the record published at W6 from the frozen commit, at which point the DOI
     resolves), fixture tests/fixtures/aug18-regression -->
