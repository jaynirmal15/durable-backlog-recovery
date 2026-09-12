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
