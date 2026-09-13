# E2d — is the boundary saturation, with configured C overstating truth?

**Analysis only, archived data. No instance.** Arithmetic as asked, no reframing.

## Answer

Both tests support the hypothesis.

| | |
|---|---|
| implied per-request overhead | **0.441 - 0.473 ms**, median **0.463**, CV **2.4%** |
| every measured plateau vs the value predicted at 0.46 ms | within **0.24%** |
| spread of the boundary against configured C | 0.0706 |
| spread against measured true capacity | **0.0033** |
| collapse factor | **21x** |
| median effective utilisation at the boundary | **0.9995** |

**Test 3 is not needed.** It was contingent on tests 1 and 2 being ambiguous. An overhead constant to 2.4% across two service times and three capacities, and a 21x collapse, is not ambiguous.

## One correction to the stated prediction

The brief predicts "~1827 at c10 and c50's C=2000 arms". The hypothesis does not predict a shared plateau there. True capacity is `C x S/(S+ov)`, which depends on S, so at C=2000 it is **1831 at S=5 ms** but **1964 at S=25 ms**. A shared 1827 would mean equal rho* in both arms, which is the very thing being explained. The measured values are 1829 and 1964, matching the per-arm predictions.

## Test 1 — true capacity from the plateau at UNSAFE points

| cell | S | C_d | runs | true capacity | predicted at 0.46 | error | implied overhead |
|---|---:|---:|---:|---:|---:|---:|---:|
| E1 c10/C0 | 5 | 2000 | 6 | **1828.6** | 1831.5 | -0.16% | **0.469 ms** |
| E1 c10/C1 | 5 | 1400 | 6 | **1280.9** | 1282.1 | -0.09% | **0.465 ms** |
| E1 c50/C0 | 25 | 2000 | 6 | **1964.3** | 1963.9 | +0.02% | **0.454 ms** |
| E1 c50/C1 | 25 | 1400 | 6 | **1375.7** | 1374.7 | +0.07% | **0.441 ms** |
| E2 c10@Q2500 | 5 | 2000 | 15 | **1827.1** | 1831.5 | -0.24% | **0.473 ms** |
| E2 c50@Q500 | 25 | 2000 | 15 | **1964.8** | 1963.9 | +0.05% | **0.447 ms** |
| E2b C=400 | 25 | 400 | 6 | **392.7** | 392.8 | -0.01% | **0.463 ms** |

The overhead is recovered as `ov = S x (C/plateau - 1)`. It comes out constant at **0.463 ms** across S = 5 and 25 ms and C = 400, 1400 and 2000, with a standard deviation of 0.0110 ms.

## Test 2 — the boundary against true capacity

| cell | rho* vs configured C | effective vs true capacity | brackets 1.0 | miss, in 5 rps steps |
|---|---|---|---|---:|
| E1 c10/C0 | [0.9124, 0.9150] | **[0.9979, 1.0008]** | yes | 0.00 |
| E1 c10/C1 | [0.9107, 0.9143] | **[0.9954, 0.9993]** | no | 0.18 |
| E1 c50/C0 | [0.9817, 0.9835] | **[0.9995, 1.0014]** | yes | 0.00 |
| E1 c50/C1 | [0.9786, 0.9822] | **[0.9959, 0.9995]** | no | 0.14 |
| E2 c10@Q2500 | [0.9124, 0.9150] | **[0.9987, 1.0016]** | yes | 0.00 |
| E2 c50@Q500 | [0.9820, 0.9841] | **[0.9996, 1.0017]** | yes | 0.00 |
| E2b C=400 | [0.9750, 0.9875] | **[0.9931, 1.0059]** | yes | 0.00 |

Five of seven intervals bracket 1.0 outright. The two that do not are both the reduced-capacity regime, and they fall short by **0.18 and 0.14 of a single 5 rps bisection step**. The boundary is located to 5 rps, so a miss of a fifth of a step is not a discrepancy the experiment can resolve.

**Is the residual within measurement resolution?** The residual spread across cells is 0.0033. One 5 rps step is 0.0025 in effective units for the C=2000 cells and 0.0127 for E2b. So the entire remaining spread is about one bisection step wide, and no cell departs from 1.0 by as much as a quarter of a step.

## Method note — the window decided this, not the statistic

True capacity is the maximum throughput sustained when the server always has work, measured here as the highest 30-second sustained served rate in each UNSAFE run, from the downstream's own cumulative counter.

Three narrower windows were tried first and all biased the answer the same way, because the backlog runs out at the end of a drain, the queue empties and the server idles between requests. Those ticks are not measurements of capacity:

| estimator | implied overhead | CV | reads as |
|---|---|---:|---|
| whole drain window, endpoints | 0.488 - 0.927 ms | 24% | an overhead that varies by arm |
| max 30 s sustained | **0.441 - 0.473 ms** | **2.4%** | a single constant |

`queued >= concurrency` did not fix it, because the queue passes through that level on its way to empty. `queued >= 5 x concurrency` did not either, because it means a queue of 50 for one arm and 250 for the other, making the arms incomparable in exactly the way it was meant to prevent. A maximum over sustained windows needs no queue threshold at all and cannot be dragged down by desaturation; per-tick variation inside the saturated stretch is about 0.4%%, so over 30 seconds any upward noise bias is under 0.1%%.

Under the reduced-capacity regime the window starts after the capacity step at t=20. Earlier ticks were served at the pre-fault capacity and belong to a different configuration.

## What this does not establish

The overhead is inferred, not observed. Nothing here measures a per-request cost directly; it is the residual between configured and achieved throughput, and the constant that reconciles them happens to be stable. Any mechanism adding a fixed cost per request would fit equally well, and this data cannot name which.

Test 3, a direct load sweep with no recovery load, is the measurement that would observe it rather than infer it. It remains unrun because the brief made it contingent on ambiguity, and there is none.
