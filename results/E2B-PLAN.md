# E2b — pre-run plan: is it the concurrency or the service time?

**Committed before the instance is started and before any run.** Every reading
below is arithmetic on numbers that do not yet exist.

## What E2 left open

E2 showed the queue cap does not set ρ*: each arm reproduced its own boundary
under a fivefold cap swap, in both directions. What separates the arms is
therefore some property that moves with the arm, and the two arms differ in
**two** things at once, which E1 and E2 never separated:

| | S | concurrency at C=2000 | cap-in-ms |
|---|---:|---:|---:|
| c10 | 5 ms | 10 | 250 |
| c50 | 25 ms | 50 | 1250 |

`concurrency = ceil(C x S)` and `cap-in-ms = 50 x S`, so at fixed C both follow
S and neither can be varied alone by changing the arm. E2 varied the cap in
absolute terms but **not** cap-in-ms relative to the arm's own concurrency.

## The condition

Lowering C breaks the tie, because concurrency depends on C and S while
cap-in-ms depends on S alone.

| | value |
|---|---|
| C (nominal, and at fault — this is C0) | **400** |
| S | **25 ms** |
| λ_L | **200** (λ_L/C = 0.5, as in every E1 and E2 cell) |
| concurrency = `ceil(400 x 0.025)` | **10** |
| queue cap = `50 x concurrency` | **500** |
| cap-in-ms = `Q / C` = 500/400 | **1250 ms** |
| profile | `graceful`, `profile_relative` (no `QUEUE_CAP` override) |

**Concurrency 10 matches c10. Service time and cap-in-ms match c50.** No cell of
the E1/E2 2x2 occupies this combination, and it is the only one that separates
concurrency from S.

The cap is **not** forced. Under `profile_relative` the downstream derives
`Q = 50 x ceil(C x S) = 500` on its own; the plan asserts it rather than sets it,
so a wrong C would show up as a wrong cap instead of being masked by an override.

## The three readings, fixed now

Scored against E1's two C0 midpoints, which are the two hypotheses:

```
rho10 = 0.9137   (E1 c10 @ C=2000, midpoint of [0.9124, 0.9150])
rho50 = 0.9826   (E1 c50 @ C=2000, midpoint of [0.9817, 0.9835])
D     = 0.0689

h = (rho*_E2b - rho10) / D
```

| h | reading |
|---|---|
| **h <= 0.25** | **CONCURRENCY GOVERNS.** ρ* is c10-like. S and cap-in-ms do not set it. |
| **h >= 0.75** | **S GOVERNS.** ρ* is c50-like. Concurrency does not set it. |
| otherwise | **INTERMEDIATE.** The fraction is reported and neither is claimed. |

In rate terms at C=400, λ_L=200: the c10-like prediction is **rl ≈ 165**
(ρ = 365/400 = 0.9125) and the c50-like prediction is **rl ≈ 193**
(ρ = 393/400 = 0.9825).

### The dead band, registered in advance this time

E2's attribution statistic had no dead band, so a fraction of −0.006 produced the
same verdict as one of −0.057. That defect was found mid-campaign and had to be
reported rather than fixed, because changing a criterion once you can see it is
about to fire is the thing pre-registration prevents. It is fixed here **before
any data exists**:

- `-0.25 <= h <= 0.25` reads as **CONCURRENCY GOVERNS**. Landing slightly below
  the c10 anchor is the c10-like outcome, not a separate phenomenon.
- `0.75 <= h <= 1.25` reads as **S GOVERNS**, symmetrically.
- `h < -0.25` or `h > 1.25` is **OFF-SCALE**: the cell fell outside the span the
  two hypotheses bracket, which neither predicts, and neither is claimed.

The bands are symmetric and are set now, sight unseen.

### Precision, stated because it is materially worse here

Bisection stops at 5 rps, as in E1 and E2. At C=400 that is a **ρ resolution of
5/400 = 0.0125**, five times coarser than the 0.0025 those campaigns had at
C=2000. In units of the thing being measured:

```
h quantum = 0.0125 / 0.0689 = 0.18
```

So `h` resolves only to about ±0.18, and the INTERMEDIATE band from 0.25 to 0.75
is under three quanta wide. **The registered question is still answerable**: the
two hypotheses sit 0.069 apart in ρ, which is 5.5 quanta, so a c10-like and a
c50-like outcome cannot be confused. But a fine reading *within* the intermediate
band would be over-interpretation, and the report will not offer one.

Bisecting to 1 rps would give a quantum of 0.036 at the cost of roughly two more
probes. It is not done, because 5 rps is the registered protocol of E1 and E2 and
changing the resolution for one cell would make its interval width incomparable
with the four that precede it.

## Protocol

Unchanged from E1 and E2: bisection to 5 rps, n=3 per probed point, SAFE /
UNSAFE / MARGINAL by the pre-registered thresholds, ρ under A4 from the delivery
span, the A3 spread diagnostic, and A2 downward extension if the anchor is not
SAFE. Cap and service time asserted against `/admin/capacity` before the search
and per run by the runner's own arm guard.

**Anchor: rl = 180**, ρ = 380/400 = 0.950. Chosen as the point on the 5 rps grid
nearest the midpoint of the two predictions (179), so the search is not started
adjacent to either hypothesis. If SAFE it steps up 10% to 200 and bisects down;
if not SAFE it extends down to 160 under A2. Both directions reach the 5 rps
floor in about four probes.

**Then n = 12 at the last SAFE point**, for occupancy and DEEP classification,
with the threshold fixed in E1B and unchanged: **DEEP if `drainQueueDepthMean`
>= 50**.

### Cap binding, reported per the brief

E2's null has a candidate mechanism: at every last SAFE point of all six cells
measured so far the median queue peak sat below the cap, from 1.5% to 50.6% of
it, so the cap was not a binding constraint where the boundary is set. E2b runs
at a fifth of the absolute rate, and the report will state **whether the queue
peak reaches the cap at any SAFE point of this cell**, median and max, against
the cap in force. No prediction is registered for it.

## Harness

The Go harness stays pinned at **`026be6242d26`**, the commit used by E1, E1B and
E2. No Go code is changed and no rebuild is performed.

`scripts/locate_boundary.py`, the search driver, **is** changed, because the
pinned version cannot express this condition at all: it takes C from a hardcoded
per-regime constant and derives run ids from arm and regime alone. Two additive
flags:

- `--capacity`, overriding the regime nominal. Refused for C1/C2/C3, whose fault
  capacity is an absolute rate that does not follow a changed nominal, so
  scaling it would silently redefine the manipulation.
- `--run-prefix`, so E2b ids are `e2b-c50-c0-rl180-rN` and cannot collide with
  the c50 records of E1 and E2, which share the arm and regime.

Both default to existing behaviour. `classify`, `bisect_step`, `downward_step`,
`upward_step`, `achieved_rho` and `spread_diagnostic` are untouched. The test
suite goes from 39 tests to 46, the 39 unchanged and passing, and the 7 new ones
assert that the override reaches the runner, that it changes nothing else in the
argument vector, and that classification and bisection are unaffected.

### The arm label means service time here, not concurrency

Runs are launched with `-arm c50`, and the records will read
`concurrencyArm: "c50"`. In this cell **concurrency is 10, not 50.** The labels
were named for the concurrency each arm has at C=2000; the runner's guard derives
the expectation as `ceil(C x S)`, which at C=400 correctly demands 10. So the
guard is doing the right thing under a name that no longer describes it.

Nothing downstream should read `concurrencyArm` as a concurrency. The analysis
reads `downstreamConcurrency`, which records the actual value.
