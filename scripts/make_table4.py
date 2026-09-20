#!/usr/bin/env python3
"""T1: the three findings that entered the record and were later killed.

Distinguished from process errors, which were mistakes in how the work was done
rather than claims about the system. Sourced from the committed reports.

Usage: python3 scripts/make_table4.py > figures/T4-false-findings.md
"""
ROWS = [
    {
        'finding': 'Recovery is bimodal in both arms',
        'predicted': 'Two stable regimes at the last SAFE point in c10 as well as '
                     'c50: some runs drain shallow, some deep, at the same rate.',
        'basis': 'E1, n=3 per point. Three c10 runs at rl=825 showed a spread wide '
                 'enough to read as two clusters.',
        'killed': 'E1B replication at n=12 with the DEEP threshold fixed before '
                  'running. c10 returned 0/12 DEEP and is unimodal; only c50 is '
                  'gapped, at 9/12.',
        'when': 'E1B, 2026-09-12',
        'cost': 'Bimodality became a single-arm property, and the E2 design had to '
                'ask whether it followed the cap or the arm.',
    },
    {
        'finding': 'Occupancy at the boundary is a fixed 4.1% of the queue cap',
        'predicted': 'Median queue depth at the last SAFE point scales with the '
                     'cap, so swapping caps moves occupancy with it.',
        'basis': 'A two-point agreement in E1 at C0: 4.114% and 4.071% across the '
                 'two arms, registered in E2-PLAN addendum 1 as a prediction.',
        'killed': 'The first cell that tested it. c10 at Q=2500 sat at 0.923% of '
                  'cap and c50 at Q=500 at 21.686%; absolute occupancy stayed with '
                  'the arm while the cap moved fivefold.',
        'when': 'E2, 2026-09-12',
        'cost': 'None to any other result. The prediction was registered before '
                'the cells ran and scored against them.',
    },
    {
        'finding': 'A4 achieved utilisation is valid at every probed point',
        'predicted': 'The delivery-span estimator, adopted to strip the drain '
                     'detector tail, applies to SAFE and collapsed points alike, '
                     'so a boundary interval may be reported in utilisation.',
        'basis': 'A4 was validated where it was built, on SAFE points, and then '
                 'used everywhere without the question being asked again.',
        'killed': 'A cross-check against an independently measured quantity: each '
                  'cell\'s saturation plateau. 18 of 20 UNSAFE points report a rate '
                  'above their own cell\'s independently measured saturation '
                  'plateau — a pattern incompatible with treating the estimator as '
                  'physically interpretable at collapsed points. Not '
                  'found by the estimator\'s own validation.',
        'when': 'E2e then A6, 2026-09-13',
        'cost': 'E2d\'s collapse factor halves, 21.4x to 10.5x — A6 first reported '
                '10.3x, superseded by A10 under matched estimators — and its claim '
                'that five of seven intervals bracket 1.0 falls entirely. Four other '
                'conclusions were rechecked and survive.',
    },
]

def main():
    print('# T1 — findings that entered the record and were later killed')
    print()
    print('Three claims reached the written record and were subsequently refuted by '
          'further measurement. Each is listed with what it predicted, what killed '
          'it, and when. Process errors — mistakes in how the work was carried out '
          'rather than claims about the system — are not included here; they are '
          'recorded in the plan addenda.')
    print()
    print('| # | Finding | What it predicted | What killed it | When | Consequence |')
    print('|---|---|---|---|---|---|')
    for i, r in enumerate(ROWS, 1):
        print('| %d | **%s** | %s | %s | %s | %s |'
              % (i, r['finding'], r['predicted'], r['killed'], r['when'], r['cost']))
    print()
    print('## Basis of each, as originally held')
    print()
    for i, r in enumerate(ROWS, 1):
        print('%d. **%s** — %s' % (i, r['finding'], r['basis']))
    print()
    print('The common thread is that none was killed by the analysis that produced '
          'it. Two fell to a replication designed to test them, and the third to a '
          'cross-check against a quantity measured by a different route. An '
          'estimator cannot find its own blind spot.')
    return 0

if __name__ == '__main__':
    main()
