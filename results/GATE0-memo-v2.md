# Gate 0 Memo (v2) — Corrected Architecture

**Campaign:** `p0{a,b,c,d}-v2-r{1,2,3}` (12/12 valid)  
**Architecture:** producer stops at restore; injector continuous through `T_full`; live SLO = injector-direct  
**W = 15 s** (3× observed ~5 s settling from `p0b-pilot-arch2b`); `tFullSecW30` reported for sensitivity  
**Params:** λ_L=1000, C=2000, outage=120 s, WORKERS=1024, graceful  
**Date:** 2026-08-14  

Supersedes `GATE0-memo.md` (NATS-live contaminated) and the pilot-only note in `GATE0-pilot-arch2b.md`.  
Static-rate sweep still **deferred**.

Invalidated first campaign retained as scoping evidence (`nats_live_contamination_post_drain`), including HOL starvation of NATS-live to 20–37 rps during drain.

---

## 1. Gate 0 answers

| # | Question | Answer (v2 data) |
|---|---|---|
| 1 | Does unrestricted catch-up damage live? | **Yes.** Drain injector p99 ≈ 1.95–1.98 s (SLO 250 ms); fraction under SLO ≈ 1–2%; vSLO ≈ 0.89–0.91. |
| 2 | Does mid-drain capacity change matter? | **Yes, modestly.** P0-B (C→1400) has longest `tDrain` (~151 s vs A ~124 s) and highest drain timeout rate (~29%). p99 remains pinned near the 2 s timeout across all conditions. |
| 3 | Is `T_drain = T_full`? | **≈ yes on this downstream.** Gap ≈ W (14–16 s at W=15; 29–31 s at W=30). No multi-minute post-drain tail. |
| 4 | Amplification | Secondary; harm is latency/timeouts/queue, not huge throughput amp. |
| 5 | Static rate sweep | Deferred. |

**Recommendation:** Gate 0 passes as a go for controlled recovery research. Unrestricted catch-up is unsafe for live SLO. Proceed to Phase 1 with attention to **metric resolution** (§4).

---

## 2. Architecture (methods)

Live and recovery use **independent paths** to a shared downstream (sync API + backlog consumer). That is the setting where recovery admission control can free capacity for live. Where live shares an ordered log with recovery, HOL blocking prevents that — empirically shown in the invalidated campaign (NATS-live 20–37 rps during drain).

| Phase | Producer → JetStream | Injector → downstream |
|---|---|---|
| Warmup / healthy | off | λ_L |
| Outage | on | λ_L |
| Restore → T_full | **stopped** | λ_L continuous |

Producer is stopped **before** backlog/epoch measurement (1 s settle) so in-flight publishes are not misclassified.

---

## 3. `T_drain ≈ T_full` — stated plainly

| Condition | mean tDrain | mean tFull (W=15) | mean gap | mean tFull (W=30) |
|---|---:|---:|---:|---:|
| P0-A | 124 s | 139 s | **15 s** | 154 s |
| P0-B | 151 s | 165 s | **14 s** | 180 s |
| P0-C | 128 s | 144 s | **15 s** | 159 s |
| P0-D | 142 s | 157 s | **15 s** | 172 s |

The invalidated campaign’s ~320 s P0-B gap was **NATS-live secondary backlog**, not outage recovery. After removing that artefact, the residual is **≈ W plus ~0–1 s queue drain**.

### Why the residual is ~W (memoryless model)

The synthetic downstream is **memoryless**. When offered load falls below capacity, the soft queue empties and latency returns to baseline within ~5 s. There is no persistent degradation for a recovery tail to consist of.

Real dependencies are not memoryless (evicted cache, connection-pool churn, lock contention, background maintenance). **`T_drain` vs `T_full` is therefore not meaningfully testable on this downstream**; it belongs to the protocol’s stateful (PostgreSQL) validation phase.

**Do not add artificial hysteresis to the synthetic downstream** to inflate the gap.

W=15 was set from measured settling (3× ~5 s), not to improve aesthetics. Reporting both W=15 and W=30 shows sensitivity: gap tracks W almost exactly.

---

## 4. Per-run primary + supplementary (drain window)

| runId | tDrain | tFull15 | tFull30 | vSLO | p50 | p90 | p95 | p99 | frac≤250ms | goodput | timeout | qPeak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| p0a-v2-r1 | 125 | 140 | 155 | 0.893 | 774 | 1592 | 1776 | 1957 | 0.018 | 17.8 | 0.146 | 507 |
| p0a-v2-r2 | 129 | 145 | 160 | 0.896 | 801 | 1617 | 1794 | 1963 | 0.013 | 12.5 | 0.165 | 506 |
| p0a-v2-r3 | 117 | 132 | 147 | 0.886 | 733 | 1550 | 1746 | 1949 | 0.012 | 12.0 | 0.117 | 507 |
| p0b-v2-r1 | 155 | 169 | 184 | 0.911 | 881 | 1702 | 1850 | 1980 | 0.010 | 9.8 | 0.312 | 505 |
| p0b-v2-r2 | 154 | 168 | 183 | 0.905 | 874 | 1698 | 1845 | 1975 | 0.016 | 15.6 | 0.304 | 506 |
| p0b-v2-r3 | 144 | 158 | 173 | 0.905 | 825 | 1662 | 1823 | 1968 | 0.018 | 17.5 | 0.254 | 508 |
| p0c-v2-r1 | 125 | 141 | 156 | 0.894 | 761 | 1595 | 1780 | 1954 | 0.016 | 16.2 | 0.182 | 505 |
| p0c-v2-r2 | 135 | 150 | 165 | 0.900 | 817 | 1647 | 1820 | 1982 | 0.016 | 14.9 | 0.220 | 505 |
| p0c-v2-r3 | 125 | 140 | 155 | 0.886 | 749 | 1584 | 1769 | 1954 | 0.019 | 18.8 | 0.178 | 506 |
| p0d-v2-r1 | 143 | 158 | 173 | 0.905 | 811 | 1657 | 1824 | 1969 | 0.020 | 20.3 | 0.312 | 507 |
| p0d-v2-r2 | 137 | 152 | 167 | 0.895 | 786 | 1643 | 1809 | 1963 | 0.019 | 18.9 | 0.295 | 508 |
| p0d-v2-r3 | 145 | 160 | 175 | 0.906 | 813 | 1664 | 1826 | 1972 | 0.022 | 22.0 | 0.319 | 505 |
---

## 5. Condition separation — Phase 1 frontier input

**Degenerate / near-degenerate primary metrics**

| Metric | Rel. spread across A–D | Notes |
|---|---:|---|
| live p99 (drain) | **0.9%** | Pinned at ~2 s request timeout |
| vSLO | **1.7%** | 0.89–0.91 everywhere — saturation ceiling |
| gap (tFull−tDrain) | **~W** | Not a condition discriminator on this model |
| qPeak | **0.3%** | Soft-cap saturated (~505–508) in all |

**Metrics that separate conditions** (relative spread of condition means)

| Rank | Metric | A | B | C | D | Rel. spread |
|---|---|---:|---:|---:|---:|---:|
| 1 | **Drain timeout rate** | 0.14 | **0.29** | 0.19 | **0.31** | **0.71** |
| 2 | Fraction under SLO | 0.014 | 0.014 | 0.017 | 0.021 | 0.39 |
| 3 | **Drain goodput** (rps ≤250 ms & 200) | 14.1 | 14.3 | 16.6 | **20.4** | **0.39** |
| 4 | Queue depth mean | **493** | 367 | 448 | 370 | 0.30 |
| 5 | **tDrain** | 124 | **151** | 128 | 142 | **0.20** |
| 6 | live p50 | 769 | **860** | 776 | 803 | 0.11 |

### Interpretation for Phase 1

- **Timeout rate**, **tDrain**, and **goodput** (and secondarily p50 / mean queue) are the candidates for Pareto axes. They move with headroom schedule; p99 and vSLO do not.
- P0-B and P0-D show the worst timeout rates (~29–31%): reduced or temporarily infeasible headroom.
- P0-D’s higher goodput alongside high timeouts reflects the fault window then restore to full C — mixed signal; treat carefully.
- Do **not** change SLO threshold or request timeout in Phase 0; operating-point choice is Phase 1 design informed by this.

If Phases 2–3 keep only p99 and vSLO, adaptive vs RHC may not separate. Prefer frontier axes drawn from the separating supplementary set above.

---

## 6. Process notes

- `p0b-pilot-arch2`: warmup at 2×λ_L — aborted correctly; warmup is injector-only.
- `p0b-v2-r2/r3` first attempts: end-drain `rem=1` false INVALID / hang — retained as `*.invalid-enddrain.*` / `*.hung-rem1.*`; integrity and T_drain completion fixed; retries valid.
- Sweep (Gate 0 item 5): still deferred.

---

## 7. Bottom line

Unrestricted JetStream catch-up **damages injector-live** under Gate 0 parameters. The large `T_full − T_drain` gap from the first campaign was an architecture artefact; on the corrected harness and memoryless downstream, **`T_full ≈ T_drain + W`**. Phase 1 should plan around **timeout rate, goodput, tDrain, and mid-latency (p50/p90)** rather than p99/vSLO alone.
