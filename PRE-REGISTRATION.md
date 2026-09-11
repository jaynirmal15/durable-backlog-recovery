# PRE-REGISTRATION — boundary estimator and B3 calibration protocol

**Registered 2026-09-11, before any E1–E4 run.** Nothing in this document may be
changed once its commit is referenced in the paper. If a rule here turns out to
be wrong, the correction is registered as a **dated amendment below**, with the
original text left intact and the reason stated. Amendments made after results
are opened are marked as such and the affected results are reported both ways.

Why this exists: every headline in this project so far has had a harness
explanation, and three separate quantities (ρ*, the transition width, the
concurrency effect) were reported to more precision than the measurement
supported. The estimator below is mechanical so that the boundary is decided by
a rule fixed in advance, not by looking at the traces.

## 1. Service level objective

Unchanged from Phase 0/1. Evaluated **per one-second window over the drain
window**, on live traffic only:

| Term | Definition |
|---|---|
| Latency breach | live p99 within the 1 s window **> 250 ms** |
| Error breach | live error rate within the 1 s window **> 1%** |
| Violating second | latency breach **OR** error breach |
| `vSLO` | violating seconds ÷ total seconds, artifact-excluded |

Live traffic means injector-direct requests only (`liveSLOPopulation =
injector_direct`). Status 429 is an injector client-side drop, not a downstream
signal, and is excluded from error accounting. Seconds flagged by the host-stall
detector are excluded from the numerator and denominator; `vSLO_raw` reports the
unexcluded value and both are recorded.

`vSLO_latency`, `vSLO_error` and `vSLO_both` decompose the violation by which
predicate fired and are reported alongside `vSLO` in every table. `vSLO` alone
is not a sufficient safety statistic: it saturates deep in collapse and is blind
to degraded-but-passing traffic at the other edge.

## 2. Point classification

Each probed rate `rl` is run **n = 3** times. The point is classified by the
three `vSLO` values alone:

| Class | Rule |
|---|---|
| **SAFE** | `vSLO ≤ 0.01` in **all three** repetitions |
| **UNSAFE** | `vSLO > 0.05` in **at least two** repetitions |
| **MARGINAL** | anything else |

The three cases are exhaustive and mutually exclusive: a point where two runs
exceed 0.05 is UNSAFE even if the third is 0; a point where one run is 0.02 is
MARGINAL, not SAFE. MARGINAL is a real outcome, not a failure to decide, and is
reported as such.

**Repetition disagreement is never averaged.** The mean of three `vSLO` values
is not computed and does not appear in any table. Disagreement across
repetitions is the signal that the operating point is unstable, which is the
property the collapsed regime actually has once the CPU clamp is removed.

## 3. Search procedure

Given a last-SAFE anchor `lo` and a first-non-SAFE ceiling `hi`:

0. **The anchor is probed first.** If it does not classify SAFE it is not a
   floor: it becomes `hi`, and the search steps **downward** in decrements of
   10% (rounded to 5 rps) until a point classifies SAFE, which becomes `lo`.
   The lowest non-SAFE point seen becomes `hi`. If the descent reaches the
   5 rps floor without a SAFE point, **no interval is reported** — the result
   is "no safe recovery rate exists at this condition on the measurable grid",
   reported as such. (Amendment A2.)
1. If `hi` is not known, step **upward** from `lo` in increments of 10% of `lo`
   (rounded to 5 rps) until a point classifies UNSAFE or MARGINAL. That point
   becomes `hi`.
2. Bisect on `rl` between `lo` and `hi`. The midpoint is rounded to the nearest
   **5 rps**.
3. A SAFE midpoint becomes the new `lo`; an UNSAFE midpoint becomes the new
   `hi`. A **MARGINAL midpoint becomes the new `hi`** — the boundary is defined
   as the last point that is unambiguously safe, so marginal behaviour lies
   inside the interval, not below it.
4. Stop when `hi − lo ≤ 5` rps. **5 rps is the resolution floor**; no claim is
   made below it.

The anchor `lo` must itself be verified SAFE under this protocol before
bisection begins. An anchor inherited from Phase 1 does not count: those points
were measured on the defective harness.

## 4. Reporting ρ*

**ρ\* is reported as an interval, never a point.**

    ρ* ∈ [ ρ_achieved(last SAFE) , ρ_achieved(first NON-SAFE) ]

The upper end is the **first non-SAFE point**, which may classify **MARGINAL or
UNSAFE**. §3 step 3 makes a MARGINAL midpoint the new ceiling, so a MARGINAL
point can and often will terminate the search from above; calling that endpoint
"first UNSAFE" would misdescribe it. **The class of the upper endpoint is
recorded per boundary** (`firstNonSafeClass`) and stated wherever the interval
is quoted, because "safe up to here, marginal above" and "safe up to here,
collapsed above" are different findings and must not be reported in the same
words.

Both endpoints are **achieved** ρ, defined in §5. The interval is the claim. A
midpoint, a mean, or a value quoted to more significant figures than the
interval width supports is a protocol violation.

If any point inside the interval classified MARGINAL, the interval is reported
with its MARGINAL points listed explicitly. If repetitions at an endpoint
disagree, the interval **widens** to include the disagreement; it is never
narrowed by discarding a repetition. A run may be excluded only for a recorded
integrity failure (`invalidReason`), never for being inconvenient, and every
excluded run is listed with its reason.

Where two conditions are compared (arms, capacity regimes), the comparison is
between intervals. **Overlapping intervals do not support a claim of
difference.** The c10/c50 gap reported in Phase 1 (~0.07) is an order of
magnitude wider than the measurement bias, so it is expected to survive; the
C0-vs-C1 invariance claim (0.92 to three significant figures) is expected not
to, and is not assumed here.

## 5. Achieved ρ, never nominal

Every ρ in this project is computed from **measured delivered rates**:

    ρ_achieved = ( λ_L_achieved + rl_achieved ) / C_d

- `λ_L_achieved` from the injector's own issue counter over the drain window
  (`injRate` in the timeline, `warmupInjectorAccuracy` at warm-up), not the
  configured `-live-rate`.
- `rl_achieved` from recovery messages acked over the drain window
  (`backlogAtRestore / tDrain`), not the configured `-rate-limit`.
- `C_d` is the configured downstream capacity during the fault window, which is
  a server setting rather than a measurement.

Nominal ρ may appear in a table **only** in a column explicitly labelled nominal
and adjacent to the achieved column. The two differ by 0.005–0.011 in this
harness, which is 0.7× to 1.6× the transition width, so the distinction changes
conclusions.

## 6. "Latency-invisible" is a number

The claim that latency gives no warning before the boundary is made
**numerically or not at all**:

> Latency is *invisible* at the boundary if the live p99 at the last SAFE point
> is **within 20%** of the healthy-baseline p99 for the same arm and capacity.

The healthy baseline is measured in the same session as a live-only run at
ρ ≈ 0.5, and is recorded per arm and per capacity in the boundary file. If p99
at the last SAFE point exceeds baseline by more than 20%, latency **is** a
usable leading indicator at that condition and the claim is reported as not
holding there. `p50` and `qMean` at the same point are reported alongside, since
the Verification-A finding was that `p50` and occupancy move while `p99` and
`vSLO` do not.

## 7. B3 calibration protocol

B3 is the latency-feedback AIMD baseline. Its parameters are chosen by a
declared procedure **before** any formal E4 run, and frozen.

### Declared grid — 36 configurations

| Parameter | Values | Meaning |
|---|---|---|
| Additive step | **10, 25, 50** rps | increment per observation interval while healthy |
| Multiplicative factor | **0.5, 0.7, 0.9** | rate multiplier on a latency trigger |
| Observation interval | **1 s, 5 s** | control period |
| Latency trigger | **p99 > 250 ms**, **p99 > 125 ms** | at-SLO and half-SLO triggers |

The half-SLO trigger is included deliberately so that B3 is not handicapped by
being forced to wait until the SLO is already breached. A baseline that loses
only because it was configured to react late is not evidence about the method.

### Calibration

- **Traces:** C0-constant (`P0-A`, C = 2000, λ_L = 1000) only, at **both arms**
  (c10 and c50). C1/C2/C3 are held out entirely: calibrating on the regimes that
  E4 evaluates would make the comparison circular.
- **Repetitions:** n = 3 per configuration per arm.
- **Objective:** **minimise `tDrain` subject to `vSLO ≤ 0.01`** in all three
  repetitions. Configurations failing the constraint are ineligible regardless
  of drain time. Ties on `tDrain` within 2% are broken by lower `vSLO_latency`,
  then by the larger observation interval (the more conservative controller).
- **Selection:** one configuration per arm. If the winners differ between arms,
  **both are carried into E4 and reported separately**; B3 is not given a
  per-condition advantage RHC does not get.
- **Freezing:** the chosen parameters are written to
  `results/B3-CALIBRATION.json` and committed **before** the first formal E4
  run. The commit hash is quoted in the paper. Re-calibration after seeing E4
  results is a protocol violation; if it happens it is reported as such and both
  sets of results are published.

RHC receives the same treatment: any RHC parameter chosen by a search is
calibrated on the same held-out traces, with the same objective, and frozen in
the same commit. Neither method is tuned against the evaluation conditions.

## 8. The E4 prediction, registered before results are opened

Quoted verbatim from `NOTES.md`:

> **Phase 2 / Gate 2 prediction (register now):** B3 (latency AIMD) should
> **approximate RHC at 50 servers and fail badly at 10.** All three outcomes
> (reproduces / B3 works at 10 / B3 fails at both) are informative.

and, in its shorter form later in the same file:

> **Phase 2 prediction:** B3 ≈ RHC at 50 servers, fails badly at 10.

### Scoring rule, fixed now

"Approximate" and "fail badly" are given numeric meaning before the data is
seen. Per arm, comparing B3 against RHC on the same condition:

| Outcome | Rule |
|---|---|
| **B3 ≈ RHC** | B3's `tDrain` within **15%** of RHC's **and** B3's `vSLO ≤ 0.01` |
| **B3 fails badly** | B3's `vSLO > 0.05`, **or** `tDrain` more than **50%** worse than RHC's |
| **Intermediate** | anything else — reported as intermediate, not rounded to either |

The prediction is **confirmed** only if B3 ≈ RHC at c50 **and** B3 fails badly
at c10. Any other combination is a failed prediction and is reported as a failed
prediction, in the same words as this paragraph, without reframing.

### The premise may not survive

Registered explicitly because it affects how the result should be read: this
prediction was derived from the claim that probing **must** overshoot at low
concurrency, and that claim rests on the sharpness of the c10 boundary as
measured on the harness with the spin-wait admission defect. E1 re-measures that
sharpness. **If the c10 boundary is not sharp on the fixed harness, the
prediction's premise is gone**, and a confirmation would then be weak evidence,
not strong. That conditional is registered now so it cannot be applied
selectively after the fact.

## 9. Scope

This document governs the boundary estimator, the achieved-ρ convention, the
latency-invisibility test, and the B3/RHC calibration and scoring. It does not
pre-register the experiment list, the conditions, or the analysis of anything
else. `STATUS.md` holds the re-run list and the validity of prior results.

Implementation: `scripts/locate_boundary.py` implements §§2–5 and is the only
sanctioned way to locate a boundary. Its unit tests assert the classification
and bisection rules against synthetic tables, so a change in behaviour breaks a
test rather than passing silently.

## Amendments

### A1 — 2026-09-11: the interval's upper end is the first NON-SAFE point

**Registered before any E1–E4 run; no results existed when this was made.**

§4 originally read:

> ρ* ∈ [ ρ_achieved(last SAFE) , ρ_achieved(first UNSAFE) ]

That contradicted §3, which already made a MARGINAL midpoint the new ceiling.
Under the original wording a search that terminated on a MARGINAL point would
have had its upper endpoint reported as "first UNSAFE", which is a stronger
claim than the data supports and exactly the kind of label-versus-measurement
mismatch this protocol exists to prevent.

§4 now reads "first NON-SAFE", requires the endpoint's class (MARGINAL or
UNSAFE) to be recorded per boundary, and requires it to be stated wherever the
interval is quoted. §3 is unchanged — its behaviour was already correct.
`scripts/locate_boundary.py` records the endpoint as `firstNonSafeRl` and
`firstNonSafeClass`; those fields were named `firstUnsafeRl` and
`firstUnsafeClass` before this amendment and carried the same values.

No measurement changes, because no measurement has been taken.

### A2 — 2026-09-11: a non-SAFE anchor extends the search downward

**Registered before any E1–E4 run; no results existed when this was made.**

§3 assumed the supplied anchor was SAFE and said nothing about what happens if
it is not. `scripts/locate_boundary.py` aborted in that case and asked for a
lower anchor by hand, which would have put a human choice inside a procedure
whose whole purpose is to remove one.

This is not hypothetical. Every candidate anchor comes from Phase 1 and was
measured on the harness with the spin-wait admission defect, and the
2026-08-19 notes state directly that the c50 last-safe point (rl=380) was
**not safe** once the harness was fixed.

§3 gains step 0: a non-SAFE anchor becomes the ceiling and the search descends
by 10% until it finds a SAFE floor, symmetric to the existing upward step. If
the descent reaches the 5 rps resolution floor without finding one, no interval
is reported and the condition is recorded as having no safe rate on the
measurable grid, rather than an interval being forced.

Nothing else changes: classification, the 5 rps resolution, the treatment of
MARGINAL as a ceiling, and the interval definition are all untouched. Covered
by seven unit tests in `scripts/test_locate_boundary.py`.

No measurement changes, because no measurement has been taken.

### A3 — 2026-09-11: the live injector moves from the ticker to lanes

**Registered before any E1 data was collected.** Two runs had already aborted on
the delivery guard at that point; see "Not data" below.

#### The change

`-injector-pacer` moves from `ticker` (a tick-dropping `time.Ticker`) to `lanes`
(a multi-lane deadline pacer with bounded catch-up). `scripts/locate_boundary.py`
defaults to `lanes` and passes it to every run. The ±1% delivery guard is
**unchanged at ±1%** — the point of the change is that ±1% becomes satisfiable
on this platform without relaxing it.

#### Why: measured on the EC2 box at λ_L = 1000, C = 2000, S = 5 ms, 1024 workers

| pacer | delivered | of target |
|---|---:|---:|
| `ticker` | 968.0, 964.2 rps | **96.80%, 96.42%** |
| `lanes` | 999.7, 999.8 rps | **99.97%, 99.98%** |

A 3.3% shortfall in λ_L is about **0.017 in ρ**. The widest transition width
measured anywhere in this project is 0.007, so the generator error would be
roughly **2.4× the quantity being measured**. That is not a perturbation to
correct for afterwards; it would decide the answer.

The 2026-08-19 A/B at the same offered rate had already shown it (lanes 1000.0
with qMean 0.1 against the ticker's 975.4 with qMean 20.0 and `sloOK false`).
The ticker was kept then solely for comparability with the Phase 1 corpus. E1
re-measures every boundary and makes no comparison with the pre-EC2 corpus, so
that reason no longer exists.

#### Not data

Two E1 runs aborted with `injector delivered 967.0 rps vs target 1000 (96.70%),
outside +/-1.0%`. **Those are guard aborts, not measurements.** The guard fired
before the outage began; no drain was performed, no boundary point was
classified, and no run record was retained. They are recorded here because a
change of instrument mid-campaign has to be visible, not because they carry
information about any boundary.

#### Registered expectation, before boundary 1 lands

At `rl = 840` the two pacers put the operating point in different places:

| | λ_L delivered | achieved ρ at rl=840 |
|---|---:|---:|
| ticker (pre-EC2 corpus) | ~967 | **~0.909** |
| lanes (E1) | ~1000 | **~0.919** |

The anchor is therefore being probed about **0.010 higher in achieved ρ** than
the corpus point it is named after — again larger than the widest transition
width. **`rl = 840` may classify non-SAFE for injector reasons alone**, with
nothing about the dependency having changed. Amendment A2 already handles that
mechanically: a non-SAFE anchor sends the search downward.

Registering it now so that, if it happens, it is read as the instrument moving
rather than as a finding.

#### The arrival process, not just the mean rate

The justification above rests on mean delivery accuracy. That is not sufficient
on its own: two pacers can agree on rate to four figures and still present
different **processes** to the dependency, and queueing depends on the process.
Measured directly rather than assumed.

**Method.** Injector only — `scripts/probe_live_only`, no consumer and no NATS,
so the measured process is the pacer's alone. Nominal 1000 rps, 60 s measure
window, arrival timestamps captured at the downstream at **nanosecond**
resolution (`ARRIVAL_LOG_CAP`); the per-request sample stream is milliseconds and
cannot resolve 1 ms spacing. First and last 10% of each series dropped. Both
pacers measured on the **same** temporary `c6i.2xlarge`, so the comparison is
within-machine. Raw summary in `results/pacer-characterisation.json`.

| | mean inter-arrival | implied rate | **CV** | **IDC(1 s)** | IDC(100 ms) |
|---|---:|---:|---:|---:|---:|
| `ticker` | 1040.7 µs | 960.9 rps | **0.276** | **0.025** | 0.030 |
| `lanes` | 1000.1 µs | 999.9 rps | **0.359** | **0.001** | 0.005 |
| Poisson reference | — | — | 1.0 | 1.0 | 1.0 |
| Deterministic | — | — | 0.0 | 0.0 | 0.0 |

**They differ, and not in one direction.** `lanes` has a **1.3× higher CV** of
inter-arrival — slightly more jitter gap-to-gap — but a **~23× lower index of
dispersion at 1 s** and ~6× lower at 100 ms. The ticker's gaps are individually
more regular; its *counts* over any window that matters to a queue are much
less so, because dropping a tick removes a whole arrival rather than shifting it.

**Which statistic governs, and why they disagree.** The two measures point
opposite ways — `ticker` has the lower CV, `lanes` the lower IDC — so one of them
has to be the wrong instrument for this question. **IDC at 100 ms–1 s governs
here and inter-arrival CV is misleading**, for one reason: a queue integrates the
arrival–service imbalance over the time it takes to fill, and with a 500-deep cap
against a few percent of excess arrival rate that horizon is **seconds**, so what
matters is the variance of arrival *counts* over seconds, while per-gap jitter
cancels within milliseconds and never reaches the queue. CV is the right
statistic when each arrival is served immediately; IDC is the right one when
arrivals accumulate.

**Neither process is renewal, which is why CV cannot be converted into IDC.** For
a renewal process IDC → CV², and both are far below it:

| | CV | CV² | measured IDC(1 s) |
|---|---:|---:|---:|
| `ticker` | 0.276 | 0.076 | **0.025** |
| `lanes` | 0.359 | 0.129 | **0.001** |

IDC below CV² means successive intervals are **negatively correlated** — a long
gap is followed by short ones — in both pacers, by different mechanisms. The
ticker keeps an absolute schedule, so a late or dropped tick is followed by the
next tick at its originally scheduled time rather than a full period later. The
lanes pacer runs N independent deadline schedules, so one lane slipping does not
move the others and the aggregate count over a window is restored by the lanes
that did not slip. In both cases the correlation suppresses count variance far
below what the marginal gap distribution alone would imply, which is exactly why
quoting CV and reasoning about burstiness from it would get the answer backwards.

**Direction, stated as asked.** Smoother arrivals permit a higher ρ before
collapse. `lanes` is materially smoother at 100 ms–1 s, which is the timescale
over which a queue of 500 against 10 servers actually fills. So **part of any
ρ\* shift could be the arrival process rather than the rate correction**, and the
two act in **opposite directions**:

- the rate correction raises achieved ρ at a fixed `rl` (~0.909 → ~0.919), which
  pushes a point toward collapse;
- the smoothing raises the ρ the dependency tolerates, which pushes ρ\* away
  from collapse.

The anchor at `rl=840` came back **UNSAFE**, so the rate correction dominated
here. That does not disentangle them, and no attempt is made to: **any ρ\*
difference against the pre-EC2 corpus confounds machine, rate correction and
arrival process**, which is why §A3 already forbids that comparison outright.

**A caution against over-reading the smoothness.** Both processes are far
smoother than Poisson at every timescale measured — IDC 0.001 and 0.025 against
1.0. The difference between them is a difference between two nearly
deterministic generators, not between a smooth and a bursty one. It is recorded
because it exists and was asked for, not because there is evidence it moves ρ\*
at these magnitudes. Establishing that it does would need ρ\* measured under
deliberately varied arrival burstiness, which is an E2 question and is **not**
claimed here.

#### Consequence: rl-space comparison with the old corpus is invalid

**Comparisons against the pre-Aug-19 corpus in `rl` space are meaningless and are
not made.** The same nominal `rl` no longer denotes the same offered load,
because λ_L underneath it has moved by 3.3%. Only **achieved ρ** is comparable,
and even then only with the platform caveat in `NOTES.md` — which is to say, for
E1, not at all.

This is the same rule already stated for the platform change, arrived at
independently: the old last-SAFE values are search starting points, not
baselines.

#### The two terms of ρ are paced by different mechanisms

Stated explicitly because it belongs in the methods section and is easy to miss:

    ρ_achieved = ( λ_L_achieved + rl_achieved ) / C_d
                    ^^^^^^^^^^^^   ^^^^^^^^^^^
                    lanes          STILL THE TICKER

**Only the live injector moved.** The consumer's recovery rate limiter in
`consumer/main.go` is still a plain `time.NewTicker`, unchanged. The two terms
of ρ are therefore paced by different mechanisms with different error
characteristics: the injector now delivers ~99.98% of its target, while the
limiter under-delivers by an amount that **grows with rl** — measured on
2026-08-19 at 98.4% at rl=900 falling to 97.2% at rl=990.

**The asymmetry falls the wrong way round.** λ_L is the term held **fixed**
across an entire boundary search, and it is the one that now has the accurate
pacer. `rl` is the term being **bisected** — the only thing that varies, the
thing whose value the boundary *is* — and it is the one still on the
tick-dropping ticker. The instrument is precise on the axis that does not move
and imprecise on the axis being measured.

**The interval stays valid; the precision of the search does not follow for
free.** §5 requires achieved ρ to be measured per run from messages actually
acked, so the limiter's error is absorbed into the reported value rather than
propagated into it: an interval endpoint means what it says. What the error
costs is **search precision** — bisection decides which way to go from a
nominal `rl`, while the achieved ρ that nominal rate produces carries a
run-to-run error the search cannot see. Bisecting to 5 rps buys nothing if the
same nominal rate lands at different achieved ρ on different repetitions. That
is measured per point rather than assumed; see the spread diagnostic below.

Three things follow, and they are registered rather than fixed, because changing
the limiter now would move the instrument again mid-campaign:

1. Achieved ρ must be computed from **measured** delivered rates on both terms,
   which §5 already requires. The limiter's error is absorbed by measuring
   `rl_achieved` from messages acked, not from the flag.
2. The error is **not common-mode across the two terms**, so it does not cancel,
   and it is **rl-dependent**, so it is larger at the top of a sweep than at the
   bottom. A boundary located by bisection walks up in rl, which is the
   direction the limiter error grows.
3. Every boundary file records per-run `liveAchievedRps` and
   `recoveryAchievedRps` separately, so the two can be inspected rather than
   inferred.

#### Spread diagnostic — registered decision rule

For every probed point, the **spread of achieved ρ across its n repetitions** at
the same nominal `rl` is recorded, alongside the resolution the search claims:

    rho_resolution = RESOLUTION_RPS / C_d     (5 / 2000 = 0.0025 at C0;
                                               5 / 1400 = 0.0036 at C1)

**If the within-point spread exceeds that resolution, the 5 rps interval at that
point cannot be trusted** — the limiter's run-to-run noise is then larger than
the distance the search is trying to resolve, and the bisection is reading its
own jitter. Every such point is flagged in the boundary file
(`spreadExceedsResolution`) and named in the run log; the interval is still
reported, with the flag attached, rather than suppressed.

For scale: the injector's own ticker A/B spanned 96.42–96.80%, which is 0.0019
in ρ — already close to the 0.0025 threshold, and that was the *good* term.

**Decided in advance, so the outcome cannot pick the rule:**

- Flag fires on **more than two points across E1** → the consumer limiter moves
  to a deadline pacer before E2, and every affected boundary is re-run. The
  asymmetry is then a defect, not a caveat.
- Flag fires on **two or fewer** → the asymmetry is a methods paragraph and
  nothing more, and the intervals stand as reported.

Whether the limiter should also move to a deadline pacer is otherwise a question
for E2 and is **not** pre-judged here.
