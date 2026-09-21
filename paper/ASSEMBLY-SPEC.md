# Phase 1 — the assembly spec

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
