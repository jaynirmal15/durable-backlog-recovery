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

All ten amendments and record corrections are listed in [@tab:s1-amendments] with their commits; the article glosses the six that
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
