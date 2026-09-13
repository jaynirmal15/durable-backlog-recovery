# E2b — concurrency or service time?

**Data only.** Readings registered in `results/E2B-PLAN.md` before the instance was started. Go harness pinned at `026be6242d26`, the commit used by E1, E1B and E2.

## The condition

| | value | matches |
|---|---:|---|
| C | 400 | neither — E1 and E2 ran at 2000 |
| S | 25 ms | **c50** |
| lambda_L | 200 | lambda_L/C = 0.5, as everywhere |
| concurrency | 10 | **c10** |
| queue cap | 500 | derived, not forced |
| cap-in-ms | 1250 | **c50** |

Asserted on every one of the 21 records: cap 500, S 25 ms, concurrency 10, C 400, lambda_L 200. Conforming: **21 of 21**.

The record field `concurrencyArm` reads `c50`. That names the **service time**, not the concurrency, which is 10 here. The arm labels were named for the concurrency each arm has at C=2000.

## Result

| | |
|---|---|
| rl interval | **[190, 195]** UNSAFE |
| rho* interval (A4) | **[0.9750, 0.9875]** |
| width | 0.0125 |
| midpoint | 0.9812 |
| probes / runs | 4 / 21 |
| spread-diagnostic flags | none |

```
h = (rho* - rho10) / D = (0.9812 - 0.9137) / 0.0689 = +0.980
```

| hypothesis | predicted rho* | predicted rl | distance from observed |
|---|---:|---:|---:|
| c10-like: concurrency governs | 0.9137 | 165 | +0.0675 |
| c50-like: S governs | 0.9826 | 195 | -0.0014 |

### Registered verdict: **S GOVERNS**

Bands fixed in E2B-PLAN before the instance was started: concurrency for `-0.25 <= h <= 0.25`, S for `0.75 <= h <= 1.25`, intermediate between, off-scale outside. The dead band was registered in advance, which is the E2 defect corrected rather than repeated.

At C=400 the 5 rps resolution is a rho resolution of 0.0125, so **h resolves to about +/-0.18**. The two hypotheses are 5.5 quanta apart, which is why this reading holds; a finer reading within the intermediate band would not, and none is offered.

### Every probed point

| rl | nominal rho | class | n | vSLO per rep | rho (A4) | median rec rps |
|---:|---:|---|---:|---|---|---:|
| 180 | 0.9500 | SAFE | 3 | 0.0000, 0.0000, 0.0000 | 0.9500 | 180.0 |
| **190** | 0.9750 | SAFE | 12 | 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000 ... | 0.9750 | 190.0 |
| **195** | 0.9875 | UNSAFE | 3 | 0.7014, 0.6667, 0.6805 | 0.9875 | 195.0 |
| 200 | 1.0000 | UNSAFE | 3 | 0.8182, 0.8112, 0.8042 | 1.0000 | 200.0 |

Probe order from run timestamps: 180 -> 200 -> 190 -> 195.

## Occupancy and depth at the last SAFE point (rl=190)

| | |
|---|---|
| n | 12 |
| DEEP (`drainQueueDepthMean` >= 50) | **0/12** |
| median qMean | 2.63 (0.53% of cap 500) |
| gapRatio / dipGap / BC | 3.08 / 0.245 / 0.346 |
| max vSLO | 0.0000 |

Sorted: 2.1 2.2 2.2 2.3 2.4 2.6 2.6 2.8 2.9 2.9 3.1 3.4

### Does the queue peak bind the cap at any SAFE point?

E2's null has a candidate mechanism: across all six cells measured before this one, the median queue peak at the last SAFE point sat below the cap, 1.5% to 50.6% of it. The brief asks for the same check at a fifth of the absolute rate.

| rl | class | n | cap | median peak | % of cap | max peak | % of cap | reaches cap |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 180 | SAFE | 3 | 500 | 3.0 | 0.6% | 3 | 0.6% | no |
| 190 | SAFE | 12 | 500 | 9.0 | 1.8% | 15 | 3.0% | no |
| 195 | non-SAFE | 3 | 500 | 365.0 | 73.0% | 409 | 81.8% | no |
| 200 | non-SAFE | 3 | 500 | 500.0 | 100.0% | 500 | 100.0% | **yes** |

**No SAFE point reaches the cap. The cap is not a binding constraint where the boundary is set, as in all six earlier cells, now confirmed at a fifth of the absolute rate.**

