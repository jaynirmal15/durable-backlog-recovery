# A10 — registration draft for review, revision 1

*Drafted 2026-09-19. To be appended to `PRE-REGISTRATION.md` as addendum A10.
A **record correction**, like A9: it changes no rule, no criterion, no
estimator, no datum and no conclusion. Nothing below may change once its commit
is cited.*

*The heading below carries the literal placeholder `<COMMIT DATE>`. Substitute
the repository clock at commit time, per the convention adopted at A9.*

---

### A10 — <COMMIT DATE>: record correction to A6's collapse factor

**This is a correction to the text of a prior registration. It governs no data
and no analysis, and neither temporal column in Table 1 applies to it.**

#### What is wrong

Addendum A6, registered in commit `c3aee75`, reports the E2d collapse factor as
`10.3x` in two places: once in its conclusions table —

> | **E2d collapse to effective ~1.0** | **spread 0.0033, 21.4x** | **spread 0.0068, 10.3x** | **CHANGES** |

— and once in the paragraph beneath it, "Its collapse factor halves, from 21.4x
to 10.3x".

That factor was computed from mismatched estimators. Its numerator was a spread
over interval **midpoints**; its denominator was a spread over **SAFE points
only**. Recomputing the numerator on the SAFE side, matching the denominator,
gives 0.0716 rather than the 0.0706 the report used, and a factor of **10.5x**.
The audit that established this is recorded as item 22 of
`results/METHOD-AUDIT.md`, and the correction was applied there in place.

#### What this changes

The factor, and nothing else. `10.3x` is superseded by `10.5x`.

#### What this does not change

The denominator, 0.0068, stands. The direction, the substance and A6's verdict
all stand: the E2d cells still collapse by an order of magnitude when
renormalised, and the entry is still the one conclusion in A6's table that
moves. The earlier `21.4x` remains correctly recorded as the pre-A6 figure. No
datum is revisited, no analysis is re-run, and no other reported value changes.

The numerator 0.0706 is **not** part of A6's registered text; it appears in
`results/A6-REPORT.md`, which is an analysis report and was corrected in place.
This addendum therefore corrects the factor alone, because the factor alone is
what the registration carries.

#### Its direction, stated because the direction matters

This correction makes the reported effect **larger**, not smaller: 10.3x becomes
10.5x. A record correction that flatters the result deserves more scrutiny than
one that does not, so the reasoning is given in full above and the arithmetic is
reproducible from the committed artefacts. The change is 2%, it does not affect
whether the collapse is an order of magnitude, and no claim anywhere in the
manuscript turns on the difference between 10.3x and 10.5x.

#### Why it is recorded rather than edited

The registration is immutable once its commit is cited: corrections take the
form of dated addenda with the original text left intact. A6 is itself a
correction, so this is a correction to a correction, and that is precisely why
it is appended rather than folded in — the sequence of what was believed, and
when, is the record. A6 stands as written, with this addendum attached.

#### How the manuscript carries it

The manuscript quotes 10.5x, not 10.3x. Table 1 lists A10 as a record
correction with both temporal columns reading N/A, and §IV-A's count becomes
*six amendments, one registered re-analysis, one registered replication, and two
record corrections*. §IX records both corrections together.
