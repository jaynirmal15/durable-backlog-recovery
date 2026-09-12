# E1B — pre-run plan

**Written and committed BEFORE any run in this batch.** Its purpose is to fix the
classification threshold and the success criteria while the answer is still
unknown, because the question in item 1 is the *shape of a distribution* and a
threshold chosen after seeing twelve points can produce whichever shape is
wanted.

## Item 1 — replicate the bimodality

Two points, n = 12 each, on the same instance type and the same harness commit
as E1 (`026be6242d26`), spaced 60 s, default queue cap, `lanes` injector.

| | |
|---|---|
| c10 / C0 | `rl = 825`, the last SAFE point of boundary 1 |
| c50 / C0 | `rl = 975`, the last SAFE point of boundary 3 |

### Classification threshold, fixed now

> **A run is DEEP-QUEUE if its `drainQueueDepthMean` ≥ 50 requests, and SHALLOW
> otherwise.**

Chosen on three grounds, none of which depends on the new data:

1. **It is a queueing-delay threshold, and it is automatically matched across
   the two arms.** Implied queueing delay is `qMean / C_d`, because the service
   rate is `concurrency / S = C_d`. At `C_d = 2000` both arms give
   `delay_ms = qMean × 0.5`, so 50 requests is **25 ms of queueing delay in both
   arms** — no arm-specific constant is needed.
2. **25 ms is 10% of the 250 ms SLO**, so a DEEP run is one that has spent a
   tenth of its latency budget waiting, while still passing.
3. **It sits well clear of every non-last SAFE point already measured**: the
   deepest are 4.27 (c10/C0 rl=820) and 7.95 (c50/C0 rl=970), both about an
   order of magnitude below.

### What each outcome means, fixed now

- **Bimodal with a stable minority fraction** — both DEEP and SHALLOW runs occur,
  and the DEEP fraction has a 95% confidence interval excluding 0 and 1. The
  operating point is genuinely two-state.
- **Unimodal with one outlier** — 11 or 12 of 12 fall in one class. The n=3
  observation was a tail draw, not structure.
- **Unimodal deep** — all 12 DEEP. The point is uniformly degraded and the n=3
  scatter was sampling within one mode.

Reported regardless: per-run `drainQueueDepthMean` and `drainLiveP99Ms`, the
DEEP fraction with a binomial confidence interval, and a dip test of the
distribution's shape that does not use the threshold at all.

### The vSLO question

Every run is checked against the pre-registered classification (`vSLO ≤ 0.01` in
all repetitions is SAFE). **A point that classifies SAFE at n = 3 and non-SAFE at
n = 12 changes boundary 1**, so this is reported prominently either way, and the
n = 12 result supersedes the n = 3 one for that point if they disagree.

## Item 2 — complete the 2×2

`c10 / C1` at `rl = 240` and `rl = 255`, n = 3 each. Both are below the existing
last SAFE point (275), so **the boundary interval [275, 280] cannot change**;
these add resolution inside the safe range so the leading-indicator question can
be asked at that condition at all. It currently has only two SAFE points.

## Harness version

All runs use commit **`026be6242d26`**, the exact commit every E1 run used. Later
commits touched `downstream/main.go` (optional arrival capture) and the analysis
scripts. Even though the capture is off by default, replicating a distribution
on a different binary would confound the thing being measured.
