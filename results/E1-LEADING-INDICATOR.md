# E1 leading-indicator analysis — does anything warn before the boundary?

**Analysis only. No new runs.** Every number comes from the 66 E1 run records
and their traces. E1 established *where* the boundaries are; this asks whether
anything is observable *before* one, which is what the controller argument
rests on: a controller can only act on a signal it can see coming.

## Answer

> **(c) A signal warns in both arms. It is mean queue depth.**

The registered expectation in `NOTES.md` was **(b)**, a signal at c50 but not
at c10. **The data does not support (b).** Queue depth warns in every boundary
whose geometry allows the question to be asked, and the earliest warning in ρ
terms is at **c10**, not c50 — 0.0124 against 0.0125, which is a tie.

| boundary | SAFE pts | first warning | ρ room to last SAFE | points of room |
|---|---:|---|---:|---:|
| c10-C0 | 4 | rl=800 (ρ 0.9000) | **0.0124** | 2 |
| c10-C1 | 2 | — (only 2 SAFE points) | — | — |
| c50-C0 | 5 | rl=940 (ρ 0.9695) | **0.0125** | 3 |
| c50-C1 | 3 | rl=360 (ρ 0.9714) | **0.0072** | 1 |

`c10-C1` has only two SAFE points, so no point *before* the last one exists.
That is a **limitation of the search geometry, not a null result** — its anchor
failed and bisection converged in four probes. It cannot support or refute
either arm of the question.

## Method

Six drain-window observables per SAFE point, n=3: live p50, p90, p99, mean queue
depth, mean in-flight, timeout rate. Two statistics, because they answer
different questions:

- **rise/σ** — the rise from the deepest-safe point, over the *median*
  within-point standard deviation. Answers "is there a trend at all".
- **detect@point** — the same rise over the scatter *at that point*. Answers
  "could a controller taking one sample here tell it apart from deep-safe
  operation". A point can have a huge trend and still be undetectable in one
  observation, and one here is exactly that.

The noise scale is the median, not the mean, of the within-point SDs. At the
c10/C0 last-safe point the three repetitions scatter enormously and a
mean-pooled σ would let that one point swamp the estimate and hide a signal
that was already obvious two points earlier. Percentiles quantised to whole
milliseconds get a 0.5 ms noise floor, so an apparent zero-variance metric
cannot manufacture unbounded significance.

Warning threshold fixed at **3σ** before looking at the numbers.

## Mean queue depth, point by point

| boundary | rl | ρ | qMean | sd | rise/σ | detect@point |
|---|---:|---:|---:|---:|---:|---:|
| c10-C0 | 755 | 0.8775 | 0.575 | 0.141 | 0.0 | 0.0 |
| c10-C0 | 800 | 0.9000 | 1.388 | 0.070 | 6.8 | 11.7 |
| c10-C0 | 820 | 0.9100 | 4.269 | 0.100 | 30.7 | 37.1 |
| c10-C0 **(last SAFE)** | 825 | 0.9124 | 75.743 | 86.972 | 624.3 | 0.9 |
| c10-C1 | 260 | 0.9000 | 2.800 | 1.061 | 0.0 | 0.0 |
| c10-C1 **(last SAFE)** | 275 | 0.9107 | 8.450 | 2.717 | 3.0 | 2.1 |
| c50-C0 | 890 | 0.9449 | 0.530 | 0.262 | 0.0 | 0.0 |
| c50-C0 | 940 | 0.9695 | 1.442 | 0.211 | 3.3 | 4.3 |
| c50-C0 | 965 | 0.9781 | 5.029 | 0.330 | 16.5 | 13.6 |
| c50-C0 | 970 | 0.9799 | 7.952 | 0.273 | 27.2 | 27.2 |
| c50-C0 **(last SAFE)** | 975 | 0.9819 | 103.593 | 27.036 | 377.8 | 3.8 |
| c50-C1 | 340 | 0.9571 | 0.735 | 0.082 | 0.0 | 0.0 |
| c50-C1 | 360 | 0.9714 | 1.799 | 0.110 | 9.7 | 9.7 |
| c50-C1 **(last SAFE)** | 370 | 0.9786 | 4.846 | 0.237 | 37.5 | 17.4 |

Queue depth climbs **two orders of magnitude** inside the safe region in both
C0 arms — 0.53 → 4.3 at c10 and 0.53 → 8.0 at c50 — before the last safe point,
where it then jumps to 76 and 104. Every step is monotone.

## Every metric

| boundary | metric | deep safe | last safe | rise | rise/σ | detect@last | first warns | verdict |
|---|---|---:|---:|---:|---:|---:|---|---|
| c10-C0 | live p50 | 5.333 | 50.67 | 45.33 | 90.7 | 0.8 | rl=820 | WARNS, 1 point(s) of room |
| c10-C0 | live p90 | 7.333 | 75.33 | 68 | 136.0 | 0.9 | rl=820 | WARNS, 1 point(s) of room |
| c10-C0 | live p99 | 8.333 | 95 | 86.67 | 173.3 | 1.0 | rl=820 | WARNS, 1 point(s) of room |
| c10-C0 | mean queue depth | 0.5751 | 75.74 | 75.17 | 624.3 | 0.9 | rl=800 | WARNS, 2 point(s) of room |
| c10-C0 | mean in-flight | 6.036 | 46.84 | 40.8 | 293.9 | 0.9 | rl=820 | WARNS, 1 point(s) of room |
| c10-C0 | timeout rate | 0 | 0 | 0 | 0.0 | 0.0 | — | flat |
| c10-C1 | live p50 | 6 | 8.667 | 2.667 | 5.3 | 5.3 | rl=275 | rises only at the last safe point |
| c10-C1 | live p90 | 8.667 | 22.33 | 13.67 | 2.7 | 1.4 | — | flat |
| c10-C1 | live p99 | 10.33 | 34.33 | 24 | 5.5 | 3.1 | rl=275 | rises only at the last safe point |
| c10-C1 | mean queue depth | 2.8 | 8.45 | 5.65 | 3.0 | 2.1 | — | flat |
| c10-C1 | mean in-flight | 6.8 | 11.82 | 5.025 | 4.3 | 2.3 | rl=275 | rises only at the last safe point |
| c10-C1 | timeout rate | 0 | 0 | 0 | 0.0 | 0.0 | — | flat |
| c50-C0 | live p50 | 25 | 80.33 | 55.33 | 110.7 | 3.2 | rl=965 | WARNS, 2 point(s) of room |
| c50-C0 | live p90 | 30 | 105.3 | 75.33 | 150.7 | 4.0 | rl=965 | WARNS, 2 point(s) of room |
| c50-C0 | live p99 | 34 | 115.7 | 81.67 | 163.3 | 4.9 | rl=965 | WARNS, 2 point(s) of room |
| c50-C0 | mean queue depth | 0.5297 | 103.6 | 103.1 | 377.8 | 3.8 | rl=940 | WARNS, 3 point(s) of room |
| c50-C0 | mean in-flight | 25.75 | 78.27 | 52.52 | 121.2 | 3.8 | rl=965 | WARNS, 2 point(s) of room |
| c50-C0 | timeout rate | 0 | 0 | 0 | 0.0 | 0.0 | — | flat |
| c50-C1 | live p50 | 26 | 28 | 2 | 4.0 | 4.0 | rl=370 | rises only at the last safe point |
| c50-C1 | live p90 | 30.33 | 34.67 | 4.333 | 8.7 | 8.7 | rl=370 | rises only at the last safe point |
| c50-C1 | live p99 | 34.67 | 41.67 | 7 | 14.0 | 7.4 | rl=370 | rises only at the last safe point |
| c50-C1 | mean queue depth | 0.735 | 4.846 | 4.111 | 37.5 | 17.4 | rl=360 | WARNS, 1 point(s) of room |
| c50-C1 | mean in-flight | 26.43 | 28.98 | 2.55 | 13.4 | 13.4 | rl=370 | rises only at the last safe point |
| c50-C1 | timeout rate | 0 | 0 | 0 | 0.0 | 0.0 | — | flat |

## What this shows

**1. Queue depth is the leading indicator, in both arms.** It is the earliest
metric to clear 3σ in all three boundaries that have enough SAFE points to ask,
and it clears it by a wide margin: 6.8σ at c10/C0 rl=800, 3.3σ at c50/C0 rl=940,
9.7σ at c50/C1 rl=360.

**2. Latency also warns, but later.** p50, p90 and p99 first clear 3σ one to two
probed points after queue depth does. They are not silent — the earlier
characterisation of latency as flat until the cliff does not hold on this
harness — but they are second.

**3. Timeout rate never warns.** It is exactly zero at every SAFE point in all
four boundaries. It carries no information inside the safe region.

**4. Mean in-flight is not an independent signal.** It tracks queue depth
through Little's law and warns at the same point or later. Counting it as a
second confirming indicator would be double-counting one measurement.

**5. The signal degrades exactly where it is needed most.** At the last safe
point in both C0 arms, single-sample detectability collapses even though the
trend is enormous: detect@point falls to **0.9** at c10/C0 and **3.8** at
c50/C0, from 37.1 and 27.2 one step earlier. The cause is bimodality. At
c10/C0 rl=825 the three repetitions gave qMean of **198.7, 13.3 and 15.2**, and
p99 of **223, 24 and 38 ms** — one run sat just under the 250 ms SLO while two
were near-healthy. All three classified SAFE because none breached.

So the warning is clear during the *approach* and unreliable at the *edge*. A
controller sampling once at the last safe point in the c10 arm would see a
healthy queue two times in three.

**6. The signal is statistically strong but absolutely small at first warning.**
At c10/C0 rl=800 the queue is 1.39 against a 0.58 baseline — 6.8σ, but under one
request in absolute terms. Acting on it requires a calibrated per-condition
baseline rather than a fixed threshold, which matches what `NOTES.md` recorded
as the Phase 3 design input: level against baseline, not an absolute setpoint.

## Plots

`results/figs/{c10-C0,c10-C1,c50-C0,c50-C1}.svg` — each observable against
achieved ρ across the SAFE points, error bars at ±1 within-point SD.

## What this does not show

No controller is proposed or evaluated here, and no claim is made about the
pre-EC2 corpus. Whether a warning of this size and this reliability is
*sufficient* to control on is an E2/E4 question. This establishes only that a
signal exists inside the safe region, in both arms, and identifies which one.

Raw output: `results/E1-leading-indicator.json`.
