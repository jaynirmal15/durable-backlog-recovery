#!/usr/bin/env bash
# This file was reconstructed from the 2026-08-19 session log; original was never committed.
# See RECONSTRUCTION.md.
# Post-fix anchor measurements: quantify the offset introduced by replacing the
# graceful spin-wait admission with a blocking semaphore (NOTES.md 2026-08-19).
# Compare against the pre-fix runs of the same points.
set -euo pipefail
cd "$(dirname "$0")/.."
NATS=${NATS_URL:-nats://127.0.0.1:14222}
DS=${DOWNSTREAM_URL:-http://127.0.0.1:8080}
make build >/dev/null
run() { # id condition arm svc rl
  local id=$1 cond=$2 arm=$3 svc=$4 rl=$5
  if [ -f "results/${id}.json" ]; then echo "skip ${id}"; return; fi
  echo "=== ${id} (${cond} arm=${arm} S=${svc} rl=${rl}) ==="
  caffeinate -i ./bin/runner -condition "$cond" -run-id "$id" -arm "$arm" \
    -nats "$NATS" -downstream "$DS" \
    -live-rate 1000 -capacity 2000 -outage 120 -service-time-ms "$svc" \
    -workers 1024 -rate-limit "$rl" 2>&1 | tail -3
}
for rep in r1 r2; do run "p1x-anchor-c0-rl840-${rep}"    P0-A c10 5 840; done
for rep in r1 r2; do run "p1x-anchor-h3-c1-rl840-${rep}" P0-B c10 5 840; done
echo "S=5 anchors complete"
