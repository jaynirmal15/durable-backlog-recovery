# Phase 1 §3b — C1 at 50-server arm (S = 25 ms)

**Regime:** C1 = P0-B, C → 1400 at t = 20 s → **35 servers** during fault (⌈1400×0.025⌉)  
**Sweep:** rl ∈ {280, 330, 380, 430, 480} × **2** (+ prior 280×2) — **10/10 valid**  
**Prediction (before run):** if ρ*=0.988 unchanged → safe rl ≈ **383**; expect ≤383 if ρ* falls with concurrency drop (50→35).

---

## Per-rate means (drain)

| rl | total | ρ (fault) | tDrain | vSLO | p50 | p99 | qMean |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 280 | 1280 | 0.914 | 429 | **0.000** | 25 | 34 | 0.1 |
| 330 | 1330 | 0.950 | 365 | **0.000** | 26 | 35 | 0.3 |
| **380** | **1380** | **0.986** | **317** | **0.000** | **32** | **56** | **11.6** |
| **430** | **1430** | **1.021** | **283** | **0.861** | **1338** | **1920** | **1505** |
| 480 | 1480 | 1.057 | 254 | 0.862 | 1340 | 1950 | 1537 |

---

## Cliff (four forms)

| Form | Last safe | First unsafe |
|---|---|---|
| **1. Absolute rl** | **380** | **430** |
| **2. Total offered** | **1380** | **1430** |
| **3. ρ (fault, C_d=1400)** | **0.986** | **1.021** |
| **4. qMean / p50 at edge** | q≈12, p50≈32 | q≈1505, p50≈1338 |

Transition: **50 rps** (380→430), **sharp collapse** (vSLO 0 → 0.86), not a thin marginal band at this concurrency during C1.

---

## Prediction vs observed

| | Predicted (ρ*=0.988) | Observed |
|---|---|---|
| Safe rl | ≈ 383 | **380** (within grid) |
| Safe ρ | 0.988 | **0.986** |

**ρ* is near the C0@50 prediction at C=1400** — capacity scaling of total offered (~1380 vs ~1975 at C=2000) tracks concurrency-dependent ρ*, not a fixed absolute rl. The capacity step also cuts concurrency (50→35), which should push ρ* down; observed safe ρ=0.986 is slightly **below** C0@50 (0.988), consistent with that.

Compare C1 @ **10 servers** (prior): last safe rl=290, ρ=0.921. Same C_d, **much lower safe rl** at low concurrency — same qualitative pattern as C0.

---

## Carry-forward

- ρ* is **concurrency-dependent** and **roughly tracks** when stated in ρ at the fault-window server count.
- C1 @ 50 servers: **graded approach** through 380 (p50/q rise, vSLO=0) then **sharp** step at 430 — unlike C1@10's 290→300 one-step collapse at lower ρ.
- C2/C3 at both levels still pending. H3/H4 @ 50 still needed. Downstream should be restored to S=5 for 10-server arm reproducibility when idle.
