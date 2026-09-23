# §10 — Conclusion

*Draft 4 — TWO-REVIEW REVISION, 2026-09-23. B1: the headline retires "within 1%". B4: the prescription is scoped to this harness, keeping the sentence that declines to decide between external calibration and online inference.*

*Draft 3 — SCIENCE FROZEN, copy edit only. 2026-09-20. "overstated its own
service capacity **by** a per-request timing bias of 0.463 ms" put a throughput
overstatement and a time quantity in the same measure; it is now "**because
of**". The 9.26% / 1.85% sentence that follows already carries the magnitude of
the capacity error. Flagged as a W5 copy edit in review and taken now rather
than carried: a known defect held until W5 is one more thing to remember, and
remembering is what has failed five times in this project. No science changed.
Draft 2 made three sentence-level edits, each taking
back a claim the paper is careful not to make elsewhere.
(i) "available only to an operator who measures capacity rather than accepting
it" reads as mandating offline measurement, while C2 deliberately leaves the
offline-versus-online question open. Now: the result **depends on an empirically
validated capacity reference rather than on the configured parameter**.
(ii) "Choosing between the two requires a controller comparison" made a
controller experiment the necessary discriminator between two *capacity
estimation* strategies, which does not follow and drifts toward the controller
recommendation this paper refuses to make. Now: a separate study, left to future
work. §IX owns the two named experiments; the conclusion adds no third.
(iii) "What it did was make the retractions happen before publication" gives
pre-registration causal credit C4 does not establish — the retractions were
produced by replication, additional test cells and cross-checks. Now: **the
pre-registered record made those reversals explicit and auditable** before
publication rather than after.
Outline budget 500 words; draft 2 is **457** of body (draft 1: 454) —
under budget, and I have not padded it. A conclusion that restates the paper is
worse than a short one.
No figure, no table. Written against outline v9.1.*

*CONSTRAINTS OBSERVED. Headline and scale-mismatch wording are the claim
register's, verbatim where marked. No controller-performance verb appears —
§I's C3 wording is followed exactly and the queue-depth ordering is NOT
reintroduced as a result. Capacity terminology is the rigid four-term set;
the configured parameter is never called true capacity. No numeric range is
quoted for the headline, no collapse factor, no strict inequality against 1.0,
and "statistically" does not appear. The close is C4, per the plan, because a
measurement reviewer is likeliest to value it. Source comments strip in W6.*

---

## 10. CONCLUSION

**Across seven cells the safe drain boundary lay at or near measured service
capacity and was indistinguishable from it at each cell's experimental
resolution.** The cells span two service times, three configured capacities, two
admission limits and four concurrency levels. Varying the latency objective over
the range where the question is well posed moved the boundary by no resolvable
amount. One residual disagreement between capacity regimes is declared in §VI
and is not claimed: it is smaller than the resolution of the cell at one end of
it.

That result depends on an empirically validated capacity reference rather than
on the configured parameter. The instrument used here was purpose-built, its capacity parameter
chosen by its author, and its worker count derived from that parameter by
Little's law — and it overstated its own service capacity because of a
per-request timing bias of 0.463 ms, the pooled saturation-plateau-inferred value, which is
9.26% at a 5 ms service time and 1.85% at 25 ms. The margin under study was
under one percent.

**When the safety margin being characterised is sub-percent, a small and
approximately service-time-independent per-request timing bias can exceed the
phenomenon under study, generate a stable but false second-order effect, survive
deliberate falsification, and invalidate conclusions about which signals are
usable for control.**

The practical implication is methodological: in this harness, interpreting a
sub-percent recovery margin required a capacity reference validated against
observed throughput rather than the configured parameter. More generally, a
configured capacity figure should not be treated as ground truth when its
calibration error is unknown or comparable to the operating margin. Whether the estimate
should be supplied by external calibration or inferred online is not settled
here. One measurement bears on it without deciding it: the per-request cost is
not fixed but varies with offered load, so an offline benchmark would itself
have to be conducted at the load condition that matters. Evaluating that trade-off requires a separate
study, which this paper does not perform and which we leave to future work.

On observables, the corrected evidence supports one conclusion and withholds
another. Request timeout rate gives no advance warning of the boundary: it never
crosses its criterion before the last safe point, and that result replicates on
a corpus collected after the analysis statistic was frozen. Whether queue depth
leads live latency remains unresolved; §VII names the experiment that would
settle it.

What we would keep from the method is the pre-registration. It did not prevent
the campaign from writing down three claims that further measurement later
overturned, and it did not expose a sub-millisecond bookkeeping error from the
effects that error produced — §VIII gives that case and §IX those three. What
the pre-registered record did was make those reversals explicit and auditable
before publication rather than after.
