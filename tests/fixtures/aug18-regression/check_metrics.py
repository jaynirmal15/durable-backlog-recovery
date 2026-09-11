#!/usr/bin/env python3
"""Regression check: the reconstructed metrics path against the pre-2026-08-19 corpus.

The 2026-08-19 harness work was recovered from a session log rather than from a
commit, and `runner/main.go` is the one file whose end state could not be
verified byte-for-byte (RECONSTRUCTION.md). Output format and record schema were
verified; **arithmetic was not**. A changed computation would pass every one of
those checks and still silently move every number in the paper.

So this recomputes the sample-derived metrics straight from the raw per-request
traces, using the formulas in the reconstructed `computeSupplementary` /
`fillLiveSupp`, and compares them against what the ORIGINAL pre-Aug-19 runner
wrote into the committed run records. Agreement means the reconstruction did not
change the arithmetic.

Two details make the comparison apples-to-apples:

  * Artifact exclusion (`excl`) did not exist before Aug 19, so it is passed
    empty here. The reconstructed code path with an empty exclusion list is
    exactly the old code path.
  * The old `vSLO` had no stall exclusion, so it is compared against the
    timeline recomputation without exclusion, which is what `vSLO_raw` means in
    the new records.

Usage:
  python3 tests/fixtures/aug18-regression/check_metrics.py
  python3 tests/fixtures/aug18-regression/check_metrics.py --raw-dir /path/to/rhc-raw-data/results

Exits non-zero if any field disagrees beyond tolerance. Skips with exit 0 and a
clear message if the raw traces are not present, since they live outside the
repository (see results/RAW-DATA.md).
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DEFAULT_RAW = os.path.join(os.path.dirname(REPO), 'rhc-raw-data', 'results')

# Tolerances. Percentiles and queue depth are exact integers or exact means, so
# they must match exactly. Goodput divides by a wall clock derived from sample
# timestamps and is compared relatively.
# Tolerances split into two groups, for a reason worth stating.
#
# Timeline-derived fields (tDrainSec, vSLO, drainQueueDepthMean) are recomputed
# from the record's own timeline, so there is no sample-set boundary and they
# must match EXACTLY. They do.
#
# Sample-derived fields are recomputed from the trace, where the exact set the
# runner held in memory cannot be reproduced to the sample: the boundary is
# fuzzy by up to one flush interval (see recompute()). The residual shows up as
# at most one rank in an integer percentile and a fraction of a percent in a
# rate. These tolerances bound that, and are far tighter than any difference a
# changed formula would produce -- a changed formula does not land within 0.1%.
EXACT_FIELDS = ['tDrainSec', 'vSLO', 'drainQueueDepthMean']
RANGE_FIELDS = ['drainLiveP50Ms', 'drainLiveP99Ms', 'drainGoodputRpsMean',
                'drainTimeoutRate', 'G_norm']
# Slack on the range endpoints.
#
# p50, p99 and timeoutRate are reproduced inside the bracket on every run, so
# they get float slack only. Goodput (and G_norm, which is goodput / G_ceil)
# needs a little more: it is `good / wall`, where `wall` is the span between the
# FIRST and LAST qualifying sample inside the window. A single sample at either
# edge moves both numerator and denominator, so the value is quantised at a
# level finer than the 100 ms bracket can resolve. Measured residual across the
# 12-run corpus: 0.0002% on one run and 0.048% on another, both at collapsed
# operating points where qualifying samples are sparse and irregular.
#
# 0.1% bounds that and is still far tighter than any formula change could hide:
# the earlier window bug in this very script showed up as an 8x error, not a
# fourth-decimal one.
RANGE_EPS_REL = 1e-6
GOODPUT_EPS_REL = 1e-3
G_CEIL = 998.0

# The runner's post-restore sample set does not begin exactly at the restore
# epoch. tailSamples follows the trace by byte offset every 200 ms and the
# injector flushes its buffer every 500 ms, so at the moment `samples = nil`
# runs, some samples written before the restore are still unread and get counted
# (set starts EARLY), while some written after it have already been read and get
# discarded (set starts LATE). Which way, and by how much, is timing and depends
# on the run: measured directly, one collapsed run reproduces its committed
# goodput at 0 ms and another needs the opposite sign.
#
# Rather than pick a lag and call the residual tolerance, sample-derived fields
# are computed across the whole plausible window and the committed value must
# fall inside the resulting range. That is a sharper test than a loose
# tolerance: it fails if the value is unreachable under ANY admissible boundary.
FLUSH_LAGS_MS = list(range(-800, 801, 100))


def open_trace(raw_dir, run_id):
    base = os.path.join(raw_dir, '%s-consumer.jsonl' % run_id)
    if os.path.exists(base):
        return open(base, 'rb')
    if os.path.exists(base + '.gz'):
        return gzip.open(base + '.gz', 'rb')
    return None


def pct(xs, p):
    """Percentile exactly as runner/main.go pct(): index int((n-1)*p), no interpolation."""
    if not xs:
        return 0.0
    return xs[int((len(xs) - 1) * p)]


def fill_live_supp(samples, t0, t1, slo_p99):
    """Mirror of fillLiveSupp() with an empty exclusion list.

    Live means injector-direct: class == "live" AND age_ms == 0. Status 429 is an
    injector client-side drop and is excluded from all accounting.
    """
    lats = []
    ok_slo = total = timeouts = good = 0
    min_ts = 0
    max_ts = 0
    for s in samples:
        if s['class'] != 'live' or s['age_ms'] != 0:
            continue
        ts = s['ts']
        if ts < t0 or ts > t1:
            continue
        if s['status'] == 429:
            continue
        total += 1
        if min_ts == 0 or ts < min_ts:
            min_ts = ts
        if ts > max_ts:
            max_ts = ts
        if s['status'] == 504:
            timeouts += 1
        if s['status'] == 200:
            lat = float(s['latency_ms'])
            lats.append(lat)
            if lat <= slo_p99:
                ok_slo += 1
                good += 1
    lats.sort()
    out = {
        'p50': pct(lats, 0.50),
        'p99': pct(lats, 0.99),
        'frac': (ok_slo / total) if total else 0.0,
        'timeoutRate': (timeouts / total) if total else 0.0,
        'goodput': 0.0,
        'n': total,
    }
    wall = (max_ts - min_ts) / 1000.0
    if wall > 0:
        out['goodput'] = good / wall
    return out


def recompute(rec, samples):
    """Recompute the drain-window metrics for one run from its raw trace."""
    slo_p99 = rec['params'].get('sloP99Ms', 250)
    slo_err = rec['params'].get('sloErrorRate', 0.01)
    t_drain = rec.get('tDrainSec') or 0

    # The runner clears its in-memory sample slice at restore ("Clear samples for
    # drain phase metrics (keep file append-only for raw data)"), so
    # computeSupplementary only ever sees post-restore samples -- while the trace
    # on disk still holds the whole run including warm-up. Recomputing from the
    # file therefore has to drop everything before the restore epoch first, or
    # the drain window lands on the warm-up and every collapsed run reads healthy.
    # ...but the clear does not land exactly on the restore epoch. tailSamples
    # follows the file by byte offset every 200 ms and the injector flushes its
    # buffer every 500 ms, so samples written up to one flush interval before the
    # restore are still unread at the clear and are therefore counted in the
    # post-restore set. Reconstructing that set from the file means starting one
    # flush interval early. Measured directly: sweeping this offset on a
    # collapsed run reproduces the committed p50 and p99 exactly from 200 ms
    # onward and is stable across 200-1000 ms; 0 ms is one sample short.
    ranges = {f: [] for f in RANGE_FIELDS}
    for lag in FLUSH_LAGS_MS:
        restore = rec['restoreEpochMs'] - lag
        sub = [s for s in samples if s['ts'] >= restore]
        min_ts = 0
        for s in sub:
            if s['class'] == 'live' and s['age_ms'] == 0:
                min_ts = s['ts']
                break
        if min_ts == 0 and sub:
            min_ts = sub[0]['ts']
        drain_end = (min_ts + int(t_drain * 1000)) if t_drain > 0 else (1 << 62)
        lv = fill_live_supp(sub, min_ts, drain_end, slo_p99)
        ranges['drainLiveP50Ms'].append(lv['p50'])
        ranges['drainLiveP99Ms'].append(lv['p99'])
        ranges['drainGoodputRpsMean'].append(lv['goodput'])
        ranges['drainTimeoutRate'].append(lv['timeoutRate'])
        ranges['G_norm'].append(lv['goodput'] / G_CEIL)
    live = lv

    # Queue depth over the drain window, from the timeline.
    dq_sum = 0.0
    dq_n = 0
    for p in rec.get('timeline', []):
        if t_drain <= 0 or p['tSec'] <= t_drain + 0.5:
            dq_sum += float(p.get('queued', 0))
            dq_n += 1
    q_mean = (dq_sum / dq_n) if dq_n else 0.0

    # vSLO over the timeline, without artifact exclusion, which is what the
    # pre-Aug-19 runner computed.
    t_full = rec.get('tFullSec') or 0
    violations = 0
    for p in rec.get('timeline', []):
        if t_full > 0 and p['tSec'] > t_full:
            continue
        if p.get('liveP99Ms', 0) > slo_p99 or p.get('errorRate', 0) > slo_err:
            violations += 1
    v_slo = (violations / t_full) if t_full > 0 else 0.0

    out = {
        'drainQueueDepthMean': q_mean,
        'vSLO': v_slo,
        'tDrainSec': t_drain,
        '_liveSamples': live['n'],
        '_ranges': {f: (min(v), max(v)) for f, v in ranges.items()},
    }
    for f in RANGE_FIELDS:
        out[f] = ranges[f][0]
    return out


def committed(rec):
    sup = rec['supplementary']
    return {
        'drainLiveP50Ms': sup['drainLiveP50Ms'],
        'drainLiveP99Ms': sup['drainLiveP99Ms'],
        'drainGoodputRpsMean': sup['drainGoodputRpsMean'],
        'drainTimeoutRate': sup['drainTimeoutRate'],
        'drainQueueDepthMean': sup['drainQueueDepthMean'],
        'G_norm': sup['drainGoodputRpsMean'] / G_CEIL,
        'vSLO': rec['vSLO'],
        'tDrainSec': rec['tDrainSec'],
    }


def agrees(field, got, want):
    """True if the committed value is reproducible by the reconstructed code."""
    if field in EXACT_FIELDS:
        return abs(got[field] - want[field]) <= 1e-9
    lo, hi = got['_ranges'][field]
    rel = GOODPUT_EPS_REL if field in ('drainGoodputRpsMean', 'G_norm') else RANGE_EPS_REL
    eps = max(abs(lo), abs(hi), 1e-12) * rel
    return lo - eps <= want[field] <= hi + eps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw-dir', default=DEFAULT_RAW)
    ap.add_argument('--manifest', default=os.path.join(HERE, 'manifest.json'))
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()

    manifest = json.load(open(a.manifest))
    runs = manifest['runs']

    if not os.path.isdir(a.raw_dir):
        print('SKIP: raw traces not found at %s' % a.raw_dir)
        print('      They live outside the repository; see results/RAW-DATA.md and')
        print('      release raw-data-2026-08-18. Nothing was checked.')
        return 0

    failures = []
    checked = 0
    print('%-28s %-4s %-3s %10s %10s %10s %10s %10s' % (
        'run', 'arm', 'reg', 'p50', 'p99', 'goodput', 'qMean', 'vSLO'))
    for entry in runs:
        run_id = entry['runId']
        rec_path = os.path.join(REPO, 'results', '%s.json' % run_id)
        if not os.path.exists(rec_path):
            failures.append((run_id, 'record', 'missing', rec_path))
            continue
        rec = json.load(open(rec_path))
        fh = open_trace(a.raw_dir, run_id)
        if fh is None:
            print('  SKIP %s (no trace)' % run_id)
            continue
        samples = []
        with fh:
            for line in fh:
                if line.strip():
                    samples.append(json.loads(line))
        got = recompute(rec, samples)
        want = committed(rec)
        checked += 1
        row_bad = []
        for field in EXACT_FIELDS + RANGE_FIELDS:
            if not agrees(field, got, want):
                row_bad.append(field)
                detail = got[field] if field in EXACT_FIELDS else got['_ranges'][field]
                failures.append((run_id, field, want[field], detail))
        print('%-28s %-4s %-3s %10.1f %10.1f %10.2f %10.2f %10.4f %s' % (
            run_id, entry['arm'], entry['regime'],
            got['drainLiveP50Ms'], got['drainLiveP99Ms'], got['drainGoodputRpsMean'],
            got['drainQueueDepthMean'], got['vSLO'],
            'MISMATCH: ' + ','.join(row_bad) if row_bad else 'ok'))
        if a.verbose:
            for f in RANGE_FIELDS:
                lo, hi = got['_ranges'][f]
                print('     %-22s committed=%-12.4f reproducible range [%.4f, %.4f]' % (
                    f, want[f], lo, hi))

    print()
    if failures:
        print('FAIL: %d field disagreement(s) across %d run(s) checked' % (len(failures), checked))
        for run_id, field, want, got in failures:
            print('  %-28s %-24s committed=%r recomputed=%r' % (run_id, field, want, got))
        print()
        print('A disagreement here means the reconstructed metrics path computes')
        print('something different from the code that produced the existing corpus.')
        print('Do not run experiments until it is explained.')
        return 1
    print('PASS: %d runs, %d fields each -- 3 exact, 5 reproducible within the\n      sample-set boundary window' % (checked, len(EXACT_FIELDS) + len(RANGE_FIELDS)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
