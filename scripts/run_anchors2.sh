#!/usr/bin/env bash
# This file was reconstructed from the 2026-08-19 session log; original was never committed.
# See RECONSTRUCTION.md.
# Anchors 3 and 4: collapsed point under PROFILE=cliff (S=5), and the c50 safe
# anchor (S=25). Each requires a downstream reconfigure, so they are separate
# from run_anchors.sh. Compose is left on graceful/S=5 at the end.
set -euo pipefail
cd "$(dirname "$0")/.."
NATS=${NATS_URL:-nats://127.0.0.1:14222}
DS=${DOWNSTREAM_URL:-http://127.0.0.1:8080}
make build >/dev/null
reconfigure() { # profile svc
  sed -i.bak "s/PROFILE: \".*\"/PROFILE: \"$1\"/; s/SERVICE_TIME_MS: \".*\"/SERVICE_TIME_MS: \"$2\"/" docker-compose.yml
  rm -f docker-compose.yml.bak
  docker compose -p rhc-phase0 up -d --build downstream >/dev/null 2>&1
  # Settle after rebuild. Starting a run ~6s after `up --build` made the very
  # first warm-up read 95.3% of target and the generator self-check refused it.
  # Warm the container with throwaway load, then idle before measuring.
  sleep 10
  for i in $(seq 1 2000); do curl -s -o /dev/null -X POST "$DS/process" & done >/dev/null 2>&1
  wait
  sleep 15
  echo "downstream: $(curl -s $DS/admin/capacity | tr -d '\n ')"
}
run() { # id condition arm svc rl profile
  local id=$1 cond=$2 arm=$3 svc=$4 rl=$5 prof=$6
  if [ -f "results/${id}.json" ] && ! grep -q '"invalid": *true' "results/${id}.json"; then
    echo "skip ${id} (valid record exists)"; return
  fi
  echo "=== ${id} (${cond} arm=${arm} S=${svc} rl=${rl} profile=${prof}) ==="
  set +e
  caffeinate -i ./bin/runner -condition "$cond" -run-id "$id" -arm "$arm" \
    -nats "$NATS" -downstream "$DS" -profile "$prof" \
    -live-rate 1000 -capacity 2000 -outage 120 -service-time-ms "$svc" \
    -workers 1024 -rate-limit "$rl" 2>&1 | tail -4
  local rc=${PIPESTATUS[0]}
  set -e
  [ "$rc" -ne 0 ] && echo "!! ${id} did not complete (rc=$rc) — continuing"
  return 0
}
echo "### anchor 4: collapsed point under cliff (S=5) ###"
reconfigure cliff 5
for rep in r1 r2; do run "p1x-anchor-h3-c1-rl840-cliff-${rep}" P0-B c10 5 840 cliff; done

echo "### anchor 2: c50 safe point (S=25, graceful) ###"
reconfigure graceful 25
for rep in r1 r2; do run "p1x-anchor-c50-c1-rl380-${rep}" P0-B c50 25 380 graceful; done

echo "### restoring graceful / S=5 ###"
reconfigure graceful 5
echo "anchors 2+4 complete"
