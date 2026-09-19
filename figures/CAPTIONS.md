# Figure captions

Drafted alongside each figure. Each states what the figure shows, not where it sits.

---

**Fig. 1. The harness.** Live traffic reaches the dependency by direct HTTP and
never enters the message broker; recovery traffic is produced into JetStream
during the outage and drained from it by a rate-limited consumer. The two paths
share nothing until the downstream, which is the only contended resource. The
fault withdraws the dependency's capacity for 120 s, and its restoration is the
time origin for every measurement reported here.

**Fig. 2. Where the unaccounted cost enters.** The harness sizes the dependency
as ⌈C·S⌉ workers on the assumption that each turns a request round in exactly S,
which makes capacity equal to C by construction. A worker in fact pays a fixed
additional 0.463 ms per request, almost all of it the operating system sleeping
longer than asked. C_model is therefore C·S/(S+ov), and because the cost is
additive rather than proportional it consumes a larger share of a short service
time than a long one.

**Fig. 3. The cost is constant, not proportional.** Mean per-request excess over
the requested sleep, measured on the worker path at 90% of C_measured over
roughly 120,000 requests per arm. Sleep overshoot accounts for 99.8% of it; the
runtime timer work, queue bookkeeping and channel send together contribute 1.3
microseconds. Right: the discriminating test. A constant cost predicts a
difference of zero between the arms and a proportional one predicts a ratio of
five; the measured difference is −0.0052 ms and the measured ratio 0.990. The
worker additionally pays about 0.0003 ms of timer work per request, excluded here
so the bar matches the figure used throughout the analysis.

**Fig. 4. Predicting the plateau.** Maximum sustained throughput, predicted from
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

**Fig. 5. The same seven boundaries, measured against the wrong capacity and the
right one.** Each line is one cell's last safe point, plotted first as a fraction
of configured capacity and then as a fraction of the capacity that cell was
measured to have. Both are the median across that point's repetitions. Against
the configured value the boundaries span 0.0716 and appear to separate by
concurrency arm; against measured capacity they close to 0.0068, a factor of
ten, and every cell sits within 0.7% of saturation. The
apparent variation in safe utilisation is an artefact of a capacity figure that
is wrong by a different amount in each cell.

**Fig. 6. Both candidate signals are flat until they are useless.** Drain queue
peak and live tail latency across the corrected c10 cell as utilisation
approaches its boundary. Neither moves appreciably while the system is safe, and
both saturate together at the transition: the queue reaches its cap and tail
latency crosses the objective within a single 5 rps step. A controller reading
either signal has no advance warning, which is what motivates measuring headroom
against capacity rather than inferring it from load.

---

## Post-A6 note on Fig. 5

The brief specified a collapse from 0.0706 to 0.0033. Those are the pre-A6
figures from the E2d report, computed from interval midpoints whose upper ends
are collapsed points where the utilisation estimator over-reads. Under A6 the
boundary is reported at the last safe point, giving 0.0716 collapsing to 0.0068,
a factor of 10.5 rather than 21. The figure uses the post-A6 values, as the brief
requires post-A6 values throughout. The visual claim is unchanged and the
arithmetic is now defensible.

**Corrected 2026-09-19.** This note and the caption above said 0.0719. That was
the left axis taken as the **maximum** across the last safe point's repetitions,
set against a right axis that was the **median** — so a figure arguing that the
spread collapses was comparing a max with a median, which inflates the collapse
it draws. Both axes are now the median: 0.0716 collapsing to 0.0068, a factor of
10.49, displayed as 10.5 as before. The max-based figure was 10.54. The corrected
numerator now agrees with A6's collapse factor (`METHOD-AUDIT.md` item 22, and
`PRE-REGISTRATION.md` A10).
