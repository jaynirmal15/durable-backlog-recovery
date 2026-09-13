#!/usr/bin/env python3
"""Did the queue cap ever bind at the boundary?

A cap can only change an outcome if the queue actually reaches it. This reports,
per probed point, the peak drain-window queue depth against the cap in force, and
whether any run in the point touched the cap.

Also reports the failure mode, because a smaller cap could in principle convert
latency violations into rejections -- and rejected 429s are excluded from the
error accounting by `sloErrorAccounting`, which would make a run look SAFE for
the wrong reason. If that were happening, `rejected` would be non-zero in the
small-cap cells.

Usage: python3 scripts/cap_binding.py
"""
import glob
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cap_occupancy import effective_cap  # noqa: E402


def counter_delta(rec, key):
    """Increase in a cumulative counter across the recorded timeline.

    `rejected` and `timedOut` are cumulative and already carry the fault window's
    total by the first sample -- c10/C1 sits at 50114 timeouts at t=1s and never
    moves -- so the running total says nothing about the drain. The delta does:
    anything the drain itself rejected or timed out shows up as an increase.
    """
    tl = rec.get('timeline') or []
    if not tl:
        return 0
    return (tl[-1].get(key, 0) or 0) - (tl[0].get(key, 0) or 0)


def rows_for(paths, label):
    by = {}
    for path in sorted(paths):
        rec = json.load(open(path))
        rl = rec['params']['rateLimitRps']
        cap, cd = effective_cap(rec)
        d = by.setdefault(rl, {'cap': cap, 'cd': cd, 'peaks': [], 'vslo': [],
                               'rej': [], 'to': [], 'lat': [], 'err': []})
        d['peaks'].append(rec['supplementary']['drainQueueDepthPeak'])
        d['vslo'].append(rec['vSLO'])
        d['lat'].append(rec['vSLO_latency'])
        d['err'].append(rec['vSLO_error'])
        d['rej'].append(counter_delta(rec, 'rejected'))
        d['to'].append(counter_delta(rec, 'timedOut'))
    out = []
    for rl in sorted(by):
        d = by[rl]
        mx = max(d['peaks'])
        med = statistics.median(d['peaks'])
        out.append({'cell': label, 'rl': rl, 'n': len(d['peaks']), 'cap': d['cap'],
                    'maxQPeak': mx, 'pctOfCap': round(100.0 * mx / d['cap'], 1),
                    'medQPeak': round(med, 1), 'medPctOfCap': round(100.0 * med / d['cap'], 1),
                    'capTouched': mx >= d['cap'],
                    'safe': max(d['vslo']) <= 0.01,
                    'maxVSLO': round(max(d['vslo']), 4),
                    'anyRejected': max(d['rej']), 'anyTimedOut': max(d['to']),
                    'maxVSLOError': round(max(d['err']), 4),
                    'maxVSLOLatency': round(max(d['lat']), 4)})
    return out


def main():
    cells = []
    for arm, reg, label in [('c10', 'c0', 'E1 c10/C0 Q=500'), ('c10', 'c1', 'E1 c10/C1 Q=350'),
                            ('c50', 'c0', 'E1 c50/C0 Q=2500'), ('c50', 'c1', 'E1 c50/C1 Q=1750')]:
        p = (glob.glob('results/%s-%s-rl*-r*.json' % (arm, reg))
             + glob.glob('results/e1b-%s-%s-rl*-r*.json' % (arm, reg)))
        if p:
            cells += rows_for(p, label)
    for d, label in [('results/e2/c10-Q2500', 'E2 c10 Q=2500'),
                     ('results/e2/c50-Q500', 'E2 c50 Q=500'),
                     ('results/e2b', 'E2b C=400 Q=500')]:
        p = glob.glob(os.path.join(d, '*c*-c*-rl*-r*.json'))
        if p:
            cells += rows_for(p, label)

    print('%-18s %6s %3s %6s %8s %8s %8s %8s %-9s %s' % (
        'cell', 'rl', 'n', 'cap', 'medQPeak', '% cap', 'maxQPeak', '% cap', 'class',
        'rejected/timedOut'))
    for r in cells:
        print('%-18s %6d %3d %6d %8.1f %7.1f%% %8d %7.1f%%%s %-9s %d / %d' % (
            r['cell'], r['rl'], r['n'], r['cap'], r['medQPeak'], r['medPctOfCap'],
            r['maxQPeak'], r['pctOfCap'], '*' if r['capTouched'] else ' ',
            'SAFE' if r['safe'] else 'non-SAFE', r['anyRejected'], r['anyTimedOut']))
    print('(* = at least one run in the point reached the cap)')

    print()
    tot_rej = sum(r['anyRejected'] for r in cells)
    tot_to = sum(r['anyTimedOut'] for r in cells)
    print('Increase during the recorded timeline, summed over every point in every '
          'cell: rejected=%d, timedOut=%d.' % (tot_rej, tot_to))
    if tot_rej == 0:
        print('No run in either campaign rejected a request during the drain, at any')
        print('cap. So no cap converted a latency violation into a 429 that the error')
        print('accounting would have excluded -- the concern that motivated this check.')
    else:
        print('WARNING: rejections occurred; the 429 exclusion rule bears on the result.')

    # vSLO_error is not zero everywhere, and saying so would be wrong.
    errs = [r for r in cells if r['maxVSLOError'] > 0]
    print()
    if not errs:
        print('vSLO_error is zero at every point: all violations are latency violations.')
    else:
        print('Points where vSLO_error > 0 (checked against vSLO_both to see whether the')
        print('error seconds are additional violations or the same seconds twice):')
        for r in errs:
            print('  %-18s rl=%-5d vSLO_error %.4f  vSLO_latency %.4f'
                  % (r['cell'], r['rl'], r['maxVSLOError'], r['maxVSLOLatency']))

    print()
    print('Cap touched at the last SAFE point / at the first non-SAFE point:')
    print('%-18s %-28s %s' % ('cell', 'last SAFE', 'first non-SAFE'))
    for c in sorted({r['cell'] for r in cells}, key=lambda x: (x[:2], x)):
        rs = [r for r in cells if r['cell'] == c]
        ls = max([r for r in rs if r['safe']], key=lambda r: r['rl'], default=None)
        ns = min([r for r in rs if not r['safe']], key=lambda r: r['rl'], default=None)
        f = lambda r: ('rl=%d  med %.1f%%  max %.1f%%%s'
                       % (r['rl'], r['medPctOfCap'], r['pctOfCap'],
                          '  CAP HIT' if r['capTouched'] else '')) if r else 'none'
        print('%-18s %-32s %s' % (c, f(ls), f(ns)))

    json.dump({'points': cells, 'totalRejected': tot_rej, 'totalTimedOut': tot_to},
              open('results/E2-cap-binding.json', 'w'), indent=2)
    print()
    print('wrote results/E2-cap-binding.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
