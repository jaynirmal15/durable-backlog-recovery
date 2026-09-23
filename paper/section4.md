# §4 — Method

*Draft 30 — TWO-REVIEW REVISION, 2026-09-23. A3: the excess above unity in the two highest cells is 0.06 and 0.08 of a bisection step, not "about a fifth". A fifth was imported from E2D-REPORT, where 0.18 and 0.14 of a step describe different cells falling short of 1.0.*

*Draft 29 — CONCEPT DOI, 2026-09-23. §IV-I cites `10.5281/zenodo.22761130`, the **concept** DOI, naming the version in the sentence: "archived as version 1.0.1 under DOI …". The version DOI was replaced because once IEEE Access publishes, the DOI printed in the paper is frozen permanently, and a version DOI would leave that paper pointing at a superseded artefact with no edit available. Byte-pinning is unaffected — `MANIFEST.json` and the pre-registration commit do that — and naming the version tells a reader which entry in the Versions panel to open. **This is the only change: one DOI and the four words around it.***
*Draft 28 — DEPOSIT PUBLISHED, 2026-09-22. **No body text changes.** The source comment beside §IV-I records the Zenodo record as published 2026-09-23 from commit `e22e779` rather than as a reserved empty draft. The reproducibility statement itself already read "are archived under DOI …" in the present tense, and publication made that true without an edit — which is what reserving the DOI in W2 was for.*
*Draft 27 — ACRONYM COMPLIANCE, 2026-09-20, ruled by review: §IV-B's `vSLO` definition names it the SLO violation fraction. No other change; Draft 26's freeze otherwise stands.*
*Draft 26 — CUT PASS, increment 2, 2026-09-20. §IV-B and §IV-C are compressed
and their full text moves, unchanged, to Supplement S1-F; §IV-D and §IV-E are
tightened in place. Kept, per the ruling: the SLO definition and both registered
exclusions with their exercised extent; n = 3 and the SAFE / UNSAFE / MARGINAL
rules; no averaging of repetitions; the per-cell aggregator and its immateriality;
the seven-cell / corrected-cell scope; bisection semantics and the 5 rps floor;
the asymmetric-error argument and the monotonicity audit; the unexercised
MARGINAL class; the weak E1 c10/C0 bracket; the numerator and denominator
uncertainty terms with their scope; the "at or near" form; the two reported
objects, 1.0002, the refusal of a [ρ_safe, 1] interval, and equations (7)–(8).
Moved to S1: the stall detector's four conditions, the initial-bracket
construction, inherited anchors, and the corrected cells' per-repetition spread
against their 55 and 65 rps steps. No number, finding or rule changes.*
*Draft 26 — APPROVED AND FROZEN by review, 2026-09-20, on all five checks: the seven-cell / corrected-cell scope in §IV-C; the corrected cells outside every seven-cell statistic while supporting §V, the plateau figure, §VII and A7; A6's registered framing versus the narrower reporting form in §IV-E; `C_measured` as normalisation reference, `ρ_eff,safe` SAFE-side only, no [ρ_safe, 1] interval; and both uncertainty terms in §IV-D.*
*Draft 25 — CUT PASS, increment 1, 2026-09-20, under the reviewer's supplement
ruling. §IV-G, §IV-H and §IV-I are compressed and their full text moves, unchanged,
to Supplement S1 (`paper/supplement-S1.md`), together with Table 1. Kept in the
article, as the ruling requires: the standalone plateau tool's missing provenance
(a limitation that qualifies the prospective test); the probe-selection gap; a
gloss of A4–A10, because amendments are cited 42 times outside §IV-H; the
before-data / before-analysis distinction; and the archive's identifiers. No
number, finding or rule changes.*
*Draft 25.1 — APPROVED by review; "six" corrected to "seven" in §IV-A and §IV-H, since the gloss covers A4–A10. Increment 1 frozen.*
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
record corrections were made. §IV-H glosses the seven that later sections cite;
Supplement S1 lists all ten with their commits.

### B. The service level objective

The objective is evaluated per one-second window over the drain window, on live
traffic only. A window is a *latency breach* if live p99 exceeds 250 ms, an
*error breach* if the live error rate exceeds 1%, and a *violating second* if
either holds. `vSLO` is the fraction of violating seconds (the SLO violation fraction).

Live traffic means injector-direct requests only. Two exclusions were registered
in advance, and **neither was exercised.** Status 429, an injector-side drop, is
excluded from error accounting; no run in the 171-run seven-cell corpus recorded
one, and the worst in-drain delivery deficit among SAFE runs is 0.0099%, with
delivery marginally *better* in UNSAFE runs — the opposite of the direction that
would flatter the result. Seconds flagged by the host-stall detector are
excluded, with the unexcluded value kept as `vSLO_raw`; the detector requires a
shallow downstream queue, so genuine overload cannot trigger it, and it never
fired. No result depends on it. Supplement S1 gives both rules in full.

`vSLO_latency`, `vSLO_error` and `vSLO_both` identify which failure mode produced
a violation. None of them sees sub-threshold degradation — a second at p99 =
249 ms is non-violating under all four — so continuous live p99 and queue-depth
series are retained separately, and §VII uses those. The registration states,
before any data, that `vSLO` alone is not a sufficient safety statistic: it
saturates deep in collapse and is blind to degraded-but-passing traffic.

### C. Point classification and the search

Each probed rate is run **n = 3** times and classified from those three `vSLO`
values alone:

- **SAFE** — `vSLO ≤ 0.01` in all three repetitions.
- **UNSAFE** — `vSLO > 0.05` in at least two repetitions.
- **MARGINAL** — anything else.

**Repetition disagreement is never averaged**, for rate or for `vSLO`: a point
retains all three achieved rates, and the reported interval spans every achieved
ρ observed at each endpoint, so disagreement widens the interval rather than
being collapsed into a mean or a median. Disagreement is itself the signal of an
unstable operating point. A registered diagnostic, raised when a point's
achieved-ρ spread exceeds the search resolution, **never fired**: zero of forty
points, the worst at 40% of its own resolution.

Where a single per-point figure is required — the per-cell value in
[@fig:collapse] — it is the maximum achieved ρ across the last SAFE point's
repetitions. Because SAFE requires **all three** repetitions to pass, that is the
highest demonstrated safe throughput at the terminal SAFE point, not the most
favourable of several candidates. It is also immaterial: under minimum, maximum,
mean and median the monotonicity audit, the last SAFE point in every cell and the
rounded values are all unchanged, because the largest within-point spread in the
campaign is 0.0010, or two requests per second.

That sensitivity covers **the seven cells** — four from E1, two from E2, one from
E2b; forty points, 171 runs — which are the boundary result and self-contained.
**The two corrected-harness cells** were assembled by a separate analysis path.
They support §V's predict-and-eliminate result, two of the bars in
[@fig:plateau], §VII's signal series and A7, and **contribute to no seven-cell
number.** Their per-repetition rates, since recovered from the retained run
records, change none of those results under any aggregator. One difference
remains: the seven measure over the delivery span (A4), the corrected cells over
the drain window, which is why [@fig:plateau]'s caption states that its bars come
from two corpora.

The search probes an anchor, steps upward to a first non-SAFE ceiling — every
candidate freshly probed at n = 3 — and then bisects between the last SAFE point
and the first non-SAFE one, rounding midpoints to 5 rps. A SAFE midpoint becomes
the floor; an UNSAFE **or MARGINAL** midpoint becomes the ceiling (A1), so
marginal behaviour lies inside the reported interval rather than below it. A
non-SAFE anchor steps the search downward (A2). **The search stops when the
bracket is 5 rps wide, and the registration states that 5 rps is the resolution
floor and that no claim is made below it.** Supplement S1 gives the procedure in
full, including one asymmetry in it: the upward search has no probe budget, a
defect in the procedure that did not arise in this campaign.

Bisection presupposes that safety is non-increasing in offered load, and the two
misclassification errors are not symmetric. A spurious **non-SAFE** point moves
the reported estimate away from capacity, against the headline; a spurious
**SAFE** point above the boundary moves it toward the claim the paper makes.
Requiring three of three for SAFE, against two of three for UNSAFE, makes the
consequential classification the stringent one. Monotonicity was audited rather
than assumed, under all four aggregators: **no inversion occurred in any of the
seven cells.** The audit speaks only for the forty probed points, and **no point
ever classified MARGINAL** — twenty SAFE, twenty UNSAFE — so the MARGINAL class
and A1 were never exercised on any reported result.

One bracket is weaker than the rest and is named rather than averaged. In E1
c10/C0 the first UNSAFE point reports 0.077, 0.000 and 0.135: UNSAFE under the
registered rule, with one replicate at exactly zero — the instability the
registration anticipated at an unstable operating point, reported as such.

### D. Resolution, and why the headline is phrased as it is

That floor is the paper's precision discipline, and it was registered rather than
adopted afterwards; the registration also makes quoting a value to more
significant figures than its interval supports a protocol violation. At a
capacity near 2000 rps one 5 rps step is about 0.25% of capacity. Per-cell
resolution varies with capacity and is tabulated with each boundary; the
coarsest cell resolves to 0.0127 in utilisation.

Two sources of uncertainty enter the reported ratio. In the **numerator**,
replicate spread at points carrying n = 12 is at most 24% of one step, so where
that replication exists the step dominates. **That bound is scoped:** the five
replicated points are all last-SAFE endpoints, both reduced-capacity cells are
replicated at n = 3 only, and nothing is claimed about non-SAFE endpoints or the
two unreplicated cells. In the **denominator**, `C_measured` is the median,
across a cell's 6 to 15 saturation runs, of each run's maximum 30-second
sustained served rate from the downstream's own counter. Its range spans 0.10%
to 0.24% of capacity, or 0.09 to 0.80 of that cell's step. The two terms are
reported separately: one is a deterministic grid width and the other an observed
range, and nothing in this design licenses combining them as variances. Read
conservatively they add linearly, and the quoted resolution then understates the
figure a reader should use by 1.09× to 1.80×.

<!-- results/REVIEWER-RESPONSE-W2.md task 2; T3 in §VI -->

**The quoted per-cell resolution is the search step alone**, and §IX records
that omission. One consequence: at the lowest plateau observed in each cell, two
cells place the safe-side estimate marginally above 1.0. The statement the data
support is that the boundary sits at or near measured capacity, indistinguishable
from it at the experiment's resolution — not that every cell lies strictly below
it. That strict form fails for two independent reasons, the numerator aggregator
and the denominator spread, and is used nowhere in this paper.

Every value is quoted at its own cell's resolution — three decimals where the
step permits, two in the coarsest cell, never four — and no boundary comparison
rests on a difference smaller than one cell's step. Registered values are
reproduced verbatim at their registered precision; re-rounding them would
falsify the record of what was predicted.

### E. What a boundary is, and what is quoted

A6 forbids reporting achieved utilisation at collapsed points, so the space in
which the boundary is reported has to be stated. Two objects are reported, and
only two.

**The boundary bracket, in rate.** `[R_lastSAFE, R_firstNonSAFE]` — what the
bisection actually resolved, and which no utilisation estimator touches.

**A safe-side normalised estimate**, `ρ_eff,safe = R_ach,lastSAFE / C_measured`,
computed at SAFE points only, where the estimator was built and validated. The
numerator is the maximum achieved rate across **all** of that point's
repetitions — three at a point visited once by the search, twelve or fifteen at
the five replicated points. This matters for the two cells that read above 1.0:
over all repetitions they reach 1.0002, and over the first three neither exceeds
1.0.

**`C_measured` is a normalisation reference, not an imposed ceiling.** Numerator
and denominator are both measurements, so a safe-side ratio may read slightly
above 1.0 without implying service beyond a known physical bound. The excess in
those two cells is 0.06 and 0.08 of a bisection step, below the experiment's
resolution. For the same reason **no `[ρ_safe, 1]` interval is constructed**, and
no cell is described as degenerate or pinned at saturation: A6's registered text
frames the report as an interval up to a cell ceiling, which assumes
`C_measured` bounds the achieved rate from above. That text stands as the record
of what was decided; the form used here is narrower. **No achieved utilisation
is manufactured for a collapsed upper endpoint** — the per-cell value in §VI is
the last SAFE point's, not a bracket midpoint and not an interpolation.

Two denominators are in use, never mixed within a table:

    ρ_config = ( λ_L,ach + R_ach ) / C_config                               (7)
    ρ_eff    = ( λ_L,ach + R_ach ) / C_measured                             (8)

Boundary files report `ρ_config`, following the registered definition of
achieved ρ. **The collapse figures of §VI are `ρ_eff`**, which makes them a
statement about measured service capacity rather than about the configured
parameter. They are reported per cell at each cell's own resolution in
[@tab:resolution]; no range spanning the cells is quoted, because the cells do
not share a precision. Predicted plateaus are `C_model`. `C_staffed` equals
`C_config` identically in this campaign, since `ceil(C_config · S)` is exact in
all seven cells, and each cell's measured-capacity reference ratio is
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

Every boundary run carries a commit, a branch, a dirty flag and a start time,
and the runner refuses to start without a resolvable commit — a guard added
after an early defect left 137 of 140 run records without one. No run reported
in this paper lacks a commit. The guard does not cover the standalone saturation
tool that measures plateaus, which stamps no provenance of any kind; §V states
what that costs and §IX carries it.

One further gap is reported rather than closed. The search driver does not record
its own invocation, so probe *selection* is recoverable only by replaying the
committed planner against the observed classifications; all seven cells
reconstruct exactly. The measurements themselves are complete: every probed rate,
repetition and classification is retained and used, and no run is excluded.
Supplement S1 gives the full record.

### H. Amendments

Supplement S1 tabulates all ten entries with their commits and, for each, whether
it was registered before the data it governs and before the analysis it governs —
different claims, of which only the first is prospective registration. A1–A3
predate all governed data and fix details of the search and the injector. The
seven that later sections rely on are:

- **A4** measures the achieved recovery rate over the delivery span rather than
  the drain window. It was registered during E1, after the first boundary's traces
  existed and before the remaining cells, and was applied retrospectively to
  those traces.
- **A5** changed the leading-indicator noise scale from mean to median with the
  E1 numbers in view. It is the one amendment made with the data visible, and it
  changes an answer.
- **A6** records that A4 over-reads at collapsed points, where the recovery
  traffic's occupied span is not the drain; utilisation is not reported there.
- **A7** is a registered re-analysis, not an amendment: the frozen
  leading-indicator criterion and statistic, re-run over the corrected-harness
  corpus, which played no part in choosing them. It was registered before the
  analysis but after the data existed. Its ordering prediction did not replicate,
  and that corpus could not have resolved the ordering in either direction (§VII).
- **A8** is a registered replication: ten 60-second windows per arm for the two
  corrected plateaus, with each arm's reading fixed before any window was run. It
  changes no rule and is prospective in the strict sense; §V-D reports it.
- **A9** and **A10** are record corrections: dated addenda fixing factual
  misstatements in earlier registration text, with the originals left standing.
  Neither changes a rule, a datum or a conclusion; §IX gives both.

### I. Reproducibility

The harness, the pre-registration with its amendments and record corrections,
every run record and per-request trace, the analysis code, the figure generators,
the regression fixture and Supplement S1 are archived as version 1.0.1 under
DOI `10.5281/zenodo.22761130`. The traces are held in the deposit rather than the
repository, so delivery-span quantities are re-derivable from raw observations
only with the deposit. Every reported artefact regenerates byte-identically from
the committed data by its own script, and a manifest records a SHA-256 for each
file and the commit the package was built from. Verifying that property found one
counter-example, since fixed: the figures carried a wall-clock creation time
(S1).

<!-- repo commit, pre-registration 371e477, Zenodo CONCEPT DOI
     10.5281/zenodo.22761130, which always resolves to the newest version.
     v1.0.0 was published 2026-09-23 as record 22761131 from commit e22e779
     and carried a build defect on page 20; v1.0.1 supersedes it. The version
     DOI is deliberately NOT cited here: the DOI printed in an accepted paper
     cannot be changed, so it must not name one version.
     fixture tests/fixtures/aug18-regression -->
