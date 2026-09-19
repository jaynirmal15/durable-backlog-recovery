# A6 — A4 over-reads on collapsed runs: reach, corrected reporting, and what moved

**Analysis only, archived data, no instance.** Registered as `PRE-REGISTRATION.md`
amendment A6.

> **Terminology corrected in place, 2026-09-19.** This report used "true capacity" for two different quantities: the model c/(S+δ) = C·S/(S+δ), which the paper names **C_model**, and the measured saturation plateau, **C_measured**. Each occurrence now carries the term its context requires. No number changed. The configured parameter is **C_config** and is never "true capacity". Field names in committed data are unchanged; `results/METHOD-AUDIT.md` item 33 maps them.

## The defect

A4 measures the recovery rate over the span the traffic occupied. On a healthy
drain that span is the whole drain and the correction is exactly right — it was
introduced to strip the drain detector's confirmation tail, which injected
run-to-run noise the limiter never produced.

On a collapsed run the span excludes stalled intervals, so it returns the rate
during the moving parts rather than the rate sustained. The error grows with the
severity of the collapse.

**It was found by cross-check, not by validation.** A4's own validation covered
SAFE points only. Each cell's saturation plateau — its maximum 30-second
sustained served rate, from the downstream's own counter — is measured
independently, and nothing can sustain more than it can serve. An achieved rate
above the plateau is impossible, not merely suspect.

## 1. Reach

```
E1 c10/C0         840     3     1839.2     1828.6     +10.6   +0.0053 IMPOSSIBLE
E1 c10/C1         280     3     1280.0     1280.9      -0.9   -0.0006 within plateau
E1 c10/C1         290     3     1290.0     1280.9      +9.1   +0.0065 IMPOSSIBLE
E1 c50/C0         980     3     1966.8     1964.3      +2.5   +0.0013 IMPOSSIBLE
E1 c50/C0         990     3     1971.8     1964.3      +7.5   +0.0037 IMPOSSIBLE
E1 c50/C1         375     3     1374.9     1375.7      -0.8   -0.0005 within plateau
E1 c50/C1         380     3     1380.0     1375.7      +4.3   +0.0031 IMPOSSIBLE
E2 c10@Q2500      830     3     1829.8     1827.1      +2.7   +0.0014 IMPOSSIBLE
E2 c10@Q2500      835     3     1834.4     1827.1      +7.3   +0.0037 IMPOSSIBLE
E2 c10@Q2500      845     3     1842.2     1827.1     +15.1   +0.0076 IMPOSSIBLE
E2 c10@Q2500      865     3     1841.4     1827.1     +14.3   +0.0071 IMPOSSIBLE
E2 c10@Q2500      905     3     1841.8     1827.1     +14.7   +0.0074 IMPOSSIBLE
E2 c50@Q500       980     3     1967.8     1964.8      +3.0   +0.0015 IMPOSSIBLE
E2 c50@Q500       990     3     1971.6     1964.8      +6.8   +0.0034 IMPOSSIBLE
E2 c50@Q500      1000     3     1973.6     1964.8      +8.8   +0.0044 IMPOSSIBLE
E2 c50@Q500      1025     3     1977.4     1964.8     +12.6   +0.0063 IMPOSSIBLE
E2 c50@Q500      1075     3     1981.0     1964.8     +16.2   +0.0081 IMPOSSIBLE
E2b C=400         195     3      395.0      392.7      +2.3   +0.0058 IMPOSSIBLE
E2b C=400         200     3      400.0      392.7      +7.3   +0.0183 IMPOSSIBLE

UNSAFE points: 20.  A4 rate above the cell plateau: 18 (90%).
```

```
Excess where positive: +0.0006 to +0.0183 rho, median +0.0049.
Reported interval widths: 0.0018 to 0.0125. The inflation is 0.0x to 10.2x a whole interval.

=== 2. CORRECTED REPORTING ===
```

| | |
|---|---|
| UNSAFE points audited | **20** |
| A4 rate above the cell's own plateau | **18 (90%)** |
| excess where positive | **+0.0006 to +0.0183 rho**, median +0.0049 |
| reported interval widths | 0.0018 to 0.0125 |
| worst case | the inflation is **10x a whole interval** |

Five of the seven interval upper endpoints are affected. The two that are not,
c10/C1 at rl=280 and c50/C1 at rl=375, sit 0.0005 to 0.0006 *below* their
plateau — inside its own uncertainty rather than clearly passing.

The excess grows with depth into the unsafe region, as the mechanism predicts:
E2 c50@Q500 runs +0.0015, +0.0034, +0.0044, +0.0063, +0.0081 across rl 980 to 1075.

## 2. Corrected reporting

A4 is **not patched**. At a collapsed point the achieved rate *is* the plateau,
so utilisation there is `plateau / C` by construction and carries no information
about that point. A better estimator would be correct and still uninformative.

- Boundary intervals are reported in **rate**, which is what the bisection
  resolved and which no rho estimator touches.
- Achieved utilisation is reported at **SAFE points only**.
- Each cell's **ceiling** (`plateau / C`) is the upper bound, a property of the
  cell rather than a measurement of a point.

```
cell           rl interval    rho at last SAFE       ceiling    headroom to ceiling
E1 c10/C0      [ 825,  830]   [0.9124, 0.9125]       0.9143     +0.0018
E1 c10/C1      [ 275,  280]   [0.9107, 0.9107]       0.9149     +0.0042
E1 c50/C0      [ 975,  980]   [0.9817, 0.9823]       0.9821     -0.0002
E1 c50/C1      [ 370,  375]   [0.9786, 0.9786]       0.9826     +0.0040
E2 c10@Q2500   [ 825,  830]   [0.9124, 0.9125]       0.9135     +0.0010
E2 c50@Q500    [ 975,  980]   [0.9820, 0.9826]       0.9824     -0.0002
E2b C=400      [ 190,  195]   [0.9750, 0.9750]       0.9818     +0.0068
```

In **E1 c50/C0** and **E2 c50@Q500** the last SAFE point already sits at the
ceiling, so the corrected interval is degenerate. That is a result rather than a
failure: in those two cells rho* is pinned at saturation.

## 3. What moved

Every conclusion resting on an UNSAFE endpoint was recomputed. Four survive, one
changes materially.

| conclusion | as reported | corrected | verdict |
|---|---|---|---|
| capacity invariance, C0 vs C1 | overlaps in both arms | overlaps in both arms | **survives** |
| concurrency gap | 0.0689 | 0.0688–0.0698 | **survives** |
| E2 cap swap | identical, f = 0.001 | identical rate intervals, f = 0.000 | **survives, stronger** |
| E2b, S governs | h = 0.980 | h = 0.895–0.945 | **survives** |
| **E2d collapse to effective ~1.0** | **0.0033 spread, 21.4x** | **0.0068 spread, 10.3x** | **CHANGES** |

```
(a) capacity invariance: does C0 overlap C1 within an arm?
    c10  C0 [0.9125, 0.9143]  C1 [0.9107, 0.9149]  -> OVERLAP, survives
    c50  C0 [0.9821, 0.9823]  C1 [0.9786, 0.9826]  -> OVERLAP, survives

(b) the concurrency gap between the arms
    as reported, interval midpoints  c10 0.9137  c50 0.9826  gap 0.0689
    corrected, last SAFE rho         c10 0.9125  c50 0.9823  gap 0.0698
    corrected, interval midpoints    c10 0.9134  c50 0.9822  gap 0.0688

(c) E2 cap swap: rate intervals, unaffected by the estimator
    c10  E1 [825, 830]  E2 [825, 830]  -> identical
    c50  E1 [975, 980]  E2 [975, 980]  -> identical
    f_c10 on last SAFE rho: (0.9125 - 0.9125) / 0.0693 = +0.000

(d) E2b: does S still govern?
    on last SAFE rho: h = (0.9750 - 0.9125) / (0.9823 - 0.9125) = 0.895 -> S GOVERNS
    on interval midpoints: h = 0.945 -> S GOVERNS

(e) E2d: the collapse to effective utilisation ~1.0
    E1 c10/C0      effective at last SAFE = 1825.0 / 1828.6 = 0.9980
    E1 c10/C1      effective at last SAFE = 1275.0 / 1280.9 = 0.9954
    E1 c50/C0      effective at last SAFE = 1964.2 / 1964.3 = 0.9999
    E1 c50/C1      effective at last SAFE = 1370.0 / 1375.7 = 0.9959
    E2 c10@Q2500   effective at last SAFE = 1825.0 / 1827.1 = 0.9989
    E2 c50@Q500    effective at last SAFE = 1964.6 / 1964.8 = 0.9999
    E2b C=400      effective at last SAFE = 390.0 / 392.7 = 0.9931
    corrected spread 0.0068 (was 0.0033 using UNSAFE endpoints)
    against configured C, SAFE points only: 0.0716
    collapse factor 0.0716 / 0.0068 = 10.5x  (E2d reported 21.4x)
    CORRECTION: the numerator was 0.0706, E2d's midpoint-based spread,
    which carries the collapsed endpoints this amendment rules invalid.
    Recomputed from SAFE points only it is 0.0716, and the factor 10.5x
    rather than 10.3x. Immaterial; made consistent with A6's own rule.
    every cell sits BELOW 1.0, at 0.9931 to 0.9999: the boundary is at or just
    under saturation, but the "interval brackets 1.0" phrasing does not survive,
    since it depended on the inflated UNSAFE endpoint.
```

### The one that changed

**E2d's collapse factor halves, from 21.4x to 10.5x.** The old spread was computed
from interval midpoints whose upper ends were inflated. The substance survives —
recomputing against C_measured still collapses the cells by an order of
magnitude — but the magnitude was overstated twofold.

> **CORRECTED IN PLACE, 2026-09-14.**(date corrected 2026-09-14: first written as 2026-09-15 from a UTC-offset clock; no other content changed — METHOD-AUDIT item 31) This figure was first published as
> **10.3x**, dividing E2d's `rhoStarSpread` of 0.0706 by the corrected 0.0068.
> That numerator is the range of **interval midpoints**, each averaging the last
> SAFE endpoint with a collapsed non-SAFE one — the values this very amendment
> rules invalid — while the denominator had already been recomputed from SAFE
> points only. Half the ratio obeyed A6 and half did not. Recomputed on the same
> footing, both as the across-cell range of a quantity read at the last SAFE
> point, the numerator is **0.0716** and the factor **10.5x**. The change is
> immaterial — the order-of-magnitude claim is untouched and nothing downstream
> moves — but the ratio is now internally consistent. Found in the Section 5
> audit; see `results/METHOD-AUDIT.md` item 19. The `(a)-(e)` block above is now
> regenerated by `python3 scripts/collapsed_estimator_audit.py --conclusions`,
> which was unreachable dead code until this correction and is why the block had
> previously to be pasted by hand.

**Its phrasing does not survive.** "Five of seven intervals bracket 1.0" rested
entirely on the inflated endpoint. Corrected, **every cell sits below 1.0**, at
0.9931 to 0.9999. The defensible statement is that the last SAFE point lies
within 0.7% of saturation in every cell — a claim about how the boundary is
approached, not a bracket around it.

`results/E2D-REPORT.md` carries a correction notice pointing here.

### Why the cap swap gets stronger

E2's result is that swapping the queue cap moves nothing. Its rate intervals are
identical, [825, 830] and [975, 980] in both directions, and rate is what the
bisection resolved. The estimator never entered it. A6 removes a dependency the
conclusion never needed.

## Scope

No run is repeated and no measurement is discarded. The same records support the
corrected reporting; it uses fewer of their derived quantities, not different ones.

Reproduce with `python3 scripts/collapsed_estimator_audit.py`; full per-point
output in `results/A6-collapsed-estimator.json`.
