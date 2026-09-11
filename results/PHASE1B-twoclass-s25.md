# Two-class burstiness at 50 servers (S = 25 ms)

**Question:** Does the Verif-A two-class penalty (live-only OK vs recovery collapsed at
same ρ) survive at 50 servers, or was it a low-concurrency artefact?

**Live-only:** C=2000, S=25, injector only — `results/probe-twoclass-s25-c2000-live-only.json`  
**Two-class:** same totals via λ_L=1000 + rl from Verif B / extend.

---

## Side-by-side at equal total offered

| total | ρ | Live-only SLO / p50 / p99 / qMean | Two-class vSLO / p50 / p99 / qMean | q ratio |
|---:|---:|---|---|---:|
| 1900 | 0.950 | ✓ / 25 / 35 / **0.3** | **0** / 25 / 35 / **0.4** | 1.1× |
| 1950 | 0.975 | ✓ / 25 / 35 / **1.1** | **0** / 26 / 35 / **1.1** | 1.1× |
| 1975 | 0.988 | ✓ / 27 / 36 / **3.4** | **0** / 28 / 44 / **6.9** | 2.0× |
| 1990 | 0.995 | ✓ / 40 / 84 / **40** | **0.050** / 136 / 244 / **209** | 5.3× |

Live-only `C_SLO,live` ≥ **1990** on this grid (every point sloOK).

---

## Verdict

**The catastrophic two-class collapse does not reproduce at 50 servers.**

At 10 servers (Verif A, C=1400, ρ=0.929): live-only passed (qMean 81, frac 0.998)
while two-class collapsed (vSLO 0.844, qMean 331) — ~4× occupancy, 140× vSLO.

At 50 servers, through ρ=0.975 the two paths are **indistinguishable**. A mild
composed-arrival penalty appears only **near ρ→1** (2× q at 0.988; 5× q and thin
vSLO at 0.995), not a binary architecture-justifying cliff.

**Implication for harness framing:** two-path architecture remains useful (live vs
recovery are still distinct workloads), but “composed arrival destroys the
marginal band” is **concurrency-conditional** — strong at pooled/low-c, weak at
high-c. Rewrite architecture justification accordingly; do not claim a
concurrency-invariant two-class effect.

---

## Next (prediction stated)

**C1 at S=25:** C→1400 at t=20 → concurrency = ⌈1400×0.025⌉ = **35** (not 50).
If ρ* stayed 0.988: safe total ≈ 1383 → **safe rl ≈ 383**.
But capacity drop also cuts concurrency (50→35), which should **push ρ* down** —
expect safe rl ≤ 383. Grid will bracket that.
