# Aug 19 runs — headline metrics recovered from the session log

<!-- reconstructed from the 2026-08-19 session log; original was never committed. -->

The 2026-08-19 session wrote 36 result files into `results/` of a working copy
that was later deleted. **None of those files' full contents (timelines,
per-second samples) appear in the session log, so the files themselves are not
recoverable.** What follows is everything the session log does contain about
them: the runner's `wrote results/…` log line per run, and the tables the
session reported. Source is the session log's command output for command *NNNN*
(zero-based order of Bash calls) or the written status report at the given UTC time.

Harness state for every run below: the Aug 19 working tree — d09049a plus the
uncommitted edits reconstructed on this branch. Runs before 16:15Z used the
spin-wait downstream; runs after used the blocking-semaphore downstream. Runs
after 18:39Z used the multi-lane injector pacer unless stated. The session
itself flagged the last stretch (from ~19:20Z) as confounded by host load
(1-min load average 5.6, 15-min 13.9 on 8 cores).

## Runner log lines (verbatim)

| run record | runner log (tool output of cmd) |
|---|---|
| `p1x-anchor-c0-rl840-r1.json` | `tDrain=142.0 tFull(W=15)=156.0 tFull(W30)=171.0 vSLO=0.000 (raw 0.000) stallSec=1 contamSec=6` (0181) |
| `p1x-anchor-c0-rl840-r2.json` | `tDrain=143.0 tFull(W=15)=157.0 tFull(W30)=172.0 vSLO=0.000 (raw 0.000) stallSec=0 contamSec=0` (0181) |
| `p1x-anchor-h3-c1-rl840-r1.json` | `tDrain=221.0 tFull(W=15)=245.0 tFull(W30)=260.0 vSLO=0.853 (raw 0.853) stallSec=0 contamSec=0` (0181) |
| `p1x-anchor-h3-c1-rl840-r2.json` | `tDrain=197.0 tFull(W=15)=221.0 tFull(W30)=236.0 vSLO=0.882 (raw 0.882) stallSec=0 contamSec=0` (0189) |
| `p1x-anchor-h3-c1-rl840-cliff-r2.json` | `tDrain=141.0 tFull(W=15)=158.0 tFull(W30)=173.0 vSLO=0.778 (raw 0.778) stallSec=0 contamSec=0` (0195) |
| `p1x-anchor-h3-c1-rl840-cliff-r1b.json` | `tDrain=140.0 tFull(W=15)=157.0 tFull(W30)=172.0 vSLO=0.777 (raw 0.777) stallSec=0 contamSec=0` (0199) |
| `p1x-anchor-c50-c1-rl380-r1b.json` | `tDrain=0.0 tFull(W=15)=149.0 tFull(W30)=149.0 vSLO=0.000` — aborted attempt, invalid record retained (0199) |
| `p1x-anchor-c50-c1-rl380-r2b.json` | `tDrain=0.0 tFull(W=15)=16.1 tFull(W30)=16.1 vSLO=0.000` — aborted attempt, invalid record retained (0199) |
| `p1x-anchor-c50-c1-rl380-r1c.json` | tDrain 309.0, vSLO **0.744** (report 19:04Z; run under the unbounded multi-lane pacer — **withdrawn as evidence** 19:25Z) |
| `p1x-anchor-c50-c1-rl380-r2c.json` | tDrain 322.0, vSLO **0.854** (report 19:04Z; same status) |
| `p1x-anchor2-c0-rl840-r1.json` | collapsed under the unbounded multi-lane pacer — **withdrawn as evidence** (19:25Z) |
| `p1x-anchor3-c0-rl840-r1.json` | `tDrain=131.1 tFull(W=15)=150.0 tFull(W30)=165.0 vSLO=0.847 (lat 0.847 err 0.013) faultVSLO=0.000 t2health=0 stallSec=0 contamSec=0`; self-check 99.43% (0231) |
| `p1x-anchor3-c0-rl840-r2` | **REFUSED** by the generator self-check (98.95%); no record (19:34Z) |
| `p1x-anchor4-c0-rl840-r1.json` | ticker pacer restored; verification run, result superseded by the host-load finding (19:50Z) |
| `p1x-ratetest-c0-rl840-live994.json` | `tDrain=135.1 tFull(W=15)=154.0 tFull(W30)=169.0 vSLO=0.805 (lat 0.805 err 0.000) faultVSLO=0.000 t2health=0 stallSec=0 contamSec=0`; ρ_ach 0.906 (0243) |
| `smoke-injfix-c10.json` | `tDrain=26.0 tFull(W=15)=40.0 tFull(W30)=55.0 vSLO=0.000 (lat 0.000 err 0.000)`; injector 99.98% (0217) |
| `smoke-injfix-c50.json` | `tDrain=27.0 tFull(W=15)=41.0 tFull(W30)=56.0 vSLO=0.000 (lat 0.000 err 0.000)`; injector 99.98% (0218) |
| `hysteresis-s5-c2000.json`, `hysteresis-s5-c1400.json` | written by `scripts/hysteresis/main.go` (0159, 0161); tables below |
| `hysteresis-s5-c2000-mechanism.json` | served/s, timedOut/s, CPU per step; table below (14:27Z) |
| `hysteresis-cliff-control.json` | `PROFILE=cliff` control; table below (14:27Z) |
| `hysteresis-s5-c2000-blocking.json` | post-fix downstream; table below (16:22Z) |
| `hysteresis.json` | first driver output, superseded by the `-s5-*` files |
| `probe-c50-gceil-s25-paced.json`, `-lanes.json` | G_ceil probes with the token-bucket and multi-lane pacers; both arms gave **G_ceil = 998** (0131, 13:46Z) |
| `probe-warmup-check-s5-c2000-desc.json`, `-c1400-desc.json` | descending warm-up checks feeding the hysteresis finding (14:16Z) |
| `PHASE1C-C2C3-predictions.md` | **fully recovered** — see the file on this branch |
| `*-consumer.jsonl` (9 files) | raw traces; several were 0 bytes because the disk was full |

## Anchor validity as recorded by the runner (cmd 0206)

The session's own listing of `invalidReason` across the anchor records. Three
records named here are not in the 36-file list above because they were aborted
attempts whose only trace is this listing.

```
p1x-anchor-c0-rl840-r1.json                  VALID
p1x-anchor-c0-rl840-r2.json                  VALID
p1x-anchor-c50-c1-rl380-r1.json              generator_rate_deviation_at_warmup
p1x-anchor-c50-c1-rl380-r1b.json             sustained_live_rate_deviation
p1x-anchor-c50-c1-rl380-r2.json              generator_rate_deviation_at_warmup
p1x-anchor-c50-c1-rl380-r2b.json             sustained_live_rate_deviation
p1x-anchor-h3-c1-rl840-cliff-r1.json         generator_rate_deviation_at_warmup
p1x-anchor-h3-c1-rl840-cliff-r1b.json        VALID
p1x-anchor-h3-c1-rl840-cliff-r2.json         VALID
p1x-anchor-h3-c1-rl840-r1.json               VALID
p1x-anchor-h3-c1-rl840-r2.json               VALID
```

## Tables as reported by the session

### Hysteresis, C=2000, stepping down from collapse (14:16Z)

| offered | ρ | p50 | frac ≤SLO | qMean | state |
|---:|---:|---:|---:|---:|---|
| 1850 *(fresh start)* | 0.925 | 15 | 1.000 | 44.8 | healthy |
| 1950 | 0.975 | 1273 | 0.000 | 481.9 | collapsed |
| 1900 | 0.950 | 1219 | 0.000 | 500.6 | still collapsed |
| 1850 | 0.925 | 991 | 0.000 | 500.4 | still collapsed |
| 1800 | 0.900 | 987 | 0.000 | 500.6 | still collapsed |
| 1750 | 0.875 | 936 | 0.000 | 500.6 | still collapsed |
| 1700 | 0.850 | 739 | 0.000 | 500.6 | still collapsed |
| 1650 | 0.825 | 183 | 0.513 | 258.1 | recovering |

### Hysteresis, C=1400 (14:19Z)

| offered | ρ | frac ≤SLO | qMean | state |
|---:|---:|---:|---:|---|
| 1250 *(fresh)* | 0.893 | 1.000 | 9.6 | healthy |
| 1350 | 0.964 | 0.009 | 349.7 | collapsed |
| 1300 | 0.929 | 0.000 | 341.9 | still collapsed |
| 1250 | 0.893 | 0.000 | 350.6 | still collapsed |
| 1200 | 0.857 | 0.847 | 68.8 | recovering |
| 1150 | 0.821 | 1.000 | 1.4 | recovered |

### Mechanism and control (14:27Z) — the hysteresis is a harness artefact

| state | offered | served/s | timedOut/s | qMean | frac ≤SLO | CPU |
|---|---:|---:|---:|---:|---:|---:|
| healthy | 1850 | 1837 | 0 | 171.8 | 1.000 | ~76% |
| collapsed | 1950 | 1463 | 459 | 500.4 | 0.000 | 1216% |
| collapsed | 1700 | 1589 | 113 | 500.4 | 0.000 | ~1050% |
| healthy | 1500 | 1500 | 0 | 1.7 | 1.000 | ~58% |

| profile | offered | frac ≤SLO | qMean | CPU |
|---|---:|---:|---:|---:|
| graceful (spin-wait) | 1950 | 0.000 | 500.4 | 1216% |
| cliff | 1950 | 0.886 | 17.4 | ~100% |

### Blocking-semaphore admission, offered 1950 (16:22Z)

| admission | frac ≤SLO | qMean | served/s | timedOut/s | CPU |
|---|---:|---:|---:|---:|---:|
| spin-wait | 0.000 | 500.4 | 1463 | 459 | 1216% |
| blocking | 0.000 | 500.0 | 1620 | 269 | ~100% |
| cliff | 0.886 | 17.4 | 1501 | 0 | ~100% |

### Anchors on the fixed downstream (17:22Z), n=2 each unless noted

| anchor | tDrain | vSLO | p50 | p99 | G_norm | timeout | qMean |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0-840 spin-wait *(safe, Phase 1)* | 146.0 | 0.000 | 6 | 24 | 1.001 | 0.000 | 2.2 |
| C0-840 blocking *(safe)* | 142.5 | 0.000 | 6 | 42 | 0.977 | 0.000 | 3.5 |
| H3 spin-wait *(Phase 1)* | 152.0 | 0.795 | 687 | 1960 | 0.140 | 0.235 | 303.6 |
| H3 blocking-graceful | 209.0 | 0.868 | 1999 | 2002 | 0.080 | 0.567 | 398.4 |
| H3 cliff | 140.5 | 0.778 | 15 | 19 | 0.737 | 0.000 | 11.2 |

Run-to-run spread, H3 @ C1: pre-fix tDrain 152.0 / 152.0 (0.0%), post-fix
221.0 / 197.0 (12.2%); pre-fix vSLO 0.7953 / 0.7941, post-fix 0.8530 / 0.8823.

### Injector pacer A/B on one downstream (19:41Z)

| offered | ticker | lanes |
|---|---|---|
| 1000 | achieved 975.4, qMean 20.0, qPeak 500, p99 779, sloOK false | achieved 1000.0, qMean 0.1, qPeak 3, p99 8 |
| 1600 | achieved 1549.2, qMean 3.5 | achieved 1595.1, qMean 1.4 |
| 1850 | achieved 1793.0, qMean 4.4 | achieved 1803.7, qMean 487.9 |

Bounded multi-lane vs historical ticker at safe load (19:25Z): offered 1000 —
ticker qMean 0.1 / qPeak 6 / p99 8 vs lanes qMean 0.3 / qPeak 50 / p99 26;
offered 1400 — identical (qMean 0.1, qPeak 1, p99 7).

### Session's own caveat on the last stretch (19:50Z)

Host load averages were 5.59 (1 min), 10.96 (5 min), 13.91 (15 min) on 8
cores during the pacer experiments; the ticker delivered 96.18% where it
historically delivered 99.4–99.8%. The session declined to draw pacer
conclusions from `p1x-anchor3`, `p1x-anchor4`, `p1x-ratetest`, and the A/B
until re-measured on a quiet host. That re-measurement never happened.
