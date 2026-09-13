#!/usr/bin/env python3
"""Cap-normalised queue occupancy at every probed point (E2-PLAN, addendum 1).

The registration asks whether occupancy at the boundary is a fixed fraction of
the queue cap. That was a two-point agreement at C0 in E1 (4.11% and 4.07%), and
E2 is the first thing to test it.

Two corrections to how the registered table computed "% of cap":

  1. It used `downstreamQueueCap`, the value at t=0. Under C1 the cap tracks
     capacity -- SetCapacity recomputes Q = 50 x ceil(C x S) -- so it has already
     fallen to 350 (c10) or 1750 (c50) by the time the drain window opens. The
     effective cap is the one in force during the window the occupancy is
     measured over.
  2. Occupancy is `drainQueueDepthMean`, so the cap it should be divided by is
     the drain-window cap, not the run's opening cap.

Usage: python3 scripts/cap_occupancy.py
"""
import glob
import json
import math
import os
import statistics
import sys


def effective_cap(rec):
    """The queue cap in force during the drain window."""
    p = rec['params']
    s = p['downstreamServiceTimeMs'] / 1000.0
    sched = rec.get('capacitySchedule') or []
    cap_rate = sched[-1]['rate'] if sched else p['nominalCapacity']
    if p['downstreamQueueCapMode'] != 'profile_relative':
        return p['downstreamQueueCap'], cap_rate
    return 50 * int(math.ceil(cap_rate * s)), cap_rate


def cell(paths, label):
    by_rl = {}
    for path in sorted(paths):
        rec = json.load(open(path))
        rl = rec['params']['rateLimitRps']
        cap, cd = effective_cap(rec)
        by_rl.setdefault(rl, {'q': [], 'cap': cap, 'cd': cd, 'vslo': []})
        by_rl[rl]['q'].append(rec['supplementary']['drainQueueDepthMean'])
        by_rl[rl]['vslo'].append(rec['vSLO'])
    rows = []
    for rl in sorted(by_rl):
        d = by_rl[rl]
        med = statistics.median(d['q'])
        rows.append({'cell': label, 'rl': rl, 'n': len(d['q']), 'cap': d['cap'],
                     'capacityDuringDrain': d['cd'],
                     'medianQMean': round(med, 2),
                     'pctOfCap': round(100.0 * med / d['cap'], 3),
                     'maxVSLO': round(max(d['vslo']), 4),
                     'safe': max(d['vslo']) <= 0.01})
    return rows


def main():
    cells = []
    for arm, cond, label in [('c10', 'P0-A', 'E1 c10/C0'), ('c10', 'P0-B', 'E1 c10/C1'),
                             ('c50', 'P0-A', 'E1 c50/C0'), ('c50', 'P0-B', 'E1 c50/C1')]:
        reg = 'c0' if cond == 'P0-A' else 'c1'
        # E1B added nine replication runs at two of the last SAFE points, run
        # ids prefixed e1b-. The registered occupancy medians (20.57, 101.79)
        # are the n=15 pooled values, so the E1 column has to include them.
        paths = (glob.glob('results/%s-%s-rl*-r*.json' % (arm, reg))
                 + glob.glob('results/e1b-%s-%s-rl*-r*.json' % (arm, reg)))
        if paths:
            cells += cell(paths, label)
    for d, label in [('results/e2/c10-Q2500', 'E2 c10@Q2500'),
                     ('results/e2/c50-Q500', 'E2 c50@Q500'),
                     ('results/e2b', 'E2b C=400')]:
        paths = glob.glob(os.path.join(d, '*c*-c*-rl*-r*.json'))
        if paths:
            cells += cell(paths, label)

    print('%-14s %6s %3s %6s %6s %10s %9s %s' % (
        'cell', 'rl', 'n', 'C_d', 'cap', 'med qMean', '% of cap', 'class'))
    for r in cells:
        print('%-14s %6d %3d %6d %6d %10.2f %8.3f%% %s' % (
            r['cell'], r['rl'], r['n'], r['capacityDuringDrain'], r['cap'],
            r['medianQMean'], r['pctOfCap'], 'SAFE' if r['safe'] else 'non-SAFE'))

    print()
    print('Last SAFE point of each cell -- the row the registration scores:')
    print('%-14s %6s %6s %10s %9s' % ('cell', 'rl', 'cap', 'med qMean', '% of cap'))
    last = {}
    for r in cells:
        if r['safe'] and (r['cell'] not in last or r['rl'] > last[r['cell']]['rl']):
            last[r['cell']] = r
    for c in ['E1 c10/C0', 'E1 c10/C1', 'E1 c50/C0', 'E1 c50/C1', 'E2 c10@Q2500', 'E2 c50@Q500']:
        if c in last:
            r = last[c]
            print('%-14s %6d %6d %10.2f %8.3f%%' % (c, r['rl'], r['cap'], r['medianQMean'], r['pctOfCap']))

    json.dump({'note': 'cap is the effective cap during the drain window, 50*ceil(C_d*S) '
                       'under profile_relative, not the t=0 value',
               'points': cells,
               'lastSafePerCell': {k: v for k, v in last.items()}},
              open('results/E2-cap-occupancy.json', 'w'), indent=2)
    print()
    print('wrote results/E2-cap-occupancy.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
