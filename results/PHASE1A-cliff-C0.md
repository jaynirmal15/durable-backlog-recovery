# Phase 1 §3a — C0 cliff location

**Regime:** C0 stationary, P0-A, C=2000, λ_L=1000, W=15  
**Sweep:** recovery rl ∈ {600, 675, 750, 825, 900} × **3 runs** (15/15 valid)  
**Data:** `results/p1a-c0-rl*-r*.json`, summary `results/PHASE1A-cliff-C0.json`  
**G_ceil** = 985 (Probe 1)

---

## Per-rate means (drain window)

| rl | ≈total | tDrain | vSLO | p50 | p95 | p99 | frac≤250 | goodput | G_norm | timeout | qMean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 600 | 1600 | 202.0 | **0.000** | 5 | 7 | 8 | 1.000 | 994 | 1.01 | 0 | 0.2 |
| 675 | 1675 | 180.0 | **0.000** | 5 | 7 | 8 | 1.000 | 995 | 1.01 | 0 | 0.1 |
| 750 | 1750 | 162.0 | **0.000** | 5 | 7 | 8 | 1.000 | 995 | 1.01 | 0 | 0.2 |
| **825** | **1825** | **148.0** | **0.000** | 6 | 8 | **11** | 1.000 | 995 | 1.01 | 0 | 1.0 |
| **900** | **1900** | **136.0** | **0.793** | 292 | 438 | **547** | 0.137 | 137 | 0.14 | 0 | 459 |

Variance: tDrain sd ≈ 0 across all rates; vSLO at 900: 0.780 / 0.793 / 0.807 (sd 0.013).

---

## Cliff location (explicit)

| Quantity | Value |
|---|---|
| **Max recovery rate with mean vSLO = 0** | **825 rps** |
| **First rate with mean vSLO > 0.05** | **900 rps** |
| **Transition width** | **75 rps** (825 → 900) |

Within the probed grid, health holds through **1825 total offered** (1000+825) and collapses by **1900** (1000+900). The cliff is **sharp**: one 75 rps step takes vSLO from 0 → ~0.79 and goodput from ~995 → ~137 (G_norm 1.01 → 0.14). No intermediate vSLO in (0, 0.05] appears on this grid — the jump clears 0.05 in a single step.

Safe-vs-Probe-2: rl=600 still perfect; rl=900 matches Probe 2 (vSLO≈0.79). The new finding is that **825 is still fully safe** — ~27 s faster drain than 600 with no live damage.

---

## Implications (for §3b review — not started)

- Under C0, static policies can sit at **rl ≤ 825** without live SLO violations; **900 is already on the wrong side of the cliff**.
- RHC must estimate a boundary in a **~75 rps** band under this stationary regime — narrow, but not a single point.
- §3b (C1/C2/C3) should bracket each regime’s own cliff; under C→1400 expect the safe rl ceiling to fall roughly with headroom.

**§3b not started** — awaiting review of this cliff location.
