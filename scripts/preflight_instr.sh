#!/usr/bin/env bash
# Preflight Check 1/3: live+recovery concurrency with producer ALWAYS running.
# Outage-equivalent backlog build 300s @ λ_L, then drain with live injector + consumer.
set -euo pipefail
cd "$(dirname "$0")/.."

NATS="${NATS_URL:-nats://127.0.0.1:14222}"
DOWN="${DOWNSTREAM_URL:-http://127.0.0.1:8080}"
OUT="results/preflight-instr"
OUTAGE_SECS="${1:-300}"   # backlog build = outage duration
DRAIN_SECS="${2:-300}"    # min drain observation window
LIVE=1000
CAP=2000
WORKERS=1024
MAX_INFLIGHT="${MAX_INFLIGHT:-4096}"

mkdir -p results
rm -f "${OUT}"-*.jsonl "${OUT}"-*.log "${OUT}-report.json"

echo "== preflight: reset (producer stays up for entire test) =="
curl -sf -X POST "$DOWN/admin/capacity?rate=$CAP" >/dev/null
go run ./scripts/reset_stream -nats "$NATS"

echo "== outage/build backlog ${OUTAGE_SECS}s @ ${LIVE}/s (consumer off, producer ON) =="
NATS_URL="$NATS" SUBJECT=events.orders STREAM=EVENTS RATE_PER_SEC=$LIVE \
  ./bin/producer >"${OUT}-producer.log" 2>&1 &
PID_PROD=$!
sleep "$OUTAGE_SECS"

EPOCH=$(python3 -c 'import time; print(int(time.time()*1000))')
echo "== restore epoch=$EPOCH; start consumer+live injector; producer STILL RUNNING =="
NATS_URL="$NATS" STREAM=EVENTS SUBJECT=events.orders DURABLE=rhc-consumer \
  DOWNSTREAM_URL="$DOWN" WORKERS=$WORKERS BATCH=256 RESTORE_EPOCH_MS=$EPOCH \
  SAMPLES_OUT="${OUT}-consumer.jsonl" \
  ./bin/consumer >"${OUT}-consumer.log" 2>&1 &
PID_CONS=$!

go run ./scripts/live_inject -url "$DOWN" -rate $LIVE -out "${OUT}-live.jsonl" \
  -max-inflight "$MAX_INFLIGHT" -path /process \
  >"${OUT}-inject.log" 2>&1 &
PID_INJ=$!

# Run until DRAIN_SECS elapsed (caller may analyze recoveryRemaining from samples).
sleep "$DRAIN_SECS"

kill -INT $PID_CONS $PID_INJ $PID_PROD 2>/dev/null || true
sleep 2
kill -9 $PID_CONS $PID_INJ $PID_PROD 2>/dev/null || true
wait 2>/dev/null || true

cat "${OUT}-consumer.jsonl" "${OUT}-live.jsonl" > "${OUT}-all.jsonl"

python3 ./scripts/analyze_preflight.py \
  --samples "${OUT}-all.jsonl" \
  --inject-log "${OUT}-inject.log" \
  --backlog-at-restore $((LIVE * OUTAGE_SECS)) \
  --duration "$DRAIN_SECS" \
  --target-live "$LIVE" \
  --capacity "$CAP" \
  --out "${OUT}-report.json"

echo "== report =="
cat "${OUT}-report.json"
echo "== inject peaks =="
grep peakInFlight "${OUT}-inject.log" | tail -n 8 || true
