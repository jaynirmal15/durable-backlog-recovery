# Cut plan — from ~25 pages to 18

*Draft 1, 2026-09-20. Proposed, not applied. Nothing in any section changes
until the reviewer and the author approve this plan.*

## Why

IEEE Access recommends under 20 pages and requires the Editor-in-Chief's
approval above it. The first compile gave **26 pages** with defects; the
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
  is a smaller delay than waiting on an Editor-in-Chief exception, and it
  produces a paper that reviews better.

## Decisions needed

1. **The approach and the target:** move apparatus to a supplement; target **18** (recommended) or **16** (items 11-14 as well). *(Author,
   then reviewer.)*
2. **The last page:** option (a), (b) or (c). *(Author; I recommend (a).)*
