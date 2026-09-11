#!/usr/bin/env bash
# This file was reconstructed from the 2026-08-19 session log; original was never committed.
# See RECONSTRUCTION.md.
# Completes anchors 2 and 4. Two deviations, both recorded:
#  - replacement IDs (…-r1b) because the aborted attempts left invalid records,
#    which are retained rather than overwritten.
#  - c50 runs use -gen-tolerance 0.02. The injector delivers 98.4-98.7% at S=25
#    versus 99.2-100% at S=5 (ticker drops ticks under higher goroutine
#    residency), so the +/-1% guard is unsatisfiable in that arm. The actual
#    delivered rate is recorded per run as warmupInjectorAccuracy.
set -uo pipefail
cd "$(dirname "$0")/.."
NATS=${NATS_URL:-nats://127.0.0.1:14222}; DS=${DOWNSTREAM_URL:-http://127.0.0.1:8080}
make build >/dev/null
reconfigure() {
  sed -i.bak "s/PROFILE: \".*\"/PROFILE: \"$1\"/; s/SERVICE_TIME_MS: \".*\"/SERVICE_TIME_MS: \"$2\"/" docker-compose.yml
  rm -f docker-compose.yml.bak
  docker compose -p rhc-phase0 up -d --build downstream >/dev/null 2>&1
  sleep 10
  for i in $(seq 1 2000); do curl -s -o /dev/null -X POST "$DS/process" & done >/dev/null 2>&1
  wait; sleep 15
  echo "downstream: $(curl -s $DS/admin/capacity | tr -d '\n ')"
}
run() { # id cond arm svc rl profile tol
  echo "=== $1 (S=$4 rl=$5 profile=$6 tol=$7) ==="
  caffeinate -i ./bin/runner -condition "$2" -run-id "$1" -arm "$3" \
    -nats "$NATS" -downstream "$DS" -profile "$6" -gen-tolerance "$7" \
    -live-rate 1000 -capacity 2000 -outage 120 -service-time-ms "$4" \
    -workers 1024 -rate-limit "$5" 2>&1 | tail -3
}
echo "### anchor 4 replacement: collapsed under cliff (S=5) ###"
reconfigure cliff 5
run p1x-anchor-h3-c1-rl840-cliff-r1b P0-B c10 5 840 cliff 0.01

echo "### anchor 2: c50 safe point (S=25, graceful) ###"
reconfigure graceful 25
run p1x-anchor-c50-c1-rl380-r1b P0-B c50 25 380 graceful 0.02
run p1x-anchor-c50-c1-rl380-r2b P0-B c50 25 380 graceful 0.02

echo "### restoring graceful / S=5 ###"
reconfigure graceful 5
echo "anchors complete"
