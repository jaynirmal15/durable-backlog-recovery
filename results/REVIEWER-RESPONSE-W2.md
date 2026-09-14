# W2 — reviewer response: fit-vs-test separation, resolution, and the error model

**Offline analysis of committed data. No new runs, no instance.** Every claim
below names the artefact or commit it comes from. Where committed data cannot
answer a question, that is stated rather than inferred.

Regenerate with `python3 scripts/reviewer_w2_analysis.py`; full output in
`results/W2-reviewer-analysis.json`.

---

# Task 1 — is the predict-and-eliminate result out-of-sample?

**Short answer: partly, and the part that matters is.** The constant used to
*choose* the intervention was estimated in-sample. The constant used to *predict*
the outcome was measured by a different instrument on runs that are not part of
the test, and the prediction it produced was **not** the value that a naive
"subtract what you measured" argument would give.

## 1.1 Which runs produced the 0.463 ms constant

`0.463` is the **median of seven per-cell estimates** produced by
`scripts/capacity_calibration.py` and recorded in
`results/E2D-capacity-calibration.json` (commit `6036293`, 2026-09-13 11:57:35
-0400).

It is derived **from the saturation plateau**, not from in-situ probing and not
from a separate calibration cell. For each cell the script takes the maximum
30-second sustained served rate at that cell's UNSAFE points, from the
downstream's own cumulative `served` counter, and inverts the capacity model:

```
ov = S * (C_d / plateau - 1)          scripts/capacity_calibration.py:164
```

| cell | S | C_d | UNSAFE runs | plateau | implied ov |
|---|---:|---:|---:|---:|---:|
| E1 c10/C0 | 5 | 2000 | 6 | 1828.6 | 0.469 |
| E1 c10/C1 | 5 | 1400 | 6 | 1280.9 | 0.465 |
| E1 c50/C0 | 25 | 2000 | 6 | 1964.3 | 0.454 |
| E1 c50/C1 | 25 | 1400 | 6 | 1375.7 | 0.441 |
| E2 c10@Q2500 | 5 | 2000 | 15 | 1827.1 | 0.473 |
| E2 c50@Q500 | 25 | 2000 | 15 | 1964.8 | 0.447 |
| E2b C=400 | 25 | 400 | 6 | 392.7 | **0.463** |

Median = **0.4630**. It is the exact median of the seven, not a rounded value;
it coincides with the E2b cell's own estimate.

## 1.2 Reconciling 0.463 with the measured 0.5165 and 0.5114

These are **three different measurements of the same physical cost, by two
instruments under three load conditions**. None is a subset attribution of
another, and 0.463 is not a rounded version of either.

| value | instrument | load | source |
|---:|---|---|---|
| **0.463 ms** | throughput residual: `S*(C/plateau-1)` | saturated, campaign workload (NATS consumer and injector both running) | `results/E2D-capacity-calibration.json` |
| **0.4947 / 0.4914 ms** | per-request wall clock on the worker path | saturated, isolated closed-loop driver | `results/e2e/exp1-s5-sat-on.json`, `exp1-s25-sat-on.json` |
| **0.5165 / 0.5114 ms** | same probe | 90% of capacity, isolated open-loop driver | `results/e2e/exp1-s5-load90.json`, `exp1-s25-load90.json` |

Two facts settle the "subset attribution" question:

- **It is not the sleep-overshoot component alone.** At saturation the probe
  reports sleep overshoot of 0.4935 ms for c10, against a total of 0.4947.
  0.463 matches neither.
- **The applied correction is smaller than the direct measurement because the
  two were taken under different workloads.** The probe figure rises as load
  falls: 0.4947 saturated against 0.5165 at 90%. The plateau-derived figure is
  lower again, and E2e recorded the in-situ drain value lower still, at 0.4775
  (`results/E2E-analysis.json`). The ordering is consistent, spans 0.463 to
  0.517, and **the paper should not present any single value as "the" overhead
  without naming its load condition.**

**This is a real caveat and is flagged rather than smoothed:** the reported
constant 0.463 is the lowest of four measurements of the same quantity, and it
is the one that happens to make the correction land on exactly 2000.

## 1.3 Were the predicted plateaus computed for held-out cells?

**No cell was held out from the estimation of 0.463.** All seven E2d cells fed
the median, and they include `E1 c10/C0` and `E1 c50/C0`, which are the
uncorrected counterparts of the two cells later corrected and re-measured. Per
arm:

| arm | corrected cell | contributed to the 0.463 median? |
|---|---|---|
| c10 | S=4.537 ms, conc 10, C=2000, C0 | **yes** — via E1 c10/C0, E1 c10/C1 and E2 c10@Q2500 |
| c50 | S=24.537 ms, conc 50, C=2000, C0 | **yes** — via E1 c50/C0, E1 c50/C1, E2 c50@Q500 and E2b |

**But the predicted plateaus 1987.4 and 1997.7 were not computed from 0.463.**
They come from the *probe* constants measured in E2e experiment 1:

```
c10:  10 / ((4.537 + 0.4947) ms)  = 1987.4
c50:  50 / ((24.537 + 0.4914) ms) = 1997.7
```

Had 0.463 been used, the prediction would have been **exactly 2000.0 in both
arms**. It was not. This matters directly to the reviewer's objection: the test
was not "we subtracted an offset and recovered the round number we subtracted to".
The registered prediction was a specific non-round value, from a second
instrument, and the measurement returned 1987.4 and 1998.1 — errors of −0.00% and
+0.02% (`results/E2E-analysis.json`).

The experiment-1 runs that produced 0.4947 and 0.4914 were made at the
**uncorrected** sleep of 5000 and 25000 µs. They are separate runs from the
corrected-cell measurement, so the prediction is out-of-sample with respect to
the runs that tested it, though not with respect to the arm or the machine.

## 1.4 Where the prediction was registered, and whether it predates the runs

| event | commit | timestamp |
|---|---|---|
| 0.463 established (E2d) | `6036293` | 2026-09-13 15:57:35 UTC |
| probe constants measured (E2e exp 1) | `af98ca2` | 2026-09-13 16:47:47 UTC |
| **plateaus 1987.4 / 1997.7 registered** (E2E-PLAN addendum 1) | **`67c448b`** | **2026-09-13 17:31:47 UTC** |
| first corrected-cell run | — | 2026-09-13 18:10:27 UTC (`results/e2e/e2e-c10-c0-rl975-r1.json`, `startedAt`) |

**The registration predates the first corrected run by 39 minutes.** The
corrected-cell plateau measurement sits between the two: the campaign log records
the c10 gate at 18:07:30 UTC, before the first boundary run at 18:10:27 and after
the 17:31:47 registration. That log is on the instance and is **not** a committed
artefact; the committed bound is the run record's own `startedAt`.

## 1.5 Can a leave-one-out test be built from committed data?

**Yes, and it needs no new runs.** The seven E2d cells span two service times
(5, 25 ms), three configured capacities (400, 1400, 2000) and two queue caps.
For each cell in turn: take the median implied `ov` of the other six, predict
that cell's plateau as `C_d * S / (S + ov)`, and compare with its measured
plateau. Nothing is retuned.

- **Data needed:** `results/E2D-capacity-calibration.json` only, which already
  carries per-cell plateau, S, C_d and run counts.
- **Cells:** all seven, each held out once.
- **Cost:** arithmetic on seven numbers. Seconds of CPU, no instance, no runs.
- **What it would and would not show:** it tests whether the constant
  generalises *across cells of the existing corpus*. It does **not** test the
  corrected configuration, because no corrected cell was measured at a held-out
  service time — both corrected arms use service times whose uncorrected
  counterparts fed the estimate.

Not run, per the brief.

---

# Task 2 — boundary resolution and uncertainty

```
TASK 2 — resolution table
==============================================================================
cell            C_cfg    C_true   step step/C_true interval (rl)  width/C_true    n repl spread
E1 c10/C0        2000    1828.6      5    0.00273  [ 825,  830]      0.00273   15     0.00010
E1 c10/C1        1400    1280.9      5    0.00390  [ 275,  280]      0.00390    3     0.00000
E1 c50/C0        2000    1964.3      5    0.00255  [ 975,  980]      0.00255   15     0.00060
E1 c50/C1        1400    1375.7      5    0.00363  [ 370,  375]      0.00363    3     0.00000
E2 c10@Q2500     2000    1827.1      5    0.00274  [ 825,  830]      0.00274   12     0.00010
E2 c50@Q500      2000    1964.8      5    0.00254  [ 975,  980]      0.00254   12     0.00060
E2b C=400         400     392.7      5    0.01273  [ 190,  195]      0.01273   12     0.00000

==============================================================================
```

`step as fraction of C_true` is one 5 rps bisection step divided by that cell's
measured true capacity, from `results/E2D-capacity-calibration.json`. Replicate
spread is the range of A4 achieved utilisation across replicates at the last SAFE
point.

## 2.1 Residual spread against per-cell resolution

```
2.1 — is the 0.0068 residual spread above or below per-cell resolution?
==============================================================================
post-A6 residual spread in effective utilisation: 0.0068
  (source: results/A6-collapsed-estimator.json, last SAFE point per cell)

cell             resolution   spread/res    verdict
E1 c10/C0           0.00273         2.50 resolvable
E1 c10/C1           0.00390         1.75 resolvable
E1 c50/C0           0.00255         2.68 resolvable
E1 c50/C1           0.00363         1.88 resolvable
E2 c10@Q2500        0.00274         2.49 resolvable
E2 c50@Q500         0.00254         2.68 resolvable
E2b C=400           0.01273         0.54 BELOW resolution

coarsest resolution: 0.01273 (E2b C=400)
finest   resolution: 0.00254 (E2 c50@Q500)
aggregate: the spread is 0.54x the coarsest and 2.68x the finest step.

==============================================================================
```

The spread exceeds the resolution in six cells, at 1.75x to 2.68x, and falls
**below** it in E2b, at 0.54x. E2b is the cell that defines the low end of the
spread, so the comparison that matters is the one that fails.

## 2.2 Distinguishability of the endpoints

```
2.2 — are the endpoints distinguishable?
==============================================================================
extremes: E2b C=400 at 0.9931 and E1 c50/C0 at 0.9999

0.9999 vs 1.0000: difference 0.00005, against E1 c50/C0 resolution 0.00255 -> NOT distinguishable
0.9931 vs 0.9999: difference 0.00682, against the coarser of the two resolutions 0.01273 (E2b C=400) -> NOT distinguishable
  the same difference against the finer resolution 0.00255 would be 2.68 steps

==============================================================================
```

Pairwise across all 21 cell pairs, using the coarser resolution of each pair as
the limit: **4 of 21 pairs are distinguishable.** All four exceed their limit by
only 1.11x to 1.17x, and every one is a C0-versus-C1 comparison:

| pair | difference | limit | steps |
|---|---:|---:|---:|
| E1 c10/C1 vs E1 c50/C0 | 0.00456 | 0.00390 | 1.17 |
| E1 c10/C1 vs E2 c50@Q500 | 0.00450 | 0.00390 | 1.15 |
| E1 c50/C0 vs E1 c50/C1 | 0.00409 | 0.00363 | 1.13 |
| E1 c50/C1 vs E2 c50@Q500 | 0.00404 | 0.00363 | 1.11 |
Excluding E2b, the remaining six cells span 0.00456, which is 1.17 to 1.79 steps.

## 2.3 Replicate spread at the n=12 points

```
2.3 — run-to-run spread at the n=12 points, in bisection-step units
==============================================================================
point                      n      rho min      rho max     spread  spread/step
E1 c10/C0 rl=825          15       0.9124       0.9125    0.00010         0.04
E1 c50/C0 rl=975          15       0.9817       0.9823    0.00060         0.24
E2 c10@Q2500 rl=825       12       0.9124       0.9125    0.00010         0.04
E2 c50@Q500 rl=975        12       0.9820       0.9826    0.00060         0.24
E2b C=400 rl=190          12       0.9750       0.9750    0.00000         0.00

replicate spread is 0% to 24% of one bisection step.
so the dominant uncertainty is the step, not run-to-run variation.

==============================================================================
```

**Run-to-run variation is not the limiting uncertainty.** At worst it is 24% of
one bisection step; at three of five points it is under 5%. The step size
dominates by roughly a factor of four.

## 2.4 Boundary movement across the tenfold SLO range

```
2.4 — boundary movement across the tenfold SLO range
==============================================================================
cell           tightest well-posed          loosest                       move (rl)   in steps
E1 c10/C0      50 ms: rl [820, 825]         500 ms: rl [830, 840]                10        2.0
E1 c10/C1      50 ms: rl [275, 280]         500 ms: rl [275, 280]                 0        0.0
E1 c50/C0      100 ms: rl [970, 975]        500 ms: rl [980, 990]                10        2.0
E1 c50/C1      100 ms: rl [370, 375]        500 ms: rl [375, 380]                 5        1.0
E2 c10@Q2500   100 ms: rl [825, 830]        500 ms: rl [830, 835]                 5        1.0
E2 c50@Q500    250 ms: rl [975, 980]        500 ms: rl [980, 990]                 5        1.0
E2b C=400      100 ms: rl [190, 195]        500 ms: rl [190, 195]                 0        0.0

maximum movement 10 rps = 2.0 bisection steps (E1 c10/C0)

==============================================================================
```

Expressed in the same units as the residual spread, the largest SLO-induced
movement is 10 rps at E1 c10/C0, which is **0.00547** of that cell's true
capacity. The residual spread across cells is **0.00682**, only **1.25x** as
large.

## 2.5 Which statement the data supports

**(a), with one stated exception.** The evidence:

1. The two cells defining the spread — E2b at 0.9931 and E1 c50/C0 at 0.9999 —
   are **not** distinguishable: their difference of 0.00682 is smaller than
   E2b's own resolution of 0.01273.
2. **17 of 21 pairs are indistinguishable.** The four that are not exceed their
   limit by 11% to 17%, which is one step and a sixth at best.
3. 0.9999 is **not** distinguishable from 1.0000: the difference is 0.00005
   against a resolution of 0.00255, a fiftieth of a step.
4. The whole residual is only 1.25x the movement produced by changing an
   arbitrary methodological parameter — the SLO threshold — over a tenfold range.

Statement (b), "reduced by a factor of 10.5 but remains resolvable", is **not
supported as written**. Four marginal pairs at 1.1 steps is not a resolvable
residual, and the pair that defines the quoted 0.0068 is the least resolvable of
all.

**The exception that should be reported rather than buried:** all four
distinguishable pairs are C0-versus-C1, with the reduced-capacity cells sitting
below the full-capacity ones (0.9954 and 0.9959 against 0.9999). That is a
consistent direction across an independent pairing, and at 1.1 steps it is at
the edge of what this instrument can assert. It is a candidate finding for a
future experiment at finer resolution, not a claim this data establishes.

---

# Task 3 — error model check

```
TASK 3 — error model
==============================================================================
S_actual = S_configured + delta;  C_actual = concurrency / S_actual
capacity overstatement = delta / S_configured,  delta = 0.463 ms

  delta/S at S= 5 ms = 9.2600%  (paper states 9.30%)  DIFFERS
  delta/S at S=25 ms = 1.8520%  (paper states 1.85%)  matches

cell               S  conc  C_cfg     model C    measured     error verdict
E1 c10/C0          5    10   2000      1830.5      1828.6    -0.10% ok
E1 c10/C1          5     7   1400      1281.3      1280.9    -0.03% ok
E1 c50/C0         25    50   2000      1963.6      1964.3    +0.03% ok
E1 c50/C1         25    35   1400      1374.5      1375.7    +0.08% ok
E2 c10@Q2500       5    10   2000      1830.5      1827.1    -0.19% ok
E2 c50@Q500       25    50   2000      1963.6      1964.8    +0.06% ok
E2b C=400         25    10    400       392.7       392.7    -0.01% ok

every cell matches concurrency/(S+delta) within 0.5%.
```

## Verdict

- `C_actual = concurrency / (S + delta)` reproduces every measured plateau to
  within **0.19%**, well inside the 0.5% tolerance. **No cell fails.**
- `delta / S` at S=25 ms gives 1.852%, matching the stated 1.85%.
- **`delta / S` at S=5 ms gives 9.260%, not 9.30%.** With delta = 0.463 the
  correct figure is **9.26%**. 9.3% would require delta = 0.465. This is a
  rounding discrepancy in the paper's stated value, flagged and not silently
  corrected. Either state 9.26% with delta = 0.463, or state the delta that
  produces 9.3%.

Note that concurrency is `ceil(C*S)`, so the C1 cells use 7 and 35 workers rather
than a scaled 10 and 50; the model above uses the integer value, which is what
the downstream actually runs.

---

# Summary of what a reviewer should be told

1. The correction constant is **in-sample**: no cell was held out, and both
   corrected arms had their uncorrected counterparts in the estimate.
2. The **prediction** that was tested used a different constant from a different
   instrument, and predicted 1987.4 and 1997.7 rather than the round 2000 that
   the correction alone implies. That is the substance of the out-of-sample
   claim, and it holds.
3. A leave-one-out test across the seven cells is possible from committed data
   at negligible cost and has not been run.
4. The seven corrected boundaries are **identical to within the experiment's
   resolution**, with a marginal C0-versus-C1 offset at 1.1 steps that should be
   reported as unresolved rather than as a result.
5. Four decimal places are not warranted. **0.9999 is not distinguishable from
   1.0000**, and the honest precision is roughly two decimal places in effective
   utilisation, or one bisection step in rate.
6. One arithmetic correction: 9.26%, not 9.3%.
