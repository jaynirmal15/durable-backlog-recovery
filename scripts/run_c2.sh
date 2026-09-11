#!/usr/bin/env bash
# This file was reconstructed from session transcript 2026-08-19; original was never committed.
# See RECONSTRUCTION.md.
# C2 — temporary degradation (P0-C: 2000 -> 1300 @t=20 -> 2000 @t=60), arm c10.
# Predictions registered in results/PHASE1C-C2C3-predictions.md BEFORE this ran.
set -euo pipefail
cd "$(dirname "$0")/.."
NATS=${NATS_URL:-nats://127.0.0.1:14222}
DS=${DOWNSTREAM_URL:-http://127.0.0.1:8080}
RATES=${RATES:-"150 200 275 350"}
REPS=${REPS:-"r1 r2"}
make build >/dev/null
for rl in $RATES; do
  for rep in $REPS; do
    id="p1c-c2-rl${rl}-${rep}"
    if [ -f "results/${id}.json" ]; then echo "skip ${id} (exists)"; continue; fi
    echo "=== ${id} ==="
    caffeinate -i ./bin/runner -condition P0-C -run-id "${id}" -arm c10 \
      -nats "$NATS" -downstream "$DS" \
      -live-rate 1000 -capacity 2000 -outage 120 -service-time-ms 5 \
      -workers 1024 -rate-limit "${rl}" 2>&1 | tail -4
  done
done
echo "C2 grid complete"
