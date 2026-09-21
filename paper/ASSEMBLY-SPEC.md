# Phase 1 — the assembly spec

*Draft 2, 2026-09-20. Draft 1 was reviewed against the real sources and missed
fourteen things. The rulings below **supersede Draft 1 wherever they conflict**;
Draft 1's text is kept beneath them as the record of what was specified and why
it was wrong.*

## Draft 2 — rulings on the fourteen findings

**1–2. Title and author block — SUPPLIED.** `frontmatter.md` now carries them
between `<!-- article:NAME:start/end -->` delimiters: title, short title (for
`\markboth`), author, address, corresponding author. The author block copies
Paper 1's submission exactly. No placeholders are needed.

**12. Front matter becomes an allowlist, not a strip list.** The build emits
**only** text between `article:` delimiters in `frontmatter.md` — title,
short-title, author, address, corresp, abstract, index-terms, biography — and
nothing else from that file. This removes the BLOCKER section, the
pre-submission note and the abstract's word-count note by construction, and it
removes the class of bug: a new drafting paragraph added to `frontmatter.md`
later cannot reach the article. **An `article:` delimiter that is missing,
duplicated or unclosed fails the build.**

**3. Fenced blocks inside section bodies are article content** and are set
verbatim in a small monospace display. The §V-D plateau arithmetic is the only
one. The halt rule now applies to a fenced block **with a language tag**, which
would signal drafting code rather than a worked display.

**5. Section headings:** `## <numeral>. TITLE` where the numeral is Roman *or*
Arabic — §I is Roman, §II–§X Arabic. The build takes the title and discards the
numeral; `\section` numbers. `### X. Title` is a subsection. Any other heading
level inside a section body fails the build.

**6. All eight equations.** Every indented literal line ending in `(n)` becomes
a numbered `equation` with `\label{eq:n}`; every prose `(n)` that denotes an
equation becomes `\eqref{eq:n}`, and a range `(4)–(6)` becomes
`\eqref{eq:4}–\eqref{eq:6}`. **Check:** the build's equation count equals the
source's, 8 today, and every label is referenced at least once. Prose
parentheses that are not equation references — "(n = 15)", "(2)" in a list —
must not be converted; the build converts only `(n)` for `n` in the set of
defined equation numbers, and reports every conversion it made so a person can
read the list once.

**7. Escaping** of `% _ & #` outside math and code is mandatory and is done by
the build, never by editing the markdown. `%` is the dangerous one: all 84 are
real percent signs, and an unescaped one silently deletes the rest of its line
without an error. **Check:** the count of `%` in body text equals the count of
`\%` in the generated `.tex` body.

**8. Unicode under pdflatex, not a switch to XeLaTeX.** The template's fonts are
Type 1 and its sample is a pdflatex document; changing engine changes the
template. Each character in the census (`— § ρ δ – · − × ≤ ± λ µ σ → ≥ ⌈ ⌉`)
gets an explicit mapping in the generated preamble — Greek letters to math-mode
symbols, `§` to `\S`, dashes to `---`/`--`, `−` to math minus. **A character
not in the mapping fails the build** rather than being dropped; the census is
the allowlist.

**9. Inline markdown.** `*italic*` → `\textit`; bullet lists → `itemize`.
Backtick spans split into two classes, decided by an explicit map, not a
heuristic: **variables** (`δ`, `S`, `C_config`, `C_measured`, `ρ_safe`, …) are
set in math mode with subscripts as `\mathrm{}`, which is IEEE style for a
variable; **identifiers** (commit hashes, file names, field names like
`trueCapacity`) are set in `\texttt`. A backtick span in neither class fails
the build. **Bold is the one open question — see A below.**

**10. Figure and table references become keyed, like citations.** The literal
numbers in prose are replaced, in the markdown, by keys — `[@fig:harness]`,
`[@tab:resolution]` — and rendered at build time to `Fig.~\ref{}` /
`Table~\ref{}`. This is the same design as the citation pass and for the same
reason: a number written into prose goes stale the first time the ordering
moves, and the §5 question below would move it. It also normalises the five
spellings of figure references to IEEE's "Fig. N". **This is a markers-only
pass over frozen prose** and is done by the drafter, reviewed, then committed —
not by the build.

**11. Captions get explicit boundaries.** Each caption in `CAPTIONS.md` is
wrapped in `<!-- caption:KEY:start/end -->`; only delimited text is set. What
falls inside F4's delimiters — which of its three trailing paragraphs are
caption and which are rationale — is a drafting decision, made by the drafter
against the outline's F4 requirements (n = 10, median, IQRs 1.71/1.29 rps,
long-arm non-discrimination, the two-corpus statement), and reviewed. The same
delimiter rule selects the **article table** from each `T*.md` file: T3 carries
a second table, *Sources, cell by cell*, that is artefact documentation and must
not be set.

**13. The bibliography: the committed file is authoritative.** The build emits
`thebibliography` directly — no BibTeX — in the order `references.md` commits,
one `\bibitem{marker-key}` per entry, entry text unwrapped, `*italic*` set
italic, comments stripped. It then recomputes first-appearance order from the
markers and **fails if the two disagree.** Recomputing and silently reordering
would let the printed article and the committed file diverge with nothing to
catch it.

**14. `IEEEbiographynophoto`.** There is no author photograph in the
repository and none is required at submission.

**4 and the table census — OPEN, for review.** There are nine tables, not four:
§IV's amendments table, **four in §V** (the δ-by-condition table, the A8
replication table, the δ-candidate predictions, the before/after accounting),
and the three generated artefacts. IEEE convention numbers every table in order
of first appearance. Two coherent options, which the reviewer rules on:
- **Number all nine.** Conventional; the §V tables carry registered data a
  reviewer will want to cite (the A8 table above all). Table 1 stays the
  amendments table; §V's four become Tables 2–5; the resolution table, the
  candidate-explanations table and the false-findings table become 6, 7 and 8,
  with any renumbering absorbed by the keyed references in 10.
- **Keep §V's four as unnumbered displays.** Preserves the current Table 1–4
  numbering, but unnumbered data tables are unusual in IEEE Access and cannot
  be cited by number.
**The drafter recommends numbering all nine.** Item 10 makes the renumbering
free, and the artefact file names need not change: a key is not a number.

**A. Bold — OPEN, for review.** The body carries 444 bold runs. That is drafting
emphasis; IEEE Access body text rarely uses bold, and a copy editor will strip
it. **The drafter recommends: bold in body prose is set as plain text; bold
inside table cells is kept**, because there it marks the registered choice and
the measured value (§V's prediction table) and carries meaning. The words do not
change, so the claim register's verbatim statements are unaffected.

### Review rulings, 2026-09-20 — both recommendations confirmed

**A — every article table is numbered, and the census is EIGHT, not nine.**
The reviewer caught the arithmetic: §IV's one, §V's four and the three generated
artefacts make eight. The ninth pipe table in the executor's count is T3's
*Sources, cell by cell* — artefact documentation, excluded by the table
delimiter rule above. **Invariant, replacing Draft 1's "exactly 6 figures and 4
tables":** the generated table count equals the source census (8), the figure
count equals 6, and every numbered float has exactly one key, one label, one
caption and at least one in-text reference. Artefact file names do not change:
the key is the identity, the printed number is presentation.

**The reviewer's numbering was wrong in the same way the Papadopoulos order was,
and the keyed build is what makes that harmless.** It placed the resolution table
at 6. The resolution table is first cited in §IV, before §V's tables, so by first
appearance it is **Table 2**. Derived from the keyed markers now in the sources:
Table 1 amendments · **2 resolution** · 3 δ by condition · 4 A8 replication ·
5 δ-candidate predictions · 6 accounting · 7 candidate explanations · 8 findings
overturned.

**The figures were already out of order, and nobody had noticed.** IEEE numbers
figures by first citation too. §IV cites the collapse figure (the old Fig. 5)
before the plateau figure, and the overhead figure (the old Fig. 3) is first
cited in §V. By first appearance: **Fig. 1 harness · 2 capacity model · 3 collapse
· 4 plateau · 5 overhead · 6 signals.** The printed "Fig. 3" and "Fig. 5" swap.
The keyed references absorb it; the executor should confirm that no figure PDF
prints its own number in its drawn title, which the keys cannot reach.

**B — body-prose bold is set as plain text; bold inside article table cells is
kept; template-controlled front-matter styling is outside the rule.** The words
do not change, so the claim register's verbatim statements are untouched. The
same applies to captions: bold in caption text is drafting emphasis and is set
plain.

**Unchanged from Draft 1:** LaTeX; the class used as shipped; the build
generates and never edits `paper/`; the six figures; the 40 MB check; the page
count reported from the PDF with where the breaks fall.

---

## Draft 1, as written — superseded where the rulings above conflict

*Draft 1, 2026-09-20. What the build must do to turn ten frozen markdown
sections into one IEEE Access LaTeX article and its matching PDF. Written to be
implemented as a script, because the build will be re-run after every late
change and a hand assembly cannot be re-run.*

**Decision taken: LaTeX**, not Word. The article source is generated from the
markdown by a script; the PDF comes from the same source in the same run, which
is how the two files stay identical in content — an IEEE Access requirement.

---

## 0. The template, which this machine cannot fetch

`https://ieeeaccess.ieee.org/wp-content/uploads/2026/05/ACCESS_latex_template_20260513-1-1.zip`

**Both shells are refused by the egress proxy (403 on CONNECT), so the author
downloaded it by hand.** **DONE 2026-09-20:** unpacked to
`build/template/ACCESS_latex_template_20260513/`, unmodified, and nothing else
in the build needs the network. **The class file is used as shipped** — no local
edits to `.cls`, ever, because a reviewer's build must match ours.

**Toolchain proven on this machine.** `pdflatex`, `latexmk`, `pandoc` and
`pdfinfo` are all present, and the template's own `access.tex` compiles to an
8-page PDF. **One finding:** the sample preamble loads `algorithmic.sty`, which
this TeX installation does not have. The article needs no algorithm environment,
so our preamble simply does not load it — **this is not a reason to install
anything, and never a reason to edit the class.** If some later need brings back
a missing package, that is a decision to record, not to work around silently.

---

## 1. Inputs, in article order

| part | source |
|---|---|
| title, authors, affiliation, ORCID | `paper/frontmatter.md` header material |
| abstract | `paper/frontmatter.md` (249 words, verbatim) |
| index terms | `paper/frontmatter.md`, alphabetical, 7 terms |
| §I–§X | `paper/section1.md` … `section10.md`, body below the first `---` |
| Table 1 | hand-written in `section4.md` — stays where it is |
| Tables 2–4 | `figures/T2-resolution.md`, `T3-candidate-explanations.md`, `T4-false-findings.md` |
| Figures 1–6 | `figures/F1…F6*.pdf`, vector, as built |
| captions | `figures/CAPTIONS.md` — the single source; never retyped inline |
| references | `paper/references.md`, in its committed order |
| biography | `paper/frontmatter.md`, after the references |

**No acknowledgements section.**

---

## 2. What the build strips

Everything that is drafting apparatus and not article text:

1. the header block of each file — everything above the first `---`;
2. every HTML comment, including plan-sync markers, citation inventories,
   cite-keys and exemption markers;
3. fenced code blocks that exist as drafting notes (none are article content
   today — **if the build finds one, it stops** rather than guessing);
4. the `W6-PLAN.md`, `OUTLINE.md`, `readability-audit.md` and registration files
   entirely — they are repository documents, not article parts.

**A strip is a deletion, never a rewrite.** If a construct is not in the list
above, the build fails loudly and a human decides; silent passthrough of
unrecognised markup is how a drafting note reaches a reviewer.

---

## 3. What the build renders

**Citations.** `[@key]` → `\cite{key}`, with the bibliography emitted in
first-appearance order so the printed numbers are 1–14 as derived. The mapping
is computed at build time from the markers, never from a stored list.

**Section headings.** `## N. TITLE` → `\section{TITLE}`; `### A. Title` →
`\subsection{Title}`. IEEE numbering is the class's job; the build must not
hard-code "§IV" anywhere it generates. Cross-references *inside* the prose
("§IV-G", "§IX-C") are prose as frozen and stay as written.

**Equation (1)** in §III is an indented literal today. It becomes a numbered
`equation` environment, and the prose references to "(1)" must resolve to it —
`\label{eq:staffing}` and `\eqref`, not a literal "1".

**Tables.** Markdown pipe tables → `table*` environments (they are wide).
Column alignment as in the source; the numeric right-alignment in T2 is
deliberate. Captions above tables, per IEEE style.

**Figures.** `\includegraphics` of the committed PDFs into `figure` or
`figure*`, captions below, from `CAPTIONS.md` verbatim. **F4's caption carries
the long-arm non-discrimination sentence** and must not be truncated to fit.

---

## 4. Checks the build runs, and fails on

1. **every `[@key]` resolves**, and every bibliography entry is cited — already
   enforced by `check_manuscript.py`; re-run against the generated source;
2. **no HTML comment, no `[@`, no `<!--` survives** into the `.tex`;
3. **figure and table counts**: exactly 6 figures and 4 tables, each referenced
   at least once in the prose;
4. **no overfull box** wider than the column — an overfull table is a layout
   defect a reviewer sees;
5. **`.tex` and `.pdf` are produced in the same run**, and the PDF is not stale;
6. **each file under 40 MB** (the figures are vector; this should be far under,
   and if it is not, something has been rasterised).

---

## 5. What the build produces, and the number we are waiting for

```
build/access/article.tex      the submission source
build/access/article.pdf      the submission PDF, same run
build/access/build.log        pdflatex output, kept
```

**Then the page count, which is the point of Phase 1.** IEEE Access recommends
under 20 pages and requires the Editor-in-Chief's approval above it. Report the
number from the generated PDF — not an estimate — together with where the
breaks fall, because if the article is at 20 or 21 pages the cheapest path may
be a figure size or a table split rather than cutting prose.

---

## 6. Then, and only then, the scans that need the assembled article

- the **promotion scan** — no withdrawn or superseded claim anywhere in the
  assembled text, captions and table cells included;
- the **marker audit**, re-run now that exemption markers exist;
- **acronyms defined at first use**, which the IEEE Access checklist requires
  even for acronyms already defined in the abstract;
- a read of the PDF end to end, by a person.

---

## 7. Boundaries

The build **generates**; it never edits `paper/`. If the markdown needs a
change, the change is made in the markdown by whoever owns that text and the
build is re-run. A fix applied to `article.tex` is lost on the next run and,
worse, makes the source and the submission disagree.
