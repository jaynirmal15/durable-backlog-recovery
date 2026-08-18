#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
from collections import defaultdict

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--samples', required=True)
    ap.add_argument('--inject-log', default='')
    ap.add_argument('--backlog-at-restore', type=int, default=0)
    ap.add_argument('--duration', type=float, default=300)
    ap.add_argument('--target-live', type=float, default=1000)
    ap.add_argument('--capacity', type=float, default=2000)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    live_ts, rec_ts = [], []
    status = defaultdict(int)
    live_http = 0
    n429 = 0
    n = 0
    by = defaultdict(lambda: {'live': 0, 'rec': 0, 'live429': 0, 'live_ok': 0})

    with open(args.samples) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                s = json.loads(line)
            except Exception:
                continue
            n += 1
            st = s.get('status') or 0
            status[st] += 1
            cls = s.get('class')
            ts = s.get('ts') or 0
            sec = ts // 1000
            if cls == 'live':
                live_ts.append(ts)
                by[sec]['live'] += 1
                if st == 429:
                    n429 += 1
                    by[sec]['live429'] += 1
                else:
                    live_http += 1
                    if st == 200:
                        by[sec]['live_ok'] += 1
            elif cls == 'recovery':
                rec_ts.append(ts)
                by[sec]['rec'] += 1

    def max_gap(ts):
        if len(ts) < 2:
            return None
        ts = sorted(ts)
        return max((ts[i] - ts[i - 1]) / 1000.0 for i in range(1, len(ts)))

    live_ts.sort()
    rec_ts.sort()

    def trim(ts, edge=5000):
        if len(ts) < 3:
            return ts
        lo, hi = ts[0] + edge, ts[-1] - edge
        mid = [t for t in ts if lo <= t <= hi]
        return mid or ts

    max_live_gap = max_gap(trim(live_ts))
    max_rec_gap = max_gap(trim(rec_ts))

    secs = sorted(by)
    concurrent = [s for s in secs if (by[s]['live'] - by[s]['live429']) > 0 and by[s]['rec'] > 0]
    best_len, best = 0, None
    i = 0
    while i < len(concurrent):
        j = i
        while j + 1 < len(concurrent) and concurrent[j + 1] == concurrent[j] + 1:
            j += 1
        length = concurrent[j] - concurrent[i] + 1
        if length > best_len:
            best_len = length
            best = (concurrent[i], concurrent[j])
        i = j + 1

    # recoveryRemaining series
    backlog = args.backlog_at_restore
    rec_acked = 0
    t_drain = None
    # order recovery by ts
    rec_by_sec = defaultdict(int)
    for t in rec_ts:
        rec_by_sec[t // 1000] += 1
    if secs and backlog:
        start = secs[0]
        for s in range(start, secs[-1] + 1):
            rec_acked += rec_by_sec.get(s, 0)
            rem = max(0, backlog - rec_acked)
            if rem == 0 and t_drain is None:
                t_drain = s - start
                break

    peak_live = max((by[s]['live'] - by[s]['live429']) for s in secs) if secs else 0
    peak_rec = max(by[s]['rec'] for s in secs) if secs else 0
    peak_combined = max((by[s]['live'] - by[s]['live429'] + by[s]['rec']) for s in secs) if secs else 0

    # average live rps over concurrent window (excl 429)
    avg_live = 0.0
    if best_len and best:
        avg_live = sum(by[s]['live'] - by[s]['live429'] for s in range(best[0], best[1] + 1)) / best_len

    live_total = n429 + live_http
    rate_429 = (n429 / live_total) if live_total else 0

    rec_span = (rec_ts[-1] - rec_ts[0]) / 1000.0 if len(rec_ts) > 1 else 0
    # Continuous if gaps ok AND recovery present for most of the drain until T_drain or duration
    target_span = min(args.duration, t_drain if t_drain is not None else args.duration)
    rec_continuous = (
        max_rec_gap is not None and max_rec_gap <= 2.0 and len(rec_ts) > 0
        and rec_span >= max(30.0, target_span * 0.8)
    )

    # peakInFlight from inject log
    peak_if = 0
    if args.inject_log and Path(args.inject_log).exists():
        for line in open(args.inject_log):
            if 'peakInFlight=' in line:
                try:
                    peak_if = int(line.split('peakInFlight=')[1].split()[0])
                except Exception:
                    pass

    report = {
        'check1': {
            'max_recovery_gap_s': max_rec_gap,
            'max_live_gap_s': max_live_gap,
            'recovery_sampling_continuous': rec_continuous,
            'recovery_samples': len(rec_ts),
            'live_samples_excl_429': live_http,
            'live_samples_incl_429': live_total,
            'total_samples': n,
            'recovery_span_s': rec_span,
            'live_span_s': (live_ts[-1] - live_ts[0]) / 1000.0 if len(live_ts) > 1 else 0,
            'concurrent_longest_s': best_len,
            'concurrent_range': best,
            't_drain_s_est': t_drain,
            'backlog_at_restore': backlog,
            'pass': bool(max_rec_gap is not None and max_rec_gap <= 2.0 and rec_continuous and best_len >= 30),
        },
        'check3': {
            'live_429_count': n429,
            'live_429_rate': rate_429,
            'avg_live_rps_excl_429_in_concurrent': round(avg_live, 1),
            'peak_live_rps_excl_429': peak_live,
            'target_live_rps': args.target_live,
            'peak_recovery_rps': peak_rec,
            'peak_combined_rps_excl_429': peak_combined,
            'capacity': args.capacity,
            'peakInFlight': peak_if,
            'status_counts': dict(status),
            'pass': rate_429 < 0.001 and avg_live >= args.target_live * 0.85,
        },
    }
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if not report['check1']['pass'] or not report['check3']['pass']:
        sys.exit(2)

if __name__ == '__main__':
    main()
