# E2c — does rho* track absolute service time, or S/SLO?

**Analysis only. No new runs.** Recomputes vSLO for every archived run at SLO thresholds of 50, 100, 250 and 500 ms, re-classifies each probed point under the unchanged SAFE/UNSAFE/MARGINAL rules, and re-locates each boundary.

## Answer

**The cells do not collapse against S/SLO. rho\* tracks absolute service time.** Grouping the well-posed cells by absolute S accounts for **99.7%** of the variance in rho\*; grouping by S/SLO accounts for **24.6%**.

| grouping | residual SD of rho* | variance explained |
|---|---:|---:|
| absolute S (milliseconds) | 0.002 | 99.7% |
| S/SLO (ratio) | 0.030 | 24.6% |
| _(ungrouped total)_ | 0.034 | |

Per the brief, that is the second outcome: **the effect is tied to milliseconds** and needs a mechanism or a threats paragraph. It is not the generalisable S/SLO statement.

## The discriminating comparison

Only two S/SLO values are populated by **both** arms. Those are the only groups that can test the hypothesis at all; the other three contain a single arm each and would collapse under any hypothesis.

| S/SLO | cells | rho* range | spread | discriminating? |
|---:|---:|---|---:|---|
| 0.010 | 3 | 0.912 - 0.917 | **0.005** | no, S=5 only |
| 0.020 | 3 | 0.912 - 0.914 | **0.001** | no, S=5 only |
| 0.050 | 7 | 0.911 - 0.985 | **0.074** | **yes, both arms** |
| 0.100 | 6 | 0.911 - 0.983 | **0.072** | **yes, both arms** |
| 0.250 | 3 | 0.980 - 0.981 | **0.001** | no, S=25 only |

At both discriminating ratios the spread is about **0.07**, which is the entire separation between the arms. Matching S/SLO does nothing to bring the cells together.

The converse holds sharply. Within an arm, rho\* barely moves across a tenfold change in the SLO:

| S | well-posed cells | rho* range | spread across a 10x SLO change |
|---:|---:|---|---:|
| 5 ms | 11 | 0.911 - 0.917 | **0.006** |
| 25 ms | 11 | 0.980 - 0.985 | **0.004** |

## Why the SLO has so little leverage

The transition is a cliff, not a slope. vSLO at the last SAFE point and at the first non-SAFE point, one 5 rps step apart, at the original 250 ms:

| cell | last SAFE | vSLO | first non-SAFE | vSLO |
|---|---:|---|---:|---|
| E1 c10/C0 | 825 | 0.000, 0.000, 0.000 | 830 | 0.077, 0.000, 0.136 |
| E1 c10/C1 | 275 | 0.000, 0.000, 0.000 | 280 | 0.630, 0.494, 0.734 |
| E1 c50/C0 | 975 | 0.000, 0.000, 0.000 | 980 | 0.250, 0.102, 0.267 |
| E1 c50/C1 | 370 | 0.000, 0.000, 0.000 | 375 | 0.097, 0.297, 0.236 |
| E2 c10@Q2500 | 825 | 0.000, 0.000, 0.000 | 830 | 0.255, 0.325, 0.263 |
| E2 c50@Q500 | 975 | 0.000, 0.000, 0.000 | 980 | 0.248, 0.221, 0.140 |
| E2b C=400 | 190 | 0.000, 0.000, 0.000 | 195 | 0.701, 0.667, 0.681 |

Every cell goes from exactly zero violating seconds to a large fraction in one step. A threshold change moves the cliff by at most a step or two, which is why rho\* is nearly invariant to the SLO and why the ratio has no purchase.

## Well-posedness

Rule fixed before the sweep: a (cell, threshold) pair is well-posed only if the healthy baseline live p99 is at most **half** the threshold. Below that margin the SLO is a question about idle latency, not about recovery headroom.

Baseline measured in the settled window **after** T_full, not inside the healthy streak. The streak is defined by p99 <= SLO, so any statistic taken inside it is conditioned on the threshold under test.

| cell | S | baseline p99 | 50 ms | 100 ms | 250 ms | 500 ms |
|---|---:|---:|---|---|---|---|
| E1 c10/C0 | 5 | 7 ms | 14% ok | 7% ok | 3% ok | 1% ok |
| E1 c10/C1 | 5 | 7 ms | 14% ok | 7% ok | 3% ok | 1% ok |
| E1 c50/C0 | 25 | 34 ms | 68% **dropped** | 34% ok | 14% ok | 7% ok |
| E1 c50/C1 | 25 | 34 ms | 68% **dropped** | 34% ok | 14% ok | 7% ok |
| E2 c10@Q2500 | 5 | 7 ms | 14% ok | 7% ok | 3% ok | 1% ok |
| E2 c50@Q500 | 25 | 34 ms | 68% **dropped** | 34% ok | 14% ok | 7% ok |
| E2b C=400 | 25 | 34 ms | 68% **dropped** | 34% ok | 14% ok | 7% ok |

**Dropped: 4 pairs, all of them the S=25 ms cells at 50 ms.** Their healthy baseline is 34 ms, 68% of the threshold, so a healthy idle system already sits most of the way to violating. The S=5 ms cells have a 7 ms baseline and are well-posed everywhere, exactly as the brief anticipated.

## Every (cell, threshold): bracketed, or what to run

| cell | SLO | S/SLO | well-posed | bracket rl | width | rho* interval | mid |
|---|---:|---:|---|---|---:|---|---:|
| E1 c10/C0 | 50 | 0.100 | yes | 820-825 | 5 | [0.910, 0.912] | 0.911 |
| E1 c10/C0 | 100 | 0.050 | yes | 820-825 | 5 | [0.910, 0.912] | 0.911 |
| E1 c10/C0 | 250 | 0.020 | yes | 825-830 | 5 | [0.912, 0.915] | 0.914 |
| E1 c10/C0 | 500 | 0.010 | yes | 830-840 | 10 **coarse** | [0.915, 0.920] | 0.917 |
| E1 c10/C1 | 50 | 0.100 | yes | 275-280 | 5 | [0.911, 0.914] | 0.912 |
| E1 c10/C1 | 100 | 0.050 | yes | 275-280 | 5 | [0.911, 0.914] | 0.912 |
| E1 c10/C1 | 250 | 0.020 | yes | 275-280 | 5 | [0.911, 0.914] | 0.912 |
| E1 c10/C1 | 500 | 0.010 | yes | 275-280 | 5 | [0.911, 0.914] | 0.912 |
| E1 c50/C0 | 50 | 0.500 | **dropped** | | | | |
| E1 c50/C0 | 100 | 0.250 | yes | 970-975 | 5 | [0.980, 0.982] | 0.981 |
| E1 c50/C0 | 250 | 0.100 | yes | 975-980 | 5 | [0.982, 0.984] | 0.983 |
| E1 c50/C0 | 500 | 0.050 | yes | 980-990 | 10 **coarse** | [0.983, 0.986] | 0.985 |
| E1 c50/C1 | 50 | 0.500 | **dropped** | | | | |
| E1 c50/C1 | 100 | 0.250 | yes | 370-375 | 5 | [0.979, 0.982] | 0.980 |
| E1 c50/C1 | 250 | 0.100 | yes | 370-375 | 5 | [0.979, 0.982] | 0.980 |
| E1 c50/C1 | 500 | 0.050 | yes | 375-380 | 5 | [0.982, 0.986] | 0.984 |
| E2 c10@Q2500 | 50 | 0.100 | yes | **not bracketed** | | every probed point is non-SAFE | |
| E2 c10@Q2500 | 100 | 0.050 | yes | 825-830 | 5 | [0.912, 0.915] | 0.914 |
| E2 c10@Q2500 | 250 | 0.020 | yes | 825-830 | 5 | [0.912, 0.915] | 0.914 |
| E2 c10@Q2500 | 500 | 0.010 | yes | 830-835 | 5 | [0.915, 0.917] | 0.916 |
| E2 c50@Q500 | 50 | 0.500 | **dropped** | | | | |
| E2 c50@Q500 | 100 | 0.250 | yes | **not bracketed** | | every probed point is non-SAFE | |
| E2 c50@Q500 | 250 | 0.100 | yes | 975-980 | 5 | [0.982, 0.984] | 0.983 |
| E2 c50@Q500 | 500 | 0.050 | yes | 980-990 | 10 **coarse** | [0.984, 0.986] | 0.985 |
| E2b C=400 | 50 | 0.500 | **dropped** | | | | |
| E2b C=400 | 100 | 0.250 | yes | 190-195 | 5 | [0.97, 0.99] | 0.98 |
| E2b C=400 | 250 | 0.100 | yes | 190-195 | 5 | [0.97, 0.99] | 0.98 |
| E2b C=400 | 500 | 0.050 | yes | 190-195 | 5 | [0.97, 0.99] | 0.98 |

### Not bracketed by existing probes — the targeted runs that would fix it

| cell | SLO | direction | rl values to probe | runs |
|---|---:|---|---|---:|
| E2 c10@Q2500 | 50 | below rl=825 | **820, 815, 810** | 9 |
| E2 c50@Q500 | 100 | below rl=975 | **970, 965, 960** | 9 |

18 cheap runs in total, on the registered 5 rps grid. Not a new campaign: each is the same condition already provisioned, at a lower rate.

### Brackets coarser than the registered 5 rps

The probed rates are whatever each bisection happened to visit, so a boundary that moves under a new threshold can land between two rates further apart than 5 rps. These intervals are correspondingly wider and are **not** 5 rps boundaries:

| cell | SLO | bracket | width |
|---|---:|---|---:|
| E1 c10/C0 | 500 | 830-840 | 10 rps |
| E1 c50/C0 | 500 | 980-990 | 10 rps |
| E1 c50/C1 | 50 | 360-370 | 10 rps |
| E2 c50@Q500 | 500 | 980-990 | 10 rps |
| E2b C=400 | 50 | 180-190 | 10 rps |

## Method and its validation

vSLO is a per-second predicate over a 5 s trailing window: violating when the live p99 exceeds the SLO **or** the error rate exceeds 1%. Every input is recorded per tick in each run timeline, so the sweep replays the runner's own loop at a different threshold rather than re-deriving anything from raw traces. The error component and all other pre-registered rules are unchanged.

**T_full is re-derived, not held fixed.** Stabilisation requires the live p99 under the SLO for 15 consecutive seconds, so a tighter SLO delays T_full and a looser one brings it forward. Holding it at the recorded value would understate a tight threshold, since vSLO is violating seconds over T_full.

**Validation: at each run's own recorded threshold the replay reproduces the recorded vSLO, vSLO_latency, vSLO_error and T_full for all 171 archived runs, with zero mismatches.** `python3 scripts/slo_sweep.py --validate`.

Achieved rho is unchanged throughout. It is a property of delivered rates, not of latency, so the A4 values from each cell's boundary file carry over and no rho was recomputed for this analysis.

### Limits

- A run stops sampling once it stabilises, so under a tight SLO a recorded timeline can end before a 15 s healthy streak forms. Such runs are marked INDETERMINATE, never silently counted as violating. **None occurred** in the well-posed set.
- Latencies are integer milliseconds, so at 50 ms the threshold has 2% granularity. That is immaterial at the observed baselines of 7 and 34 ms.
- Three of the five S/SLO groups contain one arm only. They cannot discriminate, and their small spread should not be read as support for the ratio model.
