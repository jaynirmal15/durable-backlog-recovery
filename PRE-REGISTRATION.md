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
