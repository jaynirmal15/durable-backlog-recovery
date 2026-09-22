# Figure and table captions

Drafted alongside each figure. Each states what the figure shows, not where it sits.

*2026-09-20 — CAPTION BOUNDARIES. Only text between a `caption:KEY` start and end
delimiter pair is set as a caption; everything else in this file is apparatus. The literal
"Fig. N." prefixes are removed because the build numbers floats from order of first
appearance. **All four of Fig. 4's paragraphs are caption**: the outline requires
the caption to carry n = 10, the median convention, the IQRs 1.71 / 1.29 rps as
window-to-window scatter rather than an inferential interval, the long-arm
non-discrimination and the two-corpus statement, and those are spread across all
four; the first trailing paragraph explains the marks, which a reader needs. The
post-A6 note below is not caption. **Fig. 2 notation corrected** from C·S/(S+ov) to
c/(S + δ), matching (1) and (5): the caption was the only place in the *text* that still wrote the overhead as
"ov". **Correction, 2026-09-20: that claim was false as a claim about the paper** —
the figure itself (now Fig. S1) still *draws* "ov" five times and draws
`concurrency = ⌈C·S⌉` rather than `c = ⌈C_config·S⌉`, as the executor found. The
drawn content therefore disagrees with its corrected caption until the generator
is fixed. Table captions are titles, per IEEE style;
explanation lives in the text. Table 1's caption stays in §IV where it was written,
delimited there. **A trailing `:s1` on a `figure:` or `table:` marker puts that float in Supplement S1 instead of the article**; without it the float is the article's. The caption library below is shared: a caption is found by key, wherever its float is placed. **Each figure caption is preceded by a `figure:KEY:FILE` marker** binding the key to the artefact it sets, the figure counterpart of the `table:KEY` marker that sits before a table. The binding lives here rather than in a file name because the key is the identity and the file names do not change.*

---

<!-- figure:fig:harness:F1-architecture.pdf -->
<!-- caption:fig:harness:start -->
**The harness.** Live traffic reaches the dependency by direct HTTP and
never enters the message broker; recovery traffic is produced into JetStream
during the outage and drained from it by a rate-limited consumer. The two paths
share nothing until the downstream, which is the only contended resource. The
fault withdraws the dependency's capacity for 120 s, and its restoration is the
time origin for every measurement reported here.
<!-- caption:fig:harness:end -->

<!-- caption:fig:capacity-model:start -->
**Where the unaccounted cost enters.** The harness sizes the dependency
as c = ⌈C_config·S⌉ workers on the assumption that each turns a request round in
exactly S, which makes capacity equal to C_config by construction. A worker in fact pays a fixed
additional 0.463 ms per request, almost all of it the operating system sleeping
longer than asked. C_model is therefore c/(S + δ), as in (5), and because the cost is
additive rather than proportional it consumes a larger share of a short service
time than a long one.
<!-- caption:fig:capacity-model:end -->

<!-- figure:fig:overhead:F3-overhead-measured.pdf -->
<!-- caption:fig:overhead:start -->
**The cost is constant, not proportional.** Mean per-request excess over
the requested sleep, measured on the worker path at 90% of C_measured over
roughly 120,000 requests per arm. Sleep overshoot accounts for 99.8% of it; the
runtime timer work, queue bookkeeping and channel send together contribute 1.3
microseconds. Right: the discriminating test. A constant cost predicts a
difference of zero between the arms and a proportional one predicts a ratio of
five; the measured difference is −0.0052 ms and the measured ratio 0.990. The
worker additionally pays about 0.0003 ms of timer work per request, excluded here
so the bar matches the figure used throughout the analysis.
<!-- caption:fig:overhead:end -->

<!-- figure:fig:plateau:F4-plateau-predicted-measured.pdf -->
<!-- caption:fig:plateau:start -->
**Predicting the plateau.** Maximum sustained throughput, predicted from
the additive model and measured from the dependency's own served counter. In the
uncorrected arms the configured capacity of 2000 overstates the measured plateau
by 171 and 36 requests per second, and the model accounts for both to within
0.2%. Reducing the configured sleep by the measured overhead, with concurrency
held fixed, brings the measured plateau to 1989.0 and 1997.7 against predictions
of 1987.4 and 1997.7 — differences of +1.6 and +0.0 requests per second at two
service times a factor of five apart. **The +0.0 in the long arm is agreement, not
evidence.** The two candidate corrections imply plateaus 1.60 rps apart there,
and the observed range across the ten windows is 2.83 rps, so that arm cannot
separate them however closely its median lands. Candidate selection is tested
only by the short arm, where the separation is 8.6 rps. §V-D gives the argument.

**Predictions are drawn as points on a short rule, measurements as bars**, so
the two are not rendered in the same visual grammar.

**The two pairs come from different corpora.** The uncorrected pair is E1 c10/C0
and E1 c50/C0, two of the seven-cell boundary campaign, whose plateaus are each
the median of six per-run maximum-30 s-sustained measurements, repeatable to
0.11% and 0.13%. The corrected pair is the E2e campaign, replicated under
pre-registration addendum A8: **each corrected plateau is the median of n = 10
60-second closed-loop windows**, the same median convention used for the
seven cells.

**The whiskers on the two corrected bars are the observed interquartile range**
of those ten windows — 1.71 and 1.29 requests per second. They are
**window-to-window scatter, not an inferential interval**, and no confidence
statement is attached to them. The uncorrected bars carry no whiskers because
those plateaus were not replicated in this form; the absence is a statement
about what was measured, not a claim of zero uncertainty.
<!-- caption:fig:plateau:end -->

<!-- figure:fig:collapse:F5-collapse.pdf -->
<!-- caption:fig:collapse:start -->
**The same seven boundaries, measured against the wrong capacity and the
right one.** Each line is one cell's last safe point, plotted first as a fraction
of configured capacity and then as a fraction of the capacity that cell was
measured to have. Both use the maximum achieved rate across that point's
repetitions, the per-cell value §IV defines for this figure. Against the
configured value the boundaries span 0.0719 and appear to separate by
concurrency arm; against measured capacity they close to 0.0071, and every cell
sits within 0.7% of saturation — two of them fractionally above it, by about a
fifth of a bisection step, which §IV explains. The apparent variation in safe
utilisation is an artefact of a capacity figure that is wrong by a different
amount in each cell.
<!-- caption:fig:collapse:end -->

<!-- figure:fig:signals:F6-signal-selection.pdf -->
<!-- caption:fig:signals:start -->
**Both candidate signals rise together, then jump at the transition.**
Drain queue peak and live tail latency across the corrected c10 cell as
utilisation approaches its boundary, each point the largest of its three
repetitions. Both rise across the sampled safe range — queue peak 7, 18 and 111
requests and live p99 8, 14 and 58 ms at 975, 1075 and 1185 rps — and then change
sharply across the 55 rps interval to the first unsafe probe at 1240 rps, where
the queue reaches its cap of 500 and live p99 reaches 508 ms. Read as leading
indicators, the two do not separate. In the registered analysis (A7), which uses
per-point means, mean queue depth and live p99 both first cross three standard
deviations at 1075 rps, one probe point before the last safe one, together with
live p90 and mean in-flight; live p50 crosses only at the last safe point, and
timeout rate never crosses. The queue plotted here is its **peak**. That
analysis's DEEP criterion concerns **mean** queue depth, which reaches 23.1
requests inside the safe range against a threshold of 50 and so does not cross
it there; a peak of 111 at the same point does not contradict that.
<!-- caption:fig:signals:end -->

---

## Table captions

<!-- caption:tab:resolution-full:start -->
Per-cell resolution of the boundary estimate, in full: the article's compact
table gives the bracket, the normalised resolution and the safe utilisation;
this one adds the configured and measured capacities, the raw bisection step,
the bracket width, the repetition count, the replicate spread and the measured
capacity's own range.
<!-- caption:tab:resolution-full:end -->

<!-- caption:tab:resolution:start -->
Per-cell resolution of the boundary estimate.
<!-- caption:tab:resolution:end -->

<!-- caption:tab:delta-conditions:start -->
The per-request timing bias δ measured by the direct timing probe under three conditions.
<!-- caption:tab:delta-conditions:end -->

<!-- caption:tab:a8-replication:start -->
Plateau replication under addendum A8: ten 60-s windows per arm, in requests per second.
<!-- caption:tab:a8-replication:end -->

<!-- caption:tab:delta-predictions:start -->
Plateau predictions from registered and comparison δ estimates, with the replicated measured plateau, in requests per second.
<!-- caption:tab:delta-predictions:end -->

<!-- caption:tab:accounting:start -->
The apparent concurrency effect before and after calibration, under each accounting.
<!-- caption:tab:accounting:end -->

<!-- caption:tab:candidates:start -->
Candidate explanations of the boundary, and what calibration changed about each.
<!-- caption:tab:candidates:end -->

<!-- caption:tab:false-findings:start -->
Findings that entered the written record and were later overturned by independent checks.
<!-- caption:tab:false-findings:end -->

---

## Post-A6 note on Fig. 5

The brief specified a collapse from 0.0706 to 0.0033. Those are the pre-A6
figures from the E2d report, computed from interval midpoints whose upper ends
are collapsed points where the utilisation estimator over-reads. Under A6 the
boundary is reported at the last safe point, giving 0.0719 collapsing to 0.0071
under the maximum numerator §IV names. The figure uses the post-A6 values, as the brief
requires post-A6 values throughout. The visual claim is unchanged and the
arithmetic is now defensible.

**Superseded the same day by the note below; kept as the record.**
**Corrected 2026-09-19.** This note and the caption above said 0.0719. That was
the left axis taken as the **maximum** across the last safe point's repetitions,
set against a right axis that was the **median** — so a figure arguing that the
spread collapses was comparing a max with a median, which inflates the collapse
it draws. Both axes are now the median: 0.0716 collapsing to 0.0068, a factor of
10.49, displayed as 10.5 as before. The max-based figure was 10.54. The corrected
numerator now agrees with A6's collapse factor (`METHOD-AUDIT.md` item 22, and
`PRE-REGISTRATION.md` A10).

**Corrected again 2026-09-19 — the note above fixed the wrong half.** §IV names
the aggregator for the per-cell value plotted here: the maximum achieved ρ across
the last SAFE point's repetitions. The left axis already used it. The right axis
did not: it divided a4Rate, a **median** numerator, by C_measured. The note above
moved the left axis to the median to match, which corrected the half that was
right. Both axes now use the maximum — 0.0719 against configured capacity,
0.0071 against measured capacity. The denominator, C_measured, is a different
median, across a cell's saturation runs of each run's maximum 30-second
sustained rate, and is unchanged. The figure, its title and this caption give
the two spreads and no ratio between them; the title previously carried "a
factor of 10.5" and the caption "a factor of ten", and both are removed.
