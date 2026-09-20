# A9 — registration draft for review, revision 4

*Drafted 2026-09-18, revised 2026-09-19. To be appended to `PRE-REGISTRATION.md`
as addendum A9.
This is a **record correction**, not a methodological amendment: it changes no
rule, no criterion, no estimator, no datum and no result. Nothing below may
change once its commit is cited.*

*Revision 3. Revision 2 fixed three defects found in verification, one of which
was an unsupported claim in revision 1; revision 3 fixed a miscount — the
provenance list named three fields and the following sentence said four. See the
note at the end.*

---

### A9 — 2026-09-19: record correction to A8's short-arm reading

**This is a correction to the text of a prior registration. It governs no data
and no analysis, and neither temporal column in Table 1 applies to it.**

#### What is wrong

Addendum A8, registered in commit `590d1cc`, states in **"The readings, fixed in
advance"**, in the short-arm paragraph (quoted verbatim; line breaks normalised):

> Both plateau figures are exact arithmetic consequences of constants that were
> registered; neither figure was itself registered as a plateau, and this
> addendum does not describe them as though it were.

That statement is incorrect. Addendum 1 of the E2e plan, commit `67c448b`
(2026-09-13 17:31:47 UTC), tabulates both plateau values directly and makes them
a gating check:

> **Plateau check first.** Each corrected cell's saturation plateau must match
> 1987.4 and 1997.7 before its boundary is read. If the plateaus match and the
> boundaries do not, that is a real finding and not the correction.

The values 1987.4 and 1997.7 rps were therefore registered as plateau
predictions, with a pre-committed reading of the alternative outcome.

#### What this changes

Nothing operative. A8's readings, its n, its median convention, its arm-specific
criteria, its scope guard and its reported outcome are all unaffected, because
none of them depends on the corrected sentence. No datum is revisited, no
analysis is re-run, and no reported value changes.

#### What this addendum does not establish

Revision 1 of this draft asserted that the registration predates the measurements
that tested it. **The committed record does not establish that, and the claim is
withdrawn.**

The two corrected plateau measurements are written by
`scripts/overhead_run/main.go`, which records the label, the offered rate, the
connection count and the measurement, and **no provenance**: no commit, no
branch, no dirty flag and no timestamp. The runner's boundary records carry all
four; this standalone tool carries none. What the committed record bounds is therefore only:

| time (UTC) | committed event |
|---|---|
| 16:31:55 | `c96f406` — from here the harness can run the corrected sleep |
| **17:31:47** | **`67c448b` — addendum 1 registers 1987.4 and 1997.7** |
| 18:50:07 | `f032f12` — addendum 2 reports the c10 plateau gate already passed |

That window contains the registration time. Addendum 1 states that "experiment 1
is complete and no boundary run has started"; it makes no statement about the
plateau measurement, so the ordering rests on the registration's forward-looking
language — "must match … before its boundary is read" — and on a campaign log
that timestamps the c10 gate at 18:07:30 UTC but is not a committed artefact.

The same gap applies to A8's own twenty windows, which use the same record type
and are likewise untimed. A8's registration does assert in its own committed text
that no result existed when it was written, which addendum 1 does not.

This addendum records the gap. It does not close it, and no claim in the
manuscript should be written as though it were closed.

#### Why it is recorded rather than edited

The registration is immutable once its commit is cited: corrections take the form
of dated addenda with the original text left intact. Applying that rule only when
a correction is convenient would cost more than the addendum does. A8 therefore
stands as written, with this addendum attached.

#### How the manuscript carries it

§V notes in one sentence that A8 misstates these figures as unregistered and
points here. §V also states the provenance gap above rather than describing the
plateau test as timestamped. §IX carries the `overhead_run` provenance defect as
a threat to validity. Table 1 lists A9 as a record correction with both temporal
columns reading N/A, and §IV-A's count becomes *six amendments, one registered
re-analysis, one registered replication, and one record correction*.

---

*Verification note, not part of the registration. Revision 1 said the correction
was safe to record after the fact because the commit disproving A8's sentence
predates the runs. That reasoning was circular: it assumed the ordering this
addendum has now been unable to establish. The correction is safe for a different
and sufficient reason — it understates what was registered rather than inflating
it — and every revision from 2 onward rests on that alone.*
