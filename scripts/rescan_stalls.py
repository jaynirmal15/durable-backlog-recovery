#!/usr/bin/env python3
# This file was reconstructed from session transcript 2026-08-19; original was never committed.
# See RECONSTRUCTION.md.
"""Re-scan existing run records for the host-stall (measurement-artifact) signature.

Stage 1 (this script) uses only the run record timeline, so it needs no raw
jsonl. The timeline's p99 columns are 5s-trailing-window values, so a stall
appears smeared across several seconds; the inter-sample-gap criterion cannot be
checked here and must be confirmed per-run against the consumer jsonl.

Criteria (timeline proxy for the runner's live detector):
  live p99 and recovery p99 both >= FACTOR x rolling median baseline, and
  downstream queued <= QMAX (dependency idle => not saturation).
"""
import json, glob, os, sys, statistics

FACTOR = 5.0
QMAX = 5
BASE_N = 30
BASE_MIN = 10

def scan(path):
    d = json.load(open(path))
    if 'timeline' not in d or 'runId' not in d:
        return None
    lb, rb, hits = [], [], []
    for p in d['timeline']:
        lp, rp, q = p.get('liveP99Ms', 0), p.get('recoveryP99Ms', 0), p.get('queued', 0)
        if lp <= 0 or rp <= 0:
            continue
        stall = False
        if len(lb) >= BASE_MIN:
            ml, mr = statistics.median(lb), statistics.median(rb)
            if ml > 0 and mr > 0 and lp >= FACTOR*ml and rp >= FACTOR*mr and q <= QMAX:
                stall = True
        if stall:
            hits.append((round(p['tSec']), lp, rp, q))
        else:
            lb = (lb + [lp])[-BASE_N:]
            rb = (rb + [rp])[-BASE_N:]
    if not hits:
        return None
    tF = d.get('tFullSec', 0) or 1
    # each stall second contaminates itself + the following 5s reporting window
    contam = set()
    for t, *_ in hits:
        for k in range(t, t+6):
            contam.add(k)
    viol = sum(1 for p in d['timeline']
               if p.get('liveP99Ms', 0) > 250 or p.get('errorRate', 0) > 0.01)
    viol_in = sum(1 for p in d['timeline']
                  if (p.get('liveP99Ms', 0) > 250 or p.get('errorRate', 0) > 0.01)
                  and round(p['tSec']) in contam)
    return dict(run=os.path.basename(path), vSLO=d.get('vSLO', 0), tFull=tF,
                stalls=len(hits), contam=len(contam), viol=viol, viol_in=viol_in,
                dv=viol_in/tF, hits=hits[:6])

rows = []
for f in sorted(glob.glob('results/*.json')):
    try:
        r = scan(f)
    except Exception:
        continue
    if r:
        rows.append(r)

rows.sort(key=lambda r: -r['dv'])
print('%-30s %7s %6s %7s %6s %8s %8s' % ('run', 'vSLO', 'stalls', 'contam', 'viol', 'viol_in', 'dvSLO'))
for r in rows:
    print('%-30s %7.4f %6d %7d %6d %8d %8.4f' % (
        r['run'], r['vSLO'], r['stalls'], r['contam'], r['viol'], r['viol_in'], r['dv']))
print('\n%d of %d run records show the signature' % (len(rows), len(glob.glob('results/*.json'))))
if rows:
    print('\nexample stall seconds (t, liveP99, recP99, queued):')
    for r in rows[:6]:
        print('  %-30s %s' % (r['run'], r['hits']))
