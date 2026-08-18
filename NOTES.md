# Phase 0 Notes

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
| Secondary safety | G_norm = G_policy / 985 |
| Saturated-regime | timeout rate |
| Healthy-vs-healthy | tDrain |
| Demoted | qPeak (soft-cap censored); p99 demoted in saturation |
| T_full | reported, not a frontier axis on this downstream |

Phase 1 = static sweeps only (no controllers). §3a cliff under C0: **done**
(`results/PHASE1A-cliff-C0.md`) — coarse max safe rl=825, cliff by 900.
Fine sweep + occupancy analysis: `results/PHASE1A-followups.md` — max safe
rl=840; marginal 855; collapsed by 870 (width 30 rps). G_ceil=998.
§3b not started.

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

Under C1 (C_d=1400): last safe rl=290 (ρ=0.921, qMean≈9), first unsafe rl=350
(ρ=0.964, qMean≈345). **ρ* = 0.92 to 3 s.f. across a 30% capacity drop** — strong
invariance; the ~290 prediction landed exactly. **Absolute critical occupancy is
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
| **1** | **ρ* rises with concurrency** | **Established** | ≈0.92 at 7–10 servers; ≈0.986–0.988 at 35–50 |
| **2** | **Transition width narrow in ρ** | **Provisional** | ≤ 0.007 at every condition measured so far; equals one grid step everywhere — unresolved, grid-limited. Ultra-fine C1 @ 50 (rl 382–388) pending |
| **3** | **Severity past boundary falls with concurrency** | **Established** | Same one-step overshoot past ρ*: vSLO **0.03–0.07** at 50 fault-window servers (C0 @ 50) vs **0.758** at 35 servers (C1 @ 50) |

**Implication of (3):** a capacity step is a **double penalty** — it lowers ρ*
slightly *and* reduces concurrency (50→35), making any overshoot substantially
more damaging. This is the case RHC exists for; now quantified.

**Transition width (honest claim):** do not claim width invariance. State upper
bound only: transition from vSLO = 0 to material violation occurs within
Δρ ≤ 0.007 everywhere measured; true width may be far narrower.

**Marginal band:** absence/presence tracks fault-window concurrency (35 vs 50
servers), not the capacity step per se.

**H3/H4 @ 50 (done):** prediction **not confirmed** for H3 — vSLO **0.820** vs
@10 **0.795** (slightly worse); G_norm 0.059 vs 0.14. H3 fault window is C1
(35 servers), not nominal 50. H4: tD≈412 unchanged; vSLO≈0.008; G_norm≈0.50 vs
1.00 @10. Report: `results/PHASE1B-H3H4-s50.md`.

**Pending:** C2/C3 @ 10 only (reclamation / suspension). Do not start Phase 2.

### Two-class check at 50 servers

Live-only vs recovery at totals 1900/1950/1975/1990: **no catastrophic
two-class collapse**. Paths match through ρ=0.975; mild edge penalty only near
ρ→1 (q 2–5× at 0.988–0.995). Verif-A effect was largely a **low-concurrency
artefact**. Architecture justification must be concurrency-conditional.
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

