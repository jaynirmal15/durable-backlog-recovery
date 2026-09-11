# Phase 0 Notes

## Platform change — the campaign moved to EC2 before E1 (2026-09-11)

**Every boundary run from E1 onward is measured on EC2, not on the laptop.**

| | Machine |
|---|---|
| Gate 0, Phase 1, and the whole 2026-08-18 corpus | MacBookPro15,2 — Intel i5-8259U, 8 cores, 8 GiB |
| E1 onward | EC2 `c6i.2xlarge` — 8 vCPU, 16 GiB, Ubuntu 24.04, Docker native |

The move is for measurement integrity, not convenience. The laptop ran the
experiment alongside everything else on a desktop machine, and the 2026-08-19
campaign was lost precisely to that: load climbed during the runs, the injector
fell from 99.4–99.8% delivery to 96.2%, and the conclusions from that stretch
were withdrawn. A dedicated box removes the class of problem rather than
watching for it. The instance is deliberately fixed-performance — a burstable
t-series would throttle once CPU credits ran out and change the downstream's
service rate partway through a drain.

### What this means for the old numbers

**The 2026-08-18 last-SAFE values are SEARCH STARTING POINTS, not comparisons.**

`PRE-REGISTRATION.md` §3 step 0 already requires every anchor to be re-verified
on the current harness before a search proceeds, and a non-SAFE anchor sends the
search downward (amendment A2). That is what the old values are for: they say
where to start probing. They are not a baseline, and an E1 interval that lands
somewhere else is **not** evidence that anything moved.

**No cross-platform claim is made anywhere.** Not in this file, not in the
boundary files, not in the paper. Any statement of the form "ρ* moved from X to
Y" across the platform change would be comparing two machines and one harness
fix at once, with no way to separate them. If a before-and-after on the harness
fix is ever wanted, it needs both arms re-measured on the same box.

The three laptop runs at the C0/10 anchor that were probed on 2026-09-11 before
the move are retained in `results/laptop-preec2/` and are excluded from E1 for
the same reason.

### Recorded per run

Every record now carries the machine and its condition, so none of this has to
be inferred from a date:

- `platform`: instance type, kernel, OS/arch, CPU model and count, memory,
  Docker version, Go version
- `hostLoad1Min` / `Mean` / `Max`, `hostLoadSamples`, `hostLoadBreached` — the
  1-minute load sampled every 10 s **for the life of the run**, not only at the
  start. A start-only reading cannot see load that climbs during measurement,
  which is the exact failure that cost the 2026-08-19 campaign.
- `hostFreeDiskGB`, and the queue-cap and jitter settings

A run whose load breaches `cores × 1.0` at any sample is marked invalid with
`host_load_breached_during_run` and halts the search, so it is reported rather
than silently kept.

Provisioning is committed under `deploy/`.


<!-- Every section dated 2026-08-19 was reconstructed from the 2026-08-19 session log; original was never committed.
     See RECONSTRUCTION.md. -->

## Downstream validation (2026-08-13)

Load sweep against graceful profile, CAPACITY=2000, SERVICE_TIME_MS=5, TIMEOUT_MS=2000.

Observed:
- Flat p99 ≈5–8ms from 20–95% util
- Clear knee at util≈1.0 (p99 jumps from ~7ms → ~30ms at 100%, then hundreds of ms)
- Timeouts appear under sustained overload (≥1.5–2.0×); with 50× queue, in-queue wait alone maxes ~250ms, so 504s come from admission wait under open-loop overload
- Dropping capacity to 1400 moves the knee left; same absolute offered load that was healthy at 2000 saturates at 1400

Load generator must be open-loop. Closed-loop self-throttles and hides the knee.

Data: `results/load_sweep.csv`

## Smoke run (2026-08-13)

`make up && make smoke` (live=400, capacity=800, outage=15s)

- `backlogAtRestore=5989` ≈ 400×15 — deterministic backlog OK
- Drain completed; live/recovery classes separated in JSONL
- With workers=32 and ~50ms observed latency, consumer pool capped offered ≈690 rps
  below capacity 800 — for full P0 runs keep workers=64 (or higher) so unrestricted
  catch-up can actually hit the downstream knee
- Run record: `results/smoke-p0a.json`

## Runner: consumer must start with producer

Warmup with producer alone builds ~λ×warmup backlog; starting the consumer
afterward looks like a mini outage and fails the pre-outage SLO check.

## Live / recovery concurrency architecture (load-bearing for methods)

**Scoping assumption:** live work and recovery work arrive on **independent
paths** to a shared downstream. This models a common deployment: a synchronous
API writes to a dependency while a separate backlog consumer drains accumulated
work to the same dependency. Recovery admission control is meaningful here —
throttling the consumer frees capacity for live. Where live shares an ordered
log with recovery, head-of-line blocking means throttling recovery does not help
(empirically: prior campaign NATS-live was starved to 20–37 rps during drain;
that result is retained as evidence for this scoping choice, not as Gate 0 data).

| Phase | Producer → JetStream | Injector → downstream |
|---|---|---|
| Warm-up / healthy | **off** (avoids 2×λ_L) | running at λ_L |
| Outage (no consumer) | **running** — builds backlog | running at λ_L |
| Restoration → T_full | **stopped** | **running at λ_L continuously** |

Warmup is injector-only so the healthy check measures the live path at λ_L
against capacity C. Producer starts at outage begin so backlog ≈ λ_L×outage
(unchanged vs prior campaign). The discarded first-campaign finding that
NATS-live was HOL-starved to 20–37 rps during concurrent drain remains
evidence that live must not share the ordered log with recovery.

```
  Producer (pre-restore only) ──► JetStream ──► Consumer ──► recovery only
                                                              (post-restore)
  Runner live injector ──────────────────────────► Downstream
       (λ_L open-loop, age_ms=0)                    (shared capacity C)
```

**Consequences:**
- No post-epoch JetStream messages → NATS-live population is zero after restore
- `V_SLO` and `T_full` are both measured on injector-live (one population)
- Injector does **not** stop at `T_drain`; integrity fails if injector issue rate
  is zero anywhere between restore and `T_full`

Superseded (nats_live_contamination_post_drain): the first formal 12-run campaign
kept the producer running after restore and stopped the injector at `T_drain`,
so the post-drain saturation tail was secondary NATS-live backlog — an artefact
of the two-path design, not residual recovery from the outage.

## Capacity resize must not rebuild the queue

P0-B died at t=20s: `SetCapacity` stopped all workers and closed the queue under
~1k in-flight requests, wedging/crashing the process (`cap=0`). Resize now only
adjusts the worker target + soft queue cap in place.


## Workers must exceed downstream concurrency under queueing

Default 64 workers is too low for full-scale runs: at ~40ms latency the consumer
self-limits to ~1600 rps and never hits the 2000-rps knee. Use `-workers 512`
so in-flight work can fill the graceful queue (≈500) and press the downstream.

## Gate 0 status (2026-08-14)

First formal 12-run campaign **invalidated** (`nats_live_contamination_post_drain`).
Architecture corrected; pilot accepted; **v2 campaign 12/12 valid**. Memo: `results/GATE0-memo-v2.md`.
Gate 1 prep probes: `results/GATE1-probes.md`.

## Gate 1 decisions (frozen 2026-08-14)

| Item | Decision |
|---|---|
| Operating point | λ_L=1000, C=2000 — keep |
| W | 15 s — keep |
| Primary frontier | tDrain × vSLO |
| Secondary safety | G_norm = G_policy / **998** (c10) — see G_ceil note below |
| Saturated-regime | timeout rate |
| Healthy-vs-healthy | tDrain |
| Demoted | qPeak (soft-cap censored); p99 demoted in saturation |
| T_full | reported, not a frontier axis on this downstream |

Phase 1 = static sweeps only (no controllers). §3a cliff under C0: **done**
(`results/PHASE1A-cliff-C0.md`) — coarse max safe rl=825, cliff by 900.
Fine sweep + occupancy analysis: `results/PHASE1A-followups.md` — max safe
rl=840; marginal 855; collapsed by 870 (width 30 rps). G_ceil=998.
§3b not started.

## METHODS COMMITMENT — establish the mechanism before reporting (2026-08-19)

**No result is reported until its mechanism is established.** Where a result
could plausibly be produced by the harness, run a control that distinguishes
"property of the system" from "property of the implementation" *before* the
result is written up, not after review asks.

The model is the `PROFILE=cliff` control below: one 65-second run, same load and
capacity, differing only in the implementation detail under suspicion. It
converted a plausible headline (queueing hysteresis with strong control
implications) into a diagnosed defect.

**Why this rule.** Every major finding in this project so far has had a harness
explanation:

| # | Claimed finding | Actual cause |
|---|---|---|
| 1 | Post-drain saturation tail | NATS-live contamination (two-path artefact) |
| 2 | Live SLO population | blended live/recovery — corrected in Phase 0 |
| 3 | Transition width invariant ≤0.007 | grid resolution; downgraded to an upper bound |
| 4 | Sharp cliff, no marginal band | partly low concurrency; now also queue-cap/SLO coupling |
| 5 | ρ* values, two-class pairing | tick-dropping `time.Ticker` in both pacers |
| 6 | Hysteresis at the knee | spin-wait admission control |

Six for six. That is not a failing harness — it is what checking looks like —
but it sets the prior. **Assume a harness explanation exists until a control
rules it out.**

Corollaries already in force:
- Do not claim invariance at a precision finer than measurement bias + grid step.
- Report achieved rates, never nominal, wherever a pacer is involved.
- Retain raw per-request data; it was decisive in (2), (5) and (6).

---

## CRITICAL — collapse regime is a harness artefact (2026-08-19)

**The `graceful` profile's admission control is a busy-wait, and it manufactures
congestion collapse.** This is a harness defect, not a property of the
dependency. It contaminates every collapsed-regime measurement in Phase 1.

### Mechanism

`downstream/main.go` `Process()`, graceful path: a request that cannot enter the
queue spins on `time.After(100 * time.Microsecond)`, re-checking `softLen()`,
until it is admitted or the 2 s timeout expires. Each waiter allocates a timer
every 100 µs. With a few thousand waiters that is tens of millions of timer
allocations per second, which saturates the host and starves the 10 worker
goroutines. Less service → more waiters → more CPU → less service. The feedback
loop belongs to the harness.

### Evidence (C=2000, S=5, 10 workers, 8-core host)

| state | offered | served/s | timedOut/s | qMean | frac ≤SLO | container CPU |
|---|---:|---:|---:|---:|---:|---:|
| healthy | 1850 | **1837** | 0 | 171.8 | 1.000 | **~76%** |
| collapsed | 1950 | **1463** | 459 | 500.4 | 0.000 | **1216%** |
| collapsed | 1700 | **1589** | 113 | 500.4 | 0.000 | **~1050%** |
| healthy | 1500 | **1500** | 0 | 1.7 | 1.000 | **~58%** |

CPU rises **16×** while *useful* service **falls**. Data:
`results/hysteresis-s5-c2000-mechanism.json`.

### Control — same load, admission without the spin

`PROFILE=cliff` rejects instead of spin-waiting. Same C, same concurrency, same
offered rate:

| profile | offered | frac ≤SLO | qMean | CPU |
|---|---:|---:|---:|---:|
| graceful | 1950 | **0.000** | **500.4** | **1216%** |
| cliff | 1950 | **0.886** | **17.4** | **~100%** |

The collapse disappears when the spin-wait is removed. Data:
`results/hysteresis-cliff-control.json`.

### Consequence — what is and is not contaminated

**Contaminated (measured the harness, not the dependency):** every collapsed /
"unsafe" grid point; H3 in both arms (vSLO 0.795 / 0.820, timeout rates,
p99 ≈ 2 s); concurrency-effect finding (3) "severity past the boundary falls with
concurrency"; the two-class near-ρ→1 penalty; the hysteresis measured below.

**Not contaminated (CPU 57–78% of one core, served/s tracks arrivals exactly):**
the healthy/safe regime — ρ* bracketing from the safe side, `tDrain` and
`G_norm` for safe policies, occupancy on the lower branch, and the whole H4
(wrong-low) result.

**Onset vs severity:** a run at ρ ≈ 0.975 begins to queue for genuine M/D/c
reasons; the spin-wait then amplifies that into total collapse and holds it
there. So the *existence* of a boundary is real; its *severity, persistence, and
hysteresis width* are artefacts.

### Hysteresis measurement — retained as evidence of the defect, NOT as a finding

Continuous stepped load, no gap or capacity reset between steps
(`scripts/hysteresis`, `results/hysteresis-s5-c2000.json`,
`results/hysteresis-s5-c1400.json`):

| C | safe from idle | still collapsed on the way down | recovered | Δρ |
|---:|---|---|---|---:|
| 2000 | 1850 (ρ=0.925) | 1900, 1850, 1800, 1700 (ρ=0.850) | ~1650 partial | **≥0.10** |
| 1400 | 1250 (ρ=0.893) | 1300, 1250 (ρ=0.893) | **1150 (ρ=0.821)** | **0.071** |

Both capacities show the same shape: the lower branch is re-entered at
ρ ≈ 0.82, well below the ρ ≈ 0.89–0.93 at which it is left. **Do not present
this as a control finding.** It is a property of the busy-wait, and it would not
appear on a dependency that sheds or blocks instead of spinning. It does
resolve the C=1400 offered-1250 anomaly: 1250 is genuinely on the lower branch,
and the earlier reading was collapsed-state carryover.

### Fix applied and verified (2026-08-19)

Graceful admission now **blocks on a semaphore** (`Server.slots`, a token channel
with a timeout `select`). A waiting request parks on a channel receive and is
woken one-per-release; one timer per request instead of one per 100 µs per
request. `resizeSlots` keeps the token count in step with `SetCapacity`.

**Verified at offered 1950, C=2000, S=5** (`results/hysteresis-s5-c2000-blocking.json`):

| admission | frac ≤SLO | qMean | served/s | timedOut/s | CPU |
|---|---:|---:|---:|---:|---:|
| spin-wait (old) | 0.000 | 500.4 | 1463 | 459 | **1216%** |
| **blocking (new)** | 0.000 | 500.0 | **1620** | 269 | **~100%** |
| cliff | 0.886 | 17.4 | 1501 | 0 | ~100% |

**CPU fixed (10× reduction, stays near one core). Useful service recovers from
1463 to 1620/s. Hysteresis largely gone** — after collapse, offered 1700 recovers
to frac 0.469 within 45 s, versus staying pinned at 0.000 under the spin-wait.

**But the cliff survives the fix.** At ρ = 0.975 blocking-graceful still gives
frac = 0.000 with the queue at cap. So the sharp boundary is **not** a spin-wait
artefact — the spin-wait exaggerated its severity and manufactured the
hysteresis, but did not create the boundary.

### Anchor measurements — profile dominates the admission fix (2026-08-19)

Same policy (H3: rl=840 under C1, ρ_nom = 1.31), three admission designs, 2 runs
each. Safe anchor (C0 rl=840) for contrast.

| anchor | tDrain | vSLO | p50 | p99 | G_norm | timeout | qMean |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0-840 spin-wait (safe) | 146.0 | 0.000 | 6 | 24 | 1.001 | 0.000 | 2.2 |
| C0-840 blocking (safe) | 142.5 | 0.000 | 6 | 42 | 0.977 | 0.000 | 3.5 |
| H3 spin-wait | 152.0 | **0.795** | 687 | 1960 | 0.140 | 0.235 | 303.6 |
| H3 blocking-graceful | 209.0 | **0.868** | 1999 | 2002 | 0.080 | 0.567 | 398.4 |
| **H3 cliff** | **140.5** | **0.778** | **15** | **19** | **0.737** | **0.000** | **11.2** |

**1. Safe side is unaffected by the fix** (−2.4% tDrain, −2.4% G_norm, vSLO 0
both). The clean/contaminated split holds: healthy-regime Phase 1 results stand.

**2. Collapsed side moved a lot under the fix** — tDrain +38%, p50 +191%,
timeout rate +141%, G_norm −43%. And it moved *worse*: the spin-wait's unfair
admission let fresh arrivals jump the queue, masking latency (p50 687 vs 1999)
while degrading capacity. Pre-fix collapsed runs were also suspiciously
reproducible (tDrain 152.0 / 152.0, spread 0.0%); post-fix they are properly
stochastic (221 / 197, spread 12%). **The tight agreement of collapsed-regime
repetitions was itself an artefact of the CPU clamp** — anything in Phase 1 that
treated close agreement across repetitions as evidence was reading the clamp.

**3. Profile choice dominates the fix, by an order of magnitude.** At the same
ρ = 1.31, `cliff` gives p99 = **19 ms** and G_norm = **0.737** with **zero**
timeouts, versus p99 ≈ 2000 ms and G_norm 0.08–0.14 under either graceful
variant. Graceful suffers latency collapse; cliff sheds load cleanly and keeps
live traffic fast. Same policy, same capacity, same concurrency.

**4. vSLO is nearly blind to this.** Across the three designs vSLO reads 0.795 /
0.868 / 0.778 — a spread of 9% — while p99 varies **100×**, goodput **9×**, and
timeout rate from 0.000 to 0.567. Under `cliff` the SLO breach is via *error
rate* (503 shedding), under `graceful` via *latency*; vSLO cannot tell them
apart because it counts violating seconds without recording which predicate
fired.

> **Consequence for the frontier metrics.** vSLO cannot be the primary safety
> axis for saturated-regime comparisons. It saturates, and it conflates
> "dependency sheds load and live traffic stays fast" with "live traffic times
> out". This generalises the Verification-A blind-zone note, which found the
> same defect in the opposite direction (degraded-but-passing): **vSLO is blind
> at both edges of its range and discriminating only in the narrow band
> between.**

### Frontier axes changed (decision, 2026-08-19)

**Primary: `tDrain` × `G_norm`.** `G_norm` separates the two profiles by **9×**
where vSLO separates them by **9%**, and it has range in both regimes
(0.08–1.00 measured, versus vSLO pinned at 0.78–0.89 across everything
saturated). This also answers the earlier worry that adaptive and RHC would fail
to separate on vSLO near the knee.

**vSLO retained, demoted, and decomposed** — the runner now records:

| field | meaning |
|---|---|
| `vSLO` | violating seconds / T_full (artifact-excluded), as before |
| `vSLO_latency` | fraction of seconds where live p99 > SLO |
| `vSLO_error` | fraction of seconds where live error rate > ε |
| `vSLO_both` | overlap — seconds where both predicates fired |

A second counts in whichever fired; both are counted when both fire, with the
overlap recorded so the components are not naively additive. Pre-2026-08-19
records have no decomposition and report 0 for the components.

**`p50` and timeout rate are standing columns in saturation.** p50 moved **191%**
at the collapsed anchor while vSLO moved 9%.

### Profile scope (decision, 2026-08-19)

**`graceful` is the primary model; `cliff` is a reported boundary condition, not
a second dimension.** A connection-pooled database queues rather than rejects,
queueing-to-latency-collapse is the more common failure mode, and it is the case
where recovery admission control has something to contribute. Under `cliff` the
dependency partially protects itself (live stays at 19 ms) and the harm appears
as shed load instead.

Boundary-condition statement supported by the anchor data: *where the dependency
sheds load rather than queueing, the harm from unrestricted recovery is reduced
load acceptance rather than latency collapse, and the case for admission control
is correspondingly weaker.* Obtained from two runs, not a parallel campaign.

### WARNING — suspiciously tight reproducibility has twice indicated an artefact

Pre-fix collapsed runs agreed **to the second** (tDrain 152.0 / 152.0, spread
0.0%). Post-fix the same point spreads **12%** (221 / 197). The tight agreement
was the CPU clamp pinning the system to a fixed degraded operating point, not
precision.

This reaches the **transition-width** work, where "both runs at this rate
collapsed identically" formed part of the evidence — that agreement is now
suspect for every collapsed-regime grid point.

**General rule:** in this project, unusually tight run-to-run agreement in a
*saturated* regime is evidence of a clamp, not of a clean measurement. Treat it
as a prompt to look for the mechanism, not as confirmation. (Second occurrence:
the first was transition width reading as invariant because it equalled one grid
step everywhere.)

### The cliff is a consequence of the queue-depth multiplier, not of queueing

`queueCapFor(graceful) = 50 × concurrency`, and `concurrency = C × S`. So the
delay represented by a **full** graceful queue is

    (50 × concurrency) / (concurrency / S) = 50 × S = 50 × 5 ms = 250 ms

— **independent of C and of concurrency, and exactly equal to the 250 ms SLO.**
In the graceful profile "queue full" is definitionally "SLO breach". `cliff`
caps the queue at 2 × concurrency (10 ms at S=5) and sheds the excess as 503s,
which is why it degrades smoothly at the same offered load.

This plausibly explains several Phase 1 results at once: the sharpness of the
boundary, the absence of a marginal band, and why ρ* came out similar across
capacities (the queue-delay-at-cap is capacity-invariant by construction).
**Profile and queue-depth multiplier are therefore first-class experimental
parameters, not implementation details**, and the paper must justify which models
a real dependency rather than defaulting to `graceful` with 50×.

At S=25 the same arithmetic gives 50 × 25 ms = **1250 ms**, five times the SLO —
so the c50 arm's queue is *not* SLO-matched, which may be the real reason the
c50 transition looked softer and ρ* higher. **This needs re-testing, and it is a
more parsimonious explanation than "ρ* rises with concurrency".**

---

### Load-generator pacing defect (2026-08-19) — affects ρ throughout Phase 1

**Mechanism.** Both the probe generator (`scripts/probe_live_only` `flood()`)
and the consumer recovery limiter (`consumer/main.go`) paced with
`time.NewTicker(1s/rate)` and received from `ticker.C`. **Go tickers drop ticks
when the receiver is late.** Delivered rate therefore degrades silently with
in-flight count, offered rate, and process warm-up — and never reports the
shortfall.

**Measured shortfall (achieved / target):**

| generator | condition | delivered |
|---|---|---|
| probe `flood()` | S=25, first point of a process | **88–97%** |
| probe `flood()` | S=25, later points | 97–99.8% |
| probe `flood()` | S=5, ≤1600 rps | 99.9% |
| probe `flood()` | S=5, 1800–1950 rps | 98.4–98.5% |
| consumer limiter | rl=900 → rl=990 | **98.4% → 97.2%** (worsens with rl) |
| runner injector | λ_L=1000, both arms | 99.4–99.8% |

**Decision — fix the probe, do NOT change the consumer limiter mid-phase.**
- `flood()` is **replaced** with a token-bucket pacer (target count derived from
  elapsed wall time, so a late loop catches up rather than losing requests).
  Probe results are self-contained, so there is no cross-run comparability cost.
- The **consumer limiter is left as-is.** Changing it would make `rl` mean
  something different in C2/C3 than in every prior Phase 1 run — a silent
  discontinuity mid-campaign, which is worse than a known, measured bias.
  Instead: report **achieved** recovery rate alongside nominal `rl` in every
  result, and compute ρ from achieved.
- **Generator self-check added to the runner:** injector rate is measured over
  the warm-up window and the run is **refused** (`generator_rate_deviation_at_warmup`)
  if it is outside ±1% of target. Recorded as `warmupInjectorRps` /
  `warmupInjectorAccuracy` on every run. The ticker defect was invisible for the
  whole c50 campaign; this makes it loud.

**Consequence for ρ — do not cite nominal ρ without the achieved value.**
Every Phase 1 ρ was computed as (λ_L + rl) / C_d from *nominal* rates. True
utilisation is lower, and **the shift is not uniform**:

| condition | ρ nominal | ρ achieved | shift |
|---|---:|---:|---:|
| c10 C0 last-safe (rl=840) | 0.9200 | **0.9089** | −0.0111 |
| c10 C1 last-safe (rl=290) | 0.9214 | **0.9155** | −0.0060 |
| c10 C1 first-unsafe (rl=300) | 0.9286 | **0.9237** | −0.0049 |
| c50 C1 last-safe (rl=380) | 0.9857 | **0.9792** | −0.0065 |
| c50 C0 (rl=900, safe) | 0.9500 | **0.9403** | −0.0097 |

Shifts are 0.005–0.011, i.e. **0.7×–1.6× the stated transition width (0.007)**.

**What survives:** transition *width* is robust — it is a difference between
adjacent grid points within one condition, where the bias is near common-mode.
**What does not:** "ρ* = 0.92 to 3 s.f. across a 30% capacity drop" becomes
**0.909 (C0) vs 0.916 (C1)** — still close, but a spread of ~0.007, i.e. one
transition width, not agreement to 3 s.f. "ρ* ≈ 0.92 at 7–10 servers,
≈0.986–0.988 at 35–50" becomes ≈**0.909–0.916** and ≈**0.979**. The
*qualitative* finding (ρ* rises with concurrency) is unaffected — the gap is
~0.07, an order of magnitude larger than the bias.

### Two-class comparison at 50 servers — conclusion partly withdrawn (2026-08-19)

`PHASE1B-twoclass-s25.md` paired live-only against two-class **at equal nominal
offered**. Because the consumer limiter under-delivers more than the injector
does, the two-class side sat at systematically **lower achieved ρ**:

| nominal total | live-only ρ_ach | two-class ρ_ach | Δ | live-only qMean | two-class qMean |
|---:|---:|---:|---:|---:|---:|
| 1900 | 0.9477 | 0.9403 | −0.0074 | 0.3 | 0.3 |
| 1950 | 0.9688 | 0.9620 | −0.0067 | 1.1 | 1.2 |
| 1975 | 0.9854 | 0.9728 | −0.0126 | 3.4 | **7.3** |
| 1990 | 0.9918 | 0.9772 | −0.0146 | 39.7 | **201.1** |

The two-class side was **advantaged by up to 2× the transition width** at every
row. Interpolating live-only to matched achieved ρ: at ρ≈0.973 live-only q≈1.7
vs two-class 7.3 (**4.4×**); at ρ≈0.977 live-only q≈2.3 vs two-class 201
(**~87×**).

**Survives:** the headline verdict. Two-class vSLO at 50 servers is 0.029 versus
0.844 at 10 servers — the *catastrophic* collapse genuinely does not reproduce.
**Withdrawn:** "through ρ=0.975 the two paths are indistinguishable" (they were
never compared at the same ρ) and "Verif-A effect was **largely** a
low-concurrency artefact" (overstated — the effect is weaker at 50 servers but
substantially larger than reported). Rewrite the architecture justification
against achieved ρ before citing it.

### Live-only knee is order-sensitive at the margin (2026-08-19)

Descending re-sweeps at S=5 (`probe-warmup-check-s5-c2000-desc.json`,
`...-c1400-desc.json`) contradict the ascending determinations at the margin:

- **C=2000:** ascending had last-safe **1900** (p99=246 against a 250 ms SLO,
  frac=0.996 — barely passing). Descending, arriving from a collapsed 1950,
  1900 gives p99=**3311**, frac=**0.179**. 1850 passes cleanly in both
  (p99 24–80). **1900 is bistable, not safe.** The robust last-safe is **1850**
  → ρ*_live(2000) = 0.925 nominal / **0.910 achieved**, not 0.950.
- **C=1400:** 1300 confirms safe descending (p99=17, qMean=2.5 — far healthier
  than the ascending reading of p99=122, qMean=80.8). The 1250 point is
  **anomalous** (frac=0.147 at a *lower* offered rate than a passing point);
  non-monotonic, discard and re-measure.

**Implication for verif A's "live-only ρ* is not invariant" claim (0.929 @1400
vs 0.950 @2000): it does not survive.** With the robust C=2000 value, ρ*_live is
0.925–0.929 nominal at both capacities. The probe protocol has no per-point
reset and no stall detection; single-order sweeps should not be used to locate a
knee that sits inside a bistable band.

**Arm-relative normalisation (2026-08-19).** `G_ceil` is measured **per arm**,
so any table putting c10 and c50 side by side is normalising against separately
measured denominators. State this wherever the arms are compared.

**G_ceil = 998 is the INJECTOR's ceiling, not the downstream's (2026-08-19).**
With the pacing defect fixed (multi-lane pacer), a live-only probe at offered
1000 against C=2000/S=25 delivers **1000.0** rps and **1000.0** goodput,
frac=1.000. The original `G_ceil` = 998 came from a ticker-paced Probe 1 whose
own 0.2% shortfall *was* the missing 2 rps. The downstream was never the
constraint at λ_L.

**Keep G_ceil = 998 for Phase 1.** G_norm asks what fraction of *achievable*
live goodput a policy preserved, and the achievable value for this harness is
what the runner's injector can deliver (99.4–99.8% of λ_L). Normalising by 1000
would fold the injector's own shortfall into every policy's score and no run
could reach 1.0 even with zero recovery load.

**Consequence for Phase 2:** when the injector and consumer limiter are
re-paced with the lane design, **G_ceil becomes 1000** and every G_norm shifts
up ~0.2%. Re-measure it with the fixed generator and state which generator any
G_norm was computed against — Phase 1 and Phase 2 G_norm are not directly
comparable until that is done. This is part of the same re-anchoring as the two
Phase 1 anchor-point re-runs (c10 C0 rl=840, c50 C1 rl=380).

**Injector re-paced (2026-08-19).** The runner's live injector used the same
single `time.Ticker`, delivering **99.2–100% of λ_L at S=5 but only 98.4–98.7%
at S=25** (~25 vs ~5 goroutines in flight). That is a systematic **between-arm
bias**: the c10 and c50 arms were never run at the same live load, so every
cross-arm comparison — including the headline concurrency result — compared arms
whose λ_L differed by ~1% (≈0.005 in ρ, about one transition width). It does not
overturn the ~0.07 c10/c50 ρ* gap, which is an order of magnitude larger, but it
must be stated wherever the arms are compared.

Replaced with the multi-lane deadline pacer. **Both arms now deliver 99.98%**
(`smoke-injfix-c10`, `smoke-injfix-c50`), so the ±1% generator self-check is
satisfiable everywhere and was **not** relaxed globally.

**Pacer A/B on one downstream (2026-08-19).** `scripts/probe_live_only -pacer
ticker|lanes` A/Bs the arrival process with everything else held fixed.
C=2000, S=5, blocking-graceful:

| offered | ticker | lanes |
|---:|---|---|
| 1000 | achieved 975.4, qMean **20.0**, qPeak **500**, p99 779, sloOK **false** | achieved **1000.0**, qMean **0.1**, qPeak 3, p99 **8** ✓ |
| 1600 | achieved 1549.2, qMean 3.5 | achieved 1595.1, qMean **1.4** |
| 1850 | achieved 1793.0, qMean **4.4** ✓ | achieved 1803.7, qMean **487.9** ✗ |

**Neither pacer is uniformly better.** At λ_L = 1000 — the only rate the runner's
injector uses — `lanes` is decisively better (exact rate, qMean 0.1 vs 20). At
1850 `lanes` degrades: 10 lanes staggered 0.54 ms apart fall below OS timer
resolution and wake together, so the stagger collapses and arrivals bunch. The
ticker cannot bunch (single goroutine, drops rather than accumulates) but
under-delivers 3-4%.

**Rule:** use `lanes` where lanes ≤ ~5 (rate ≤ ~1000/lane-interval); above that
the stagger is finer than the timer and the design degrades. For live-only
probes at 1600+, prefer `ticker` and report achieved, not offered. **Sub-
millisecond even spacing is not achievable with OS timers** — any open-loop
generator at those rates either drops or bunches. State which.

**Generator pacing — three designs, two wrong (2026-08-19).**

| design | delivered rate | arrival smoothness |
|---|---|---|
| `time.Ticker` receive | **88–99%** (drops ticks under load) | smooth |
| single-lane catch-up (target from elapsed time) | 100.0% | **bursty** — discharges timer debt; offered 1100 at ρ=0.55 gave p99 **428** ms, qPeak **446** |
| **multi-lane deadline pacer** | **100.0%** | **smooth** — p99 35–37, qPeak ≤44 across 900–1400 |

Lanes = ⌈rate/200⌉ so each lane's interval is ≥5 ms (above OS timer
granularity), phase-staggered, each sleeping to its own next deadline and
issuing exactly one request. **An open-loop generator can be wrong in two
opposite directions and neither shows up in summary metrics.** Use the lane
design when re-pacing the consumer limiter — the token-bucket version would have
improved rate accuracy while regressing arrival smoothness.

**c50 G_ceil basis — cite runner data, not a probe.** `p1b-verifb-s25-rl825-r1`
sustained **998.2** live goodput at λ_L with `fracUnderSLO` = **1.0000** *while
also carrying rl = 825 of concurrent recovery load*. A ceiling established under
concurrent recovery load is stronger evidence than one measured in isolation:
it is a lower bound achieved under strictly harder conditions than any
live-only probe, and it is measured through the same injector path that produces
the goodput being normalised. **G_ceil(c50) = 998, basis =
`p1b-verifb-s25-rl825-r1`.** The live-only probes are corroborating only.

Measured result: **both arms give G_ceil = 998.** The ceiling at λ_L is set by
the *injector*, not the downstream — both arms have large headroom at λ_L
(c10 live-only p99 = 8 ms at offered 1000; c50 p99 = 36 ms), so neither
dependency is the binding constraint and the denominators coincide. The
c10/c50 comparisons in `PHASE1B-H3H4-s50.md` are therefore unaffected in
practice, but the equality is an empirical result, not an assumption — re-measure
per arm if λ_L, C, or S changes.

Do **not** take `G_ceil` for c50 from `scripts/probe_live_only`: its generator
is a 1 ms `time.Ticker` that **drops ticks** under goroutine residency. At S=25
(~25 in-flight at λ_L) it undershoots by 1–4% (reported 981–993 at offered
1000); at S=5 (~5 in-flight) it tracks to 99.9%. Real c50 runs sustain
**998.2** live goodput at λ_L with `fracUnderSLO` = 1.0000
(`p1b-verifb-s25-rl825-r1`) — above anything the probe reported, which is how
the artifact was caught. Probe data: `results/probe-c50-gceil-s25.json`,
`results/probe-c50-gceil-s25-reversed.json`.

**G_ceil definition pinned (2026-08-19).** The record carried two values:
this table froze **985** (`GATE1-probes.md` interpolated goodput at offered
**987**) while `PHASE1A-followups.md` and every published report used **998**
(live-only goodput at offered **1000 = λ_L**). `GATE1-probes.md` itself said
"use ~985–998", never resolving it. **998 is correct and is now the definition:
live-only goodput at λ_L, measured per arm.** An unpinned ceiling is how the
2 × 998 = 1996 divisor error survived review. `scripts/report_metrics.py`
requires `--g-ceil` explicitly and never derives it from a sweep maximum.

### Phase 3 design input — leading indicator (from §3a follow-up)

Latency percentiles are flat through the safe band; **queue / in-flight level**
rises before the cliff (825 qMean≈1, 855≈18, 870≈320). Within an rl=825 drain,
occupancy is **flat** (no upward drift) — usable signal is level vs baseline,
not within-run slope. Occupancy alarms ~15–30 rps (~1.5–3% of C) before SLO
breach (855: qMean≈18, p99=95 still inside 250 ms). That band is the entire
control margin. Implication: latency-feedback adaptive concurrency (B3) may
overshoot a step-like boundary; occupancy-based control has a pre-cliff level
signal. Instantaneous capacity steps (C0→C1) make **reaction time** dominate
gradient sensitivity. Do not design a controller from this yet.

C0 frontier: rl=840, tDrain≈146 s, vSLO=0. Critical ρ* under C0 ≈ 0.92–0.935
(total ~1840–1870 / 2000). §3b tests whether ρ* and critical occupancy are
invariant across capacity regimes.

### §3b C1 result (before C2/C3)

Under C1 (C_d=1400): last safe rl=290 (ρ=0.921 nominal / **0.916 achieved**,
qMean≈9), first unsafe rl=350 (ρ=0.964, qMean≈345).

> **WITHDRAWN 2026-08-19:** "ρ* = 0.92 to 3 s.f. across a 30% capacity drop".
> In achieved units ρ* is **0.909 (C0)** vs **0.916 (C1)** — a spread of roughly
> **one transition width**. Correct statement: **ρ\* is approximately 0.91 at
> 7–10 servers, with a C0/C1 spread comparable to the transition width; the
> invariance is qualitative, not to three significant figures.** The ~290
> prediction still landed within one grid step.

**Second time a claimed invariance has proved to be an artefact of resolution or
bias** — the first was transition-width invariance (grid-limited; downgraded to
an upper bound). Carry this into how Phase 2 results are stated: **do not claim
invariance at a precision finer than the measurement bias plus the grid step.**
Report achieved units and the bias budget alongside any invariance claim. **Absolute critical occupancy is
not invariant** (C0 last-safe qMean≈2.2 / IF≈6.6 vs C1 ≈9.0 / 12.7): concurrency
scales with C×S, so fewer servers at the same ρ hold a longer queue. A fixed
occupancy setpoint therefore fails across regimes (q≤2 too conservative at C=1400;
q≤9 past the cliff at C=2000). ρ itself needs C_d to compute. **Online capacity
estimation is required** — the v2.1 novelty claim holds; this is not SlowFast
CoDel with different units. Phase 3 design direction (do not build yet): estimate
ρ from achieved throughput (≈ C_d when queue non-empty) plus offered rate.
See `results/PHASE1B-cliff-C1.md`. C1 fine grid + H3/H4: see
`results/PHASE1B-C1-fine-H3H4.md`. Fine finding: last safe still ρ=0.921 (rl=290);
rl=300 (ρ=0.929) already collapsed (vSLO≈0.84) — **no C0-like marginal band**.
Absolute margin shrinks with C. H3 (rl=840@C1): vSLO≈0.80, G_norm≈0.14.
H4 (rl=290@C0): vSLO=0 but tDrain≈414 vs optimum 146 (~2.8× slower).

### Phase 3 rationale — probing must fail; estimate C_d (from §3b)

Empirically grounded (do **not** build a controller yet):

1. Safe boundary at invariant ρ* ≈ 0.92.
2. Latency gives almost no gradient approaching it under C0 (p99 flat ~8–11 ms
   across hundreds of rps).
3. Under reduced capacity (C1) there is **no marginal band** — at ρ≈0.929,
   C0 is barely cracked (vSLO=0.006, qMean=18) while C1 is collapsed
   (vSLO=0.844, qMean=331).
4. Therefore any probing controller must overshoot into collapse — no "close"
   signal before "too late".
5. Viable strategy: estimate Ĉ_d and set `R = ρ* × Ĉ_d − λ_L`, not probe toward
   the boundary.

Phase 2 sharp prediction: **B3 (latency-feedback AIMD) should oscillate across
the boundary under C1** — probe into collapse, back off, repeat. Settling instead
needs explaining. Absolute margin shrinks with C (~30 rps @2000 → ~10–14 @1400)
with least warning right after a capacity drop. Wrong-high (H3) destroys live
traffic; wrong-low (H4) only wastes drain time (~2.8×) — operators are pushed
to conservatism. H3's "fast" 152 s drain is thrashing, not useful throughput.

Verifications A (live-only @C=1400) and B (S=25 ms / 50-server concurrency) run
before C2/C3 — B can force re-baseline if the sharp cliff is a low-concurrency
artefact.

### Verification A findings (live-only)

C=1400: configured capacity is real (achieved ≈1340 at offered 1350). C_SLO,live
= **1300** → ρ*_live = **0.929**. Matches C1 last-safe total ≈1290. Occupancy
anomaly vs C0 is not a capacity shortfall; bistability remains a candidate.

> **REVERSED 2026-08-19.** The later claim that live-only ρ* is **not** invariant
> (0.929 @ C=1400 vs 0.950 @ C=2000) **does not survive**. The C=2000 value of
> 1900 was an **ascending-sweep reading sitting on the unstable branch**: it
> passed only marginally (p99 = 246 against a 250 ms SLO, frac = 0.996), and a
> descending sweep arriving from a collapsed 1950 puts the same offered rate at
> p99 = **3311**, frac = **0.179**. The robust last-safe — passing from both
> directions — is **1850**.
>
> With 1850, ρ*_live = **0.925 nominal / 0.910 achieved** at C=2000 versus
> **0.929 / ~0.92** at C=1400. **Live-only ρ\* is invariant to within the
> measurement bias at both capacities.** The "not the same to 3 s.f."
> conclusion rested entirely on the unstable-branch value. See the hysteresis
> section.

**Two-class arrival removes the marginal band** (paper-worthy): at C=1400,
ρ=0.929 live-only passes (p99=122, qMean=80.8) while the same total with
injector+rate-limited recovery collapses (vSLO=0.844, qMean=331). Burstiness of
the composed arrival — not aggregate rate — destroys the soft landing. Single-
class benchmarks would invent a marginal band that the workload of interest
lacks. Strengthens §2: probing fails under the two-class process.

**vSLO hides degraded-but-passing:** at offered 1300 / C=1400, p50 6→63 ms and
qMean→80.8 while sloOK stays true (p99=122 < 250). Add **p50** to Phase 2
frontier metrics. Do not change SLO now; record vSLO's blind zone. Controllers
optimising only vSLO can sit 10× above baseline latency indefinitely.

Extend C=2000 live-only to 1700–1950 to test whether ρ*_live ≈ 0.929 is
invariant (expected knee ≈1858) and compare qMean at equal ρ under live-only.

### Verification B — S=25 ms / 50 servers (outcome 2)

Full grid rl∈{600…900}×2: **all vSLO=0 through ρ=0.95** (rl=900). Under S=5 the
same rl=900 collapsed (vSLO≈0.79, qMean≈459). **Cliff softens materially** —
S=5 / 7–10 servers is an artificially hard knee. The §2 claim that probing
*must* overshoot does **not** survive at realistic concurrency and should be
**withdrawn rather than qualified** pending where the 50-server cliff (if any)
sits. ρ*≈0.92 from C0/C1 was two samples in a narrow concurrency band (7–10);
at 50 servers ρ* is demonstrably higher — **ρ* is concurrency-dependent**.
Proposed direction (not decided): concurrency as a first-class dimension
(10 / 50 / 100 servers). Extend S=25 to rl∈{925…990} before any re-baseline.
See `results/PHASE1B-verifB-s25.md`.

### Decision — concurrency is a first-class dimension (two levels)

**Levels:** 10 servers (S=5 ms, pooled-DB archetype) and 50 servers (S=25 ms,
HTTP/slow-backend archetype). Add 100 only if two-level result is ambiguous.
Do **not** discard 10-server results — they are one arm of a two-arm design.

**Finding:** as concurrency rises, ρ* → 1 and the transition softens (10: ρ*≈0.92
sharp / no warning; 50: ρ*≈0.988 graded / p50+qMean lead). Matches standard
queueing; novelty is the recovery-control consequence.

**Mechanism claim (conditional; absolute form withdrawn):** at low concurrency
the boundary is sharp with no latency gradient → probing overshoots → capacity
estimation required; at high concurrency a graded transition exists →
latency-feedback can track it. Match the controller to the dependency.

**Phase 2 / Gate 2 prediction (register now):** B3 (latency AIMD) should
**approximate RHC at 50 servers and fail badly at 10.** All three outcomes
(reproduces / B3 works at 10 / B3 fails at both) are informative.

**Next:** re-test two-class burstiness at 50 servers (live-only vs recovery at
same total offered), then C1 at 50 servers (predict ρ*≈0.988 → safe rl≈383 at
C=1400, noting C drop also cuts concurrency 50→35 so ρ* may shift down). Then
C2/C3 at both levels. H3/H4 at 50 still needed.

### Concurrency effects

Three separate findings from the two-arm campaign (c10 ≈ 7–10 servers, c50 ≈
35–50 servers). Do not collapse into a single “concurrency changes ρ*” story.

| # | Effect | Status | Summary |
|---|---|---|---|
| **1** | **ρ* rises with concurrency** | **Established** (values corrected 2026-08-19) | ≈**0.91** at 7–10 servers, ≈**0.979** at 35 — *achieved* units. Nominal figures (0.92 / 0.986–0.988) overstate utilisation by 0.005–0.011. The c10/c50 gap is ~0.07, an order of magnitude above the bias, so the concurrency-dependence is unaffected |
| **2** | **Transition width narrow in ρ** | **Provisional** | ≤ 0.007 at every condition measured so far; equals one grid step everywhere — unresolved, grid-limited. Ultra-fine C1 @ 50 (rl 382–388) pending |
| **3** | **Severity past boundary falls with concurrency** | **Established** | Same one-step overshoot past ρ*: vSLO **0.03–0.07** at 50 fault-window servers (C0 @ 50) vs **0.758** at 35 servers (C1 @ 50). Holds only for small overshoot near ρ*; at ρ ≫ 1 concurrency gives no protection — H3 @50 vSLO 0.820 / G_norm 0.118 vs @10 0.795 / 0.140, i.e. ~15% apart on both metrics across a 5× concurrency difference (G_norm corrected 2026-08-19, see below) |

**Implication of (3):** a capacity step is a **double penalty** — it lowers ρ*
slightly *and* reduces concurrency (50→35), making any overshoot substantially
more damaging. This is the case RHC exists for; now quantified.

**Transition width (honest claim):** do not claim width invariance. State upper
bound only: transition from vSLO = 0 to material violation occurs within
Δρ ≤ 0.007 everywhere measured; true width may be far narrower.

**Marginal band:** absence/presence tracks fault-window concurrency (35 vs 50
servers), not the capacity step per se.

**H3/H4 @ 50 (done):** prediction **not confirmed** for H3 — vSLO **0.820** vs
@10 **0.795** (slightly worse); G_norm **0.118 vs 0.140**. H3 fault window is C1
(35 servers), not nominal 50. H4: tD≈412 unchanged; vSLO **0**; G_norm **0.997**
vs 0.999 @10 — wrong-low is arm-invariant.
Report: `results/PHASE1B-H3H4-s50.md`.

**Correction 2026-08-19 (two errors in the c50 H3/H4 report, run records were
correct):**
1. `G_norm` for both c50 rows used divisor **1996 = 2 × G_ceil** instead of 998,
   halving them (0.059→**0.118**, 0.498→**0.997**). Divisor solved from the
   published values lies in [1995.2, 1999.2], excluding 2000, the probe's
   `C_SLO_live` 1990, and its max achieved 1983.5. **No report generator exists**
   — no code computes `G_norm`/`G_ceil` and none was deleted; both tables were
   hand-typed. Now generated by `scripts/report_metrics.py` with `G_ceil` passed
   explicitly, never derived from a sweep maximum.
2. H4 @50's vSLO 0.008 was **two host stalls**, not live damage — see host-stall
   detector below. Corrected to 0.

The G_norm error changed a stated conclusion: the "2.4× goodput deficit at 50
servers" does not exist. H3's two arms sit ~15% apart on both vSLO and G_norm,
which is a cleaner statement of "no protection at ρ ≫ 1" than the original.

**Pending:** C2/C3 @ 10 only (reclamation / suspension). Do not start Phase 2.

### Two-class check at 50 servers

Live-only vs recovery at totals 1900/1950/1975/1990: **no catastrophic
two-class collapse** — two-class vSLO 0.029 at 50 servers vs 0.844 at 10.

> **CORRECTED 2026-08-19.** The two sides were paired at equal *nominal* offered,
> but the consumer limiter under-delivers more than the injector, so the
> two-class side sat at **lower achieved ρ at every row** (by 0.007–0.015, i.e.
> 1–2× the transition width). Recomputed at matched achieved ρ the penalty is
> **4.4× occupancy at ρ≈0.973** and **~87× at ρ≈0.977** — substantially
> **larger** than reported, not smaller.
>
> **Withdrawn:** "paths match through ρ=0.975" (never compared at equal ρ) and
> "Verif-A effect was **largely** a low-concurrency artefact" (overstated).
>
> **Corrected statement:** the two-class penalty **persists at 50 servers and is
> large**; what does not reproduce at 50 servers is the *catastrophic collapse*
> seen at 10. The two-path architecture justification therefore **holds at both
> concurrencies** — a stronger result than the claim it replaces.

See `results/PHASE1B-twoclass-s25.md`.

### C1 @ S=25 (35 servers at fault)

rl grid 280–480×2: last safe **rl=380 (ρ=0.986, q≈12)**; first unsafe **rl=430
(ρ=1.021, vSLO≈0.86)** — but 430 is ρ>1 (trivially unsafe). **Fine sweep needed:**
rl∈{390,395,400} to locate cliff in (0.986, 1.0]. Prediction rl≈383 validated
within 1%. Hold "sharp step" claim until fine sweep; graded p50/q rise through 380
is real. Report: `results/PHASE1B-cliff-C1-s25.md`.

**Arm guard:** runner `-arm c10|c50` asserts downstream S/concurrency before
start; records `downstreamServiceTimeMs` + `downstreamConcurrency`. Audit:
`results/PHASE1B-arm-audit.json`.

**Scope:** C2/C3 at **10 servers only**. H3/H4 @ 50 still needed — **prediction:**
wrong-high penalty smaller at 50 (graded transition). Register before run.

**C1 @50 fine (rl 390–400):** last safe **rl=380 (ρ=0.986)**; first damage
**rl=390 (ρ=0.993, vSLO≈0.76)**. **Do not claim Δρ invariance** — measured width
= one grid step everywhere; upper bound Δρ ≤ 0.007. **Severity scales with
concurrency:** C0@50 one step past ρ* → vSLO 0.03–0.07; C1@50 (35 servers) →
0.76. Capacity step = double penalty (ρ* + concurrency). Ultra-fine 382–388 next.
Report: `results/PHASE1B-cliff-C1-s25-fine.md`.

**H3/H4 @50 prediction (register before run):** wrong-high penalty **smaller
than @10** — same overshoot at 50 servers gave vSLO 0.03–0.07 vs 0.76 at 35;
expect H3@50 well below H3@10's 0.795.

**Phase 2 prediction:** B3 ≈ RHC at 50 servers, fails badly at 10.

Ops: disable host sleep for remaining campaign — suspended host silently
corrupts timing windows (false `zero_live` on 350-r3).

### Host-stall detector + sustained-rate integrity check (2026-08-19)

Sub-second stalls of the **measurement host** survive `caffeinate` and are not
downstream behaviour. Signature: live and recovery p99 spike **together** in one
second while downstream `queued` is **0** and the request stream itself shows an
inter-sample gap far above the λ_L inter-arrival time. The system under test was
idle.

Detector (criteria fixed in advance, runner flags `-stall-*`):
- live **and** recovery 1s p99 each ≥ **5×** rolling 30 s healthy baseline
- downstream `queued` ≤ **5**
- max inter-sample gap > **150 ms**

All three required. `queued≈0` is what separates a stall from saturation; the
**gap criterion is the load-bearing one** — on re-scan, 10 runs met the two
p99/queued criteria but had gaps of only 4–20 ms (ordinary jitter against a
single-digit-ms baseline) versus 224 ms for a true stall.

Because reported p99 comes from a 5 s trailing window, one stalled second
contaminates the following 5. Flagged seconds are excluded from vSLO
(numerator **and** denominator) and from latency percentiles; run records now
carry `stallSeconds`, `contaminatedSeconds`, `artifactExcludedSamples`, and
`vSLO_raw` (unexcluded). Exclusions are always reported.

**Why this matters more than H4:** one stalled second produced vSLO ≈ 0.01.
Phase 2 controller comparisons near the knee may differ by that much, so
undetected host stalls would swamp the signal in exactly the regime the paper
depends on. The detector must be live before any Phase 2 run.

**Re-scan of all 165 existing records** (`scripts/rescan_stalls.py`, stage 1 =
timeline criteria, stage 2 = gap criterion against raw jsonl): signature present
in **2 runs only** — `p1b-h4-s50-rl290-r1/r2`, vSLO 0.0094/0.0070 → **0**. No
other Phase 1 vSLO needs footnoting. `p1a-c0-rl855-r2`'s vSLO 0.0127 is **real**
(gaps 5 ms), so the PHASE1A marginal-band finding stands.

**New integrity check — `sustained_live_rate_deviation`:** injector issue rate
below **90%** of λ_L for ≥ **2** consecutive seconds marks the run INVALID. The
existing zero-rate checks need a full 3 s stall; the dip cluster at t=266–274 in
`p1b-h4-s50-rl290-r1` (trough **517 rps** against 1000) passed every prior check.
Note the timeline `liveRps` column reads ≈0.8× truth (5 s trailing window over
completed samples with flush lag) — the check uses the injector issue counter,
not that column.

**Raw data was decisive again.** Both the G_norm correction and the host-stall
finding required per-request jsonl; summaries alone were insufficient. This is
the second such case (the Phase 0 live-population correction was the first).
Worth a line in the paper's methods section on data retention.

### Consumer sample TS (fix before §3b C1)

Recovery samples previously stamped `TS` **before** the shared rate-limiter wait.
A Fetch burst of N workers shared one timestamp, then fell out of the runner's 5s
RPS window together → false `zero_recovery_traffic_during_drain` at low rl (e.g.
C1 rl=150). Fix: stamp TS at post-limiter request start; flush samples every 500ms.

### `p0b-pilot-arch2` abort (note)

Warmup ran injector **and** NATS consumer at λ_L simultaneously → ~2×λ_L on
capacity C → pre-outage unhealthy (p99≈1.8s). Aborted rather than salvaged;
warmup is now injector-only.

### Stabilize window W

Protocol: W fixed from observed downstream settling. Pilot measured queue
259→0 in ~1s and latency ~1.5s→10ms in ~5s. **W = 15 s = 3× settling.**
Previous W=30 dominated T_full as a near-constant offset. Every run records
`stabilizeSeconds=15` and also `tFullSecW30` for sensitivity.

### Memoryless downstream (T_drain ≈ T_full)

The synthetic downstream has no persistent state. Once offered load drops below
capacity, the queue drains and latency returns immediately — residual gap after
removing NATS-live was ~5s settling + W. **Do not add artificial hysteresis.**
`T_drain` vs `T_full` is properly testable only on a stateful dependency
(PostgreSQL validation phase). T_full ≈ T_drain + W is the expected result here.

## NATS host ports

Use `nats://127.0.0.1:14222` (monitor `:18222`). Leave other stacks on `:4222` alone.

## Spec correction: T_drain uses recoveryRemaining, not JetStream pending

`totalPending` never cleanly hits 0 while the producer keeps publishing.
Drain metric:

    recoveryRemaining(t) = backlogAtRestore − recoveryMessagesAcked(t)
    T_drain = first t where recoveryRemaining(t) = 0

Both `totalPending` and `recoveryRemaining` are recorded each second.

**Producer stops at restore.** JetStream then carries recovery-only work;
live load is the injector through `T_full`. (Earlier note forbidding producer
stop is superseded — that assumed injector absence.)

Integrity:
- live RPS zero ≥3s while `recoveryRemaining > 0` → `zero_live_traffic_during_recovery`
- recovery RPS zero ≥3s while rem≥max(100,1% backlog) and live flowing →
  `zero_recovery_traffic_during_drain` (end-of-drain rem=1 false positives on
  p0b-v2-r2/r3 retained as `*.invalid-enddrain.*`; hung rem=1 retry as
  `*.hung-rem1.*`. Fix: stop producer before epoch; T_drain also when
  pending=0 with rem≤5 for 2s.
- injector issue rate zero any second before `T_full` → `zero_injector_rate_before_tfull`

## Preflight results (2026-08-13 evening)

### Check 1 — sampling stall — PASS
Producer kept running. 300s outage build + 300s drain.
- max recovery gap 0.091s; max live gap 0.09s
- recovery continuous 282s concurrent with live
- 429 count = 0

### Check 2 — no blocking I/O in locks — PASS (after injector buffer fix)
Consumer `sampleMu`: only buffer copy under lock; Write/Sync outside.
Injector `bufMu`/`mu`: only in-memory append; file Write on flush ticker outside lock.

### Check 3 — injector — PASS
- `/noop` ceiling ≈ **8000 rps** (tracks through 8k; collapses at 10k)
- `maxInFlight=4096`; peak occupancy in Check1 = 1166
- 429 rate = 0; avg live ≈ 996 vs target 1000
- peak combined offered ≈ 2117; 2× = 4234 < ceiling 8000 (OK)

### Check 4 — headroom — PASS
A/B/C/D @1000 start; P0-D allows negative; P0-B@1400 refuses.

### Check 5 — records — PASS
Fields present: liveRatePerSec, headroomSchedule, maxInFlight,
sloErrorAccounting, gitCommit/gitDirty, recoveryRemaining timeline.

## Analysis A/B from Check 1 (campaign planning)

### A — Gate 0 item 3 (Check 1 concurrent window, 282 s)

Check 1 had no pre-outage live samples (consumer off during outage build).
**Baseline = post-drain live-only (~27 s)**; **Drain = concurrent window**.

| | Baseline (post-drain) | Drain (concurrent) |
|---|---|---|
| Live p50 / p95 / p99 | 625 / 1684 / 1930 ms | 735 / 1733 / 1939 ms |
| Live error rate (excl 429) | 8.8% | 11.2% |
| Soft queueCap | 500 | 500 |
| Est. wait-implied depth (p99) | ~3850 | ~3868 |

`recoveryRemaining` did **not** quite reach 0 in 300 s: acked 296835 / 300000.
Mean recovery drain rate ≈ **1053 msg/s** (≈ full headroom of 1000).

Campaign timeouts (outage 120 s → backlog ≈ 120 k), scaled by headroom:

| Cond | Headroom | Est T_drain | Runner timeout budget |
|---|---|---|---|
| P0-A | 1000 | ~114 s | 2700 s global (OK) |
| P0-B | 400 | ~285 s | OK |
| P0-C | 300 | ~380 s | OK |
| P0-D | neg then 1000 | grows then ~200 s | OK |

### B — Offered-rate ceiling (closed-loop recovery)

Check 1 used **WORKERS=1024** (not 64). Observed peak combined ≈ 2117 rps.

Decomposition:
- Live injector is **open-loop** at λ_L=1000 (peakInFlight 1166)
- Recovery consumer is **closed-loop**: ≈ WORKERS / latency  
  mean drain latency ≈ 842 ms → 1024/0.842 ≈ **1216 rps** recovery
- Sum ≈ 1000 + 1216 ≈ 2216 ≈ observed 2117

So recovery cannot force large throughput amplification past capacity; harm is via
**queue occupancy + latency** on live. M4 amplification (~1.06× vs C=2000) is
real but secondary to live p99 / queue. Do **not** raise WORKERS to inflate M4.

Provisioning rationale for WORKERS=1024 (recorded, not tuned for aesthetics):
enough in-flight to fill graceful soft queue (≤500) and still press the
downstream under multi-hundred-ms latency; exceeds Little’s-law servers at
nominal (C×S=10).



Stopped `p0b-003` mid-run. Retained under `results/` with
`invalidReason=spec_parameter_defect_zero_headroom`.
`p0a-002` marked `superseded_parameter_change`. C/D not started.

Corrected λ_L: 1400 → **1000**. P0-D fault capacity: **900**.

### §4a live/recovery concurrency (`p0b-003`)

Confirmed concurrent for **127 contiguous seconds** after restore (t=0..126):

| Metric | Value |
|---|---|
| avg live attempt RPS | ~1389 |
| avg recovery attempt RPS | ~1310 |
| ratio live:recovery | ~1.06 |
| JetStream pending | ~166k → ~158k (slow growth after cap drop) |

After t≈126s recovery samples stopped while live continued (consumer JSONL
`f.Sync()` held `sampleMu` and stalled workers). Fixed: Sync outside lock.

### §4b ~70% error rate

| Source | Count share (post-restore live) |
|---|---|
| **429 client drop** (injector maxInFlight) | **~50%** |
| 504 timeout | ~2.5% |
| 503 rejected | **0%** |
| `/admin/stats` rejected | **0** |
| `/admin/stats` timedOut | 89545 (vs served 1.8M) |

Graceful profile OK (no 503s). Inflated error rate was mostly injector 429s —
excluded from SLO accounting; maxInFlight raised to 512.

