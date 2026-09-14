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
| 10. initial bracket | documented above; `--hi` optional, always freshly probed, a SAFE ceiling is promoted to floor; six of seven cells reconstruct with no `--hi`; **E1 c10/C1 is not reconstructible and the invocation is not recorded** |
