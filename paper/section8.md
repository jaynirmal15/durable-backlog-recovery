# §8 — How calibration changed the interpretation

*Draft 3 — SCIENCE FROZEN, package included. 2026-09-20. The freeze condition
was seeing the regenerated Table 3 under the asymmetric schema; that table is
regenerated, quote-asserted with zero changes to its assertion set, idempotent
on re-run, and numerically identical to its predecessor. **With §8 frozen, all
ten manuscript sections are scientifically frozen.**
Outline budget 900 words; this draft is ~965. Table 3.
Draft 3 is one precision edit, twice. The §VIII-A heading said "affirmed, then
removed" and the body said "It did not survive calibration"; the measurement is
94-95% removal, not 100%, and an unqualified "removed" invites a reader to
contrast it with the 5-6% residual. Both now say what was measured: the effect
is no longer resolved after calibration.
Draft 2 applied the three substantive corrections from review of Draft 1.
Draft 2 applies the three substantive corrections from review of Draft 1.
(i) The A6 paragraph recreated the false symmetry it existed to prevent — it
said A6 "left all three findings standing", but the admission limit was not a
finding, and A6 did not change how utilisation is estimated at collapsed points:
it established that the A4 estimator over-reads there and the response was to
stop reporting utilisation at those points. (ii) The service-time subsection
borrowed §VIII-A's collapse to close a gap in its own record; the two later
results that bear on the S-governs reading are now named as what they are, and
neither is a recomputation of `h`. (iii) The admission-limit queue/SLO
arithmetic was backwards — a full queue at 25 ms exceeds the objective more
strongly, not less; the real asymmetry is that at 25 ms the objective is crossed
while queue capacity remains.
Every row sourced from `figures/calibration-artefact-findings.md` at `c0a4eb2`,
whose generator asserts each quotation against its artefact and aborts on a
missing fragment. The section deliberately does NOT tell three identical
stories — the three rows have three different standings, and that asymmetry is
the finding. Retitled from "How the defect misled us", which promised a symmetry
the record does not contain. Source comments strip in W6.*

---

## 8. HOW CALIBRATION CHANGED THE INTERPRETATION

Three candidate explanations of the boundary's position were put to registered
falsification tests during this campaign. The tests did not treat them alike, and
the differences between the three outcomes are more informative than any one of
them.

One point has to be established first, because two corrections happened days
apart and are easy to conflate. Amendment A6 concerns the treatment of collapsed
points: it established that the A4 utilisation estimator over-reads there, and
the response was to stop reporting utilisation at those points rather than to
re-estimate them. A6 changed no candidate explanation's standing — concurrency
and service time remained affirmed, the admission limit remained rejected. What
changed the interpretation of the two affirmed results was a separate and later
operation: replacing the configured capacity parameter with an empirically
calibrated capacity reference. Table 3 keeps the two apart throughout.

### A. Concurrency: affirmed, then no longer resolved after calibration

The E1 arms separated by 0.0689 in achieved utilisation at the last safe point —
0.9137 at concurrency 10 against 0.9826 at concurrency 50. Two explanations were
available and confounded in E1, because the arms differed in both concurrency and
admission limit.

The registered test swapped the caps and scored the fraction of the separation
that followed the cap rather than the arm. A verdict of CONCURRENCY-DRIVEN
required that fraction to be at most 0.25. It came back at **+0.000 and −0.006**:
the separation stayed with the arm while the cap moved fivefold. The finding
survived a test designed to kill it, and the test was registered before the cells
ran.

The resolved concurrency effect did not survive calibration. Expressed against
measured rather than configured capacity, the same separation between the same two arms falls from 0.0670 to
0.0032 under drain-window accounting and from 0.0696 to 0.0043 under
delivery-span — **94 to 95% of it removed**, or 134.0 requests per second down to
6.4. §V-F gives the matched accounting.

This is the one complete chain in the paper: a second-order effect that was
registered, challenged, survived its challenge, and was then almost entirely
removed by measuring the instrument. What survives of it is a small fraction of
the original separation, below what this experiment resolves (§VI). The paper's
central lesson rests on it.

### B. Service time: affirmed, and not re-adjudicated

E2b separated concurrency from service time by running a cell at a configured
capacity of 400 with concurrency 10 and a 25 ms service time — the concurrency of
one arm and the service time of the other. The registered statistic scored where
that cell's boundary landed between the two E1 arm positions, with S GOVERNS
requiring at least 0.75 and a dead band fixed in advance. It returned **0.980**.

That result also survived its registered test. Its standing after calibration
differs from §VIII-A's, and the difference is not cosmetic.

The statistic is defined *relative to the E1 arm separation* — it scores where
the E2b boundary falls between the two E1 midpoints — and that separation was
measured against the configured capacity parameter. Two later results bear on
the reading that service time governs the boundary. Physically correcting the
harness removes most of the separation between those same two arms (§V-F).
Expressing seven cells against measured capacity resolves no service-time
difference at all (§VI-D). Both undermine the interpretation.

Neither is the registered statistic. The first is a different estimator in two
cells; the second a different quantity across seven. **`h` itself was never
recomputed, and cannot be**: the corrected harness ran no cell at a configured
capacity of 400, which is where `h` was measured.

The honest statement is therefore three-part: this inference was affirmed before
calibration; the interpretation it carried is undermined by calibrated evidence;
and its exact registered test was not re-adjudicated. This paper does not borrow
§VIII-A's collapse to close that gap.

### C. The admission limit: a falsification that worked

The third explanation is in this section for the opposite reason, and it is not a
retracted finding.

The arithmetic behind it is worth stating, because it shows the hypothesis was
not lazy. The graceful queue cap is fifty times the concurrency, so the delay
through a full queue is fifty times the service time: 250 ms at a 5 ms service
time, which is the latency objective itself, and 1250 ms at 25 ms, five times
it. The two arms therefore reach their limits in a different order. In the
short-service arm the queue fills at about the point the objective is crossed,
so the admission limit and the objective are very nearly the same constraint. In
the long-service arm the objective is crossed while substantial queue capacity
remains, so the cap is still slack at the boundary. An arm-dependent boundary
and an arm-dependent binding constraint is exactly the coincidence that makes a
cap explanation credible — which is why it was given a registered test rather
than dismissed. The campaign's own status notes recorded it before E2 as a
competing explanation of the concurrency effect, not yet ruled out.

The same cap-swap test that confirmed concurrency scored this hypothesis the
other way: CAP-DRIVEN required the cap-following fraction to reach 0.75. It was
**off-scale**. The explanation was eliminated before calibration, by its own
registered criterion, and no written result had ever asserted it as a finding —
only as an open question with a test attached.

Nothing about it dissolved when the instrument was calibrated, because there was
nothing left to dissolve.

### D. What the three outcomes establish together

The falsification protocol was not useless. It rejected a wrong explanation
cleanly, on a criterion fixed in advance, before anything was known about the
timing bias. That is the machinery working.

What it could not do is identify a sub-millisecond bookkeeping error from the
effects that error produced. The concurrency finding passed a test built
specifically to break it, and was removed only after the instrument itself was
measured rather than reasoned about. The service-time inference passed its own
test and remains only partly adjudicated.

**A campaign operating under a public pre-registration with an explicit
falsification protocol could reject an incorrect causal explanation, and could
not detect the calibration bias from its consequences.** Those two facts are the
section, and they are not in tension: falsification tests the hypothesis it is
given, and none of the hypotheses on offer was that the instrument's own capacity
figure was wrong.
