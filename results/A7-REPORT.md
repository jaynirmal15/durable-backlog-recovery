# A7 — Leading indicator on the corrected-harness corpus

**Registered:** `939902d`, 2026-09-14 00:15:59 -0400, before the analysis ran.
**Analysis:** `scripts/leading_indicator_corrected.py` → `results/A7-leading-indicator-corrected.json`.
**Statistic, threshold and criterion unchanged.** The corrected script imports
`METRICS`, `WARN_SIGMA` and `analyse` from `scripts/leading_indicator.py` rather
than restating them, so they cannot drift. Only the corpus differs: `results/e2e/`
in place of the four E1 boundaries.

## The registered prediction

> Queue depth crosses its criterion before live p99 does, and timeout rate does
> not cross at all.

## Result, per cell

### corrected c10 — SAFE at rl 975, 1075, 1185

| metric | first warning | room | total σ | means across SAFE points |
|---|---|---|---|---|
| mean queue depth | rl 1075 | 1 point | 32.98 | 1.404 → 4.777 → 23.127 req |
| live p99 | rl 1075 | 1 point | 39.19 | 8.0 → 13.0 → 40.0 ms |
| live p90 | rl 1075 | 1 point | 29.39 | 6.667 → 10.0 → 30.667 ms |
| live p50 | rl 1185 | 0 points | 17.33 | 5.0 → 6.333 → 13.667 ms |
| mean in-flight | rl 1075 | 1 point | 38.08 | 5.742 → 7.416 → 16.631 req |
| timeout rate | never | — | 0.00 | 0.0 → 0.0 → 0.0 |

**Margin: 0 rps.** Queue depth and live p99 first cross at the same probe rate.
The queue **DEEP threshold (50 req) is never crossed inside the SAFE range** —
the deepest safe point sits at 23.1 req, less than half of it.

### corrected c50 — SAFE at rl 975, 1150, 1210

| metric | first warning | room | total σ | means across SAFE points |
|---|---|---|---|---|
| mean queue depth | rl 1210 | 0 points | 17.03 | 1.014 → 17.804 → 125.450 req |
| live p99 | rl 1210 | 0 points | 8.60 | 34.0 → 60.667 → 164.333 ms |
| live p90 | rl 1210 | 0 points | 15.73 | 30.0 → 45.667 → 149.333 ms |
| live p50 | rl 1210 | 0 points | 19.48 | 25.0 → 32.0 → 82.333 ms |
| mean in-flight | rl 1210 | 0 points | 17.08 | 25.538 → 33.980 → 87.802 req |
| timeout rate | never | — | 0.00 | 0.0 → 0.0 → 0.0 |

**Margin: 0 rps.** Queue depth crosses DEEP at rl 1210 — which is the *last* SAFE
point, so under the frozen criterion this is not advance warning at all
(`warningRoomPoints = 0`). Every metric in this cell first moves at the same
place, and that place is the edge.

## Does E1 replicate?

**Half of it does. The half that matters does not.**

| boundary | queue depth | live p99 | margin |
|---|---|---|---|
| E1 c10-C0 | rl 800 (2 pts room) | rl 820 (1 pt) | **+20 rps** |
| E1 c10-C1 | never | rl 275 | n/a |
| E1 c50-C0 | rl 940 (3 pts) | rl 965 (2 pts) | **+25 rps** |
| E1 c50-C1 | rl 360 (1 pt) | rl 370 (0 pts) | **+10 rps** |
| corrected c10 | rl 1075 (1 pt) | rl 1075 (1 pt) | **0 rps** |
| corrected c50 | rl 1210 (0 pts) | rl 1210 (0 pts) | **0 rps** |

- **Timeout rate does not cross at all** — replicates cleanly, in both corrected
  cells, exactly as in all four E1 boundaries. σ is identically 0.00.
- **Queue depth crosses before live p99** — **does not replicate.** The two tie in
  both corrected cells. In E1 queue depth led in three of four boundaries, by 10
  to 25 rps.

### The limitation registered in advance, now quantified

The registration recorded ahead of the result that three SAFE points per cell
give less room than E1's four and five, and that a non-replication could mean
either absence of signal or absence of room. It can now be put in rates:

| cell | SAFE probe rates | gaps | finest spacing |
|---|---|---|---|
| E1 c10-C0 | 755, 800, 820, 825 | 45, 20, 5 | 5 rps |
| E1 c50-C0 | 890, 940, 965, 970, 975 | 50, 25, 5, 5 | 5 rps |
| E1 c50-C1 | 340, 360, 370 | 20, 10 | 10 rps |
| corrected c10 | 975, 1075, 1185 | 100, 110 | **100 rps** |
| corrected c50 | 975, 1150, 1210 | 175, 60 | **60 rps** |

E1's margins were 10–25 rps. The corrected corpus is sampled at 60–110 rps.
**A lead of E1's size is below this corpus's resolution by construction**, so the
tie is what the design would produce whether or not the effect is real. This is
not a rescue of the prediction — it does not license claiming the lead exists. It
means the corrected corpus **cannot adjudicate the ordering in either direction**.

The honest statement is therefore the stronger of the two: the ordering claim is
unreplicated, and the only corpus that could have replicated it is too coarsely
sampled to have done so. The E1 ordering result stands as a **single-corpus
finding on E1's own probe grid**, and the statistic that produced it (A5's
median-pooled noise scale) was chosen with those E1 numbers in view.

### Consequence for C3

**C3 is exploratory, not confirmatory.** This follows from the registration's own
terms ("If it does not, C3 is exploratory and the E1 finding is a single-corpus
result") and is consistent with `results/METHOD-AUDIT.md` item 3, which reached
the same label from the A5 chronology independently. A7 removes the remaining
route by which C3 might have been promoted: the corrected corpus was collected
~34 hours after A5 froze and so was genuinely independent of the choice of
statistic, but it did not reproduce the ordering and could not have.

A further point against any strong reading: in corrected c50 **no metric gives
advance warning at all** — all five move for the first time at the last SAFE
point. On that cell the leading-indicator framing has nothing to lead with.

## F6 is unaffected

`f6()` in `scripts/make_figures.py` reads `E2E['c10']['points']` and uses four
fields per point — `rho`, `queuePeak`, `liveP99Ms`, `class`. It plots the two
series directly against achieved utilisation, with the queue cap (500) and the
SLO (250 ms) as reference lines and the SAFE/non-SAFE edge as a shaded span.

`scripts/make_figures.py` imports only `json`, `os`, `sys`, `matplotlib` and two
`matplotlib.patches` names. It contains **zero** occurrences of
`leading_indicator`, `sigma`, `noise`, `warn`, `median` or `A5`. No noise
statistic enters F6's pipeline at any stage.

**Therefore F6 is unaffected by A5 and by this re-run.** Its claim is the raw
shape of the two series — both flat until the last safe point, then a cliff — and
that claim is visible in the plotted values without any inferential step. This
should be stated in §VII: F6 survives the C3 downgrade intact, because it never
depended on the statistic being downgraded. Its own title, "both signals are flat
until the last safe point, then cliff", is in fact the *corrected* corpus's
behaviour rather than E1's lead, so the figure and the A7 result agree.

## Files

- `scripts/leading_indicator_corrected.py` — adapter; imports the frozen analysis.
- `results/A7-leading-indicator-corrected.json` — full per-point output, both cells.
