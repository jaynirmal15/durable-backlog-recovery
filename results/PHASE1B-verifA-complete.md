# Verification A — complete (live-only ρ* + occupancy at equal ρ)

**Hold C2/C3.** Verification B (S=25 ms) running separately.  
Data: `results/probe-verifa-c1400-live-only.json`, `results/probe-verifa-c2000-live-only-extend.json`  
(+ Probe 1 `results/probe1-live-only.json` for C=2000 ≤1600).

---

## 1. Settled earlier

- C=1400 is achievable (≈1340 rps at 1350 offered).
- `C_SLO,live`(1400) = **1300** → ρ*_live = **0.929**.
- Two-class arrival at the same ρ collapses the marginal band that live-only keeps
  (NOTES; paper line).
- vSLO blind zone: degraded-but-passing at 1300/1400 (p50×10, qMean×58, still sloOK).
  **Add p50 to Phase 2 metrics.**

---

## 2. C=2000 extension — offered ∈ {1700, 1800, 1850, 1900, 1950}

| offered | ρ | achieved | p50 | p99 | frac≤250 | goodput | qMean | qPeak | SLO |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1700 | 0.850 | 1691 | 5 | 18 | 1.000 | 1691 | 0.6 | 49 | ✓ |
| 1800 | 0.900 | 1797 | 5 | 192 | 0.998 | 1795 | 8.9 | 391 | ✓ |
| **1850** | **0.925** | 1845 | 6 | **80** | 1.000 | 1845 | **9.1** | 164 | ✓ |
| **1900** | **0.950** | 1893 | **173** | **246** | 0.996 | 1885 | **283** | 464 | ✓ |
| 1950 | 0.975 | 1943 | 336 | 1167 | 0.175 | 340 | 455 | 503 | ✗ |

**`C_SLO,live`(2000) = 1900** → **ρ*_live = 0.950.**

Predicted knee if ρ*_live were invariant at 0.929: ≈ **1858**. Observed last-safe
is **1900** (ρ=0.950); 1850 (ρ=0.925) is still healthy with low occupancy.

### Is live-only ρ* invariant?

| | C=1400 | C=2000 |
|---|---|---|
| C_SLO,live | 1300 | **1900** |
| ρ*_live | **0.929** | **0.950** |

**Not the same to 3 s.f.** Live-only ρ* sits slightly higher at larger C
(~0.93 vs ~0.95). The *recovery* experiment’s ρ*≈0.92 remains a separate,
tighter bound under two-class load — do not conflate with live-only ρ*.

---

## 3. Occupancy at equal ρ ≈ 0.929 under live-only

| | C=1400 @ 1300 (ρ=0.929) | C=2000 @ 1850 (ρ=0.925) |
|---|---|---|
| p50 | 63 | 6 |
| p99 | 122 | 80 |
| **qMean** | **80.8** | **9.1** |
| SLO | pass | pass |

**~9× occupancy difference at essentially the same ρ under single-class
live-only traffic.** Occupancy non-invariance is a property of the **queue /
concurrency model** (fewer servers → longer queue at equal ρ), not an artefact
of the two-class arrival process. That is the clean version of the experiment.

(Nearest C=2000 point to ρ=0.929 is 1850; 1900 is already ρ=0.950 and qMean=283 —
past the live-only knee into the degraded-but-passing / near-fail zone.)

---

## 4. Carry-forward

- Configured C is real; bistability still a candidate for *two-class* 18× gap,
  but equal-ρ occupancy already diverges under live-only.
- Live-only ρ* ≈ 0.93–0.95 (capacity-dependent); recovery ρ* ≈ 0.92 is stricter.
- Two-class burstiness + p50 early indicator stay as stated in NOTES.
- **Verification B** (S=25 ms / 50 servers) decides whether the sharp cliff is a
  low-concurrency artefact — more consequential for re-baseline.

**C2/C3 not started.**
