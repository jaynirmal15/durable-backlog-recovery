# E1 — four boundaries on the fixed harness

**Data only. No interpretation, no memo.** Located under `PRE-REGISTRATION.md`
(`371e477`) with amendments A1 (`e5bf303`), A2 (`1fe9de3`), A3 (`699e105`,
`25583c7`, `99eda6d`, `1bd09d3`) and A4 (`d5ea89d`, `ddd428d`).

## Conditions

| | |
|---|---|
| Machine | EC2 `c6i.2xlarge`, `i-099dca965768db94a`, us-east-1 |
| CPU / memory | Intel Xeon Platinum 8375C, 8 vCPU, 15.3 GiB |
| OS / kernel | Ubuntu 24.04, Linux 7.0.0-1012-aws |
| Go / Docker | go1.25.3 / 29.1.3 |
| Harness commit | `026be6242d26` — **all 66 runs, no exceptions** |
| Queue cap | 500, `profile_relative` (default), full-queue delay 250 ms |
| Service-time jitter | σ = 0.15 |
| Injector pacer | `lanes` (A3) |
| Recovery limiter | `time.Ticker`, unchanged (A3) |
| Repetitions | n = 3 per probed point |

## The four boundaries

Achieved ρ under **A4** — recovery measured over the span it occupied, not
`backlog / tDrain`. Interval is [last SAFE, first NON-SAFE] per A1.

| boundary | rl interval | endpoint | ρ* interval (A4) | width | probes | runs |
|---|---|---|---|---:|---:|---:|
| **c10 / C0** | [825, 830] | UNSAFE | **[0.9124, 0.9150]** | 0.0026 | 6 | 18 |
| **c10 / C1** | [275, 280] | UNSAFE | **[0.9107, 0.9143]** | 0.0036 | 4 | 12 |
| **c50 / C0** | [975, 980] | UNSAFE | **[0.9817, 0.9835]** | 0.0018 | 7 | 21 |
| **c50 / C1** | [370, 375] | UNSAFE | **[0.9786, 0.9822]** | 0.0036 | 5 | 15 |

All four reached the 5 rps resolution floor. **No point classified MARGINAL**
anywhere in E1. Every upper endpoint is UNSAFE.

## Every probed point

### c10 / C0 — anchor 840, C_d = 2000

| rl | class | vSLO per rep | ρ (A4) per rep | drain tail (s) |
|---:|---|---|---|---|
| 755 | SAFE | 0.0000, 0.0000, 0.0000 | 0.8775, 0.8774, 0.8775 | 1.5–2.1 |
| 800 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9000, 0.9000, 0.9000 | 1.9–6.6 |
| 820 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9100, 0.9100, 0.9100 | 1.7–2.5 |
| **825** | **SAFE** | 0.0000, 0.0000, 0.0000 | 0.9124, 0.9124, 0.9124 | 2.1–2.4 |
| **830** | **UNSAFE** | 0.0769, 0.0000, 0.1355 | 0.9149, 0.9150, 0.9149 | 1.8–1.9 |
| 840 | UNSAFE | 0.6474, 0.7070, 0.6792 | 0.9196, 0.9196, 0.9196 | 2.5–6.5 |

Probe order: 840 (anchor, UNSAFE) → 755 → 800 → 820 → 830 → 825.

### c10 / C1 — anchor 290, C_d = 1400

| rl | class | vSLO per rep | ρ (A4) per rep | drain tail (s) |
|---:|---|---|---|---|
| 260 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9000, 0.9000, 0.9000 | 1.8–2.3 |
| **275** | **SAFE** | 0.0000, 0.0000, 0.0000 | 0.9107, 0.9107, 0.9107 | 1.6–1.9 |
| **280** | **UNSAFE** | 0.6300, 0.4941, 0.7336 | 0.9143, 0.9143, 0.9143 | 2.6–3.5 |
| 290 | UNSAFE | 0.8446, 0.8472, 0.8544 | 0.9214, 0.9214, 0.9214 | 3.8–4.1 |

Probe order: 290 (anchor, UNSAFE) → 260 → 275 → 280.

### c50 / C0 — anchor 990, C_d = 2000

| rl | class | vSLO per rep | ρ (A4) per rep | drain tail (s) |
|---:|---|---|---|---|
| 890 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9449, 0.9450, 0.9449 | 1.7–2.3 |
| 940 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9695, 0.9695, 0.9694 | 1.6–2.1 |
| 965 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9780, 0.9782, 0.9782 | 1.5–2.1 |
| 970 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9800, 0.9800, 0.9797 | 1.7–2.2 |
| **975** | **SAFE** | 0.0000, 0.0000, 0.0000 | 0.9817, 0.9820, 0.9821 | 1.7–2.2 |
| **980** | **UNSAFE** | 0.2500, 0.1022, 0.2667 | 0.9835, 0.9833, 0.9834 | 2.0–2.7 |
| 990 | UNSAFE | 0.6014, 0.5985, 0.5474 | 0.9858, 0.9859, 0.9862 | 2.1–6.4 |

Probe order: 990 (anchor, UNSAFE) → 890 → 940 → 965 → 975 → 980 → 970.

### c50 / C1 — anchor 380, C_d = 1400

| rl | class | vSLO per rep | ρ (A4) per rep | drain tail (s) |
|---:|---|---|---|---|
| 340 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9571, 0.9571, 0.9571 | 2.1–2.4 |
| 360 | SAFE | 0.0000, 0.0000, 0.0000 | 0.9714, 0.9715, 0.9714 | 1.7–2.5 |
| **370** | **SAFE** | 0.0000, 0.0000, 0.0000 | 0.9786, 0.9786, 0.9786 | 1.6–6.5 |
| **375** | **UNSAFE** | 0.0966, 0.2972, 0.2356 | 0.9821, 0.9821, 0.9822 | 2.1–2.8 |
| 380 | UNSAFE | 0.6500, 0.7375, 0.7671 | 0.9857, 0.9857, 0.9856 | 3.0–3.3 |

Probe order: 380 (anchor, UNSAFE) → 340 → 360 → 375 → 370.

## Campaign

| | |
|---|---|
| Total runs | **66** |
| Probed points | 22 |
| Wall clock | **8.99 h** (17:44:37Z 2026-09-11 → 02:43:58Z 2026-09-12) |
| Discarded runs | **none** |
| Runs marked invalid | **0** |
| Guard aborts | **0** |
| Runs with `gitDirty` | **0** |
| Distinct harness commits | **1** (`026be6242d26`) |
| Host-load breaches | **0** (max 1-minute load 1.94 on 8 cores, limit 8.0) |

Two guard aborts occurred **before** the campaign proper, on the ticker injector;
they produced no run record and are documented in A3 as guard aborts, not data.
Three laptop runs probed before the platform move are quarantined in
`results/laptop-preec2/` and are excluded.

## Spread diagnostic (A3)

| boundary | points | flagged | max spread | resolution |
|---|---:|---:|---:|---:|
| c10 / C0 | 6 | 0 | 0.00010 | 0.00250 |
| c10 / C1 | 4 | 0 | 0.00000 | 0.00357 |
| c50 / C0 | 7 | 0 | 0.00040 | 0.00250 |
| c50 / C1 | 5 | 0 | 0.00010 | 0.00357 |
| **total** | **22** | **0** | | |

**Registered trigger (more than two flagged points) is not met.** The consumer
limiter stays on the ticker and the pacing asymmetry remains a methods paragraph,
as A3 provided for.

Measured directly, the limiter's count noise is σ(N(1 s)) = **0.24–1.61 rps**
against a 5 rps resolution, 0.05× to 0.32× of one unit. Under the pre-A4
estimator two points had flagged; both were artefacts of the drain detector's
tail and disappeared under A4.

## Did any boundary move?

**No comparison is made, and none can be made from this data.**

Every anchor drawn from the pre-EC2 corpus classified **non-SAFE on its first
probe** — 840, 290, 990 and 380, all four — and every search extended downward
under A2. A3 registered that possibility in advance, before boundary 1 ran.

Three independent changes separate E1 from the corpus: the **machine**, the
**injector pacer**, and the **ρ estimator**. A4 removes the third and applies to
both sides; the first two remain. Per A3 and the platform-change note in
`NOTES.md`, the corpus last-SAFE values are **search starting points, not
baselines**, and no cross-platform ρ* claim is made anywhere.

For reference only, the corpus anchors under A4 (`results/corpus-a4-recompute.json`):

| anchor | corpus ρ (A4) | E1 result at the same rl |
|---|---:|---|
| c10/C0 rl=840 | 0.9224 | UNSAFE |
| c10/C1 rl=290 | 0.9176 | UNSAFE |
| c50/C0 rl=990 | 0.9872 | UNSAFE |
| c50/C1 rl=380 | 0.9802 | UNSAFE |

Those two columns are **not comparable** and are placed side by side only to show
which rates were probed.

## Artefacts

- Boundary files: `results/boundaries/{c10-C0,c10-C1,c50-C0,c50-C1}.json`
- Run records: `results/c10-c*.json`, `results/c50-c*.json` (66)
- Per-request traces: `../rhc-raw-data/results/c*-consumer.jsonl.gz` (66, 150 MB)
- Corpus recomputation: `results/corpus-a4-recompute.json`
- Pacer characterisation: `results/pacer-characterisation.json`
