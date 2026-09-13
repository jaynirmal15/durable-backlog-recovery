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

---

## Addendum 1 — the correction under-corrects, and the model says by how much

**Registered before experiment 2's boundaries are read.** At the time of writing
experiment 1 is complete and no boundary run has started.

The 0.463 ms correction is campaign-inferred. Experiment 1 measured the overhead
directly under saturation at **0.4947 ms (S=5)** and **0.4914 ms (S=25)**, so the
correction leaves about 0.032 ms uncorrected. The model therefore predicts a
specific non-unity outcome, not 1.000:

| arm | sleep | + overhead | cycle | true capacity | **rho\*** | boundary rl |
|---|---:|---:|---:|---:|---:|---:|
| c10 | 4.537 | 0.4947 | 5.0317 ms | 1987.4 | **0.9937** | 987.4 |
| c50 | 24.537 | 0.4914 | 25.0284 ms | 1997.7 | **0.9989** | 997.7 |

Predicted residual gap **0.0052**, against 0.0706 uncorrected: **92.7% removed**.
Arithmetic confirmed independently. The result is read against these values, not
against 1.000.

### The sensitivity this exposes, registered rather than resolved afterwards

Experiment 1 found the overhead is **not the same at every load**: 0.4947 under
saturation but 0.5165 at 90% of capacity for c10, and 0.4914 against 0.5114 for
c50 — about 4% higher when the server is not saturated. Which value governs the
boundary is not something experiment 1 settles, and the two give measurably
different predictions:

| overhead used | c10 rho\* | c50 rho\* | gap | fraction removed |
|---|---:|---:|---:|---:|
| **saturated** (registered above) | 0.9937 | 0.9989 | 0.0052 | 92.7% |
| **90% load** | 0.9894 | 0.9981 | 0.0087 | 87.7% |

They differ by 0.0043 in the c10 arm, which is **1.7 bisection steps** and so
distinguishable by this experiment.

The saturated value is the registered one and the reason is stated now rather
than chosen later: at the last SAFE point the server runs at about 99% of
capacity, where it is essentially never idle, so the saturated figure is the one
that should apply. **If the boundaries land nearer the 90%-load predictions
instead, that is reported as the finding** — it would mean the cost that governs
the boundary is the one paid at sub-saturation load, not the one paid at the
plateau.

To settle it with measurement rather than argument, each corrected cell has its
overhead measured at **both** saturation and ~99% load before its boundary is
read, alongside the plateau check the brief requires.

### Outcomes, from the brief, unchanged

| outcome | reading |
|---|---|
| boundaries within one bisection step of 0.9937 and 0.9989 | confirmed; the model predicts the residual as well as the collapse |
| both at 1.000 exactly | the saturated overhead is not what acts during a drain; report the discrepancy, do not smooth it |
| residual materially larger than 0.0052 | something beyond the additive overhead separates the arms |

One bisection step is 5 rps, or 0.0025 in rho.

**Plateau check first.** Each corrected cell's saturation plateau must match
1987.4 and 1997.7 before its boundary is read. If the plateaus match and the
boundaries do not, that is a real finding and not the correction.

---

## Addendum 2 — the bisection cannot terminate, and why

**Recorded mid-campaign, with the c10 search in progress.** State of knowledge:
the c10 plateau gate passed exactly (measured 1987.4 against 1987.4 predicted),
rl=975 classified SAFE on three reps, rl=1075 classified SAFE on three reps, and
the search has stepped to rl=1185. No c50 boundary run has started.

### The problem

Achieved rho is bounded by capacity. True capacity in the corrected c10 cell is
1987.4, so achieved rho against the configured C=2000 **cannot exceed 0.9937** no
matter how high `rl` is set. That number is the registered prediction.

So the prediction is that the boundary sits **at the capacity ceiling**, and the
cell is therefore SAFE at every load it is possible to offer. A bisection
terminates only by finding a non-SAFE point. If the prediction is right, no such
point exists, and `upward_step` walks +10% for ever: 1185, 1305, 1435, and on.

This is not a defect in the correction. It is the instrument being wrong for the
hypothesis: the search was built to bracket a boundary from above, and the
corrected cell has no reachable region above it.

### What the data shows so far

| rl | recovery delivered | total | achieved rho (vs C) | queue peak | class |
|---:|---:|---:|---:|---:|---|
| 975 | 945–949 | ~1948 | 0.974 | 6–7 | SAFE |
| 1075 | 967–969 | ~1968 | 0.984 | 16–18 | SAFE |
| ceiling | — | 1987.4 | **0.9937** | — | — |

The queue is nowhere near its 500 cap and live p99 is 8–13 ms against a 250 ms
SLO. The cell is not close to breaking; it is running out of offerable load.

### A mechanism I proposed and then withdrew

Mid-campaign I attributed this to the recovery consumer self-throttling below the
headroom, contrasting it with the uncorrected cell. **That explanation does not
survive the comparison and is withdrawn.** In the uncorrected E2 c10 cell the
consumer also delivered just below its headroom — 823.4 against 828.6, a ratio of
0.994 — and those points were UNSAFE with the queue at 2257 of 2500. Delivered
versus headroom does not separate the two cases. Queue behaviour does, and the
reason is not established here. It is recorded as unexplained rather than given a
story that fits one cell and not the other.

### Registered change of instrument

The +10% walk is replaced by **direct probes near the ceiling**, because achieved
rho asymptotes and the walk would take several probes to arrive where one can:

- **c10**: rl = 1185 (already running), then **rl = 1400**.
- **c50**: rl = 975, 1150, 1400. Its ceiling is 1997.7/2000 = **0.9989**.

Each at n=3, same runner, same in-situ probe, same everything else.

Readings, fixed now:

| outcome | reading |
|---|---|
| SAFE at every probe, achieved rho approaching the ceiling | rho\* equals the capacity ratio: the corrected cell is stable at every offerable load. The registered value is confirmed as a ceiling reached from below, not as a bracketed boundary. |
| a probe classifies non-SAFE | a boundary exists below the ceiling; bisect the bracket normally and report it against the registered value |

The first outcome cannot be expressed as a `[last SAFE, first non-SAFE]`
interval, and **no interval will be manufactured for it.** It is reported as a
lower bound on rho\* together with the ceiling that bounds it above.

### Cost

Stopping the walk saves roughly an hour of probes that are safe for reasons
unrelated to the boundary. The revised set is 12 to 15 runs, about 80 to 100
minutes, against the 3.5 hours the original two searches would have taken.

---

## Addendum 3 — correcting addendum 2: the boundary exists and was found

**Recorded immediately on the first rl=1400 result, before the point completed.**

Addendum 2 argued the bisection could not terminate, because achieved rho is
bounded by capacity and the registered prediction puts the boundary at that
ceiling. **That argument was wrong, and it was wrong on the evidence available
when I made it.** rl=1400 classifies UNSAFE:

| rl | total rps | achieved rho | queue peak | live p99 | class |
|---:|---:|---:|---:|---:|---|
| 975 | 1948.5 | 0.9743 | 7 | 8 ms | SAFE |
| 1075 | 1967.0 | 0.9835 | 18 | 14 ms | SAFE |
| 1185 | 1976.7 | 0.9883 | 111 | 58 ms | SAFE |
| **1400** | **1988.2** | **0.9941** | **500 (cap)** | **1030 ms** | **UNSAFE** |

The error was reading two flat points as an asymptote. By rl=1185 the queue had
already gone 7 → 18 → 111 and live p99 8 → 14 → 58 ms; the cell was visibly
degrading toward its limit, and the +10% walk would have found the boundary at
1305 or 1435, one or two probes on. The claim that no non-SAFE point exists was
not supported by the data I had.

The change of instrument still helped — a direct jump found the ceiling in one
probe rather than two — but it was justified by a wrong argument, and the record
says so rather than keeping the outcome and quietly dropping the reasoning.

The mechanism withdrawn in addendum 2 stays withdrawn; nothing here revives it.

### What the result says about which overhead governs

The cell broke at achieved rho **0.9941**, against:

| prediction | source | rho\* | verdict |
|---|---|---:|---|
| **0.9937** | saturated calibration (registered) | ceiling 1987.4/2000 | **the break sits 0.0004 above it** |
| 0.9972 | in-situ drain cycle, 0.478 ms | ceiling 1994.4/2000 | **excluded** — the cell broke below it |
| 0.9894 | 90%-load calibration | ceiling 1978.8/2000 | excluded — the cell was SAFE well above it |

So the **saturated** figure is the one that governs the boundary, which is what
addendum 1 registered as primary and gave a reason for. The in-situ cycle time is
a real and stable third value — 0.478 ms across every rate, against 0.4947
saturated — but it does **not** predict where the cell breaks.

That is worth stating plainly: the in-situ measurement was the better instrument
in principle and turned out to be the wrong predictor in practice.

### Refinement still needed

The bracket is [1185 SAFE, 1400 UNSAFE], which is 215 rps wide — far coarser than
the registered 5 rps. In rho it is [0.9883, 0.9941], a width of 0.0058, because
rho compresses hard near the ceiling. One probe at **rl = 1290** should close it
to under one rho-step. That is run after the c50 probes, at n=3.

---

## Addendum 4 — correcting addendum 3: the bracket does not yet discriminate

**Recorded before the refinement probe runs, while its outcome is unknown.**

Addendum 3 said the saturated prediction governs and the 90%-load prediction is
"excluded — the cell was SAFE well above it". **That is wrong.** The c10 bracket
is rho [0.9883, 0.9941], and it contains *both* candidates:

| prediction | rho\* | in the bracket [0.9883, 0.9941]? |
|---|---:|---|
| saturated (registered) | 0.9937 | **yes** |
| 90% load | 0.9894 | **yes** |
| in situ | 0.9973 | no — excluded |
| measured ceiling | 0.9937 | yes |

The highest SAFE point is 0.9883, which is *below* 0.9894, not above it. Nothing
observed so far is inconsistent with the 90%-load figure. The only claim the data
supports is the negative one: **the in-situ overhead does not predict where the
cell breaks**, being 2.4 bisection steps above the bracket.

I reached the stronger conclusion by comparing the single UNSAFE point against
0.9937 and ignoring that the bracket's lower end sits below the other candidate.
A bracket 215 rps wide cannot separate two predictions 0.0043 apart.

### What the refinement decides

The probe at rl = 1290 discriminates cleanly, and the reading is fixed here
before it runs:

| outcome | bracket becomes | reading |
|---|---|---|
| 1290 SAFE | rho [~0.991, 0.9941] | excludes 0.9894, retains 0.9937 — **the saturated figure governs** |
| 1290 UNSAFE | rho [0.9883, ~0.991] | excludes 0.9937, retains 0.9894 — **the 90%-load figure governs** |

Either way one candidate survives and one dies. That is the whole purpose of the
refinement, and addendum 3 should have said so instead of announcing a winner.

---

## Addendum 5 — the estimator disagreement is as large as the thing being measured

**Recorded on completing the campaign, before the report was written.**

Addenda 3 and 4 compared the candidate overheads against brackets computed with
the **as-measured** (drain-window) estimator. The registered estimator is **A4**,
the delivery-span one used by E1, E2, E2b, E2c and E2d. Applying A4 changes the
answer:

| arm | estimator | bracket | which candidate is inside |
|---|---|---|---|
| c10 | as-measured | [0.9883, 0.9924] | 90% load (0.9894) |
| c10 | **A4 (registered)** | **[0.9956, 1.0016]** | **in situ (0.9974)** |
| c50 | as-measured | [0.9915, 0.9944] | none |
| c50 | **A4 (registered)** | **[0.9999, 1.0064]** | none |

So the c10 verdict **inverts** with the estimator: the 90%-load figure under one,
the in-situ figure under the other. That is not a result, it is an artefact of a
choice, and reporting either as the answer would be wrong.

### Why neither estimator can settle it

The two disagree by about **0.0080** in rho. The candidate predictions span
**0.0080** in the c10 arm (0.9894 to 0.9974). **The measurement uncertainty is the
same size as the effect being discriminated**, so this experiment cannot say
which overhead figure governs the boundary. That conclusion is forced by the
data, not chosen.

There is a reason to distrust A4 specifically at the non-SAFE points. Its values
there exceed each cell's own **measured saturation plateau** — by +0.0079 in c10
and +0.0073 in c50 — and no system can sustain more than its plateau. A4 measures
the recovery rate over the span the traffic occupied, which on a collapsed run
excludes stalled intervals and so overstates the sustained rate. A4 was designed
to remove the drain-detector tail bias at SAFE points and does that well; it was
never validated on collapsed runs, and this is the first campaign whose interval
endpoints depend on it there.

The as-measured estimator has the opposite bias, dividing an exact backlog by a
window padded with the drain-detector tail. The true value lies between, and each
cell's measured plateau — 0.9937 and 0.9991 — does sit between the two brackets.

### What survives regardless of estimator

1. **The plateau gates.** Predicted 1987.4 and 1997.7, measured 1987.4 and
   1998.1, errors of -0.00% and +0.02%. These are direct throughput
   measurements and involve no rho estimator at all. The additive model is
   confirmed by them alone.
2. **The gap between the arms is essentially eliminated**: 0.0026 under
   as-measured, 0.0045 under A4, against 0.0706 uncorrected — **94% to 96%
   removed** either way, bracketing the registered 92.7%.
3. **Both arms land within about 0.008 of 1.000** under either estimator, which
   is the brief's original prediction before addendum 1 refined it.

### What does not survive

The addendum-1 refinement — that the correction under-corrects and predicts
0.9937 and 0.9989 specifically — **cannot be tested by this campaign.** Under A4
both arms sit above those values, under as-measured both sit below, and the
difference between the two candidate positions is smaller than the estimator
spread.

Addenda 3 and 4 are superseded in their conclusions and retained for the record.
