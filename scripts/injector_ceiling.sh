#!/usr/bin/env bash
# Check 4a: measure injector ceiling against /noop (no queue, no service time).
set -euo pipefail
cd "$(dirname "$0")/.."
DOWN="${DOWNSTREAM_URL:-http://127.0.0.1:8080}"
OUT=results/injector-ceiling
MAX_INFLIGHT="${MAX_INFLIGHT:-8192}"
mkdir -p results
rm -f "$OUT".jsonl "$OUT".log "$OUT".json

echo "== injector ceiling vs /noop maxInFlight=$MAX_INFLIGHT =="
# Ramp rates until achieved stops tracking
python3 - <<PY
import json, subprocess, time, os, signal, collections

down = "$DOWN"
max_inflight = int("$MAX_INFLIGHT")
out_base = "$OUT"
rates = [1000, 2000, 4000, 6000, 8000, 10000, 12000, 16000]
results = []
for rate in rates:
    out = f"{out_base}-{rate}.jsonl"
    log = f"{out_base}-{rate}.log"
    for p in (out, log):
        try: os.remove(p)
        except FileNotFoundError: pass
    proc = subprocess.Popen(
        ["go", "run", "./scripts/live_inject",
         "-url", down, "-path", "/noop", "-rate", str(rate),
         "-out", out, "-max-inflight", str(max_inflight)],
        stdout=open(log,"w"), stderr=subprocess.STDOUT)
    time.sleep(8)  # measure middle 5s after 2s warmup inside
    time.sleep(2)
    # sample 5s window by reading file growth
    def count_ok():
        n=0; n429=0
        try:
            with open(out) as f:
                for line in f:
                    if not line.strip(): continue
                    s=json.loads(line)
                    if s.get("status")==429: n429+=1
                    elif s.get("status")==200: n+=1
        except FileNotFoundError:
            pass
        return n, n429
    c1, d1 = count_ok()
    t0=time.time(); time.sleep(5); c2, d2 = count_ok()
    dt=time.time()-t0
    ok_rps=(c2-c1)/dt
    drop_rps=(d2-d1)/dt
    # peak from log
    peak=0
    try:
        for line in open(log):
            if "peakInFlight=" in line:
                peak=int(line.split("peakInFlight=")[1].split()[0])
    except FileNotFoundError:
        pass
    proc.send_signal(signal.SIGINT)
    try: proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
    tracking = ok_rps >= rate * 0.9
    results.append({"target": rate, "achieved_ok_rps": round(ok_rps,1),
                    "drop_rps": round(drop_rps,1), "peakInFlight": peak,
                    "tracking": tracking})
    print(f"rate={rate} achieved={ok_rps:.0f} drops/s={drop_rps:.0f} peakIF={peak} tracking={tracking}")
    if not tracking and rate >= 4000:
        # continue a couple more to confirm ceiling
        pass

# Ceiling = highest tracking rate
ceiling = 0
peak_at = 0
for r in results:
    if r["tracking"]:
        ceiling = r["target"]
        peak_at = r["peakInFlight"]
report = {"results": results, "ceiling_rps": ceiling, "peakInFlight_at_ceiling": peak_at,
          "maxInFlight_config": max_inflight}
open(f"{out_base}.json","w").write(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
PY
