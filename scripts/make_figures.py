#!/usr/bin/env python3
"""Generate every Paper 2 figure as vector PDF, from committed data only.

Sized for a two-column IEEE Access layout: 3.4 in single-column, 7.0 in
double-column, 8 pt type, no raster elements anywhere.

Post-A6 values throughout. Where a figure would otherwise use a pre-A6 number
the script recomputes it from results/A6-collapsed-estimator.json.

Usage: python3 scripts/make_figures.py
"""
import json
import os
import sys

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

OUT = 'figures'
COL, WIDE = 3.4, 7.0
INK, MUTE, HI, LO = '#1a1a1a', '#8a8a8a', '#b2182b', '#2166ac'

plt.rcParams.update({
    'font.size': 8, 'axes.labelsize': 8, 'axes.titlesize': 8,
    'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 7,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
    'lines.linewidth': 1.1, 'pdf.fonttype': 42,
})
# No tight bbox: the emitted PDF is exactly the authored canvas, so a figure
# placed at \columnwidth or \textwidth renders its type at the 8 pt it was set
# in. Tight cropping makes the file narrower than the target and the type grows
# when LaTeX scales it back up.

A6 = json.load(open('results/A6-collapsed-estimator.json'))['cells']
CAL = json.load(open('results/E2D-capacity-calibration.json'))['cells']
E2E = json.load(open('results/E2E-analysis.json'))['cells']
ORDER = ['E1 c10/C0', 'E1 c10/C1', 'E2 c10@Q2500',
         'E1 c50/C0', 'E1 c50/C1', 'E2 c50@Q500', 'E2b C=400']
SHORT = {'E1 c10/C0': 'c10/C0', 'E1 c10/C1': 'c10/C1', 'E2 c10@Q2500': 'c10 Q=2500',
         'E1 c50/C0': 'c50/C0', 'E1 c50/C1': 'c50/C1', 'E2 c50@Q500': 'c50 Q=500',
         'E2b C=400': 'E2b C=400'}


def save(fig, name, pad=True):
    p = os.path.join(OUT, name + '.pdf')
    if pad:
        try:
            fig.tight_layout(pad=0.25)
        except Exception:
            pass
    fig.savefig(p)
    plt.close(fig)
    print('  %-28s %6.1f KB' % (p, os.path.getsize(p) / 1024.0))


def cells():
    """(label, configured rho, effective rho) at each cell's last SAFE point."""
    for k in ORDER:
        c = A6[k]
        last = max(c['safePoints'], key=lambda p: p['rl'])
        yield k, c['reported']['rhoAtLastSafe'][1], last['a4Rate'] / c['plateau']


# ---------------------------------------------------------------- F1
def f1():
    fig, ax = plt.subplots(figsize=(WIDE, 2.9))
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)

    def box(x, y, w, h, label, sub=None):
        ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=INK, lw=0.9))
        ax.text(x + w / 2, y + h * (0.63 if sub else 0.5), label, ha='center',
                va='center', fontsize=8)
        if sub:
            ax.text(x + w / 2, y + h * 0.27, sub, ha='center', va='center',
                    fontsize=6.5, color=MUTE)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                     mutation_scale=7, lw=0.8, color=INK,
                                     shrinkA=1, shrinkB=1))

    # live path, top
    box(0.15, 3.05, 1.7, 0.85, 'injector', 'lanes pacer, $\\lambda_L$')
    arrow(1.85, 3.47, 6.75, 3.47)
    ax.text(4.30, 3.60, 'live path: direct HTTP, never enters NATS',
            ha='center', fontsize=6.8, color=MUTE)

    # recovery path, bottom
    box(0.15, 0.95, 1.7, 0.85, 'producer', 'fills during the outage')
    box(2.45, 0.95, 1.5, 0.85, 'NATS', 'JetStream')
    box(4.55, 0.95, 1.6, 0.85, 'consumer', 'rate limit $r_l$')
    arrow(1.85, 1.37, 2.45, 1.37)
    arrow(3.95, 1.37, 4.55, 1.37)
    arrow(6.15, 1.37, 6.75, 1.90)
    ax.text(3.15, 0.72, 'recovery path: backlog drained at $r_l$',
            ha='center', fontsize=6.8, color=MUTE)

    # shared dependency
    box(6.75, 1.55, 1.85, 2.30, 'downstream',
        'conc $= \\lceil C\\cdot S \\rceil$ workers\nqueue cap $Q$')
    arrow(8.60, 2.70, 9.25, 2.70)
    ax.text(9.32, 2.70, 'served', ha='left', va='center', fontsize=7.5)

    # fault reference
    ax.plot([7.68, 7.68], [0.32, 1.55], color=HI, lw=1.0, ls=':')
    ax.plot([7.55, 7.81], [0.32, 0.32], color=HI, lw=1.0)
    ax.text(7.95, 0.32, 'fault: $C$ withdrawn for 120 s.\n'
                        'Restore is $t_0$ for every measurement.',
            ha='left', va='bottom', fontsize=6.8, color=HI)

    ax.text(0.15, 4.30, 'The two paths are independent until the downstream, '
                        'which is the only shared resource.',
            fontsize=7.2, color=INK)
    save(fig, 'F1-architecture', pad=False)


# ---------------------------------------------------------------- F2
def f2():
    fig, ax = plt.subplots(figsize=(WIDE, 2.35))
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.4)

    ax.text(0.0, 3.05, 'What the harness assumes', fontsize=8, weight='bold')
    ax.text(0.0, 2.55, 'concurrency $=\\lceil C\\cdot S\\rceil$ workers, each turning a '
                       'request round in exactly $S$', fontsize=8)
    ax.text(0.0, 2.10, 'so capacity $=$ concurrency $/\\,S = C$', fontsize=8, color=MUTE)

    ax.plot([0, 10], [1.82, 1.82], color=MUTE, lw=0.5)

    ax.text(0.0, 1.45, 'What a worker actually pays', fontsize=8, weight='bold')
    seg = [('timer', 0.0003, MUTE), ('pre', 0.0004, MUTE),
           ('sleep $S$', 5.0, LO), ('overshoot', 0.5156, HI), ('post', 0.0006, MUTE)]
    x, scale = 0.0, 1.60
    for name, w, col in seg:
        ww = max(w * scale, 0.09)
        ax.add_patch(Rectangle((x, 0.62), ww, 0.36, facecolor=col, alpha=0.85, lw=0))
        if w > 0.4:
            ax.text(x + ww / 2, 0.80, name, ha='center', va='center', fontsize=7,
                    color='white')
        x += ww
    ax.annotate('', xy=(x, 0.50), xytext=(0, 0.50),
                arrowprops=dict(arrowstyle='<->', lw=0.7, color=INK))
    ax.text(x / 2, 0.30, 'realised cycle $=S+\\mathrm{ov}$', ha='center', fontsize=7.5)

    ax.text(x + 0.18, 0.80, 'ov $= 0.463$ ms,\nunaccounted for in $C$',
            va='center', fontsize=7.5, color=HI)
    ax.text(0.0, 0.02, 'true capacity $=$ concurrency$/(S+\\mathrm{ov}) = C\\cdot S/(S+'
                       '\\mathrm{ov})$ — the same ov costs proportionally more '
                       'when $S$ is short', fontsize=7.5, color=MUTE)
    save(fig, 'F2-capacity-model', pad=False)


# ---------------------------------------------------------------- F3
def f3():
    d = {s: json.load(open('results/e2e/exp1-s%s-load90.json' % s))['overhead']
         for s in ('5', '25')}
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDE, 2.3),
                                 gridspec_kw={'width_ratios': [1.25, 1]})
    # Components of the `total` field the analysis uses throughout: pre-sleep,
    # sleep overshoot, post-sleep. The worker also pays ~0.0003 ms of runtime
    # timer work per request, which `total` excludes; it is stated in the caption
    # rather than drawn, so the bar height equals the number quoted elsewhere.
    parts = [('preSleep', 'pre-sleep'),
             ('sleepExcess', 'sleep overshoot'), ('postSleep', 'post-sleep')]
    xs = [0, 1]
    bot = [0.0, 0.0]
    cols = {'preSleep': '#aaaaaa', 'sleepExcess': HI, 'postSleep': '#888888'}
    for key, lab in parts:
        v = [d['5'][key]['meanNs'] / 1e6, d['25'][key]['meanNs'] / 1e6]
        ax.bar(xs, v, 0.5, bottom=bot, color=cols[key], label=lab, lw=0)
        bot = [b + y for b, y in zip(bot, v)]
    for i, t in enumerate(bot):
        ax.text(i, t + 0.012, '%.4f ms' % t, ha='center', fontsize=7.5)
    ax.set_xticks(xs)
    ax.set_xticklabels(['$S=5$ ms', '$S=25$ ms'])
    ax.set_ylabel('mean excess per request (ms)')
    ax.set_ylim(0, max(bot) * 1.24)
    ax.legend(frameon=False, loc='lower center', ncol=2, handlelength=1.0,
              columnspacing=0.9, borderpad=0.1)
    ax.set_title('sleep overshoot is 99.8% of it', fontsize=7.5, color=MUTE)

    obs_d, obs_r = bot[1] - bot[0], bot[1] / bot[0]
    bx.axhline(0, color=MUTE, lw=0.5)
    bx.bar([0], [obs_d], 0.42, color=LO, lw=0)
    bx.bar([1], [obs_r], 0.42, color=LO, lw=0)
    bx.plot([-0.28, 0.28], [0, 0], color=HI, lw=1.4)
    bx.plot([0.72, 1.28], [5, 5], color=HI, lw=1.4)
    bx.text(0.30, 0.28, 'constant\npredicts 0', fontsize=7, color=HI, va='center')
    bx.text(1.30, 5.0, 'proportional\npredicts 5.0', fontsize=7, color=HI, va='center')
    bx.text(0, obs_d - 0.42, '%+.4f' % obs_d, ha='center', fontsize=7.5)
    bx.text(1, obs_r + 0.30, '%.3f' % obs_r, ha='center', fontsize=7.5)
    bx.set_xticks([0, 1])
    bx.set_xticklabels(['difference\n(ms)', 'ratio'])
    bx.set_ylim(-0.9, 6.3)
    bx.set_title('constant, not proportional', fontsize=7.5, color=MUTE)
    save(fig, 'F3-overhead-measured')


# ---------------------------------------------------------------- F4
def f4():
    rows = [('c10\nuncorrected', 2000, CAL['E1 c10/C0']['predictedAt046'],
             CAL['E1 c10/C0']['trueCapacity']),
            ('c50\nuncorrected', 2000, CAL['E1 c50/C0']['predictedAt046'],
             CAL['E1 c50/C0']['trueCapacity']),
            ('c10\ncorrected', 2000, E2E['c10']['registered']['predPlateau'],
             E2E['c10']['plateau']),
            ('c50\ncorrected', 2000, E2E['c50']['registered']['predPlateau'],
             E2E['c50']['plateau'])]
    fig, ax = plt.subplots(figsize=(COL, 2.5))
    x = range(len(rows))
    ax.bar([i - 0.19 for i in x], [r[2] for r in rows], 0.36,
           label='predicted', color=MUTE, lw=0)
    ax.bar([i + 0.19 for i in x], [r[3] for r in rows], 0.36,
           label='measured', color=LO, lw=0)
    for i, r in enumerate(rows):
        ax.plot([i - 0.42, i + 0.42], [r[1], r[1]], color=HI, lw=1.0, ls='--')
        err = 100 * (r[3] - r[2]) / r[2]
        ax.text(i, max(r[2], r[3]) + 26, '%+.2f%%' % err, ha='center', fontsize=7)
    ax.text(3.48, 2000, 'configured $C$', color=HI, fontsize=6.8, va='center')
    ax.set_xticks(list(x))
    ax.set_xticklabels([r[0] for r in rows])
    ax.set_ylabel('saturation plateau (rps)')
    ax.set_ylim(1700, 2105)
    ax.legend(frameon=False, loc='lower left', handlelength=1.0)
    save(fig, 'F4-plateau-predicted-measured')


# ---------------------------------------------------------------- F5
def _declutter(vals, gap):
    """Push near-identical label positions apart, preserving order.

    Several cells share a configured utilisation to four decimals, so their
    labels land on top of each other. This spreads them by a minimum gap while
    keeping each within sight of its own point.
    """
    idx = sorted(range(len(vals)), key=lambda i: vals[i])
    out = list(vals)
    for n, i in enumerate(idx):
        if n and out[i] - out[idx[n - 1]] < gap:
            out[i] = out[idx[n - 1]] + gap
    return out


def f5():
    data = list(cells())
    cfg = [c for _, c, _ in data]
    eff = [e for _, _, e in data]
    sc, se = max(cfg) - min(cfg), max(eff) - min(eff)

    fig, ax = plt.subplots(figsize=(WIDE, 3.2))
    lab_y = _declutter(cfg, 0.0060)
    for i, (k, c, e) in enumerate(data):
        col = LO if 'c10' in k else (HI if 'c50' in k else '#7a3b8f')
        ax.plot([0, 1], [c, e], color=col, lw=0.9, alpha=0.7, zorder=1)
        ax.scatter([0, 1], [c, e], s=24, color=col, zorder=3)
        ax.annotate(SHORT[k], xy=(0, c), xytext=(-0.11, lab_y[i]),
                    ha='right', va='center', fontsize=7, color=col,
                    arrowprops=dict(arrowstyle='-', lw=0.4, color=col,
                                    shrinkA=0, shrinkB=2) if abs(lab_y[i] - c) > 1e-4
                    else None)

    for xx, lo, hi, val, side, dx in [(0, min(cfg), max(cfg), sc, -1, 0.34),
                                      (1, min(eff), max(eff), se, +1, 0.10)]:
        bx = xx + dx * side
        ax.plot([bx, bx], [lo, hi], color=INK, lw=1.3)
        for y in (lo, hi):
            ax.plot([bx - 0.02, bx + 0.02], [y, y], color=INK, lw=1.3)
        ax.text(bx + 0.035 * side, (lo + hi) / 2, 'spread\n%.4f' % val,
                ha='left' if side > 0 else 'right', va='center',
                fontsize=8, weight='bold')

    ax.set_xlim(-0.62, 1.46)
    ax.set_ylim(0.900, 1.012)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['against configured $C$', 'against measured true capacity'])
    ax.set_ylabel('utilisation at the last SAFE point')
    ax.axhline(1.0, color=MUTE, lw=0.5, ls=':', zorder=0)
    ax.set_title('the same seven boundaries, divided by the wrong capacity and by the right one:\n'
                 'spread %.4f collapses to %.4f, a factor of %.1f' % (sc, se, sc / se),
                 fontsize=8)
    save(fig, 'F5-collapse')
    return sc, se


# ---------------------------------------------------------------- F6
def f6():
    pts = [p for p in E2E['c10']['points']]
    rho = [p['rho'] for p in pts]
    q = [p['queuePeak'] for p in pts]
    lat = [p['liveP99Ms'] for p in pts]
    safe = [p['class'] == 'SAFE' for p in pts]

    fig, ax = plt.subplots(figsize=(COL, 2.6))
    bx = ax.twinx()
    bx.spines['right'].set_visible(True)
    ax.plot(rho, q, 'o-', color=LO, ms=4, label='queue peak (left)')
    bx.plot(rho, lat, 's--', color=HI, ms=4, label='live p99 (right)')
    ax.axhline(500, color=LO, lw=0.5, ls=':')
    ax.text(rho[0], 512, 'queue cap 500', fontsize=6.5, color=LO)
    bx.axhline(250, color=HI, lw=0.5, ls=':')
    bx.text(rho[-1], 268, 'SLO 250 ms', fontsize=6.5, color=HI, ha='right')

    edge = (max(r for r, s in zip(rho, safe) if s)
            + min(r for r, s in zip(rho, safe) if not s)) / 2
    ax.axvspan(edge, max(rho) + 0.001, color='#f2f2f2', zorder=0)
    ax.text(edge + 0.0004, 430, 'non-SAFE', fontsize=7, color=MUTE)

    ax.set_xlabel('achieved utilisation approaching the boundary')
    ax.set_ylabel('drain queue peak (requests)', color=LO)
    bx.set_ylabel('live p99 (ms)', color=HI)
    ax.tick_params(axis='y', colors=LO)
    bx.tick_params(axis='y', colors=HI)
    ax.set_xlim(min(rho) - 0.001, max(rho) + 0.001)
    ax.set_title('both signals are flat until the last safe point, then cliff',
                 fontsize=7.5, color=MUTE)
    save(fig, 'F6-signal-selection')


def main():
    os.makedirs(OUT, exist_ok=True)
    print('writing figures/')
    f1(); f2(); f3(); f4()
    sc, se = f5()
    f6()
    print()
    print('F5 collapse: %.4f -> %.4f (%.1fx), post-A6' % (sc, se, sc / se))
    return 0


if __name__ == '__main__':
    sys.exit(main())
