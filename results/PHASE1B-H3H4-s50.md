# H3/H4 @ 50 servers (c50)

<!-- This file was reconstructed from the 2026-08-19 session log; original was never committed.
     See RECONSTRUCTION.md. -->

**Date:** 2026-08-18  
**Arm:** `-arm c50` verified (dsS=25, dsC=50) on all runs.  
**Data:** `p1b-h3-s50-rl840-r*.json`, `p1b-h4-s50-rl290-r*.json`

> **Correction (2026-08-19).** The `G_norm` column as first published was wrong
> for both rows, and the H4 `vSLO` was a measurement artifact. Original text and
> values are preserved in §Correction below. Corrected values are used in the
> table and prose. The run records were correct throughout; only this report was
> wrong.

---

## Pre-registered prediction

Wrong-high penalty (H3) should be **materially smaller than @10**, since severity
past the boundary falls with concurrency. H3 @ 10 gave vSLO **0.795**, G_norm
**0.14** — expect H3 @ 50 **well below** 0.795.

---

## Results (2 runs each)

| Hyp | Policy | Regime | ρ (fault) | tDrain | vSLO | G_norm | timeout | p99 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| **H3** | C0-tuned rl=**840** | **C1** | **1.31** | **179.5** | **0.820** | **0.118** | **0.14** | **1971** |
| **H4** | C1-tuned rl=**290** | **C0** | 0.645 | **412.0** | **0.000**† | **0.997** | ~0 | **35** |

† H4's originally reported vSLO of 0.008 was two host stalls, not live-traffic
damage; see §Correction. Under the stall detector both runs give vSLO = 0.

Compare @10 (same hypotheses). **`G_norm` is normalised per arm**: both arms
measure `G_ceil` = 998 (the ceiling at λ_L is injector-limited, not arm-limited
— both dependencies have large headroom at λ_L), so these rows are directly
comparable. See the arm-relative normalisation note in `NOTES.md`.

| Hyp | tDrain | vSLO | G_norm |
|---|---:|---:|---:|
| H3 @10 | 152 | **0.795** | **0.140** |
| H4 @10 | 414 | **0.000** | **0.999** |

---

## Prediction vs observation

**H3 — prediction not confirmed.** vSLO @ 50 (**0.820**) is slightly *worse* than
@ 10 (0.795), not well below. G_norm also slightly lower (**0.118 vs 0.140**).
Drain slower (180 s vs 152 s). The two arms differ by only ~15% on both metrics
despite a 5× concurrency difference — at ρ ≫ 1, concurrency provides no
protection.

**Mechanism:** finding (3) applies to **one-step overshoot past ρ\*** at the
boundary. H3 throws rl=840 into C1 — ρ ≈ 1.31, far past any boundary. During
the fault window C_d = 1400 → **35 servers**, same concurrency as C1 @ 50 cliff
tests where vSLO ≈ 0.76 one step past ρ*. The 50-server baseline (C=2000) does
not protect the C1 fault phase.

**H4 — equivalent to @10.** tDrain essentially unchanged (412 vs 414 s), vSLO 0
in both arms once host stalls are excluded, G_norm **0.997 vs 0.999**. Wrong-low
is as safe and as fast at 50 servers as at 10. There is no throughput penalty;
the apparent one was the divisor error below.

---

## Correction

### 1. `G_norm` divided by 2 × G_ceil

| Row | published | correct | |
|---|---:|---:|---|
| H3 @50 | 0.059 | **0.118** | |
| H4 @50 | 0.498 | **0.997** | |

Both c50 rows used a divisor of **1996 = 2 × 998** instead of `G_ceil` = 998.
Solving for the divisor implied by the published figures gives [1995.2, 1999.2],
which admits 1996 and excludes every other candidate — nominal capacity 2000
(→ 0.497), the c50 live-only probe's `C_SLO_live` 1990 (→ 0.500), and its
maximum achieved rate 1983.5 (→ 0.501). The c10 rows in
`PHASE1B-C1-fine-H3H4.md` used 998 and are correct.

There is no report generator: no code in the repository computes `G_norm` or
`G_ceil`, and none was ever deleted. Both tables were computed by hand and typed
in. `scripts/report_metrics.py` now derives this table from the run records with
`G_ceil` as an explicit argument, so it is no longer hand arithmetic.

### 2. H4 vSLO 0.008 was a host stall, not a live breach

Both H4 @50 runs show, in a single second, live **and** recovery p99 spiking
together (r1 t=269: live p99 34→500 ms, recovery 34→531 ms) while the downstream
queue is at **0** and the request stream itself shows inter-sample gaps of 224 ms
and 203 ms. The dependency was idle; the measurement host paused. The runner's 5 s
trailing window smeared one bad second into four violation-seconds, giving
vSLO 0.0094 (r1) and 0.0070 (r2). r2 shows the same signature at t=339–341.

A detector for this is now in the runner (three criteria, fixed in advance:
both-class p99 spike ≥ 5× rolling baseline, `queued` ≤ 5, inter-sample gap
> 150 ms). Flagged seconds are excluded from vSLO and latency percentiles and
counted in the run record as `stallSeconds` / `contaminatedSeconds`, with
`vSLO_raw` retained unexcluded.

A re-scan of all 165 run records (`scripts/rescan_stalls.py`) found the
signature in **only these two runs**. Ten further runs matched on the two
timeline-visible criteria but were refuted by the gap criterion (max gaps
4–20 ms, versus 224 ms here) — ordinary p99 jitter against a single-digit-ms
baseline. Notably `p1a-c0-rl855-r2`'s vSLO = 0.0127 is **real** (gaps 5 ms), so
the marginal-band finding in `PHASE1A-followups.md` stands.

## Carry-forward

- H3 wrong-high penalty is **regime-concurrency during fault**, not nominal arm
  concurrency. Capacity step + high rl = double penalty (quantified in
  concurrency-effects (3)).
- H4 wrong-low is arm-invariant: same tDrain, same vSLO (0), same G_norm (~1.0)
  at 10 and 50 servers. Conservatism costs the same 2.8× drain time either way.
- C2/C3 @ 10 only next. Do not start Phase 2.
