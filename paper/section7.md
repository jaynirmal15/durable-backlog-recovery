# §7 — What warns, and what does not

*Draft 6 — one-clause resync, 2026-09-20. §VII's close said "§II sets out why
latency feedback is the conventional construction". That phrasing was withdrawn
at §2 draft 2 — DAGOR and Breakwater key on queueing delay, Bouncer on
response-time percentiles, and none of the three establishes an industry
default — and §2 now says "an established construction", with live latency as a
literature-grounded comparator. Outline v9.0 corrected the §7 PLAN line and I
did not sweep §VII's own body, so a frozen section was left asserting what §2
had retracted. Only that clause changed; §VII's findings are untouched.*
*Draft 5 — SCIENCE FROZEN. 2026-09-19. Outline budget 900 words; this draft is
~1,290 and the excess is the two-cell distinction, which compression must keep.
F6.
Draft 5: DEEP is named as a separate preregistered marker rather than a second
condition a queue warning must satisfy — mean queue depth crosses 3σ at rl 1075
while never reaching DEEP inside the safe range, and "additionally" invited that
to read as a contradiction. Two scope words narrowed.*
*Draft 4. 2026-09-19. Outline budget 900 words. F6.
Draft 4: "no observable leads" collapsed two different claims — that no metric
warns, and that queue depth does not lead latency. The first is false in the
short-service cell, where four metrics cross with a safe point still ahead. §VII-C
is restructured around the distinction and now carries the complete
corrected-corpus result; §VII-D is left to the figure. The hypothesis is narrowed
to resolution of *ordering* rather than absence of room, and the opening
chronology names A5's post-data statistic choice up front.*
*Draft 3. 2026-09-19. Outline budget 900 words. F6.
Draft 3: §VII-D said neither signal "moves appreciably" across the safe range.
Both rise by roughly an order of magnitude. Corrected, and the warning-room
result that A7 records for this cell is now stated rather than omitted — it cuts
against the figure's framing, which is why it belongs in the text. F6's caption
makes two claims this contradicts; see the note at the end of §VII-D.*
*Draft 2. 2026-09-19. Outline budget 900 words. F6.
Draft 2: the "single 5 rps step" was wrong and was inherited from F6's committed
caption — the corrected searches resolved to 55 and 65 rps, not 5, and this cell's
transition spans 55. A7 is downgraded from "confirmed / strict replication" to
independent-corpus replication under a registered re-analysis, matching frozen
§IV. Controller-performance language removed per the claim register; the "any
cell" scope, the two-reasons logic and the hypothesis mechanism are corrected.*
*Draft 1. 2026-09-19. Outline budget 900 words; this draft is ~910. F6.
Every number verified against `results/A7-REPORT.md`,
`results/A7-leading-indicator-corrected.json` and `results/E1-LEADING-INDICATOR.md`
before drafting. The three findings are kept at three different evidentiary
statuses, which is the whole difficulty of this section. Source comments strip
in W6.*

---

## 7. WHAT WARNS, AND WHAT DOES NOT

An observable that moved before the safe boundary would provide advance warning
of the transition. This section asks whether any measured signal did so, and
reports three things at three different levels of confidence.

The warning rule compares each metric with three times its own noise scale, and
the drain queue additionally carries a separately preregistered DEEP threshold of
50 requests, registered in `results/E1B-PLAN.md` at commit `09e41e5` before the
runs it governs. Warning *room* is counted in probe points: a metric that first
crosses at the last SAFE point has given none. **The 3σ crossing is what defines
a warning in this analysis; DEEP is a separate preregistered absolute marker of
queue depth, not a further condition a queue warning must satisfy.** A metric can
therefore warn without the queue ever reaching DEEP, and in the corrected
short-service cell it does. The noise-scale estimator was
later changed under amendment A5, with the E1 data already in view — which is why
§VII-B treats the E1 ordering as exploratory — and addendum A7 imports that
frozen post-A5 statistic unchanged into the independent corrected corpus.

### A. Replicated on an independent corpus: timeout rate gives no advance warning

**Timeout rate does not cross its criterion before the boundary in any of the six
cells evaluated in the leading-indicator analysis** — the four E1 boundaries and
the two corrected cells. Its total σ is identically 0.00 in all six: the rate is
flat at zero through every safe point and only moves once the system has already
collapsed.

The result reproduces on the corrected-harness corpus. That corpus was collected
roughly thirty-four hours after amendment A5 froze the median-pooled noise
statistic, and played no part in choosing it. Addendum A7 subsequently registered
the criterion, statistic and prediction before re-analysing those already
collected data, importing them from the original script rather than restating
them so they could not drift. This is therefore an independent-corpus
replication under a registered re-analysis, not a prospective replication.

Timeout rate gave no advance warning of the safe boundary in either corpus.

### B. Exploratory: the queue-depth lead does not survive as a contribution

On the E1 corpus, mean drain queue depth crossed its criterion before live tail
latency in three of the four boundaries, by 20, 25 and 10 requests per second;
in the fourth it never crossed at all. That ordering was the campaign's most
operationally attractive result, and it is reported here as **exploratory**, for
two separate reasons that do different work: the first prevents a confirmatory
interpretation of the E1 result, and the second prevents the corrected corpus
from resolving the ordering independently.

The first is chronological. The statistic the ordering depends on — A5's
median-pooled noise scale — was chosen with the E1 numbers already in view. An
ordering measured with a statistic selected against the same data cannot be
treated as confirmatory of itself.

The second is resolution. Addendum A7 re-ran the frozen criterion on the
corrected corpus, and the ordering did not reproduce: queue depth and live p99
first cross at the same probe rate in both corrected cells, a margin of zero.
But that corpus cannot settle the question either way. Its safe points are
spaced 60 requests per second apart in one cell and 100 in the other, against
E1 margins of 10 to 25. **A lead of E1's size is below this corpus's resolution
by construction**, so a tie is what the design would produce whether or not the
effect exists.

The honest reading is the stronger of the two, not the weaker: the ordering is
unreplicated, and the only available independent corpus that could have
adjudicated it is too coarsely sampled to have done so. It stands as a single-corpus finding on E1's own probe
grid. A7 closed the remaining route by which it might have been promoted, and it
is not promoted.

### C. The corrected corpus: warning without ordering

The corrected corpus answers differently in each of its two cells, and the two
answers together are the result.

In the corrected **long-service** cell there is no warning room at all. Mean queue
depth, all three live latency percentiles and mean in-flight requests first cross
at `rl` 1210, which is the last safe point. On that cell the leading-indicator
framing has nothing to lead with.

In the corrected **short-service** cell there is warning room but no resolved
ordering. Mean queue depth, live p99, live p90 and mean in-flight all first cross
at `rl` 1075, with the last safe point at 1185 still ahead of them — one probe
point, roughly 110 requests per second of safe operating range after the first
crossing. Only live p50 crosses with no room, and only timeout rate never
crosses. But those four cross *together*: what is absent in this cell is the
ordering, not the warning.

**The corrected corpus therefore does not reproduce the queue-before-latency
ordering at its available resolution. It does not show that no metric gives
advance warning.** Those are
different claims and this section keeps them apart.

One further observation belongs here, with its quantity named. In the
short-service cell the *mean* drain queue depth never reaches its DEEP threshold
anywhere inside the safe range, peaking at 23.1 requests against 50. That is a
statement about the mean; Figure 6 plots the queue *peak*, which behaves
differently and is discussed below.

A possible explanation suggests itself, and is offered as a hypothesis rather
than as a finding. The corrected corpus samples coarsely near the boundary — 60
and 100 requests per second between safe points, against E1 margins of 10 to 25 —
so it may leave too little resolution to distinguish the relative *onset* of
queue depth and live latency even where both give advance warning. Under that
hypothesis a lead of E1's size would disappear below this corpus's sampling
resolution. Whether the original separation was itself related to the calibration
error remains untested.

**This is not a fourth retracted finding, and the evidence here does not support
making it one.** It is a hypothesis with a named experiment: a 5 requests per
second sweep across the top 50 of each corrected cell's safe range, about sixty
runs at n = 3, which would resolve a lead of E1's size in either direction.
§IX records it as the study that would settle the question.

### D. What the figure shows, and why it is unaffected

Figure 6 plots drain queue peak and live tail latency across the corrected
short-service cell as utilisation approaches its boundary. Both rise across the
sampled safe range — the queue peak from 7 requests to 111, live p99 from 8 ms to
58 — and both then change sharply at the transition between the final SAFE point
and the following non-SAFE one: the queue reaches its cap of 500 and live p99
rises to 508 ms. **That interval is 55 requests per second, not 5.** The
corrected-harness searches did not resolve at the seven-cell corpus's 5 rps step;
§IV records their achieved resolutions as 55 and 65 rps, and they are not members
of the seven-cell boundary corpus.

The figure is unaffected by the downgrade in §VII-B, and the reason is worth
stating. Its pipeline uses no noise statistic anywhere — it reads utilisation,
queue peak, live p99 and the classification directly — so it never depended on
the quantity A5 chose or A7 re-examined. A figure that survives a downgrade
because it never rested on the downgraded thing is evidence about the figure, not
a coincidence.

What §VII does **not** claim is that latency warns last, or that either signal is
the right one to build a controller on. §II establishes live latency as a
literature-grounded comparator, which is what makes these observations about a
signal the literature already uses. This section reports only that on this
harness, at
this resolution, timeout rate never warns; the queue-depth lead observed on E1 is
unreplicated and unresolvable on the available data; and on the corrected corpus
some observables do give advance warning in one cell, but queue depth does not
lead live p99 at the resolution available.
