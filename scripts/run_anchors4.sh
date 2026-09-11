#!/usr/bin/env bash
# This file was reconstructed from session transcript 2026-08-19; original was never committed.
# See RECONSTRUCTION.md.
# Post-injector-fix anchors.
#  - c50 safe anchor (closes the gap left by the ticker under-delivery)
#  - c10 safe anchor RE-RUN, to test whether the injector fix moves a known
#    clean point. If it does, the clean/contaminated split needs revisiting
#    before committing to the rho* sweep.
set -uo pipefail
cd "$(dirname "$0")/.."
NATS=${NATS_URL:-nats://127.0.0.1:14222}; DS=${DOWNSTREAM_URL:-http://127.0.0.1:8080}
make build >/dev/null
reconfigure() {
  sed -i.bak "s/SERVICE_TIME_MS: \".*\"/SERVICE_TIME_MS: \"$1\"/" docker-compose.yml
  rm -f docker-compose.yml.bak
  docker compose -p rhc-phase0 up -d --build downstream >/dev/null 2>&1
  sleep 10
  for i in $(seq 1 2000); do curl -s -o /dev/null -X POST "$DS/process" & done >/dev/null 2>&1
  wait; sleep 15
  echo "downstream: $(curl -s $DS/admin/capacity | tr -d '\n ')"
}
run() { # id cond arm svc rl
  if [ -f "results/$1.json" ] && ! grep -q '"invalid": *true' "results/$1.json"; then
    echo "skip $1 (valid)"; return 0; fi
  echo "=== $1 (S=$4 rl=$5) ==="
  caffeinate -i ./bin/runner -condition "$2" -run-id "$1" -arm "$3" \
    -nats "$NATS" -downstream "$DS" \
    -live-rate 1000 -capacity 2000 -outage 120 -service-time-ms "$4" \
    -workers 1024 -rate-limit "$5" 2>&1 | tail -3
  return 0
}
echo "### c50 safe anchor (S=25) ###"
for rep in r1c r2c; do run "p1x-anchor-c50-c1-rl380-${rep}" P0-B c50 25 380; done
echo "### c10 safe anchor re-run, post injector fix (S=5) ###"
reconfigure 5
for rep in r1 r2; do run "p1x-anchor2-c0-rl840-${rep}" P0-A c10 5 840; done
echo "anchors4 complete"
