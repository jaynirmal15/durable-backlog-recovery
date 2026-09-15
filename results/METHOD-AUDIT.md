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

---
---

# Round 2 — three more questions from the Section 4 review

Generated by `scripts/endpoint_sensitivity.py` (items 8 and 9) and by replaying
the committed search planner against each cell's observed classifications
(item 10). Read-only; no new runs.

## 8. Which endpoint is quoted

### The answer

**The maximum across the last SAFE point's repetitions.**

It is produced at **`scripts/collapsed_estimator_audit.py:108`**:

```python
lo, hi = min(pt['rhoAchieved']), max(pt['rhoAchieved'])
```

stored as `rhoAtLastSafe = [lo, hi]` (line 112), and the single number is
selected at **`scripts/make_figures.py:66`**:

```python
yield k, c['reported']['rhoAtLastSafe'][1], last['a4Rate'] / c['plateau']
```

`[1]` is `hi`. That value is the configured-ρ axis of **F5-collapse** (`f5()`
line 253, `data = list(cells())`).

### A finding that fell out of locating it

The **two axes of F5 use different aggregators.** The configured-ρ axis is the
`max` above; the effective-ρ axis on the same line of the same function is
`a4Rate / plateau`, and `a4Rate` is a **median** (`collapsed_estimator_audit.py:53`,
`med = statistics.median(rates)`). Nothing in the code or the captions says so.

The repo holds five conventions in all. None is wrong on its own; none is
declared:

| site | quantity | aggregation |
|---|---|---|
| `locate_boundary.py:466` | `rhoStarInterval` | `min(lastSAFE) … max(firstNonSAFE)` — no aggregation, full span |
| `collapsed_estimator_audit.py:108` | `rhoAtLastSafe` | `[min, max]` pair |
| `make_figures.py:66` | F5 configured axis | **max** |
| `make_figures.py:66` | F5 effective axis | **median** (via `a4Rate`) |
| `collapsed_estimator_audit.py:53` | `a4Rate`, `a4Rho` | median |
| `method_audit.py:61` | monotonicity ordering | median |
| `leading_indicator.py:80` | per-point ρ | **mean** |
| `e2_report.py:282` | monotonicity sequence | **max** |
| `e2e_analysis.py:111` | E2e point ρ | median |
| `capacity_calibration.py:206` | calibration endpoints | `min` / `max` of the respective endpoints |

### Sensitivity: min / max / mean / median

**(a) Monotonicity audit — unchanged.** 0 inversions under all four
aggregators, in all seven cells. Stronger than that: the aggregator never
reorders the points at all. The rank order by achieved rate is identical under
min, max, mean and median in every cell, so the audit is not merely robust, it
is reading the same sequence each time.

**(b) Last SAFE point — unchanged, and cannot change.** `class` comes from
`classify(vslos)`, and `rhoAchieved` is not an input to it. Verified explicitly
across all seven cells: `lastSafeRl` is 825, 275, 975, 370, 825, 975, 190 under
every aggregator. The bracket `[lastSafeRl, firstNonSafeRl]` is a property of the
classification and no choice of endpoint can move it.

**(c) The 0.993–1.000 headline — unchanged after resolution-matched rounding.**

| cell | C_d | plateau | min | max | mean | median |
|---|---|---|---|---|---|---|
| E1 c10/C0 | 2000 | 1828.6 | 0.998 | 0.998 | 0.998 | 0.998 |
| E1 c10/C1 | 1400 | 1280.9 | 0.995 | 0.995 | 0.995 | 0.995 |
| E1 c50/C0 | 2000 | 1964.3 | 1.000 | 1.000 | 1.000 | 1.000 |
| E1 c50/C1 | 1400 | 1375.7 | 0.996 | 0.996 | 0.996 | 0.996 |
| E2 c10@Q2500 | 2000 | 1827.1 | 0.999 | 0.999 | 0.999 | 0.999 |
| E2 c50@Q500 | 2000 | 1964.8 | 1.000 | 1.000 | 1.000 | 1.000 |
| E2b C=400 | 400 | 392.7 | 0.99 | 0.99 | 0.99 | 0.99 |

Every cell is identical to the reported resolution under all four. **None of the
three changes. This is a reporting detail, not a real issue.**

The reason is worth stating rather than asserting: the largest within-point
achieved-ρ spread anywhere in the corpus is **0.0010** (E2 c50@Q500, rl=1025),
i.e. 2 rps. The rounding step is 0.001 and the search resolution is 0.0025. The
repetitions agree more tightly than either, so there is no room for the choice of
endpoint to matter.

### Two things that are nonetheless worth fixing

1. **`max` puts two cells above 1.0.** Unrounded, the effective utilisation at
   the last SAFE point under `max` is **1.0002** for E1 c50/C0 and 1.0002 for
   E2 c50@Q500 — above each cell's own measured plateau, which is the same class
   of impossibility A6 was written to remove. Under min, mean and median both sit
   at 0.9995–0.9999. The A6 report's sentence *"every cell sits BELOW 1.0, at
   0.9931 to 0.9999"* is therefore true under the estimator A6 uses (median) and
   **false under the aggregator F5 plots on its other axis** (max). It does not
   survive to the reported resolution — both round to 1.000 — but the claim as
   written is aggregator-dependent and should be stated as "at or just below 1.0
   at the resolution the search supports", which is how A6-REPORT §7 already
   phrases the defensible version.

2. **The headline's own precision is mixed.** "0.993 to 1.000" takes its lower
   end from **E2b at C=400**, the one cell the resolution-matched rule restricts
   to two decimals (5/400 = 0.0125). Under the rule the lower end is **0.99**.
   The honest headline is "0.99 to 1.000" with the precision difference stated,
   or "0.99 to 1.00" at the coarsest common resolution. The three-decimal lower
   end is not supported by the cell it comes from.

Also noted, not a result: **F5 prints both spreads to four decimals**
(`'spread\n%.4f'`, `make_figures.py:277`), which the same rule disallows for a
utilisation quantity. Recomputed with one aggregator on both axes the collapse
factor is 11.0× (min), 10.2× (max), 10.6× (mean), 10.5× (median), against 10.5×
as published with the mixed pair. The order-of-magnitude claim is untouched; the
single-decimal factor moves by 0.8× across the choice.

## 9. Did the spread diagnostic ever fire

**No. Zero times, in any cell, at any point.**

40 points examined across the seven boundary files. `flaggedCount` is 0 in every
file and `spreadExceedsResolution` is `false` at every individual point,
endpoints included. **No flagged point exists, so the question of whether a
flagged point was a bracket endpoint does not arise.**

| file | points | max spread | resolution | flagged |
|---|---|---|---|---|
| `results/boundaries/c10-C0.json` | 6 | 0.0001 | 0.0025 | 0 |
| `results/boundaries/c10-C1.json` | 6 | 0.0000 | 0.0036 | 0 |
| `results/boundaries/c50-C0.json` | 7 | 0.0006 | 0.0025 | 0 |
| `results/boundaries/c50-C1.json` | 5 | 0.0001 | 0.0036 | 0 |
| `results/e2/c10-Q2500/boundaries/c10-C0.json` | 6 | 0.0003 | 0.0025 | 0 |
| `results/e2/c50-Q500/boundaries/c50-C0.json` | 6 | 0.0010 | 0.0025 | 0 |
| `results/e2b/boundaries/c50-C0.json` | 4 | 0.0000 | 0.0125 | 0 |

The worst point in the corpus sits at **40% of its own resolution**
(0.0010 / 0.0025). A3's escalation rule — "more than two flagged points across E1
moves the consumer limiter to a deadline pacer before E2 and re-runs the affected
boundaries" — was never approached: E1 flagged none of 24.

**The diagnostic was recomputed under A4, not inherited.** `recompute_rho.py:107`
calls `pt.update(spread_diagnostic(new_rhos, cap or 2000))` on the recomputed
values and rewrites `flaggedRates`/`flaggedCount` at line 124, so these are A4
spreads, not stale drain-window ones. The denominator was also correct in each
file: recorded `rhoResolution` back-solves to C_d = 2000, 1400, 2000, 1400, 2000,
2000, 400 — in particular E2b used 5/400 = 0.0125 and did **not** silently take
the `cap or 2000` fallback.

### Two caveats, both unflattering

- **The two corrected-harness cells have no spread diagnostic at all.**
  `results/e2e/boundaries/` is an **empty directory**. The E2e cells were
  assembled by `scripts/e2e_analysis.py` directly from per-run records, which
  stores a single already-aggregated `rho` per point
  (`statistics.median(ach) / C_D`, line 111) and never keeps the per-repetition
  list. So A3's check was never run on the corrected harness — the campaign whose
  boundaries the paper's headline rests on. Nothing suggests it would have fired;
  the point is that it was not asked.
- `recompute_rho.py:107` passes `cap`, the loop variable left over from the last
  run processed, rather than the point's own capacity. It is harmless here
  because every run in a boundary shares `faultCapacity` (confirmed by the
  denominator check above), but it would bind silently if a point ever mixed
  capacities, and `cap or 2000` would then substitute a wrong denominator without
  a warning.

## 10. Initial bracket construction

The Method documents bisection given a floor and a ceiling, and A2 documents the
non-SAFE anchor. This is the missing third path, read out of
`scripts/locate_boundary.py` rather than reconstructed.

### The procedure, mechanically

The search takes `--anchor` (**required**) and `--hi` (**optional**, help text:
*"known first non-SAFE rate (MARGINAL or UNSAFE), if any"*). `search()` runs
three gates in order:

1. **Anchor** (line 378–380). `probe_once(args.anchor)`; `lo = args.anchor`,
   `hi = args.hi`.
2. **A2 descent** (382–400), only if the anchor is not SAFE. The anchor becomes
   the ceiling, `lo = None`, and `downward_step` takes 10% decrements rounded to
   5 rps until a SAFE point is found; reaching the 5 rps floor raises
   `SystemExit` rather than forcing an interval.
3. **Ceiling** (401–420), the part not previously documented:

```python
if hi is not None:
    hi_pt = probe_once(hi)
    if hi_pt['class'] == 'SAFE':
        log('  supplied ceiling %d is SAFE; falling back to upward search' % hi)
        lo, hi = hi, None

if hi is None:
    log('no UNSAFE ceiling known: stepping upward in 10% increments')
    while True:
        cand = upward_step(lo)
        pt = probe_once(cand)
        if pt['class'] == 'SAFE':
            lo = cand
            continue
        hi = cand
        break
```

Answering the three parts directly:

- **How the first candidate ceiling is chosen.** If `--hi` is given, it *is* the
  first candidate. If not, the first candidate is `upward_step(lo)` =
  `lo + max(5, round(lo * 0.10 / 5) * 5)` — the floor plus 10%, rounded to the
  5 rps grid, with a 5 rps minimum (line 120).
- **Is it always freshly probed on the corrected harness.** **Yes, and not only
  there — unconditionally, on every harness.** Line 402 is
  `hi_pt = probe_once(hi)` with no guard: a supplied ceiling is measured before
  it is used. There is no code path that adopts a ceiling on assertion. Every
  probe, supplied ceiling included, is appended to `points`, so **every rate in
  every boundary file is a rate that was actually run** at this campaign's `--n`.
- **What happens if that candidate is still SAFE.** Two distinct behaviours,
  both no-fail:
  - a **supplied** `--hi` that comes back SAFE is *promoted to the floor*
    (`lo, hi = hi, None`) and the upward search restarts from it, with a log line
    naming the fallback. The stale ceiling is not discarded — it is retained as
    a measured SAFE point and widens nothing.
  - a **stepped** candidate that comes back SAFE becomes the new floor and the
    loop takes another 10% step. The upward loop has **no probe budget and no
    terminating guard** — it exits only on a non-SAFE classification. (The
    downward loop, by contrast, has the 5 rps floor check. The asymmetry is real:
    a cell with no reachable non-SAFE rate would step upward indefinitely. In
    practice the injector ceiling bounds it, but the code does not.)

### Which path each campaign actually took

The boundary files record `arm`, `regime` and `preRegistration`, but **not the
command line** — `build_output()` has no `args` echo. So `--hi` cannot be read
off the artefact. It can, however, be *tested*: replaying the committed planner
`plan(anchor, hi, oracle)` against each cell's own observed classifications, and
requiring that the planned probe set equal the observed probe set exactly with no
unprobed rate demanded, admits these solutions:

| cell | observed probes | exact reconstruction | path |
|---|---|---|---|
| E1 c10/C0 | 755, 800, 820, 825, 830, 840 | `--anchor 840`, no `--hi` | A2 descent, then bisect |
| E1 c10/C1 | 240, 255, 260, 275, 280, 290 | **none** | see below |
| E1 c50/C0 | 890, 940, 965, 970, 975, 980, 990 | `--anchor 990`, no `--hi` | A2 descent, then bisect |
| E1 c50/C1 | 340, 360, 370, 375, 380 | `--anchor 380`, no `--hi` | A2 descent, then bisect |
| E2 c10@Q2500 | 825, 830, 835, 845, 865, 905 | `--anchor 825`, no `--hi` | upward search, then bisect |
| E2 c50@Q500 | 975, 980, 990, 1000, 1025, 1075 | `--anchor 975`, no `--hi` | upward search, then bisect |
| E2b C=400 | 180, 190, 195, 200 | `--anchor 180` or `200`, no `--hi` | either direction reaches it |

**Six of seven reconstruct exactly, and every one of them with `--hi` absent.**
The upward-search path is therefore not a dormant branch: it is how the three
E2/E2b brackets were built, and the A2 descent is how three of the four E1
brackets were built.

**E1 c10/C1 does not reconstruct under any single invocation.** The closest is
`--anchor 290`, no `--hi`, which explains 260, 275, 280 and 290 and leaves
**240 and 255 unexplained** — two SAFE points below the floor the descent found.
No `(anchor, hi)` pair drawn from its own probed rates produces them. The
consistent reading is more than one invocation, or points probed outside the
search; the artefact cannot distinguish those, because it does not record the
invocation.

> **CORRECTED IN ITEM 12.** The last sentence is wrong. The artefact *does*
> distinguish them: the run ids at rl=240 and rl=255 carry the `e1b-` prefix,
> marking them as E1B probes rather than search probes. With E1B separated, this
> cell reconstructs exactly, like the other six. See item 12.

### The gap, stated as a gap

This is the concrete reproducibility defect: **`locate_boundary.py` does not
record its own arguments in its output.** A reader cannot tell from
`results/boundaries/c10-C1.json` how its six rates were chosen, and for that one
cell the answer is not recoverable at all. The fix is one dictionary in
`build_output()` echoing `vars(args)`; it would help every future run and none of
the committed ones. I have not applied it — it changes the frozen search driver
after the campaigns closed, and that is your call, not mine.

---

## Summary for Section 4 — round 2

| item | outcome |
|---|---|
| 8. quoted endpoint | **max**, at `collapsed_estimator_audit.py:108` → `make_figures.py:66`; none of (a), (b), (c) changes under min/max/mean/median — a reporting detail, not a real issue |
| 8, incidental | **unflattering** — F5's two axes use different aggregators; under `max` two cells sit at 1.0002, above their own plateau; the headline's "0.993" lower end comes from the one cell restricted to two decimals |
| 9. spread diagnostic | **never fired** — 0 of 40 points, worst at 40% of its resolution; but **not computed at all for the two corrected-harness cells**, whose boundaries directory is empty |
| 10. initial bracket | documented above; `--hi` optional, always freshly probed, a SAFE ceiling is promoted to floor; six of seven cells reconstruct with no `--hi` — **seven of seven once E1B is separated, see item 12** |

---
---

# Round 3 — dataset map and the E1 c10/C1 provenance gap

## 11. Which data support which claim

### A prior note on the labels

The labels C1, C2 and C3 appear in **no committed artefact**. They exist only in
the paper draft, which is not in this repository. Everything below is therefore
mapped by *description* — "the seven-cell boundary result", "predict and
eliminate" — and the reader has to carry the label across. **That is itself part
of the reviewer's objection**, and the cheapest fix is to name the datasets in
the paper by their directory, which is unambiguous, rather than by a claim label
that has no definition on disk.

### The seven cells: confirmed, E1 x4 + E2 x2 + E2b x1

Your recollection is correct. All seven are produced by
`scripts/locate_boundary.py` and enumerated identically in three places
(`method_audit.py:15`, `collapsed_estimator_audit.py:23`,
`capacity_calibration.py:61`, `reviewer_w2_analysis.py:24`):

| # | cell | boundary file | points | runs |
|---|---|---|---|---|
| 1 | E1 c10/C0 | `results/boundaries/c10-C0.json` | 6 | 30 |
| 2 | E1 c10/C1 | `results/boundaries/c10-C1.json` | 6 | 18 |
| 3 | E1 c50/C0 | `results/boundaries/c50-C0.json` | 7 | 33 |
| 4 | E1 c50/C1 | `results/boundaries/c50-C1.json` | 5 | 15 |
| 5 | E2 c10@Q2500 | `results/e2/c10-Q2500/boundaries/c10-C0.json` | 6 | 27 |
| 6 | E2 c50@Q500 | `results/e2/c50-Q500/boundaries/c50-C0.json` | 6 | 27 |
| 7 | E2b C=400 | `results/e2b/boundaries/c50-C0.json` | 4 | 21 |

40 points, 171 runs.

**The seven cells are self-contained.** Their effective-utilisation denominator,
`trueCapacity`, is computed per cell from *that cell's own* UNSAFE-point run
records — `capacity_calibration.py:61-74` globs `results/c10-c0-rl*`,
`results/e2/c10-Q2500/*` and so on — not from E2e. No E2e measurement flows into
any number in the seven-cell result.

### The two E2e cells are SEPARATE. They are not members of the seven.

`results/e2e/boundaries/` is an empty directory; the E2e cells were never built
by `locate_boundary.py`. They live in `results/E2E-analysis.json`, assembled by
`scripts/e2e_analysis.py` from `results/e2e/e2e-*-r*.json` (33 run records).

What they support, exhaustively — every consumer of `results/e2e`:

| consumer | what it takes from E2e |
|---|---|
| predict-and-eliminate (the "corrected" campaign) | both cells: plateau gates, boundary brackets, in-situ overhead |
| **F3** `F3-overhead-measured` | **neither cell** — `results/e2e/exp1-s5-load90.json` and `exp1-s25-load90.json`, the direct-observation runs, not the boundary probes |
| **F4** `F4-plateau-predicted-measured` | **two of its four bars** (`E2E['c10']`, `E2E['c50']`) |
| **F6** `F6-signal-selection` | the **c10 cell only** |
| **A7** | both cells, via `leading_indicator_corrected.py` reading `results/e2e/` |
| `reviewer_w2_analysis.py` | both cells, for the fit-vs-test separation |

And what they do **not** support: F5, the leave-one-out test
(`loo_overhead.py:25` reads only `results/E2D-capacity-calibration.json`, i.e.
the seven cells), the capacity calibration, the monotonicity audit, the spread
census, or T1 (which is a hand-written narrative table with no data source at
all).

So the overhead constant is **fitted on the seven cells and tested on E2e** —
which is the separation the W2 response claims, and it survives this check.

### Does any cell contributing to the seven-cell result come from the lossy path?

**No. Not one.** Verified directly: in all seven boundary files, every point's
`rhoAchieved` is a list whose length equals `len(point['runs'])`, and every
individual run carries its own `rhoAchieved`. 171 of 171 repetitions retain their
own rate.

The lossy path is **E2e, and only E2e**. `e2e_analysis.py:110-111` stores
`achievedRps` and `rho` as a single `statistics.median(ach)` per point; the
per-repetition rate list is not written. The only per-repetition array surviving
in `E2E-analysis.json` is `vSLO`.

**The consequence, stated precisely.** The repetition-level sensitivity analysis
of item 8 — that min, max, mean and median give identical results — covers the
seven cells and therefore F5, and does **not** cover E2e, and therefore does not
cover C2's predict-and-eliminate brackets, F4's two corrected bars, F6 or A7. The
paper must say that. But note which way the limitation points: **it does not
touch the seven-cell result at all.** If the Section 4 sentence means the
seven-cell collapse when it says "the corrected cells on which Section 6's
central comparison rests", it is **wrong on two counts** — those cells are not
the seven, and they are the ones the sensitivity check cannot reach.

Two mitigations, both worth stating rather than leaning on:

1. **The loss is at the analysis layer, not the data layer.** All 33 E2e run
   records are on disk and each carries `backlogAtRestore`, `tDrainSec` and the
   full `timeline`, which is exactly what `e2e_analysis.a4_rate()` consumes. The
   per-repetition rates are re-derivable, so this is repairable by re-running the
   analysis with the list retained — not a lost measurement.
2. **The two corpora are on different rho estimators**, which is a second and
   independent reason not to describe them as one dataset. The seven cells use
   **A4**, the delivery-span estimator (`recompute_rho.py`). E2e uses the
   **as-measured / drain-window** estimator. This is documented and deliberate —
   `results/E2E-REPORT.md` §"The estimator disagreement is as large as the
   effect" and E2E-PLAN addendum 5.

   > **CORRECTED IN ITEM 14.** This paragraph originally went on to claim that
   > the function computing it is named `a4_rate()` and so contradicts its own
   > body. **That was wrong — there is no `a4_rate` in `e2e_analysis.py`.** The
   > function is `achieved()` (`e2e_analysis.py:47`), and its docstring, "Total
   > delivered rate over the drain", describes what it does accurately. I
   > misattributed the name. The estimator difference above is real and stands;
   > the naming defect does not exist and the summary row has been corrected.

### Which dataset each figure plots

| figure | dataset | detail |
|---|---|---|
| **F3** | E2e, observation runs only | `results/e2e/exp1-s5-load90.json`, `exp1-s25-load90.json` |
| **F4** | **mixed** | bars 1–2 from the seven cells (`CAL['E1 c10/C0']`, `CAL['E1 c50/C0']`); bars 3–4 from E2e (`E2E['c10']`, `E2E['c50']`) |
| **F5** | **the seven cells only** | via `results/A6-collapsed-estimator.json`, which reads the seven boundary files plus the seven per-cell plateaus. No E2e input |
| **F6** | E2e, c10 cell only | `E2E['c10']['points']` |

**F4 is the one to be careful with in the caption.** It is the only figure that
puts the two corpora side by side, its four bars are two datasets on two rho
estimators, and nothing in the current caption says so. The comparison it draws
is legitimate — predicted versus measured plateau is a direct throughput
quantity with no rho estimator involved in either pair — but a reviewer who
notices the mixture and is not told about it will assume the worse reading.

## 12. E1 c10/C1 — does the provenance gap touch any result?

**It does not. Every run is retained and analysed. Nothing is missing.**

### Retention

- **All six rates retained**: 240, 255, 260, 275 (SAFE), 280, 290 (UNSAFE).
- **All repetitions retained**: n=3 at every point, 18 runs total.
- **All classifications retained**, with per-repetition `vSLO` for each:
  240/255/260/275 all `0.0000, 0.0000, 0.0000`; 280 `0.6300, 0.4941, 0.7336`;
  290 `0.8446, 0.8472, 0.8544`.
- **Terminal bracket retained and at resolution**: `lastSafeRl 275`,
  `firstNonSafeRl 280`, `resolutionReachedRps 5`, `firstNonSafeClass UNSAFE`,
  `marginalRates []`.

### Are 240 and 255 analysed, or only recorded?

**Analysed.** They are not inert records:

- `results/E1-leading-indicator.json` — this cell's `safePoints` are
  `[240, 255, 260, 275]`, and every metric's `perPoint` array lists all four. The
  two E1B points are half the evidence in the leading-indicator analysis for this
  cell.
- `results/A6-collapsed-estimator.json` — `safePoints` are
  `[(240, 1240.0), (255, 1255.0), (260, 1260.0), (275, 1275.0)]`.
- The monotonicity audit and the round-2 aggregator sweep iterate all six points.

They are correctly *not* used by F5 (which plots the last SAFE point, 275, only)
or by the plateau fit (UNSAFE points only). That is by design, not omission.

### Is any run absent?

**No, in both directions.**

- Run records on disk matching this cell (`results/c10-c1-rl*-r*.json` plus
  `results/e1b-c10-c1-*.json`): **18**.
- Runs listed in `results/boundaries/c10-C1.json`: **18**.
- Disk records absent from the boundary file: **0**.
- Boundary run ids with no record on disk: **0**.
- Runs carrying `invalid` or `invalidReason`: **0**.

There is no excluded run, so there is no `invalidReason` to inspect. (The search
could not have proceeded past one in any case: `locate_boundary.py:338` raises
`SystemExit` on an invalid run rather than dropping it.)

### The gap is smaller than item 10 said — a correction

Item 10 recorded that E1 c10/C1 "does not reconstruct under any single
invocation" and that "the artefact cannot distinguish" the readings. **The second
half is wrong.** The run ids record the campaign:

| rl | run ids | campaign |
|---|---|---|
| 240 | `e1b-c10-c1-rl240-r1..r3` | **E1B** |
| 255 | `e1b-c10-c1-rl255-r1..r3` | **E1B** |
| 260, 275, 280, 290 | `c10-c1-rl*-r1..r3` | original search |

Separate the two E1B rates and replay the committed planner on what remains:
`plan(anchor=290, hi=None)` over `{260, 275, 280, 290}` returns **exactly those
four rates** — anchor 290 UNSAFE, downward step to 260 SAFE, bisect 275 SAFE,
bisect 280 UNSAFE, terminate at 5 rps. An exact match.

So **all seven cells reconstruct**, every one of them with `--hi` absent, and
this cell is not anomalous. E1B's footprint across the corpus is small and
visible: two new rates here, and additional repetitions at two existing rates
elsewhere (c10/C0 rl=825 to n=15, c50/C0 rl=975 to n=15). It added no new rate to
any other cell.

### Verdict

**The gap affects reproducibility of probe selection, and not the measurements.**
Concretely: a reader cannot reconstruct the exact command line, because
`build_output()` does not echo `vars(args)`. A reader *can* reconstruct which
campaign contributed each rate, from the run-id prefix, and can verify that the
search path is the one the code would have taken. Every probed rate, every
repetition, every classification and the terminal bracket are present and in use.
You can write that.

---

## Summary for Section 4 — round 3

| item | outcome |
|---|---|
| 11a. the seven cells | **confirmed** E1 x4 + E2 x2 + E2b x1, 40 points, 171 runs; self-contained, no E2e input |
| 11b. the E2e cells | **separate, not members**; they support predict-and-eliminate, F3, two of F4's four bars, F6, A7 and the W2 fit-vs-test — not F5, not the LOO, not the calibration |
| 11c. lossy path | **no seven-cell data is lossy** — 171/171 repetitions retain their own rate. E2e alone is lossy, at the analysis layer only, and is re-derivable from its 33 run records. The item-8 sensitivity therefore covers the seven cells and F5 and **does not** cover C2/F4-corrected/F6/A7 — a limitation to state, but one that does not touch the seven-cell result |
| 11d. F4 / F5 | **F5 = the seven cells only. F4 = mixed**, two bars per corpus, on two different rho estimators, and its caption says neither |
| 11e. incidental | ~~naming defect in `e2e_analysis`~~ — **withdrawn, it was my error; see item 14.** The estimator difference between the two corpora is real and stands; the function is `achieved()` and is named accurately |
| 12. E1 c10/C1 | **clean** — 18 of 18 runs retained and analysed, 0 absent, 0 invalid, bracket at 5 rps resolution; 240 and 255 are E1B probes and are used, not merely recorded; the cell reconstructs exactly once E1B is separated. Reproducibility of probe selection only; measurements untouched |

---
---

# Round 4 — the denominator, and the E2e per-repetition rates

Generated by `scripts/denominator_uncertainty.py` →
`results/W7-denominator-uncertainty.json` (item 13) and `scripts/e2e_per_rep.py`
→ `results/W7-e2e-per-repetition.json` (item 14). Read-only; no new runs.

## 13. Uncertainty in C_measured

### More than one measurement exists. Nothing is synthesised.

**Between 6 and 15 plateau measurements exist per cell**, one per UNSAFE run.
`capacity_calibration.py:142-156` computes `max_sustained(rec)` — the highest
30 s sustained served rate in that run's uncontaminated drain window — for every
UNSAFE run of the cell, and `C_measured` is the **median** of that list. The
extremes were already being recorded (`trueCapacityMin`, `trueCapacityMax`); what
was missing is the propagation, not the data.

| cell | n | source runs | min | median (published C) | max |
|---|---|---|---|---|---|
| E1 c10/C0 | 6 | rl 830, 840 (n=3 each) | 1827.96 | **1828.61** | 1829.88 |
| E1 c10/C1 | 6 | rl 280, 290 | 1279.08 | **1280.95** | 1281.99 |
| E1 c50/C0 | 6 | rl 980, 990 | 1962.68 | **1964.33** | 1965.26 |
| E1 c50/C1 | 6 | rl 375, 380 | 1375.04 | **1375.74** | 1378.30 |
| E2 c10@Q2500 | 15 | rl 830, 835, 845, 865, 905 | 1825.49 | **1827.13** | 1829.49 |
| E2 c50@Q500 | 15 | rl 980, 990, 1000, 1025, 1075 | 1963.72 | **1964.85** | 1965.72 |
| E2b C=400 | 6 | rl 195, 200 | 392.52 | **392.73** | 393.00 |

Per-run values are listed individually in `W7-denominator-uncertainty.json`. Each
recomputed median reproduces the committed `trueCapacity` exactly (asserted in
the script, not eyeballed).

### Spread

| cell | range (rps) | range / C_measured |
|---|---|---|
| E1 c10/C0 | 1.92 | 0.11% |
| E1 c10/C1 | 2.91 | 0.23% |
| E1 c50/C0 | 2.58 | 0.13% |
| E1 c50/C1 | 3.26 | 0.24% |
| E2 c10@Q2500 | 4.00 | 0.22% |
| E2 c50@Q500 | 2.00 | 0.10% |
| E2b C=400 | 0.47 | 0.12% |

The denominator is repeatable to about a quarter of one percent at worst.

### Propagating the extremes into ρ_eff,safe

Numerator held at the published `R_ach,lastSAFE`; denominator swept across the
observed min, median and max. Resolution here is the cell's bisection step in
these units, 5 / C_measured.

| cell | R_ach | at C_max | at C_median | at C_min | span | resolution | span / resolution |
|---|---|---|---|---|---|---|---|
| E1 c10/C0 | 1825.0 | 0.9973 | 0.9980 | 0.9984 | 0.0010 | 0.0027 | **0.38×** |
| E1 c10/C1 | 1275.0 | 0.9945 | 0.9954 | 0.9968 | 0.0023 | 0.0039 | **0.58×** |
| E1 c50/C0 | 1964.2 | 0.9995 | 0.9999 | 1.0008 | 0.0013 | 0.0025 | **0.52×** |
| E1 c50/C1 | 1370.0 | 0.9940 | 0.9958 | 0.9963 | 0.0024 | 0.0036 | **0.65×** |
| E2 c10@Q2500 | 1825.0 | 0.9975 | 0.9988 | 0.9997 | 0.0022 | 0.0027 | **0.80×** |
| E2 c50@Q500 | 1964.6 | 0.9994 | 0.9999 | 1.0004 | 0.0010 | 0.0025 | **0.40×** |
| E2b C=400 | 390.0 | 0.9924 | 0.9931 | 0.9936 | 0.0012 | 0.0127 | **0.09×** |

**Denominator variability is smaller than the search step in every cell**, by
between 1.25× and 11×. It is not negligible: in E2 c10@Q2500 it reaches 80% of
the quoted resolution.

### It does move the headline's upper end

| denominator | headline span, resolution-matched | cells above 1.0 |
|---|---|---|
| C_max | 0.99 – 1.000 | none |
| **C_median (published)** | **0.99 – 1.000** | none |
| C_min | 0.99 – **1.001** | **E1 c50/C0 (1.0008), E2 c50@Q500 (1.0004)** |

Taking the *smallest* of six or fifteen plateau measurements is a one-in-n
extreme, not a confidence bound, so this is not a claim that the true value is
1.001. But it means the headline's robustness is asymmetric: item 8 showed it is
immune to the numerator aggregator, and it is **not** immune to the denominator
at the same resolution. The upper end moves from 1.000 to 1.001 and two cells
cross 1.0. The phrasing "at or just below 1.0 at the resolution the search
supports" survives this; "every cell sits below 1.0" does not.

### Does the quoted per-cell resolution include any of this? No.

`capacity_calibration.py:213` computes

```python
c['resolutionInEff'] = round(RESOLUTION_RPS / c['trueCapacity'], 4)
```

— the 5 rps search step divided by the median plateau. **It is the search step
alone.** Denominator variability is not in it, and no other field carries it.

Sizing the omission by adding the two in quadrature (shown to scale the gap, not
proposed as the paper's number): the quoted resolution understates by 1.00× at
E2b, 1.07–1.20× across the E1 cells, and **1.29× at E2 c10@Q2500**.

### What to write

Both of your options are available, and the stronger one is:

> The per-cell resolution quoted for ρ_eff is the bisection step alone. The
> denominator is itself an estimate — the median of 6 to 15 per-run plateau
> measurements, repeatable to 0.10–0.24% — and propagating its observed extremes
> moves ρ_eff,safe by 0.09 to 0.80 of one bisection step, reaching 1.001 in two
> cells at the lower extreme.

That is not conditional on a single reference and does not need Section 9 cover,
because the repeatability is measured rather than assumed. What does belong in
Section 9 is that the quoted resolution is the search step only, and that a
resolution combining both terms would be up to 1.29× wider.

## 14. E2e per-repetition rates: reconstructed

### The records contain everything needed. The reconstruction is exact.

`e2e_analysis.achieved()` (line 47) computes
`backlogAtRestore / tDrainSec + median(injRate over the drain window)` — the
drain-window as-measured estimator, which is what these cells used. Its three
inputs are `backlogAtRestore`, `tDrainSec` and `timeline`. **All 33 records carry
all three, and all 33 carry `injRate` samples.** Zero records are deficient.

The estimator was not modified, re-derived or approximated: the reconstruction
imports `achieved` from `e2e_analysis` so it cannot drift, and every recomputed
median is checked against the committed `achievedRps` before anything is reported
from it. **All 11 points match exactly**, classes included.

| arm | rl | class | per-repetition rates (rps) | median = committed |
|---|---|---|---|---|
| c10 | 975 | SAFE | 1945.0, 1948.5, 1948.6 | 1948.5 ✓ |
| c10 | 1075 | SAFE | 1966.9, 1967.0, 1969.0 | 1967.0 ✓ |
| c10 | 1185 | SAFE | 1974.6, 1976.7, 1976.8 | 1976.7 ✓ |
| c10 | 1240 | UNSAFE | 1979.6, 1984.8, 1985.4 | 1984.8 ✓ |
| c10 | 1290 | UNSAFE | 1984.2, 1986.0, 1989.6 | 1986.0 ✓ |
| c10 | 1400 | UNSAFE | 1984.1, 1988.2, 1988.4 | 1988.2 ✓ |
| c50 | 975 | SAFE | 1943.3, 1946.5, 1947.7 | 1946.5 ✓ |
| c50 | 1150 | SAFE | 1975.0, 1975.9, 1978.4 | 1975.9 ✓ |
| c50 | 1210 | SAFE | 1980.6, 1983.1, 1987.0 | 1983.1 ✓ |
| c50 | 1275 | UNSAFE | 1986.8, 1988.8, 1992.3 | 1988.8 ✓ |
| c50 | 1400 | UNSAFE | 1985.4, 1991.0, 1992.5 | 1991.0 ✓ |

**The limitation is discharged.** The two sentences in Section 4 can be replaced
by one: the per-repetition rates are recorded in
`results/W7-e2e-per-repetition.json`, regenerable from the run records by
`scripts/e2e_per_rep.py`.

### Per-repetition spread, and the A3 question

| arm | rl | class | spread (rps) | in ρ | vs 5 rps constant | vs this cell's actual resolution |
|---|---|---|---|---|---|---|
| c10 | 975 | SAFE | 3.63 | 0.00182 | . | . |
| c10 | 1075 | SAFE | 2.11 | 0.00105 | . | . |
| c10 | 1185 | SAFE | 2.19 | 0.00110 | . | . |
| c10 | 1240 | UNSAFE | 5.83 | 0.00292 | FLAG | . |
| c10 | 1290 | UNSAFE | 5.42 | 0.00271 | FLAG | . |
| c10 | 1400 | UNSAFE | 4.34 | 0.00217 | . | . |
| c50 | 975 | SAFE | 4.36 | 0.00218 | . | . |
| c50 | 1150 | SAFE | 3.34 | 0.00167 | . | . |
| c50 | 1210 | SAFE | 6.44 | 0.00322 | FLAG | . |
| c50 | 1275 | UNSAFE | 5.47 | 0.00274 | FLAG | . |
| c50 | 1400 | UNSAFE | 7.14 | 0.00357 | FLAG | . |

Against A3's nominal constant, 5 rps / 2000 = 0.0025, **five of eleven points
flag, and one of them (c50 rl=1210) is the last SAFE point and therefore a
bracket endpoint** — exactly the condition A3 exists to catch, and one that never
occurred in the seven cells (0 of 40, item 9).

**That comparison is the wrong one, and I am reporting it only so it is not
discovered later.** A3's rule is that a search must not resolve finer than its own
instrument. These cells **did not resolve to 5 rps**: their brackets are
rl [1185, 1240] and [1210, 1275], widths 55 and 65 rps, and `atRlResolution` is
`false` in both. Their actual resolution in ρ is 0.0275 and 0.0325 — eight to ten
times the largest spread observed. Against the resolution these searches actually
achieved, **no point flags**, and the margin is comfortable.

The honest statement is therefore: E2e's repetition noise is roughly twice the
seven cells' in absolute terms (3–7 rps against under 2), but its search step is
eleven to thirteen times coarser, so the A3 condition is satisfied with more room
than anywhere in the seven-cell corpus, not less.

### Does the predict-and-eliminate result move? No.

| arm | aggregator | bracket | width | mid | registered candidate inside |
|---|---|---|---|---|---|
| c10 | min | [0.9873, 0.9898] | 0.0025 | 0.9886 | 90%-load (0.9894) |
| c10 | max | [0.9884, 0.9927] | 0.0043 | 0.9906 | 90%-load |
| c10 | mean | [0.9880, 0.9916] | 0.0036 | 0.9898 | 90%-load |
| c10 | **median (published)** | **[0.9883, 0.9924]** | 0.0041 | 0.9903 | 90%-load |
| c50 | min | [0.9903, 0.9934] | 0.0031 | 0.9918 | none |
| c50 | max | [0.9935, 0.9962] | 0.0027 | 0.9949 | none |
| c50 | mean | [0.9918, 0.9947] | 0.0029 | 0.9932 | none |
| c50 | **median (published)** | **[0.9915, 0.9944]** | 0.0029 | 0.9929 | none |

The committed brackets are reproduced exactly by the median, and **the verdict is
identical under all four aggregators**: in c10 the 90%-load figure (0.9894) is
inside and the saturated figure (0.9937) is outside; in c50 neither candidate is
inside. So the item-8 sensitivity now covers E2e as well, with the same answer.

This does not disturb E2E-REPORT's finding that the campaign cannot discriminate
the two candidates — that conclusion rests on the disagreement between the
*drain-window and A4 estimators* (0.0080 in ρ, the same size as the effect), not
on repetition scatter within one estimator, and nothing here touches it.

### Does A7 move? No.

`leading_indicator_corrected.py` orders the SAFE points by achieved ρ and then
reads six per-run metrics, none of which is a function of the rate estimator.
Only the ordering could change, and it does not: under min, max, mean and median
the SAFE order is `[975, 1075, 1185]` in c10 and `[975, 1150, 1210]` in c50 in
every case. **A7's result stands unchanged** — the ordering prediction still does
not replicate and the timeout prediction still does.

### A correction to round 3

Item 11 claimed that the function computing E2e's rate is named `a4_rate()` and
so contradicts its own body. **There is no `a4_rate` in `e2e_analysis.py`.** The
function is `achieved()`, and its docstring — "Total delivered rate over the
drain: live issue rate plus recovery" — describes it accurately. I misattributed
the name; the paragraph and the summary row are corrected in place. The
substantive point survives untouched: the two corpora are on different ρ
estimators, and that remains a reason not to describe them as one dataset.

---

## Summary for Section 4 — round 4

| item | outcome |
|---|---|
| 13a. how many | **6 to 15 plateau measurements per cell**, one per UNSAFE run; nothing synthesised, extremes already in the artefact |
| 13b. spread | 0.47–4.00 rps, **0.10%–0.24%** of C_measured |
| 13c. propagation | moves ρ_eff,safe by **0.09× to 0.80× of one bisection step** — smaller than the search step everywhere, but not negligible at E2 c10@Q2500 |
| 13d. T3's resolution | **search step only** — `RESOLUTION_RPS / trueCapacity`. Denominator variability is absent from it; in quadrature the quoted figure understates by up to 1.29× |
| 13e. headline | **unflattering** — at the lowest observed plateau the upper end goes to **1.001** and two cells cross 1.0. "At or just below 1.0" survives; "every cell below 1.0" does not |
| 14a. reconstruction | **yes, exact** — all 33 records carry all three inputs; all 11 medians reproduce the committed values; **the limitation is discharged** |
| 14b. spread | 2.11–7.14 rps per point; flags against A3's nominal 5 rps constant at 5 of 11 points, **but these searches resolved to 55 and 65 rps**, against which nothing flags with room to spare |
| 14c. results | **predict-and-eliminate unchanged** under all four aggregators, verdict identical; **A7 unchanged**, SAFE ordering identical |
| 14d. correction | round 3's `a4_rate` naming defect **was my error and is withdrawn**; the estimator difference it sat beside is real and stands |

---
---

# Round 5 — Section 5 review

Item 19 is generated by `scripts/effect_size_accounting.py` →
`results/W8-effect-size-accounting.json`. Items 15–18 are read out of the
registration history and the exp1/exp2 records. Read-only; no new runs.

## 15. Gate 2's registered estimator

### Neither of your two sentences is true. The registration named A4.

The base registration of the E2e campaign, `results/E2E-PLAN.md` line 88,
committed **`2e18538`, 2026-09-13 12:28:51 -0400**, message *"E2E-PLAN: register
both experiments before touching any code"*:

> Unchanged: bisection to 5 rps, n = 3, **A4 rho over the delivery span**, A3
> spread diagnostic, lanes injector pacer, C0, lambda_L = 1000.

Addendum 1 (`67c448b`, 13:31:47 -0400), which registers ρ* = 0.9937 and 0.9989,
changes no part of that protocol line; its only estimator-adjacent addition is
the outcome row *"both at 1.000 exactly"*. Verified by diff.

So the gate was **not** silent, and it did **not** name the as-measured
estimator. It named A4, and the campaign then adjudicated the gate under the
as-measured estimator instead.

### Gate 2 failed. It fails under both estimators, but only one of them is checkable.

**Under the estimator actually used (as-measured, drain-window):** the brackets
are [0.9883, 0.9924] and [0.9915, 0.9944], midpoints 0.9903 and 0.9929. The
registered values sit outside both brackets, 1.36 and 2.40 bisection steps from
the respective midpoints. The draft's "1.4 and 2.4 steps" is correct.

**Under the registered estimator (A4):** the quoted brackets are [0.9956, 1.0016]
and [0.9999, 1.0064] (E2E-PLAN addendum 5). 0.9937 and 0.9989 fall outside both.
Gate 2 fails here too.

**But that second row is not reproducible from retained data, and the paper
should not lean on it.** Three findings, all unflattering:

1. ~~**The A4 E2e brackets exist in no artefact.**~~ **WITHDRAWN — this was my
   error; see item 23.** They are retained in `results/E2E-a4.json`, a committed
   artefact holding the per-point delivery-span utilisation for both corrected
   cells, from which the quoted brackets derive exactly. What is true is narrower:
   nothing in the repository *wrote* that file and, until item 23, nothing read
   it — `e2e_report.py` hardcoded the numbers instead of reading the artefact
   beside them.
2. **A4 cannot be RE-DERIVED at the c10 arm's last SAFE point.**
   `recompute_rho.delivery_rate()` needs per-arrival timestamps from the consumer
   trace; the 1-second `timeline` cannot supply them, and **0** traces survive at
   c10 rl=1185. Consumer traces are gitignored corpus-wide (`.gitignore`:
   `*.jsonl`, `*.jsonl.*`), so none was ever committed for any campaign. **This
   is not specific to E2e**: no A4 value anywhere in the corpus is re-derivable.
   E1, E2 and E2b preserve theirs inside their boundary files; E2e, which has no
   boundary file, preserves its own in `results/E2E-a4.json`. Retained, not
   re-derivable — the same status throughout.
3. **Where it can be partially checked, it does not reproduce exactly.** c50 has
   traces at rl=1210 and rl=1275 for r1 and r2 but not r3. Recomputing A4 there
   gives ρ 1.0006 and 1.0011 at the last SAFE point and 1.0064 and 1.0076 at the
   first UNSAFE one — a bracket of [1.0006, 1.0076] at n=2, against the quoted
   [0.9999, 1.0064]. Same conclusion, different digits.

### The sentence to write

> The registration designated the delivery-span estimator. The gate was
> adjudicated under the as-measured estimator and fails under it by 1.4 and 2.4
> bisection steps; it fails under the registered estimator too, whose brackets
> are [0.9956, 1.0016] and [0.9999, 1.0064]. Those values are retained rather
> than re-derivable — the consumer traces the delivery-span estimator reads are
> excluded from the repository, as they are for every campaign.

**Gate 2 failed, under both estimators, and both are documented.** *(Revised at
item 23. The first version of this item said the registered-estimator brackets
were reproducible nowhere. They are in `results/E2E-a4.json`; I had not found
it.)*

## 16. Was the saturation pair designated in advance?

**Yes. Before either corrected plateau was measured, and against a tabulated
alternative.**

| time (2026-09-13, −0400) | commit | event |
|---|---|---|
| 12:28:51 | `2e18538` | base registration; protocol names A4 |
| 12:47:47 | `af98ca2` | exp1 records committed — all four direct-probe δ values now exist (0.4947, 0.4914 saturated; 0.5165, 0.5114 at 90% load) |
| **13:31:47** | **`67c448b`** | **addendum 1 registers the saturation pair**, predicting 1987.4 / 1997.7 and ρ* 0.9937 / 0.9989 |
| 14:50:07 | `f032f12` | addendum 2 records mid-campaign: *"the c10 plateau gate passed exactly (measured 1987.4 against 1987.4 predicted)"* |
| 16:32:07 | `96e7063` | the **in-situ** δ first appears in code |
| 17:56:37 | `fa8ca3b` | plateau artefacts committed |

Addendum 1 does not merely assert the choice. It tabulates the competing
candidate and its different prediction —

> | saturated (registered above) | 0.9937 | 0.9989 | 0.0052 | 92.7% |
> | 90% load | 0.9894 | 0.9981 | 0.0087 | 87.7% |

— states the mechanism for preferring it in advance (*"at the last SAFE point the
server runs at about 99% of capacity, where it is essentially never idle"*), and
pre-commits the failure reading: *"If the boundaries land nearer the 90%-load
predictions instead, that is reported as the finding."*

**This is not post-hoc selection among three candidates.** Only **two** existed at
13:31:47; the third, in-situ, was not measured until later that afternoon. It was
a prospective choice between two, with the loser's prediction registered
alongside.

**One honest qualification.** The ordering rests on contemporaneous committed
statements — addendum 1's *"experiment 1 is complete and no boundary run has
started"* and addendum 2's mid-campaign plateau report — not on a timestamp
inside the measurement artefact. `exp2-c10-plateau.json` carries no `startedAt`
field, and its commit time (17:56:37) is after everything. The evidence is a
registration written before the fact rather than a clock inside the datum.

## 17. Plateau repeatability for the corrected cells

### One measurement each. There is no spread. Nothing is synthesised.

`results/e2e/exp2-c10-plateau.json` and `exp2-c50-plateau.json` each contain a
**single scalar** `servedRps` — 1987.3834 and 1998.1460 — from one 60-second
closed-loop saturation window. No sample list, no per-window series, no
replicate. **n = 1 per corrected cell.**

**So the ±0.4 rps agreement cannot be characterised as precision, and "−0.00%"
must not appear.** Quote the raw differences, as the draft already does.

This is a Method-level inconsistency worth stating in its own right: the **seven
cells** carry 6 to 15 plateau measurements each, with a measured repeatability of
0.10–0.24% (item 13). The **corrected cells** — the ones the prospective
prediction is scored against — carry one apiece. The more load-bearing
measurement is the less replicated one.

**What cannot substitute for it.** The corrected cells' highest-rate UNSAFE
boundary runs give delivered-rate spreads of 4.34 rps (c10 at rl=1400) and
7.14 rps (c50 at rl=1400) across three repetitions (item 14). Those are a
different instrument — drain-window delivered rate under a bursty arrival
process, not a closed-loop saturation counter — and must not be quoted as the
plateau's repeatability. They are noted only to show that an order-of-magnitude
guess would be *larger* than 0.4 rps, not smaller, which is the direction that
disfavours the precision reading.

**Write it as a limitation.** The corrected plateau is a single measurement per
arm; its repeatability is unknown; the agreement with the registered prediction
is reported as a raw difference of 0.0 and +0.4 rps and is not evidence of
precision at that scale.

## 18. Load condition and instrument for the attribution figures

Both figures come from the **direct per-request timing probe** — the
`overhead` block of the exp1 records, decomposed into `preSleep`, `sleepExcess`,
`postSleep` and `timer`, over a 60-second window — and both are at the **90% of
capacity** condition, not saturation.

| record | condition | served | total δ | sleepExcess | share | pre+post | pre+post+timer |
|---|---|---|---|---|---|---|---|
| `exp1-s5-sat-on` | saturation | 1819.9 | 0.49470 | 0.49351 | **99.760%** | 1.18 µs | 1.47 µs |
| `exp1-s5-load90` | **90% load** | 1646.0 | 0.51654 | 0.51557 | **99.811%** | 0.97 µs | **1.29 µs** |
| `exp1-s25-sat-on` | saturation | 1961.3 | 0.49144 | 0.49020 | **99.748%** | 1.24 µs | 1.55 µs |
| `exp1-s25-load90` | **90% load** | 1768.0 | 0.51137 | 0.51031 | **99.794%** | 1.05 µs | 1.38 µs |

- **99.8%** is the 90%-load condition. It holds in both arms there (99.81%,
  99.79%). At saturation the long arm gives **99.7%**, so "99.8%" is not a
  condition-free figure. `make_figures.f3()` loads `exp1-s5-load90.json` and
  `exp1-s25-load90.json`, which confirms the figure is drawn at 90% load — though
  the title string *"sleep overshoot is 99.8% of it"* is **hardcoded**
  (`make_figures.py:188`), not computed from the loaded data.
- **1.3 µs** matches `preSleep + postSleep + timer` at **S = 5 ms, 90% load**:
  1.29 µs. It is arm-specific — the same quantity is 1.38 µs at S = 25 — and
  it includes the runtime timer component. Quoted as a single figure it covers
  one arm at one load.

**Two defects found while establishing this:**

1. **The records' own `note` field is wrong.** It states
   *"total = timer + preSleep + sleepExcess + postSleep"*. Numerically, in all
   four records, `total = preSleep + sleepExcess + postSleep` and **excludes**
   `timer` (checked to 1e-6 ms). The code comment in `make_figures.f3()` has it
   right — *"the worker also pays ~0.0003 ms of runtime timer work per request,
   which `total` excludes"* — and the artefact contradicts it. Anyone computing
   the bookkeeping share from the note would get it wrong.
   **FIXED in item 20**, at the source and in all 43 affected records.
2. The 99.8% in the figure title is a literal. If the underlying records are ever
   regenerated it will not follow them.

**What Section 5 should say:** *"…99.8% of the total excess measured by the
per-request timing probe at 90% of capacity (99.76% and 99.75% at saturation),
with bookkeeping and the completion signal together contributing 1.29 µs at
S = 5 ms and 1.38 µs at S = 25 ms under the same condition."*

## 19. Matched-estimator audit of the 94–96% claim (BLOCKING)

### They are not matched. Four dimensions differ, and one of them is the statistic.

**What 0.0706 actually is.** Traced to `capacity_calibration.py:221`:

```python
'rhoStarSpread': round(max(mids_c) - min(mids_c), 4)
```

It is the **range of ρ\* interval midpoints across all seven cells** —
max 0.9830 (E2 c50@Q500), min 0.9124 (E2b C=400) — under A4, where each midpoint
averages the last SAFE endpoint with a **collapsed** non-SAFE endpoint, i.e. the
values A6 ruled invalid.

**`results/E2E-REPORT.md:79` labels it *"E1 midpoints 0.9137 and 0.9826"*. Those
two differ by 0.0689, not 0.0706.** The label is wrong; the number is the
seven-cell range. The report has been describing a range as a two-arm gap.

**What 0.0026 actually is.** The difference between **two** cells' bracket
midpoints, 0.9929 − 0.9903, under the drain-window estimator with a median
aggregator.

| dimension | 0.0706 | 0.0026 | |
|---|---|---|---|
| statistic | **range over seven cells** | **difference between two cells** | **NOT MATCHED** |
| estimator | A4, delivery span | drain-window as-measured | **NOT MATCHED** |
| observation interval | the delivery span | `tDrainSec` | **NOT MATCHED** |
| aggregator | min at one end, max at the other | median at both ends | **NOT MATCHED** |
| denominator | configured C — 2000, 1400 **and** 400 | configured C = 2000 | partially |
| numerator | interval midpoint | interval midpoint | matched |
| collapsed endpoints | included | included | matched, both invalid |

The estimator mismatch alone is worth **0.0080** in ρ by this campaign's own
measurement — three times the corrected residual it is being differenced against.

### Both estimators are available on both sides

*(Revised at item 23. This section originally said A4 on both sides was
impossible. It is not.)*

- **Drain-window**: `recompute_rho.py` retained the pre-A4 values as
  `rhoAchievedDrainWindow` in every seven-cell boundary file, and E2e is natively
  drain-window.
- **Delivery span (A4)**: retained as `rhoAchieved` in the seven boundary files
  and in `results/E2E-a4.json` for the corrected cells.

Neither can be re-derived from raw data, because consumer traces are excluded
from the repository. Both routes are therefore reported, side by side, rather
than one being chosen. One caveat applies to the A4 route only: `E2E-a4.json`
stores a single value per point with no per-repetition list, so the **aggregator
on its corrected side cannot be verified** to be the median used on the
uncorrected side.

### The matched recipe

Last SAFE point only (A6-compliant — no collapsed endpoint enters), drain-window
estimator on both sides, median across repetitions, denominator = configured
C = 2000, c10 arm against c50 arm under matched conditions (C0, λ_L = 1000).

| | rl | rate (rps) | ρ |
|---|---|---|---|
| uncorrected E1 c10/C0 | 825 | 1812.4 | 0.9062 |
| uncorrected E1 c50/C0 | 975 | 1946.4 | 0.9732 |
| corrected E2e c10 | 1185 | 1976.7 | 0.9883 |
| corrected E2e c50 | 1210 | 1983.1 | 0.9915 |

| accounting | before | after | removed |
|---|---|---|---|
| published (7-cell range vs 2-cell gap, mixed estimators) | 0.0706 | 0.0026 | 96.3% |
| **matched, drain-window, in ρ** | **0.0670** | **0.0032** | **95.2%** |
| **matched, drain-window, in throughput (rps)** | **134.0** | **6.4** | **95.2%** |
| **matched, A4 on both sides, in ρ** | **0.0696** | **0.0043** | **93.8%** |

### The answer

**The claim survives the audit, and the number changes.** Recomputed under one
recipe applied identically to both corpora, the inter-arm gap falls from 0.0670
to 0.0032 in ρ — equivalently from 134.0 rps to 6.4 rps in throughput space, the
same 95.2% either way, which is the consistency check worth having since only the
throughput form is free of the utilisation denominator.

So the "three false effects dissolved" narrative does not rest on an artefact of
mismatched estimators. **The matched answer is estimator-dependent: 93.8% under
A4, 95.2% under drain-window.** Quote it as **94–95%**, with the before/after
pair given per estimator — 0.0696 → 0.0043, or 0.0670 → 0.0032. That range looks
superficially like the report's original "94–96%", but it is arrived at
differently: the original bracketed two *unmatched* computations, this one
brackets two matched ones. The published pair should not be quoted again: its
first term is a seven-cell range mislabelled as a two-arm gap, and its two terms
are on different estimators.

### One more inconsistency found in passing

`results/A6-REPORT.md:139` gives the collapse factor as `0.0706 / 0.0068 = 10.3x`.
A6 recomputed the **denominator** from SAFE points only, as A6 requires, and left
the **numerator** as the midpoint-based 0.0706, which still carries the collapsed
endpoints A6 ruled invalid. Recomputing the numerator the same way gives a
safe-side seven-cell range of **0.0716**, and a factor of **10.5×** rather than
10.4×. **Immaterial to the claim** — the order-of-magnitude collapse is
untouched — but the numerator should be made consistent with its own amendment.

---

## Summary for Section 5 — round 5

| item | outcome |
|---|---|
| 15. Gate 2's estimator | **the registration named A4** — neither "it named as-measured" nor "it was silent". Gate 2 failed under the estimator used (1.4 and 2.4 steps) and under the registered one, [0.9956, 1.0016] and [0.9999, 1.0064]. ~~The A4 brackets are reproducible nowhere~~ — **withdrawn at item 23**: they are retained in `results/E2E-a4.json`. They are not *re-derivable*, which is true of every A4 value in the corpus |
| 16. saturation pair | **designated in advance**, `67c448b` 2026-09-13 13:31:47 −0400, before any corrected plateau was measured, against a tabulated 90%-load alternative and a pre-committed failure reading. Only two candidates existed; in-situ came later. **Not post-hoc.** Ordering rests on contemporaneous registration text, not on a timestamp inside the datum |
| 17. plateau repeatability | **n = 1 per corrected cell.** No spread exists; none synthesised. Quote raw differences; "−0.00%" must not appear. The seven cells have 6–15 each — the more load-bearing measurement is the less replicated one |
| 18. attribution figures | both from the **direct per-request timing probe at 90% of capacity**. 99.8% holds there in both arms; at saturation the long arm is 99.7%. 1.3 µs = pre+post+timer at **S = 5 ms**, 90% load (1.38 µs at S = 25). **The records' own `note` field mis-states its own `total`**, and F3's 99.8% title is hardcoded |
| 19. matched audit | **not matched on four dimensions**, including the statistic itself — 0.0706 is a seven-cell **range**, mislabelled in E2E-REPORT as a two-arm gap. Recomputed matched: **0.0670 → 0.0032, 95.2%** under drain-window (134.0 → 6.4 rps, same figure) and **0.0696 → 0.0043, 93.8%** under A4. **The claim survives; quote 94–95%**, per estimator. *(A4 route added at item 23.)* |

---
---

# Round 6 — three repo fixes from the Section 5 audit

No analysis; these are corrections to artefacts and generators. Every numeric
result in the repository is unchanged, and that is verified rather than asserted.

## 20. The overhead records' `note` contradicted its own arithmetic

**Established at the source, not inferred.** `downstream/main.go:412` accumulates

```go
ovTotal.add(pre + excess + post)
```

while `timer` is a separate counter added at line 239. `total` has never included
`timer`. Across the 41 probe-enabled overhead blocks in `results/e2e/`:

| formula | agreement with the recorded `total` |
|---|---|
| `preSleep + sleepExcess + postSleep` | within **2 ns** (integer-mean rounding) |
| `timer + preSleep + sleepExcess + postSleep` — *what the note claimed* | off by **277–341 ns** |

**Fixed in both places.**

- `downstream/main.go`: the note string now reads *"total = preSleep +
  sleepExcess + postSleep … timer is measured and reported alongside but is NOT
  a term of total"*, with a source comment recording that it said otherwise until
  2026-09-15. `gofmt` clean, `go build` passes.
- The 43 committed records carrying the old string were rewritten to the new one.

**Nothing but the note changed.** Each record was hashed before and after with the
`note` key stripped recursively from the JSON: **0 of 43** differ. No measurement,
no counter, no percentile moved.

### Byte-identical reproduction elsewhere: confirmed, with one exception found

Every generator was re-run and all 477 artefacts in `results/` and `figures/`
compared by SHA-256 against their pre-edit state.

**Reproduced byte-identically:** `E2E-analysis.json`,
`E2D-capacity-calibration.json`, `A6-collapsed-estimator.json`,
`E2C-slo-sweep.json`, `W7-denominator-uncertainty.json`,
`W7-e2e-per-repetition.json`, `W8-effect-size-accounting.json`,
`A7-leading-indicator-corrected.json`, and the E2, E2B, E2C, E2D reports — every
artefact that consumes these records. The `note` is metadata; no analysis reads
it.

**Changed, and expected to:** the 43 records, `A6-REPORT.md` (item 22),
`E2E-REPORT.md` (item 21).

**The exception: the figures were never byte-reproducible at all.** All six PDFs
changed, and re-running `make_figures.py` twice with no source change between
runs also produced six different files. The cause is a wall-clock
`/CreationDate` embedded by matplotlib's PDF backend — `F5-collapse.pdf` carried
`D:20260914193048-04'00'`. This is unrelated to the note fix and predates it; it
quietly falsified the *"Every committed report regenerates byte-identically from
committed data"* claim in `scripts/make_deposit.py` for `figures/`.

Fixed: `save()` now passes `metadata={'CreationDate': None}`. The figures now
regenerate byte-identically across runs, verified by two consecutive runs. Their
**drawn content is unchanged** — decompressing every PDF content stream and
hashing the marks gives an identical digest to the committed versions for all
six.

## 21. The delivery-span brackets in E2E-REPORT are marked non-reproducible

`scripts/e2e_report.py` emitted a four-row estimator-comparison table in which
all four brackets were hardcoded literals. Two of them — the as-measured rows —
**are** derivable from the committed analysis; two — the A4 rows — are not.

- The as-measured rows are now **computed** from `C[arm]['bracket']['rho']`. They
  regenerate to [0.988, 0.992] and [0.992, 0.994], identical to the literals they
  replace.
- The A4 rows keep their values and carry a footnote marker. The footnote states
  that they are literals produced by no script; that A4 needs per-arrival
  timestamps from the consumer trace, which the one-second `timeline` cannot
  supply; that traces are gitignored corpus-wide so none was ever committed; that
  E2e produced no boundary file in which A4 values would have been retained as
  they were for E1, E2 and E2b; that **no trace survives at the c10 arm's last
  SAFE point, so A4 cannot be computed there at all**; and that the c50 arm's two
  surviving repetitions give [1.0006, 1.0076] against the [1.000, 1.006] quoted.

They are retained, not deleted, because the verdict they support — that the two
estimators disagree by about the size of the effect — is corroborated
independently by the plateau comparison and by item 15. The footnote says they
must not be quoted as measurements.

## 22. A6's collapse factor is now internally consistent

The factor divided E2d's `rhoStarSpread` of **0.0706** — the range of interval
**midpoints**, each averaging the last SAFE endpoint with a collapsed non-SAFE
one — by a denominator A6 had already recomputed from **SAFE points only**. Half
the ratio obeyed the amendment and half did not.

Both terms are now the across-cell range of a quantity read at the last SAFE
point:

| | numerator | denominator | factor |
|---|---|---|---|
| as published | 0.0706 (midpoints) | 0.0068 (SAFE only) | 10.3× |
| **corrected** | **0.0716 (SAFE only)** | 0.0068 (SAFE only) | **10.5×** |

**Immaterial** — the order-of-magnitude collapse is untouched and nothing
downstream moves — but the ratio no longer mixes two conventions.
`results/A6-REPORT.md` carries the correction in place, as a block quote beside
the original figure rather than a silent edit.

**A related gap closed.** The `(a)–(e)` conclusions block quoted in A6-REPORT was
produced by `conclusions()` in `scripts/collapsed_estimator_audit.py`, which was
**unreachable dead code** — the file ended with `if __name__ != '__main__': pass`
— so the block had been pasted by hand and could not be regenerated. It now runs
under `python3 scripts/collapsed_estimator_audit.py --conclusions`, and the block
in the report is verified to match its output verbatim. Default behaviour is
unchanged, so the JSON artefact still regenerates byte-identically.

---

## Summary — round 6

| item | outcome |
|---|---|
| 20. `note` field | fixed at the Go source and in 43 records; **0 of 43** differ outside the `note` key; every consuming artefact reproduced byte-identically |
| 20, incidental | **the figures were never byte-reproducible** — a wall-clock `/CreationDate` made every run differ. Fixed; drawn content verified unchanged in all six |
| 21. A4 brackets | as-measured rows now computed and identical to the literals they replace; A4 rows ~~marked non-reproducible~~ — **superseded at item 23**, they are now computed from `results/E2E-a4.json` |
| 22. A6 collapse factor | numerator recomputed SAFE-side, 0.0706 → 0.0716, factor 10.3× → **10.5×**; corrected in place. `conclusions()` was dead code and is now reachable and verified against the report |

---
---

# Round 7 — the gap table, and a correction to rounds 5 and 6

## 23. `results/E2E-a4.json` exists. Three earlier findings were wrong.

While enumerating the generated data artefacts to verify reproduction, I found
**`results/E2E-a4.json`** — committed 2026-09-13 17:56:37 −0400 in `fa8ca3b`,
the E2e completion commit. It holds the per-point delivery-span utilisation for
both corrected cells:

| arm | rl | class | A4 ρ |
|---|---|---|---|
| c10 | 1185 | SAFE | 0.9956 |
| c10 | 1240 | UNSAFE | 1.0016 |
| c50 | 1210 | SAFE | 0.9999 |
| c50 | 1275 | UNSAFE | 1.0064 |

Taking each arm's last SAFE and first UNSAFE point reproduces the quoted
brackets **exactly**: c10 [0.9956, 1.0016], c50 [0.9999, 1.0064].

**So the central claim of item 15 was wrong.** I wrote that the A4 E2e brackets
"exist in no artefact", "appear only as prose", and that "no script computes
them; nothing regenerates them." The values were in a committed artefact the
whole time. I searched for the *numbers* in `.py` and `.md` files and for scripts
that *write* an A4 output; I did not enumerate the repository's own JSON
artefacts until this turn, and the file is named for the campaign rather than for
the estimator's role.

### What survives, stated narrowly

- **The values are retained; they are not re-derivable.** A4 needs per-arrival
  timestamps from the consumer trace, traces are gitignored corpus-wide, and none
  survives at c10 rl=1185.
- **That is true of every A4 value in the corpus, not just E2e's.** E1, E2 and
  E2b preserve theirs inside their boundary files; E2e, having no boundary file,
  preserves its own in this file. Retained-not-re-derivable is the corpus-wide
  status, and singling E2e out was wrong.
- **The file is an orphan.** Nothing in the repository writes it, and until this
  round nothing read it. `e2e_report.py` hardcoded numbers that were sitting in
  an artefact beside it.
- **One caveat is real and new.** `E2E-a4.json` stores a single value per point
  with no per-repetition list, so on that side the **aggregator is not recorded**
  and cannot be verified to be the median.

### Items 15, 19 and 21 are corrected in place

Item 15's first bullet is struck and replaced; its second is narrowed from
"cannot be computed" to "cannot be re-derived", with the corpus-wide scope
stated; its concluding sentence and summary row are rewritten. Item 19's "A4 on
both sides is not possible" section is replaced. Item 21's summary row is marked
superseded. None of the struck text is deleted.

### The A4 route, now run

Item 19 could not previously answer the blocking question under the registered
estimator. It can now, and `scripts/effect_size_accounting.py` runs both routes:

| accounting | before | after | removed |
|---|---|---|---|
| published (7-cell range vs 2-cell gap, mixed estimators) | 0.0706 | 0.0026 | 96.3% |
| matched, drain-window, in ρ | 0.0670 | 0.0032 | **95.2%** |
| matched, drain-window, in throughput | 134.0 rps | 6.4 rps | **95.2%** |
| matched, **A4 on both sides**, in ρ | 0.0696 | 0.0043 | **93.8%** |

**The matched answer is estimator-dependent: 94–95%.** The claim survives under
either. That range resembles the report's original "94–96%" but is reached
differently — the original bracketed two unmatched computations, this brackets
two matched ones.

## 24. The gap table in E2E-REPORT, corrected in place

`scripts/e2e_report.py` now emits, in place of the old two-line pair:

1. **A correction notice** stating that the table read *"uncorrected, E1
   midpoints 0.9137 and 0.9826 | 0.0706"*, that **those midpoints differ by
   0.0689, not 0.0706**, that 0.0706 is E2d's `rhoStarSpread` — the range across
   all seven cells (`capacity_calibration.py:221`) — mislabelled here as a
   two-arm difference, and that it was being differenced against a residual on a
   different estimator, aggregator and observation interval. The 0.0689 is
   computed from the constants already in the analysis, not typed in.
2. **The withdrawn pair**, struck through and marked "retained so the correction
   is legible, not for quotation".
3. **The matched accounting**, read from `results/W8-effect-size-accounting.json`
   so the report states no number of its own: both estimator routes, the
   throughput row, and the 94–95% range.
4. A note that the registered prediction was 0.0052 and 92.7% removed, so the
   correction removed somewhat *more* of the gap than registered under either
   estimator.

**One precision decision, made explicitly.** The ρ rows are given to four
decimals. `scripts/precision.py` scopes the resolution-matched rule to "a
MEASURED utilisation" at its own cell's resolution; an inter-arm gap is a
difference between two cells and is not that quantity, on the same reasoning that
exempts vSLO in the module's own docstring. At three decimals 0.0032 renders as
0.003 and stops being distinguishable from the withdrawn 0.0026, which is the
comparison the table exists to make. The report states this in line.

### Reproduction

Every generator re-run and all 477 artefacts compared by SHA-256.

| set | result |
|---|---|
| the twelve generated data artefacts | **all identical** — E2E-analysis, E2D-capacity-calibration, E2C-slo-sweep, A6-collapsed-estimator, A7-leading-indicator-corrected, W2-leave-one-out, W2-reviewer-analysis, W7-denominator-uncertainty, W7-e2e-per-repetition, E1-leading-indicator, E1-noise-scale-sensitivity, E2E-a4 |
| W8-effect-size-accounting.json | **changed by design** — the A4 route was added to it this round |
| the six figures | **all identical**, byte for byte |
| E2, E2B, E2C, E2D reports | **all identical** |
| E2E-REPORT.md | **changed — the intended edit** |

---

## Summary — round 7

| item | outcome |
|---|---|
| 23. `E2E-a4.json` | **my error, corrected** — the A4 E2e brackets are in a committed artefact and reproduce the quoted values exactly. Items 15, 19 and 21 corrected in place, nothing deleted. What survives: retained but not re-derivable, which is the corpus-wide status of every A4 value, and the file is an orphan nothing wrote or read |
| 23, consequence | the blocking matched audit now runs under **both** estimators: 95.2% (drain-window) and 93.8% (A4). **Quote 94–95%** |
| 24. gap table | corrected in place with an annotated notice, the withdrawn pair struck through and retained, and the matched accounting read from W8 rather than restated |
| 24, reproduction | twelve data artefacts and six figures all reproduce byte-identically; W8 changed by design; E2E-REPORT changed as intended |

---
---

# Round 8 — measurement characterisation of the direct timing probe

Generated by `scripts/probe_characterisation.py` →
`results/W9-probe-characterisation.json`. Read-only; no new runs. Item 28 is a
caption edit.

## 25. The direct timing probe

### Cycles, window, and the reported statistic

| arm | condition | cycles | window | reported δ | statistic |
|---|---|---|---|---|---|
| c10 (S=5) | 90% load | 115,156 | 60.00 s | 0.5165 ms | arithmetic **mean** over every cycle |
| c10 | saturation | 127,380 | 60.00 s | 0.4947 ms | arithmetic **mean** |
| c50 (S=25) | 90% load | 123,673 | 60.00 s | 0.5114 ms | arithmetic **mean** |
| c50 | saturation | 137,257 | 60.00 s | 0.4914 ms | arithmetic **mean** |
| c10 | in situ | 4,154,563 over 18 runs | 111–120 s each | 0.4775 ms | **median of medians of means** |
| c50 | in situ | 3,451,664 over 15 runs | 114–119 s each | 0.4746 ms | **median of medians of means** |

Nothing is trimmed anywhere. The first four are `ovTotal.report()`, a running
sum divided by a running count. The in-situ figure is three-deep: each run's
`overheadDrain.total.meanNs` is a **mean**; `e2e_analysis.py` takes the **median**
of the three repetitions at a point, then the **median** across the points of the
arm. A paper sentence that calls all six "the measured overhead" is eliding two
different estimators.

### Dispersion — and what is not recoverable

The records carry **p50, p90, p99 and p99.9** for `total`, `sleepExcess` and
`cycle`. They carry **no p25 and no p75**, so the **interquartile range cannot be
recovered from committed data**. I am not estimating it. What exists:

| arm | condition | mean | p50 | p90 | p99 | p99.9 | max |
|---|---|---|---|---|---|---|---|
| c10 | 90% load | 0.5165 | 0.5140 | 0.9595 | 1.0673 | 1.1102 | 1.2187 |
| c10 | saturation | 0.4947 | 0.4868 | 0.9609 | 1.0712 | 1.1305 | 1.6409 |
| c50 | 90% load | 0.5114 | 0.5054 | 0.9603 | 1.0684 | 1.1178 | 1.4216 |
| c50 | saturation | 0.4914 | 0.4830 | 0.9610 | 1.0732 | 1.1342 | 1.9179 |

(ms. In situ, medianing across runs, p50 is 0.4647 and p99 1.0582 for c10;
0.4599 and 1.0595 for c50.)

**A caveat on the percentiles.** `ovSample()` writes into a fixed buffer of
`OVERHEAD_SAMPLES` slots — default **200,000** — at `ovSampIdx++`, and silently
drops everything past the end (`downstream/main.go:305-309`). It is **first-N
truncation, not a reservoir**. The 60-second windows are under the cap, so their
percentiles cover every cycle. The **in-situ blocks are not**: 227,332 cycles
against 200,000 slots in the run inspected, so those percentiles describe the
**first 200,000 cycles of the drain**, not the whole of it. Means, counts and
maxima are over every cycle in all cases.

### The clock

Every component is a difference of two `time.Now()` readings taken around the
sleep (`downstream/main.go:405-412`). Go stores a monotonic reading inside
`time.Time` and `Sub()` uses it, so these are `CLOCK_MONOTONIC` intervals,
**nominal resolution 1 ns**.

**The effective resolution is not recoverable from the committed records.** No
calibration run exists — nothing measures the cost or granularity of a clock read
on the EC2 host. It can only be bounded indirectly: the separately-counted
`timer` component, which spans the timer work of one cycle, has a mean of
285–337 ns across the six conditions, and `preSleep` means are 414–460 ns. Both
are three orders of magnitude below the ~490 µs quantity being reported, so clock
granularity is not a material contributor to δ — but that is an argument, not a
measurement, and the paper should say which it is.

### Skew — yes, and it matters

| arm | condition | mean / p50 | p99 / p50 | max / p50 |
|---|---|---|---|---|
| c10 | 90% load | 1.005 | 2.08 | 2.37 |
| c10 | saturation | 1.016 | 2.20 | 3.37 |
| c50 | 90% load | 1.012 | 2.11 | 2.81 |
| c50 | saturation | 1.017 | 2.22 | 3.97 |

**The distribution is right-skewed in every condition.** The mean exceeds the
median everywhere, the 99th percentile is about **twice** the median, and maxima
reach three to four times it. This is what timer overshoot looks like.

**So every reported δ at 90% load and at saturation is a mean over a
right-skewed distribution, and sits above the typical cycle** — by 0.5% to 1.7%
depending on the condition. The paper must say so. Two further consequences
worth stating rather than leaving implicit:

- The **in-situ** figure is not comparable on this axis: its outer two operations
  are medians, so it is less tail-sensitive than the other four by construction.
  Part of why it is "the most stable of the three" is the estimator, not only the
  measurement condition.
- The **capacity model uses the mean, and should**. `C·S/(S+δ)` is a statement
  about throughput, which is set by total time per request, so the mean is the
  correct statistic even though it is not the typical cycle. The skew is a
  reporting obligation, not an error.

## 26. The probe-on/off intrusion test

| S | probe | served rps | window | records |
|---|---|---|---|---|
| 5 | on | 1819.9 | 60.00116 s | **1** |
| 5 | off | 1820.6 | 60.00096 s | **1** |
| 25 | on | 1961.3 | 60.00094 s | **1** |
| 25 | off | 1963.1 | 60.00053 s | **1** |

Shifts: **−0.0360%** at S = 5 and **−0.0898%** at S = 25, matching the 0.04% and
0.09% quoted.

**The control is single-shot: n = 1 against n = 1, four measurements in total.**
One on-window and one off-window per arm; no repetition exists anywhere in the
corpus. Consequently:

- No dispersion can be attached to either shift.
- Neither can be compared against the window-to-window variability of the plateau
  itself, which is **also unmeasured for these cells** (item 17: n = 1 per
  corrected plateau).
- A registered criterion of "less than 0.5%" was met by a comparison that cannot
  distinguish a real 0.04% intrusion from ordinary run-to-run scatter, because
  the scale of that scatter was never established.

**Section 5 currently presents this as a control, and a control measured once is
weaker than it reads.** The honest phrasing is that the criterion was registered
in advance and met on a single paired observation per arm, with no repetition and
therefore no error bar.

## 27. The seven plateau-inferred δ estimates

`δ = S · (C_configured / C_measured − 1)`, per cell, from that cell's own
measured plateau (`capacity_calibration.py:165`).

| cell | S (ms) | C_configured | C_measured | implied δ (ms) |
|---|---|---|---|---|
| E2 c10@Q2500 | 5 | 2000 | 1827.1 | **0.473** |
| E1 c10/C0 | 5 | 2000 | 1828.6 | **0.469** |
| E1 c10/C1 | 5 | 1400 | 1280.9 | **0.465** |
| E2b C=400 | 25 | 400 | 392.7 | **0.463** |
| E1 c50/C0 | 25 | 2000 | 1964.3 | **0.454** |
| E2 c50@Q500 | 25 | 2000 | 1964.8 | **0.447** |
| E1 c50/C1 | 25 | 1400 | 1375.7 | **0.441** |

| | |
|---|---|
| n | 7 |
| min / max | 0.441 (E1 c50/C1) / 0.473 (E2 c10@Q2500) |
| **range** | **0.032 ms — 6.9% of the median** |
| **median** | **0.463** — the value the correction used |
| mean | 0.459 |
| lower / upper hinge | 0.451 / 0.467 |
| **IQR (Tukey hinges)** | **0.016 ms** |
| SD | 0.0110 (CV 2.39%) |

At n = 7 the hinges are a coarse summary and the range is the more honest
dispersion statistic.

### The structure the median hides

**The two arms do not overlap.** Every S = 5 cell is at or above 0.465; every
S = 25 cell is at or below 0.463.

| arm | n | values | median |
|---|---|---|---|
| S = 5 ms | 3 | 0.465, 0.469, 0.473 | **0.469** |
| S = 25 ms | 4 | 0.441, 0.447, 0.454, 0.463 | **0.451** |

Within-arm spreads are 0.008 and 0.022 ms; the gap between the arm medians is
0.018 ms. **The seven are not seven draws from one constant** — they separate
perfectly by service time. This is the same per-arm structure §V-D already
reports as a 4% gap, and it is the reason the median of all seven is not a
neutral summary: it sits between two non-overlapping groups and equals no cell's
own value except E2b's.

**What the leave-one-out test does and does not show.** It shows the *model* is
stable against this spread — every held-out plateau is reproduced within one
bisection step. It does not show the *inputs* are tight, and they are not: they
vary by 7% of their own median and do so systematically with S, not randomly.

## 28. F4's caption

`figures/CAPTIONS.md` now states, in the Fig. 4 caption:

- **which corpus each pair of bars comes from** — the uncorrected pair is E1
  c10/C0 and E1 c50/C0 from the seven-cell campaign, whose plateaus are each the
  median of **six** per-run measurements repeatable to 0.11% and 0.13%; the
  corrected pair is E2e;
- that **each corrected plateau is a single 60-second closed-loop observation,
  n = 1 per arm**;
- that **no repeatability estimate exists** for them, the bars carry no error
  bars, and **their absence does not imply zero uncertainty**.

The caption's "errors of −0.00% and +0.02%" is replaced by "differences of 0.0
and +0.4 requests per second", consistent with item 17.

### The figure's bar annotations — now switched to rps

**DONE, item 29.** The figure previously printed percentages above each bar
(`make_figures.py:227`, `'%+.2f%%' % err`), rendering:

| bar | label drawn | raw difference |
|---|---|---|
| c10 uncorrected | −0.16% | −2.9 rps |
| c50 uncorrected | +0.02% | +0.4 rps |
| **c10 corrected** | **+0.00%** | +0.0 rps |
| c50 corrected | +0.02% | +0.4 rps |

A figure captioned "these are raw differences, not evidence of agreement at that
scale" was drawing **+0.00%** on the bar the caption is about. The annotations
now read **−2.9 rps, +0.4 rps, +0.0 rps, +0.4 rps**. See item 29 for the
verification that nothing else in the figure moved.

---

## Summary — round 8

| item | outcome |
|---|---|
| 25. probe | 115k–137k cycles per 60 s window; the four direct figures are **arithmetic means**, the in-situ figure a **median of medians of means**. **No IQR is recoverable** — the records carry p50/p90/p99/p99.9 only. Clock is `CLOCK_MONOTONIC` via `time.Now()`, nominal 1 ns; **effective resolution not recoverable**, no calibration run exists. **Right-skewed in every condition** (p99 ≈ 2× p50, max up to 4×), so every reported δ is a mean above the typical cycle — the paper must say so |
| 25, caveat | percentile sampling is **first-N truncation, not a reservoir**; the in-situ blocks exceed the 200,000-slot buffer, so their percentiles describe the first part of each drain |
| 26. intrusion test | **single-shot** — n = 1 against n = 1, four measurements. No dispersion attachable, and the plateau's own scatter is unmeasured too. Weaker than "control" reads |
| 27. inferred δ | range **0.032 ms, 6.9% of the median**; IQR 0.016; SD 0.0110. **The two arms do not overlap** (S=5 ≥ 0.465, S=25 ≤ 0.463) — not one population, and the median of seven equals no cell's value but E2b's |
| 28. F4 caption | corpus provenance, **n = 1 per corrected arm**, and "no error bars ≠ no uncertainty" added; "−0.00%" removed. The figure's bar annotations are now rps as well — item 29 |

---

## 29. F4's bar annotations, and what changing them moved

`make_figures.py` now draws the raw difference in requests per second above each
bar instead of a percentage:

| bar | was | now | predicted → measured |
|---|---|---|---|
| c10 uncorrected | −0.16% | **−2.9 rps** | 1831.5 → 1828.6 |
| c50 uncorrected | +0.02% | **+0.4 rps** | 1963.9 → 1964.3 |
| **c10 corrected** | **+0.00%** | **+0.0 rps** | 1987.4 → 1987.4 |
| c50 corrected | +0.02% | **+0.4 rps** | 1997.7 → 1998.1 |

The figure and its caption now make the same claim. "+0.0 rps" says a difference
was measured and it was zero to the tenth of a request per second; "+0.00%" read
as agreement to two decimal places on a quantity observed once.

### Verification

**The other five figures are byte-identical**, unchanged SHA-256 across the
regeneration: F1 `733f9623…`, F2 `2c94c9c5…`, F3 `bb0554cb…`, F5 `1895cf4e…`,
F6 `33ae10b8…`.

**F4 differs only in those annotations.** Decompressing every content stream in
both versions and separating text blocks from drawing operators:

- **Zero path or painting operators differ.** Not one `re`, `m`, `l`, `c`, `f`,
  `S`, `W`, colour or line-width operator changed. No bar, axis, tick, legend,
  reference line or shaded span moved.
- **4 of 25 text blocks differ** — the four annotations.
- The only changed graphics lines are **8 `cm` text-placement matrices**, in four
  pairs at identical y-coordinates, each shifted **−0.7812 pt** in x. That is the
  recentring of the four labels, by the same amount for each because all four
  strings changed width identically. Plus the `q`/`Q` pairs wrapping them.
- The remaining differences are **embedded font-subset tables** (`OS/2`, `cmap`,
  `glyf`, `hmtx`, `kern`, `loca`) and **ToUnicode CMap** entries. The glyph set
  changed because `%` is no longer drawn and `r`, `p`, `s` and a space now are.
  Inherent to changing the text, not a separate edit.

Rendered and inspected: no clipping, no overlap between labels.

**One pre-existing cosmetic issue, unchanged and not fixed.** The c50-uncorrected
label sits on the dashed "configured C" line at 2000, because its y is
`max(bar) + 26` and that bar tops out near 1964. The old `+0.02%` label sat in
exactly the same place; the new string is 0.78 pt wider, so the collision is
neither introduced nor materially worsened here. Left alone as out of scope.

| item | outcome |
|---|---|
| 29. F4 annotations | switched to rps; **five other figures byte-identical**; F4 differs in **zero** path/paint operators, four text blocks, four label-placement shifts of −0.7812 pt, and the font subset those labels require |
