# P0-B architecture pilot (`p0b-pilot-arch2b`)

**Status:** complete, valid — awaiting approval before full re-run.  
**Failed attempt:** `p0b-pilot-arch2` aborted (warmup ran injector+NATS consumer = 2×λ_L).

## Architecture under test

| Phase | Producer | Injector |
|---|---|---|
| Warmup / healthy | off | λ_L |
| Outage | on (builds backlog) | λ_L |
| Restore → T_full | **stopped** | λ_L continuous |

## Results vs invalidated p0b-r1

| Metric | Old p0b-r1 (contaminated) | Pilot arch2b |
|---|---:|---:|
| backlogAtRestore | 118531 | 116936 |
| tDrain | 145 s | **149 s** |
| tFull | 468 s | **184 s** |
| **gap (tFull−tDrain)** | **323 s** | **35 s** |
| queue→0 after drain | ~290 s later | **~1 s later (t=150)** |
| vSLO | 0.934 (blended) | 0.837 (injector) |
| NATS-live post-restore | large | **1 sample** (≈0) |
| Recovery samples | — | 116936 (= backlog) |
| Injector-live samples | — | 183296 |
| liveRps≤0 seconds | — | **0 / 184** |

## Interpretation

1. **NATS-live artefact removed** — post-restore live is injector-only.
2. **Post-drain gap collapsed** from ~323 s to **~35 s**, of which **~30 s is the configured stabilize window** and ~5 s is queue draining from ~259→0 with latency falling from ~1.5 s→~10 ms.
3. Residual `T_drain ≠ T_full` after removing the artefact is **mostly stabilize-window padding**, not a multi-minute recovery hysteresis. The protocol’s headline gap under P0-B was **largely artefactual**.
4. Unrestricted catch-up still harms live during drain (injector p99 ~2 s, vSLO 0.84) — Gate 0 safety failure remains; only the T_full gap claim changes.

## Recommendation

Do **not** start the full campaign until this pilot is reviewed. If accepted:

- Re-run P0-A/B/C/D × 3 under this architecture
- Memo should report the small residual gap honestly and reconsider whether
  `T_full` (with a 30 s stabilize requirement) overstates recovery time when
  the queue empties within ~1–5 s of `T_drain`
- Retain old 12 runs + HOL 20–37 rps NATS-live finding as scoping evidence
