#!/usr/bin/env python3
"""Recompute achieved rho over the delivery span (PRE-REGISTRATION A4).

`backlogAtRestore / tDrain` divides an exact backlog by a window padded with the
drain detector's confirmation tail -- 1.5 to 6.6 s on boundary 1, varying run to
run. That understates the recovery rate by a different amount each run and puts
noise into achieved rho that the limiter did not produce.

This measures it over the span the recovery traffic actually occupied, from the
retained per-request trace, and rewrites the boundary file's rho values and
spread diagnostic in place. No run is repeated.

  python3 scripts/recompute_rho.py --boundary results/boundaries/c10-C0.json \
      --raw-dir ../rhc-raw-data/results --write
"""
import argparse, glob, gzip, json, os, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import RESOLUTION_RPS, spread_diagnostic  # noqa: E402


def open_trace(dirs, run_id):
    """Open a trace, preferring the gzip when both forms exist.

    The .gz is authoritative: the runner writes it only when a run COMPLETES and
    deletes the plain file at the same time. So a plain file sitting beside a .gz
    is a stale partial -- typically an rsync that caught the run mid-flight. It
    shadowed a complete trace once and produced a silently skipped run; preferring
    plain would eventually produce silently WRONG numbers instead.
    """
    for d in dirs:
        gz = os.path.join(d, run_id + '-consumer.jsonl.gz')
        plain = os.path.join(d, run_id + '-consumer.jsonl')
        if os.path.exists(gz):
            if os.path.exists(plain):
                print('  note: ignoring stale partial %s (complete .gz present)' % plain)
            return gzip.open(gz, 'rb')
        if os.path.exists(plain):
            return open(plain, 'rb')
    return None


def delivery_rate(rec, fh):
    """Recovery arrivals and the span they occupied, inside the drain window."""
    restore, td = rec['restoreEpochMs'], rec.get('tDrainSec') or 0
    ts = []
    for line in fh:
        if not line.strip():
            continue
        d = json.loads(line)
        if d['class'] == 'recovery' and restore <= d['ts'] <= restore + td * 1000:
            ts.append(d['ts'])
    if len(ts) < 2:
        return None
    ts.sort()
    span = (ts[-1] - ts[0]) / 1000.0
    return {'arrivals': len(ts), 'spanSec': round(span, 3),
            'tailSec': round(td - (ts[-1] - restore) / 1000.0, 3),
            'rateRps': len(ts) / span if span else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--boundary', required=True)
    ap.add_argument('--raw-dir', action='append', default=[])
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    dirs = a.raw_dir or ['results', '../rhc-raw-data/results']

    b = json.load(open(a.boundary))
    if 'rhoEstimator' in b:
        print('%s already recomputed under A4; refusing to double-apply. '
              'Restore the as-measured file first (git checkout) if you need to redo it.'
              % os.path.basename(a.boundary))
        return 1
    cap = None
    changed = 0
    for pt in b['points']:
        new_rhos = []
        for run in pt['runs']:
            rec = json.load(open('results/%s.json' % run['runId']))
            fh = open_trace(dirs, run['runId'])
            if fh is None:
                # Leaving one run on the old estimator would mix estimators inside
                # a point and corrupt its spread. Refuse rather than half-apply.
                print('  FATAL: no trace for %s. Every run in a point must use the '
                      'same estimator; fetch the trace and retry.' % run['runId'])
                return 1
            with fh:
                dr = delivery_rate(rec, fh)
            if not dr:
                new_rhos.append(run['rhoAchieved'])
                continue
            cap = run['faultCapacity']
            rho = (run['liveAchievedRps'] + dr['rateRps']) / cap
            run['recoveryAchievedRpsDrainWindow'] = run['recoveryAchievedRps']
            run['recoveryAchievedRps'] = round(dr['rateRps'], 2)
            run['recoveryDeliverySpanSec'] = dr['spanSec']
            run['drainDetectorTailSec'] = dr['tailSec']
            run['rhoAchievedDrainWindow'] = run['rhoAchieved']
            run['rhoAchieved'] = round(rho, 4)
            new_rhos.append(round(rho, 4))
            changed += 1
        pt['rhoAchievedDrainWindow'] = pt['rhoAchieved']
        pt['rhoAchieved'] = new_rhos
        pt.update(spread_diagnostic(new_rhos, cap or 2000))

    lo, hi = b['boundary']['lastSafeRl'], b['boundary']['firstNonSafeRl']
    by = {p['rl']: p for p in b['points']}
    b['boundary']['rhoStarIntervalDrainWindow'] = b['boundary']['rhoStarInterval']
    b['boundary']['rhoStarInterval'] = [min(by[lo]['rhoAchieved']), max(by[hi]['rhoAchieved'])]
    b['boundary']['rhoIntervalWidth'] = round(
        b['boundary']['rhoStarInterval'][1] - b['boundary']['rhoStarInterval'][0], 4)
    flagged = [p['rl'] for p in b['points'] if p.get('spreadExceedsResolution')]
    # Boundaries located before the diagnostic was wired in have no such block.
    b.setdefault('spreadDiagnostic', {
        'rule': 'PRE-REGISTRATION.md A3, computed retrospectively under the A4 estimator.',
        'resolutionRps': RESOLUTION_RPS,
    })
    b['spreadDiagnostic'].update({'flaggedRates': flagged, 'flaggedCount': len(flagged),
                                  'maxSpread': max(p['rhoAchievedSpread'] for p in b['points'])})
    b['rhoEstimator'] = ('delivery span (PRE-REGISTRATION A4); the drain-window values are '
                         'retained alongside under *DrainWindow keys')

    print('%s: %d runs recomputed' % (os.path.basename(a.boundary), changed))
    print('  rho interval  %s -> %s' % (b['boundary']['rhoStarIntervalDrainWindow'],
                                        b['boundary']['rhoStarInterval']))
    print('  spread flags  %s -> %s' % (b['spreadDiagnostic'].get('flaggedRatesDrainWindow', '(as measured)'), flagged))
    if a.write:
        json.dump(b, open(a.boundary, 'w'), indent=2)
        print('  written')
    return 0


if __name__ == '__main__':
    sys.exit(main())
