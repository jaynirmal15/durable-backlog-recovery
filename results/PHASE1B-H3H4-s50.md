# H3/H4 @ 50 servers (c50)

**Date:** 2026-08-18  
**Arm:** `-arm c50` verified (dsS=25, dsC=50) on all runs.  
**Data:** `p1b-h3-s50-rl840-r*.json`, `p1b-h4-s50-rl290-r*.json`

---

## Pre-registered prediction

Wrong-high penalty (H3) should be **materially smaller than @10**, since severity
past the boundary falls with concurrency. H3 @ 10 gave vSLO **0.795**, G_norm
**0.14** — expect H3 @ 50 **well below** 0.795.

---

## Results (2 runs each)

| Hyp | Policy | Regime | ρ (fault) | tDrain | vSLO | G_norm | timeout | p99 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| **H3** | C0-tuned rl=**840** | **C1** | **1.31** | **179.5** | **0.820** | **0.059** | **0.14** | **1971** |
| **H4** | C1-tuned rl=**290** | **C0** | 0.645 | **412.0** | **0.008** | **0.498** | ~0 | **35** |

Compare @10 (same hypotheses):

| Hyp | tDrain | vSLO | G_norm |
|---|---:|---:|---:|
| H3 @10 | 152 | **0.795** | **0.14** |
| H4 @10 | 414 | **0.000** | **1.00** |

---

## Prediction vs observation

**H3 — prediction not confirmed.** vSLO @ 50 (**0.820**) is slightly *worse* than
@ 10 (0.795), not well below. G_norm also lower (0.059 vs 0.14). Drain slower
(180 s vs 152 s).

**Mechanism:** finding (3) applies to **one-step overshoot past ρ\*** at the
boundary. H3 throws rl=840 into C1 — ρ ≈ 1.31, far past any boundary. During
the fault window C_d = 1400 → **35 servers**, same concurrency as C1 @ 50 cliff
tests where vSLO ≈ 0.76 one step past ρ*. The 50-server baseline (C=2000) does
not protect the C1 fault phase.

**H4 — mixed.** tDrain essentially unchanged (412 vs 414 s). vSLO nominally
worse (0.008 vs 0.000 — small live breach during drain). G_norm halved (0.50 vs
1.00): recovery goodput constrained despite low live damage. Wrong-low at 50
servers is still safe on vSLO but **not** equivalent to @10 on throughput.

---

## Carry-forward

- H3 wrong-high penalty is **regime-concurrency during fault**, not nominal arm
  concurrency. Capacity step + high rl = double penalty (quantified in
  concurrency-effects (3)).
- C2/C3 @ 10 only next. Do not start Phase 2.
