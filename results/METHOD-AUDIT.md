# Method audit — seven questions from the Section 4 review

**Audits of committed data. No new runs.** Every answer is reproducible with
`python3 scripts/method_audit.py`. Where an answer is unflattering it is written
that way.

---

## 1. Monotonicity audit (blocking)

**Result: zero inversions in all seven cells, and no MARGINAL classification
exists anywhere in the corpus.** Across the 40 probed points in the seven
boundary files the classifications are 20 SAFE and 20 UNSAFE. The failure mode
the reviewer describes — a noisy MARGINAL at n=3 truncating the search and
pulling the boundary down — **did not occur, because no point was ever
classified MARGINAL.**

Points are ordered by **achieved** rate, not by nominal `rl`, because the two
orderings differ: in E2 c10@Q2500 the achieved rates run 1841.4, 1841.8, 1842.2
for nominal rates 865, 905, 845 respectively. Ordering by nominal rate would
have hidden that.

```
1. MONOTONICITY AUDIT
==============================================================================
Points ordered by ACHIEVED rate (A4), with nominal rl alongside.
An inversion is a higher-achieved-rate point classifying safer than a
lower-achieved-rate one.

--- E1 c10/C0   bracket rl [825, 830]
    achieved     rl    n class     vSLO
      1755.0    755    3 SAFE      0.000, 0.000, 0.000
      1800.0    800    3 SAFE      0.000, 0.000, 0.000
      1820.0    820    3 SAFE      0.000, 0.000, 0.000
      1825.0    825   15 SAFE      0.000, 0.000, 0.000 <-
      1829.8    830    3 UNSAFE    0.077, 0.000, 0.135 <-
      1839.2    840    3 UNSAFE    0.647, 0.707, 0.679
    inversions: 0
    terminal endpoint decided by a MARGINAL: no

--- E1 c10/C1   bracket rl [275, 280]
    achieved     rl    n class     vSLO
      1240.0    240    3 SAFE      0.000, 0.000, 0.000
      1255.0    255    3 SAFE      0.000, 0.000, 0.000
      1260.0    260    3 SAFE      0.000, 0.000, 0.000
      1275.0    275    3 SAFE      0.000, 0.000, 0.000 <-
      1280.0    280    3 UNSAFE    0.630, 0.494, 0.734 <-
      1290.0    290    3 UNSAFE    0.845, 0.847, 0.854
    inversions: 0
    terminal endpoint decided by a MARGINAL: no

--- E1 c50/C0   bracket rl [975, 980]
    achieved     rl    n class     vSLO
      1889.8    890    3 SAFE      0.000, 0.000, 0.000
      1939.0    940    3 SAFE      0.000, 0.000, 0.000
      1956.4    965    3 SAFE      0.000, 0.000, 0.000
      1960.0    970    3 SAFE      0.000, 0.000, 0.000
      1964.2    975   15 SAFE      0.000, 0.000, 0.000 <-
      1966.8    980    3 UNSAFE    0.250, 0.102, 0.267 <-
      1971.8    990    3 UNSAFE    0.601, 0.599, 0.547
    inversions: 0
    terminal endpoint decided by a MARGINAL: no

--- E1 c50/C1   bracket rl [370, 375]
    achieved     rl    n class     vSLO
      1339.9    340    3 SAFE      0.000, 0.000, 0.000
      1360.0    360    3 SAFE      0.000, 0.000, 0.000
      1370.0    370    3 SAFE      0.000, 0.000, 0.000 <-
      1374.9    375    3 UNSAFE    0.097, 0.297, 0.236 <-
      1380.0    380    3 UNSAFE    0.650, 0.737, 0.767
    inversions: 0
    terminal endpoint decided by a MARGINAL: no

--- E2 c10@Q2500   bracket rl [825, 830]
    achieved     rl    n class     vSLO
      1825.0    825   12 SAFE      0.000, 0.000, 0.000 <-
      1829.8    830    3 UNSAFE    0.255, 0.325, 0.263 <-
      1834.4    835    3 UNSAFE    0.627, 0.590, 0.497
      1841.4    865    3 UNSAFE    0.828, 0.834, 0.828
      1841.8    905    3 UNSAFE    0.867, 0.866, 0.866
      1842.2    845    3 UNSAFE    0.758, 0.739, 0.760
    inversions: 0
    terminal endpoint decided by a MARGINAL: no

--- E2 c50@Q500   bracket rl [975, 980]
    achieved     rl    n class     vSLO
      1964.6    975   12 SAFE      0.000, 0.000, 0.000 <-
      1967.8    980    3 UNSAFE    0.248, 0.221, 0.140 <-
      1971.6    990    3 UNSAFE    0.610, 0.591, 0.569
      1973.6   1000    3 UNSAFE    0.659, 0.591, 0.618
      1977.4   1025    3 UNSAFE    0.717, 0.706, 0.681
      1981.0   1075    3 UNSAFE    0.754, 0.759, 0.759
    inversions: 0
    terminal endpoint decided by a MARGINAL: no

--- E2b C=400   bracket rl [190, 195]
    achieved     rl    n class     vSLO
       380.0    180    3 SAFE      0.000, 0.000, 0.000
       390.0    190   12 SAFE      0.000, 0.000, 0.000 <-
       395.0    195    3 UNSAFE    0.701, 0.667, 0.681 <-
       400.0    200    3 UNSAFE    0.818, 0.811, 0.804
    inversions: 0
    terminal endpoint decided by a MARGINAL: no
```

```
TOTAL inversions across all seven cells: 0
Terminal endpoints decided by a MARGINAL: 0
```

**What this does and does not establish.** It establishes that the recorded
classifications are monotone in achieved rate and that no bracket endpoint rests
on a MARGINAL. It does **not** establish that the search could not have been
truncated early: bisection only ever probes the rates it chooses, so a
hypothetical non-monotonicity at an unprobed rate is invisible by construction.
The audit can only speak for the 40 points that exist.

Note also that the vSLO separation at every bracket is large. The smallest jump
from last SAFE to first NON-SAFE is E1 c10/C0, going from 0.000 on all three
replicates to 0.077, 0.000, 0.135 — and that point classifies UNSAFE on two of
three replicates exceeding 0.05, with the third at exactly zero. **That is the
weakest bracket in the study and the closest any point comes to the MARGINAL
band.** It is E1's headline cell.

---

## 2. The denominator (blocking)

**Two denominators are in use, and they are never mixed within a single table or
figure.** A third appears only as a prediction.

`C_staffed` is not a distinct quantity here: `concurrency = ceil(C·S)` is exact
in all seven cells, so `concurrency/S` equals `C_config` identically. There is no
ambiguity from that source.

| quantity | denominator | defined by | value |
|---|---|---|---|
| `rhoAchieved` in every boundary file | **C_config** | `fault_capacity()` in `scripts/locate_boundary.py`, which returns the capacity from the run's own schedule | 2000, 1400 or 400 |
| "effective utilisation" in E2d and A6 | **C_measured** | max sustained 30 s served rate, `scripts/capacity_calibration.py` | 1828.6 … 392.7 |
| predicted plateaus in E2e | **C_model** | `concurrency/(S+delta)` | 1987.4, 1997.7 |

### Location by location

| location | figure or table | denominator |
|---|---|---|
| E1-REPORT.md, the four rho* intervals | table | C_config |
| E2-REPORT.md, the 2x2 and per-point tables | tables | C_config |
| E2B-REPORT.md, rho* interval and per-point | tables | C_config |
| E2C-REPORT.md, all rho* values | tables | C_config |
| E2D-REPORT.md, "rho* vs configured C" column | table | C_config |
| E2D-REPORT.md, "effective vs true capacity" column | table | **C_measured** |
| E2D-REPORT.md, the collapse figures | prose | **C_measured** |
| A6-REPORT.md, "rho at last SAFE" column | table | C_config |
| A6-REPORT.md, "ceiling" column | table | C_measured / C_config, a ratio of the two |
| A6-REPORT.md, "effective at last SAFE" | prose, 0.993–1.000 | **C_measured** |
| W2 response, all resolution arithmetic | tables | C_measured |
| **F5, left axis** | figure | C_config |
| **F5, right axis** | figure | **C_measured** |
| F4 | figure | rates, no denominator |
| F6 | figure | C_config |

**The 0.9931–0.9999 range quoted from E2d and A6 uses C_measured.** A6's own
definition of rho against C_d is C_config, so the two coexist in A6: the
"rho at last SAFE" column is C_config and the "effective" prose figure is
C_measured. That is the one place a reader could conflate them, and Section 6
should name the denominator at every use.

---

## 3. A5 chronology (blocking for C3)

**The A5-dependent analysis used the same data A5 saw. It must be labelled
exploratory.**

| event | commit | timestamp (UTC) |
|---|---|---|
| E1 corpus collected | — | 2026-09-11 17:44:37 → 2026-09-12 02:43:58 |
| **A5 frozen** | **`fe36734`** | **2026-09-12 07:31:30** |
| E2e corrected-harness corpus collected | — | 2026-09-13 18:10:27 → 21:45:51 |

The leading-indicator analysis reads only the four E1 boundaries.
`scripts/leading_indicator.py` and `scripts/noise_scale_sensitivity.py` contain
**zero** references to `results/e2`, `e2b` or `e2e`, and
`results/E1-leading-indicator.json` covers exactly `c10-C0, c10-C1, c50-C0,
c50-C1`. The E1 corpus predates A5 by about five hours, and it is the data in
view when mean was changed to median.

So, precisely:

- **The corrected-harness dataset was collected after A5 was frozen** — by about
  34 hours — **and was not used in choosing mean over median.** On that half of
  the test it is independent.
- **But the Section 7 signal-selection result as currently computed does not use
  it.** The statistic that A5 governs is the 3-sigma warning criterion, and that
  is computed on E1 data only.

**Therefore C3 cannot be claimed as independent confirmation on the present
analysis.** Two honest routes: label C3 exploratory, or re-run the
leading-indicator analysis over the E2e corrected corpus, which is committed and
would need no new runs. The second is the stronger paper, and it is cheap. It is
not done here because it changes a result rather than auditing one.

Note that F6, the figure captioned as signal-selection evidence, plots queue
depth and tail latency directly and **does not use the noise statistic at all**,
so A5 does not bear on it. If Section 7's claim rests only on F6, A5 is
irrelevant to it; if it rests on the 3-sigma warning result, A5 applies and the
label is exploratory.

---

## 4. Host-stall exclusion

### What triggers it

From the per-run record's own `stallDetector` block, so it is recorded with every
run rather than only in the code:

```
p99Factor        5      live AND recovery 1 s p99 must both exceed 5x their rolling baseline
queuedMax        5      while the downstream queue is at or below 5
gapMs            150    and the max inter-sample gap exceeds 150 ms
baselineWindow   30     baseline is a 30-sample rolling median
contaminationSec 5      a flagged second contaminates the following 5
```

All four conditions must hold simultaneously.

### Was it registered in advance

**Yes.** The criteria appear in `PRE-REGISTRATION.md` and the runner comment
states they are "fixed in advance; flagged seconds are counted and reported,
never silently dropped". `vSLO_raw` — the unexcluded value — is written to every
run record, which is what makes item 4's recomputation possible at all.

### Can genuine overload trigger it

**Only if the queue is simultaneously near-empty.** The `queued <= 5` condition
is what separates the two cases: under genuine recovery overload the queue is
deep, by construction — at the collapsed points it reaches its cap of 500 or
2500. A stall with a deep queue cannot be flagged. The residual risk is a genuine
overload whose queue happens to sit at or below 5 while both latency percentiles
spike fivefold, which is not a configuration this harness produces.

### How much was excluded

```
4. HOST-STALL EXCLUSION
==============================================================================
class        runs    w/ excl     excluded s as %% of T_full
SAFE          111          0              0       0.000%
UNSAFE         60          0              0       0.000%
total excluded: 0 seconds across 0 runs of 171
```

**Zero seconds were excluded, in zero runs of 171.** The detector never fired
anywhere in the reported corpus. Consequently:

- The exclusion rate is neither balanced nor concentrated: it is **empty**.
- `vSLO` and `vSLO_raw` are identical in every run.
- **No headline boundary classification changes under `vSLO_raw`, in any cell.**
  The recomputation was run per point and is reported as no-change rather than
  assumed.

The honest reading is that the stall detector is an unexercised safeguard in this
corpus. It cannot be cited as evidence that stalls were handled correctly,
because none occurred; it can only be cited as evidence that the results do not
depend on it.

---

## 5. Injector 429s and run validity

### The guard

`-gen-tolerance`, default **0.01**, i.e. **±1%**, enforced at
`runner/main.go:415`. It compares the injector's issue rate over the **warm-up
window** against the target, and on breach marks the run invalid, writes the
record and aborts before the fault. Two such aborts occurred before the E1
campaign proper and are documented in A3 as guard aborts, not measurements.

**The guard checks warm-up only.** It does not re-check during the drain, which
is exactly the window the reviewer is worried about. So the guard alone does not
answer the question, and the drain was measured directly.

### 429s and delivery

```
5. INJECTOR 429s AND DELIVERY DEFICIT
==============================================================================
class        runs   total 429s     max 429s    max deficit worst accuracy
SAFE          111            0            0        0.0000%       99.9607%
UNSAFE         60            0            0        0.0000%       99.9225%
```

**Zero 429s in all 171 runs, in both classifications.** The injector never
dropped a request.

Measuring the concern directly — issue rate against target **within the drain
window**, which the guard does not cover:

| classification | runs | median deficit | worst run median | worst single tick |
|---|---:|---:|---:|---:|
| SAFE | 111 | 0.0003% | 0.0099% | 2.31% |
| UNSAFE | 60 | 0.0002% | 0.0087% | 1.53% |

**No SAFE run has an in-drain delivery deficit above half the ±1% guard.** The
worst sustained figure is 0.0099%, a hundredth of a percent, two orders of
magnitude inside the guard. The worst single one-second tick reaches 2.31%, but
that is one sample and not a sustained deficit.

The mechanism the reviewer describes — the injector dropping more as load rises,
making the downstream look artificially safe — **is not present in this data.**
Delivery is if anything marginally better in the UNSAFE runs than the SAFE ones.

---

## 6. n=12 coverage

**The claim must be scoped. It does not cover every cell, and it covers no
first-NON-SAFE endpoint at all.**

```
6. n=12 COVERAGE
==============================================================================
cell               rl    n class     is a terminal endpoint?
E1 c10/C0         825   15 SAFE      last SAFE
E1 c10/C1           -    - -         NO n>=12 POINT
E1 c50/C0         975   15 SAFE      last SAFE
E1 c50/C1           -    - -         NO n>=12 POINT
E2 c10@Q2500      825   12 SAFE      last SAFE
E2 c50@Q500       975   12 SAFE      last SAFE
E2b C=400         190   12 SAFE      last SAFE
```

```
cells with an n>=12 point: 5 of 7
n>=12 points that ARE a terminal bracket endpoint: 5
first NON-SAFE endpoints at n>=12: 0
```

- **Two cells have no replicated point at all**: E1 c10/C1 and E1 c50/C1, both
  reduced-capacity regimes. Every point in them is n=3.
- **Every replicated point is a last-SAFE endpoint.** Not one first-NON-SAFE
  endpoint was replicated.
- So the 24%-of-one-step figure is measured on **safe-side endpoints in five of
  seven cells**, and generalising it to all n=3 estimates — including every
  unsafe-side endpoint and both C1 cells — is an extrapolation, not a
  measurement.

Suggested scoping for Section 4: *"At the five last-SAFE points replicated to
n≥12, run-to-run spread is at most 24% of one bisection step. No first-NON-SAFE
endpoint and neither reduced-capacity cell was replicated, so this bounds
safe-side variability only."*

---

## 7. A6's commit hash

`c3aee75` — full hash
`c3aee75a2d9a7c1049302240b5437b8e7bb1d9da`, committed 2026-09-13 19:08:18 -0400
(23:08:18 UTC), message *"PRE-REGISTRATION A6: A4 is invalid at collapsed points;
report rate, not utilisation, there"*.

---

## Summary for Section 4

| item | outcome |
|---|---|
| 1. monotonicity | **clean** — 0 inversions, 0 MARGINAL anywhere |
| 2. denominator | **two in use**, never mixed within a table; 0.993–1.000 is C_measured |
| 3. A5 chronology | **unflattering** — C3 is exploratory as currently computed |
| 4. stall exclusion | **clean but unexercised** — 0 seconds excluded, no classification changes |
| 5. 429s and delivery | **clean** — 0 drops, worst sustained deficit 0.0099% |
| 6. n=12 coverage | **unflattering** — 5 of 7 cells, safe-side endpoints only |
| 7. A6 hash | `c3aee75` |

Two of the seven are unflattering and neither was softened. Item 1, which the
reviewer expected to be the worst, is the cleanest.
