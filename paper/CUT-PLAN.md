# Cut plan — from ~25 pages to 18

*Draft 1, 2026-09-20. Proposed, not applied. Nothing in any section changes
until the reviewer and the author approve this plan.*

## Draft 2 — REVIEW RULINGS, 2026-09-20 (supersede Draft 1 where they conflict)

**Baseline corrected: the clean compile is 27 pages, not 25.** Zero errors,
floats in place. The target of 18 therefore needs about **9 pages**, and the
table below, estimated against 25, reaches only about 21-22. The shortfall is
found by recompiling after each increment, not by estimating further.

**1. Approach — APPROVED, with a stricter boundary: move the audit trail; keep
everything needed to evaluate the claim.** Three classes stay in the article
even when their detailed evidence moves to S1:
- **anything defining an estimator or a classification rule** — n = 3
  classification, the SAFE / UNSAFE / MARGINAL rules, last-SAFE / first-non-SAFE
  semantics, the resolution rule;
- **anything needed to understand the resolution and precision discipline;**
- **any limitation that materially qualifies a result.** In particular, the
  full provenance chronology may move, but the article must still say that the
  standalone plateau tool lacked the provenance fields needed to prove, from the
  committed record, that registration preceded those plateau measurements. That
  limits the evidentiary status of the prospective test; it is not bookkeeping.

**2. Target — 18. Sixteen is NOT authorised.** The sequence is frozen: build
fixed (done) → apply the 18-page cuts incrementally, recompiling after each →
evaluate the real PDF. If it lands at 17-19 and reads well, **stop**. Deeper
structural cuts are considered only if executing this plan still leaves 20+.

**3. §IV-F stays, compressed.** The achieved-versus-nominal distinction is
load-bearing — it changes values and even rate ordering — so its definition and
why it matters remain. **§IV-I's reproducibility mechanics are the cleaner
supplement candidate.** Options (a)/(b)/(c) below are **not pre-authorised**;
choose after recompiling.

**4. §VIII → §IX merge — REJECTED.** §VIII is results: what calibration did to
the three candidate explanations, whose asymmetric outcomes are themselves a
methodological finding. §IX is validity: it states that its three overturned
claims are a different set with a different cause, none a calibration artefact.
Merging them would invite exactly the false equivalence the structure prevents.
Item 11 below is withdrawn with the rest of the 16-page tier.

## Draft 3 — MEASUREMENT FINDINGS, 2026-09-21 (not rulings)

*These are measurements against the frozen sources and against the 27-page
clean compile of `af8bea8`, taken at the reviewer's request. **Nothing here
decides anything.** Where a measurement contradicts an estimate below, the
estimate is wrong and the plan needs a ruling, which is with the reviewer
together with the float decisions and a proposed target of 19. **No cut is
applied until those rulings return.***

**Method, so the numbers can be rechecked.** A float-free page of this article
holds **5,204 characters**, measured across the eleven pages of the compile
that carry no float (range 4,787-5,446). Prose characters are counted from the
section bodies with header blocks, HTML comments, fenced blocks, table rows and
markdown punctuation removed. Float areas are measured from the PDF itself:
either the vertical extent of the float's text band on its page, or the page's
character deficit against 5,204 plus the float's own character content. The two
methods agree on Table 1 to within 0.04 of a page.

### 1. The prose baseline is 18,310 words, not 17,910

`scripts/section_wordcount.py` reports **18,310**. Draft 1's table is 400 words
low, and the reason is identifiable: §I and §X match the script exactly (-3
each) while every other section is 42-60 low, and those two are the only
sections with no subsections. **Draft 1's counts exclude the `###` subsection
headings**, which the script's stated convention includes ("counted: body prose
below the first `---`, including headings, since a reader reads them"). The
per-subsection figures in Draft 1 are otherwise sound, within 1-3%.

| § | Draft 1 | `section_wordcount.py` | chars | prose pages |
|---|---:|---:|---:|---:|
| I | 1,595 | 1,598 | 8,479 | 1.63 |
| II | 1,376 | 1,420 | 7,974 | 1.53 |
| III | 1,650 | 1,702 | 8,690 | 1.67 |
| **IV** | **4,684** | **4,744** | **24,507** | **4.71** |
| V | 2,708 | 2,762 | 14,779 | 2.84 |
| VI | 1,492 | 1,540 | 7,827 | 1.50 |
| VII | 1,306 | 1,358 | 6,766 | 1.30 |
| VIII | 1,029 | 1,071 | 5,663 | 1.09 |
| IX | 1,615 | 1,657 | 8,786 | 1.69 |
| X | 455 | 458 | 2,502 | 0.48 |
| **all** | **17,910** | **18,310** | **95,973** | **18.4** |

### 2. Two corrected part lists

- **§II** omitted **A (243 words)**, which is larger than the listed E (198).
  Measured: C 323 · D 312 · B 309 · **A 243** · E 198.
- **§IX** listed B 469 · C 466. Measured, **C (478) is larger than B (474)**.
  Item 5 targets C, so the order matters slightly.

### 3. Where the 27 pages go

| | pages | share |
|---|---:|---:|
| prose, the ten sections | 18.4 | 68% |
| tables: rows and rules, captions excluded | 3.3 | 12% |
| figures: image area, captions excluded | ~2.3 | 9% |
| all fourteen captions | 1.07 | 4% |
| bibliography | 1.14 | 4% |
| abstract, index terms, biography, title block | ~1.2 | 4% |
| **sum of the estimates** | **~27.4** | |
| **actual** | **27.0** | |

The 0.4 overshoot is this method's error, and it is stated rather than
distributed: the figure areas are the soft term, because a figure's caption
characters offset the page deficit its image creates. **Floats -- tables,
figures and captions together -- are about 6.7 of the twenty-seven pages.**
Items 9 and 10 recover about 0.5 of that. This is the single largest fact the
plan was written without.

### 4. Per-item recalibration

Table 1 occupies **0.84 of page 8** — its text band spans 446 of that page's
531 usable units, and the deficit method gives 0.80. §IV-H is **4,175
characters = 0.80 pages**, and it is not adjacent to its table: the `H.
AMENDMENTS` heading is on **page 13** and §IV-I begins on **page 14**, while
Table 1 floats to page 8 beside its first reference.

| # | Draft 1 est. | measured | note |
|---|---:|---:|---|
| 1 | 1.4 | **1.33** | 0.84 (table) + 0.80 (prose) − 0.31 kept; see finding 5 — the kept text must be ~250 words, not ~80 |
| 2 | 0.7 | 0.70 | §IV-C is 1.34 pages; a 52% cut |
| 3 | 0.3 | 0.35 | §IV-G 0.32 + §V-G 0.07, less one sentence each |
| 4 | 0.4 | 0.41 | §IV-D 0.55 + E 0.57 + B 0.45 |
| 5 | 0.3 | 0.33 | §IX-C is 0.48 pages |
| 6 | 0.4 | 0.45 | §I is 1.63 pages |
| 7 | 0.3 | 0.37 | §V-C 0.55 + D 1.11 |
| 8 | 0.5 | 0.48 | §II-E 0.20 + §IX-B 0.48 + §VI-D 0.41 + §VII-D 0.28 |
| **9** | **0.7** | **0.34** | **overstated.** F1 costs ~0.40 of a page and F5 ~0.28; single-column recovers about half of each |
| **10** | **0.3** | **0.15** | **overstated.** T3 costs 0.33 and T6 only 0.12 — T6 is three narrow rows and is nearly free already |
| total | 5.3 | **4.91** | 27.0 − 4.91 = **22.1 pages** |

**This confirms Draft 2's corrected estimate of 21-22 and shows Draft 1's
19-20 was optimistic.** The shortfall against 18 is about **four pages, not
two**.

### 5. The amendment log is cited 42 times outside §IV-H

Item 1 treats the amendment log as apparatus. It is referenced by number
throughout the article:

| | citations | sections |
|---|---:|---|
| **A8** | 13 | §I, §IV, §V, §IX |
| **A7** | 9 | §IV, §VII |
| **A5** | 5 | §VII |
| **A6** | 4 | §IV, §VIII |
| A9 | 4 | §IV, §V, §IX |
| A4 | 3 | §IV, §VIII |
| A1, A2, A3, A10 | 1 each | §IV only |
| **total** | **42** | |

*(The review that produced this finding said 40. The per-amendment rows sum to
42; the count above is the one the script prints, and the rows are the record.)*

§I contains "addendum A8 subsequently replicated both plateaus" — in
claim-register-protected text. Under item 1 as written, a reader meeting that
sentence has nowhere in the article to learn what A8 is. Three amendments carry
argument rather than bookkeeping: **A5** changed the noise-scale estimator with
the E1 data already in view, which is what makes §VII's ordering result
exploratory; **A7** is the registered re-analysis on which §VII's independence
rests; **A8** is the registered replication behind the corrected plateaus,
Fig. 4's caption and §I's numbers.

**Requirement, for the reviewer's ruling:** if the log moves, the article
retains a one-line gloss for each amendment cited by number — **A4 through A9,
about 250 words**, not the ~80 words item 1 allows. A1, A2, A3 and A10 are each
cited once, inside §IV, and can move with a pointer. Item 1's net saving of
1.33 pages already accounts for this.

**Subsection coupling is otherwise light**, which supports option (a):
§IV-F, §IV-I, §IX-C, §V-G and §IX-D are **never** cross-referenced; §IV-G is
referenced once, from §IX-C, which moves with it; §IV-H once, from §IV-E.

### 6. Float areas, measured, and four candidates

| float | pages | float | pages |
|---|---:|---|---:|
| Table 1, amendments | **0.80** | Table 3, δ conditions | 0.33 |
| Table 2, resolution | **0.67** | Tables 4+5, A8 and δ predictions | 0.28 |
| Table 7, candidates | **0.67** | Table 6, accounting | 0.12 |
| Table 8, findings overturned | 0.40 | all fourteen captions | 1.07 |

Figure areas are less precise, because a figure's caption characters offset its
page deficit: F1 ~0.40, F4 ~0.44, F6 ~0.54, F3 ~0.34, F2 ~0.27, F5 ~0.28.

**Four candidates, offered as measurements rather than recommendations.** These
are with the reviewer.

1. **Table 7, ~0.45 recoverable.** Three rows of four prose columns, carrying
   the same three outcomes as §VIII's 1,059 words of prose. One of the two is
   redundant; a compact candidate-to-status table keeps the citable object.
2. **Table 2, ~0.40 recoverable, and it is the table still overfull** at 12-36
   pt. §IV-D and §IV-E need the resolution discipline, not all eleven columns;
   cell / bracket / width / ρ_eff,safe would fit and would fix the overfull box.
3. **Captions, ~0.30 recoverable.** They total 1.07 pages. Fig. 4's alone is
   four paragraphs; its two-corpus and whisker explanations are argument, and
   would sit in §V as prose.
4. **Figure 2, ~0.45 recoverable.** It is a schematic of equations (1)-(6),
   which §III also states algebraically. Dropping it removes no result.

**Arithmetic for a target.** Items 1-10 give 4.91. The four float candidates
give ~1.60. Option (a) gives ~0.45 and (c) ~0.28. Against 27 pages that is
**about 19.5-20 at best**, which is why the target of 19 now with the reviewer
is the one this measurement supports. Reaching 18 would additionally need part
of the 16-page tier; of those, items 12 and 13 (§V to ~1,900, §III to ~1,200)
are the least structurally damaging, because neither dissolves a section the
way item 11 would. Finding 6.1 recovers much of item 11's saving without
touching the §VIII/§IX boundary Draft 2 ruled on.


## Draft 4 — REVIEW RULINGS ON THE FLOATS, and the target, 2026-09-20

**Target: 19.** Success is a finished, defect-free submission below 20 pages
with enough margin that ordinary float movement cannot push it back to 20;
**19–19.5 is a successful endpoint.** (**Outcome: 21**, and accepted. The
target rested on a page-limit claim corrected below; see "Why".) §V → ~1,900 and §III → ~1,200 are **not**
pre-authorised; they are reconsidered only if the authorised set still leaves
the build above 20.

**Authorised, then recompile:**
- **Option (a)** with the **~250-word A4–A9(–A10) gloss retained** in §IV-H;
  the full log and Table 1 move to S1. *(Applied: increment 1.)*
- **Table 7 compact:** Candidate explanation | Registered test | Standing after
  calibration, with the asymmetric standings kept in words — concurrency no
  longer resolved after calibration; service time affirmed but not
  re-adjudicated; admission limit rejected before calibration.
- **Table 2 compact:** Cell | Boundary bracket (rps) | Resolution Δρ |
  ρ_eff,safe — the resolution column is the **normalised** per-cell resolution
  (coarsest 0.0127), not the raw bracket width. Full 11 columns to S1.
- **Fig. 2 to S1**, not discarded. *(Applied: increment 1.)*
- **Fig. 4 caption: all four paragraphs stay** with the figure; later
  sentence-level compression only.

---

## Why

IEEE Access recommends under 20 pages. This plan also said it required the
Editor-in-Chief's approval above that. **CORRECTED 2026-09-24. The Editor-in-Chief approval claim was wrong, and it was ours, not IEEE's.** It appears nowhere the author could verify: IEEE Access's author-guidelines pages 404, and current guidance is that there is **no strict page limit and no over-length waiver procedure** — editors judge length against the contribution during review. The 20-page line is a readability recommendation, which is what `OUTLINE.md` said all along; this file contradicted it and drove a cut pass on a premise nobody had checked. **21 pages needs no gate.** The cut pass was still worth doing — it removed repetition and unsupported aggregate claims — but it was not compelled by a rule. The first compile gave **26 pages** with defects; the
corrected build is estimated at **24-27**. The target is **18**, leaving room
for additions a reviewer asks for. That is roughly **6 pages**, which is about
4,500 words of prose plus about 1.5 pages of floats.

**The rule for this pass is different from W3's.** W3 could only remove a
repetition that did no local work, and it removed two words. This pass may
**move apparatus out of the article into a supplementary document**, provided
the argument stays in the article. Apparatus here means the audit trail that
makes the result trustworthy but that the reader does not need inline: the
amendment log, provenance records, procedure detail, record corrections. The
supplement ships with the submission as IEEE Access supplementary material and
sits in the Zenodo deposit, so nothing is lost, only moved one click away.

**What may not change:** the claim register's verbatim statements (§I, §II,
§X), any number, any finding, any withdrawn-phrase rule. Every moved passage
leaves a one-sentence summary and a pointer in its place.

---

## Measured starting point

Prose words by subsection, same convention as `section_wordcount.py` (tables,
comments and code excluded). Total **17,910**.

| § | words | largest parts |
|---|---:|---|
| I | 1,595 | one block |
| II | 1,376 | B 306 · C 321 · D 307 · E 192 |
| III | 1,650 | A 409 · C 336 · B 327 · D 287 |
| **IV** | **4,684** | **C 1,363 · H 811 · E 570 · D 539 · B 449 · G 325** |
| V | 2,708 | D 1,067 · C 542 · B 396 |
| VI | 1,492 | D 433 · B 317 · C 304 |
| VII | 1,306 | C 403 · B 290 · D 285 |
| VIII | 1,029 | evenly spread |
| IX | 1,615 | B 469 · C 466 · G 223 |
| X | 455 | one block |

**§IV is a quarter of the paper**, and most of it is protocol and provenance.
That is where the plan takes most of its pages.

---

## The proposed cuts

| # | where | action | words saved | floats | est. pages |
|---|---|---|---:|---|---:|
| 1 | §IV-H Amendments + **Table 1** | Move the amendment log to Supplement S1. Keep ~80 words: how many amendments there were, that each predates its governed data or analysis (with the N/A exception), and the pointer. | ~730 | −Table 1 | **1.4** |
| 2 | §IV-C Point classification and the search | Keep the classification rule and the search's logic; move the procedure detail (driver behaviour, edge cases, invalid-run handling) to S1. 1,363 → ~650. | ~710 | | 0.7 |
| 3 | §IV-G Provenance, §V-G Provenance | Move to S1; keep one sentence each. | ~330 | | 0.3 |
| 4 | §IV-D, E, B | Tighten. D (resolution) and E (what is quoted) justify the headline's phrasing and mostly stay; B (the SLO) keeps its definition and loses its derivation. 1,558 → ~1,150. | ~400 | | 0.4 |
| 5 | §IX-C Provenance and corrections to the record | The record corrections move to S1 beside the amendment log; keep what they changed. 466 → ~150. | ~310 | | 0.3 |
| 6 | §I Introduction | 1,595 → ~1,150. The claim-register statements stay verbatim; the trimming is in the set-up and the roadmap. | ~450 | | 0.4 |
| 7 | §V-C, §V-D | Keep the evidence and Tables 4-5; trim the narration around them. 1,609 → ~1,250. | ~350 | | 0.3 |
| 8 | §II-E, §IX-B, §VI-D, §VII-D | Tighten. §II-E's disclaimers can fold into one paragraph; the others lose restatement of results given elsewhere. | ~500 | | 0.5 |
| 9 | Figures | Set Figs. 1 and 5 (harness, overhead) single-column instead of full-width, if they stay legible. | | 2 figs | 0.7 |
| 10 | Tables 3 and 6 | Both are three rows; set them single-column. | | 2 tables | 0.3 |
| | **Total** | | **~3,780** | | **~5.3** |

**That reaches about 19-20 pages, not 18.** Reaching 18 needs one more of:
- **(a)** move §IV-F (achieved rates, 267 words) and §IV-I (reproducibility,
  211) mostly to S1, keeping the reproducibility statement's four identifiers
  in the article; or
- **(b)** move Table 8 (findings overturned) to S1 and keep §IX-D's prose
  summary of the three findings; or
- **(c)** cut §VII, the exploratory signals section, to its registered result
  plus the figure, about −500 words.

I recommend **(a)**: it is apparatus. **(c)** is the largest saving but touches
a result. **(b)** removes the table a petition reader is most likely to find
compelling, and I would not do it.

---

## If the target is 16 — the author's suggestion, 2026-09-20

**16 is achievable, but it is a different kind of pass.** From ~25 pages it
means removing about **9 pages**, roughly 8,000 words-equivalent, taking the
prose from ~17,900 words to about **11,000**. Everything above plus options (a)
**and** (c) gets to about 18.5. The last 2.5 pages need structural changes,
not tightening:

| # | action | est. saving |
|---|---|---:|
| 11 | **Merge §VIII into §IX.** §VIII (how calibration changed the candidate explanations) and §IX-D (claims overturned) tell the reversals partly twice. One section, "What changed, and what was overturned", with Tables 7 and 8. 2,644 → ~1,700. | ~0.9 |
| 12 | **§V to ~1,900 words.** Keep §V-B, the prediction and the A8 result; the §V-C three-condition discussion shrinks to Table 3 plus two sentences. | ~0.7 |
| 13 | **§III to ~1,200 words.** The four capacity terms and the error model stay; §III-C (admission) and §III-F compress. | ~0.4 |
| 14 | **§IV to ~1,800 words total** (plan above takes it to ~2,300). | ~0.5 |

**Costs of 16 over 18:** every section is rewritten, not trimmed; §VIII
disappears as a section, which changes the paper's structure and the §I
roadmap; and each cut removes something a reviewer might have wanted — the
margin for "please add" requests shrinks to nothing. It is roughly twice the
work of the 18-page plan.

**My recommendation remains 18**, with 16 as a stretch applied only if the
18-page build still reads long. The reason is specific to this paper: its
contribution is methodological, and the reviewer's trust rests on seeing the
checks. A 16-page version keeps the checks only by reference. If the author
prefers 16, the order is the same — build fixes first, then the 18-page cuts,
then items 11-14 — so choosing 18 now costs nothing if 16 is chosen later.

---

## Supplement S1 — "Protocol and provenance record"

One document, built by the same pipeline, carrying: the full amendment log
(today's Table 1 and §IV-H), the search procedure detail, the provenance
records from §IV-G and §V-G, the record corrections from §IX-C and, under
option (a), §IV-F/I in full. Its own short introduction says what it is and
that every item is cited from the article. **It is submitted with the article
and deposited on Zenodo.**

---

## What this costs

- **Sections §I, §II, §IV, §V, §VI, §VII, §IX are reopened.** Each cut is a
  new draft and goes through review, as every draft has.
- **The claim register and the checker are the guard.** Every cut section is
  re-checked against the withdrawn-phrase list and the verbatim statements.
- **Order matters:** the build defects get fixed first so the page count is
  trustworthy, then cuts are applied section by section, recompiling after each.
- **Rough effort:** two to three working sessions of drafting and review. That
  produces a paper that reviews better. (The clause that once stood here —
  that this was faster than waiting on an Editor-in-Chief exception — rested on
  the corrected claim above. There is no exception to wait on.)

## Decisions needed

1. **The approach and the target:** move apparatus to a supplement; target **18** (recommended) or **16** (items 11-14 as well). *(Author,
   then reviewer.)*
2. **The last page:** option (a), (b) or (c). *(Author; I recommend (a).)*
