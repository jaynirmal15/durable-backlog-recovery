# Phase 1 §3a follow-ups (before §3b)

**Date:** 2026-08-14  
**§3b not started.**

---

## 1. Leading indicator — rl=825 occupancy time series

### Cross-rate (from coarse sweep) — still true

| rl | p99 | qMean | mean liveInFlight (drain) |
|---:|---:|---:|---:|
| 600–750 | 8 | ~0.1–0.2 | — |
| **825** | **11** | **~1.0** | **~6.2** |
| 900 | 547 | ~459 | ~292 |

Latency is flat; queue mean steps ~5× at the last safe coarse point.

### Within-run at rl=825 — flat, not drifting

Across all three drains (~148 s), occupancy does **not** ramp toward the cliff:

| run | queued thirds (early→mid→late) | inflight thirds | queued mean / peak | peak IF |
|---|---|---|---|---|
| r1 | 0.46 → 0.90 → 0.96 | 6.1 → 6.2 → 6.3 | 0.76 / 8 | 11 |
| r2 | 1.25 → 2.16 → 1.20 | 6.2 → 6.7 → 6.3 | 1.52 / 28 | 22 |
| r3 | 0.69 → 0.69 → 0.86 | 6.1 → 6.1 → 6.0 | 0.74 / 9 | 13 |

**Verdict:** qMean≈1 at 825 is a **steady elevated occupancy**, not an accumulating early-warning that grows during the drain. A controller that only watches within-run drift of queue/latency would still see a flat signal. The useful signal is **level vs a calibrated baseline** (e.g. qMean ≪ 1 vs ≈1 vs ≫10), not slope during a single drain.

### rl=825 vs rl=900 occupancy / time-in-queue proxy

| | rl=825 (3-run) | rl=900 (3-run) |
|---|---|---|
| qMean | 0.7–1.5 | 456–462 |
| qPeak | 8–28 | 501 (cap) |
| mean liveInFlight | ~6 | ~292 |
| peak liveInFlight | 11–22 | 345–357 |
| injector peakInFlight (params) | 24–34 | 357–367 |
| p50 latency (≈ wait+5ms) | 6 ms → wait ≈1 ms | 289–293 ms → wait ≈285 ms |
| p99 latency | 9–14 ms → wait ≈4–9 ms | 535–568 ms → wait ≈530–563 ms |

Time-in-queue is not a separate instrumented field; injector latency minus ~5 ms service is the wait proxy. At 825, wait is negligible; at 900, wait dominates and the soft queue is pegged at the cap (true waiting continues outside `queued` — see queue-censoring note).

**Phase 3 design input (NOTES):** latency-feedback (B3) sees almost no gradient until collapse; **occupancy level** (queue / in-flight) separates 825 from 600–750 and especially from 900. Prefer level thresholds over within-run latency slope. Do not design a controller yet.

---

## 2. Fine cliff sweep — rl ∈ {840, 855, 870, 885} × 2

Plus coarse 825 / 900 for context. Data: `results/PHASE1A-cliff-C0-fine.json`.

| rl | n | tDrain | vSLO (mean) | p99 | G_norm | qMean | mean IF |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 825 | 3 | 148 | **0.000** | 11 | 0.997 | 1.0 | 6.2 |
| **840** | 2 | 146 | **0.000** | 24 | 1.001 | 2.2 | 6.6 |
| **855** | 2 | 143 | **0.006** | 95 | 1.000 | **18** | **15** |
| **870** | 2 | 141 | **0.354** | 288 | 0.625 | 320 | 178 |
| **885** | 2 | 138 | **0.730** | 424 | 0.210 | 441 | 262 |
| 900 | 3 | 136 | **0.793** | 547 | 0.137 | 459 | 292 |

Per-run detail at the edge:
- 855-r1: vSLO=0.000, p99=26, qMean=5.0  
- 855-r2: vSLO=**0.0127**, p99=164, qMean=**30.5** ← first crack  
- 870-r1/r2: vSLO=0.23 / 0.48 — already deep into damage

### Explicit cliff answers (fine grid)

| Quantity | Value |
|---|---|
| Highest rate with **all** runs vSLO = 0 | **840** |
| Any rate with vSLO ∈ (0, 0.05] | **Yes — rl=855** (mean 0.006; one run 0.013) |
| First rate with mean vSLO > 0.05 | **870** |
| Transition width (vSLO=0 → vSLO>0.05) | **30 rps** (840 → 870) |

**Not a pure step at 15 rps resolution.** There is a thin gradient: 840 safe → 855 marginal (occupancy rising, occasional tiny vSLO) → 870 collapsed. Best achievable tDrain at vSLO=0 on this grid: **146 s at rl=840** (vs 148 s at 825). Gate 2 frontier point under C0: **rl=840, tDrain≈146 s, vSLO=0**.

Occupancy foreshadows better than latency: qMean 1→2→18 across 825→840→855 while p99 only 11→24→95 until 855-r2 spikes.

---

## 3. G_norm fix

- **G_ceil = 998** (Probe 1 live-only goodput at offered 1000).
- Recomputed on Phase 0 v2, Probe 2, Phase 1a coarse + fine (30+ files).
- Phase 1a coarse G_norm now ≤1.0 (e.g. rl=825 mean **0.997**).
- **One exceedance:** `probe2-p0a-rl600` G_norm=**1.0005** (gp=998.47). Not clamped — 0.47 rps above the 60 s Probe 1 mean; longer drain window variance. Documented, not adjusted.

---

## Implications for §3b (still not started)

- C0 frontier is nearly a point: **rl=840** is the practical optimum; faster rates enter a short marginal band then collapse.
- H2 (static limit optimal under stationary C) strengthened: little room to beat rl=840 on tDrain without entering the cliff.
- Leading indicator for Phase 3: **occupancy level**, not latency slope; within-run drift at the safe point is absent.
- §3b should show C0-tuned rl=840 (or 825) overshooting under C1 (predicted safe rl ≈ headroom-scaled).

**Awaiting review before §3b.**
