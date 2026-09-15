# A8 — repeatability of the corrected saturation plateaus

**Registered before any run** as `PRE-REGISTRATION.md` addendum A8, commit
**`590d1cccee8228da739743245b85ac49e9cb056e`**, 2026-09-14 21:08:27 −0400. That
commit contains the registration and nothing else.

Analysis: `scripts/a8_repeatability.py` → `results/A8-plateau-repeatability.json`.
Records: `results/a8/`, 20 files.

## The build

Rebuilt at **`c7f5835b2b06e59bd29239ea352451e040cf12a5`**, the commit the original
corrected runs used, and the rebuild **reproduces the original binaries byte for
byte**:

| binary | SHA-256 |
|---|---|
| `downstream` | `ac88c60879e89868cc2bf1f042eaa4e88c709ad665ac072f86645df203d3b750` |
| `overhead_run` | `ea6c54f2daf3cfd5380108a72dba368d6f84e4eb46cb0608bc6f56ae2cb8a987` |

Reaching that required care worth recording. A first rebuild differed from the
originals, and the difference was **entirely the VCS stamp**: `vcs.modified=true`
and a `+dirty` module version, because the box's checkout had accumulated
untracked result files since the original build. Go's stamping counts untracked
files. Setting only the untracked files aside — the tracked tree was already
exactly `c7f5835b` — and rebuilding at the original path reproduced both binaries
exactly. Independently, `-trimpath -buildvcs=false` builds from the campaign tree
and from a pristine clone are byte-identical, which isolates the compiled code
from path and VCS metadata.

The only difference in any build input between `c7f5835b` and current `HEAD` is
the `note` string literal and its comment in `downstream/main.go`. A8 declared in
advance that this build inherits the superseded note; the twenty records carry
it, and it is wrong in the way METHOD-AUDIT item 20 describes. The build must
match or the measurement is of something else.

## Construction

Each window: a **fresh `downstream` process**, then one `overhead_run` invocation
— closed-loop, **400 connections**, no configured offered rate, 10 s warm-up
discarded, **60 s** measured — then the process torn down. Identical in
construction to the original `exp2-*-plateau` measurement.

All 20 records were checked against the original configuration and match exactly:
`offeredRate` 0, `closedLoopConns` 400, `configuredCapacity` 2000,
`serviceTimeUs` 4537/24537, `concurrency` 10/50, `queueCap` 500/2500,
**`rejected` 0 and `timedOut` 0 in every window**, every `windowSec` within
1.2 ms of 60.

One operational note, for the record: the first attempt stalled after one window.
The run script tore the downstream down with `SIGINT`, but the script was started
with `nohup` in the background, so its children inherited SIGINT ignored
(`SigIgn 0x3`) and the teardown silently never fired. Fixed to `SIGTERM` with a
`SIGKILL` fallback. The one window produced before the stall was constructed
identically and is retained as `c10` w1; no measurement was affected.

## All twenty windows

### Short arm, `c10` — S = 4.537 ms, 10 workers

| window | servedRps | windowSec | rejected | timedOut |
|---|---|---|---|---|
| 1 | 1989.1312 | 60.0011 | 0 | 0 |
| 2 | 1990.2411 | 60.0003 | 0 | 0 |
| 3 | 1988.7487 | 60.0005 | 0 | 0 |
| 4 | 1989.0465 | 60.0011 | 0 | 0 |
| 5 | 1989.6870 | 60.0004 | 0 | 0 |
| 6 | 1987.7941 | 60.0012 | 0 | 0 |
| 7 | 1987.9792 | 60.0006 | 0 | 0 |
| 8 | 1990.3835 | 60.0010 | 0 | 0 |
| 9 | 1987.2731 | 60.0003 | 0 | 0 |
| 10 | 1988.8817 | 60.0006 | 0 | 0 |

### Long arm, `c50` — S = 24.537 ms, 50 workers

| window | servedRps | windowSec | rejected | timedOut |
|---|---|---|---|---|
| 1 | 1996.8857 | 60.0009 | 0 | 0 |
| 2 | 1997.9669 | 60.0010 | 0 | 0 |
| 3 | 1997.0730 | 60.0003 | 0 | 0 |
| 4 | 1997.4977 | 60.0006 | 0 | 0 |
| 5 | 1998.3636 | 60.0011 | 0 | 0 |
| 6 | 1997.9084 | 60.0002 | 0 | 0 |
| 7 | 1998.5715 | 60.0004 | 0 | 0 |
| 8 | 1996.5246 | 60.0003 | 0 | 0 |
| 9 | 1999.3534 | 60.0009 | 0 | 0 |
| 10 | 1997.0968 | 60.0006 | 0 | 0 |

No window was discarded. There was no integrity failure to record.

## Per arm

| arm | n | min | **median** | max | **range** | lower hinge | upper hinge | **IQR** | SD |
|---|---|---|---|---|---|---|---|---|---|
| c10 | 10 | 1987.2731 | **1988.9641** | 1990.3835 | **3.1104** | 1987.9792 | 1989.6870 | **1.7078** | 0.9542 |
| c50 | 10 | 1996.5246 | **1997.7031** | 1999.3534 | **2.8288** | 1997.0730 | 1998.3636 | **1.2905** | 0.8127 |

The spread is **3.1 rps in the short arm and 2.8 rps in the long one**, against
the 0.10–0.24% (1.9–4.0 rps) repeatability of the seven-cell plateaus. These two
plateaus are no noisier than the rest of the corpus; they simply had never been
measured more than once.

## The registered readings

### Short arm (S = 5 ms) — OUTCOME 1: the prediction discriminated

| | |
|---|---|
| observed spread | **[1987.2731, 1990.3835]**, width 3.1104 rps |
| implied by the registered constant (δ = 0.4947) | **1987.3999** — **inside** |
| implied by the rival constant (δ = 0.5165) | **1978.8266** — **outside** |
| separation | 8.5733 rps |

**The value implied by the registered constant lies within the observed spread
and the rival lies outside it.** This is A8's first outcome: the short-arm
prediction discriminated.

The margin is not large. The registered value sits 0.13 rps above the lowest of
the ten windows — near the bottom edge of the spread, not in its middle. The
rival sits 8.4 rps below the lowest window, which is 2.7 spreads clear.

### Long arm (S = 25 ms) — the registered prediction is confirmed

| | |
|---|---|
| implied plateaus | 1997.7306 (registered constant) and 1996.1355 (rival) |
| separation | 1.5951 rps |
| observed spread | **2.8288 rps** |

**The observed spread exceeds the separation.** A8 predicted exactly this. The
long arm cannot discriminate the two constants, and the manuscript's existing
statement to that effect stands.

### The original single windows

| arm | original | median of 10 | difference | spread | reading |
|---|---|---|---|---|---|
| c10 | 1987.3834 | 1988.9641 | **+1.5807** | 3.1104 | within the spread |
| c50 | 1998.1460 | 1997.7031 | **−0.4429** | 2.8288 | within the spread |

**Neither median differs from its original single window by more than the
observed spread**, so A8's finding-about-the-original clause is not triggered in
either arm. Both originals lie inside the replicated range.

Two facts stated because they are directly auditable, not as interpretation: in
the short arm **1 of the ten replicated windows falls below the original and 9
above it**; in the long arm 7 fall below and 3 above.

## What this does not say

A8 fixed three readings and this report answers those three. It does not revisit
the boundary prediction, the boundary brackets, or any seven-cell result, and
nothing here bears on them. Any question outside the repeatability of these two
plateaus is outside this addendum's scope and would need its own.
