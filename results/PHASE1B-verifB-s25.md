# Verification B — S = 25 ms concurrency probe (50 servers)

**Hold C2/C3.** Downstream restored to S=5 ms after this probe.  
**Setup:** C=2000, λ_L=1000, P0-A, SERVICE_TIME_MS=**25** → concurrency = **50**, queueCap=2500.  
**Sweep:** rl ∈ {600, 750, 825, 855, 900} × **2** (10/10 valid).  
Data: `results/p1b-verifb-s25-rl*-r*.json`, summary `results/PHASE1B-verifB-s25.json`.

---

## Results (drain means)

| rl | ρ | tDrain | vSLO | p50 | p99 | goodput | qMean | mean IF |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 600 | 0.800 | 200 | **0.000** | 26 | 44 | 969 | 0.7 | 26 |
| 750 | 0.875 | 160 | **0.000** | 26 | 76 | 988 | 1.9 | 27 |
| 825 | 0.912 | 147 | **0.000** | 25 | 34 | 998 | 0.06 | 26 |
| 855 | 0.927 | 142 | **0.000** | 25 | 34 | 998 | 0.11 | 26 |
| **900** | **0.950** | **135** | **0.000** | **25** | **35** | **997** | **0.35** | **26** |

Compare same grid under S=5 (10 servers) from §3a:

| rl | S=5 vSLO / p99 / qMean | S=25 vSLO / p99 / qMean |
|---:|---|---|
| 825 | 0 / 11 / 1.0 | 0 / 34 / 0.06 |
| 855 | **0.006** / 95 / **18** | **0** / 34 / **0.11** |
| 900 | **0.793** / 547 / **459** | **0** / 35 / **0.35** |

---

## Answers to the three questions

### Does ρ* stay ≈ 0.92?

**Not observed on this grid.** Every point through ρ=0.950 is fully SLO-safe
(vSLO=0). Either ρ* moved **above 0.95**, or the cliff is soft enough that this
coarse grid never hits it. Cannot claim invariance of ρ*≈0.92 at 50 servers
without extending past rl=900.

### Does a marginal band appear?

**The hard cliff disappears.** Under S=5, rl=900 is deep collapse. Under S=25,
rl=900 is indistinguishable from rl=825 on vSLO/occupancy. There is no
C0-style 855-marginal → 870-collapse sequence on this grid — because there is
**no collapse at all** through ρ=0.95.

### Does p99 develop a gradient approaching the boundary?

**No useful pre-cliff latency gradient** on this grid: p50 sits on the service
time (~25 ms), p99 ≈ 34–35 ms from rl=825 through 900. One 750-r1 outlier
(p99=117) did not recur. Occupancy stays ≪1. Latency does not warn because
there is no boundary in range.

---

## Verdict — outcome 2 (cliff softens materially)

**S = 5 ms / 7–10 servers produces an artificially hard knee.** At 50 servers
the saturating dependency no longer exhibits the sharp cliff, absent marginal
band, or occupancy blow-up that §2’s “probing must fail” argument relied on.

| Implication | Action |
|---|---|
| Operating point | **Re-baseline before Phase 2** is warranted — default S=5 is not representative of high-concurrency dependencies |
| §2 mechanism argument | **Weakens** for many-server regimes; may still hold at low concurrency, but that is a narrower claim |
| ρ* ≈ 0.92 from C0/C1 | Established under S=5 only; **do not treat as concurrency-invariant** until re-measured at the new operating point |
| Two-class burstiness (Verif A) | Also measured at S=5; **re-test at higher concurrency** if re-baselining |
| C2/C3 | **Hold** — running more S=5 regimes compounds the artefact |

### Suggested next decision (not executed)

Pick a higher-concurrency operating point (e.g. S=25 ms, C=2000, concurrency=50,
or an intermediate), re-locate ρ* / cliff / marginal band with a fine sweep that
extends past ρ=0.95, then decide whether Phase 2/3 framing is “estimate C_d
because probing has no warning” or a narrower claim.

**Downstream restored to S=5 ms** so the harness matches prior C0/C1 artifacts
until that decision.
