#!/usr/bin/env python3
# This file was reconstructed from the 2026-08-19 session log; original was never committed.
# See RECONSTRUCTION.md.
"""Standard metric table from run records.

Exists because G_norm was previously computed by hand and typed into report
markdown. That is how PHASE1B-H3H4-s50.md came to divide by 2*G_ceil=1996 for
its two c50 rows, halving both. G_ceil is an explicit argument here; it is never
derived from a sweep's maximum achieved rate.

  python3 scripts/report_metrics.py --g-ceil 998 --group "H4 @50=p1b-h4-s50-rl290-r1,p1b-h4-s50-rl290-r2"
  python3 scripts/report_metrics.py --g-ceil 998 --glob 'results/p1c-c2-rl*.json'
"""
import argparse, glob, json, os, re, statistics, sys

def load(run):
    p = run if run.endswith('.json') else 'results/%s.json' % run
    return json.load(open(p))

def fault_capacity(d):
    nom = d['params'].get('nominalCapacity', 2000)
    for st in d.get('capacitySchedule', []):
        if st['rate'] < nom:
            return st['rate']
    return nom

def achieved(d):
    """Live and recovery arrival rates actually delivered.

    Both pacers under-deliver (tick-dropping time.Ticker), so nominal
    (lambda_L + rl) overstates true utilisation by 0.005-0.011 in rho.
    Always report rho_ach alongside rho_nom."""
    import datetime
    st = datetime.datetime.fromisoformat(d['startedAt'].replace('Z', '+00:00'))
    wall = (d['restoreEpochMs'] / 1000.0 - st.timestamp()) + d['timeline'][-1]['tSec']
    live = d['params'].get('injectorIssued', 0) / wall if wall else 0
    td = d.get('tDrainSec', 0)
    rec = d['backlogAtRestore'] / td if td and td > 0 else 0
    return live, rec

def row(label, runs, g_ceil):
    ds = [load(r) for r in runs]
    sup = [d['supplementary'] for d in ds]
    mean = lambda f: statistics.mean([f(d, s) for d, s in zip(ds, sup)])
    inval = [d.get('invalidReason') for d in ds if d.get('invalid')]
    return dict(
        label=label, n=len(ds),
        rl=ds[0]['params'].get('rateLimitRps'),
        arm=ds[0]['params'].get('concurrencyArm')
            or {5: 'c10', 25: 'c50'}.get(ds[0]['params'].get('serviceTimeMs'), '?'),
        tDrain=mean(lambda d, s: d['tDrainSec']),
        tFull=mean(lambda d, s: d['tFullSec']),
        vSLO=mean(lambda d, s: d['vSLO']),
        vLat=mean(lambda d, s: d.get('vSLO_latency', 0)),
        vErr=mean(lambda d, s: d.get('vSLO_error', 0)),
        vSLOraw=mean(lambda d, s: d.get('vSLO_raw', d['vSLO'])),
        p99=mean(lambda d, s: s['drainLiveP99Ms']),
        p50=mean(lambda d, s: s['drainLiveP50Ms']),
        G=mean(lambda d, s: s['drainGoodputRpsMean']),
        Gn=mean(lambda d, s: s['drainGoodputRpsMean']) / g_ceil,
        tmo=mean(lambda d, s: s['drainTimeoutRate']),
        qMean=mean(lambda d, s: s['drainQueueDepthMean']),
        stall=mean(lambda d, s: d.get('stallSeconds', 0)),
        faultVSLO=mean(lambda d, s: d.get('faultVSLO', 0)),
        t2health=mean(lambda d, s: d.get('timeToHealthAfterRestoreSec', -1)),
        liveAch=mean(lambda d, s: achieved(d)[0]),
        recAch=mean(lambda d, s: achieved(d)[1]),
        rhoNom=mean(lambda d, s: (d['params']['liveRatePerSec']
                                  + max(0, d['params'].get('rateLimitRps', 0))) / fault_capacity(d)),
        rhoAch=mean(lambda d, s: sum(achieved(d)) / fault_capacity(d)),
        contam=mean(lambda d, s: d.get('contaminatedSeconds', 0)),
        invalid=inval)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--g-ceil', type=float, required=True,
                    help='live-only goodput ceiling for THIS arm at lambda_L')
    ap.add_argument('--group', action='append', default=[], help='"label=run1,run2"')
    ap.add_argument('--glob', help='group run records by rateLimitRps')
    a = ap.parse_args()

    groups = []
    for g in a.group:
        label, runs = g.split('=', 1)
        groups.append((label, runs.split(',')))
    if a.glob:
        by = {}
        for f in sorted(glob.glob(a.glob)):
            d = json.load(open(f))
            by.setdefault(d['params'].get('rateLimitRps'), []).append(f)
        for rl in sorted(by, key=lambda x: (x is None, x)):
            groups.append(('rl=%s' % rl, by[rl]))
    if not groups:
        sys.exit('no groups')

    print('G_ceil = %.1f' % a.g_ceil)
    arms = {row(l, r, a.g_ceil)['arm'] for l, r in groups}
    if len(arms) > 1:
        print('NOTE: groups span arms %s. G_ceil is measured PER ARM; these rows are'
              % sorted(arms))
        print('      normalised against separately measured denominators (both 998 as of')
        print('      2026-08-19 — the ceiling is injector-limited at lambda_L, not arm-limited).')
    # Frontier axes: tDrain x G_norm (PRIMARY). vSLO retained but demoted --
    # it separated cliff from blocking-graceful by 9% where G_norm separated
    # them by 9x, across a 100x p99 difference. p50 and timeout rate are
    # standing columns because p50 moved 191% at the collapsed anchor while
    # vSLO moved 9%.
    hdr = ('group', 'arm', 'n', 'tDrain', 'G_norm', 'rho_ach', 'p50', 'p99',
           'tmo', 'qMean', 'vSLO', 'v_lat', 'v_err', 'faultV', 't2heal')
    print('%-16s %-4s %2s %7s %8s %8s %6s %7s %6s %8s %7s %7s %7s %7s %7s' % hdr)
    for label, runs in groups:
        r = row(label, runs, a.g_ceil)
        print('%-16s %-4s %2d %7.1f %8.3f %8.4f %6.0f %7.0f %6.3f %8.1f %7.4f %7.4f %7.4f %7.4f %7.1f' % (
            r['label'], r['arm'], r['n'], r['tDrain'], r['Gn'], r['rhoAch'], r['p50'],
            r['p99'], r['tmo'], r['qMean'], r['vSLO'], r['vLat'], r['vErr'],
            r['faultVSLO'], r['t2health']))
        print('%-16s     achieved: live=%.1f rec=%.1f rps | G=%.1f | rho_nom=%.4f | stall=%.1f' % (
            '', r['liveAch'], r['recAch'], r['G'], r['rhoNom'], r['stall']))
        if r['invalid']:
            print('    INVALID: %s' % r['invalid'])

main()
