#!/usr/bin/env python3
"""Per-point achieved-rho spread against the search resolution (PRE-REGISTRATION A3).

Reads run records directly rather than a boundary file, so it works on a
boundary located before the diagnostic was wired into locate_boundary.py, and
can be re-run over the whole corpus at any time.

The question it answers: at a given nominal rl, do the n repetitions land at
achieved rho values further apart than the distance bisection claims to resolve?

    rho_resolution = RESOLUTION_RPS / C_d      5/2000 = 0.0025 at C0
                                               5/1400 = 0.0036 at C1

If the spread is larger, the search is resolving finer than its own instrument
and the 5 rps interval at that point cannot be trusted. This is expected to be
driven by the consumer's recovery rate limiter, which is still a tick-dropping
time.Ticker while the live injector has moved to a deadline pacer -- and rl is
the term being bisected.

Registered decision rule: more than two flagged points across E1 moves the
limiter to a deadline pacer before E2 and re-runs the affected boundaries. Two
or fewer and the asymmetry is a methods paragraph.

Usage:
  python3 scripts/spread_check.py                       # every E1 boundary found
  python3 scripts/spread_check.py --glob 'results/c10-c0-rl*-r*.json'
  python3 scripts/spread_check.py --json                # machine-readable
"""
import argparse
import collections
import glob as globmod
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locate_boundary import RESOLUTION_RPS, achieved_rho, spread_diagnostic  # noqa: E402

RUN_RE = re.compile(r'^(?P<arm>c\d+)-(?P<regime>c\d)-rl(?P<rl>\d+)-r(?P<rep>\d+)$')


def load_points(pattern):
    """Group run records by (arm, regime, rl)."""
    groups = collections.defaultdict(list)
    for path in sorted(globmod.glob(pattern)):
        name = os.path.basename(path)[:-5]
        m = RUN_RE.match(name)
        if not m:
            continue
        try:
            rec = json.load(open(path))
        except Exception:
            continue
        if 'runId' not in rec:
            continue
        key = (m.group('arm'), m.group('regime').upper(), int(m.group('rl')))
        groups[key].append(rec)
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', default='results/c*-c*-rl*-r*.json')
    ap.add_argument('--json', action='store_true', help='emit JSON instead of a table')
    a = ap.parse_args()

    groups = load_points(a.glob)
    if not groups:
        print('no run records matched %s' % a.glob)
        return 0

    rows = []
    for (arm, regime, rl), recs in sorted(groups.items()):
        rhos, vslos, invalid = [], [], []
        cap = None
        for rec in recs:
            ar = achieved_rho(rec)
            rhos.append(ar['rhoAchieved'])
            cap = ar['faultCapacity']
            vslos.append(rec.get('vSLO'))
            if rec.get('invalid'):
                invalid.append(rec.get('invalidReason'))
        diag = spread_diagnostic(rhos, cap)
        rows.append({
            'arm': arm, 'regime': regime, 'rl': rl, 'n': len(recs),
            'faultCapacity': cap,
            'rhoAchieved': rhos,
            'vSLO': vslos,
            'invalidReasons': invalid,
            **diag,
        })

    flagged = [r for r in rows if r['spreadExceedsResolution']]

    if a.json:
        print(json.dumps({
            'resolutionRps': RESOLUTION_RPS,
            'flaggedCount': len(flagged),
            'flaggedPoints': [{'arm': r['arm'], 'regime': r['regime'], 'rl': r['rl']} for r in flagged],
            'points': rows,
        }, indent=2))
        return 0

    print('%-5s %-3s %6s %2s %9s %9s %9s %6s  %s' % (
        'arm', 'reg', 'rl', 'n', 'rho_min', 'rho_max', 'spread', 'vs_res', 'flag'))
    for r in rows:
        print('%-5s %-3s %6d %2d %9.4f %9.4f %9.5f %6s  %s' % (
            r['arm'], r['regime'], r['rl'], r['n'],
            min(r['rhoAchieved']), max(r['rhoAchieved']),
            r['rhoAchievedSpread'],
            ('%.2fx' % r['spreadRatio']) if r['spreadRatio'] is not None else '-',
            'FLAG (res %.4f)' % r['rhoResolution'] if r['spreadExceedsResolution'] else ''))
        if r['invalidReasons']:
            print('%29s invalid: %s' % ('', ', '.join(filter(None, r['invalidReasons']))))

    print()
    print('points: %d   flagged: %d   resolution: %d rps' % (len(rows), len(flagged), RESOLUTION_RPS))
    if len(flagged) > 2:
        print()
        print('MORE THAN TWO POINTS FLAGGED.')
        print('Per PRE-REGISTRATION.md A3 that is the registered trigger: the consumer')
        print('rate limiter moves to a deadline pacer before E2, and the affected')
        print('boundaries are re-run. The asymmetry is a defect, not a caveat.')
    elif flagged:
        print('At or under the two-point threshold: the asymmetry stays a methods')
        print('paragraph and the intervals stand, with these points named.')
    else:
        print('No point resolved finer than its own instrument.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
