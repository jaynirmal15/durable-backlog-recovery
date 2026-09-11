# C2 / C3 — predictions registered before running

<!-- This file was reconstructed from the 2026-08-19 session log; original was never committed.
     See RECONSTRUCTION.md. -->

**Date:** 2026-08-19 (written before the first C2 or C3 run)
**Arm:** `c10` only — `-arm c10`, downstream S = 5 ms, concurrency 10 at C = 2000.
**Operating point:** λ_L = 1000, nominal C = 2000, outage 120 s, backlog ≈ 120 k.
**Basis:** ρ* ≈ 0.92 at 7–10 servers (C0/C1, both arms of the c10 evidence);
transition width ≤ 0.007 in ρ; severity past ρ* falls with concurrency only for
small overshoot near ρ*.

These conditions test **controller behaviours** — headroom reclamation (C2) and
recovery suspension (C3) — not concurrency effects, so one arm suffices.

---

## C2 — temporary degradation (`P0-C`: 2000 → 1300 @ t=20 → 2000 @ t=60)

Fault capacity C_d = 1300 → concurrency at fault = ⌈1300 × 0.005⌉ = **7 servers**,
the same fault-window concurrency as C1. Safe total at ρ* = 0.92 is
0.92 × 1300 = **1196**, so **predicted safe rl ≈ 196**.

| rl | total | ρ (fault) | prediction |
|---:|---:|---:|---|
| 150 | 1150 | **0.885** | **safe** — vSLO 0, qMean low |
| 200 | 1200 | **0.923** | **first unsafe**, marginal — 0.003 past ρ*; C1 fine sweep put last-safe at ρ=0.921 and collapse at ρ=0.929 |
| 275 | 1275 | **0.981** | unsafe |
| 350 | 1350 | **1.038** | unsafe, ρ > 1 (trivially) |

### Second prediction — post-audit, in achieved units

**Registered 2026-08-19, after the ρ audit, before any C2 run.** Provenance is
deliberately visible: the primary prediction above was made in **nominal** units
against a nominal-units baseline (ρ* ≈ 0.92) and is **not** revised. This second
prediction restates it in **achieved** units after the load-generator audit
showed nominal ρ overstates true utilisation by 0.005–0.011.

Achieved-unit baseline: ρ* = **0.909** (C0) to **0.916** (C1) at 7–10 servers.
The consumer limiter delivers ~98–99% of nominal `rl` and the injector ~99.4–99.8%
of λ_L, so at C_d = 1300 achieved total ≈ 0.997·1000 + 0.985·rl.

> **Post-audit derived prediction:** in achieved units the boundary sits near
> **rl ≈ 180**. Therefore **rl = 200 (ρ_achieved ≈ 0.918) is expected
> marginal-to-unsafe, not safe.**

| rl | ρ nominal | ρ achieved (est.) | primary prediction | post-audit prediction |
|---:|---:|---:|---|---|
| 150 | 0.885 | **0.881** | safe | safe |
| 200 | 0.923 | **0.918** | first unsafe (marginal) | **marginal-to-unsafe** |
| 275 | 0.981 | **0.975** | unsafe | unsafe |
| 350 | 1.038 | **1.032** | unsafe | unsafe |

C2 is reported against **both**, with achieved ρ computed per run from
`injectorIssued` and `backlogAtRestore / tDrain`.

**Coverage pre-commitment (registered before the run):** if rl = 200 comes back
**safe**, run **{215, 230, 245}** immediately without waiting for review —
otherwise the next grid point (275, ρ = 0.981) brackets the boundary across
ρ ∈ [0.923, 0.981] and locates nothing, the failure mode of the C1 coarse grid.
If rl = 200 is unsafe the boundary is already bracketed tightly enough.

**Honest reading registered in advance:** rl = 200 sits at ρ = 0.923 nominal,
only 0.003 past ρ*, closer to the boundary than any prior Phase 1 grid point. If
it comes back safe, the correct reading is that **ρ\* is slightly above 0.923 at
7 servers** — *not* that the prediction was confirmed with margin.

**Caveat registered in advance:** the fault window is only 40 s, but vSLO is
normalised over the whole T_full. A run can be badly damaged during the fault
and still show a modest whole-run vSLO. **`faultVSLO` (violations within
t ∈ [20,60)) is therefore the primary safety axis for C2**, with whole-run vSLO
reported alongside. This is a reporting split, not a change to the vSLO
definition.

**Reclamation:** after t = 60 headroom returns to 1000 while rl stays fixed, so
a static policy cannot exploit it. Expect tDrain to be dominated by rl, not by
the fault — i.e. tDrain ≈ backlog / rl regardless of the fault window. Evidence
that static policies waste reclaimed headroom.

---

## C3 — infeasible (`P0-D`: 2000 → 900 @ t=20 → 2000 @ t=90)

During the fault, C_d = 900 **< λ_L = 1000**. Headroom is **−100**: live traffic
alone sits at ρ_live = 1000/900 = **1.111 > 1** with *zero* recovery admitted.
**Predicted safe rl = 0** — no positive rate is safe, and 0 is not sufficient
either.

| rl | total | ρ (fault) | prediction |
|---:|---:|---:|---|
| **−1** (suspended) | 1000 | **1.111** | **live SLO violated during the fault window despite zero recovery load** |
| 100 | 1100 | **1.222** | violated, worse |
| 200 | 1200 | **1.333** | violated, worst |

**Primary prediction (rl = −1):** live SLO is violated during t ∈ [20,90) even
with no recovery work at all. If confirmed, suspension is **necessary but not
sufficient**: no recovery controller can protect live traffic when live alone
exceeds capacity. That bounds what `RECOVERY_SUSPENDED` can be expected to
achieve and justifies it as a distinct state rather than "rate → 0".

**Second prediction (time to health):** after capacity is restored at t = 90
(C = 2000, λ_L = 1000, ρ = 0.5), live returns to health within **tens of
seconds** — point estimate **5–15 s**. The downstream is memoryless (queue
drains ~1 s, latency returns ~5 s per `p0b-pilot-arch2b`); the 5 s reporting
window plus the 3 s healthy streak required by the detector adds ~8 s of
measurement lag. This bounds how quickly a controller could resume.

**Protocol note for rl = −1.** `-rate-limit 0` already means *unrestricted*, so
zero admission is expressed as **`-rate-limit -1`** (new sentinel; 0 unchanged,
so every existing record keeps its meaning). A suspended run never drains, so
`T_drain` cannot be reached: these runs use a fixed **300 s horizon**
(`-horizon 300`, leaving 210 s post-restore) and record `tDrainSec = -1` with
`tDrainReached = false`. The `zero_recovery_traffic_during_drain` integrity
check is suppressed when recovery is suspended by design.

---

## Metrics

All runs carry the host-stall detector (`stallSeconds`, `contaminatedSeconds`,
`vSLO_raw`) and the `sustained_live_rate_deviation` integrity check, both added
2026-08-19. `G_norm` is computed by `scripts/report_metrics.py --g-ceil 998`,
never by hand. G_ceil = 998 for the c10 arm.
