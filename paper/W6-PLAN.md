# W6 — the plan from frozen drafts to a submitted article

*Draft 1.2, 2026-09-20 (repository clock, UTC-04:00 — dates in this file are the
author's local day, not UTC, per METHOD-AUDIT item 31; draft 1 dated three files
a day ahead because UTC had rolled over). Written after the citation pass closed W5 at `28d6785`.
This plan sequences W6; it does not decide anything the author has to decide.
`scripts/DEPOSIT-W6.md` remains the operational checklist for the deposit
itself and is not restated here — this file says when it runs, what blocks it,
and records two defects found in it while writing this plan.*

**Publisher requirements below were read from IEEE Access's own pages on
2026-09-20** (submission guidelines, submission checklist, 2026 APC list).
Each is cited where used. **Anything a submission depends on is re-read on the
day of submission**; a publisher page is not a frozen artefact.

---

## The shape of W6

Four phases, strictly ordered. Each blocks the next.

| phase | what it produces | blocked by |
|---|---|---|
| 0. Decisions | the answers only Jay can give | nothing — start now |
| 1. Assembly | the article in the IEEE Access template, matching PDF | phase 0 |
| 2. Deposit | a published Zenodo record whose DOI resolves | phase 1's freeze commit |
| 3. Submission | the ScholarOne submission | phase 2 |

The freeze commit sits between 1 and 2 and is the pivot: **what is deposited and
what §IV cites must be the same commit.** That rule already caught one defect in
this campaign, when a staged package sat four commits behind main.

---

## Phase 0 — ANSWERED 2026-09-20

**The author's answers, recorded verbatim in effect:**

| # | decision | answer |
|---|---|---|
| 1 | Degree | **B.E.** The manuscript already reads B.E.; the hard check in the outline's W6 row is closed. The iCloud CV that says "B.S." is corrected separately |
| 2 | ORCID | `https://orcid.org/0009-0003-0886-4663`. **VERIFIED 2026-09-20 on the live page: public, and populated** — name Jay Suresh Nirmal, one employment (Meazure Learning, Senior Software Engineer, 2021-11-15 to present), two education entries, one work. Meets the IEEE Access requirement. **Two mismatches with the manuscript and CV are recorded below; neither blocks submission and neither is a manuscript change** |
| 3 | Page count | No answer needed yet — the number does not exist until Phase 1 builds the template. The path is chosen then |
| 4 | APC | **Accepted** at $2,160 on acceptance |

> **Two mismatches the ORCID check surfaced, both outside the manuscript.**
> Recorded because a reader comparing the public record with the paper — a
> reviewer, or an immigration officer reading the same profile — sees both.
> 1. **Field of the first degree.** ORCID says *"Bachelor of Engineer in
>    Computer Science"*, Mumbai University. The CV and the biography say
>    **computer engineering**. The biography follows the certificate, which the
>    author has confirmed; it is the ORCID entry that should be corrected (its
>    "Bachelor of Engineer" wording too).
> 2. **Location.** ORCID gives the employer as Meazure Learning, Birmingham,
>    Alabama; the biography says the author is a Senior Software Engineer in
>    Boston, MA, which the CV supports. Both can be true — employer
>    headquarters against the author's own location — and IEEE biographies give
>    the author's location, so the biography stands. No change.
>
> Neither is a manuscript defect. Both are profile housekeeping, best done
> before the paper makes the profile worth reading.

---

## Phase 0 as originally written — four decisions, none of them mine

**1. The biography**, and with it the open B.E./B.S. question, which is already
a hard pre-submission check in the outline's W6 row. The degree designation
comes from the certificate, not from either CV.

**2. ORCID.** *"The submitting author is required to have an ORCID ID associated
with their account. The ORCID profile must be publicly visible and populated."*
If Jay does not have one, it is created and populated before submission, not
during it. This is the cheapest item here and the easiest to discover too late.

**3. Page count — the one with lead time.** IEEE Access *"strongly
recommend[s] keeping the page count under 20 pages"*, and **exceeding 20 pages
requires pre-submission approval from the Editor-in-Chief**. The manuscript is
18,321 prose words plus six figures and **four** tables — T2, T3 and T4
generated, and Table 1, the amendments table, hand-written in `section4.md`, with
the most rows of the four (11), though T3 carries the most content — which has been estimated at 22-23 pages in the
template. (Draft 1 said three tables, missing the hand-written one; corrected
2026-09-20 on the executor's catch. The error understated the page estimate,
which is the wrong direction for the check it feeds.) **The estimate is not evidence.** Phase 1
produces the real number, and the moment it exceeds 20, one of two paths opens,
both of which take time:
- request EIC approval and wait, or
- cut to fit, which is a content decision and therefore the author's.
This is the item most likely to delay submission, and it cannot be assessed
before the template build.

**4. The APC.** IEEE Access is fully open access: the 2026 list gives
**$2,160** per article. Payable on acceptance, not at submission, but it is a
decision, and it should be a made decision rather than a discovered one.

---

## Phase 1 — assembly, and the checks that only work on the assembled article

The manuscript is ten markdown sections, a front matter file, a references file,
six figure PDFs and three generated tables. IEEE Access requires *"a double
column, single-spaced format using a required IEEE Access template"*, and
**both** a Word or LaTeX source **and** a matching PDF, each under 40 MB, with
identical content.

1. **Choose the template.** LaTeX or Word. Either is accepted; the choice
   affects who can fix a formatting defect at 11 p.m. before submission.
2. **Render, don't retype.** The assembly is mechanical and must be scripted, so
   it can be re-run after any late change: strip drafting headers and HTML
   source comments, render `[@key]` markers to IEEE numbers from first
   appearance, place figures and tables at their called positions, emit the
   bibliography in the numbered order.
3. **Then the checks that need the assembled article:**
   - the **promotion scan**, deferred to W6 from the start: no withdrawn or
     superseded claim may survive anywhere in the assembled text, including in
     captions, table cells and figure labels — the layers where this campaign's
     recurring failure lived;
   - the **marker audit**, re-run now that exemption markers exist;
   - **acronyms defined at first use**, which the checklist requires *even if
     already defined in the abstract*;
   - **keywords: 3 to 10.** The index terms are seven. Compliant;
   - **biographies for all authors** — one author, one biography. Present;
   - the page count, against the 20-page line above.
4. **Freeze.** The commit at the end of this phase is the commit §IV cites and
   the commit the deposit is built from. Nothing content-bearing lands after it
   until submission.

---

## Phase 2 — the deposit

`scripts/DEPOSIT-W6.md` is the checklist and it is sound. Run it against the
freeze commit. Three notes, two of which are defects in that file found while
writing this plan.

**Defect 1 — its step 6 is unrunnable as written.** It says to add
`{'relation': 'isSupplementTo', 'identifier': '<article DOI>'}` to the
deposition metadata *"once the article is accepted and has a DOI"*, and then
publish. But its own next paragraph requires publication **before submission**,
and the article DOI does not exist until acceptance, which is months after
submission. As written, the two instructions cannot both be obeyed.
*Proposed resolution, for the executor to rule on:* publish without the
relation, and add `isSupplementTo` as a metadata edit on the published record
after acceptance. Zenodo permits metadata edits post-publication; files and DOI
stay fixed. The step should say so explicitly, because the current wording
invites someone to delay publication and discover the trap at submission time.

**Defect 2 — its step 3 recommends the tool that caused the earlier failure.**
Step 3 says to confirm the upload path with `--probe`, which uploads test
objects. Three leftover `_probe_*` objects are exactly what broke deposition
22740491 and forced its deletion, and the same file says elsewhere that
`--show` "is what should have been used instead of `--probe`". Step 3 should
recommend `--show`, and say that `--probe` is a last resort whose objects must
be deleted before verification.

**Note 3 — the manifest/commit equality check is the one that matters.** It has
already caught a stale package once. Run it after staging and read the output;
do not assume `--stage` picked up HEAD.

Then, unchanged from the checklist: upload resumably, verify every key, size and
checksum with `zenodo_verify.py`, expect zero missing/extra/mismatched,
**publish from the web interface by hand** — never from a script, because a
published record cannot be deleted.

**After publishing, two hard checks, each against a primary source. BOTH DONE
2026-09-23:**
- `https://doi.org/10.5281/zenodo.22761131` resolves to the published record at
  `https://zenodo.org/records/22761131` — version 1.0.0, CC BY 4.0, published
  2026-09-23 — which is what makes the abstract's *"publicly archived"* true;
- the record's file count matches the manifest: seven objects, verified before
  publication at 815 checks with zero missing, extra, mismatched or unchecked.

**Still open, carried to acceptance:** `DEPOSIT-W6.md` step 7 — add the
`isSupplementTo` relation with the article DOI, as a metadata edit on the
published record. Nothing else will prompt for it.

---

## Phase 3 — submission

ScholarOne. Have ready: the template source and the matching PDF (identical
content, each under 40 MB), supplementary material if any, the manuscript type
(default *Research Article*), keywords, the ORCID, an opposed-reviewers list if
Jay wants one, and the confirmation that the work is not under consideration
elsewhere. The checklist also prohibits the Lena image; no figure here uses it.

**The last act before clicking submit** is to re-verify the two assertions the
manuscript makes about the outside world — the resolving DOI, and the degree
designation in the biography — because both are true only if someone checked.

---

## What this plan does not decide

The degree, the ORCID, the page-count path, and the APC. All four are Jay's. Everything else here is sequencing and mechanics.
