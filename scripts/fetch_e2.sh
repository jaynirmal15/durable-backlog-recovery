#!/bin/bash
# Fetch one E2 cell from the box without overwriting anything recomputed locally.
#
# The failure this exists to prevent happened once already in this campaign: a
# plain `rsync results/` pulled the box's pre-A4 boundary file over a local file
# that had already been recomputed under A4, and the next edit appended new runs
# to the reverted file, mixing two estimators inside one point.
#
# The box's boundary file is authoritative for the SEARCH (which rates were
# probed, and how each classified). The local one is authoritative for the
# ESTIMATOR (A4 rho, recomputed from traces the box does not keep after upload).
# So the box's copy is fetched to a .from-box sidecar and never over the local
# file; applying it is a deliberate act, not a side effect of syncing.
#
# Usage: scripts/fetch_e2.sh c50-Q500
set -euo pipefail
TAG="${1:?usage: fetch_e2.sh <tag>   e.g. c50-Q500}"
IP="$(cat /tmp/e1/ip3)"
KEY="$HOME/.ssh/rhc-ec2"
SSH="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 -i $KEY"
HOST="ubuntu@$IP"
REPO="$HOME/Jay_NIW/durable-backlog-recovery"
DEST="$REPO/results/e2/$TAG"
RAW="$HOME/Jay_NIW/rhc-raw-data/results/e2"
SRC="ubuntu@$IP:rhc/results-$TAG"

mkdir -p "$DEST/boundaries" "$RAW"

# 1. Run records. Never the boundaries/ directory.
rsync -az --include='*.json' --exclude='boundaries/***' --exclude='*' \
  -e "$SSH" "$SRC/" "$DEST/"

# 2. Traces, gzip only. A plain .jsonl beside a .gz is a partial from a run that
#    was still writing; readers prefer the .gz, but not fetching it is cleaner.
rsync -az --include='*.gz' --exclude='*' -e "$SSH" "$SRC/" "$RAW/"

# 3. The box's boundary file, to a sidecar that no reader picks up.
for f in $($SSH "$HOST" "ls ~/rhc/results-$TAG/boundaries/*.json 2>/dev/null | xargs -r -n1 basename"); do
  rsync -az -e "$SSH" "$SRC/boundaries/$f" "$DEST/boundaries/$f.from-box"
done

echo
echo "records:  $(ls "$DEST"/*.json 2>/dev/null | wc -l | tr -d ' ')"
echo "traces:   $(ls "$RAW"/${TAG%%-*}-*.gz 2>/dev/null | wc -l | tr -d ' ')"
echo "sidecars: $(ls "$DEST"/boundaries/*.from-box 2>/dev/null | wc -l | tr -d ' ')"
echo
for f in "$DEST"/boundaries/*.from-box; do
  [ -e "$f" ] || continue
  live="${f%.from-box}"
  if [ ! -e "$live" ]; then
    echo "$(basename "$live"): no local copy yet — cp the sidecar into place, then run recompute_rho.py"
  elif python3 -c "import json,sys; sys.exit(0 if 'rhoEstimator' in json.load(open('$live')) else 1)" 2>/dev/null; then
    echo "$(basename "$live"): local copy is ALREADY A4-recomputed — do NOT overwrite it with the sidecar."
    echo "  To add runs: rebuild the point from records on the as-measured estimator first,"
    echo "  then apply recompute_rho.py once over the whole file."
  else
    echo "$(basename "$live"): local copy is as-measured; the sidecar can replace it, then recompute."
  fi
done
