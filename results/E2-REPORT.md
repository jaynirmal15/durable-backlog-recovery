# E2 — separating the queue-cap effect from the concurrency effect

**Data only. No interpretation beyond the readings registered in `results/E2-PLAN.md` before the runs.** Harness pinned at `026be6242d26`, the same commit as E1 and E1B.

## The 2x2

E1 measured the diagonal where arm and cap vary together. E2 fills the other.

| | Q=500 (250 ms full-queue delay) | Q=2500 (1250 ms) |
|---|---|---|
| **c10** (S=5 ms, concurrency 10) | E1: [0.9124, 0.9150] | E2: [0.9124, 0.9150] |
| **c50** (S=25 ms, concurrency 50) | E2: [0.9820, 0.9841] | E1: [0.9817, 0.9835] |

Intervals are [last SAFE, first NON-SAFE] achieved rho under A4.

| cell | rl interval | endpoint | rho* interval | width | probes | runs |
|---|---|---|---|---:|---:|---:|
| **E1 c10 @ Q=500** | [825, 830] | UNSAFE | **[0.9124, 0.9150]** | 0.0026 | 6 | 30 |
| **E1 c50 @ Q=2500** | [975, 980] | UNSAFE | **[0.9817, 0.9835]** | 0.0018 | 7 | 33 |
| **E2 c10 @ Q=2500** | [825, 830] | UNSAFE | **[0.9124, 0.9150]** | 0.0026 | 6 | 27 |
| **E2 c50 @ Q=500** | [975, 980] | UNSAFE | **[0.9820, 0.9841]** | 0.0021 | 6 | 27 |

Run counts for the two E1 cells include the twelve E1B replication runs pooled into their last SAFE points, so they exceed the 18 and 21 stated in `E1-REPORT.md`, which counted the boundary search alone.

`f_c10` is 0.000 against the registered constants. An earlier commit gave 0.001 from unrounded midpoints; the registered arithmetic uses the rounded values fixed in the plan, and that figure supersedes it. The difference is four orders of magnitude below the 0.25 threshold either way.

## Attribution statistic (registered before the runs)

```
m10 = 0.9137   m50 = 0.9826   D = m50 - m10 = 0.0689
f_c10 = (m(c10@2500) - m10) / D      f_c50 = (m50 - m(c50@500)) / D
CAP-DRIVEN both f >= 0.75    CONCURRENCY-DRIVEN both f <= 0.25    else MIXED
```

| cell | midpoint | f | reading |
|---|---:|---:|---|
| c10 @ Q=2500 | 0.9137 | **+0.000** | concurrency-driven |
| c50 @ Q=500 | 0.9830 | **-0.006** | **off-scale** — moved away from the other arm, not towards it (addendum 3) |

Registered verdict: **OFF-SCALE** (f = +0.000 and -0.006).

**`CAP-DRIVEN` was already unreachable before this cell was measured.** It requires both fractions to be at least 0.75, and the c10 cell returned +0.000. So the absence of a cap verdict is settled by the c10 cell alone and the c50 cell cannot count as evidence for it. What the c50 cell decides is which of the remaining readings applies.

Per addendum 3, registered before this cell was measured: the negative fraction means the cell moved **away** from the other arm, so it does not satisfy `CONCURRENCY-DRIVEN` despite being below 0.25, and moving away is not evidence for the cap. Neither registered verdict is claimed.

**The criterion has no dead band, and here that matters.** Addendum 4, registered before the deciding probe: the verdict above is what addendum 3 produces, and the criterion was deliberately not changed once the arithmetic showed it was about to fire. But the magnitude is -0.006. Addendum 3 was written against a cell that moves materially the wrong way and was tested at -0.057. At -0.006 the cell has not moved.

Reported alongside, with no verdict status: `|f| <= 0.25` in both cells, so **neither cell moved materially in either direction**. The plan can express "moved" and "did not move"; it cannot distinguish -0.006 from +0.006, and the data does not settle which side of zero this fell on.

### Interval overlap, reported alongside because f hides width

| cell | overlaps its own arm E1 interval | overlaps the other arm E1 interval |
|---|---|---|
| c10 @ Q=2500 | yes | no |
| c50 @ Q=500 | yes | no |

## Every probed point, both E2 cells

`rec rps` is the achieved recovery rate over the delivery span (A4), against the nominal `rl` the search was bisecting. Where the two diverge the limiter is saturating and the nominal rate overstates the load actually offered.

### c10 @ Q=2500

| rl | class | n | vSLO per rep | rho (A4) | median rec rps | rec / rl |
|---:|---|---:|---|---|---:|---:|
| **825** | SAFE | 12 | 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000 ... | 0.9124-0.9125 | 825.0 | 1.000 |
| **830** | UNSAFE | 3 | 0.2548, 0.3248, 0.2628 | 0.9149-0.9150 | 829.9 | 1.000 |
| 835 | UNSAFE | 3 | 0.6266, 0.5897, 0.4968 | 0.9172-0.9173 | 834.4 | 0.999 |
| 845 | UNSAFE | 3 | 0.7579, 0.7388, 0.7597 | 0.9210-0.9213 | 842.3 | 0.997 |
| 865 | UNSAFE | 3 | 0.8280, 0.8344, 0.8280 | 0.9205-0.9208 | 841.4 | 0.973 |
| 905 | UNSAFE | 3 | 0.8671, 0.8662, 0.8662 | 0.9209-0.9211 | 841.7 | 0.930 |

Probe order, from run timestamps rather than the order points are stored in: 825 -> 905 -> 865 -> 845 -> 835 -> 830. The replication runs then returned to rl=825.

### c50 @ Q=500

| rl | class | n | vSLO per rep | rho (A4) | median rec rps | rec / rl |
|---:|---|---:|---|---|---:|---:|
| **975** | SAFE | 12 | 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000 ... | 0.9820-0.9826 | 964.6 | 0.989 |
| **980** | UNSAFE | 3 | 0.2482, 0.2206, 0.1397 | 0.9835-0.9841 | 967.9 | 0.988 |
| 990 | UNSAFE | 3 | 0.6103, 0.5912, 0.5693 | 0.9857-0.9860 | 971.6 | 0.981 |
| 1000 | UNSAFE | 3 | 0.6594, 0.5912, 0.6176 | 0.9868-0.9869 | 973.7 | 0.974 |
| 1025 | UNSAFE | 3 | 0.7174, 0.7059, 0.6811 | 0.9884-0.9894 | 977.5 | 0.954 |
| 1075 | UNSAFE | 3 | 0.7536, 0.7591, 0.7591 | 0.9900-0.9905 | 981.0 | 0.913 |

Probe order, from run timestamps rather than the order points are stored in: 975 -> 1075 -> 1025 -> 1000 -> 990 -> 980. The replication runs then returned to rl=975.

### Is the interval well formed?

The interval is [min rho at the last SAFE point, max rho at the first non-SAFE point]. That is only meaningful if rho actually rises between the two. It need not: the recovery limiter saturates, so past the boundary a higher nominal rate can deliver no more recovery and rho can fall.

| cell | rho rises across the interval | width | monotonic across all probed points |
|---|---|---:|---|
| c10 @ Q=2500 | yes | +0.0026 | no, and it does not need to be: the departures are at deep non-SAFE points that bound nothing |
| c50 @ Q=500 | yes | +0.0021 | yes |

## Bimodality at the last SAFE point

Threshold fixed in E1B and unchanged: **DEEP if `drainQueueDepthMean` >= 50**.

| cell | cap | n | DEEP | median qMean | gapRatio | dipGap | BC | max vSLO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| E1B c10/C0 @ Q=500 | 500 | 12 | **0/12** | 20.88 | 3.9 | 0.269 | 0.387 | 0.0000 |
| E1B c50/C0 @ Q=2500 | 2500 | 12 | **9/12** | 102.25 | 7.04 | 0.385 | 0.351 | 0.0000 |
| E2 c10 @ Q=2500 | 2500 | 12 | **0/12** | 23.09 | 5.05 | 0.249 | 0.452 | 0.0000 |
| E2 c50 @ Q=500 | 500 | 12 | **12/12** | 108.43 | 2.59 | 0.234 | 0.38 | 0.0000 |

The plan asked two questions in these words. Both are answered no.

- **"c10 given c50's cap — does it *become* bimodal?"** No. 0/12 DEEP, against 0/12 at its own cap. Unchanged.
- **"c50 given c10's cap — does it *stop* being bimodal?"** No, and it moves the other way: 12/12 DEEP against 9/12 at its own cap. The three shallow runs that produced E1B's gap are gone, and the gap with them (gapRatio 7.04 to 2.59, dipGap 0.385 to 0.234). The cell is now uniformly deep, which is E1B's "unimodal deep" category rather than bimodal.

Median occupancy barely moved in either cell when the cap changed fivefold: 20.88 to 23.09 for c10 and 102.25 to 108.43 for c50. Depth followed the arm, not the cap.

Every one of the 24 replication runs classified SAFE, max vSLO 0.0000.

## Cap-normalised occupancy (addendum 1, registered mid-campaign)

Cap is the cap **in force during the drain window**, `50 x ceil(C_d x S)` under `profile_relative`, not the t=0 value.

| cell | rl | n | C_d | cap | median qMean | % of cap | class |
|---|---:|---:|---:|---:|---:|---:|---|
| E1 c10/C0 | 755 | 3 | 2000 | 500 | 0.54 | 0.108% | SAFE |
| E1 c10/C0 | 800 | 3 | 2000 | 500 | 1.34 | 0.269% | SAFE |
| E1 c10/C0 | 820 | 3 | 2000 | 500 | 4.26 | 0.853% | SAFE |
| E1 c10/C0 | 825 | 15 | 2000 | 500 | 20.57 | 4.114% | SAFE |
| E1 c10/C0 | 830 | 3 | 2000 | 500 | 227.72 | 45.544% | non-SAFE |
| E1 c10/C0 | 840 | 3 | 2000 | 500 | 417.74 | 83.549% | non-SAFE |
| E1 c10/C1 | 240 | 3 | 1400 | 350 | 1.43 | 0.408% | SAFE |
| E1 c10/C1 | 255 | 3 | 1400 | 350 | 1.23 | 0.351% | SAFE |
| E1 c10/C1 | 260 | 3 | 1400 | 350 | 3.42 | 0.978% | SAFE |
| E1 c10/C1 | 275 | 3 | 1400 | 350 | 6.85 | 1.956% | SAFE |
| E1 c10/C1 | 280 | 3 | 1400 | 350 | 263.02 | 75.150% | non-SAFE |
| E1 c10/C1 | 290 | 3 | 1400 | 350 | 319.15 | 91.185% | non-SAFE |
| E1 c50/C0 | 890 | 3 | 2000 | 2500 | 0.37 | 0.015% | SAFE |
| E1 c50/C0 | 940 | 3 | 2000 | 2500 | 1.55 | 0.062% | SAFE |
| E1 c50/C0 | 965 | 3 | 2000 | 2500 | 4.92 | 0.197% | SAFE |
| E1 c50/C0 | 970 | 3 | 2000 | 2500 | 7.91 | 0.316% | SAFE |
| E1 c50/C0 | 975 | 15 | 2000 | 2500 | 101.79 | 4.071% | SAFE |
| E1 c50/C0 | 980 | 3 | 2000 | 2500 | 275.82 | 11.033% | non-SAFE |
| E1 c50/C0 | 990 | 3 | 2000 | 2500 | 561.28 | 22.451% | non-SAFE |
| E1 c50/C1 | 340 | 3 | 1400 | 1750 | 0.75 | 0.043% | SAFE |
| E1 c50/C1 | 360 | 3 | 1400 | 1750 | 1.76 | 0.100% | SAFE |
| E1 c50/C1 | 370 | 3 | 1400 | 1750 | 4.71 | 0.269% | SAFE |
| E1 c50/C1 | 375 | 3 | 1400 | 1750 | 191.04 | 10.917% | non-SAFE |
| E1 c50/C1 | 380 | 3 | 1400 | 1750 | 853.30 | 48.760% | non-SAFE |
| E2 c10@Q2500 | 825 | 12 | 2000 | 2500 | 23.09 | 0.923% | SAFE |
| E2 c10@Q2500 | 830 | 3 | 2000 | 2500 | 299.07 | 11.963% | non-SAFE |
| E2 c10@Q2500 | 835 | 3 | 2000 | 2500 | 626.79 | 25.071% | non-SAFE |
| E2 c10@Q2500 | 845 | 3 | 2000 | 2500 | 1236.36 | 49.454% | non-SAFE |
| E2 c10@Q2500 | 865 | 3 | 2000 | 2500 | 1762.03 | 70.481% | non-SAFE |
| E2 c10@Q2500 | 905 | 3 | 2000 | 2500 | 1988.64 | 79.546% | non-SAFE |
| E2 c50@Q500 | 975 | 12 | 2000 | 500 | 108.43 | 21.686% | SAFE |
| E2 c50@Q500 | 980 | 3 | 2000 | 500 | 274.18 | 54.835% | non-SAFE |
| E2 c50@Q500 | 990 | 3 | 2000 | 500 | 397.02 | 79.403% | non-SAFE |
| E2 c50@Q500 | 1000 | 3 | 2000 | 500 | 401.16 | 80.232% | non-SAFE |
| E2 c50@Q500 | 1025 | 3 | 2000 | 500 | 431.33 | 86.266% | non-SAFE |
| E2 c50@Q500 | 1075 | 3 | 2000 | 500 | 450.92 | 90.185% | non-SAFE |
| E2b C=400 | 180 | 3 | 400 | 500 | 0.66 | 0.132% | SAFE |
| E2b C=400 | 190 | 12 | 400 | 500 | 2.63 | 0.526% | SAFE |
| E2b C=400 | 195 | 3 | 400 | 500 | 180.21 | 36.043% | non-SAFE |
| E2b C=400 | 200 | 3 | 400 | 500 | 364.99 | 72.998% | non-SAFE |

The `4.1% of cap` agreement registered in addendum 1 does not survive either new cell. The two E1 C0 cells sat at 4.114% and 4.071%; the same arms at swapped caps sit at 0.923% and 21.686%. Absolute occupancy stayed with the arm while the cap moved fivefold, which is what breaks the ratio.

### g, the occupancy analogue of f

```
g = (observed median - retain) / (swap - retain)
  c10@2500: retain 20.57 swap 103      c50@500: retain 101.79 swap 21
cap-governed both g >= 0.75    concurrency-governed both <= 0.25
```

| cell | observed median | g | reading |
|---|---:|---:|---|
| c10 @ Q=2500 | 23.09 | **+0.031** | concurrency-governed |
| c50 @ Q=500 | 108.43 | **-0.082** | **off-scale** (addendum 3) |

Registered verdict: **OFF-SCALE** (g = +0.031 and -0.082).

Addendum 4 applies here unchanged. The verdict is what addendum 3 produces and the criterion was not altered after the fact, but the magnitude is -0.082 and the criterion has no dead band. Reported alongside, without verdict status: `|g| <= 0.25` in both cells, so occupancy did not follow the cap in either -- g of +0.031 and -0.082 against a swap prediction of 1.0.

## Did the cap bind, and what failed

Not a registered reading. Two checks on whether the registered statistics are measuring what they are meant to.

**Failure mode.** `sloErrorAccounting` excludes client 429s, so a smaller cap could in principle turn latency violations into excluded rejections and make a run classify SAFE for the wrong reason. Rejections during the drain, summed over every point of both campaigns at every cap: **0**. The concern does not arise.

Violations are latency violations everywhere except 2 points: E1 c10/C1 Q=350 rl=290, vSLO_error 0.3652 against vSLO_latency 0.8544; E2b C=400 Q=500 rl=200, vSLO_error 0.1678 against vSLO_latency 0.8182. Each is the deepest non-SAFE anchor of its cell and they define no interval.

**Cap binding.** Peak drain-window queue depth against the cap in force. Median and max across the runs at each point, because one run in fifteen at c10/C0 rl=825 peaked at 400 of 500 while the median peaked at 55.

| cell | rl | n | cap | median peak | % of cap | max peak | % of cap | class |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| E1 c10/C0 Q=500 | 755 | 3 | 500 | 3.0 | 0.6% | 4 | 0.8% | SAFE |
| E1 c10/C0 Q=500 | 800 | 3 | 500 | 5.0 | 1.0% | 6 | 1.2% | SAFE |
| E1 c10/C0 Q=500 | 820 | 3 | 500 | 19.0 | 3.8% | 22 | 4.4% | SAFE |
| E1 c10/C0 Q=500 | 825 | 15 | 500 | 55.0 | 11.0% | 400 | 80.0% | SAFE |
| E1 c10/C0 Q=500 | 830 | 3 | 500 | 489.0 | 97.8% | 496 | 99.2% | non-SAFE |
| E1 c10/C0 Q=500 | 840 | 3 | 500 | 500.0 | 100.0% | 500 | 100.0% **cap hit** | non-SAFE |
| E1 c10/C1 Q=350 | 240 | 3 | 350 | 6.0 | 1.7% | 9 | 2.6% | SAFE |
| E1 c10/C1 Q=350 | 255 | 3 | 350 | 6.0 | 1.7% | 9 | 2.6% | SAFE |
| E1 c10/C1 Q=350 | 260 | 3 | 350 | 12.0 | 3.4% | 20 | 5.7% | SAFE |
| E1 c10/C1 Q=350 | 275 | 3 | 350 | 49.0 | 14.0% | 55 | 15.7% | SAFE |
| E1 c10/C1 Q=350 | 280 | 3 | 350 | 350.0 | 100.0% | 350 | 100.0% **cap hit** | non-SAFE |
| E1 c10/C1 Q=350 | 290 | 3 | 350 | 350.0 | 100.0% | 350 | 100.0% **cap hit** | non-SAFE |
| E1 c50/C0 Q=2500 | 890 | 3 | 2500 | 4.0 | 0.2% | 5 | 0.2% | SAFE |
| E1 c50/C0 Q=2500 | 940 | 3 | 2500 | 7.0 | 0.3% | 9 | 0.4% | SAFE |
| E1 c50/C0 Q=2500 | 965 | 3 | 2500 | 21.0 | 0.8% | 27 | 1.1% | SAFE |
| E1 c50/C0 Q=2500 | 970 | 3 | 2500 | 28.0 | 1.1% | 31 | 1.2% | SAFE |
| E1 c50/C0 Q=2500 | 975 | 15 | 2500 | 213.0 | 8.5% | 277 | 11.1% | SAFE |
| E1 c50/C0 Q=2500 | 980 | 3 | 2500 | 488.0 | 19.5% | 522 | 20.9% | non-SAFE |
| E1 c50/C0 Q=2500 | 990 | 3 | 2500 | 1122.0 | 44.9% | 1242 | 49.7% | non-SAFE |
| E1 c50/C1 Q=1750 | 340 | 3 | 1750 | 7.0 | 0.4% | 7 | 0.4% | SAFE |
| E1 c50/C1 Q=1750 | 360 | 3 | 1750 | 9.0 | 0.5% | 9 | 0.5% | SAFE |
| E1 c50/C1 Q=1750 | 370 | 3 | 1750 | 27.0 | 1.5% | 31 | 1.8% | SAFE |
| E1 c50/C1 Q=1750 | 375 | 3 | 1750 | 433.0 | 24.7% | 485 | 27.7% | non-SAFE |
| E1 c50/C1 Q=1750 | 380 | 3 | 1750 | 1750.0 | 100.0% | 1750 | 100.0% **cap hit** | non-SAFE |
| E2 c10 Q=2500 | 825 | 12 | 2500 | 72.5 | 2.9% | 83 | 3.3% | SAFE |
| E2 c10 Q=2500 | 830 | 3 | 2500 | 596.0 | 23.8% | 607 | 24.3% | non-SAFE |
| E2 c10 Q=2500 | 835 | 3 | 2500 | 1120.0 | 44.8% | 1332 | 53.3% | non-SAFE |
| E2 c10 Q=2500 | 845 | 3 | 2500 | 2256.0 | 90.2% | 2257 | 90.3% | non-SAFE |
| E2 c10 Q=2500 | 865 | 3 | 2500 | 2264.0 | 90.6% | 2264 | 90.6% | non-SAFE |
| E2 c10 Q=2500 | 905 | 3 | 2500 | 2268.0 | 90.7% | 2268 | 90.7% | non-SAFE |
| E2 c50 Q=500 | 975 | 12 | 500 | 224.0 | 44.8% | 329 | 65.8% | SAFE |
| E2 c50 Q=500 | 980 | 3 | 500 | 500.0 | 100.0% | 500 | 100.0% **cap hit** | non-SAFE |
| E2 c50 Q=500 | 990 | 3 | 500 | 500.0 | 100.0% | 500 | 100.0% **cap hit** | non-SAFE |
| E2 c50 Q=500 | 1000 | 3 | 500 | 500.0 | 100.0% | 500 | 100.0% **cap hit** | non-SAFE |
| E2 c50 Q=500 | 1025 | 3 | 500 | 500.0 | 100.0% | 500 | 100.0% **cap hit** | non-SAFE |
| E2 c50 Q=500 | 1075 | 3 | 500 | 500.0 | 100.0% | 500 | 100.0% **cap hit** | non-SAFE |
| E2b C=400 Q=500 | 180 | 3 | 500 | 3.0 | 0.6% | 3 | 0.6% | SAFE |
| E2b C=400 Q=500 | 190 | 12 | 500 | 9.0 | 1.8% | 15 | 3.0% | SAFE |
| E2b C=400 Q=500 | 195 | 3 | 500 | 365.0 | 73.0% | 409 | 81.8% | non-SAFE |
| E2b C=400 Q=500 | 200 | 3 | 500 | 500.0 | 100.0% | 500 | 100.0% **cap hit** | non-SAFE |

At the last SAFE point of every cell in both campaigns:

| cell | rl | median peak as % of cap |
|---|---:|---:|
| E1 c10/C0 Q=500 | 825 | 11.0% |
| E1 c10/C1 Q=350 | 275 | 14.0% |
| E1 c50/C0 Q=2500 | 975 | 8.5% |
| E1 c50/C1 Q=1750 | 370 | 1.5% |
| E2 c10 Q=2500 | 825 | 2.9% |
| E2 c50 Q=500 | 975 | 44.8% |
| E2b C=400 Q=500 | 190 | 1.8% |

## Campaign

| | |
|---|---|
| c10 @ Q=2500 records | 27 |
| c50 @ Q=500 records | 27 |
| Total E2 runs | **54** |
| Distinct harness commits | 026be6242d26 |
| Records flagged gitDirty | 53 — all from the untracked `results-*` output directory, which `provenanceOutputPrefixes` does not cover. No code differs from the pinned commit. |

### Configuration conformance

Every E2 record checked against the cap its cell is supposed to impose. The two cells share run-id namespaces with E1 (`c50-c0-rl975-r1` exists in both), which is why each writes to its own directory; the last row checks that no E2 record reached the E1 corpus.

| cell | expected cap | expected S | records | conforming |
|---|---:|---:|---:|---|
| c10 @ Q=2500 | 2500 | 5 ms | 27 | all 27 |
| c50 @ Q=500 | 500 | 25 ms | 27 | all 27 |
| E1 corpus (`results/`) | 500 for c10, 2500 for c50 | | 96 | no E2 record present |

