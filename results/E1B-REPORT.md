# E1B — replication, the 2×2, and what it overturns

Threshold and success criteria fixed in `results/E1B-PLAN.md` (`09e41e5`) and
committed **before the instance was started**. 30 runs, harness commit
`026be6242d26` — the exact commit every E1 run used — on the same instance.
Zero failures, zero guard aborts, zero invalid runs.

## Headline: the bimodality is real, but it is in the other arm

I previously reported that the c10/C0 last-safe point was bimodal and that the
warning signal "degrades exactly where it is needed most". **Both halves of
that were wrong, and in opposite directions.** At n=12 it is the **c50** point
that is bimodal and the **c10** point that is stable.

| point | n | DEEP | fraction | 95% CI | verdict |
|---|---:|---:|---:|---|---|
| c10/C0 rl=825 | 12 | 0 | **0%** | 0.0–26.5% | **unimodal shallow** |
| c50/C0 rl=975 | 12 | 9 | **75%** | 42.8–94.5% | **bimodal** |

DEEP was fixed in advance as `drainQueueDepthMean ≥ 50`, which is 25 ms of
implied queueing delay in both arms and 10% of the SLO.

### c10/C0 rl=825 — unimodal, one historical outlier

```
qMean, 12 fresh runs, sorted:
  10.4 12.5 15.0 17.0 17.9 20.6 21.2 22.5 24.1 25.6 33.1 38.5
```

**Zero of twelve** reach the threshold; the maximum is 38.5. The E1 run that
produced qMean 198.7 and p99 223 has no counterpart. Largest gap 7.5 against a
median gap of 1.9 (ratio 3.9) — no bimodal signature.

Pooling all 15 runs at this point: fourteen lie between 10.4 and 38.5 and one
sits at 198.7. **A single outlier, not a stable minority mode.** If the true
DEEP rate were the 33% the original triplet implied, seeing zero in twelve has
probability 0.008. A *rare* mode is not excluded — twelve runs bound the rate
only below 26.5%.

### c50/C0 rl=975 — genuinely bimodal

```
qMean, 12 fresh runs, sorted:
  23.4 37.0 40.0 92.1 92.1 101.8 102.7 110.1 117.1 120.8 151.0 158.7
```

**Nine of twelve** are DEEP. The gap of **52.1** after 40.0, against a median
gap of 7.4 (ratio **7.0**), is a clean separation — three runs cluster near
23–40 and nine near 92–159, with nothing between. The DEEP fraction's
confidence interval excludes both 0 and 1, which is the pre-registered
definition of "bimodal with a stable fraction".

## Neither boundary changes

**Every one of the 24 replication runs has `vSLO` exactly 0.** Both points
therefore remain SAFE at n=15, not just n=3, and boundaries 1 and 3 stand
unchanged. The pre-registered concern — a point classifying SAFE at n=3 and
non-SAFE at n=12 — did not materialise at either point.

The n=15 estimates are much better than the triplets they replace:

| point | qMean at n=3 | qMean at n=15 |
|---|---|---|
| c10/C0 rl=825 | 75.74 ± 86.97 | **32.38 ± 45.07** (median 20.57) |
| c50/C0 rl=975 | 103.59 ± 27.04 | **97.17 ± 38.79** (median 101.79) |

At c10/C0 the n=3 mean was more than double the n=15 median, entirely because
of the outlier. At c50/C0 the mean barely moved — because there the high values
are the majority mode, not an accident.

## Item 2 — the 2×2 is complete, and it weakens the queue-depth story

`c10/C1` gained rl=240 and rl=255, both **SAFE**, giving four SAFE points. Both
are below the existing last SAFE point, so **the interval [275, 280] cannot and
does not change**.

| rl | ρ | qMean |
|---:|---:|---|
| 240 | 0.8857 | 1.57 ± 0.38 |
| 255 | 0.8964 | 1.52 ± 0.45 |
| 260 | 0.9000 | 2.80 ± 1.06 |
| 275 | 0.9107 | 8.45 ± 2.72 |

**Queue depth gives no advance warning at this boundary under any noise
scale.** The two lowest points are indistinguishable and slightly non-monotone,
so the whole rise arrives at the last safe point. Under Welch the boundary does
warn, but through p90 (one point of room) and mean in-flight (two) — different
metrics from every other boundary.

So "queue depth is the leading indicator" holds at **three of four** boundaries,
not universally, and the exception is a c10 boundary.

## The (a)/(b)/(c) answer is unchanged by all of this

| noise scale | c10-C0 | c10-C1 | c50-C0 | c50-C1 | answer |
|---|---|---|---|---|---|
| mean | none | none | none | queue depth | **(b)** |
| median | 5 metrics | none | 5 metrics | queue depth | **(c)** |
| welch | 5 metrics | p90, in-flight | 5 metrics | p99, queue depth | **(c)** |

Adding 30 runs and completing the 2×2 did not move it. It remains scale-
dependent exactly as A5 records.

## What I withdraw

From the E1 leading-indicator report:

1. **"The signal degrades exactly where it is needed most."** Withdrawn. It
   rested on a single-sample detectability of 0.9σ at c10/C0 rl=825, which was
   produced by one outlying run out of three. At n=15 that point is stable.
2. **"c10/C0 rl=825 is bimodal."** Withdrawn — 0 of 12.
3. **The bimodality claim moves to c50/C0 rl=975**, where it is supported at
   9 of 12 with a clean gap.

What survives unchanged: queue depth is the earliest warning at c10/C0,
c50/C0 and c50/C1; timeout rate never warns anywhere; and the scale
sensitivity in A5.

## Artefacts

- `results/E1B-PLAN.md` — pre-run plan, committed before the runs
- `results/E1B-replication.json` — per-run values, fractions, CIs, gap statistics
- `results/E1-noise-scale-sensitivity.json` — the three-scale table
- 30 run records `results/e1b-*.json`; 30 traces in the raw-data corpus
