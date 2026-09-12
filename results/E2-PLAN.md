# E2 — pre-run plan: separating the queue-cap effect from the concurrency effect

**Committed before the instance is started.** The readings below are stated as
arithmetic on numbers that do not yet exist, so the outcome cannot pick the rule.

## Design

Full-queue delay is `Q / C_d`, independent of S and of concurrency. E1 measured
only the diagonal of an arm × cap 2×2, where the two vary together:

| | Q=500 (250 ms) | Q=2500 (1250 ms) |
|---|---|---|
| **c10** (S=5, conc 10) | E1: ρ* [0.9124, 0.9150] | **E2 — to measure** |
| **c50** (S=25, conc 50) | **E2 — to measure** | E1: ρ* [0.9817, 0.9835] |

E2 fills the other diagonal by swapping the caps, at C0, with the pre-registered
estimator unchanged: bisection to 5 rps, n=3, A4 ρ, spread diagnostic, A2
downward extension if an anchor fails. Each search starts from its own arm's E1
boundary and goes where it goes.

## The attribution statistic, fixed now

Using interval midpoints, with E1's two diagonal cells as the endpoints of the
scale:

```
c10 midpoint (Q=500)  m10 = 0.9137
c50 midpoint (Q=2500) m50 = 0.9826
separation            D   = m50 - m10 = 0.0689

f_c10 = (m(c10@2500) - m10) / D      fraction of the gap crossed by giving c10 the big cap
f_c50 = (m50 - m(c50@500))  / D      fraction crossed by giving c50 the small cap
```

`f ≈ 1` means the cell moved all the way to the other arm's E1 value, i.e. the
cap explains the difference. `f ≈ 0` means it did not move, i.e. concurrency
explains it.

| verdict | criterion |
|---|---|
| **CAP-DRIVEN** | both `f ≥ 0.75` |
| **CONCURRENCY-DRIVEN** | both `f ≤ 0.25` |
| **MIXED** | anything else — both fractions reported, no single cause claimed |

Reported alongside, because a fraction computed from midpoints hides width:
whether each new interval **overlaps** its own arm's E1 interval, and whether it
overlaps the other arm's. Overlapping intervals do not support a difference
claim (§4 of the pre-registration), and that rule applies here too.

If the two fractions disagree with each other — one near 1 and the other near 0 —
that is itself the result and is reported as an asymmetry, not averaged.

## Bimodality, folded in

At the **last SAFE point of each new boundary**, n = 12, the same protocol and
the same pre-committed threshold as E1B:

> **DEEP-QUEUE if `drainQueueDepthMean` ≥ 50 requests**, which is 25 ms of
> implied queueing delay at C_d = 2000 in either arm, and 10% of the SLO.

The threshold transfers unchanged and stays well inside both caps: the ceiling is
250 ms of delay at Q=500 and 1250 ms at Q=2500.

E1B found the c10 cell unimodal (0/12 DEEP) and the c50 cell bimodal (9/12). The
question here:

- **c10 given c50's cap** — does it *become* bimodal?
- **c50 given c10's cap** — does it *stop* being bimodal?

If bimodality follows the cap, it is queue geometry. If it follows the arm, it is
concurrency. Either outcome is reported; neither is favoured.

## Harness

Commit **`026be6242d26`**, the same pinned commit as E1 and E1B. It already
contains `QUEUE_CAP` and records `downstreamQueueCap`, `downstreamQueueCapMode`
and `downstreamFullQueueDelayMs` per run, so **no harness change is required**
and no E1 point needs re-running to show the boundary is unmoved.

Cap is set per boundary via the `QUEUE_CAP` environment variable and asserted
against `/admin/capacity` before the search starts, alongside the existing
service-time assertion.

## Addendum, registered 2026-09-12 before the replication phase

Added while the c10@Q=2500 boundary search was still running and **before any
n=12 replication run**. It concerns occupancy, which the plan above did not
cover.

### The observation

Median queue depth at the last SAFE point is very nearly the same **fraction of
the cap** in the two E1 C0 cells:

| cell | cap | median qMean at last SAFE | % of cap |
|---|---:|---:|---:|
| c10 / C0 (n=15) | 500 | 20.57 | **4.11%** |
| c50 / C0 (n=15) | 2500 | 101.79 | **4.07%** |

The 5× difference in absolute occupancy is exactly the 5× difference in cap.

### Registered prediction

If the cap is the governing variable, occupancy swaps with it:

| cell | if CAP governs | if CONCURRENCY governs |
|---|---:|---:|
| c10 @ Q=2500 | median qMean ≈ **103** (4.1% of 2500) | ≈ **21**, unchanged from E1 |
| c50 @ Q=500 | median qMean ≈ **21** (4.1% of 500) | ≈ **102**, unchanged from E1 |

Scored with the same shape of statistic as the ρ* attribution, fixed now:

```
g = (observed median - retain value) / (swap value - retain value)

  c10@2500:  retain 20.57   swap 103
  c50@500:   retain 101.79  swap 21
```

`g ≈ 1` means occupancy followed the cap; `g ≈ 0` means it stayed with the arm.
**Cap-governed if both g ≥ 0.75; concurrency-governed if both ≤ 0.25; mixed
otherwise, with both reported.** Medians, not means, because the E1B replication
showed these distributions are right-skewed and at least one is gapped.

### A caveat that weakens the premise, registered rather than left out

**The coincidence holds only at C0.** The same normalisation across all four E1
cells:

| cell | cap | median qMean | % of cap |
|---|---:|---:|---:|
| c10 / C0 | 500 | 20.57 | 4.11% |
| c50 / C0 | 2500 | 101.79 | 4.07% |
| c10 / C1 | 500 | 6.85 | **1.37%** |
| c50 / C1 | 2500 | 4.71 | **0.19%** |

The two C1 cells sit at 1.37% and 0.19% — differing from each other by seven
times, and from the C0 pair by three to twenty times. So "occupancy at the
boundary is a fixed fraction of cap" is a **two-point agreement at C0, not a
regularity across the four E1 cells**, and it is registered here as such. Two
points agreeing to within 1% of each other is also exactly the kind of thing that
happens by chance often enough to deserve suspicion before it deserves a
mechanism.

E2 tests it at C0, where it was observed. Nothing here extends it to C1.

### Reporting

Cap-normalised occupancy (% of cap) is reported for **every probed point** in
both E2 cells alongside the absolute value, and the same column is added
retrospectively to all four E1 cells so the 2×2 is comparable on one scale.

## Second addendum, 2026-09-12 — a within-arm cap argument that does not hold

Registered as directed, but **the premise it rests on is false**, and the entry
records that rather than the expectation as proposed.

### The proposed argument

That E1 already varied cap-in-ms within each arm, because cap-in-ms is `Q/C` and
`C` drops from 2000 to 1400 at C1 while `Q` stays fixed — giving 250 → 357 ms at
c10 and 1250 → 1786 ms at c50, a 43% rise in both, against which the observed
ρ* movement of −0.0012 and −0.0022 is ~zero where a log-linear cap model
calibrated on the cross-arm gap predicts +0.015.

### Why it does not hold: Q is not fixed at C1

`SetCapacity` recomputes the cap whenever capacity changes:

```go
conc := concurrencyFor(rate, s.serviceTime)          // ceil(C * S)
s.queueCap.Store(int64(queueCapFor(s.profile, conc)))  // 50 * conc
```

So `Q = 50 · C · S` and **cap-in-ms `= Q/C = 50 · S`, independent of C**:

| arm | C | conc | Q | cap-in-ms |
|---|---:|---:|---:|---:|
| c10 | 2000 | 10 | 500 | **250** |
| c10 | 1400 | 7 | **350** | **250** |
| c50 | 2000 | 50 | 2500 | **1250** |
| c50 | 1400 | 35 | **1750** | **1250** |

Confirmed in the data, not just the source. Deeply collapsed runs press against
the cap, and their peak queue depth reports it exactly:

| condition | qPeak across reps | cap if fixed | cap if resized |
|---|---|---:|---:|
| c10/C1 rl=280 | 350, 350, 350 | 500 | **350** ✓ |
| c10/C1 rl=290 | 350, 350, 350 | 500 | **350** ✓ |
| c50/C1 rl=380 | 1474, 1750, 1750 | 2500 | **1750** ✓ |
| c10/C0 rl=840 | 500, 500, 500 | — | **500** ✓ |

**E1 did not vary cap-in-ms within either arm.** The C0→C1 comparison holds it
exactly constant, so it constrains the cap model not weakly but **not at all**.

### What the comparison actually varies, and what it implies

C0→C1 at fixed cap-in-ms changes capacity 2000→1400 and **fault-window
concurrency** 10→7 and 50→35. It is a pure concurrency-and-capacity manipulation.

Calibrating a log-linear slope on the cross-arm gap (0.0689 over ln 5 = 0.0428
per ln-unit) and applying it to a 0.7× concurrency change predicts **−0.0153**.
Observed: **−0.0012 and −0.0022** — an overprediction of **12.7× and 6.9×**.

So the within-arm evidence undercuts a smooth **concurrency** model, which is the
opposite of what the proposed entry concluded. Read on its own it is mildly
*pro*-cap: across arms both cap-in-ms and concurrency change 5× and ρ* moves
0.069; within an arm cap-in-ms is unchanged, concurrency changes 0.7×, and ρ*
barely moves. The variable that tracks the outcome is the one that did not vary
within an arm.

### The resulting three-way tension, stated because it is real

| source | cap-in-ms | concurrency | Δρ* |
|---|---|---|---|
| E1 across arms, C0 | ×5 | ×5 | **+0.0689** |
| E1 within arm, C0→C1 | ×1 | ×0.7 | ≈ **−0.002** |
| **E2 c10, Q swap** | **×5** | **×1** | **+0.0001** |

E2's c10 cell — already measured, f = 0.001 — says cap alone does nothing. The
within-arm rows say a 0.7× concurrency change also does nearly nothing. Yet
together they produce 0.069. **No log-linear model in either variable fits all
three rows**, so at least one of these must be nonlinear, threshold-like, or
driven by something that co-varies with S and is neither cap nor concurrency.

### Registered expectation

The c10 cell is **already measured**, so nothing about it can be registered now.
For the one cell still outstanding:

> **c50 @ Q=500 is expected to return g ≤ 0.25 (concurrency-governed)**, by
> symmetry with the c10 cell rather than from the within-arm argument, which is
> void.

If c50 instead returns g ≥ 0.75 while c10 returned 0.001, that is an **asymmetry
between the arms**, not a cap verdict, and §"attribution statistic" above already
requires it to be reported as such rather than averaged.

### The caveat, restated in the form it should take

The proposed caveat was that C0→C1 changes capacity as well as cap-in-ms. The
sharper statement is that it changes **concurrency** — the very variable E2
exists to separate — and does **not** change cap-in-ms at all. E2, which varies Q
at fixed C, S and concurrency, remains the only clean test, and it is now more
clearly the only one rather than merely the best one.

---

## Correction to the caveat table (recorded before the c50 cell completed)

The four-cell caveat table above divides by `downstreamQueueCap`, which is the
cap at t=0. Under C1 the cap does not stay there: `SetCapacity` recomputes
`Q = 50 x ceil(C x S)` when capacity steps to 1400 at t=20, so the cap in force
during the drain window — the window the occupancy is measured over — is 350 for
c10 and 1750 for c50, not 500 and 2500.

Recomputed against the cap actually in force:

| cell | cap at t=0 | cap during drain | median qMean | % as registered | % corrected |
|---|---:|---:|---:|---:|---:|
| c10 / C0 | 500 | 500 | 20.57 | 4.11% | **4.11%** |
| c50 / C0 | 2500 | 2500 | 101.79 | 4.07% | **4.07%** |
| c10 / C1 | 500 | 350 | 6.85 | 1.37% | **1.96%** |
| c50 / C1 | 2500 | 1750 | 4.71 | 0.19% | **0.27%** |

**The caveat's conclusion is unchanged and is not weakened.** The two C0 cells
are untouched, because at C0 the cap never moves. The two C1 cells move closer to
the C0 pair but remain far from it — 1.96% and 0.27% against 4.11% and 4.07% —
and still differ from each other by seven times. "Occupancy at the boundary is a
fixed fraction of cap" remains a two-point agreement at C0 rather than a
regularity across the four cells.

The registered scoring values for `g` are **not** restated: both are C0 cells, so
the correction does not touch them. `retain 20.57 / swap 103` for c10@2500 and
`retain 101.79 / swap 21` for c50@500 stand exactly as registered.

Computed by `scripts/cap_occupancy.py`, which uses the drain-window cap
throughout; full per-point output in `results/E2-cap-occupancy.json`.
