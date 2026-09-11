# Phase 1 §3b — C1 fine transition + H3/H4

**Date:** 2026-08-17  
**Before C2/C3.** Data: `results/PHASE1B-C1-fine-H3H4.json`, per-run `p1b-c1-fine-*`, `p1b-h3-*`, `p1b-h4-*`.  
**G_ceil** = 998. Host sleep disabled (`caffeinate`) for these runs.

---

## 1. C1 fine transition — rl ∈ {300, 310, 320, 330} × 2

Anchors from coarse grid included. Fault-window occupancy (C_d = 1400).

| rl | ρ | n | tDrain | vSLO | p99 | goodput | qMean (fault) | mean IF |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **290** | **0.921** | 3 | 414 | **0.000** | 33 | 995 | **9.0** | **12.7** |
| **300** | **0.929** | 2 | 403 | **0.844** | 400 | 150 | **331** | **274** |
| 310 | 0.936 | 2 | 390 | 0.870 | 487 | 104 | 339 | 301 |
| 320 | 0.943 | 2 | 378 | 0.883 | 677 | 88 | 341 | 341 |
| 330 | 0.950 | 2 | 366 | 0.888 | 1185 | 80 | 343 | 439 |
| 350 | 0.964 | 3 | 345 | 0.888 | 1593 | 77 | 345 | 555 |

### Is transition width invariant in ρ-space?

| | C0 | C1 (fine) |
|---|---|---|
| Last all-runs vSLO = 0 | rl=840, **ρ = 0.920** | rl=290, **ρ = 0.921** |
| First crack / collapse | rl=855, ρ=0.928 (vSLO≈0.006 marginal) | rl=300, **ρ = 0.929** (vSLO≈0.84 — already collapsed) |
| First mean vSLO > 0.05 | rl=870, ρ=0.935 | rl=300, ρ=0.929 |
| Δρ (last safe → first damage) | ≈ **0.008–0.015** with a thin marginal band | ≈ **0.008** but **no marginal band** — one 10 rps step jumps to vSLO≈0.84 |

**ρ* last-safe is still invariant (0.920–0.921).** The *shape* of the transition is **not**: C0 had a usable marginal band (855); C1 has none at 10 rps resolution — **300 is already deep collapse**.

Absolute control margin at the cliff:
- C0: Δρ ≈ 0.015 → **~30 rps** of room  
- C1: Δρ ≈ 0.008 (290→300) with no soft landing → **~10–14 rps**, and the first step past ρ* is catastrophic  

**The absolute margin shrinks as capacity falls**, and under C1 the cliff is sharper in outcome space even when Δρ looks similar. That is the hard control problem: least room to manoeuvre exactly when capacity has just dropped.

Occupancy trajectory: at ρ=0.921, qMean≈9 (safe); at ρ=0.929, qMean≈331 (collapsed). Same discontinuous occupancy jump as C0’s 2→18→320 path, but compressed into a single 10 rps step here.

---

## 2. H3 / H4 — motivating table

| Hyp | Policy | Regime | ρ | tDrain | vSLO | goodput | G_norm | timeout | p99 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| **H3** | C0-tuned rl=**840** | **C1** (C→1400) | **1.31** | 152 | **0.795** | 140 | **0.14** | **0.23** | 1960 |
| **H4** | C1-tuned rl=**290** | **C0** (C=2000) | 0.645 | **414** | **0.000** | 997 | **1.00** | 0 | 7 |
| *(ref)* | C0 optimum rl=840 | C0 | 0.920 | **146** | 0 | ~999 | ~1.00 | 0 | 24 |
| *(ref)* | C1 safe rl=290 | C1 | 0.921 | 414 | 0 | 995 | 1.00 | 0 | 33 |

Means over 2 runs each for H3/H4.

**H3:** C0 optimum under C1 destroys live traffic — vSLO≈0.80, G_norm≈0.14, timeout≈23%, p99≈2 s. Drain is “fast” (152 s) only because the system is thrashing past capacity.

**H4:** C1-safe rate under C0 is fully healthy (vSLO=0) but **wastes ~268 s** of drain vs C0 optimum (414 vs 146) — about **2.8× slower**.

Asymmetric cost: wrong-high (H3) harms live SLO; wrong-low (H4) only burns recovery time. Static policies cannot be right for both regimes.

---

## 3. Carry-forward (before C2/C3)

- ρ* ≈ 0.92 invariant; absolute occupancy not; online C_d estimation still required (NOTES).
- C1 transition: no C0-like marginal band at 10 rps — cliff is sharp; absolute margin shrinks with C.
- H3/H4 table is the paper’s static-policy motivation.
- Predict C2/C3 safe rl from ρ*=0.92 before running; report predicted vs observed.

**C2/C3 not started.**
