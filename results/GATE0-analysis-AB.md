# Analysis A & B (from Check 1 data)

## Analysis A — Gate 0 item 3

**Caveat:** Check 1 did not instrument live traffic *before* the outage (consumer
was off while the backlog built). Baseline below is the **post-drain live-only**
window (~27s). Drain = 282s concurrent live+recovery.

| Metric | Baseline (post-drain) | Drain (concurrent) |
|---|---|---|
| Live p50 | 625 ms | 735 ms |
| Live p95 | 1684 ms | 1733 ms |
| Live p99 | 1930 ms | 1939 ms |
| Live error rate (excl 429) | 8.8% | 11.2% |
| Soft queueCap (graceful@2000) | 500 | 500 |

- `recoveryRemaining` reached 0? **No** (296835 / 300000 acked in 282s; ~3165 left)
- Mean recovery drain rate: **1053 msg/s**

Live is clearly degraded vs a healthy system (healthy p99 should be ≪250ms SLO);
post-drain baseline itself remains elevated (queue not fully cleared / dual live
paths). Campaign runs will capture true pre-outage baseline via the runner.

## Analysis B — Closed-loop offered rate

Check 1 used **WORKERS=1024**. Peak combined offered ≈ **2117 rps** (amp 1.06× vs C=2000).

Not unexplained: live injector is open-loop (~1000 rps) + recovery is closed-loop
(`WORKERS/latency`). Mean latency ~842 ms ⇒ recovery ≈ 1024/0.842 ≈ **1216 rps**;
sum ≈ 2216 ≈ observed.

**Finding:** recovery harms live via **latency/queue**, not huge throughput
amplification. Keep WORKERS=1024 (provisioning: fill soft queue under high
latency). Do not tune workers to inflate M4.

Injector `/noop` ceiling ~8000 rps; 2× peak combined (4234) < ceiling — OK.
