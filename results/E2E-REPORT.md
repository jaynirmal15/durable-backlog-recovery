# E2e — observing the overhead, then eliminating it

**Two experiments.** Registered in `results/E2E-PLAN.md` before any code change, with four addenda, two of which correct my own errors mid-campaign.

This is the first cell not run on the pinned harness `026be6242d26`. It needed instrumentation that does not exist there and a sub-millisecond service time the code could not express. Every change is additive and defaults to the pinned behaviour, no earlier cell was re-run, and any comparison with E1 crosses commits.

## Experiment 1 — the overhead is real, constant, and sleep overshoot

| | S = 5 ms | S = 25 ms |
|---|---:|---:|
| mean excess at 90% of capacity | 0.5165 ms | 0.5114 ms |
| mean excess at saturation | 0.4947 ms | 0.4914 ms |
| mean excess in situ, during a drain | 0.4775 ms | 0.4746 ms |

The registered contrast is settled. A constant cost predicts `excess(25) - excess(5) = 0`; a proportional one predicts a ratio of 5. Measured: **-0.0051 ms**, a ratio of **0.990**. The cost does not scale with service time.

**It is almost entirely `time.Sleep` overshoot** — 99.8% of the total. The runtime timer work, the queue and slot bookkeeping and the done-channel send come to 1.3 microseconds between them.

**Probe control**, registered in advance because the instrumentation could distort the throughput it explains: the saturation plateau moves 0.04% at S=5 and 0.09% at S=25 between probe on and probe off, against a 0.5% criterion. It does not perturb.

## Experiment 2 — correcting the sleep

Sleep reduced by 0.463 ms with concurrency held fixed, so integer rounding of `ceil(C x S)` cannot blur the prediction.

### The plateau gate

| arm | sleep | concurrency | predicted capacity | measured | error |
|---|---:|---:|---:|---:|---:|
| c10 | 4.537 ms | 10 | 1987.4 | **1987.4** | -0.00% |
| c50 | 24.537 ms | 50 | 1997.7 | **1998.1** | +0.02% |

**Both gates pass essentially exactly.** Correcting by a single constant produces the predicted capacity at two service times five times apart. That confirms the additive model independently of where the boundaries land.

### Every probe

#### c10

| rl | n | achieved | rho | queue peak | live p99 | cycle | vSLO | class |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 975 | 3 | 1948.5 | 0.974 | 7 | 8 ms | 5.0140 ms | 0.000, 0.000, 0.000 | SAFE |
| 1075 | 3 | 1967.0 | 0.984 | 18 | 14 ms | 5.0174 ms | 0.000, 0.000, 0.000 | SAFE |
| 1185 | 3 | 1976.7 | 0.988 | 111 | 58 ms | 5.0132 ms | 0.000, 0.000, 0.000 | SAFE |
| 1240 | 3 | 1984.8 | 0.992 | 500 | 508 ms | 5.0125 ms | 0.518, 0.511, 0.467 | UNSAFE |
| 1290 | 3 | 1986.0 | 0.993 | 500 | 1033 ms | 5.0128 ms | 0.763, 0.765, 0.770 | UNSAFE |
| 1400 | 3 | 1988.2 | 0.994 | 500 | 1036 ms | 5.0128 ms | 0.712, 0.742, 0.746 | UNSAFE |

Bracket rl [1185, 1240], 55 rps — coarser than the registered 5. In rho: **[0.988, 0.992]**, width 0.004.

| prediction | rho* | inside the bracket? |
|---|---:|---|
| saturated (registered) | 0.9937 | no, -1.4 steps from the midpoint |
| 90% load | 0.9894 | **yes** |
| in situ | 0.9974 | no, -2.8 steps from the midpoint |
| measured ceiling | 0.9937 | no, -1.4 steps from the midpoint |

#### c50

| rl | n | achieved | rho | queue peak | live p99 | cycle | vSLO | class |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 975 | 3 | 1946.5 | 0.973 | 8 | 34 ms | 25.0269 ms | 0.000, 0.000, 0.000 | SAFE |
| 1150 | 3 | 1975.9 | 0.988 | 107 | 80 ms | 25.0149 ms | 0.000, 0.000, 0.000 | SAFE |
| 1210 | 3 | 1983.1 | 0.992 | 363 | 207 ms | 25.0092 ms | 0.000, 0.000, 0.000 | SAFE |
| 1275 | 3 | 1988.8 | 0.994 | 1480 | 761 ms | 25.0040 ms | 0.674, 0.672, 0.704 | UNSAFE |
| 1400 | 3 | 1991.0 | 0.996 | 1998 | 1028 ms | 25.0083 ms | 0.719, 0.705, 0.729 | UNSAFE |

Bracket rl [1210, 1275], 65 rps — coarser than the registered 5. In rho: **[0.992, 0.994]**, width 0.003.

| prediction | rho* | inside the bracket? |
|---|---:|---|
| saturated (registered) | 0.9989 | no, -2.4 steps from the midpoint |
| 90% load | 0.9981 | no, -2.1 steps from the midpoint |
| in situ | 0.9996 | no, -2.7 steps from the midpoint |
| measured ceiling | 0.9991 | no, -2.5 steps from the midpoint |

### The gap between the arms

> **CORRECTED, 2026-09-14. The pair below is withdrawn; use the matched accounting that follows it.** The table as first published read *"uncorrected, E1 midpoints 0.9137 and 0.9826 | 0.0706"*. **Those two midpoints differ by 0.0689, not 0.0706.** The 0.0706 is E2d's `rhoStarSpread` — the RANGE of rho* interval midpoints across all **seven** cells (`capacity_calibration.py:221`) — and it was being labelled here as a two-arm difference. It was also being differenced against a corrected residual computed on a different estimator, a different aggregator and a different observation interval, so the before and after were not the same quantity. See `results/METHOD-AUDIT.md` item 19. (This notice was first dated 2026-09-15, from a UTC-offset clock; the date is corrected and nothing else in it changed — METHOD-AUDIT item 31.)

**Withdrawn pair** — retained so the correction is legible, not for quotation:

| | |
|---|---:|
| ~~uncorrected, E1 midpoints 0.9137 and 0.9826~~ | ~~0.0706~~ |
| predicted residual (registered) | 0.0052 |
| ~~measured residual~~ | ~~0.003~~ |
| ~~fraction of the gap removed~~ | ~~96.3%~~ |

**Matched accounting.** Each recipe applied identically to both corpora: last SAFE point, drain-window, median, C=2000, c10 vs c50, C0; and the same against the delivery-span estimator. Generated by `scripts/effect_size_accounting.py`.

| | uncorrected | corrected | removed |
|---|---:|---:|---:|
| inter-arm gap, in rho | 0.0670 | 0.0032 | **95%** |
| inter-arm gap, in throughput (rps) | 134.0 | 6.4 | **95%** |
| the same, under A4 on both sides | 0.0696 | 0.0043 | **94%** |

**The matched answer is estimator-dependent: 94% to 95%.** Both rows are matched; the withdrawn 96.3% was not. The A4 route carries one caveat the drain-window route does not — the corrected side stores one value per point, so its aggregator is not recorded and cannot be matched to the median used on the uncorrected side.

The two rows agree because the denominator is the same constant on both sides; the throughput row is the one free of any utilisation estimator. The rho row is given to four decimals because an inter-arm gap is a difference between two cells, not a utilisation at one cell's resolution, and the resolution-matched rule of section IV covers the latter. The registered prediction was 0.0052 and 92.7% removed, so the correction removed somewhat more of the gap than registered under either estimator, not less.

Both estimators are available on both sides. The drain-window values are retained for every point of both corpora; the delivery-span values are retained in the boundary files for E1, E2 and E2b and in `results/E2E-a4.json` for the corrected cells. Neither set can be re-derived from raw data, because the consumer traces the delivery-span estimator reads are excluded from the repository corpus-wide. The routes are reported side by side rather than one being chosen.

Bracket midpoints: c10 0.990, c50 0.993.

## The estimator disagreement is as large as the effect

The brackets above use the **as-measured** (drain-window) estimator. The registered estimator is **A4**, the delivery-span one used by every earlier campaign. Applying A4 moves both brackets up by about 0.008 and **inverts the c10 verdict**:

| arm | estimator | bracket | candidate inside |
|---|---|---|---|
| c10 | as-measured | [0.988, 0.992] | 90% load, 0.9894 (registered) |
| c10 | **A4**&nbsp;[^a4] | **[0.9956, 1.0016]** | **in situ, 0.9974 (registered)** |
| c50 | as-measured | [0.992, 0.994] | none |
| c50 | **A4**&nbsp;[^a4] | **[0.9999, 1.0064]** | none |

[^a4]: **Provenance.** The A4 rows are computed from `results/E2E-a4.json`, which retains the per-point delivery-span utilisation for these cells; the brackets above are its last SAFE and first UNSAFE points. They are **retained measurements, not re-derivable ones**: A4 needs per-arrival timestamps from the consumer trace, the one-second `timeline` cannot supply them, and consumer traces are excluded from the repository corpus-wide (`.gitignore`: `*.jsonl`, `*.jsonl.*`). That is true of every A4 value in every campaign — E1, E2 and E2b preserve theirs inside their boundary files, and E2e, which has no boundary file, preserves its own here. Of the traces still on disk, none survives at the c10 arm's last SAFE point (rl=1185); in the c50 arm two of three repetitions survive at each endpoint and recomputing from those gives [1.0006, 1.0076] against the [0.9999, 1.0064] retained here, a difference consistent with the missing third repetition. `results/E2E-a4.json` is written by no script in this repository and read by nothing else; it is an orphan artefact of the campaign.

The two estimators differ by 0.0080 in rho. The candidates span 0.0080 in the c10 arm. **The measurement uncertainty is the same size as the thing being discriminated, so this campaign cannot say which overhead governs the boundary.** That is forced by the data, not chosen.

A4 is specifically suspect at the non-SAFE points: its values there exceed each cell's own measured saturation plateau, by +0.0079 in c10 and +0.0073 in c50, and nothing sustains more than its plateau. A4 measures recovery over the span the traffic occupied, which on a collapsed run excludes stalled intervals and overstates the rate. It was built to remove the drain-tail bias at SAFE points, was never validated on collapsed runs, and this is the first campaign whose interval endpoints depend on it there. The as-measured estimator carries the opposite bias, and each cell's measured plateau sits between the two brackets.

### What survives regardless of estimator

1. **The plateau gates**, above: direct throughput, no rho estimator involved, errors of -0.00% and +0.02%. The additive model is confirmed by these alone.
2. **The gap between the arms is essentially eliminated**: 0.0026 as-measured, 0.0045 under A4, against 0.0706 uncorrected. **94% to 96% removed** either way, bracketing the registered 92.7%.
3. **Both arms land within about 0.008 of 1.000**, the brief's original prediction before addendum 1 refined it.

### What does not survive

The addendum-1 refinement, that the correction under-corrects and gives 0.9937 and 0.9989 specifically, **cannot be tested here**. Under A4 both arms sit above those values, under as-measured both sit below, and the distance between the candidates is smaller than the estimator spread.

## The three overhead measurements disagree, and none reliably predicts

The in-situ figure is the lowest and the most stable — about 0.478 ms in c10 and 0.474 in c50, holding across every probed rate. It was the better instrument in principle, measured under the campaign's own bursty arrival process rather than a smooth driver. **It is also the wrong predictor**: it puts the boundary above where both arms actually broke.

That is worth stating rather than burying, because the reasoning that motivated in-situ measurement was sound and the result still went against it.

## Two corrections I made mid-campaign

Both are in `E2E-PLAN.md` with the reasoning that produced them.

**Addendum 2 claimed the bisection could not terminate**, on the argument that achieved rho is bounded by capacity and the prediction puts the boundary at that ceiling. Wrong, and wrong on evidence I already had: by rl=1185 the queue had gone 7, 18, 111 and live p99 8, 14, 58 ms. I read two flat points as an asymptote. The upward walk would have found the boundary one or two probes later.

**Addendum 3 then announced that the saturated figure governs and the 90%-load figure was excluded.** Also wrong: the bracket contained both. I compared the single UNSAFE point against one candidate and ignored that the bracket's lower end sat below the other. Corrected in addendum 4 **before** the deciding probe ran, with the reading fixed in advance.

