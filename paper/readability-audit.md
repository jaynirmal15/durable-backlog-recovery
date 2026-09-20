# Readability pass — candidate list, measured not impressionistic

*Draft 1. 2026-09-20. **No edits made.** This is evidence for the reviewer to
rule on, because every section it touches is science-frozen and the pass's
mandate forbids deleting an owed forward-reference item to hit a number.*

*Method: section bodies below their header blocks, source comments, code fences
and table rows excluded — the `section_wordcount.py` convention. Cross-section
8-gram overlap, then sentence-level similarity, then a targeted search for
caveats stated in more than one section.*

---

## What the overlap measurement shows

| pair | shared 8-grams | verdict |
|---|---:|---|
| §1 ↔ §10 | 123 | **deliberate — do not touch** |
| §1 ↔ §2 | 70 | **deliberate — do not touch** |
| §2 ↔ §10 | 56 | **deliberate — do not touch** |
| §4 ↔ §6 | 18 | **candidate** |
| §5 ↔ §9 | 17 | mostly owed by forward reference |
| §3 ↔ §5 | 11 | definition then use; small |
| §4 ↔ §9 | 10 | **candidate** |
| §1 ↔ §3 | 9 | small |

**The three largest pairs are the claim register doing its job.** The headline
claim and the scale-mismatch statement are required to appear verbatim in §1,
§2 and §10 — that is what makes them a register rather than a style note. A
naive redundancy pass would cut exactly these and destroy the discipline the
paper's precision rests on. They are excluded from every recommendation below.

## Caveats stated in more than one section

| caveat | sections |
|---|---|
| no `[ρ_safe, 1]` interval; no cell degenerate or pinned | §4 §6 |
| `C_measured` is a normalisation reference, not a ceiling | §4 §6 |
| quoted resolution is the search step alone | §4 §6 §9 |
| no collapse factor is quoted | §4 §6 |
| the two terms are never combined in quadrature | §4 §6 |
| "at or near" measured capacity, not strictly below | §4 §6 §9 |
| δ carries its provenance at first use | §3 §5 §10 |
| the runner's provenance guard (commit, branch, dirty flag, start time) | §4 §5 §9 |
| two cells read 1.0002 | §4 §6 |
| live path is injector-direct and never enters NATS | §3 §4 |

**§4 ↔ §6 carries six of the ten**, which is structural rather than careless:
§4 is Method and defines the rules; §6 is the corrected boundary and uses them.
§4 is also the longest section in the paper at 4,755 words.

## The two clearest candidates

**1. The `[ρ_safe, 1]` sentence is near-verbatim in both.**
> §4: *"No [ρ_safe, 1] interval is constructed, and no cell is described as degenerate or as pinned at saturation."*
> §6: *"No [ρ_safe, 1] interval is constructed and no cell is called degenerate or pinned at saturation."*

0.92 similarity. One of these is a rule and the other is a restatement.

**2. The provenance guard is described three times** — §IV-G states it, §V refers
to it, §IX-C restates it in full with the same four fields.

## The argument AGAINST cutting either, which the reviewer should weigh

§6 must be readable by someone who has skipped §4. A reader arriving at the
corrected boundary and seeing per-cell values above 1.0 will construct exactly
the interval §4 forbids unless §6 says not to, at the point of temptation. The
same holds for `C_measured` as a reference rather than a ceiling.

**So the question is not "is this repeated" but "does the second statement do
work where it stands".** My reading, for the reviewer to overturn:

- **Keep** the `C_measured`-is-a-reference and "at or near" statements in §6:
  they prevent a specific misreading at the place it would occur.
- **Candidate for compression, not deletion:** §6's `[ρ_safe, 1]` sentence could
  become a clause rather than its own sentence, since §6-A already says
  utilisation is not assigned to collapsed endpoints.
- **Candidate:** §IX-C's restatement of the four provenance fields could cite
  §IV-G instead of re-listing them — §IX-C's point is the *absence* of those
  fields in the standalone tool, which needs the contrast but not the full list.

## What this pass should NOT do

Every one of these sections is science-frozen, and three of the ten caveats are
owed by an explicit forward reference from another frozen section. The mandate
is repetition, duplicated setup, repeated caveats, and sentences whose content
lives in a table — **targeting no number**. On this evidence the honest estimate
is **low hundreds of words, not thousands**. If that is disappointing, it is
because the sections were written under a rule that already forbade padding.

**Nothing here is a defect.** No factual error, no unsupported claim, no stale
instruction. This is a style question, and it is the first one in the project
that has been.
