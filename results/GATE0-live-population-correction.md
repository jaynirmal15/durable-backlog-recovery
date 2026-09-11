# Gate 0 — live population correction

## Population definitions

| Population | Rule (post-`restoreEpochMs`) | Role |
|---|---|---|
| Injector-live | `class=live`, `age_ms==0` | Direct HTTP; **live SLO** |
| NATS-live | `class=live`, `age_ms>0` | Post-epoch JetStream; reported separately |
| Recovery | `class=recovery` | Pre-epoch catch-up |

## §3 Representative drain-window breakdown

### p0a-r1

| Population | count | mean rps | p50 | p95 | p99 | error rate |
|---|---:|---:|---:|---:|---:|---:|
| Injector-live | 113565 | 987.5 | 800 | 2003 | 2167 | 0.1051 |
| NATS-live | 4258 | 37.0 | 780 | 2001 | 2152 | 0.0768 |
| Recovery | 119214 | 1036.6 | 800 | 2003 | 2176 | 0.1059 |

### p0b-r1

| Population | count | mean rps | p50 | p95 | p99 | error rate |
|---|---:|---:|---:|---:|---:|---:|
| Injector-live | 143158 | 987.2 | 1192 | 2027 | 2210 | 0.2763 |
| NATS-live | 2979 | 20.5 | 1227 | 2037 | 2207 | 0.2632 |
| Recovery | 118539 | 817.4 | 1160 | 2022 | 2206 | 0.2654 |

### p0c-r1

| Population | count | mean rps | p50 | p95 | p99 | error rate |
|---|---:|---:|---:|---:|---:|---:|
| Injector-live | 121166 | 985.0 | 901 | 2006 | 2178 | 0.1686 |
| NATS-live | 4065 | 33.0 | 776 | 2001 | 2188 | 0.0817 |
| Recovery | 119192 | 969.0 | 867 | 2005 | 2181 | 0.1532 |

### p0d-r1

| Population | count | mean rps | p50 | p95 | p99 | error rate |
|---|---:|---:|---:|---:|---:|---:|
| Injector-live | 135421 | 988.4 | 1148 | 2024 | 2191 | 0.2909 |
| NATS-live | 3227 | 23.6 | 786 | 2001 | 2164 | 0.0781 |
| Recovery | 119233 | 870.2 | 1029 | 2017 | 2185 | 0.2484 |

## §4 Old vs new (injector-live SLO)

| runId | old peak liveRps | new mean inj Rps | old peak live p99 | new inj p99 | nats p99 (drain) | old vSLO | new vSLO |
|---|---:|---:|---:|---:|---:|---:|---:|
| p0a-r1 | 1499 | 987.5 | 1974 | 2167 | 2152 | 0.875 | 0.879 |
| p0a-r2 | 1496 | 988.2 | 1965 | 2168 | 2116 | 0.877 | 0.880 |
| p0a-r3 | 1375 | 985.7 | 1991 | 2166 | 2154 | 0.876 | 0.880 |
| p0b-r1 | 1484 | 987.2 | 1993 | 2210 | 2207 | 0.934 | 0.936 |
| p0b-r2 | 1153 | 985.2 | 2021 | 2211 | 2199 | 0.935 | 0.937 |
| p0b-r3 | 1482 | 985.5 | 2058 | 2204 | 2204 | 0.936 | 0.938 |
| p0c-r1 | 1371 | 985.0 | 1986 | 2178 | 2188 | 0.885 | 0.888 |
| p0c-r2 | 1513 | 986.9 | 1989 | 2176 | 2136 | 0.889 | 0.889 |
| p0c-r3 | 1511 | 987.2 | 1989 | 2180 | 2164 | 0.887 | 0.887 |
| p0d-r1 | 1525 | 988.4 | 1999 | 2191 | 2164 | 0.899 | 0.899 |
| p0d-r2 | 1493 | 988.2 | 1993 | 2190 | 2142 | 0.896 | 0.899 |
| p0d-r3 | 1492 | 986.1 | 2006 | 2192 | 2139 | 0.900 | 0.900 |

## §5 P0-B T_drain → T_full gap

The gap is **real post-drain saturation**, not stabilize-window padding.
Stabilize contributes ~33 s everywhere (30 s streak + a few seconds). The
condition difference is how long the soft queue stays pinned after `T_drain`.

| runId | tDrain | queue→0 | nats p99≤250 | tFull | post-drain sat | stabilize tail |
|---|---:|---:|---:|---:|---:|---:|
| p0b-r1 | 145 | 435 | 439 | 468 | **290 s** | 33 s |
| p0b-r2 | 145 | 442 | 446 | 475 | **297 s** | 33 s |
| p0b-r3 | 143 | 449 | 453 | 482 | **306 s** | 33 s |
| p0a-r1 (ref) | 115 | 216 | 219 | 249 | 101 s | 33 s |

During P0-B saturation: queued mean ~313–315 (cap ~350), NATS-live p99 ~2.0–2.2 s,
timeouts continue (~3% of gap work). At the cliff, queue→0 and p99→~7 ms.

Note: post-drain `age_ms==0` samples are mostly fresh NATS (same-ms publish),
not injector — injector stops at `T_drain`. Drain-window `age_ms==0` counts
match `injectorCompleted` within ~1%.

## §6 Downstream timeout rates (full run window from timeline)

| runId | Δserved | ΔtimedOut | timeout rate |
|---|---:|---:|---:|
| p0a-r1 | 434853 | 25333 | 0.0550 |
| p0a-r2 | 437874 | 25633 | 0.0553 |
| p0a-r3 | 438360 | 24426 | 0.0528 |
| p0b-r1 | 608207 | 84199 | 0.1216 |
| p0b-r2 | 617275 | 84191 | 0.1200 |
| p0b-r3 | 633032 | 81570 | 0.1141 |
| p0c-r1 | 450373 | 39483 | 0.0806 |
| p0c-r2 | 453308 | 38952 | 0.0791 |
| p0c-r3 | 445837 | 39331 | 0.0811 |
| p0d-r1 | 458367 | 69748 | 0.1321 |
| p0d-r2 | 462794 | 69642 | 0.1308 |
| p0d-r3 | 463667 | 70613 | 0.1322 |
