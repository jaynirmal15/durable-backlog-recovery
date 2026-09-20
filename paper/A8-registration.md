# A8 — registration draft for review

*Drafted 2026-09-14, before any run. To be committed to `PRE-REGISTRATION.md`
as addendum A8 **before** the harness is rebuilt or any measurement is taken.
Nothing below may change once its commit is cited.*

---

### A8 — 2026-09-14: repeatability of the corrected saturation plateaus

**Registered before any run of this measurement. No result exists.**

#### Why

The prospective plateau prediction of E2e is adjudicated against two
measurements, one per arm, each a single 60-second sustained-throughput
window. The seven-cell corpus carries 6 to 15 saturation
measurements per cell and a repeatability of 0.10–0.24% of capacity; the two
measurements the prospective test turns on carry one apiece and therefore carry
no repeatability estimate at all.

The consequence is that the observed agreement — 0.02 rps in the short arm,
0.4 rps in the long one — cannot be assessed against the scatter of the quantity
it agrees with. This addendum measures that scatter.

#### What is measured

The saturation plateau of each corrected arm, **replicated**, at the same
configuration, the same corrected sleep and the same commit as the original
corrected runs.

- **n = 10 per arm**, 20 measurements total.
- Each measurement is a 60-second sustained-throughput window, closed-loop with
  400 connections and no configured offered rate, identical in construction to
  the original corrected plateau measurement.
- The reported plateau per arm is the **median** of its ten windows, matching
  the convention already used for `C_measured` in the seven cells. Range and
  interquartile range are reported alongside; no measurement is discarded
  except for a recorded integrity failure, and every exclusion is listed with
  its reason.

#### What is not changed, and not revisited

No new operating point is probed. No boundary is re-searched. The correction
constant, the registered prediction constants, the staffing, the admission
limit and the analysis path are all unchanged. This addendum measures the
repeatability of an existing quantity and nothing else. The boundary prediction,
the boundary brackets, and every seven-cell result are outside its scope and are
not reopened by it.

The two original single-window measurements are **retained and reported
alongside** the replicated medians. They are not replaced, and if a median
differs from its original single window by more than the observed spread, that
is reported as a finding about the original window.

#### The readings, fixed in advance

Let `spread` be the range of the ten windows in an arm.

**Short arm (`S` = 5 ms).** The registered constant implies a plateau of
1987.4 rps; the rival constant registered alongside it implies 1978.8 rps, a
separation of 8.6 rps. Both plateau figures are exact arithmetic consequences of
constants that were registered; neither figure was itself registered as a
plateau, and this addendum does not describe them as though it were.

- If the value implied by the registered constant lies within the observed
  spread **and** the rival's lies outside it, the short-arm prediction
  discriminated, and the manuscript says so.
- If both lie within the spread, the short arm **did not** discriminate. The
  manuscript then reports the plateau prediction as a consistency check with no
  discriminating power in either arm, and the candidate table loses its claim to
  have tested anything.
- If the value implied by the registered constant lies outside the spread, the
  prospective prediction failed on replication, and the manuscript reports it as
  failed.

**Long arm (`S` = 25 ms).** The two implied plateaus differ by 1.6 rps. The manuscript already states this arm cannot discriminate them. The
prediction registered here is that **the observed spread will exceed 1.6 rps**,
confirming that statement. If the spread is instead below 1.6 rps, the long arm
does discriminate after all and the manuscript's current wording is too weak and
will be corrected.

**Either outcome is reported.** A result that removes the short arm's
discriminating power is more useful than one that confirms it, because the
manuscript currently rests a prospective claim on it.

#### Relationship to the campaign

No formal closure of the experimental campaign is recorded in this repository,
and this addendum does not assert one. What is on the record is that the last
measurement cell, E2e, completed on 2026-09-13, and that every change since has
been analysis of existing data rather than new measurement. A8 is the first
addendum since then to collect new observations.

Its scope guard is part of this registration rather than an intention: any
result outside the repeatability of these two plateaus is out of scope for this
addendum and would require its own.

#### One inherited defect, declared

Reproducing the original build means building at the commit the corrected runs
used. That build contains a descriptive `note` string, since corrected, which
misstates which components its `total` field sums. The new records will inherit
it. The build must match or the measurement is of something else, so the string
is not patched here; the A8 report states that the inherited note is known to be
wrong and points at the correction.
