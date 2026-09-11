> **SUPERSEDED (2026-08-14).** Architecture corrected: producer now stops at
> restore; injector runs through `T_full`. The post-drain gap reported below was
> dominated by NATS-live secondary backlog (`nats_live_contamination_post_drain`).
> All 12 runs invalidated; re-run pending pilot. Retain this file for the
> empirical HOL evidence (NATS-live 20–37 rps) and population-correction method.

# Gate 0 Memo — Unrestricted JetStream Catch-up vs Live Safety

**Campaign:** formal P0-A…D × 3, λ_L=1000, C=2000, outage=120s, WORKERS=1024, graceful.  
**Date:** 2026-08-14  
**Live SLO population (corrected):** `injector_direct` — direct HTTP injector only.  
**Artifacts:** `results/p0{a,b,c,d}-r{1,2,3}.json`, `results/GATE0-live-population-correction.*`, `NOTES.md` (architecture).

Static-rate sweep (`p0b-rate-*`) is **out of scope** for this memo (rate-200 killed; remaining rates not run).

---

## 1. Methods — how concurrent live/recovery is achieved

JetStream pull delivery is ordered. Post-restore publishes sit behind the outage
backlog, so a NATS-only consumer cannot load the downstream with true live work
at the same time as recovery.

**Harness design:** during drain the runner open-loop injects HTTP at λ_L to
`/process` (injector-live). The consumer drains JetStream: pre-epoch → recovery,
post-epoch → NATS-live. Diagram and Q&A: `NOTES.md` § “Live / recovery concurrency architecture”.

| Population | Definition (post-restore) | Role |
|---|---|---|
| Injector-live | `class=live`, `age_ms==0` | **Live SLO** — newly arriving work |
| NATS-live | `class=live`, `age_ms>0` | Reported separately (ordered catch-up artefact) |
| Recovery | `class=recovery` | Outage backlog |

Original runner timelines blended injector + NATS into one `live*` series (and
double-counted injector in memory via jsonl tail). **All safety numbers below
use offline recomputation from retained JSONL, injector-live only.**  
Drain-window injector mean RPS is **985–988** across all 12 runs (tracks λ_L=1000).

---

## 2. Verdict (Gate 0 questions)

| # | Question | Answer |
|---|---|---|
| 1 | Does unrestricted catch-up damage live? | **Yes.** Injector-live p99 during drain is ~2.1–2.2 s (SLO 250 ms); error rates 10–29%. |
| 2 | Does mid-drain capacity change matter? | **Yes.** P0-B (C→1400) has the longest `T_full−T_drain` gap (~320–340 s) and highest timeout rate (~12%). |
| 3 | Is `T_drain = T_full`? | **No.** Every condition shows a large post-drain saturation tail; P0-B largest. |
| 4 | Amplification / offered rate | Secondary. Peak offered ~2.1× vs C; harm is queue + latency, not huge throughput amp. |
| 5 | Static rate sweep | **Deferred** (instrumentation / sample-path issues under rate limit). |

**Gate 0 recommendation:** proceed to controlled recovery (Phase 1+). Unrestricted
catch-up is unsafe for live SLO under these parameters.

---

## 3. Population split (representative drain windows)

Injector and NATS p99 are similar during drain because both compete for the same
saturated downstream. They are **not** the same population: NATS-live mean RPS
is only ~20–37 while injector holds ~987 — almost no post-epoch JetStream work
reaches the downstream until recovery clears.

### P0-A / p0a-r1 (drain)

| Population | count | mean rps | p50 | p95 | p99 | error rate |
|---|---:|---:|---:|---:|---:|---:|
| Injector-live | 113565 | 987.5 | 800 | 2003 | 2167 | 0.105 |
| NATS-live | 4258 | 37.0 | 780 | 2001 | 2152 | 0.077 |
| Recovery | 119214 | 1036.6 | 800 | 2003 | 2176 | 0.106 |

### P0-B / p0b-r1 (drain)

| Population | count | mean rps | p50 | p95 | p99 | error rate |
|---|---:|---:|---:|---:|---:|---:|
| Injector-live | 143158 | 987.2 | 1192 | 2027 | 2210 | 0.276 |
| NATS-live | 2979 | 20.5 | 1227 | 2037 | 2207 | 0.263 |
| Recovery | 118539 | 817.4 | 1160 | 2022 | 2206 | 0.265 |

### P0-C / p0c-r1 · P0-D / p0d-r1

| Run | Inj rps | Inj p99 | Inj err | NATS rps | NATS p99 | Rec rps | Rec p99 |
|---|---:|---:|---:|---:|---:|---:|---:|
| p0c-r1 | 985.0 | 2178 | 0.169 | 33.0 | 2188 | 969.0 | 2181 |
| p0d-r1 | 988.4 | 2191 | 0.291 | 23.6 | 2164 | 870.2 | 2185 |

Blended live p99 in the original records is therefore **not interpretable as a
single arrival class**, even though its magnitude happened to track injector p99
under saturation. Corrected records set `liveSLOPopulation: "injector_direct"`.

---

## 4. Old vs corrected (all 12 runs)

| runId | tDrain | tFull | gap | old peak liveRps | **inj mean Rps** | old peak live p99 | **inj p99** | old vSLO | **new vSLO** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| p0a-r1 | 115 | 249 | 134 | 1499 | **987.5** | 1974 | **2167** | 0.875 | **0.879** |
| p0a-r2 | 115 | 252 | 137 | 1496 | **988.2** | 1965 | **2168** | 0.877 | **0.880** |
| p0a-r3 | 113 | 251 | 138 | 1375 | **985.7** | 1991 | **2166** | 0.876 | **0.880** |
| p0b-r1 | 145 | 468 | **323** | 1484 | **987.2** | 1993 | **2210** | 0.934 | **0.936** |
| p0b-r2 | 145 | 475 | **330** | 1153 | **985.2** | 2021 | **2211** | 0.935 | **0.937** |
| p0b-r3 | 143 | 482 | **339** | 1482 | **985.5** | 2058 | **2204** | 0.936 | **0.938** |
| p0c-r1 | 123 | 269 | 146 | 1371 | **985.0** | 1986 | **2178** | 0.885 | **0.888** |
| p0c-r2 | 123 | 271 | 148 | 1513 | **986.9** | 1989 | **2176** | 0.889 | **0.889** |
| p0c-r3 | 123 | 266 | 143 | 1511 | **987.2** | 1989 | **2180** | 0.887 | **0.887** |
| p0d-r1 | 137 | 296 | 159 | 1525 | **988.4** | 1999 | **2191** | 0.899 | **0.899** |
| p0d-r2 | 137 | 299 | 162 | 1493 | **988.2** | 1993 | **2190** | 0.896 | **0.899** |
| p0d-r3 | 139 | 300 | 161 | 1492 | **986.1** | 2006 | **2192** | 0.900 | **0.900** |

- Corrected live rate tracks λ_L → **double-count / blend diagnosis confirmed**.
- V_SLO barely moves: downstream was already past the 250 ms SLO for most of
  the run on injector alone.
- Injector drain counts match `injectorCompleted` within ~1%.

Stall audit (separate): no run has ≥3 s of `recoveryRps=0` while
`recoveryRemaining>0` and `liveRps>0`. Main campaign stands on that check.

---

## 5. `T_drain ≠ T_full` — especially P0-B

After recovery clears, the injector stops. The downstream then faces the
JetStream live backlog (producer continued at λ_L during drain). Soft queue
stays pinned near cap; live p99 stays ~2 s; then queue depth falls to 0 and
latency collapses to ~7 ms. The runner’s 30 s stabilize window accounts for
only ~33 s of every gap.

| Condition | tDrain | post-drain saturation (queue>0) | stabilize tail | tFull−tDrain |
|---|---:|---:|---:|---:|
| P0-A (r1) | 115 s | ~101 s | ~33 s | ~134 s |
| **P0-B (r1)** | **145 s** | **~290 s** | **~33 s** | **~323 s** |
| P0-C (r1) | 123 s | ~113 s | ~33 s | ~146 s |
| P0-D (r1) | 137 s | ~126 s | ~33 s | ~159 s |

P0-B (reduced headroom to 400 at t=20) is the predicted direction: backlog
clears in <2.5 min, but the system needs another ~5 min before live is healthy.
**This is real system recovery, not a stabilize-logic artefact.**

P0-B gap detail (p0b-r1): queued mean ~313 (max 355) until ~t=435; timeouts
continue at ~3% of gap work; NATS-live p99 ~2.0–2.2 s until the cliff at
~t=439, then p99≈7 ms and 30 s healthy → `T_full=468`.

---

## 6. Downstream timeout rates (timeline ΔtimedOut / (Δserved+ΔtimedOut))

| Condition | Timeout rate (3-run range) |
|---|---|
| P0-A | 5.3–5.5% |
| **P0-B** | **11.4–12.2%** |
| P0-C | 7.9–8.1% |
| P0-D | 13.1–13.2% |

Sustained timeouts confirm the downstream spent a large fraction of each run
saturated — context for injector-live p99 ≫ 250 ms. (Killed sweep rate-200 had
~7.3% timeouts on a longer saturated window; same qualitative regime.)

---

## 7. Integrity / process notes

- `zero_live_traffic_during_recovery` and `zero_recovery_traffic_during_drain`
  (≥3 s) are enforced in the runner going forward.
- Sweep item 5 blocked on sample-path / rate-limit observability; do not mix
  into this memo.
- Superseded / invalid exploratory runs retained but excluded: `p0a-001`,
  `p0a-002`, `p0b-002`, `p0b-003`, `p0b-rate-200`.

---

## 8. Bottom line

Unrestricted recovery **does** harm live traffic under Gate 0 parameters.
Corrected injector-live metrics remove the blended-population ambiguity and
still show clear SLO violation for the entire drain in every condition.
`T_drain ≪ T_full`, maximally so under P0-B reduced headroom — the protocol’s
central distinction holds and is strongest where predicted.
