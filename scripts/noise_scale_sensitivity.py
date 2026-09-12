#!/usr/bin/env python3
"""How much does the leading-indicator answer depend on the noise scale?

PRE-REGISTRATION A5. The within-point noise scale in the E1 leading-indicator
analysis was changed from mean-pooled to median-pooled AFTER the data was in
view. That is the most attackable step in the analysis, so this recomputes the
whole warning table under both, plus a third estimator that needs no pooling at
all, and reports whether the (a)/(b)/(c) answer changes.

The detection criterion is held FIXED across all three scales so that only the
scale varies:

    a metric WARNS at a boundary if its rise from the deepest-safe point first
    reaches >= 3 sigma at a point that is NOT the last SAFE point,

i.e. there is at least one probed point of room between the first warning and
the edge of the safe region. Warning that arrives only at the last safe point is
not advance warning.

Three scales:

  mean    sigma = mean of the within-point SDs across all SAFE points
  median  sigma = median of the same
  welch   no pooling: each point is compared against the deepest-safe point with
          sqrt(sd_i^2/n_i + sd_0^2/n_0), the ordinary two-sample statistic

Usage: python3 scripts/noise_scale_sensitivity.py
"""
import json
import statistics
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from leading_indicator import BOUNDARIES, METRICS, WARN_SIGMA, collect  # noqa: E402


def sigma_series(pts, key, floor, scale):
    """Rise-in-sigma at each SAFE point, under one noise scale."""
    means = [p[key]['mean'] for p in pts]
    sds = [p[key]['sd'] for p in pts]
    ns = [p['n'] for p in pts]
    base, base_sd, base_n = means[0], sds[0], ns[0]
    if scale == 'mean':
        noise = max(statistics.mean(sds), floor)
        return [(m - base) / noise for m in means], noise
    if scale == 'median':
        noise = max(statistics.median(sds), floor)
        return [(m - base) / noise for m in means], noise
    if scale == 'welch':
        out = []
        for m, sd, n in zip(means, sds, ns):
            se = (max(sd, floor) ** 2 / n + max(base_sd, floor) ** 2 / base_n) ** 0.5
            out.append((m - base) / se if se > 0 else 0.0)
        return out, None
    raise ValueError(scale)


def first_warning(pts, sigmas):
    """Index of the first point at or above WARN_SIGMA, or None."""
    for i in range(1, len(pts)):
        if sigmas[i] >= WARN_SIGMA:
            return i
    return None


def main():
    scales = ['mean', 'median', 'welch']
    data = {b: collect(b)[1] for b in BOUNDARIES}
    verdicts = {}

    print('Detection criterion, held fixed: rise from deepest-safe reaches >= %.0f sigma'
          % WARN_SIGMA)
    print('at a point that is NOT the last SAFE point (so there is room before the edge).')
    print()
    print('%-9s %-17s %s' % ('boundary', 'metric',
          '  '.join('%-26s' % ('--- %s ---' % s) for s in scales)))
    print('%-9s %-17s %s' % ('', '',
          '  '.join('%-26s' % 'first warn / room / sigma' for s in scales)))

    for b in BOUNDARIES:
        pts = data[b]
        for key, label, unit, floor in METRICS:
            if len(pts) < 2:
                continue
            cells = []
            for sc in scales:
                sig, _ = sigma_series(pts, key, floor, sc)
                i = first_warning(pts, sig)
                if i is None:
                    cells.append('%-26s' % 'never')
                    verdicts.setdefault((b, key), {})[sc] = None
                else:
                    room = len(pts) - 1 - i
                    early = room >= 1
                    cells.append('%-26s' % ('rl=%d  room=%d  %.1fs%s'
                                            % (pts[i]['rl'], room, sig[i], '' if early else '  (edge only)')))
                    verdicts.setdefault((b, key), {})[sc] = (pts[i]['rl'], room, sig[i], early)
            print('%-9s %-17s %s' % (b, label, '  '.join(cells)))
        print()

    # Which boundaries have an EARLY warning from any metric, under each scale?
    print('=' * 96)
    print('Does any metric give ADVANCE warning (>= 1 probed point of room)?')
    print()
    print('%-9s %-10s %s' % ('boundary', 'SAFE pts', '  '.join('%-30s' % s for s in scales)))
    arm_warns = {sc: {} for sc in scales}
    for b in BOUNDARIES:
        pts = data[b]
        cells = []
        for sc in scales:
            hits = [label for key, label, unit, floor in METRICS
                    if (b, key) in verdicts and verdicts[(b, key)].get(sc)
                    and verdicts[(b, key)][sc][3]]
            arm_warns[sc][b] = bool(hits)
            cells.append('%-30s' % (', '.join(hits) if hits else 'none'))
        print('%-9s %-10d %s' % (b, len(pts), '  '.join(cells)))

    print()
    print('=' * 96)
    print('(a)/(b)/(c) under each noise scale')
    print()
    for sc in scales:
        c10 = any(arm_warns[sc][b] for b in ['c10-C0', 'c10-C1'])
        c50 = any(arm_warns[sc][b] for b in ['c50-C0', 'c50-C1'])
        ans = ('(c) warns in both arms' if (c10 and c50) else
               '(b) warns at c50 but not c10' if (c50 and not c10) else
               '(a) no signal warns in either arm' if not (c10 or c50) else
               'warns at c10 but not c50 (none of a/b/c)')
        print('  %-8s -> %s' % (sc, ans))
    print()
    answers = set()
    for sc in scales:
        c10 = any(arm_warns[sc][b] for b in ['c10-C0', 'c10-C1'])
        c50 = any(arm_warns[sc][b] for b in ['c50-C0', 'c50-C1'])
        answers.add((c10, c50))
    if len(answers) > 1:
        print('  *** THE ANSWER DEPENDS ON THE NOISE SCALE. ***')
    else:
        print('  The answer is the same under all three scales.')

    json.dump({'warnSigma': WARN_SIGMA,
               'criterion': 'first point >= WARN_SIGMA that is not the last SAFE point',
               'scales': scales,
               'perBoundaryAnyEarlyWarning': arm_warns,
               'detail': {'%s|%s' % (b, k): v for (b, k), v in verdicts.items()}},
              open('results/E1-noise-scale-sensitivity.json', 'w'), indent=2)
    print()
    print('wrote results/E1-noise-scale-sensitivity.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
