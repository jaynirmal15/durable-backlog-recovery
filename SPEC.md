# PHASE 0 BUILD SPEC — RHC Recovery Harness

> **How to use this:** save as `SPEC.md` at the repo root, open in Cursor, and
> prompt: *"Read SPEC.md and implement Phase 0. Start with the downstream
> service and validate it in isolation before wiring anything else."*
>
> Build in the order given. Do not skip ahead — the downstream service is the
> foundation and everything else is meaningless if its capacity model is wrong.

---

## 0. What this is

A disposable experimental harness to answer **one question**: when a durable
event-stream consumer recovers from an outage and drains its backlog at full
speed, does that measurably damage live traffic — and does changing the
downstream's capacity mid-drain change the safe recovery rate?

If yes, a research project follows. If no, the project stops. That is the entire
purpose of this code.

**This is throwaway scaffolding.** It will be rebuilt properly in Phase 1 once we
know what we actually need. Optimise for getting correct measurements quickly,
not for architecture.

### Do NOT build

- Any recovery controller or rate limiter (that is Phase 3)
- Any baseline policies (that is Phase 2)
- A broker abstraction layer or plugin interface — NATS JetStream only, hardcoded
- Config frameworks, DI containers, or interface hierarchies
- A web UI or dashboard
- Retry logic, dead-letter handling, or exactly-once semantics
- Kafka support of any kind

Every one of these is scope creep that turns a two-week spike into two months.

---

## 1. Stack

- **Go** (1.22+) for all services
- **NATS JetStream** for the durable stream
- **Docker Compose** for the topology
- Plain JSON / JSONL for output — no database, no Prometheus required
- Standard library HTTP; `github.com/nats-io/nats.go` and its `jetstream` package

Four binaries: `downstream`, `producer`, `consumer`, `runner`.

```
rhc-phase0/
  downstream/main.go
  producer/main.go
  consumer/main.go
  runner/main.go
  docker-compose.yml
  results/
  SPEC.md
```

---

## 2. Downstream service — BUILD AND VALIDATE THIS FIRST

The crux of the whole harness. Everything depends on it having a **known**
capacity that can be **changed at runtime**, with latency that degrades
predictably as that capacity is approached.

### Capacity model

Use a bounded worker pool in front of a queue. By Little's Law, sustaining `C`
requests/sec at fixed service time `S` requires `C × S` concurrent servers:

```
concurrency = ceil(capacity_rps × serviceTime_seconds)
```

So `capacity=2000 rps` with `serviceTime=5ms` → 10 workers. Changing capacity at
runtime means resizing the worker pool. This gives natural latency growth from
queueing delay as utilisation → 1, which is exactly the knee we need.

Add ~15% Gaussian jitter to service time so the distribution isn't degenerate.

### Two saturation profiles

- `graceful` — large queue (≈50× concurrency). Latency degrades smoothly; errors
  only from request timeout.
- `cliff` — small queue (≈2× concurrency). Returns 503 once the queue is full.

Profile is set at startup via env var. Both must be implemented; Phase 0 runs
use `graceful` unless a condition says otherwise.

### Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /process` | The work request. Consumers call this. |
| `POST /admin/capacity?rate=N` | Change capacity at runtime. **Harness only.** |
| `GET /admin/capacity` | Current true capacity and concurrency |
| `GET /admin/stats` | queued, served, rejected, timedOut, trueCapacity |
| `GET /healthz` | Liveness |

**Critical:** true capacity is exposed *only* on `/admin/*`. Consumers must never
read it. This separation matters later — the controller will have to infer
capacity from symptoms, and if the code ever lets it peek, the whole result is
invalid.

Do not set HTTP read/write timeouts on the server. The queue must be the only
limiter, or you'll measure the timeout instead of the saturation behaviour.

### Env vars

`CAPACITY` (default 2000), `SERVICE_TIME_MS` (5), `TIMEOUT_MS` (2000),
`PROFILE` (graceful), `PORT` (8080).

### VALIDATION GATE — do this before writing anything else

Write a standalone load-sweep script. Point it at the downstream with no NATS
involved. Sweep offered load from 20% to 150% of configured capacity and plot
p50/p95/p99 latency and error rate.

**You must see:**
1. Flat, low latency well below capacity
2. A clear knee as utilisation approaches 1
3. Errors appearing above saturation
4. Changing capacity via the admin endpoint visibly moves the knee

If the knee is mushy, drifts between runs, or doesn't move when you change
capacity, **fix this before proceeding**. Every downstream measurement in the
project depends on it.

---

## 3. Producer

Publishes to subject `events.orders` on stream `EVENTS` at a configurable
constant rate.

**Every message must carry a header `X-Pub-Ms` with the publish time in
Unix milliseconds.** This is how live and recovery work are told apart later.
Without it the harness is useless.

Payload can be a fixed small blob — content is irrelevant.

Runs continuously for the whole experiment, including during the consumer
outage. That's what builds the backlog.

Env: `NATS_URL`, `SUBJECT`, `RATE_PER_SEC`.

### Stream config

`EVENTS`, file storage, work-queue or limits retention, max age generous enough
that nothing expires mid-run. Create it idempotently at startup.

---

## 4. Consumer

Durable **pull** consumer with a fixed worker pool. Phase 0 is deliberately
**unrestricted** — no rate limiting, no controller. We are measuring what
uncontrolled catch-up does.

For each message: read `X-Pub-Ms`, classify as `recovery` if published before the
restoration epoch and `live` otherwise, call `POST /process`, record a sample,
then ack.

```go
type Sample struct {
    TS        int64  `json:"ts"`
    Class     string `json:"class"`      // "live" | "recovery"
    LatencyMs int64  `json:"latency_ms"`
    Status    int    `json:"status"`
    AgeMs     int64  `json:"age_ms"`     // now - publish time
}
```

Write JSONL to `/results/<run-id>-consumer.jsonl`, flushing every couple of
seconds so a killed run still yields data.

**Separating live from recovery latency is the single most important measurement
here.** V_SLO is defined over *live* traffic only. If the harness reports one
blended latency number, Phase 0 cannot answer Gate 0 item 3 and the whole spike
is wasted.

Ack every message regardless of downstream status. Retries would confound the
backlog count, and Phase 0 isn't about delivery semantics.

The restoration epoch comes from env `RESTORE_EPOCH_MS`, set by the runner when
it restarts consumers.

Env: `NATS_URL`, `STREAM`, `SUBJECT`, `DURABLE`, `DOWNSTREAM_URL`, `WORKERS`
(default 64), `BATCH` (256), `RESTORE_EPOCH_MS`, `SAMPLES_OUT`.

---

## 5. Runner — orchestration

Drives one run end to end and writes the record. This is what you invoke.

### Sequence

1. Reset state: delete and recreate the stream and durable consumer; reset the
   downstream to nominal capacity
2. Start live injector at λ_L; warm up (30s); verify injector-live healthy
3. Start producer; accumulate backlog for outage duration (no consumer process;
   injector continues)
4. Record backlog at restoration; **stop the producer**
5. Start consumers with `RESTORE_EPOCH_MS = now` (injector continues through T_full)
6. Apply the capacity schedule for this condition (see §6)
7. Poll until recoveryRemaining = 0 **and** injector-live returns to healthy for
   a stabilisation window
8. Write the run record

Scoping: live and recovery use independent paths to a shared downstream (API +
backlog consumer). See NOTES.md.

### Sampling loop

Every 1s throughout, record: backlog depth (JetStream consumer pending), true
downstream capacity, offered rate, downstream queued/served/rejected/timedOut,
and live vs recovery p99 computed over a trailing window.

### Run record

One JSON file per run, `results/<run-id>.json`:

```json
{
  "runId": "p0a-001",
  "condition": "P0-A",
  "gitCommit": "abc1234",
  "gitDirty": false,
  "startedAt": "...",
  "params": {
    "liveRatePerSec": 1400,
    "nominalCapacity": 2000,
    "outageSeconds": 120,
    "serviceTimeMs": 5,
    "profile": "graceful",
    "workers": 64,
    "sloP99Ms": 250,
    "sloErrorRate": 0.01
  },
  "backlogAtRestore": 168000,
  "restoreEpochMs": 1739284801234,
  "capacitySchedule": [{"atSec": 0, "rate": 2000}],
  "timeline": [ { "tSec": 0, "backlog": 168000, "trueCapacity": 2000,
                  "liveP99Ms": 42, "recoveryP99Ms": 380, "errorRate": 0.0 } ],
  "tDrainSec": 94.2,
  "tFullSec": 121.8,
  "vSLO": 0.31,
  "peakOfferedRate": 5200,
  "amplification": 3.7
}
```

**Record the git commit and dirty flag from the very first run.** This was the
one reproducibility gap in a previous harness and it costs two lines now.

---

## 6. Conditions

Three runs each. Capacity schedules are applied relative to consumer restoration
(t=0).

| ID | Schedule | Tests |
|---|---|---|
| **P0-A** | Constant 100% | Baseline: does unrestricted drain hurt live traffic at all? |
| **P0-B** | 100%, then 70% at t=20s | Does a mid-drain capacity drop change the safe rate? |
| **P0-C** | 100%, 65% at t=20s, 100% at t=60s | Does headroom return, and is it reclaimable? |
| **P0-D** | Set capacity **below** live arrival rate at t=20s, restore at t=90s | Infeasible recovery: what happens when there is no headroom at all? |

Suggested starting parameters — tune during the downstream validation sweep:

- Nominal capacity 2000 rps, service time 5ms, graceful profile
- Live rate 1400 rps (70% of nominal)
- Outage 120s → backlog ≈ 168k messages
- SLO: live p99 ≤ 250ms, error rate ≤ 1%
- P0-D reduced capacity: 1200 rps (below the 1400 live rate)

### Plus: static-rate sweep

Separately, run a crude fixed-rate limiter on the consumer at several rates
(e.g. 200, 400, 800, 1600 rps of recovery work) under P0-B. This is H3/H4 in
miniature — it should show nominal-tuned rates overloading after the capacity
drop, and conservative rates staying safe but draining slowly.

This is the only place Phase 0 touches rate limiting, and it is a hardcoded
constant, not a controller.

---

## 7. Gate 0 — the point of all this

After the runs, produce a one-page memo answering each item with data:

1. **Steady state reproducibly healthy** across runs?
2. **Outage produces deterministic backlog** — is `backlogAtRestore` consistent
   for the same outage duration?
3. **Unrestricted catch-up measurably degrades live traffic?** Compare live p99
   and error rate during drain against the pre-outage baseline.
4. **Changing capacity mid-drain materially changes the safe recovery rate?**
   Compare P0-B and P0-C against P0-A.
5. **Static rates show the predicted safety/speed tradeoff?** From the sweep.

**If 3, 4, or 5 fail, the project stops or is reformulated.** These are the
paper's motivation. No amount of controller work rescues a problem that doesn't
reproduce. Report that outcome honestly rather than tuning parameters until the
effect appears — if the effect only exists at extreme settings, that is itself
the finding.

Also extract for Gate 1: observed downstream settling time (which sets the
stabilisation window W), sensible backlog values expressed in *seconds of
equivalent live traffic*, and the achievable T_full range.

---

## 8. Reminders

- Everything in `results/` is data. Never hand-edit it.
- Reset stream and consumer state between runs. A leftover durable consumer will
  silently corrupt the next run's backlog count.
- If a run fails partway, discard it and note why. Do not salvage partial runs
  into the dataset.
- Keep a `NOTES.md` of surprises, dead ends, and parameter changes. That file
  becomes the Phase 1 design input and the paper's methods section.
