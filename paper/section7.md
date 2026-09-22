# §7 — What warns, and what does not

*Draft 8 — CUT PASS, increment 5, 2026-09-20, under the reviewer's 18-page
authorisation. §VII compressed from ~1,300 to ~800 words. Kept, as the ruling
requires: the warning rule and DEEP's status; timeout rate's result and its
independent-corpus replication status under A7; both reasons the queue-depth lead
is exploratory; and a compact §VII-C — no warning room in the long-service cell,
warning room but a joint crossing in the short-service cell — with its
two-sentence statement — "does not reproduce the queue-before-latency ordering
… It does not show that no metric gives advance warning" — unchanged from Draft 7's
§VII-C. Moved to S1-H: the
per-point trajectories, the DEEP-versus-peak discussion, the figure-pipeline
argument in full and the named sweep, which §IX also carries. The former §VII-D
heading is dissolved into §VII-C. No number or finding changes.*
*Draft 8.1 — APPROVED by review with one restoration: the sentence distinguishing mean queue depth (DEEP, peak 23.1) from the plotted queue peak, without which DEEP = 50 and a plotted peak above 50 would read as a contradiction. Frozen.*
*Draft 7 — KEYED FIGURE AND TABLE REFERENCES, 2026-09-20. Every literal "Fig. N", "Figure N" and "Table N" in the body is replaced by a key (`[@fig:…]`, `[@tab:…]`) that the build renders as "Fig. N" / "Table N" from order of first appearance — the citation design, applied to floats, so numbering cannot go stale when tables are added. No other wording changed.*
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

The warning rule compares each metric with three times its own noise scale.
Warning *room* is counted in probe points: a metric that first crosses at the
last SAFE point has given none. The drain queue additionally carries a separately
preregistered DEEP threshold of 50 requests, **an absolute marker of queue depth,
not a further condition a queue warning must satisfy.** The noise-scale estimator
was changed under amendment A5 with the E1 data already in view, and addendum A7
imports that frozen post-A5 statistic unchanged into the corrected corpus.

### A. Replicated on an independent corpus: timeout rate gives no advance warning

**Timeout rate does not cross its criterion before the boundary in any of the six
cells evaluated in the leading-indicator analysis** — the four E1 boundaries and
the two corrected cells. Its total σ is identically 0.00 in all six: the rate is
flat at zero through every safe point and only moves once the system has already
collapsed. The corrected corpus was collected roughly thirty-four hours after A5
froze the statistic and played no part in choosing it; A7 registered the
criterion, statistic and prediction before re-analysing those already collected
data. This is therefore an independent-corpus replication under a registered
re-analysis, not a prospective replication.

### B. Exploratory: the queue-depth lead does not survive as a contribution

On the E1 corpus, mean drain queue depth crossed its criterion before live tail
latency in three of the four boundaries, by 20, 25 and 10 requests per second;
in the fourth it never crossed at all. It is reported as **exploratory**, for two
separate reasons that do different work. The first is chronological: the
statistic the ordering depends on — A5's median-pooled noise scale — was chosen
with the E1 numbers already in view, so the ordering cannot be treated as
confirmatory of itself. The second is resolution. Under A7 the ordering did not
reproduce: queue depth and live p99 first cross at the same probe rate in both
corrected cells. But that corpus's safe points are spaced 60 and 100 requests per
second apart, against E1 margins of 10 to 25. **A lead of E1's size is below this
corpus's resolution by construction**, so a tie is what the design would produce
whether or not the effect exists. The ordering is unreplicated, and the only
available independent corpus that could have adjudicated it is too coarsely
sampled to have done so. It stands as a single-corpus finding on E1's own probe
grid, and it is not promoted.

### C. The corrected corpus: warning without ordering

The corrected corpus answers differently in each of its two cells, and the two
answers together are the result. In the corrected **long-service** cell there is
no warning room at all: mean queue depth, all three live latency percentiles and
mean in-flight requests first cross at the last safe point. In the corrected
**short-service** cell there is warning room but no resolved ordering: mean queue
depth, live p99, live p90 and mean in-flight all first cross one probe point —
roughly 110 requests per second — before the last safe point, and they cross
*together*. [@fig:signals] shows that cell: queue peak and live p99 rise across
the safe range and then change sharply across the final 55 rps interval into the
first unsafe probe.

**The corrected corpus therefore does not reproduce the queue-before-latency
ordering at its available resolution. It does not show that no metric gives
advance warning.** Those are different claims and this section keeps them apart.
That the corrected corpus samples too coarsely near the boundary to separate the
two onsets is offered as a hypothesis, not a finding — **not a fourth retracted
finding** — and §IX names the finer sweep that would settle it. DEEP applies to
*mean* drain queue depth, which peaks at 23.1 requests inside the safe range;
[@fig:signals] plots the queue *peak*, a different quantity. The figure's
pipeline uses no noise statistic, so it is unaffected by the downgrade in §VII-B.
Supplement S1 gives the per-point trajectories.

What §VII does **not** claim is that latency warns last, or that either signal is
the right one to build a controller on. §II establishes live latency as a
literature-grounded comparator, which is what makes these observations about a
signal the literature already uses. This section reports only that on this
harness, at this resolution, timeout rate never warns; the queue-depth lead
observed on E1 is unreplicated and unresolvable on the available data; and on the
corrected corpus some observables do give advance warning in one cell, but queue
depth does not lead live p99 at the resolution available.
