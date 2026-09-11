# Gate 1 prep probes

**Date:** 2026-08-14  
**Do not start Phase 1 until reviewed.**

---

## 0. Queue-depth censoring

At C=2000, S=5 ms → concurrency=10 → **`queueCap = 10 × 50 = 500`** (graceful).

Soft `queued` increments only when a job enters the channel. Under graceful
admission, if `softLen() ≥ queueCap`, the handler **waits outside the queue**
until a slot frees or `TIMEOUT_MS` (504). Those waiters are **not** in `queued`.

**Verdict:** `qPeak` ≈ 505–508 in Gate 0 is the soft-cap ceiling. Waiting can
still grow as blocked admitters / latency. Queue depth is **censored** like p99
at the 2 s timeout. Memo §5’s 0.3% qPeak spread is an artefact — demote `qPeak`
as a frontier axis; prefer timeout rate, goodput, mid-latency, or mean queue
*while below cap*.

---

## 1. Probe 1 — Live-only SLO capacity curve

Injector only, C=2000 fixed, no recovery / consumer idle. 30 s warmup + 60 s
measure per point. Data: `results/probe1-live-only.json`.

| offered | achieved | p50 | p90 | p95 | p99 | frac≤250 | goodput | timeout | qMean | qPeak | SLO OK |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 250 | 249.7 | 6 | 8 | 8 | 9 | 1.000 | 249.7 | 0 | 0.2 | 1 | ✓ |
| 500 | 499.2 | 6 | 7 | 8 | 9 | 1.000 | 499.2 | 0 | 0.1 | 1 | ✓ |
| 750 | 748.8 | 5 | 7 | 7 | 8 | 1.000 | 748.8 | 0 | 0.1 | 1 | ✓ |
| 900 | 899.3 | 6 | 7 | 7 | 8 | 1.000 | 899.3 | 0 | 0.1 | 1 | ✓ |
| **1000** | **998.0** | **5** | **7** | **7** | **8** | **1.000** | **998.0** | **0** | 0.1 | 6 | ✓ |
| 1200 | 1199.1 | 5 | 6 | 7 | 7 | 1.000 | 1199.1 | 0 | 0.1 | 1 | ✓ |
| 1400 | 1399.0 | 5 | 6 | 6 | 7 | 1.000 | 1399.0 | 0 | 0.1 | 1 | ✓ |
| 1600 | 1598.9 | 5 | 6 | 6 | 7 | 1.000 | 1598.9 | 0 | 0.1 | 1 | ✓ |

### Explicit answers

- **`C_SLO,live` ≥ 1600 rps** (every point in the sweep met p99 ≤ 250 ms and
  error ≤ 1%; knee not reached within the sweep — true ceiling is between 1600
  and C=2000, likely near capacity).
- **λ_L = 1000 is below `C_SLO,live`.** Live-alone is SLO-safe with large margin.
  Phase 0 is testing “recovery steals headroom,” not an already-overloaded live path.
- **`G_SLO,live-only` @ 987 ≈ 985 rps** (interp 900→1000); at offered 1000,
  goodput = **998 rps**. Use **~985–998** as the normalisation ceiling.

Operating point λ_L=1000 is **not** misconfigured on the live-only premise.

---

## 2. Probe 2 — Near-knee resolution (P0-A + static recovery limit)

λ_L=1000, C=2000, outage 120 s, W=15. Recovery capped at 300 / 600 / 900 rps
→ total offered ≈ 1300 / 1600 / 1900 (65% / 80% / 95% of C).  
Data: `results/probe2-near-knee.json`. Rate limiter worked (no `p0b-rate-200`-style stall).

| rl | ≈util | tDrain | tFull | vSLO | p50 | p90 | p95 | p99 | frac≤250 | goodput | timeout | qMean | qPeak |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **300** | 65% | 402 | 416 | **0.000** | **5** | 6 | 7 | **8** | **1.000** | **998** | 0 | 0.3 | **67** |
| **600** | 80% | 202 | 216 | **0.000** | **5** | 6 | 7 | **7** | **1.000** | **998** | 0 | 0.0 | **5** |
| **900** | 95% | 136 | 150 | **0.793** | **301** | 432 | 490 | **625** | **0.140** | **140** | 0 | 459 | **501** |
| unrestricted (P0-A v2 mean) | ~100%+ | 124 | 139 | 0.892 | 769 | — | 1772 | **1956** | 0.014 | 14 | 0.142 | 493 | **507** |

### Explicit answers

**Where do p99 / vSLO stop being censored?**

- At **300 and 600**: fully uncensored — p99 ≈ 7–8 ms (≪ 2 s), queue ≪ soft cap,
  vSLO = 0.
- At **900**: p99 = **625 ms** is below the 2 s timeout (not timeout-censored) but
  queue sits on the soft cap (501). Mid-saturation / near-knee.
- Unrestricted: p99 timeout-censored (~2 s), queue cap-censored (~507).

**Do p99 and vSLO discriminate between the three rates?**

- **300 vs 600:** No — both perfect (vSLO=0, p99≈8). Drain time does (402 vs 202).
- **300/600 vs 900:** Yes, strongly — vSLO 0 → 0.79; p99 8 → 625.
- **900 vs unrestricted:** Yes — p99 625 → 1956; vSLO 0.79 → 0.89; goodput 140 → 14.

**Supplementary: better, or also?**

- **Also**, in the regime that matters (near/below knee): frac, goodput, p50/p90,
  qMean move with the same pattern as p99/vSLO between {300,600} and 900.
- **Better** only for **300 vs 600**, where latency/SLO metrics are saturated at
  “healthy”: **tDrain** (and recovery duration) separates them; p99/vSLO cannot.
- Timeout rate stayed 0 for all three limited runs — does not help here (unlike
  unrestricted Gate 0 where it ranked #1).

### Correction to memo §5

The claim *“if Phases 2–3 keep only p99 and vSLO, adaptive vs RHC may not
separate”* was inferred from **deep unrestricted saturation**. That is the
baseline controllers avoid. Near the knee (this probe), **p99 and vSLO have
good resolution** and track controller aggressiveness. Do **not** discard them.
Keep supplementary metrics for (a) deep saturation comparisons and (b) fine
separation among healthy policies where p99 is floored at service time.

---

## 3. Implications for Gate 1 (for review — not executed)

| Topic | Recommendation from probes |
|---|---|
| Operating point λ_L=1000 @ C=2000 | **Keep** — live-only is SLO-safe with margin (`C_SLO,live` ≥ 1600). |
| W=15 | Keep (already calibrated). |
| Frontier axes | **Keep p99 + vSLO** for near-knee controller comparison; add **goodput** (normalise to `G_SLO,live-only` ≈ 985–998) and **timeout rate** for saturated baselines; **tDrain** for healthy-vs-healthy; **demote qPeak**. |
| Phase 2 matrix | Prefer points that land near the knee (like rl≈900 / ~95% util), not only unrestricted deep saturation. |

Static limiter path is healthy again under producer-stop architecture — deferred
sweep can reuse it when scheduled.
