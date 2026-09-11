# Two-class burstiness at 50 servers (S = 25 ms)

<!-- This file was reconstructed from the 2026-08-19 session log; original was never committed.
     See RECONSTRUCTION.md. -->

**Question:** Does the Verif-A two-class penalty (live-only OK vs recovery collapsed at
same ρ) survive at 50 servers, or was it a low-concurrency artefact?

> **Correction (2026-08-19) — two sub-claims withdrawn.** The two sides were
> paired at equal **nominal** offered, but the consumer rate limiter
> under-delivers more than the injector does (both used a tick-dropping
> `time.Ticker`), so the two-class side sat at systematically **lower achieved
> ρ** — by up to 2× the transition width. See §Correction. The headline verdict
> survives; "indistinguishable through ρ=0.975" does not.

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

## Correction — pairing was at nominal, not achieved, offered

| nominal total | live-only ρ_ach | two-class ρ_ach | Δ (two − live) | live-only qMean | two-class qMean |
|---:|---:|---:|---:|---:|---:|
| 1900 | 0.9477 | 0.9403 | −0.0074 | 0.3 | 0.3 |
| 1950 | 0.9688 | 0.9620 | −0.0067 | 1.1 | 1.2 |
| 1975 | 0.9854 | 0.9728 | **−0.0126** | 3.4 | **7.3** |
| 1990 | 0.9918 | 0.9772 | **−0.0146** | 39.7 | **201.1** |

The two-class side was advantaged at every row, by 1×–2× the stated transition
width (0.007). Interpolating live-only to matched achieved ρ:

- at ρ ≈ 0.973: live-only q ≈ 1.7 vs two-class **7.3** → **4.4×**
- at ρ ≈ 0.977: live-only q ≈ 2.3 vs two-class **201** → **~87×**

**Survives:** the headline verdict. Two-class vSLO at 50 servers is 0.029 vs
0.844 at 10 servers — the catastrophic collapse does not reproduce.

**Withdrawn:**
1. "through ρ=0.975 the two paths are **indistinguishable**" — they were never
   compared at the same ρ. At matched achieved ρ the two-class side is already
   4.4× on occupancy at ρ ≈ 0.973.
2. "Verif-A effect was **largely** a low-concurrency artefact" — overstated. The
   effect is weaker at 50 servers than at 10, but substantially larger than this
   report concluded.

The ρ column in the table above (0.950 / 0.975 / 0.988 / 0.995) is **nominal**
and overstates true utilisation by 0.005–0.015. Do not cite it without the
achieved value. Root cause and per-generator shortfall: `NOTES.md`,
"Load-generator pacing defect".

---

## Next (prediction stated)

**C1 at S=25:** C→1400 at t=20 → concurrency = ⌈1400×0.025⌉ = **35** (not 50).
If ρ* stayed 0.988: safe total ≈ 1383 → **safe rl ≈ 383**.
But capacity drop also cuts concurrency (50→35), which should **push ρ* down** —
expect safe rl ≤ 383. Grid will bracket that.
