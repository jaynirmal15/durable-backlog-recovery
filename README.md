# RHC Phase 0 — Recovery Harness

Disposable experimental harness: does unrestricted catch-up after an outage
damage live traffic, and does mid-drain capacity change affect the safe rate?

See [SPEC.md](SPEC.md) for the full build spec and Gate 0 criteria.

## Quick start

```bash
# 1) Downstream validation gate (no NATS) — do this first
make build
./bin/downstream &
make sweep
# expect: GATE PASSED

# 2) Full topology (NATS on host ports 14222/18222 to avoid clashing with other local NATS)
make up          # docker compose -p rhc-phase0 only
make build

# 3) Short smoke run
make smoke

# 4) Spec conditions (3× each for Gate 0)
make run-p0a
make run-p0b
make run-p0c
make run-p0d

# Static-rate sweep under P0-B (recovery-only limiter)
./bin/runner -condition P0-B -run-id p0b-rate-200 -nats nats://127.0.0.1:14222 -rate-limit 200
./bin/runner -condition P0-B -run-id p0b-rate-400 -nats nats://127.0.0.1:14222 -rate-limit 400
./bin/runner -condition P0-B -run-id p0b-rate-800 -nats nats://127.0.0.1:14222 -rate-limit 800
./bin/runner -condition P0-B -run-id p0b-rate-1600 -nats nats://127.0.0.1:14222 -rate-limit 1600
```

Binaries: `downstream`, `producer`, `consumer`, `runner` in `./bin/`.
Results: JSON run records + consumer JSONL under `results/`.

NATS from the host: `nats://127.0.0.1:14222` (monitoring `http://127.0.0.1:18222`).
Do not use `:4222` — that may belong to another local stack.

## Layout

```
downstream/   # capacity-model HTTP service (validate first)
producer/     # constant-rate JetStream publisher (X-Pub-Ms header)
consumer/     # unrestricted pull consumer; live vs recovery samples
runner/       # orchestrates one experiment run
scripts/load_sweep/  # downstream knee validation
```
