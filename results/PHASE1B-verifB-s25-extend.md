# Verification B extension — ρ* at 50 servers (S = 25 ms)

**Hold re-baseline / C2/C3** pending concurrency-dimension decision.  
Downstream restored to S=5 ms.  
**Data:** `results/PHASE1B-verifB-s25-extend.json` (+ prior `PHASE1B-verifB-s25.json` grid through rl=900).

---

## Full S=25 grid (means; extend rates bold)

| rl | ρ | tDrain | vSLO | p50 | p99 | goodput | qMean | mean IF |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 600–925 | 0.80–0.96 | — | **0** | ~25–26 | ~34–44 | ~995+ | ≪1 | ~26 |
| 950 | 0.975 | 128 | **0.000** | 26 | 35 | 995 | 1.1 | 26 |
| **975** | **0.988** | **126** | **0.000** | **28** | **44** | **994** | **6.9** | **29** |
| **990** | **0.995** | **124** | **0.050** | **136** | **244** | **990** | **209** | **130** |

Per-run at the edge:
- 975-r1/r2: vSLO=0, p50=29/28, p99=46/41, qMean=7.3/6.5  
- 990-r1: vSLO=**0.029**, p50=120, p99=245, qMean=201  
- 990-r2: vSLO=**0.071**, p50=153, p99=244, qMean=216  

---

## Cliff location at 50 servers

| Quantity | Value |
|---|---|
| Last rate with **all** runs vSLO = 0 | **rl = 975** (ρ = **0.988**) |
| First rate with any vSLO > 0 | **rl = 990** (ρ = **0.995**) |
| Marginal band (vSLO ∈ (0, 0.05]) | **Yes — 990-r1** (0.029); mean across 2 runs ≈ 0.050 |
| First mean vSLO > 0.05 | Not cleanly crossed on this grid (mean ≈ 0.050 at 990) |
| Collapse like S=5 @ ρ=0.95 | **Absent** — no deep vSLO≈0.8 regime through ρ=0.995 |

**ρ* at 50 servers ≈ 0.988–0.995** (last safe → first crack). Far above the S=5 ρ* ≈ 0.92.

---

## Which outcome?

**ρ* ≈ 0.98 with a graded transition** (user outcome 1).

Evidence:
- Occupancy / p50 rise **before** vSLO: at ρ=0.988, qMean≈7 and p50≈28 while vSLO=0; at ρ=0.995, qMean≈209 and p50≈136 with only thin vSLO.
- p99 at 990 sits just under the 250 ms SLO (~244) — degraded-but-passing / marginal, not thrashing collapse.
- Contrast S=5 at ρ=0.95: vSLO=0.79, qMean=459 in one step past the frontier.

So at high concurrency: **probing / latency-feedback can see a gradient**; the absolute “probing must overshoot” claim does **not** survive. The mechanism argument becomes **conditional on concurrency**, matching the proposed paper framing.

---

## Decision input (not decided here)

| Concurrency | Approx ρ* (recovery, two-class) | Transition |
|---|---|---|
| 10 (S=5) | ≈ **0.92** | Sharp; little/no marginal band under two-class |
| 50 (S=25) | ≈ **0.99** | Graded; p50/qMean lead; thin vSLO at the edge |

Supports making concurrency a **first-class dimension** (10 / 50 / 100) rather than picking one “realistic” point. C2/C3 and full re-baseline stay held until that call.

**What this does not change:** Gate 0 (unrestricted catch-up damages live at ρ≫1); H3/H4 asymmetry (magnitudes will move with concurrency).
