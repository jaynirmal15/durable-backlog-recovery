#!/usr/bin/env python3
"""Does anything warn before the boundary? Analysis of the E1 SAFE points.

E1 established where the boundaries are. It did not test whether any observable
rises before one, which is what the controller argument rests on: a controller
can only act on a signal it can see coming.

For every SAFE point in all four boundaries this extracts six drain-window
observables and asks, per arm and capacity, whether any of them rises across the
safe range by more than its own run-to-run noise.

The noise scale matters more than the trend. A metric that climbs 3 ms while
repetitions of the same point scatter by 4 ms has not warned of anything, and
several of these metrics are quantised to whole milliseconds, so an apparent
zero-variance signal is an artefact of the quantisation rather than evidence of
precision. Both guards are applied below.

Usage:
  python3 scripts/leading_indicator.py                    # table
  python3 scripts/leading_indicator.py --svg results/figs # also write plots
"""
import argparse
import json
import os
import statistics
import sys

BOUNDARIES = ['c10-C0', 'c10-C1', 'c50-C0', 'c50-C1']

# metric key -> (label, unit, quantisation floor for the noise estimate)
#
# The floor exists because a percentile reported in whole milliseconds can show
# zero spread across repetitions purely because the true spread is under one
# millisecond. Dividing a rise by that zero would manufacture an arbitrarily
# strong "signal". Half a quantum is the smallest defensible noise scale.
METRICS = [
    ('p50',      'live p50',        'ms',   0.5),
    ('p90',      'live p90',        'ms',   0.5),
    ('p99',      'live p99',        'ms',   0.5),
    ('qMean',    'mean queue depth', 'req', 0.05),
    ('ifMean',   'mean in-flight',   'req', 0.05),
    ('timeout',  'timeout rate',     '',    1e-6),
]

# A rise must clear this many pooled standard deviations across the safe range
# to count as a usable warning. Three is the conventional detection bar and is
# fixed here before looking at the numbers.
WARN_SIGMA = 3.0


def drain_inflight_mean(rec):
    """Mean live in-flight over the drain window, from the timeline."""
    td = rec.get('tDrainSec') or 0
    vals = [p.get('liveInFlight', 0) for p in rec.get('timeline', [])
            if td <= 0 or p.get('tSec', 0) <= td + 0.5]
    return statistics.mean(vals) if vals else 0.0


def extract(run_id):
    rec = json.load(open('results/%s.json' % run_id))
    s = rec['supplementary']
    return {
        'p50': float(s['drainLiveP50Ms']),
        'p90': float(s['drainLiveP90Ms']),
        'p99': float(s['drainLiveP99Ms']),
        'qMean': float(s['drainQueueDepthMean']),
        'ifMean': drain_inflight_mean(rec),
        'timeout': float(s['drainTimeoutRate']),
    }


def collect(boundary):
    """SAFE points for one boundary, ordered by achieved rho."""
    b = json.load(open('results/boundaries/%s.json' % boundary))
    pts = []
    for p in b['points']:
        if p['class'] != 'SAFE':
            continue
        per_run = [extract(r['runId']) for r in p['runs']]
        row = {'rl': p['rl'], 'rho': statistics.mean(p['rhoAchieved']),
               'rhos': p['rhoAchieved'], 'n': len(per_run)}
        for key, _, _, _ in METRICS:
            vals = [r[key] for r in per_run]
            row[key] = {'mean': statistics.mean(vals),
                        'sd': statistics.pstdev(vals) if len(vals) > 1 else 0.0,
                        'vals': vals}
        pts.append(row)
    pts.sort(key=lambda r: r['rho'])
    return b, pts


def analyse(pts, key, floor):
    """Rise across the safe range, in units of its own run-to-run noise.

    The noise scale is the MEDIAN within-point standard deviation, not the mean.
    That matters: at the c10/C0 last-safe point the three repetitions scatter
    enormously (p99 of 223, 24 and 38 ms), and a mean-pooled sigma would let that
    single wild point swamp the noise estimate and hide a real signal that was
    already obvious two points earlier. The median is the run-to-run scatter of a
    typical point on the curve, which is what a rise has to clear to be visible.

    Two different questions get two different answers here:

      riseSigma       how far the signal has moved by a given point, relative to
                      typical scatter. Answers "is there a trend at all".
      detectAtPoint   the same rise divided by the scatter AT THAT POINT.
                      Answers "could a controller taking one sample here tell it
                      apart from deep-safe operation". A bimodal point can have a
                      large trend and still be undetectable in one observation.
    """
    if len(pts) < 2:
        return None
    means = [p[key]['mean'] for p in pts]
    sds = [p[key]['sd'] for p in pts]
    noise = max(statistics.median(sds), floor)
    base = means[0]

    per_point = []
    first_warn = None
    for i, pt in enumerate(pts):
        rise = means[i] - base
        sigma = rise / noise
        det = rise / max(sds[i], floor)
        per_point.append({'rl': pt['rl'], 'rho': round(pt['rho'], 4),
                          'mean': round(means[i], 4), 'sd': round(sds[i], 4),
                          'rise': round(rise, 4), 'riseSigma': round(sigma, 1),
                          'detectAtPoint': round(det, 1)})
        if first_warn is None and i > 0 and sigma >= WARN_SIGMA:
            first_warn = i

    # How much room is left between the first point that warns and the boundary.
    warn_rho = pts[first_warn]['rho'] if first_warn is not None else None
    last_rho = pts[-1]['rho']
    return {
        'first': means[0], 'last': means[-1],
        'total': means[-1] - base, 'totalSigma': (means[-1] - base) / noise,
        'preLast': means[-2] - base, 'preLastSigma': (means[-2] - base) / noise,
        'detectAtLastSafe': (means[-1] - base) / max(sds[-1], floor),
        'noise': noise, 'noiseFloored': statistics.median(sds) < floor,
        'firstWarningRl': pts[first_warn]['rl'] if first_warn is not None else None,
        'firstWarningRho': warn_rho,
        'warningRoomRho': round(last_rho - warn_rho, 4) if warn_rho is not None else None,
        'warningRoomPoints': (len(pts) - 1 - first_warn) if first_warn is not None else None,
        'perPoint': per_point,
        'means': means,
        'monotone': all(means[i] <= means[i + 1] + 1e-12 for i in range(len(means) - 1)),
    }


def svg_plot(path, title, xs, series, xlabel='achieved rho'):
    """Small dependency-free scatter/line plot, one panel per metric."""
    W, H, PAD = 780, 150, 52
    rows = []
    for i, (label, unit, ys, sds) in enumerate(series):
        lo, hi = min(ys), max(ys)
        if hi - lo < 1e-12:
            lo, hi = lo - 1, hi + 1
        span = hi - lo
        lo -= span * 0.15
        hi += span * 0.15
        xlo, xhi = min(xs), max(xs)
        if xhi - xlo < 1e-12:
            xhi = xlo + 1e-6
        px = lambda x: PAD + (x - xlo) / (xhi - xlo) * (W - PAD - 20)
        py = lambda y: (H - 30) - (y - lo) / (hi - lo) * (H - 60)
        pts = ' '.join('%.1f,%.1f' % (px(x), py(y)) for x, y in zip(xs, ys))
        dots = ''.join('<circle cx="%.1f" cy="%.1f" r="3.5" fill="#2b6cb0"/>' % (px(x), py(y))
                       for x, y in zip(xs, ys))
        # error bars at +/- 1 within-point SD
        bars = ''
        for x, y, sd in zip(xs, ys, sds):
            if sd > 0:
                bars += ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#2b6cb0" '
                         'stroke-width="1.2"/>' % (px(x), py(y - sd), px(x), py(y + sd)))
        rows.append(
            '<g transform="translate(0,%d)">'
            '<text x="6" y="14" font-family="system-ui,sans-serif" font-size="12" '
            'font-weight="600" fill="#1a202c">%s%s</text>'
            '<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#cbd5e0"/>'
            '<polyline points="%s" fill="none" stroke="#2b6cb0" stroke-width="1.6"/>'
            '%s%s'
            '<text x="%d" y="%.1f" font-family="system-ui,sans-serif" font-size="10" '
            'fill="#4a5568" text-anchor="end">%.4g</text>'
            '<text x="%d" y="%.1f" font-family="system-ui,sans-serif" font-size="10" '
            'fill="#4a5568" text-anchor="end">%.4g</text>'
            '</g>' % (
                i * H, label, (' (%s)' % unit) if unit else '',
                PAD, H - 28, W - 18, H - 28,
                pts, bars, dots,
                PAD - 6, py(max(ys)), max(ys),
                PAD - 6, py(min(ys)), min(ys)))
    total_h = H * len(series) + 40
    xticks = ''.join(
        '<text x="%.1f" y="%d" font-family="system-ui,sans-serif" font-size="10" '
        'fill="#4a5568" text-anchor="middle">%.4f</text>' % (
            PAD + (x - min(xs)) / max(max(xs) - min(xs), 1e-9) * (W - PAD - 20),
            total_h - 22, x)
        for x in xs)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d"><rect width="%d" height="%d" fill="#ffffff"/>'
           '<text x="6" y="16" font-family="system-ui,sans-serif" font-size="13" '
           'font-weight="700" fill="#1a202c">%s</text>'
           '<g transform="translate(0,22)">%s</g>%s'
           '<text x="%d" y="%d" font-family="system-ui,sans-serif" font-size="11" '
           'fill="#4a5568" text-anchor="middle">%s (SAFE points only; bars are ±1 '
           'within-point SD)</text></svg>' % (
               W, total_h, W, total_h, W, total_h, title, ''.join(rows), xticks,
               W // 2, total_h - 6, xlabel))
    open(path, 'w').write(svg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--svg', help='directory to write per-boundary SVG plots into')
    a = ap.parse_args()
    if a.svg:
        os.makedirs(a.svg, exist_ok=True)

    summary = {}
    for bname in BOUNDARIES:
        b, pts = collect(bname)
        bd = b['boundary']
        print('=' * 78)
        print('%s   SAFE points: %d   last SAFE rl=%d (rho %.4f)   boundary rl [%d, %d] %s'
              % (bname, len(pts), bd['lastSafeRl'], pts[-1]['rho'] if pts else float('nan'),
                 bd['lastSafeRl'], bd['firstNonSafeRl'], bd['firstNonSafeClass']))
        print('%8s %8s | %s' % ('rl', 'rho', ' '.join('%12s' % m[1] for m in METRICS)))
        for p in pts:
            print('%8d %8.4f | %s' % (p['rl'], p['rho'],
                  ' '.join('%12s' % ('%.4g±%.3g' % (p[k]['mean'], p[k]['sd'])) for k, _, _, _ in METRICS)))
        print()
        print('%-18s %9s %9s %10s %10s %9s %8s  %s' % (
            'metric', 'deepSafe', 'lastSafe', 'rise', 'rise/sig', 'detect@LS', 'warns@rl', 'verdict'))
        res = {}
        for key, label, unit, floor in METRICS:
            r = analyse(pts, key, floor)
            if r is None:
                print('%-18s   (only %d SAFE point; no trend computable)' % (label, len(pts)))
                continue
            early = r['firstWarningRl'] is not None and r['warningRoomPoints'] and r['warningRoomPoints'] >= 1
            warns = r['totalSigma'] >= WARN_SIGMA
            if not warns:
                verdict = 'flat'
            elif early:
                verdict = 'WARNS, %d point(s) of room' % r['warningRoomPoints']
            else:
                verdict = 'rises only at the last safe point'
            res[key] = dict(r, warns=warns, early=bool(early), verdict=verdict)
            print('%-18s %9.4g %9.4g %10.4g %10.1f %9.1f %8s  %s' % (
                label, r['first'], r['last'], r['total'], r['totalSigma'],
                r['detectAtLastSafe'], r['firstWarningRl'] or '-', verdict))
        summary[bname] = {'points': pts, 'metrics': res,
                          'lastSafeRl': bd['lastSafeRl'],
                          'boundary': [bd['lastSafeRl'], bd['firstNonSafeRl']]}
        print()

        if a.svg and pts:
            xs = [p['rho'] for p in pts]
            series = [(label, unit, [p[k]['mean'] for p in pts], [p[k]['sd'] for p in pts])
                      for k, label, unit, _ in METRICS]
            svg_plot(os.path.join(a.svg, '%s.svg' % bname),
                     '%s — observables across the SAFE range' % bname, xs, series)

    if a.svg:
        print('plots written to %s/' % a.svg)

    out = {}
    for bname, v in summary.items():
        out[bname] = {
            'lastSafeRl': v['lastSafeRl'], 'boundaryRl': v['boundary'],
            'safePoints': [{'rl': p['rl'], 'rho': round(p['rho'], 4),
                            **{k: {'mean': round(p[k]['mean'], 5), 'sd': round(p[k]['sd'], 5)}
                               for k, _, _, _ in METRICS}} for p in v['points']],
            'trends': {k: {kk: (round(vv, 5) if isinstance(vv, float) else vv)
                           for kk, vv in r.items() if kk != 'means'}
                       for k, r in v['metrics'].items()},
        }
    json.dump({'warnSigma': WARN_SIGMA, 'boundaries': out},
              open('results/E1-leading-indicator.json', 'w'), indent=2)
    print('wrote results/E1-leading-indicator.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
