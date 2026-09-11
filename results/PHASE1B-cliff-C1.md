# Phase 1 §3b — C1 cliff (report before C2/C3)

**Regime:** C1 = P0-B, C → 1400 at t = 20 s, λ_L = 1000, W = 15  
**Sweep:** recovery rl ∈ {150, 225, 290, 350, 425} × **3 runs** (15/15 valid after retry)  
**Data:** `results/p1b-c1-rl*-r*.json`, summary `results/PHASE1B-cliff-C1.json`  
**G_ceil** = 998  

Harness note: consumer recovery sample `TS` now stamps post-limiter (pre-fix false `zero_recovery` at rl=150). One 350-r3 abort was host-sleep aging the 5 s window — retried valid.

---

## Per-rate means (drain; fault-window occupancy also shown)

| rl | total | ρ = tot/1400 | tDrain | vSLO | p99 | goodput | G_norm | qMean (drain) | qMean (fault) | mean IF (fault) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 150 | 1150 | 0.821 | 798 | **0.000** | 8 | 998 | 1.00 | 0.18 | 0.18 | 6.0 |
| 225 | 1225 | 0.875 | 534 | **0.000** | 8 | 995 | 1.00 | 0.42 | 0.43 | 6.1 |
| **290** | **1290** | **0.921** | **414** | **0.000** | **33** | 995 | 1.00 | **8.6** | **9.0** | **12.7** |
| **350** | **1350** | **0.964** | **345** | **0.888** | **1593** | 77 | 0.08 | **326** | **345** | **555** |
| 425 | 1425 | 1.018 | 284 | 0.874 | 1884 | 83 | 0.08 | 323 | 346 | 779 |

---

## Four-form cliff location

| Form | Last safe | First unsafe |
|---|---|---|
| **1. Absolute rl** | **290** | **350** |
| **2. Total offered (λ_L + rl)** | **1290** | **1350** |
| **3. ρ = total / C_d (fault)** | **0.921** | **0.964** |
| **4. qMean / mean IF (fault window)** | **qMean ≈ 9.0, IF ≈ 12.7** | **qMean ≈ 345, IF ≈ 555** |

Transition width on this grid: **60 rps** (290 → 350). No intermediate rate between them.

Predicted safe rl if ρ* ≈ 0.92 was ~290 — **hit exactly** as the last safe grid point.

---

## Invariance vs C0 — direct answer

| | C0 (frontier) | C1 (this sweep) | Match? |
|---|---|---|---|
| **ρ* (last safe)** | ≈ 0.92 (1840/2000 at rl=840) | **0.921** (1290/1400 at rl=290) | **Yes** |
| **qMean at last safe** | ≈ **1–2** (fine: 2.2 at 840) | ≈ **9** | **No** |
| **mean IF at last safe** | ≈ 6.6 | ≈ 12.7 | **No** |
| **Collapse occupancy** | qMean ~320 at rl=870 | qMean ~345 at rl=350 | Same regime of collapse |

**Headline:** critical **utilisation ρ* ≈ 0.92 is invariant** under the C0→C1 capacity step. Critical **occupancy level is not** — at the same ρ*, C1’s last-safe queue sits ~4–9× higher than C0’s.

### What that means for Phase 3

- A controller that only holds a **C0-calibrated occupancy setpoint** (qMean ≈ 1–2) would be **over-conservative under C1** (would back off while still safe), or if raised to C1’s qMean ≈ 9 would be **past C0’s comfortable frontier**.
- Because **ρ* matches**, a controller that tracks **utilisation** (or an occupancy signal **normalised by capacity / service rate**) can land near the right absolute rate without a separate C_d estimator *if* it can form ρ. Pure absolute queue-setpoint control is **not** sufficient across regimes.
- Novelty framing: still closer to “headroom / utilisation awareness” than to a capacity-blind AQM setpoint. Do **not** collapse the story to SlowFast-CoDel-style occupancy-only control on the strength of C1 alone.
- Instantaneous C→1400 still throws a C0-tuned rl=840 to ρ = 1840/1400 ≈ **1.31** in one step — **reaction time** remains the dominant Phase 3 requirement (H3 row deferred to after C2/C3).

**C2/C3 not started** — awaiting review of this C1 invariance result.
