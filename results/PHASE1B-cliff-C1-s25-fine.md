# C1 @ 50 servers — fine cliff (rl ∈ {390, 395, 400})

**Fault window:** C_d = 1400 → **35 servers** (S = 25 ms)  
**Data:** `p1b-c1-s25-fine-rl*-r*.json` (+ coarse anchors 380, 430)  
**Arm:** `-arm c50` verified (dsS=25, dsC=50) on all runs.

---

## Fine grid + anchors

| rl | ρ (fault) | vSLO (mean) | p50 | p99 | qMean |
|---:|---:|---:|---:|---:|---:|
| **380** | **0.986** | **0.000** | 32 | 56 | **11.6** |
| **390** | **0.993** | **0.758** | 672 | 1394 | **912** |
| 395 | 0.996 | 0.827 | 1235 | 1728 | 1252 |
| 400 | 1.000 | 0.838 | 1298 | 1813 | 1341 |
| 430 | 1.021 | 0.861 | 1338 | 1920 | 1505 |

---

## Cliff located (ρ space)

| | C1 @ 50 | C0 @ 50 |
|---|---|---|
| Last all-safe ρ | **0.986** (rl=380) | **0.988** (rl=975) |
| First material damage ρ | **0.993** (rl=390) | **0.995** (rl=990) |
| Measured Δρ | **0.007** (one 10 rps grid step) | **0.007** (one 15 rps step) |

**Do not claim transition-width invariance.** In all four conditions measured,
the reported Δρ equals exactly one grid step — signature of an unresolved
quantity. Honest claim: *transition from vSLO=0 to material violation occurs
within Δρ ≤ 0.007 everywhere*. Ultra-fine at C1 @ 50 (rl 382–388) will tighten
this bound.

---

## Prediction/observation (coarse C1)

| | Predicted | Observed |
|---|---|---|
| Safe rl (ρ*≈0.988) | ≈ 383 | **380** |
| Safe ρ | 0.988 | **0.986** |

Pre-registered prediction confirmed to ~1%.

---

## Severity scales with concurrency (new finding)

One step past ρ* at ~50-server regime, **same Δρ**, very different damage:

| | Fault-window servers | vSLO one step past ρ* |
|---|---|---|
| C0 @ 50 | 50 | **0.03–0.07** (thin marginal) |
| C1 @ 50 | 35 | **0.758** (collapse) |

Three concurrency effects (not one):

1. **ρ* rises with concurrency** — ~0.92 at 7–10 servers, ~0.987 at 35–50  
2. **Transition width narrow everywhere** — ≤ 0.007 in ρ (upper bound)  
3. **Severity past boundary falls with concurrency** — 35-server queue collapses
   harder than 50-server at equal overshoot  

A capacity step is a **double penalty**: ρ* drops slightly **and** concurrency
falls (50→35), amplifying overshoot cost. RHC exists for this case.

---

## Marginal band

"No marginal band at C1 @ 50" tracks **fault-window concurrency** (35 vs 50
servers), not the capacity step alone. Phrase accordingly.

**Next:** ultra-fine rl ∈ {382, 384, 386, 388}; then H3/H4 @ 50.
