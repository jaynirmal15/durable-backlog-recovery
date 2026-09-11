#!/usr/bin/env python3
"""Locate the safe-recovery-rate boundary by the pre-registered estimator.

Implements PRE-REGISTRATION.md sections 2-5 and nothing else. The rules are
deliberately mechanical so the boundary is decided in advance rather than by
looking at traces:

  classification (n repetitions per point)
      SAFE      vSLO <= 0.01 in ALL repetitions
      UNSAFE    vSLO >  0.05 in AT LEAST TWO repetitions
      MARGINAL  anything else

  search
      midpoints rounded to 5 rps; SAFE raises the floor, UNSAFE *and MARGINAL*
      lower the ceiling; stop when ceiling - floor <= 5 rps

  reporting
      rho* is the achieved-rho interval [last SAFE, first NON-SAFE], whose
      upper end may be MARGINAL or UNSAFE and whose class is recorded. Never a
      point, never a mean. Repetition disagreement widens the interval.

Nothing here averages vSLO across repetitions, and nothing here narrows an
interval. If you want a point estimate, this is the wrong tool.

Usage:
  locate_boundary.py --arm c10 --regime C0 --anchor 840 --dry-run
  locate_boundary.py --arm c50 --regime C1 --anchor 380 --n 3

Output: results/boundaries/<arm>-<regime>.json
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import time

RESOLUTION_RPS = 5
SAFE_MAX_VSLO = 0.01
UNSAFE_MIN_VSLO = 0.05
UNSAFE_MIN_REPS = 2

# Arms are fixed by the two-level concurrency design. Never mix them in one run.
ARMS = {
    'c10': {'service_time_ms': 5},
    'c50': {'service_time_ms': 25},
}

# Capacity regimes. nominal is C before the fault; fault is C during it.
REGIMES = {
    'C0': {'condition': 'P0-A', 'nominal': 2000, 'fault': 2000},
    'C1': {'condition': 'P0-B', 'nominal': 2000, 'fault': 1400},
    'C2': {'condition': 'P0-C', 'nominal': 2000, 'fault': 1300},
    'C3': {'condition': 'P0-D', 'nominal': 2000, 'fault': 900},
}


# ---------------------------------------------------------------- classification

def classify(vslos):
    """Classify one probed rate from its per-repetition vSLO values.

    PRE-REGISTRATION.md section 2. The three classes are exhaustive and
    mutually exclusive, and UNSAFE is tested before SAFE so a point with two
    collapsed runs and one clean run is UNSAFE rather than MARGINAL.
    """
    if not vslos:
        raise ValueError('classify() needs at least one vSLO value')
    n_unsafe = sum(1 for v in vslos if v > UNSAFE_MIN_VSLO)
    if n_unsafe >= UNSAFE_MIN_REPS:
        return 'UNSAFE'
    if all(v <= SAFE_MAX_VSLO for v in vslos):
        return 'SAFE'
    return 'MARGINAL'


def bisect_step(lo, hi):
    """Next rate to probe between a SAFE floor and a non-SAFE ceiling.

    Returns None once the interval is at or below the 5 rps resolution floor.
    The midpoint is rounded to the nearest 5 and clamped strictly inside the
    interval so the search always makes progress.
    """
    if hi - lo <= RESOLUTION_RPS:
        return None
    mid = int(round((lo + hi) / 2.0 / RESOLUTION_RPS) * RESOLUTION_RPS)
    if mid <= lo:
        mid = lo + RESOLUTION_RPS
    if mid >= hi:
        mid = hi - RESOLUTION_RPS
    if mid <= lo or mid >= hi:
        return None
    return mid


def upward_step(lo):
    """First ceiling candidate when no non-SAFE ceiling is known: +10%, to 5 rps."""
    step = max(RESOLUTION_RPS, int(round(lo * 0.10 / RESOLUTION_RPS) * RESOLUTION_RPS))
    return lo + step


def downward_step(hi):
    """Next floor candidate when the anchor itself is not SAFE: -10%, to 5 rps.

    Symmetric to upward_step. Needed because Phase 1 anchors were measured on
    the harness with the spin-wait admission defect, and the 2026-08-19 notes
    predict the c50 anchor will not survive the fix -- so a search may have to
    start by going down before it can bracket anything.
    """
    step = max(RESOLUTION_RPS, int(round(hi * 0.10 / RESOLUTION_RPS) * RESOLUTION_RPS))
    return max(RESOLUTION_RPS, hi - step)


def plan(anchor, hi=None, oracle=None, max_probes=24):
    """Probe sequence the search would follow.

    With no oracle this is the dry-run plan: it can only show the upward search
    (every probe assumed to continue) because later probes depend on outcomes.
    With an oracle -- a callable rate -> class -- it returns the real sequence,
    which is what the unit tests exercise.
    """
    seq = []
    lo = anchor
    ceiling = hi
    probes = 0
    if oracle is not None and ceiling is None:
        # If the anchor itself is not SAFE it cannot be the floor: descend.
        anchor_cls = oracle(lo)
        if anchor_cls != 'SAFE':
            seq.append({'rl': lo, 'phase': 'anchor', 'class': anchor_cls})
            ceiling = lo
            while probes < max_probes:
                cand = downward_step(ceiling)
                probes += 1
                if cand >= ceiling:
                    break
                cls = oracle(cand)
                seq.append({'rl': cand, 'phase': 'downward', 'class': cls})
                if cls == 'SAFE':
                    lo = cand
                    break
                ceiling = cand
            else:
                return seq, None, ceiling
            if lo == anchor:
                return seq, None, ceiling
    if ceiling is None:
        while probes < max_probes:
            cand = upward_step(lo)
            probes += 1
            if oracle is None:
                seq.append({'rl': cand, 'phase': 'upward', 'class': None})
                return seq, lo, None
            cls = oracle(cand)
            seq.append({'rl': cand, 'phase': 'upward', 'class': cls})
            if cls == 'SAFE':
                lo = cand
                continue
            ceiling = cand
            break
        else:
            return seq, lo, None
    while probes < max_probes:
        mid = bisect_step(lo, ceiling)
        if mid is None:
            break
        probes += 1
        if oracle is None:
            seq.append({'rl': mid, 'phase': 'bisect', 'class': None})
            return seq, lo, ceiling
        cls = oracle(mid)
        seq.append({'rl': mid, 'phase': 'bisect', 'class': cls})
        if cls == 'SAFE':
            lo = mid
        else:
            # MARGINAL lowers the ceiling exactly as UNSAFE does: the boundary
            # is the last unambiguously safe point, so marginal behaviour must
            # fall inside the reported interval.
            ceiling = mid
    return seq, lo, ceiling


# ---------------------------------------------------------------- run records

def record_path(results_dir, run_id):
    return os.path.join(results_dir, '%s.json' % run_id)


def load_record(results_dir, run_id):
    with open(record_path(results_dir, run_id)) as fh:
        return json.load(fh)


def fault_capacity(rec):
    nominal = rec['params'].get('nominalCapacity', 2000)
    for step in rec.get('capacitySchedule', []):
        if step['rate'] < nominal:
            return step['rate']
    return nominal


def achieved_rho(rec):
    """rho from measured delivered rates (PRE-REGISTRATION.md section 5).

    Live comes from the injector's own issue counter over the drain window;
    recovery from messages actually acked. Never from the configured flags.
    """
    drain = rec.get('tDrainSec') or 0
    timeline = rec.get('timeline') or []
    drain_points = [p for p in timeline if p.get('tSec', 0) <= drain] or timeline
    inj = [p['injRate'] for p in drain_points if p.get('injRate')]
    live = statistics.median(inj) if inj else 0.0
    recovery = (rec['backlogAtRestore'] / drain) if drain > 0 else 0.0
    cap = fault_capacity(rec)
    rho = (live + recovery) / cap if cap else 0.0
    return {
        'liveAchievedRps': round(live, 2),
        'recoveryAchievedRps': round(recovery, 2),
        'faultCapacity': cap,
        'rhoAchieved': round(rho, 4),
        'rhoNominal': round(
            (rec['params'].get('liveRatePerSec', 0) + rec['params'].get('rateLimitRps', 0)) / cap, 4
        ) if cap else None,
    }


def summarise_run(rec):
    sup = rec.get('supplementary') or {}
    out = achieved_rho(rec)
    out.update({
        'runId': rec['runId'],
        'gitCommit': rec.get('gitCommit'),
        'gitDirty': rec.get('gitDirty'),
        'vSLO': rec.get('vSLO'),
        'vSLO_raw': rec.get('vSLO_raw'),
        'vSLO_latency': rec.get('vSLO_latency'),
        'vSLO_error': rec.get('vSLO_error'),
        'tDrainSec': rec.get('tDrainSec'),
        'tDrainReached': rec.get('tDrainReached'),
        'stallSeconds': rec.get('stallSeconds'),
        'drainLiveP50Ms': sup.get('drainLiveP50Ms'),
        'drainLiveP99Ms': sup.get('drainLiveP99Ms'),
        'drainQueueDepthMean': sup.get('drainQueueDepthMean'),
        'invalid': rec.get('invalid', False),
        'invalidReason': rec.get('invalidReason'),
    })
    return out


# ---------------------------------------------------------------- driving runs

def runner_argv(args, rl, run_id):
    regime = REGIMES[args.regime]
    argv = [
        args.runner,
        '-condition', regime['condition'],
        '-run-id', run_id,
        '-arm', args.arm,
        '-service-time-ms', str(ARMS[args.arm]['service_time_ms']),
        '-capacity', str(regime['nominal']),
        '-live-rate', str(args.live_rate),
        '-outage', str(args.outage),
        '-workers', str(args.workers),
        '-rate-limit', str(rl),
        '-nats', args.nats,
        '-downstream', args.downstream,
        '-results', args.results,
    ]
    if args.profile:
        argv += ['-profile', args.profile]
    return argv


def probe(args, rl, log):
    """Run n repetitions at one rate and classify. Returns the point dict."""
    runs = []
    for rep in range(1, args.n + 1):
        run_id = '%s-%s-rl%d-r%d' % (args.arm, args.regime.lower(), rl, rep)
        argv = runner_argv(args, rl, run_id)
        log('    run %s' % run_id)
        started = time.time()
        proc = subprocess.run(argv, capture_output=True, text=True)
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or '').strip().split('\n')[-3:]
            raise SystemExit(
                'runner failed for %s (exit %d):\n  %s' % (run_id, proc.returncode, '\n  '.join(tail))
            )
        rec = load_record(args.results, run_id)
        summary = summarise_run(rec)
        summary['wallSeconds'] = round(time.time() - started, 1)
        runs.append(summary)
        log('      vSLO=%.4f rho_ach=%.4f tDrain=%.1f%s' % (
            summary['vSLO'] or 0, summary['rhoAchieved'], summary['tDrainSec'] or -1,
            ' INVALID:%s' % summary['invalidReason'] if summary['invalid'] else ''))

    invalid = [r for r in runs if r['invalid']]
    if invalid:
        raise SystemExit(
            'rate %d has %d invalid run(s) (%s). Invalid runs are retained, never '
            'silently dropped: re-run them before the search continues.'
            % (rl, len(invalid), ', '.join(r['invalidReason'] or '?' for r in invalid))
        )
    vslos = [r['vSLO'] for r in runs]
    return {
        'rl': rl,
        'class': classify(vslos),
        'vSLO': vslos,
        'rhoAchieved': [r['rhoAchieved'] for r in runs],
        'runs': runs,
    }


def search(args, log):
    points = []
    by_rate = {}

    def probe_once(rl):
        if rl in by_rate:
            return by_rate[rl]
        pt = probe(args, rl, log)
        by_rate[rl] = pt
        points.append(pt)
        log('  rate %d -> %s (vSLO %s)' % (rl, pt['class'], ', '.join('%.4f' % v for v in pt['vSLO'])))
        return pt

    log('verifying the anchor at rl=%d' % args.anchor)
    anchor_pt = probe_once(args.anchor)
    lo = args.anchor
    hi = args.hi
    if anchor_pt['class'] != 'SAFE':
        # The anchor is not a floor. It becomes the ceiling and the search
        # descends until it finds one. Phase 1 anchors were measured on the
        # defective harness, so this is an expected outcome, not an error.
        log('  anchor rl=%d classified %s, not SAFE: extending DOWNWARD' % (args.anchor, anchor_pt['class']))
        hi = args.anchor
        lo = None
        while True:
            cand = downward_step(hi)
            if cand >= hi:
                raise SystemExit(
                    'downward search reached the %d rps floor without finding a SAFE point '
                    'below rl=%d. No safe recovery rate exists at this condition on the '
                    'measurable grid; report that rather than forcing an interval.'
                    % (RESOLUTION_RPS, args.anchor))
            pt = probe_once(cand)
            if pt['class'] == 'SAFE':
                lo = cand
                break
            hi = cand
        log('  found a SAFE floor at rl=%d; ceiling is rl=%d (%s)' % (lo, hi, by_rate[hi]['class']))
    if hi is not None:
        hi_pt = probe_once(hi)
        if hi_pt['class'] == 'SAFE':
            log('  supplied ceiling %d is SAFE; falling back to upward search' % hi)
            lo, hi = hi, None

    if hi is None:
        log('no UNSAFE ceiling known: stepping upward in 10% increments')
        while True:
            cand = upward_step(lo)
            pt = probe_once(cand)
            if pt['class'] == 'SAFE':
                lo = cand
                continue
            hi = cand
            break

    log('bisecting between %d (SAFE) and %d (%s)' % (lo, hi, by_rate[hi]['class']))
    while True:
        mid = bisect_step(lo, hi)
        if mid is None:
            break
        pt = probe_once(mid)
        if pt['class'] == 'SAFE':
            lo = mid
        else:
            hi = mid
    return points, lo, hi, by_rate


def build_output(args, points, lo, hi, by_rate):
    lo_pt, hi_pt = by_rate[lo], by_rate[hi]
    # The interval spans every achieved rho seen at each endpoint, so repetition
    # disagreement widens it rather than being averaged away.
    lo_rhos, hi_rhos = lo_pt['rhoAchieved'], hi_pt['rhoAchieved']
    marginal = [p['rl'] for p in points if p['class'] == 'MARGINAL']
    p99s = [r['drainLiveP99Ms'] for r in lo_pt['runs'] if r['drainLiveP99Ms'] is not None]
    latency = None
    if args.baseline_p99 and p99s:
        worst = max(p99s)
        ratio = worst / args.baseline_p99
        latency = {
            'baselineP99Ms': args.baseline_p99,
            'lastSafeP99Ms': worst,
            'ratio': round(ratio, 3),
            'latencyInvisible': ratio <= 1.20,
            'rule': 'p99 at the last SAFE point within 20% of the healthy baseline',
        }
    return {
        'arm': args.arm,
        'regime': args.regime,
        'generatedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'preRegistration': {
            'document': 'PRE-REGISTRATION.md',
            'safeMaxVSLO': SAFE_MAX_VSLO,
            'unsafeMinVSLO': UNSAFE_MIN_VSLO,
            'unsafeMinReps': UNSAFE_MIN_REPS,
            'resolutionRps': RESOLUTION_RPS,
            'repetitions': args.n,
        },
        'boundary': {
            'lastSafeRl': lo,
            'firstNonSafeRl': hi,
            'firstNonSafeClass': hi_pt['class'],
            'rhoStarInterval': [min(lo_rhos), max(hi_rhos)],
            'rhoIntervalWidth': round(max(hi_rhos) - min(lo_rhos), 4),
            'resolutionReachedRps': hi - lo,
            'marginalRates': marginal,
            'note': 'rho* is this interval; its upper end is the first non-SAFE point, '
                    'whose class is firstNonSafeClass. It is not a point and must not be '
                    'averaged, narrowed, or quoted to more figures than its width supports.',
        },
        'latencyInvisibility': latency,
        'points': sorted(points, key=lambda p: p['rl']),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--arm', required=True, choices=sorted(ARMS))
    ap.add_argument('--regime', required=True, choices=sorted(REGIMES))
    ap.add_argument('--anchor', required=True, type=int, help='last SAFE rate to start from')
    ap.add_argument('--hi', type=int, help='known first non-SAFE rate (MARGINAL or UNSAFE), if any')
    ap.add_argument('--n', type=int, default=3, help='repetitions per point (default 3)')
    ap.add_argument('--baseline-p99', type=float, help='healthy-baseline live p99 ms for the invisibility test')
    ap.add_argument('--live-rate', type=int, default=1000)
    ap.add_argument('--outage', type=int, default=120)
    ap.add_argument('--workers', type=int, default=1024)
    ap.add_argument('--profile', default='graceful')
    ap.add_argument('--nats', default='nats://127.0.0.1:14222')
    ap.add_argument('--downstream', default='http://127.0.0.1:8080')
    ap.add_argument('--runner', default='./bin/runner')
    ap.add_argument('--results', default='results')
    ap.add_argument('--out-dir', default='results/boundaries')
    ap.add_argument('--dry-run', action='store_true', help='print the probe sequence and exit')
    args = ap.parse_args()

    log = lambda m: print(m, flush=True)

    if args.dry_run:
        seq, lo, hi = plan(args.anchor, args.hi)
        print('DRY RUN — %s / %s, anchor rl=%d, n=%d' % (args.arm, args.regime, args.anchor, args.n))
        print('  condition %s, C %d -> %d at fault, S=%d ms'
              % (REGIMES[args.regime]['condition'], REGIMES[args.regime]['nominal'],
                 REGIMES[args.regime]['fault'], ARMS[args.arm]['service_time_ms']))
        print('  classification: SAFE vSLO<=%.2f all %d; UNSAFE vSLO>%.2f in >=%d; else MARGINAL'
              % (SAFE_MAX_VSLO, args.n, UNSAFE_MIN_VSLO, UNSAFE_MIN_REPS))
        print('  stop at %d rps resolution' % RESOLUTION_RPS)
        print()
        print('  probe 1: rl=%d x%d   verify the anchor is SAFE on this harness' % (args.anchor, args.n))
        nxt = seq[0] if seq else None
        if nxt:
            print('  probe 2: rl=%d x%d   %s' % (
                nxt['rl'], args.n,
                'first ceiling candidate (+10%)' if nxt['phase'] == 'upward' else 'bisection midpoint'))
        print('  probes 3+: determined by outcomes; bisection continues until the')
        print('             interval is <= %d rps. MARGINAL lowers the ceiling.' % RESOLUTION_RPS)
        print()
        print('  runs: %d per probe, ~%d s each at outage=%d' % (args.n, args.outage * 3, args.outage))
        print('  writes: %s/%s-%s.json' % (args.out_dir, args.arm, args.regime))
        print()
        print('  runner argv for the first probe:')
        print('    ' + ' '.join(runner_argv(args, args.anchor, '%s-%s-rl%d-r1' % (args.arm, args.regime.lower(), args.anchor))))
        return 0

    points, lo, hi, by_rate = search(args, log)
    out = build_output(args, points, lo, hi, by_rate)
    os.makedirs(args.out_dir, exist_ok=True)
    dest = os.path.join(args.out_dir, '%s-%s.json' % (args.arm, args.regime))
    with open(dest, 'w') as fh:
        json.dump(out, fh, indent=2)
        fh.write('\n')
    b = out['boundary']
    log('')
    log('boundary: last SAFE rl=%d, first non-SAFE rl=%d classified %s (resolution %d rps)'
        % (b['lastSafeRl'], b['firstNonSafeRl'], b['firstNonSafeClass'], b['resolutionReachedRps']))
    log('rho* interval: [%.4f, %.4f]  width %.4f' % (
        b['rhoStarInterval'][0], b['rhoStarInterval'][1], b['rhoIntervalWidth']))
    if b['marginalRates']:
        log('MARGINAL rates inside the interval: %s' % b['marginalRates'])
    log('wrote %s' % dest)
    return 0


if __name__ == '__main__':
    sys.exit(main())
