# STATUS — where this project actually stands

Written 2026-09-11. Read this before trusting anything in `results/`.

## The one thing to know first

Phase 1 was measured on a harness with a **defect in the downstream's admission
path**, found on 2026-08-19 and fixed the same day. The defect inflated and
distorted every measurement taken **past the safe boundary**. Measurements on
the **safe side of the boundary are unaffected** and stand.

The fix, the finding, and a day of follow-up work were never committed: the
working copy was deleted before anything was pushed. This branch
(`aug19-reconstruction`) restores the code and notes from the session
transcript. See `RECONSTRUCTION.md` for what recovered and what did not.

A second, independent issue: **every published ρ is nominal**, computed as
(λ_L + rl) / C_d from configured rates. Achieved rates are lower, so true ρ is
**0.005 to 0.011 below** every figure in the memos. That is 0.7× to 1.6× the
stated transition width, so it moves boundary claims but not the large
concurrency gap.

## Contamination, precisely

| # | Defect | Found | What it touches |
|---|---|---|---|
| 1 | `downstream/main.go` graceful admission spin-waited on `time.After(100µs)` per blocked request. Thousands of waiters allocated ~37 M timers/s, saturating the host (CPU 1216% vs ~100%) and starving the worker pool. Congestion collapse was manufactured. | 2026-08-19 14:27Z | Every measurement past ρ*. Useful service fell 1837→1463/s while CPU rose 16×. A `PROFILE=cliff` control at the same load gave frac ≤SLO 0.886 vs 0.000. |
| 2 | Collapsed runs agreed to the second across repetitions (tDrain 152.0 / 152.0). That reproducibility **was the CPU clamp**, not stability. Post-fix the same runs give 221 / 197 (12% spread). | 2026-08-19 16:49Z | Any claim that leaned on close agreement across repetitions — the transition-width work in particular. |
| 3 | Consumer rate limiter and probe generators used a tick-dropping `time.Ticker`; delivery 97.2–99.8% of nominal, worsening with rate. All ρ published as nominal. | 2026-08-19 13:58Z | Every ρ in every memo. Shift 0.005–0.011, non-uniform. |
| 4 | Injector delivery was **arm-dependent**: 99.2–100% at S=5, 98.4–98.7% at S=25. The c10 and c50 arms were never run at the same live load (~1% in λ_L, ≈0.005 in ρ). | 2026-08-19 17:02Z | Every cross-arm comparison, including the headline "ρ* rises with concurrency". Does not overturn it: the gap is ~0.07, an order of magnitude larger. |
| 5 | `G_norm` was computed by hand for `PHASE1B-H3H4-s50.md` and divided by 2×G_ceil = 1996, halving both c50 rows. H4's reported vSLO of 0.008 was two host stalls, not live damage. | 2026-08-19 13:22Z | That memo only. Corrected on this branch; the run records were right all along. `scripts/report_metrics.py` now computes G_norm so it is never typed by hand again. |
| 6 | vSLO saturates deep in collapse and cannot distinguish load-shedding from latency collapse. Across three admission designs at ρ=1.31 it read 0.795 / 0.868 / 0.778 while p99 varied **100×** and goodput **9×**. | 2026-08-19 17:22Z | Any saturated-regime comparison keyed on vSLO. Frontier moved to tDrain × G_norm with vSLO decomposed into latency and error components. |

## Memo validity table

"Safe side" means every run in that memo with vSLO = 0. "Collapsed side" means
any run past the boundary. Defect 3 (nominal ρ) applies to every row and is not
repeated.

| Memo | What it claims | Validity now |
|---|---|---|
| `GATE0-memo.md` | Unrestricted catch-up after an outage damages live traffic, P0-A…D × 3 | **Contaminated in magnitude, direction stands.** Entirely a saturated-regime campaign, so defect 1 inflates every severity number. The qualitative result is far larger than the artefact and survives. Re-run needed before any figure is quoted. |
| `GATE0-memo-v2.md` | Corrected architecture (producer stops at restore, injector-direct live SLO), 12/12 valid | **Same as above.** Architecture correction itself is valid; the numbers are saturated-regime. |
| `GATE0-analysis-AB.md` | Harm reaches live via latency and queue, not throughput amplification (~1.06×) | **Valid as a mechanism claim.** The decomposition (open-loop injector + closed-loop consumer ≈ WORKERS/latency) is arithmetic, not a measurement of the collapsed regime. |
| `GATE0-live-population-correction.md` | Live SLO population is `injector_direct` only | **Valid.** A definition correction, recomputed from raw JSONL. |
| `GATE0-pilot-arch2b.md` | Warm-up must be injector-only; W = 15 s from observed settling | **Valid.** Healthy-regime pilot. |
| `GATE1-probes.md` | Frontier axes; G_SLO,live-only ≈ 985–998 | **Valid, one figure superseded.** G_ceil is now pinned at **998 and measured per arm** (both arms gave 998; the ceiling is injector-limited at λ_L, not downstream-limited). Memos using 985 predate that. |
| `PHASE1A-cliff-C0.md` | Coarse C0 sweep: max safe **rl=825**, first unsafe **900**, width 75 rps | **Safe side valid** (600–825, all vSLO 0). **rl=900 row contaminated.** Uses G_ceil = 985. |
| `PHASE1A-followups.md` | Fine C0: **840 safe / 855 marginal / 870 collapsed**, width 30 rps; frontier rl=840, tDrain≈146, vSLO=0; G_ceil=998; occupancy leads latency | **rl=840 safe point valid** — confirmed post-fix at tDrain 142.5, vSLO 0 (−2.4%). **855 and 870 contaminated.** The "thin gradient" and the 30 rps width both depend on contaminated points. Achieved ρ at rl=840 is **0.909**, not 0.920. |
| `PHASE1B-cliff-C1.md` | C1 @ 10 servers: last safe **rl=290** (ρ=0.921), first unsafe **350**; ρ* invariant at 0.92 across a 30% capacity drop | **Last-safe point valid. First-unsafe contaminated.** The invariance claim does **not survive** defect 3: in achieved units C0 gives 0.909 and C1 gives 0.916, not one shared 0.92 to three significant figures. |
| `PHASE1B-C1-fine-H3H4.md` | C1 fine @ 10: no marginal band (rl=300, ρ=0.929 already collapsed); H3 vSLO≈0.80; H4 tDrain≈414 | **Collapsed rows contaminated.** "No marginal band" rests entirely on a collapsed measurement and must be re-tested. H4 (a safe, wrong-low policy) is valid: tDrain 414 vs optimum 146, ~2.8× slower. |
| `PHASE1B-verifA-complete.md` | Live-only at C=1400: capacity is real, ρ*_live = 0.929; **two-class arrival removes the marginal band**; vSLO hides degraded-but-passing | **Live-only measurements valid.** The two-class claim contrasts a passing live-only run against a **collapsed** two-class run, so it is **contaminated**, and it was separately **superseded at 50 servers** (see next-but-three row). The vSLO blind-zone finding is valid and was later generalised by defect 6. |
| `PHASE1B-verifB-s25.md` | 50 servers: all vSLO = 0 through ρ=0.95 (rl=900), where S=5 collapsed | **Valid.** Every run is on the safe side. This is the strongest surviving evidence for the concurrency effect. |
| `PHASE1B-verifB-s25-extend.md` | Extension to rl=990: ρ* ≈ 0.988 at 50 servers | **Valid** for the same reason, subject to the arm bias in defect 4 when compared against c10. |
| `PHASE1B-twoclass-s25.md` | At 50 servers there is **no** catastrophic two-class collapse; Verif-A's effect was a low-concurrency artefact | **Headline valid, two sub-claims withdrawn** (corrected on this branch). Two-class vSLO at 50 is 0.029 vs 0.844 at 10, so the collapse genuinely does not reproduce. But the two sides were paired at **nominal** offered, and the consumer limiter under-delivers more than the injector, so the two-class side sat at lower achieved ρ by 1–2× the transition width. At matched achieved ρ it is already worse: q 1.7 vs 7.3 at ρ=0.973, and 2.3 vs 201 at ρ=0.977. "Indistinguishable through ρ=0.975" is **withdrawn**. The near-ρ→1 rows are additionally contaminated. |
| `PHASE1B-cliff-C1-s25.md` | C1 at 50: last safe **rl=380** (ρ=0.986); first unsafe 430 — but 430 is ρ>1, trivially unsafe | **Last-safe valid; 430 uninformative and contaminated.** The memo says so itself and calls for the fine sweep. |
| `PHASE1B-cliff-C1-s25-fine.md` | C1 @ 50 fine: last safe **380** (ρ=0.986), first damage **390** (ρ=0.993, vSLO≈0.76); severity past ρ* scales with concurrency | **Safe point valid; the 390 damage figure contaminated,** and with it the severity-scaling claim (concurrency finding 3), which compares collapsed measurements across arms. |
| `PHASE1B-H3H4-s50.md` | H3/H4 at 50 servers; H3 prediction not confirmed (vSLO 0.820 @50 vs 0.795 @10) | **Contaminated, and separately corrected** (corrected version on this branch). ** Both rows are collapsed-regime. The `G_norm` arithmetic slip (defect 5) is fixed on this branch: H3 0.059→**0.118**, H4 0.498→**0.997**; H4's vSLO 0.008→**0** (host stalls). |
| **Ultra-fine C1 @ 50, rl ∈ {382,384,386,388}** | **No memo exists.** Records `p1b-c1-s25-uf-rl38*-r{1,2}.json` were run 2026-08-18 09:52–11:02 and never written up. Last safe **382** (vSLO 0/0); 384 gives 0.317/0.058; 386 gives 0.545/0.807; 388 gives 0.724/0.775 | **Unreported, validity pending.** The safe point is sound; every damage figure is a collapsed measurement on the defective harness, and the run-to-run spread at 384 (0.317 vs 0.058) is exactly the instability the fix exposes. **Do not write this up until it is re-run.** NOTES.md still lists it as "pending". |
| `RAW-DATA.md` | Raw JSONL lives outside the repo | **Valid.** Now also archived off-machine: release `raw-data-2026-08-18`. |

## Re-run list on the fixed harness

Required before any collapsed-regime number is published. All at the two
established arms (c10: S=5 ms; c50: S=25 ms), with `report_metrics.py` for
G_norm and per-run achieved ρ recorded.

1. **C0 cliff, rl ∈ {855, 870, 885, 900}** — re-establish whether the marginal band at 855 is real or an artefact. `PHASE1A-followups.md` depends on it.
2. **C1 @ 10, rl ∈ {300, 310, 320, 330, 350}** — re-test "no marginal band at C1", the load-bearing claim for the probing-must-fail argument.
3. **C1 @ 50 fine and ultra-fine, rl ∈ {384, 386, 388, 390, 395, 400}** — the unreported sweep plus the fine grid; both damage sides are contaminated.
4. **H3 in both arms** (rl=840 under C1) — anchors already exist post-fix at 209.0 / 0.868 (blocking) and 140.5 / 0.778 (cliff), n=2; needs the full pair per arm.
5. **Two-class edge at 50 servers, totals 1975–1995** — only the near-ρ→1 rows.
6. **Gate 0 P0-A…D** — if any Gate 0 severity figure is to appear in the paper.
7. **Transition-width determinations everywhere** — defect 2 means the old repeat-agreement evidence is void, so width needs repetitions on a harness that is genuinely stochastic in collapse.

Two standing operational rules from the same session: run under `caffeinate`
(a suspended host silently corrupts timing windows), and **space runs out
rather than batching them back to back** — the final Aug 19 measurements were
taken at a 15-minute load average of 13.9 on 8 cores and the session withdrew
its own conclusions because of it. The runner should record host load at start.

## Profile choice is a first-class experimental variable

At ρ = 1.31, same policy, same capacity, same concurrency:

| profile / admission | tDrain | vSLO | p50 | p99 | G_norm | timeout |
|---|---:|---:|---:|---:|---:|---:|
| graceful, spin-wait (all of Phase 1) | 152.0 | 0.795 | 687 | 1960 | 0.140 | 0.235 |
| graceful, blocking (fixed) | 209.0 | 0.868 | 1999 | 2002 | 0.080 | 0.567 |
| **cliff** | **140.5** | **0.778** | **15** | **19** | **0.737** | **0.000** |

`cliff` sheds load and live traffic stays fast; `graceful` suffers latency
collapse. The decision recorded on Aug 19: **graceful is primary, cliff is
reported as a boundary condition.** Note the queue-cap arithmetic behind it —
graceful's cap is 50 × concurrency, so full-queue delay is 50 × S, which equals
**exactly the 250 ms SLO at S=5 ms** and 1250 ms at S=25 ms. "Queue full" is
definitionally "SLO breach" in the c10 arm and not in c50. That is a competing
explanation for the concurrency effect and is not yet ruled out.

## Phase 2 and Phase 3

**Not started, and must not be started.** SPEC.md forbids controllers and
baseline policies before their phases; NOTES.md repeats "do not design a
controller from this yet" and "Do not start Phase 2". No controller, AIMD,
capacity estimator, or B1/B2/B3 policy exists anywhere in this repository. The
only rate shaping is `consumer/main.go`'s fixed `RATE_LIMIT_RPS` ticker, which
SPEC.md permits as a hardcoded constant.

Phase 1C (C2 and C3) is also **not started**. Predictions were registered on
2026-08-19 and the driver script written, but C2 was held for review and never
ran. Both are restored on this branch:
`results/PHASE1C-C2C3-predictions.md` and `scripts/run_c2.sh`.

### Registered predictions, verbatim

From `results/PHASE1C-C2C3-predictions.md`, written before any C2 or C3 run:

> **Primary prediction (rl = −1):** live SLO is violated during t ∈ [20,90) even
> with no recovery work at all. If confirmed, suspension is **necessary but not
> sufficient**: no recovery controller can protect live traffic when live alone
> exceeds capacity.

> **Post-audit derived prediction:** in achieved units the boundary sits near
> **rl ≈ 180**. Therefore **rl = 200 (ρ_achieved ≈ 0.918) is expected
> marginal-to-unsafe, not safe.**

> **Coverage pre-commitment (registered before the run):** if rl = 200 comes back
> **safe**, run **{215, 230, 245}** immediately without waiting for review —
> otherwise the next grid point (275, ρ = 0.981) brackets the boundary across
> ρ ∈ [0.923, 0.981] and locates nothing, the failure mode of the C1 coarse grid.

> **Honest reading registered in advance:** rl = 200 sits at ρ = 0.923 nominal,
> only 0.003 past ρ*, closer to the boundary than any prior Phase 1 grid point. If
> it comes back safe, the correct reading is that **ρ\* is slightly above 0.923 at
> 7 servers** — *not* that the prediction was confirmed with margin.

From NOTES.md, registered for Gate 2:

> **Phase 2 / Gate 2 prediction (register now):** B3 (latency AIMD) should
> **approximate RHC at 50 servers and fail badly at 10.** All three outcomes
> (reproduces / B3 works at 10 / B3 fails at both) are informative.

That prediction was derived from the mechanism claim that probing **must**
overshoot at low concurrency. Defect 1 reaches that claim: the sharpness it
rests on was measured through the spin-wait. The prediction stands as
registered, but item 2 of the re-run list decides whether its premise does.

## Provenance

Branch `provenance-fix` repairs a separate defect: 137 of 140 run records carry
`gitCommit: "unknown"` because `gitInfo()` swallowed errors, and the runs were
made in a checkout whose HEAD was unborn. The runner now refuses to start unless
HEAD resolves. **No existing run record can be tied to a revision.**

## Branch map

| Branch | Contents |
|---|---|
| `main` | d09049a, as pushed 2026-08-19 12:21Z. `results/` present only as `results.zip`. |
| `results-in-git` | `results/` unpacked and committed (217 files), plus `results/README.md`. |
| `aug19-reconstruction` | The lost day: NOTES.md additions, harness fixes, 7 scripts, this file, `RECONSTRUCTION.md`. |
| `provenance-fix` | Strict git provenance in the runner, plus a smoke run proving it. |
