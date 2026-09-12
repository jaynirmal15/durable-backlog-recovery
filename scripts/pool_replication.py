#!/usr/bin/env python3
"""Pool replication runs into a boundary point, on one estimator.

Written after doing this by hand and getting it wrong. The hand-edit appended
nine A4 runs to a point holding three drain-window runs, so a single point
carried two estimators and reported a spread seven times its own resolution.

The rule this enforces: a point is rebuilt from ALL its records at once, on the
as-measured estimator, and A4 is applied afterwards over the whole file by
recompute_rho.py. Never per-run, never twice.

It refuses to touch a file that already declares an estimator, because appending
to one is what caused the fault. The recovery is to restore the as-measured file
(git checkout, or the .from-box sidecar fetch_e2.sh leaves), pool, then recompute.

  python3 scripts/pool_replication.py \
      --boundary results/e2/c50-Q500/boundaries/c50-C0.json \
      --results results/e2/c50-Q500 --rl 990 --write
  python3 scripts/recompute_rho.py --boundary ... --results ... --write

Usage: see above. --write is required to modify anything.
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import classify, summarise_run, spread_diagnostic  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--boundary', required=True)
    ap.add_argument('--results', required=True)
    ap.add_argument('--rl', type=int, required=True)
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()

    b = json.load(open(a.boundary))
    if 'rhoEstimator' in b:
        print('REFUSING: %s already declares an estimator (%s).'
              % (os.path.basename(a.boundary), b['rhoEstimator']))
        print('Pooling into a recomputed file mixes estimators inside a point, which is')
        print('the exact fault this script exists to prevent. Restore the as-measured')
        print('file first, pool, then run recompute_rho.py once over the result.')
        return 1

    pts = [p for p in b['points'] if p['rl'] == a.rl]
    if not pts:
        print('no point at rl=%d in %s' % (a.rl, a.boundary))
        return 1
    pt = pts[0]

    pat = re.compile(r'-rl%d-r(\d+)\.json$' % a.rl)
    paths = sorted((int(pat.search(p).group(1)), p)
                   for p in glob.glob(os.path.join(a.results, '*-rl%d-r*.json' % a.rl))
                   if pat.search(p))
    if not paths:
        print('no run records at rl=%d under %s' % (a.rl, a.results))
        return 1

    before = len(pt['runs'])
    runs = [summarise_run(json.load(open(p))) for _, p in paths]

    # Every record must agree on the configuration, or the point is not one point.
    cfg = set()
    for _, p in paths:
        pa = json.load(open(p))['params']
        cfg.add((pa['downstreamQueueCap'], pa['downstreamServiceTimeMs'],
                 pa['downstreamConcurrency'], pa['injectorPacer'], pa['rateLimitRps']))
    if len(cfg) != 1:
        print('REFUSING: the %d records at rl=%d do not share one configuration:'
              % (len(paths), a.rl))
        for c in sorted(cfg):
            print('  cap=%s S=%s conc=%s pacer=%s rl=%s' % c)
        return 1

    pt['runs'] = runs
    pt['vSLO'] = [r['vSLO'] for r in runs]
    pt['rhoAchieved'] = [r['rhoAchieved'] for r in runs]
    pt['class'] = classify(pt['vSLO'])
    pt.update(spread_diagnostic(pt['rhoAchieved'], runs[0]['faultCapacity']))
    pt['nNote'] = ('n=%d, rebuilt from every record at this rate on the as-measured '
                   'estimator; A4 applied afterwards over the whole file.' % len(runs))

    bd = b['boundary']
    by = {p['rl']: p for p in b['points']}
    bd['rhoStarInterval'] = [min(by[bd['lastSafeRl']]['rhoAchieved']),
                             max(by[bd['firstNonSafeRl']]['rhoAchieved'])]

    print('rl=%d: %d runs -> %d, class %s' % (a.rl, before, len(runs), pt['class']))
    print('  reps present: %s' % ', '.join(str(n) for n, _ in paths))
    print('  cap=%s S=%s conc=%s pacer=%s (all records agree)' % tuple(list(cfg)[0][:4]))
    print('  spread flag: %s' % pt['spreadExceedsResolution'])
    print('  as-measured interval: %s' % bd['rhoStarInterval'])
    if pt['class'] != 'SAFE' and a.rl == bd['lastSafeRl']:
        print('  WARNING: the last SAFE point no longer classifies SAFE with the added')
        print('  runs. The boundary itself moves; do not just recompute rho.')
    if a.write:
        json.dump(b, open(a.boundary, 'w'), indent=2)
        print('  written. Now run recompute_rho.py to apply A4.')
    else:
        print('  (dry run; pass --write)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
