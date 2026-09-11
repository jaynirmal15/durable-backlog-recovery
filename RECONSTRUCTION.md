# RECONSTRUCTION — recovering 2026-08-19 from the session log

## What happened

On 2026-08-19 about seven and a half hours of work happened in a clone at
`~/Desktop/Jay_NIW/durable-backlog-recovery`. It was never committed or pushed,
and the clone was deleted between 2026-08-21 and 2026-09-01. The only surviving
record is the local terminal session log for that day.

That log is usable because the whole day's editing went through the shell:
249 commands, of which 66 wrote files, almost all as Python heredocs containing
the literal before-and-after text of each edit.

## Method

Not hand-copying. The 249 commands were extracted in order and **replayed
against a fresh clone of d09049a** in a sandbox, with `docker`, `curl`,
`caffeinate` and friends stubbed so only the file edits took effect. The
result is a deterministic reconstruction, not an interpretation.

Two deviations from a pure replay were needed, both logged and both listed
below:

1. **Whitespace-tolerant anchor matching.** `gofmt` realigns struct tags after
   every edit, so a later command's anchor often differs from the file by
   runs of spaces or tabs. Anchors were matched exactly first, then by a
   whitespace-insensitive pattern, and only when that pattern matched exactly
   once. Every fallback was logged.
2. **Failed anchors do not abort the script.** In the original session, some
   `assert ... in ...` checks failed and the session repaired them in a later
   command. Under tolerant matching the first attempt now succeeds, so the
   repair's assert fails instead. Rather than losing the repair's other edits,
   a failed assert logs and continues.

Consequence: two edits were applied twice, and were **de-duplicated by hand**:

| Duplicate | Resolution |
|---|---|
| `Supplementary.ArtifactExcludedSamples` (cmds 0066 then 0069) | Second insertion skipped automatically; logged. |
| `RunRecord.VSLOLatency` / `VSLOError` / `VSLOBoth` (cmds 0213 then 0215) | Both applied; the duplicate block was removed by hand, keeping the later (0215) placement and the session's own `// seconds where both fired (overlap)` comment. This is the **only hand edit to reconstructed code**. |

Verification: the reconstructed tree passes `go build ./...` and
`go vet ./...`, which is the state the session itself ended in (its final
command printed `BUILD_OK`).

## Verification against the log's own read-backs (2026-09-11)

Every command in the log whose **output depends on file content** — build and
vet errors carrying line numbers, `wc`, `grep -n`, `sed -n` windows — was
compared against the same command's output in the replay. 31 such checkpoints
exist for the five reconstructed source files.

| File | Last read-back in the log | Result |
|---|---|---|
| `downstream/main.go` | cmd 0172, its own last edit: `BUILD OK` plus `301:`/`304:` line references | **Exact match**, line numbers and text |
| `consumer/main.go` | cmd 0097, a 28-line `sed -n` window | **Exact match**, character for character |
| `scripts/probe_live_only/main.go` | cmd 0228 (43-line window) and cmd 0232 (`332:44: undefined: sample`) | **Exact match** |
| `scripts/hysteresis/main.go` | cmd 0226 | **Exact match** |
| `runner/main.go` | cmd 0214 — **but the file was edited three more times afterwards (0215, 0226, 0244)** | **Cannot be verified.** See below. |

25 of the 31 checkpoints match exactly. The 6 that differ are all
`runner/main.go`, and all have the same cause: an edit whose anchor **missed in
the original** and was repaired by a later command, where whitespace-tolerant
matching made the first attempt succeed instead. Each divergence closes at the
next checkpoint (0086 and 0232 both match), so the two trees repeatedly
re-converge.

### What could not be verified, precisely

`runner/main.go` has **no read-back after its final edit**, so its end state
cannot be checked against the log at all. Two places where the first attempt
and its repair wrote *different text* were resolved in favour of the repair,
which is what the original ended with:

| Block | First attempt | Repair | Kept |
|---|---|---|---|
| `TimelinePoint.InjRate` | cmd 0202: one field with a long trailing comment | cmd 0204: a two-line comment above a bare field | **0204** |
| `RunRecord.VSLOLatency/Error/Both` | cmd 0213: `p99 2000ms`, trailing `// seconds where both fired (overlap)` | cmd 0215: `p99 ~2000ms`, no trailing comment | **0215** |

The remaining pairs (`ArtifactExcludedSamples`, the fault-window loop variables)
wrote identical text in both attempts, so the choice does not arise.

**Residual uncertainty:** at cmd 0104 the log records `runner/main.go` as 48,484
bytes / 1,539 lines; the replay at the same point gives 49,603 / 1,563. The
24-line gap is content the original was missing at that moment because its
anchors had missed, and which its repair commands added afterwards — no block
appears twice in the reconstruction, and the structure re-converges by cmd 0232.
But without a post-0244 read-back this cannot be turned into proof. Treat
`runner/main.go` as **functionally reconstructed and byte-unverified**; the
other four files are byte-verified.

## Per-file status

### Fully recovered

| File | Evidence | Size |
|---|---|---|
| `NOTES.md` | 11 edit commands, each a verbatim before/after block | +609 lines |
| `downstream/main.go` | 4 commands; the blocking-semaphore admission fix | +115 |
| `consumer/main.go` | 2 commands; limiter pacing and the suspend sentinel | +14 |
| `runner/main.go` | 45 commands | +713 |
| `scripts/probe_live_only/main.go` | 8 commands; multi-lane pacer with bounded catch-up | +152 |
| `scripts/hysteresis/main.go` | written in full by cmd 0137, then 5 edits | 318 lines |
| `scripts/report_metrics.py` | written in full by cmd 0076, then 4 edits | 122 lines |
| `scripts/rescan_stalls.py` | written in full by cmd 0071 | 76 lines |
| `scripts/run_c2.sh` | written in full by cmd 0140 | 24 lines |
| `scripts/run_anchors.sh` | cmds 0175, 0184 | 23 lines |
| `scripts/run_anchors2.sh` | cmds 0179, 0190, 0193, 0194, 0198 | 51 lines |
| `scripts/run_anchors3.sh` | cmd 0198 | 42 lines |
| `scripts/run_anchors4.sh` | cmd 0219 | 37 lines |
| `results/PHASE1C-C2C3-predictions.md` | written in full by cmd 0109, extended by cmd 0135 | 123 lines |
| `results/PHASE1B-H3H4-s50.md` | correction applied by cmd 0077 | +119 |
| `results/PHASE1B-twoclass-s25.md` | correction applied by cmd 0129 | +33 |

`docker-compose.yml` was edited 6 times but only as a runtime knob
(`SERVICE_TIME_MS`, `PROFILE`), and the edits round-trip: its final Aug 19 state
is **identical to d09049a**. Nothing to reconstruct.

### Partially recovered

| Item | What survives | What does not |
|---|---|---|
| The 36 result files | Headline metrics only, collected in `results/AUG19-run-summaries.md`: the runner's `wrote results/… tDrain=… vSLO=…` log line per run, the runner's own anchor-validity listing, and every table the session reported in its messages. | The files themselves. Timelines, per-second samples, and the full JSON bodies never appear in the log. |

### Not recovered

| Item | Why |
|---|---|
| All 36 `results/` files as files | Their contents were never printed. A filename plus a summary line is not a run record, and fabricating one would be worse than not having it. |
| 9 `*-consumer.jsonl` raw traces from Aug 19 | Never printed, and several were **0 bytes at the time** because the session filled the disk. |
| Any Aug 19 raw data in the archive | The recovered `rhc-raw-data` archive ends at 2026-08-18 12:14. Confirmed by file mtimes and by every run record's `startedAt`. |

## What this does and does not restore

**Restored:** the harness fixes, so the next campaign runs on a correct
downstream and a correct injector; the findings, so nobody re-derives them or,
worse, publishes the contaminated numbers; the registered C2/C3 predictions,
so Phase 1C can still be run as a pre-registered experiment rather than a
post-hoc one; and the two memo corrections.

**Not restored:** the measurements. Every Aug 19 anchor, hysteresis probe and
smoke run must be re-run. `STATUS.md` carries the re-run list.

One caution the session itself recorded and that survives with the data: its
last stretch of measurements, from roughly 19:20Z, was taken on a host under
its own load (1-minute load average 5.59, 15-minute 13.91, on 8 cores). The
session withdrew its pacer conclusions for that reason and stopped. The
injector-pacer default was left at `ticker` — Phase 1's behaviour — precisely
because the evidence for changing it was not trustworthy. Treat the pacer
question as open.

## Provenance of the reconstruction itself

Every reconstructed file carries a header comment naming the log and
stating the original was never committed. Commits on this branch are prefixed
`reconstruct:`. The replay log, the command dump, and the fallback log were
kept under `/tmp/aug19/` for the duration of the work; they are not committed
because they are derived from the log, which remains the source of
record.
