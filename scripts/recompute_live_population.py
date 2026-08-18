#!/usr/bin/env python3
"""Offline live-population correction for Gate 0 main-campaign runs.

Populations (post-restore only):
  injector_live — class=live, age_ms==0  (direct HTTP; SLO population)
  nats_live     — class=live, age_ms>0   (JetStream post-epoch)
  recovery      — class=recovery

Recomputes injector-only liveRps / p99 / error rate / V_SLO from JSONL.
Does not re-run the campaign.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SLO_P99 = 250.0
SLO_ERR = 0.01
RUNS = [f"{c}-r{i}" for c in ("p0a", "p0b", "p0c", "p0d") for i in (1, 2, 3)]


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def metrics(lats: list[float], statuses: list[int]) -> dict:
    # Exclude 429 from error accounting (injector client drops).
    usable = [(lat, st) for lat, st in zip(lats, statuses) if st != 429]
    if not usable:
        return {
            "count": len(lats),
            "count_excl_429": 0,
            "p50": float("nan"),
            "p95": float("nan"),
            "p99": float("nan"),
            "errorRate": float("nan"),
        }
    l2 = sorted(x[0] for x in usable)
    errs = sum(1 for _, st in usable if st != 200)
    return {
        "count": len(lats),
        "count_excl_429": len(usable),
        "p50": percentile(l2, 50),
        "p95": percentile(l2, 95),
        "p99": percentile(l2, 99),
        "errorRate": errs / len(usable),
    }


def load_samples(run_id: str, restore_epoch_ms: int) -> dict[str, list]:
    path = RESULTS / f"{run_id}-consumer.jsonl"
    pops = {
        "injector_live": {"ts": [], "lat": [], "st": []},
        "nats_live": {"ts": [], "lat": [], "st": []},
        "recovery": {"ts": [], "lat": [], "st": []},
    }
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            s = json.loads(line)
            ts = int(s["ts"])
            if ts < restore_epoch_ms:
                continue  # warmup / pre-restore
            cls = s.get("class")
            age = int(s.get("age_ms") or 0)
            lat = float(s.get("latency_ms") or 0)
            st = int(s.get("status") or 0)
            if cls == "recovery":
                key = "recovery"
            elif cls == "live" and age == 0:
                key = "injector_live"
            elif cls == "live":
                key = "nats_live"
            else:
                continue
            pops[key]["ts"].append(ts)
            pops[key]["lat"].append(lat)
            pops[key]["st"].append(st)
    return pops


def window_metrics(ts: list[int], lat: list[float], st: list[int], t_ms: int, window_ms: int = 5000):
    lo = t_ms - window_ms
    lats, sts = [], []
    # samples are roughly time-ordered; scan from end would be faster but lists are per-pop
    for i in range(len(ts) - 1, -1, -1):
        if ts[i] > t_ms:
            continue
        if ts[i] < lo:
            break
        if st[i] == 429:
            continue
        lats.append(lat[i])
        sts.append(st[i])
    if not lats:
        return 0.0, float("nan"), float("nan")
    rps = len(lats) / (window_ms / 1000.0)
    m = metrics(lats, sts)
    return rps, m["p99"], m["errorRate"]


def analyze_run(run_id: str) -> dict:
    rec = json.loads((RESULTS / f"{run_id}.json").read_text())
    epoch = int(rec["restoreEpochMs"])
    t_drain = float(rec.get("tDrainSec") or 0)
    t_full = float(rec.get("tFullSec") or 0)
    pops = load_samples(run_id, epoch)

    # Population summary over drain window [epoch, epoch+t_drain]
    drain_end = epoch + int(t_drain * 1000)
    full_end = epoch + int(t_full * 1000)

    def slice_pop(key: str, t0: int, t1: int):
        ts, lat, st = pops[key]["ts"], pops[key]["lat"], pops[key]["st"]
        sl_lat, sl_st = [], []
        for i, t in enumerate(ts):
            if t0 <= t <= t1:
                sl_lat.append(lat[i])
                sl_st.append(st[i])
        dur = max((t1 - t0) / 1000.0, 1e-9)
        m = metrics(sl_lat, sl_st)
        # mean rps uses all samples including 429 for attempt rate; excl for SLO
        return {
            "count": len(sl_lat),
            "meanRps": len(sl_lat) / dur,
            "p50": m["p50"],
            "p95": m["p95"],
            "p99": m["p99"],
            "errorRate": m["errorRate"],
        }

    pop_drain = {
        "injector_live": slice_pop("injector_live", epoch, drain_end),
        "nats_live": slice_pop("nats_live", epoch, drain_end),
        "recovery": slice_pop("recovery", epoch, drain_end),
    }
    pop_full = {
        "injector_live": slice_pop("injector_live", epoch, full_end),
        "nats_live": slice_pop("nats_live", epoch, full_end),
        "recovery": slice_pop("recovery", epoch, full_end),
    }

    # Original blended metrics from timeline (drain + full peaks / means)
    tl = rec.get("timeline") or []
    drain_tl = [p for p in tl if p.get("tSec", 0) <= t_drain + 0.5]
    old_peak_live = max((p.get("liveRps") or 0) for p in drain_tl) if drain_tl else float("nan")
    old_mean_live = (
        sum(p.get("liveRps") or 0 for p in drain_tl) / len(drain_tl) if drain_tl else float("nan")
    )
    old_peak_p99 = max((p.get("liveP99Ms") or 0) for p in drain_tl) if drain_tl else float("nan")
    # mean of per-second p99 (not global)
    old_mean_p99 = (
        sum(p.get("liveP99Ms") or 0 for p in drain_tl) / len(drain_tl) if drain_tl else float("nan")
    )
    old_vslo = float(rec.get("vSLO") or 0)

    # Recompute V_SLO and per-second injector series aligned to timeline
    inj = pops["injector_live"]
    new_timeline = []
    viol = 0
    seconds = 0
    for pt in tl:
        t_sec = float(pt["tSec"])
        t_ms = epoch + int(t_sec * 1000)
        live_rps, live_p99, live_err = window_metrics(inj["ts"], inj["lat"], inj["st"], t_ms)
        nats_rps, nats_p99, nats_err = window_metrics(
            pops["nats_live"]["ts"], pops["nats_live"]["lat"], pops["nats_live"]["st"], t_ms
        )
        rec_rps, rec_p99, _ = window_metrics(
            pops["recovery"]["ts"], pops["recovery"]["lat"], pops["recovery"]["st"], t_ms
        )
        # Injector-only SLO: only count seconds where injector produced samples
        # (injector runs restore→T_drain). After stop, use NATS-live for
        # post-drain health continuity — but V_SLO_injectorActive uses injector
        # window only.
        entry = {
            "tSec": t_sec,
            "injectorLiveRps": live_rps,
            "injectorLiveP99Ms": live_p99,
            "injectorLiveErrorRate": live_err,
            "natsLiveRps": nats_rps,
            "natsLiveP99Ms": nats_p99,
            "natsLiveErrorRate": nats_err,
            "recoveryRps": rec_rps,
            "recoveryP99Ms": rec_p99,
            "queued": pt.get("queued"),
            "timedOut": pt.get("timedOut"),
            "served": pt.get("served"),
            "trueCapacity": pt.get("trueCapacity"),
            "recoveryRemaining": pt.get("recoveryRemaining"),
            "oldLiveRps": pt.get("liveRps"),
            "oldLiveP99Ms": pt.get("liveP99Ms"),
            "oldErrorRate": pt.get("errorRate"),
        }
        new_timeline.append(entry)

        if t_sec <= t_full + 0.5:
            # Prefer injector when it has signal; else (post-drain) NATS-live.
            if not math.isnan(live_p99) and live_rps > 0:
                seconds += 1
                if live_p99 > SLO_P99 or (not math.isnan(live_err) and live_err > SLO_ERR):
                    viol += 1
            elif t_sec > t_drain and not math.isnan(nats_p99) and nats_rps > 0:
                seconds += 1
                if nats_p99 > SLO_P99 or (not math.isnan(nats_err) and nats_err > SLO_ERR):
                    viol += 1

    vslo_corrected = (viol / seconds) if seconds else float("nan")

    # Injector-active-only V_SLO (drain window)
    viol_d = sec_d = 0
    for e in new_timeline:
        if e["tSec"] > t_drain + 0.5:
            break
        if e["injectorLiveRps"] > 0 and not math.isnan(e["injectorLiveP99Ms"]):
            sec_d += 1
            if e["injectorLiveP99Ms"] > SLO_P99 or (
                not math.isnan(e["injectorLiveErrorRate"]) and e["injectorLiveErrorRate"] > SLO_ERR
            ):
                viol_d += 1
    vslo_drain = (viol_d / sec_d) if sec_d else float("nan")

    inj_drain = pop_drain["injector_live"]
    # Timeout rate from timeline counters
    if tl:
        t0, t1 = tl[0], tl[-1]
        d_served = (t1.get("served") or 0) - (t0.get("served") or 0)
        d_to = (t1.get("timedOut") or 0) - (t0.get("timedOut") or 0)
        # served counter includes successes; timedOut is separate — rate vs attempts
        timeout_rate = d_to / (d_served + d_to) if (d_served + d_to) > 0 else float("nan")
    else:
        d_served = d_to = 0
        timeout_rate = float("nan")

    return {
        "runId": run_id,
        "condition": rec.get("condition"),
        "liveSLOPopulation": "injector_direct",
        "tDrainSec": t_drain,
        "tFullSec": t_full,
        "gapSec": t_full - t_drain,
        "backlogAtRestore": rec.get("backlogAtRestore"),
        "injectorCompleted_param": (rec.get("params") or {}).get("injectorCompleted"),
        "injector_live_count_post_restore": len(pops["injector_live"]["ts"]),
        "populations_drain": pop_drain,
        "populations_full": pop_full,
        "old": {
            "vSLO": old_vslo,
            "drainPeakLiveRps": old_peak_live,
            "drainMeanLiveRps": old_mean_live,
            "drainPeakLiveP99Ms": old_peak_p99,
            "drainMeanLiveP99Ms": old_mean_p99,
        },
        "new": {
            "vSLO": vslo_corrected,
            "vSLO_drainInjectorOnly": vslo_drain,
            "drainMeanInjectorRps": inj_drain["meanRps"],
            "drainInjectorP50": inj_drain["p50"],
            "drainInjectorP95": inj_drain["p95"],
            "drainInjectorP99": inj_drain["p99"],
            "drainInjectorErrorRate": inj_drain["errorRate"],
            "drainMeanNatsRps": pop_drain["nats_live"]["meanRps"],
            "drainNatsP99": pop_drain["nats_live"]["p99"],
            "drainNatsErrorRate": pop_drain["nats_live"]["errorRate"],
            "drainMeanRecoveryRps": pop_drain["recovery"]["meanRps"],
            "drainRecoveryP99": pop_drain["recovery"]["p99"],
        },
        "downstream": {
            "deltaServed": d_served,
            "deltaTimedOut": d_to,
            "timeoutRate": timeout_rate,
        },
        "timelineCorrected": new_timeline,
    }


def p0b_gap_report(analysis: dict) -> dict:
    """Queue / timeout / injector p99 during T_drain → T_full."""
    td, tf = analysis["tDrainSec"], analysis["tFullSec"]
    gap = [e for e in analysis["timelineCorrected"] if td - 0.5 <= e["tSec"] <= tf + 0.5]
    if not gap:
        return {}
    # delta timeouts in gap
    to0 = gap[0].get("timedOut") or 0
    to1 = gap[-1].get("timedOut") or 0
    sv0 = gap[0].get("served") or 0
    sv1 = gap[-1].get("served") or 0
    queued = [e.get("queued") or 0 for e in gap]
    inj_p99 = [e["injectorLiveP99Ms"] for e in gap if not math.isnan(e["injectorLiveP99Ms"])]
    nats_p99 = [e["natsLiveP99Ms"] for e in gap if not math.isnan(e["natsLiveP99Ms"])]
    # When does injector stop appearing?
    last_inj = max((e["tSec"] for e in gap if e["injectorLiveRps"] > 10), default=None)
    # Stabilization: first streak of 30s nats p99<=250 & err<=0.01 after drain
    return {
        "gapSec": tf - td,
        "queued_min": min(queued),
        "queued_max": max(queued),
        "queued_mean": sum(queued) / len(queued),
        "timeouts_in_gap": to1 - to0,
        "served_in_gap": sv1 - sv0,
        "timeout_rate_gap": (to1 - to0) / ((to1 - to0) + (sv1 - sv0))
        if ((to1 - to0) + (sv1 - sv0)) > 0
        else float("nan"),
        "injectorP99_in_gap_max": max(inj_p99) if inj_p99 else None,
        "natsP99_in_gap_p50": percentile(sorted(nats_p99), 50) if nats_p99 else None,
        "natsP99_in_gap_p99": percentile(sorted(nats_p99), 99) if nats_p99 else None,
        "last_injector_active_tSec": last_inj,
        "series": [
            {
                "tSec": e["tSec"],
                "queued": e["queued"],
                "injectorP99": e["injectorLiveP99Ms"],
                "natsP99": e["natsLiveP99Ms"],
                "natsRps": e["natsLiveRps"],
                "timedOut": e["timedOut"],
                "cap": e["trueCapacity"],
            }
            for e in gap
            if int(e["tSec"]) % 10 == 0 or e["tSec"] < td + 2 or e["tSec"] > tf - 2
        ],
    }


def main():
    all_out = {}
    for rid in RUNS:
        print(f"analyzing {rid}...", flush=True)
        all_out[rid] = analyze_run(rid)

    # Patch run records with correction summary (keep full timeline in separate file)
    summary_rows = []
    for rid, a in all_out.items():
        path = RESULTS / f"{rid}.json"
        rec = json.loads(path.read_text())
        rec["liveSLOPopulation"] = "injector_direct"
        rec["livePopulationCorrection"] = {
            "old": a["old"],
            "new": a["new"],
            "populations_drain": a["populations_drain"],
            "downstreamTimeoutRate": a["downstream"]["timeoutRate"],
            "downstreamDeltaTimedOut": a["downstream"]["deltaTimedOut"],
            "downstreamDeltaServed": a["downstream"]["deltaServed"],
        }
        # Do not embed full corrected timeline in run json (huge); reference file
        rec["livePopulationCorrection"]["correctedTimelinePath"] = f"results/{rid}-corrected-timeline.json"
        path.write_text(json.dumps(rec, indent=2) + "\n")
        (RESULTS / f"{rid}-corrected-timeline.json").write_text(
            json.dumps(a["timelineCorrected"]) + "\n"
        )
        summary_rows.append(
            {
                "runId": rid,
                "condition": a["condition"],
                "tDrain": a["tDrainSec"],
                "tFull": a["tFullSec"],
                "gap": a["gapSec"],
                "old_vSLO": a["old"]["vSLO"],
                "new_vSLO": a["new"]["vSLO"],
                "old_peakLiveRps": a["old"]["drainPeakLiveRps"],
                "new_meanInjRps": a["new"]["drainMeanInjectorRps"],
                "old_peakLiveP99": a["old"]["drainPeakLiveP99Ms"],
                "new_injP99": a["new"]["drainInjectorP99"],
                "nats_p99_drain": a["new"]["drainNatsP99"],
                "timeoutRate": a["downstream"]["timeoutRate"],
            }
        )

    p0b_gaps = {rid: p0b_gap_report(all_out[rid]) for rid in RUNS if rid.startswith("p0b-r")}

    out = {
        "populationDefinition": {
            "injector_live": "class=live && age_ms==0 (post-restore)",
            "nats_live": "class=live && age_ms>0 (post-restore)",
            "recovery": "class=recovery (post-restore)",
            "liveSLOPopulation": "injector_direct",
        },
        "runs": {rid: {k: v for k, v in a.items() if k != "timelineCorrected"} for rid, a in all_out.items()},
        "summaryTable": summary_rows,
        "p0bGaps": p0b_gaps,
        "representativeDrainTables": {
            rid: all_out[rid]["populations_drain"] for rid in ("p0a-r1", "p0b-r1", "p0c-r1", "p0d-r1")
        },
    }
    (RESULTS / "GATE0-live-population-correction.json").write_text(json.dumps(out, indent=2) + "\n")

    # Markdown report
    lines = [
        "# Gate 0 — live population correction",
        "",
        "## Population definitions",
        "",
        "| Population | Rule (post-`restoreEpochMs`) | Role |",
        "|---|---|---|",
        "| Injector-live | `class=live`, `age_ms==0` | Direct HTTP; **live SLO** |",
        "| NATS-live | `class=live`, `age_ms>0` | Post-epoch JetStream; reported separately |",
        "| Recovery | `class=recovery` | Pre-epoch catch-up |",
        "",
        "## §3 Representative drain-window breakdown",
        "",
    ]
    for rid in ("p0a-r1", "p0b-r1", "p0c-r1", "p0d-r1"):
        lines.append(f"### {rid}")
        lines.append("")
        lines.append("| Population | count | mean rps | p50 | p95 | p99 | error rate |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for name, label in (
            ("injector_live", "Injector-live"),
            ("nats_live", "NATS-live"),
            ("recovery", "Recovery"),
        ):
            p = all_out[rid]["populations_drain"][name]
            lines.append(
                f"| {label} | {p['count']} | {p['meanRps']:.1f} | "
                f"{p['p50']:.0f} | {p['p95']:.0f} | {p['p99']:.0f} | {p['errorRate']:.4f} |"
            )
        lines.append("")

    lines += [
        "## §4 Old vs new (injector-live SLO)",
        "",
        "| runId | old peak liveRps | new mean inj Rps | old peak live p99 | new inj p99 | nats p99 (drain) | old vSLO | new vSLO |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['runId']} | {row['old_peakLiveRps']:.0f} | {row['new_meanInjRps']:.1f} | "
            f"{row['old_peakLiveP99']:.0f} | {row['new_injP99']:.0f} | {row['nats_p99_drain']:.0f} | "
            f"{row['old_vSLO']:.3f} | {row['new_vSLO']:.3f} |"
        )

    lines += [
        "",
        "## §5 P0-B T_drain → T_full gap",
        "",
    ]
    for rid, g in p0b_gaps.items():
        lines.append(f"### {rid} (gap={g.get('gapSec', float('nan')):.1f}s)")
        lines.append("")
        lines.append(
            f"- queued during gap: min={g.get('queued_min')} mean={g.get('queued_mean'):.1f} max={g.get('queued_max')}"
        )
        lines.append(
            f"- timeouts in gap: {g.get('timeouts_in_gap')} (rate={g.get('timeout_rate_gap'):.4f})"
        )
        lines.append(
            f"- NATS-live p99 in gap: p50={g.get('natsP99_in_gap_p50')} / max-of-per-sec-p99≈{g.get('natsP99_in_gap_p99')}"
        )
        lines.append(f"- last injector activity near t={g.get('last_injector_active_tSec')}")
        lines.append("")

    lines += [
        "## §6 Downstream timeout rates (full run window from timeline)",
        "",
        "| runId | Δserved | ΔtimedOut | timeout rate |",
        "|---|---:|---:|---:|",
    ]
    for rid, a in all_out.items():
        d = a["downstream"]
        lines.append(
            f"| {rid} | {d['deltaServed']} | {d['deltaTimedOut']} | {d['timeoutRate']:.4f} |"
        )

    (RESULTS / "GATE0-live-population-correction.md").write_text("\n".join(lines) + "\n")
    print("wrote results/GATE0-live-population-correction.md")
    print("wrote results/GATE0-live-population-correction.json")


if __name__ == "__main__":
    main()
