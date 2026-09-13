# E2e — observe the overhead, then eliminate it

**Committed before any code change and before the instance is started.**

E2d inferred a per-request overhead of **0.463 ms** as the residual reconciling
configured capacity with achieved throughput. Nothing measured it. E2e measures
it, then removes it and checks the boundary moves where the model says.

## Experiment 1 — observe it

Instrument the downstream worker to record wall-clock per request around the
simulated service, separately from the configured sleep, under load at roughly
90% of true capacity, at S = 5 ms and S = 25 ms.

### Registered prediction

> **Mean excess ≈ 0.463 ms at BOTH service times.** The hypothesis is a constant
> additive cost, so the excess must not scale with S. If it does, the additive
> model is wrong and E2d's collapse was coincidence.

Stated as the discriminating contrast: a constant cost predicts
`excess(25) - excess(5) = 0`. A proportional cost predicts
`excess(25)/excess(5) = 5`.

### Decomposition

The worker loop is the thing capacity depends on, so the cost is split by where
in that loop it falls:

| component | what it covers |
|---|---|
| `timer` | `idle.Stop()` / `idle.Reset()` per iteration — runtime timer-heap work |
| `preSleep` | queue-depth atomic, admission-slot release, jitter RNG under its mutex |
| `sleepExcess` | `time.Sleep(st)` actual minus requested |
| `postSleep` | served counter, and the send on the done channel |

Their sum is the per-request overhead the capacity model calls `ov`. HTTP
handling is deliberately excluded: it runs on the request goroutine, not the
worker, so it does not consume worker time and cannot reduce capacity.

The timer cost is recorded **only on iterations that received a job**. An idle
worker also pays it, but that is not a per-request cost.

### The instrumentation must not perturb what it measures

Four `time.Now()` calls and four atomic adds per request are not free. Registered
control: **measure the saturation plateau with the probe on and with it off, at
both service times.** If the plateau moves by more than 0.5%, the probe is
distorting the measurement and its numbers are reported with that caveat rather
than as the overhead.

## Experiment 2 — eliminate it

Hold concurrency fixed and reduce the configured sleep by the measured overhead,
so integer rounding of `ceil(C x S)` cannot blur the prediction:

| arm | sleep | concurrency | predicted true capacity |
|---|---:|---:|---:|
| c10 | **4.537 ms** | 10 | 10 / 0.005 = **2000** |
| c50 | **24.537 ms** | 50 | 50 / 0.025 = **2000** |

Both `ceil(2000 x 0.004537) = 10` and `ceil(2000 x 0.024537) = 50` hold, so
concurrency and queue cap are unchanged from E1.

### Registered prediction

> **rho\* = 1.000 in both arms, and the 0.0706 gap between them vanishes.**

At lambda_L = 1000 and C = 2000 that puts the boundary at **rl = 1000**. One
5 rps step is 0.0025 in rho, so "1.000 +/- resolution" means an interval
bracketing 1.000, expected around [995, 1000].

Registered outcomes, from the brief and not reinterpreted afterwards:

| outcome | reading |
|---|---|
| both land at 1.000 +/- resolution | diagnosis confirmed experimentally, not merely arithmetically |
| a residual gap survives | something beyond the additive overhead separates the arms |
| rho* overshoots 1.0 materially | over-corrected; the model is not purely additive |

**Before either boundary is read**, true capacity is verified directly from the
saturation plateau in that corrected cell, using E2d's max-sustained-30s
estimator. A cell whose plateau is not ~2000 fails its own premise, and its
boundary is reported against the measured plateau as well as against C.

### Protocol

Unchanged: bisection to 5 rps, n = 3, A4 rho over the delivery span, A3 spread
diagnostic, lanes injector pacer, C0, lambda_L = 1000.

**Anchor rl = 975 in both arms**, one step below the predicted boundary. A
bisection cannot be biased by its anchor, only made cheaper or dearer; 975 is
used for both arms rather than each arm's own old boundary, which were 825 and
965 and would have started the two searches at very different distances from the
prediction.

## Harness

**This breaks the pin.** E1, E1B, E2, E2b and the E2c/E2d analyses all rest on
`026be6242d26`. E2e cannot: it needs instrumentation that does not exist there
and a sub-millisecond service time the code cannot express. The changes are
additive and default to the pinned behaviour:

- `OVERHEAD_PROBE=1` enables the probe; unset, the added cost is one predictable
  branch per request.
- `SERVICE_TIME_US` sets service time in microseconds, taking precedence over
  `SERVICE_TIME_MS` when non-zero. Unset, nothing changes.
- `/admin/capacity` gains `serviceTimeUs`; `serviceTimeMs` keeps its existing
  meaning and type.
- The runner gains `-expect-service-us`, which replaces the arm guard's
  service-time expectation while still checking concurrency, so the guard keeps
  catching a stale downstream instead of being switched off.

**No earlier cell is re-run or re-analysed on the new commit.** E2e reports its
own commit, and every comparison against E1 is a comparison across commits, which
is stated wherever one is made.

## Cost and time

The brief estimates 2.5 hours and about $1. **My estimate is 4 to 4.5 hours and
about $1.50.** Experiment 2 needs two boundary searches of five or six probes at
n=3, which is 30 to 36 runs at the 6.7 minutes per run measured across E1, E2 and
E2b, so 3.5 to 4 hours on its own. Experiment 1 and the probe-on/probe-off
control add roughly 30 minutes. Proceeding on that basis; the difference is
runtime, not scope.
