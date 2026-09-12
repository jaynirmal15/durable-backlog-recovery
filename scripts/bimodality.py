#!/usr/bin/env python3
"""Threshold-free shape statistics for a set of run values.

E1B-PLAN committed to reporting "a dip test of the distribution's shape that does
not use the threshold at all", alongside the DEEP/SHALLOW split. The E1B report
gave only a gap ratio. This supplies the full set.

A formal Hartigan dip test is not offered, and deliberately: at n=12 its power
against any realistic alternative is negligible, so a p-value would be a
decoration. What follows are descriptive statistics that need no threshold, with
their limitations stated rather than hidden.

  gapRatio    largest gap between sorted neighbours, over the median gap.
              Scale-free. A clean two-cluster sample shows one gap much larger
              than the rest.
  BC          bimodality coefficient, (skew^2 + 1) / (kurtosis + 3(n-1)^2/((n-2)(n-3))).
              The uniform distribution gives 5/9 = 0.5556; higher suggests
              bimodality, lower unimodality. Sensitive to skew, so a long right
              tail can raise it without two modes -- read it with gapRatio.
  dipGap      the largest gap expressed as a fraction of the full range. A
              two-cluster sample puts a large share of its range in one gap.
  kmeans2     1-D two-means split: the between-cluster separation divided by the
              pooled within-cluster spread. Large means the two groups are far
              apart relative to their own widths.
"""
import json, statistics, sys


def shape(vals):
    x = sorted(float(v) for v in vals)
    n = len(x)
    gaps = [x[i + 1] - x[i] for i in range(n - 1)]
    rng = x[-1] - x[0]
    m, sd = statistics.mean(x), statistics.pstdev(x)
    skew = kurt = float('nan')
    if sd > 0:
        skew = sum((v - m) ** 3 for v in x) / n / sd ** 3
        kurt = sum((v - m) ** 4 for v in x) / n / sd ** 4 - 3.0
    bc = float('nan')
    if n > 3 and sd > 0:
        bc = (skew ** 2 + 1) / (kurt + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))
    # two-means on a sorted 1-D sample: the optimal split is at some index
    best = None
    for k in range(1, n):
        a, b = x[:k], x[k:]
        wss = sum((v - statistics.mean(a)) ** 2 for v in a) + sum((v - statistics.mean(b)) ** 2 for v in b)
        if best is None or wss < best[0]:
            best = (wss, k)
    _, k = best
    a, b = x[:k], x[k:]
    sep = abs(statistics.mean(b) - statistics.mean(a))
    within = ((statistics.pstdev(a) if len(a) > 1 else 0) + (statistics.pstdev(b) if len(b) > 1 else 0)) / 2 or 1e-9
    return {
        'n': n, 'min': x[0], 'max': x[-1], 'mean': round(m, 3), 'median': round(statistics.median(x), 3),
        'sd': round(sd, 3),
        'gapRatio': round(max(gaps) / statistics.median(gaps), 2) if statistics.median(gaps) > 0 else None,
        'largestGap': round(max(gaps), 2), 'medianGap': round(statistics.median(gaps), 2),
        'dipGap': round(max(gaps) / rng, 3) if rng > 0 else None,
        'bimodalityCoefficient': round(bc, 3) if bc == bc else None,
        'bcRefUniform': 0.5556,
        'kmeans2SplitAt': round((x[k - 1] + x[k]) / 2, 2), 'kmeans2LowN': k, 'kmeans2HighN': n - k,
        'kmeans2Separation': round(sep / within, 2),
        'sorted': [round(v, 1) for v in x],
    }


if __name__ == '__main__':
    import glob
    out = {}
    for label, pat in [('c10/C0 rl=825 (E1B, n=12)', 'results/e1b-c10-c0-rl825-r*.json'),
                       ('c50/C0 rl=975 (E1B, n=12)', 'results/e1b-c50-c0-rl975-r*.json')]:
        vals = [json.load(open(p))['supplementary']['drainQueueDepthMean'] for p in glob.glob(pat)]
        if not vals:
            continue
        out[label] = shape(vals)
    for label, s in out.items():
        print('%s' % label)
        print('  sorted      %s' % ' '.join('%.1f' % v for v in s['sorted']))
        print('  gapRatio    %-6s  (largest %.1f / median %.1f)' % (s['gapRatio'], s['largestGap'], s['medianGap']))
        print('  dipGap      %-6s  (largest gap as a share of the range)' % s['dipGap'])
        print('  BC          %-6s  (uniform reference %.4f; > suggests bimodal)' % (s['bimodalityCoefficient'], s['bcRefUniform']))
        print('  kmeans2     split at %.1f -> %d low / %d high, separation %.2f x within-spread'
              % (s['kmeans2SplitAt'], s['kmeans2LowN'], s['kmeans2HighN'], s['kmeans2Separation']))
        print()
    json.dump(out, open('results/E1B-shape-statistics.json', 'w'), indent=2)
    print('wrote results/E1B-shape-statistics.json')
