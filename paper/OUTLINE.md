# Paper 2 — section-by-section outline, v10.5

*2026-09-20. **v10.5 is v10.4 with the drafting-process notes removed at the author's instruction; no manuscript text is affected. v10.4 records the author's W6 decisions: B.E. confirmed (that hard check closes), biography approved as written, ORCID supplied, APC accepted — see `W6-PLAN.md` Phase 0.** **v10.3 adds the B.E./B.S. degree check to the W6 hard pre-submission checks, beside "publicly archived".** **v10.2 records the two F4 figure decisions (y-axis (1700, 2105) not compressed; measured bars not re-centred) as FINAL — see the F4 row — and marks the W5 artefact renames DONE at `f44d2f1`.**

**v10.1 closes W3. The readability pass is DONE and it removed two
net words.**

**THE W3 RULE, ruled and now formal — it governs any future pass:**
> **A repetition is removable only when its second occurrence performs no local
> interpretive function.**
Lexical overlap is not itself a defect. Six of the ten repeated caveats sit on
the §4↔§6 axis, which is method-then-application by design, and treating overlap
as the target would be the wrong optimisation.

**Two edits, both approved against that rule:**
- §6 draft 8 — the `[ρ_safe, 1]` sentence **compressed, not deleted**, into a
  clause of the sentence reporting 1.0002. It is 0.92-similar to §IV's, but it
  sits exactly where a reader who has just met a value above unity would invent
  the interval §IV forbids. The guard stays at the point of temptation.
- §9 draft 5 — §IX-C no longer re-lists the four provenance fields §IV-G
  teaches; it cites §IV-G. The contrast survives the cross-reference, and the
  four fields the standalone tool *does* record stay, because they are the
  evidence for the absence.

**Everything else was measured and kept.** The three largest cross-section
overlaps are the claim register's required-verbatim statements. The setup
enumeration in §1, §3, §6 and §10 each does local work — §III's states the span
across which one pooled constant holds, which is the point of that sentence.
§VI-B's cell enumeration is not duplicated by Table 2, which carries neither
service time nor concurrency.

**And a miss of my own worth recording: the audit estimated "low hundreds of
words". The actual saving is two.** The estimate was made from the count of
repeated caveats without first testing each against the rule that was about to
govern them; applying the rule disqualified eight of ten. **Do not re-open this
pass looking for the missing hundreds. They are not there, because the sections
were written under a rule that already forbade padding.**
**v10.0 closed the checker work. Three rounds of review found
eleven defects in it; seven were in versions I wrote, and three of those seven
were the check committing the defect it exists to catch.**
The one worth remembering: the outline's citation-inventory scope was resolved
with `text.find()`, which matched the tag **named in prose in the version header
announcing the fix** — so the "delimited" block ran 752 lines instead of 66 and
the hole it was meant to close stayed open. A fix defeated by its own changelog
entry. Tags must now sit alone on their line.
**And the item that was mine to decide:** my rewrite silently dropped
`"true capacity"` and `"statistically"` from the phrase list while fixing four
other bugs. Both prohibitions are live — item 33 for the first, this outline's
own claim register for the second — so a repair quietly removed coverage, with
no note, which is the failure class the list exists for. **Both restored**, with
four `withdrawn-quote-ok` markers at the legitimate sites: §III quoting the
harness specification as a primary source in order to contradict it, and the
three places where the prohibition itself must name the word it forbids.
Verified by control: a live "true capacity" assertion and a hard-wrapped
"statistically" both fail; the `trueCapacity` identifier correctly does not.
**v9.9 recorded a code review of the checker that found four bugs,
three of which were the checks committing the defect they exist to catch.**
The script is now `scripts/check_manuscript.py` (renamed — it does three things,
not one). What the review found:
1. **Phrase matching never crossed line breaks.** The old version built a
   three-line window to evaluate EXEMPTIONS but matched the phrase itself on a
   single line. These files wrap at ~78 columns, so a forbidden phrase split
   across two lines was invisible. It now matches a whitespace-normalised
   multi-line window and reports the starting line.
2. **Exemptions were lexical guesses** — "said", "never", "corrected" — so a
   live assertion one line from any of those became exempt. Replaced by an
   explicit `<!-- withdrawn-quote-ok -->` marker. Explicit exemptions are
   auditable; contextual guesses are not.
3. **Plan-sync never required a marker to EXIST.** Deleting one escaped
   silently while the script printed "all 10 marked current". Now every section
   needs exactly one marker, under its own plan heading, **equal** to the
   section's draft — draft 99 fails too.
4. **The citation check still read §2's version history**, which names the same
   works as the live inventory. Both inventories are now delimited with
   `<!-- citation-inventory:start/end -->`. Exact scopes beat inferred scopes
   for a check whose purpose is stopping stale text passing as live text.
Also: the bibliography is now the single source of truth — each entry carries
`<!-- cite-key: ... -->`, so adding a reference without registering it fails.
**Five negative controls pass**, including the wrapped-phrase case the old
version missed entirely.
**STILL MISSING, and recorded rather than pretended:** nothing scans the
assembled manuscript. `results/` stays excluded on principle — registrations are
immutable and the reports are the record — but the boundary that matters is
**promotion**: nothing quoted from a report into manuscript-facing text may
carry an unqualified withdrawn claim. **That check is a W6 task and does not
exist yet.**
**v9.8 added Papadopoulos to this plan's live Thread-4 anchor list,
which it was missing, and records the check that now prevents that.**
`references.md` had it at [14] with a note saying it attaches to §II-D. Neither
this plan nor §2's own citation inventory knew it existed — a work can enter the
bibliography and never reach the instructions that tell a drafter to cite it.
`scripts/check_withdrawn_phrases.py` now fails when a work in `references.md` is
absent from either inventory. It caught nothing else; Papadopoulos was the only
gap.
**v9.7 recorded the W4 bibliography, frozen at 14 sources, and two
source-alignment edits it forced in frozen §II.**
The reference list is `paper/references.md`, draft 4. Its source set is frozen;
**its NUMBERS are not**, and must not be hand-locked: IEEE numbers by order of
first citation, the citation markers are not yet inserted, and the predicted
order in that file is a prediction rather than a result. Insert markers first,
then generate the numbering.
§2 is at draft 5 for two narrowings, neither scientific: GitLab's incidents span
**late 2025 and early 2026**, not "across 2025"; and recurrence is claimed "in
production message processing", not across message-processing **systems**, since
both records come from one organisation's Sidekiq environment.
Also corrected, in `references.md`'s own working note: I wrote that the two
incidents were "fourteen months apart" when they are **68 days** apart — an
arithmetic error inside a note about the standard of evidence needed to say
"recurring".
**v9.6 recorded the two rulings that close W3 and the manuscript's
scientific phase.**

**§8 IS FROZEN, PACKAGE INCLUDED.** The regenerated Table 3 discharged the
condition: asymmetric schema, the admission-limit row no longer misclassified,
concurrency described as *no longer resolved after calibration* rather than
eliminated, service time preserving the unrecomputed-`h` limitation, A6
separated from calibration, and the generator still quote-asserted, idempotent
and numerically unchanged. **All ten sections are now scientifically frozen.**

**W3: RE-BUDGET UPWARD — option (b). Do not attempt the 4,460-word trim.** The
ruling: a 32% miss is too large to treat as editing drift, and the concentration
matters — §4 and §5 are long because they carry the methodological and
provenance burden that makes the central claim defensible. Cutting to satisfy a
planning estimate that was never measured under a defined convention would be
backwards. **`scripts/section_wordcount.py`'s convention is now authoritative,
the manuscript baseline is 18,308 prose words, and ~22-23 pages is accepted.
Twenty pages is a readability target, not a manuscript constraint.**
The §IV-C / §IV-H / §V redundancy audit I proposed is **explicitly not wanted**
as a prerequisite: it would turn a bad original estimate into a reason to reopen
frozen architecture.

**THE LATER READABILITY PASS HAS A DIFFERENT MANDATE, and it is written here so
the old one cannot come back.** Remove repetition, duplicated setup, repeated
caveats, and sentences whose information already lives in a table or a
neighbouring section. **It does not target 4,460 words. It does not target any
number.** It must never delete an owed forward-reference item to hit a budget.
If it removes 800-1,500 words, good; if it removes 400, also fine. **The
scientific record controls the length, not the old budget.**

Remaining work is manuscript-level: integration and readability, artefact and
table synchronisation, citation formatting, and submission checks. **Not
section-level scientific reopening.**
**v9.5 settled the word-counting convention — which nobody had ever
defined — and measures the manuscript against it. The result is that W3's trim
pass is roughly three times the size the plan assumed, and a decision is needed
before it starts.**

`scripts/section_wordcount.py` implements one convention and prints the
alternative beside it. **Counted:** body prose below the first `---`, headings
included. **Excluded:** the draft header block (a change log, stripped before
submission), HTML source comments (stripped in W6), fenced code blocks, and
markdown table rows — a table is typeset as a float, not as running text.

Measured, 2026-09-20:

| sec | prose | budget | delta |
|---|---:|---:|---:|
| 1 | 1,597 | 1,200 | +397 (+33%) |
| 2 | 1,407 | 1,500 | −93 |
| 3 | 1,703 | 1,200 | +503 (+42%) |
| 4 | **4,755** | 2,400 | **+2,355 (+98%)** |
| 5 | 2,748 | 1,600 | +1,148 (+72%) |
| 6 | 1,542 | 2,000 | −458 |
| 7 | 1,360 | 900 | +460 (+51%) |
| 8 | 1,072 | 900 | +172 (+19%) |
| 9 | 1,666 | 1,650 | +16 |
| 10 | 458 | 500 | −42 |
| **all** | **18,308** | **13,850** | **+4,458 (+32%)** |

**Three of these numbers were wrong in this plan and in the sections' own
headers, and §4 is the serious one.** Its header says "~2,000 words"; the
structure table said "currently 2,930"; it is **4,755**. Nobody had measured it.
§IV-C alone (point classification and the search) is 1,375 words — more than
half the whole section's budget. §IV-H is 817, §IV-E 582, §IV-D 551.

**THE DECISION W3 NEEDS FIRST, and it is not mine to make.** At the rate the
original estimate implies (~13,300 words ≈ 16–17 pages), 18,308 lands at roughly
**22–23 pages** with the same six figures and four tables. IEEE Access has **no
page limit and no over-length charge**; 20 pages is a readability
recommendation. So the two options are real, not one option and a penalty:
(a) **trim ~4,460 words**, concentrated in §4 (−2,355), §5 (−1,148), §7 (−460)
and §3 (−503), which is a substantial rewrite of sections whose science is
frozen — and every one of those sections is long because it carries material a
frozen forward reference promises; or
(b) **re-budget upward** to roughly the measured figures and accept ~22 pages,
spending the readability recommendation rather than the science.
**Do not start trimming before this is decided.** §9's length was settled by
exactly this argument — that cutting to a number means dropping something a
frozen section promises — and that argument applies with more force to §4 and §5.
**v9.4 fixed a stale §10 instruction and adds the check that would
have caught it — which the phrase checker could not, because the instruction
contained no banned phrase.**
The §10 plan still said "controller comparison as declared future work" after
§10 draft 2 had removed exactly that. Semantically dead, lexically innocent: a
string checker cannot see it. So every plan heading now carries
`<!-- plan-synced-to: sectionN draft M -->`, and
`scripts/check_withdrawn_phrases.py` fails when a section has moved past its
plan's marker. **That does not prove a plan is correct — it proves someone has
claimed it is current since draft M.** The claim is cheap; its absence is the
signal. Workflow: re-read the plan against the section, fix what has gone stale,
bump the marker. It caught a live case within a minute of being written (§10 at
draft 3 against a marker of 2) and its negative control passes.
The §10 plan itself is rewritten: the empirically-validated-reference wording
rather than "measure capacity rather than accept it"; offline-versus-online left
to a separate study with **"controller comparison as declared future work"
explicitly banned**; and the close stated as what C4 establishes — the
pre-registered record made the reversals **explicit and auditable** — rather
than that pre-registration *made the retractions possible*, which claims
causation C4 does not support.
§10 draft 3 also takes a copy edit flagged for W5 — "overstated its own service
capacity **by** a per-request timing bias of 0.463 ms" mixed a throughput
overstatement with a time quantity, now "**because of**". Taken now rather than
carried, because a defect held until W5 is one more thing to remember and
remembering is what has failed five times here.
**v9.3 turned the withdrawn-phrase rule into a check that runs, and
records §10 draft 2 as science frozen — every section is now drafted and nine of
ten are frozen.**
`scripts/check_withdrawn_phrases.py` fails if a withdrawn phrase appears in
manuscript-facing text. Seven phrases so far, each with the reason it was
withdrawn and the wording that replaces it: *the conventional construction*,
*the default answer*, *which was sound*, *which is impossible*, *true capacity*,
*apparent finding*, *statistically*. **Add to that list whenever a phrase is
withdrawn — that is now part of withdrawing it.** Run it at W5, and before any
freeze that follows a withdrawal.
Two design decisions, both learned from the first run. **It reads only what a
reader of the paper sees or what generates that** — `paper/section*.md` bodies
below the header block, `OUTLINE.md` below its version header, `figures/*.md`,
`scripts/make_*.py`. `results/` is excluded on purpose: registrations are
immutable once cited and the reports are the historical record, so a correction
notice quoting the wording it corrects is doing its job. The unscoped first
version fired 25 times, nearly all on legitimate history, and **a check that
always fails is a check nobody runs.** And it judges on a **context window, not
a line**: these files wrap at ~78 columns, so a prohibition and the phrase it
prohibits routinely land on different lines; line-matching reported four such
splits as violations. Verified both ways — clean on the current tree, and it
catches the §VII regression when that phrase is reinjected.
**v9.2 recorded §10 draft 1 — the last undrafted section — and a
FIFTH instance of the withdrawn-phrase failure, this one in a frozen section's
body.** §VII's close still read "§II sets out why latency feedback is the
conventional construction". v9.0 corrected the §7 PLAN line and I swept only
this outline, not the manuscript, so a frozen section was left asserting exactly
what §2 had retracted — and §2 and §VII contradicted each other on the page.
§7 draft 6 fixes the clause; its findings are untouched. **The control, now
stated for the fifth time and evidently still not being applied: when a phrase
is withdrawn, sweep the OUTLINE AND EVERY MANUSCRIPT SECTION AND EVERY GENERATED
ARTEFACT, not just the file the reviewer was looking at.** The five: the F6
caption through five layers; the Set A narrative; v8.9's "conventional
construction" banned in a header while two planning lines taught it; v8.9's
"probe was sound" instruction surviving its own withdrawal; and this.
§10 came in at 454 words against a 500 budget and is deliberately not padded.
**v9.1 removed a fourth instance of the same failure v9.0 was
written to fix, and this one I introduced while fixing the third.** v8.9's
Thread-4 instruction told a drafter to write "the independent timing probe,
which was sound" — §2 draft 2 duly wrote it, review caught that it contradicts
frozen §IX-B, draft 3 withdrew it from the manuscript, and **the instruction
stayed in this plan**. A phrase withdrawn from the body while its instruction
survives in the plan is not withdrawn. That is now four occurrences of one
mechanism in this project — the F6 caption, the Set A narrative, v8.9's
"conventional construction", and this — and the control is the same every time:
when a phrase is banned, remove it everywhere a drafter reads, not only where a
reviewer found it. v9.1 also records §2 draft 4 (science frozen): the opening no
longer claims the paper contributes to only one of the four literatures, and the
incident records support "backlogs and queueing-objective violations" rather
than "recovery-driven" ones.
**v9.0 removed the two live planning lines that still told a
drafter to write the exact overclaim v8.9 had just banned at the top of this
file.** The §2 plan said "§II-B's last paragraph … establishes that latency
feedback is the conventional construction" and the §7 plan said "§II establishes
that latency feedback is the conventional construction". Both now say what the
citations support and what C3 actually needs: **§II establishes live latency as
a literature-grounded comparator for §VII** — DAGOR and Breakwater key on
queueing delay, Bouncer on response-time percentiles, and none of the three
establishes an industry default. A banned phrase recorded only in a version
header is not banned; it has to be removed everywhere a drafter reads.
v9.0 also records §2 draft 3, which withdraws "external measurement was sound"
(it contradicted frozen §IX, which concedes the probe's effective resolution was
never measured), source-bounds a second residual gap claim in §II-A, separates
the AWS and incident-record evidentiary jobs, and narrows *The Tail at Scale* to
context only.
**v8.9 corrected the §2 anchor list after review of draft 1 found
three of them over-read, and closes the one unverified citation.**
(a) **Breakwater is verified and closed**: Cho, Saeed, Fried, Park, Alizadeh and
Belay, *Overload Control for µs-scale RPCs with Breakwater*, OSDI 2020,
pp. 299-314.
(b) **A signal mismatch was hiding in thread 2.** DAGOR and Breakwater both key
on **queueing delay**, while §VII concerns live **response-time percentiles**,
so citing only those two to support a latency-feedback claim over-reads them.
**Bouncer** (SIGMOD Companion 2024, `10.1145/3626246.3653384`, arXiv 2312.15123)
admits on estimated percentile response times against response-time objectives
and closes the gap. The claim itself is softened from "the conventional
construction" and "the default answer supplied by this literature and production
practice" to **"an established construction"** — do not restore the stronger
form, which no cited work supports.
(c) **Two over-attributions in thread 3, both corrected.** Autopilot shows that
manually managed jobs carry more slack than autopiloted ones, for CPU and memory
limits — **not** that "engineer-supplied limits are routinely wrong", and not
anything about downstream service capacity; the analogy is to the practice, not
the quantity. And *The Tail at Scale* does **not** support "small and unmodelled
per-request costs dominate what a system can deliver at high utilisation"; it
supports rising tail sensitivity with scale and utilisation. The overhead
mechanism's real anchor is **Barroso et al., *Attack of the killer
microseconds*, CACM 2017, `10.1145/3015146`** — small overheads growing large
relative to short service times, which is this paper's arithmetic exactly.
(d) **Heiser's catalogue is a maintained web resource, not a peer-reviewed
paper.** Using it as a catalogue is fine; listing it as a venue-and-year
citation is not.
**v8.8 recorded §2 draft 1 and what its literature search did and did
not establish.** Threads two, three and four have real literature and the
anchors are verified to venue and year (listed in the §2 plan below). **Thread
one does not**: searching for peer-reviewed work on the drain-rate question
returns practitioner guidance (AWS Builders' Library on queue backlogs) and
public incident records (GitLab's recurring Sidekiq queueing SLO violations),
not research. §2 therefore says the problem is documented operationally and the
guidance is qualitative, and **does not claim a literature gap** — two queries
are not a systematic search, and "no prior work exists" is exactly the shape of
claim this campaign has twice had to withdraw. If a gap claim is wanted, it
needs a recorded search protocol. §2 draft 1 came in at 1,245 words against a 1,500 budget and draft 2 at 1,404;
the room is deliberate and thread one must not be padded.
**§II-A must not claim a gap, and draft 1 did so by accident** — "we are not
aware of a published measurement" and "a first measurement" are the same claim
the draft's own sourcing note forbade. The permitted form is source-bounded:
*the operational sources reviewed here do not quantify that boundary or report
it with experimental resolution*, and this paper supplies such a measurement.
Never "first", "no published measurement" or "no prior work".
**Also struck from §II-A:** broker-side replication, which is a durability
mechanism and not a drain-rate or admission one.
**v8.7 was one mechanical correction: this plan called §9 "six
subsections" while the drafted section runs A through G — six validity
categories plus a closing future-work subsection, i.e. seven labelled.** Both
places are corrected. It also records the §9 science freeze at draft 4 and one
executor task the freeze raised: `figures/T1-false-findings.md` (manuscript
Table 4) and its generator `scripts/make_table1.py` still say 18 of 20 unsafe
points reported rates above what their cell can serve "which is impossible",
which §IX struck at draft 4 because §VI states `C_measured` is a normalisation
reference and not a physical ceiling. **§IX and the table it prints must not
disagree.** No manuscript science depends on the subsection count.
**v8.6 synced two stale instructions and corrects the planning
target, after §9 draft 3.**
(a) The §9 plan's clock bullet still carried the wording §9 draft 2 replaced —
"nominal 1 ns … cannot bound quantisation error … by its own instrument". The
first clause reads as a resolution claim the paper immediately disowns
(representation granularity is not effective resolution) and the second is
over-categorical (a clock CAN be characterised independently; this one was not).
Synced to draft 2's language so a regeneration cannot restore the bad version.
(b) **The finer-bisection reasoning added at v8.4/v8.5 is WITHDRAWN.** It said a
finer search alone would not settle the residual because the effect, at 19-24%
of a step, is comparable to the denominator term of 0.09-0.80 of a step. That
does not follow: a narrower step shrinks the search component and leaves the
denominator term unchanged, so the conservative threshold falls and a difference
of about 1.2 steps may well become resolvable. §9 draft 3 and §6 draft 7 are
corrected; this plan must not reinstate it.
(c) **The ~13,300-word target is stale, and the section budgets are not measured
the way the drafts are.** Budgets now sum to **13,850**. Raw drafted body,
counted including tables and arithmetic blocks, is about **17,100** across the
eight drafted sections; every section's own header reports a smaller number
because headers count prose and exclude tables and code. Neither convention is
wrong and nobody has said which the budgets use, which is why the two sets of
figures have never reconciled. **Fix the convention at the W3 trim pass, then
re-budget** — §4 (budget 2,400, header 2,930, raw 5,167 with T1) and §5 (budget
1,600, header ~2,250, raw 3,048 with the arithmetic blocks) are where the gap
lives, not §9.
**v8.5 deleted two instructions with no source behind them, and
records three rulings from the §9 review.**
DELETED, because drafting §9 against the artefacts could not find them:
(a) the drafting-constraints claim that the precision sweep "found one error in
70 hand-written values and zero in 241 generated ones". `results/REVIEWER-
RESPONSE-W2.md` reports 401 over-precise **occurrences**, 241 generated and 160
hand-written — a count of over-precision, not of errors, with no "70" and no
error audit anywhere in it. The every-number-traces-to-a-generated-artefact
discipline now rests on what the sweep actually shows and on the F6 and
candidate-explanation failures in §IX-C, which are real.
(b) three of the four harness-defect examples in the §9 plan — stale trace
shadowing, an E2 run-ID collision, and the E1B report quoting the sixth of
twelve elements as a median. None has a source in the Paper 2 artefacts; the
only near-hit is `results/e2b-interrupted/README.md` saying a plain trace
"has silently shadowed a good one in this project **before**", i.e. referring to
a prior incident rather than recording one. **Do not restore them without a
primary artefact.** The two sourced examples are enough for the point.
RULINGS RECORDED: §9 keeps its expanded structure, not four subsections — six
validity categories plus a closing future-work subsection, labelled A to G (v8.5
said "six", corrected at v8.7); its budget is raised from
1,100 (see the §9 plan for where it landed and why); and §VI's forward promise
is weakened at §6 draft 6 because no artefact specifies the finer-bisection
design.
**v8.4 recorded two debts §IX owes that this plan did not carry**,
both found by reading the frozen sections' forward references before drafting
rather than after review. (1) Frozen §V-B ends: *"§IX records the right-skew of
the per-cycle distribution, the clock-resolution argument and the
percentile-buffer caveat."* None of the three was in the §9 plan. The compression
pass at §V draft 15 moved them here and the plan was never updated, so §IX would
have been drafted owing a promise made in a frozen section. (2) §VI and §VII name
**two different** future experiments — the finer-bisection study that would
resolve the four-pair residual, and the near-boundary 5 rps sweep that would
resolve the signal ordering — while the plan said "named future experiment"
singular. Both are listed below. v8.4 also records that `results/METHOD-AUDIT.md`
item 33 still calls `figures/T1-false-findings.md` the manuscript's Table 2,
which v7.1 made Table 4; the outline's own copy of that note was corrected in
v8.2 and the audit's was not.
**v8.3 finished the renumbering v8.2 claimed to have finished, and
clears three more stale instructions.** v8.2 fixed the table inventory but left
the live §6 plan and the structure table still calling the resolution table T3,
which §8 now owns — those are **Table 2** throughout. Also: the target line said
three tables when the manuscript has four; the §8 table instruction still opened
"deliberately not 'what killed it' — that answer is 'the calibration correction'
three times over", which contradicts the asymmetric structure printed four lines
below it; the §6 residual paragraph still justified declaring the residual by
saying it has "the exact shape of the three findings that already died in this
campaign", which is leftover symmetric-trio rhetoric that no longer describes
anything (§IX's three retractions are a different set and were not killed by
calibration); the W2/W3 scheduling note still said §8 drafts from T2; and the
citation-order mapping still read "T3 Set A", a label v8.0 retired.
**v8.2 cleared the instructions that v8.0's restructuring left
invalid and that a regeneration would otherwise obey.** Four of them were live:
the §8 plan's table instruction still said all three rows "appear in A6's
conclusions table as surviving A6's estimator correction and fall only to the
calibration correction" (two of the three do not fall to calibration at all, and
the admission limit was refuted before it); its proposed caption still read
"three second-order findings that survived their registered falsification tests
… and disappeared"; its A6 conceptual sentence still described A6 as changing
how utilisation is estimated at collapsed points and as leaving three findings
standing; and the §5 plan's opening still said three effects each survived.
Column 1 of Table 3 becomes **"Candidate explanation"**, not "Apparent finding":
the admission limit was explicitly not a finding. v8.2 also resolves the
executor search (no pre-E2 written result asserts the cap governs — only
`STATUS.md` at `c823393` recording it as an open competing explanation), records
Table 3 as BUILT at `c0a4eb2`, and removes the last mixed T2/T3 numbering from
the table inventory and the W5 rename instruction, which still pointed
`T1-false-findings.md` at Table 2 after v7.1 made it Table 4.
**v8.0 retires the symmetric Set A / Set B framing**, which assumed
more symmetry than the evidence contains. §8 becomes *How calibration changed the
interpretation*, with three rows at three DIFFERENT statuses: concurrency as the
complete case, service time as affirmed-but-not-re-adjudicated, admission limit
as a CONTRAST — a registered falsification that succeeded. §1 draft 15 and §5
draft 22 are substantively corrected, not synced: C2 is narrowed and the
scale-mismatch claim goes singular. v7.1 renumbered the manuscript tables into citation order** —
T1 amendments (§4), **T2 resolution (§6)**, T3 Set A (§8), T4 Set B (§9) — done
NOW rather than at W5, because drafting §8 and §9 against wrong table identities
is the copy-forward debt this project keeps unwinding. Only the generated
FILENAMES wait for W5; filenames do not determine citation order. v7.1 also
found a fourth table-reference mismatch: §V-G cited the false-findings table for
three items that table's own header excludes. **v7.0 restructured §8 and §9.** The paper carries TWO distinct
sets of three retracted findings, and §8's plan pointed at one while its table
held the other. **Set A** — the boundary depending on concurrency, on the
admission limit, on service time — are artefacts of the calibration bias, and
are what §1 and §5 promise §8 delivers. **Set B** — bimodality, the 4.1%
occupancy rule, A4's validity at every point — were killed by replication, by a
test cell and by an orthogonal cross-check, and are NOT calibration artefacts.
§8 now takes Set A alone; Set B moves whole to §9. The two have different theses
and must not be merged. §4 keeps only the method fact it needs and
cross-references §9. Table numbering is now out of citation order and is
deferred to W5 — see the deliverables table. v6.5 replaced the §7 plan's "no observable leads" and its
precursor-room hypothesis with §VII draft 5's two-cell result: the corrected
corpus does not reproduce the ORDERING; it does not show that nothing warns.
Four metrics warn with one point of room in the short-service cell. v6.4 cleared
the last three: the aggregator paragraph still
described F5's mixed axes as a live defect, the §6 plan still flagged §1's
tenfold statement as undecided (§1 draft 12 decided it), and the residual
instructions still carried 11-17%, "~1.1 steps" and rounding-as-evidence. v6.3
cleared five stale detailed-plan lines that the v6.2 header had
already contradicted: the §1 plan's unqualified tenfold SLO range, T1's "Eight
rows" sitting above a ten-row list, the §6 plan's "three repetitions", its
0.9999 (a median-route value), and the residual instructions' 1.25× ratio.
v6.2 synchronises every F5/T3 figure to the frozen MAXIMUM
aggregator: the spreads are **0.0719 -> 0.0071**, not the median-derived
0.0716 -> 0.0068, and no collapse factor is quoted anywhere. The pairwise excess
is **19% to 24%**, not the 11-17% that REVIEWER-RESPONSE-W2's hand-written
median table gave. §1's "tenfold range" is scoped to match §6. v6.1 REVERSES v6.0's aggregator "fix", which was wrong and
reversed a correct statement. Frozen §4 names the **maximum** achieved ρ across
the last SAFE point's repetitions as the per-cell scalar, explicitly for Fig. 5,
and says two cells reach **1.0002 under the named aggregator**. v6.0 asserted the
named aggregator was the median. It is not. F5's both-median change at `3c00a6e`
therefore contradicts frozen Method and must be regenerated under **max on both
axes**. v6.1 also fixes the concurrency count to FOUR, verified from the cell map
(7, 10, 35, 50). v5.9 records the SLO-sensitivity scope limit — the sweep spans a
tenfold range but four (cell, threshold) pairs are excluded by a rule fixed
before it ran, so the S=25 arm's evidence spans only 100-500 ms — and flags that
frozen §1 says "tenfold" without that qualification. v5.8 records the T1/T2
artefact-name collision and the §6 inputs now confirmed against the repository. v5.7 records A9 `9caf476` and A10 `51026cc` in T1 as record
corrections with N/A temporal columns, updates the §4 count to ten, and fixes
F5's spread to the committed 0.0716/0.0068 at `3c00a6e`. v5.6 records the §6 drafting constraint that F5 and §V-F are NOT
one effect — renormalising by measured capacity closes the inter-arm gap further
than physically correcting the harness does — and updates F5's spread to the
both-median figures pending the rebuild. v5.5 records the `overhead_run` provenance gap: the plateau windows
and A8's twenty windows carry no commit, dirty flag or timestamp, so the
prospectivity of the plateau test is bounded by surrounding commits rather than
established by the records. §9 gains it as a threat item. v5.4 propagates the open-loop rate-limit wording into the §3 plan
and records that §1 draft 10 carries it too; A9 is registered as a record
correction (not an amendment) and T1 gains a ninth row whose temporal columns read
N/A. v5.3 fixes three §4/§5 plan lines that were looser than the frozen
manuscript: the sleep correction now carries its δ provenance, A8's short-arm
outcome is "satisfied its preregistered criterion" rather than "confirmed", and
the 24% replicate-spread figure is scoped to the five replicated last-SAFE
endpoints it actually covers. v5.2 clears four stale instructions that contradicted the frozen
manuscript: §3's architecture bullet still described a broker-only live path,
§3's pooled-δ bullet still ended with the "predicts capacity more precisely" and
"put this here as validation" sentences that the same bullet now forbids (an
incomplete edit in v5.0), §5's plan still credited the short arm with the long
arm's criterion, and §9 still asserted the load effect was "not plausibly window
scatter" when §5 calls that comparison indicative. v5.1 downgrades §3's pooled-δ result from "validation" to an
in-sample common-parameter check, records the §3/§4 live-traffic resolution (the
code is authoritative: live = injector-direct; post-restoration brokered messages
are a separate population the objective excludes), and replaces the withdrawn
quadrature factor 1.29× with the linear conservative bound 1.09-1.80×.
v5.0 records the reserved DOI `10.5281/zenodo.22761131`
(deposition 22761131) and that §4 draft 15 now cites it in place of the
placeholder. The outage draft 22740491 was deleted and its reserved DOI
forfeited; it was never cited in the manuscript. v4.9 resynchronises §5's plan with the manuscript's actual
evidentiary hierarchy — the plan still carried the pre-A8 wording that several
revisions were spent removing — corrects the registration interval to 39 minutes
against a committed timestamp, records that A8 registered a DIFFERENT reading per
arm, adds the pooled-correction rationale and its chronology, and fixes the
"three researchers" violation in §8. v4.8 records F4 as built against A8 (b59f83a) and two decisions
deferred to the W5 figure pass: the y-axis is NOT compressed and the measured
bars are NOT re-centred. v4.7 carries A8 into the artefacts that A8 made incomplete:
T1 gains an eighth row, §4 is reopened for it, F4's caption requirement is
replaced now that the corrected plateaus are replicated rather than n=1, and §9
gains the direct probe's unmeasured between-window repeatability. v4.6 records
the A8 replication and discharges the n=1 limitation. v4.5 moved the 96.3% supersession to §9 and adds the n=1
warning to F4's caption requirement. v4.4 recorded denominator uncertainty in T3 and §9. v4.3 synced "invalidate" and drops "confirmatory" from the A7
description. v4.2 added the F4 caption requirement and records the dataset map
(seven cells vs E2e). v4.1 cleared three stale phrases ("baked in at all", "true
capacity", "SLO invariance") and records that C_measured is a normalisation
reference rather than a ceiling. v4.0 withdrew the headline numeric range (mixed precision),
names the per-cell aggregator, and forbids repeating A6's strict inequality.
v3.9 synchronised the claim register, §7's opening and §10 with
addendum A7 — three places still carried the pre-A7 ordering claim — and removes
the "estimated continuously" over-claim that contradicted frozen §I. v3.8 split T1's temporal column, raises the §4 budget and adds
the §6 naming requirement for rho_eff. v3.7 recorded addendum A7: C3 is exploratory, and the decision
not to run a finer sweep to settle it (2-3 days, ~60 runs, plus a tail risk this
campaign has repeatedly realised; the argument rests on C1 and C2). v3.6 removed the last "invariant" and "prefer" leaks and the
universal "any controller" phrasing; §1 and §3 frozen at draft 5. v3.5 added C_model to the terminology set, fixes the T3 headings
and narrows the §7 sentence. v3.4 reopened two claim-register entries after the §1/§3 review
and adds the capacity-terminology rule. v3.3 moved the Zenodo deposit to W6, reserving the DOI now.
v3.2 folded in the precision-sweep findings. v3.1 revised the precision rule and the prediction arithmetic
after the executor's confirmation pass. Supersedes v2. v2 restructured the paper after external review;
v3 revises the claims after the W2 provenance and resolution analysis
(`results/REVIEWER-RESPONSE-W2.md`). Companion to plan v4.*

**Target:** IEEE Access. Two-column. **The ~13,300-word figure is stale as of
v8.6 and is kept only as the original planning intent.** Section budgets now sum
to 13,850; raw drafted body across the eight drafted sections is about 17,100
counting tables and arithmetic blocks, which is not the convention the section
headers use. Settle the counting convention at the W3 trim pass and re-budget
from it — until then no total in this outline is authoritative. 6 figures +
4 tables ≈ 16–17 pages on the original figure, inside the recommended 20. No page limit and no over-length
charge at IEEE Access, so 20 is a readability recommendation, not a cost
cliff. APC $1,728 at Jay's member + society rate.

---

## 0. Claim register — exact wording

These sentences are settled. Drafting transcribes them; it does not reopen
them. Every one is constrained by the resolution analysis.

**Headline (abstract, §1, §10):**

> Across seven cells the safe drain boundary lay within 1% of *measured*
> service capacity, and was indistinguishable from capacity itself at the
> experiment's resolution.

<!-- withdrawn-quote-ok: the prohibition itself, and its rationale quotes the word -->
**"Statistically" is struck.** The indistinguishability argument rests on
bisection resolution, interval width and replicate spread — an
experimental-resolution claim, not an equivalence test.
<!-- withdrawn-quote-ok: the rationale names the struck word -->
Saying "statistically"
invites "which test, which null, which equivalence margin, which confidence
level," a fight the paper does not need and §4 does not equip it for.

**No numeric range is quoted for the headline.** The lower endpoint, 0.993,
comes from E2b at C = 400 — the one cell the precision rule restricts to two
decimals — so any range spanning the cells mixes precisions and asserts one the
cells do not share. §VI reports per-cell values at each cell's own resolution in
Table 2 instead. Four decimals were never warranted: 0.9999 differs from 1.0000 by a
fiftieth of a bisection step.

**The collapse (F5 caption, §6):**

> Before correction the between-cell spread was resolvable; after correction
> it falls below per-cell bisection resolution — for the two cells defining
> the residual, E2b's resolution of 0.0127 exceeds the residual of 0.0071
> outright (0.0068 was the superseded median-derived figure).

Not "a factor of 10.5". The ratio invites a question about the ratio's own
uncertainty. Detectability is the claim, and detectability is what the paper
is about.

**The overhead (C2, §5):**

> A per-request overhead **approximately service-time-independent — constant
> to within 4% across a fivefold service-time range** — (per-arm medians 0.4690 ms at S=5 against 0.4505 at
> S=25; probe constants 0.5165 against 0.5114), and **varying with offered
> load** (0.463 to 0.517 ms across four measurements by two instruments).

Quote the 4%; never imply exactness. And state the direction: δ is *smaller*
at S=25, whereas proportionality requires it to be five times larger. Both
instruments agree in sign. The residual service-time dependence runs opposite
to the hypothesis under test, which strengthens the constant-versus-
proportional result rather than qualifying it.

Never "the overhead" unqualified. Every δ is named with its load condition
and its instrument. This is a strengthening, not a hedge: a fixed overhead is
something an engineer bakes into a capacity model once; a load-varying one
cannot be represented reliably by a single fixed correction across load
conditions. The paper therefore requires an empirically validated capacity
estimate but **does not determine whether that estimate should be supplied
offline or inferred online** — frozen §I says so explicitly, and the register
must not say otherwise.

**Scale mismatch (§1, §2 — the novelty statement):**

> When the safety margin being characterised is sub-percent, a small and
> approximately service-time-independent per-request timing bias can exceed the
> phenomenon under study, generate a stable but false second-order effect,
> survive deliberate falsification, and invalidate conclusions about which
> signals are usable for control.

"Invalidate", not "reverse": after A7 the signal conclusion became unsupported
rather than inverted.

**Precision rule — report each value to the resolution of its own cell.**
Three decimals for cells at C >= 1400; two for E2b, whose resolution is
0.0127. Never four, anywhere. **No strict inequality against a bound the
rounding touches** — "every cell sits below 1.0" resting on a highest value of
0.9999 is the over-claim this rule exists to catch, and it contradicts a
headline range that already ends at 1.000. Table 2 makes per-cell resolution auditable, which is
what licenses the varying precision. A flat two-significant-figure rule was
considered and rejected: it is coarser than the instrument, and it would
destroy the 0.0689 concurrency gap that is the central uncorrected finding.

**Registrations are reproduced verbatim and are never re-rounded.** A
registration records what was predicted before the data existed; reducing its
precision afterwards falsifies the record, and a reader comparing a registered
0.9937 against a measurement needs the digits as registered. §4 states this as
policy, so that registrations carrying more digits than the analysis supports
read as discipline rather than inconsistency.

**Percentages:** 9.26% and 1.85% — same precision, both.

**One aggregator, named.** Where a single per-cell value is needed, it is the
maximum achieved ρ across the last SAFE point's repetitions, and the figure that
plots it says so. F5 uses the maximum on **both** axes, matching frozen §IV, as
of `e04cbc9`; the previously committed mixed-aggregator and both-median versions
are superseded and must not be reinstated. The
choice is numerically immaterial (largest within-point spread 0.0010, below both
the rounding step and the search resolution), which is exactly why it must be
stated rather than left to inference.

**Do not repeat A6's "every cell sits below 1.0".** That wording is true under
median and false under the aggregator F5 plots, where two cells reach 1.0002.
Both round to 1.000, so nothing published changes — but an aggregator-dependent
strict inequality is precisely what the no-strict-inequality rule above
forbids. A6's text is quoted verbatim where quoted, and the paper's own
statement uses the non-strict form.

**Capacity terminology is rigid and the four terms are never interchanged:**
`C_config` (the configured parameter), `C_staffed` (`c / S`, the capacity the
resulting worker count implies under the intended service time), and
`C_model` (`c / (S + δ)`, the error model's prediction — a modelled quantity,
never called "actual"), and `C_measured` (the observed saturation plateau). The paper never calls the
<!-- withdrawn-quote-ok: the prohibition itself, quoting the term it forbids -->
configured parameter "true capacity" — the harness's own admin field is named
`trueCapacity` and returns `C_config`, which §3 records as a residue of the
assumption the paper falsifies. All algebra is written in terms of the worker
count `c` and `C_staffed`, so the `ceil` in `c = ceil(C_config · S)` never
enters a derivation.

**Never claim the error model is not post-hoc.** It was found because of the
discrepancy; asserting otherwise is an unnecessary philosophical claim a
reviewer can win. §3 checks it against the plateaus; §5 carries the real
defence — a prediction registered before the runs that tested it, using
constants from a separate instrument.

**Controller language — a prohibition, not a scope note.** No
controller-performance verb appears anywhere in the paper, including the
abstract. **Updated after A7 — the previously permitted sentence is no longer
permitted.** Permitted: *timeout rate gave no advance warning in either
corrected cell; a queue-depth lead over live latency was observed in the
original corpus but remains exploratory, because the independent corrected
corpus samples too coarsely to adjudicate an effect of that size.* Forbidden:
any form of *latency-feedback controllers are unsafe / queue-depth feedback
performs better*, and any controller recommendation derived from the
queue-depth ordering. The ordering is exploratory; nothing normative follows
from it in this paper.

---

## Drafting constraints (submission checklist folded in)

| Constraint | Consequence while drafting |
|---|---|
| **Single-anonymised review** | Author names stay in. No anonymisation pass. Cite the repo, the pre-registration commit and the Zenodo DOI openly. |
| **Biographies required for every author** | Draft Jay's ~100-word bio in W4 alongside §1; Paper 1's can be reused with the WebRTC sentence swapped. |
| **Abstract 150–250 words, no citations, no undefined acronyms** | Skeleton: problem → headline claim (resolution-aware wording above) → scale mismatch → consequence for control → artifact availability. |
| **Index terms, IEEE taxonomy, alphabetical** | *admission control, capacity planning, measurement, message queueing, performance evaluation, reproducibility, service level agreements.* |
| **Figures readable at one column (3.5 in)** | Satisfied — six vector PDFs at exact column widths, 8 pt, fonts embedded. Do not regenerate at other sizes. |
| **Every number traces to a *generated* artefact** | Not merely a committed one — hand-written numbers are committed too. **The old justification for this rule — "one error in 70 hand-written values and zero in 241 generated ones" — is DELETED in v8.5: it has no source.** `results/REVIEWER-RESPONSE-W2.md` counts 401 over-precise occurrences, 241 generated and 160 hand-written, which is a count of over-precision rather than of errors. What does support the rule: the sweep shows over-precision concentrated where values are written by hand, and both documentation failures recorded in §IX-C were caught by generating a source-asserted table rather than by reading prose. Cite the artefact filename in a source comment at point of use; strip in W6. The twelve data artefacts regenerate byte-identically; the six figures did not until embedded wall-clock PDF metadata was suppressed, which is now fixed and verified. Check the claim against every artefact class before restating it. |
| **Reproducibility statement** | One paragraph closing §4: repo commit, pre-registration `371e477`, Zenodo DOI, regression fixture. **DONE: DOI `10.5281/zenodo.22761131` reserved 2026-09-14 on an empty draft (deposition 22761131), zero files uploaded, cited in §4 draft 15. The deposit itself is uploaded and published in W6 from the frozen commit.** The deposited package must match the commit §4 cites — a package staged before drafting goes stale, and staging at `4975422` would have deposited pre-precision-fix reports under a permanent DOI. |

---

## Structure

Ordering revised after external review. The chronological version — three
sections of wrong results before the correction — invited the response *"the
manuscript devotes disproportionate space to artefacts of an invalid
experimental model."* The corrected result is now the primary scientific
record; the false findings become evidence for the methodological claim.

| § | Title | Words | Figures |
|---|---|---|---|
| 1 | Introduction | 1,600 | — |
| 2 | Background and related work | 1,400 | — |
| 3 | The harness, the capacity model, and its error model | 1,700 | F1, F2 |
| 4 | Method | 4,750 | T1 |
| 5 | The calibration defect | 2,750 | F3, F4 |
| 6 | The corrected boundary | 1,550 | F5, T2 |
| 7 | What warns, and what does not | 1,350 | F6 |
| 8 | How calibration changed the interpretation | 1,070 | T3 |
| 9 | Threats to validity | 1,650 | — |
| 10 | Conclusion | 460 | — |

**Baseline 18,308 prose words, measured 2026-09-20 under
`scripts/section_wordcount.py` and re-budgeted from it at v9.6.** These are not
targets to write toward — they record what the frozen sections contain. The
readability pass may lower them; nothing should raise them without a reason
named in a section's header.

## §1 Introduction — 1,600 words

<!-- plan-synced-to: section1 draft 18 -->

Four moves:

1. The operational problem, concrete and in two paragraphs — a broker with a
   durable backlog, a downstream with an SLO, a drain that competes with live
   traffic.
2. **The result up front**, in the claim-register wording. Then the contrast:
   the margin is under 1%; configured capacity was wrong by 9.26%. *The error
   is an order of magnitude larger than the quantity being measured.*
3. The scale-mismatch paragraph (claim register). This is the novelty
   statement and it must appear on page 1, because the paper's live rejection
   risk is *"this is a `time.Sleep` bug presented as a paper."*
4. C1–C4 as four one-sentence bullets, each naming its evidence.

**Both identities, deliberately.** C1 — the boundary at measured capacity
across seven cells, with no resolvable movement over the **well-posed** sweep —
tenfold in the 5 ms arm, fivefold in the 25 ms arm — is a
result an operator
can use, and exists independently of the trap. C2 is why that result cannot be
obtained from a configuration file. The paper is not a measurement-validity
case study with a campaign attached; it is a boundary measurement plus the
reason the measurement is hard. Framing it as only the former invites *"why is
there a seven-cell campaign in a methods paper."*

---

## §2 Background and related work — 1,400 words

<!-- plan-synced-to: section2 draft 7 -->

<!-- citation-inventory:start -->
**VERIFIED ANCHORS, from the 2026-09-20 search. Cite these; do not add a work
to this section without checking it the same way.**
- Thread 4 (the paper's home): Mytkowicz, Diwan, Hauswirth, Sweeney, *Producing
  wrong data without doing anything obviously wrong!*, ASPLOS 2009,
  `10.1145/1508244.1508275` — measurement bias large enough to invert a
  conclusion. Ousterhout, *Always measure one level deeper*, CACM 2018,
  `10.1145/3213770`. Heiser, *Systems benchmarking crimes* — **a maintained web
  catalogue, not a peer-reviewed paper; do not give it a venue and year.**
  Papadopoulos et al., *Methodological principles for reproducible performance
  evaluation in cloud computing*, IEEE Trans. Softw. Eng., vol. 47, no. 8,
  pp. 1528-1543, Aug. 2021, `10.1109/TSE.2019.2927908` — **added v9.8**;
  methodological/reproducibility support for §II-D. **The citation attaches to
  the existing measurement-validity paragraph; it requires no new prose**, which
  is the only kind of addition a frozen section permits.
  **§II-D must not say the bias "was not in the measurement apparatus"** — frozen
  §IX-A calls the synthetic downstream an instrument built for the experiment,
  so that phrasing contradicts it. The distinction is **external measurement
  (the independent timing probe, which **exposed rather than generated** the
  bias) versus the internally assumed capacity model, which every quantity
  normalised by configured capacity inherited**. **Do not write that the probe
  was sound** — v8.9 of this plan did, §2 draft 2 followed it into the
  manuscript, and frozen §IX-B contradicts both: the probe's effective clock
  resolution was never measured and its repeatability was not measured at the
  two conditions compared. Where the false finding originated is a separate
  question from what the diagnostic instrument can establish about itself.
- Thread 2: Zhou et al., *Overload control for scaling WeChat microservices*,
  SoCC 2018, `10.1145/3267809.3267823` (DAGOR; arXiv 1806.04075) — **queueing
  delay**. Cho, Saeed, Fried, Park, Alizadeh, Belay, *Overload Control for
  µs-scale RPCs with Breakwater*, OSDI 2020, pp. 299-314 — **queueing delay**;
  verified at v8.9. *Bouncer: Admission Control with Response Time Objectives
  for Low-latency Online Data Systems*, SIGMOD Companion 2024,
  `10.1145/3626246.3653384` (arXiv 2312.15123) — **response-time percentiles**,
  and the reason §II-B does not rest a response-time claim on queueing-delay
  systems alone.
  <!-- withdrawn-quote-ok: prohibition -->
  **Say "an established construction", never "the conventional construction" or "the default answer".**
  <!-- withdrawn-quote-ok: prohibition -->
- Thread 3: Rzadca et al., *Autopilot: workload autoscaling at Google*, EuroSys
  2020, `10.1145/3342195.3387524` — cite for **slack in manually set CPU/memory
  limits**, not for "engineer-supplied limits are routinely wrong" and not for
  service capacity. Barroso, Marty, Patterson, Ranganathan, *Attack of the
  killer microseconds*, CACM 2017, `10.1145/3015146` — **the overhead-versus-
  service-time mechanism**; this is the anchor, not The Tail at Scale. Dean and
  Barroso, *The tail at scale*, CACM 2013 — **high-utilisation tail context
  only**.
- Thread 1: **no peer-reviewed anchor found.** AWS Builders' Library on queue
  backlogs (Yanacek), and **two** GitLab Sidekiq queueing-SLO incident records —
  issue 20797 (30 Oct 2025) and issue 21046 (6 Jan 2026) — cited as evidence the
  problem recurs operationally and **never as technical authority**. Do not
  upgrade either into a research citation.
  **TWO must stay two.** One incident establishes occurrence; recurrence needs
  more than one, and §II-A uses the word "recurring". Dropping either record
  falsifies that sentence.
  **Scope the claim to what the records show.** Both are from one
  organisation's Sidekiq environment, so the permitted form is recurrence "in
  production message processing" — **not** "in production message-processing
  **systems**", which generalises across distinct systems the records do not
  cover. Corrected at §2 draft 5.
- **Cited outside §II — the inventory covers the whole manuscript, not just
  §II's threads.** J. D. C. Little, *A proof for the queuing formula: L = λW*,
  Operations Research, vol. 9, no. 3, pp. 383-387, 1961,
  `10.1287/opre.9.3.383` — **§III** uses Little's law for the staffing relation
  and **§X** repeats it; §II never cites it. It is the only reference in the
  bibliography that does not flow through §II, which is why the citation check
  scopes it to this inventory alone.
<!-- citation-inventory:end -->

**§II-B's last paragraph discharges C3's debt** — it establishes **live latency
as a literature-grounded comparator** for §VII, so §VII's result reads as a
finding about a signal the literature already uses rather than a strawman. Do
not cut it, and <!-- withdrawn-quote-ok: prohibition -->
**do not restore "the conventional construction" or "the default
answer"**: DAGOR and Breakwater key on queueing delay, Bouncer on response-time
percentiles, and none of them establishes an industry default. §VII examines
live latency **alongside** timeout rate and queue depth, which are this
experiment's signals and not the literature's.

Four threads: recovery and backlog staging in durable log systems; overload
and SLO-aware admission control; capacity estimation and self-tuning (the
thread the conclusion joins); and **measurement validity in systems
experiments** — timer resolution, sleep overshoot, calibration of synthetic
workloads. The fourth is the paper's home.

**The disclaimer paragraph, blunt and early:**

> This is not a queueing-theory contribution. We claim no new model, no new
> bound, no result about M/M/c. That a saturating server degrades sharply near
> ρ=1 is textbook. The contribution is that the ρ a system computes for itself
> can be wrong by far more than the operating margin being characterised here,
> and
> that we demonstrate this by falling into it under pre-registration.

Then the scale-mismatch claim, which is what the disclaimer clears room for.
The disclaimer alone answers the Erlang-C objection but not the
instrumentation-bug objection; the scale-mismatch claim answers both.

---

## §3 The harness, the capacity model, and its error model — 1,700 words, F1 + F2

<!-- plan-synced-to: section3 draft 12 -->

- **Architecture — get the live path right; this contradicted §4 for six review
  rounds.** Producer publishes to JetStream throughout, including after
  restoration; the consumer is a durable pull consumer. **Live traffic is
  injector-direct HTTP and never enters NATS.** Brokered messages published
  before restoration are the recovery backlog; post-restoration brokered messages
  are a *separate population*, recorded but excluded from the SLO. **The live
  injector is independently paced; recovery-class broker messages are rate-limited
  at a fixed `r_l` per run, varied between runs by the boundary search. Neither
  path uses within-run feedback control — write "open-loop rate-limited", never
  "rate-controlled", which a reviewer can read as including open-loop fixed-rate
  control.** The two paths compete only at the shared capacity-controlled
  downstream. **(F1 already labels it this way — "live path:
  direct HTTP, never enters NATS" — so the figure is authority, not the prose.)**
- The capacity model: `concurrency = ceil(C × S)` by Little's law;
  `queueCap = 50 × concurrency`, hence cap-in-ms = `50·S`, independent of C.
  State this correctly — an earlier reading was wrong and the code is the
  authority.
- Service-time emulation, and **(F2)** marking where the per-request overhead
  enters. Mark the place; do not yet give the number.
- **The error model, stated algebraically:**

  ```
  c           = ceil(C_config · S)
  C_staffed   = c / S
  S_actual    = S + δ
  C_model     = c / (S + δ)
  overstatement = C_staffed / C_model = 1 + δ / S
  ```

  All algebra runs through the worker count `c`, so the `ceil` never enters a
  derivation; where `C_config · S` is integral, `C_staffed = C_config` exactly.

  which yields 9.26% at S=5 ms and 1.85% at S=25 ms. The entire service-time
  dependence is one line of algebra, not an empirical curiosity.
- **An in-sample common-parameter check — NOT validation, and do not call it
  that.** With the **pooled** `δ` = 0.463 ms applied unchanged to all seven
  cells, `conc/(S+δ)` reproduces every measured plateau to within 0.19% (worst
  0.186%), with no cell failing. The constant came from those same seven
  plateaus, so this tests whether one number suffices across the set, not whether
  the model holds outside it. Say only that the pooled-model residual is smaller
  than one bisection step in every cell — never that the model predicts capacity
  more precisely than the experiment can locate the boundary. **Never write a bare "reproduces every plateau":** a
  per-cell `δ` substituted back into its own cell is algebraic reconstruction,
  and §V now says so explicitly. The leave-one-out form belongs to §V.
- What the downstream is not: no real dependency, no state, no I/O.

---

## §4 Method — 4,750 words, T1

<!-- plan-synced-to: section4 draft 24 -->

- **Pre-registration**, commit `371e477`: the mechanical boundary estimator,
  SAFE / UNSAFE / MARGINAL classification, 5 rps bisection, interval
  reporting `[last SAFE, first NON-SAFE]`.
- **Resolution, stated here and not left for a reviewer to derive.** 5 rps at
  C≈2000 is ~0.25% of capacity; per-cell resolution varies and is tabulated
  in §6. Replicate spread is at most 24% of one step **across the five cells that
  carry a replicated last-SAFE endpoint — not the whole corpus, and no claim is
  made about non-SAFE endpoints or the two unreplicated cells** — so the step
  dominates uncertainty there. Declaring this in §4 is what licenses the resolution-matched
  precision discipline throughout, and the policy that registrations are
  reproduced verbatim at whatever precision they were registered.
- **T1 — amendments, the registered re-analysis and the registered
  replication.** A1 `e5bf303`, A2 `1fe9de3`, A3 `699e105`+`25583c7`,
  A4 `d5ea89d`+`ddd428d`, A5 `fe36734`, A6 `c3aee75`, A7 `939902d`,
  A8 `590d1cc`, A9 `9caf476`, A10 `51026cc`. **Ten rows, three kinds:**
  amendments, one registered re-analysis, one registered replication, and two
  record corrections whose temporal columns read **N/A** — they govern neither
  data nor analysis and must not be forced into Yes/No. Columns: change, date, commit, and **two separate temporal
  columns** — predates governed *data*, predates governed *analysis*. Different
  claims; only the first is prospective registration. A7 is a registered
  re-analysis of already-collected data, never described as prospective or as
  confirmatory; A4's partial status gets its own sentence; **A8 is a registered
  replication and is neither of the other two** — it changes no rule and
  re-analyses nothing, it registers a new measurement before that measurement is
  taken, so it is prospective in the strict sense and is described that way.
  Adding it reopened frozen §4 (draft 13), which is the intended use of the
  freeze rule: new §V evidence made the frozen text factually incomplete.
- **vSLO** defined exactly: fraction of violating seconds, live p99 ≤ 250 ms
  *and* error ≤ 1%.
- **Provenance guard:** the runner refuses to start without a resolvable HEAD,
  after 137 of 140 early records wrote `"unknown"`.
- **Achieved-rate accounting:** nominal versus achieved ρ; the tick-dropping
  injector replaced with lanes after under-delivering 96.4–96.8% on EC2.
- Reproducibility statement closes the section.

---

## §5 The calibration defect — 2,750 words, F3 + F4

<!-- plan-synced-to: section5 draft 23 -->

**Open with motivation, ~250 words.** Three candidate explanations appeared in
sequence; each was pre-registered and each had a falsification test designed
against it. **Two of them survived** — that the boundary depended on concurrency,
and that it depended on service time. The third, that it depended on the
admission limit, was rejected by its own criterion. Having failed to kill the two
that survived, we turned the instrument on itself. **Do not write "each
survived"**: §VIII carries three different outcomes and §V must not promise three
matching ones. Forward-reference §8 for the detail. This paragraph is load-bearing:
present calibration cold and it reads as routine good practice, which
deflates C2 into "we did our homework."

**5.1 Direct measurement.** Per-request excess at both service times. **F3:**
the constant-versus-proportional test — difference −0.005 ms against 0
predicted by constant, ratio 0.99 against 5.0 predicted by proportional.
Attribution: 99.8% to Go `time.Sleep` overshoot. Pre-registered attribution
criteria cited (`results/E2-PLAN.md`, `671e2be`, `4c65bca`).

**Then the honest complication, in its own short subsection.** δ is
approximately service-time-independent — constant to within 4% — but varies with
offered load: four measurements of the same
cost by two instruments span 0.463 to 0.517 ms. The 0.463 ms figure is the
median of seven per-cell plateau estimates in E2d — and it is the lowest of
the four. Say so. The consequence is the claim-register rule: no unqualified
"the overhead," and the control conclusion follows directly, because a
load-varying cost cannot be represented reliably by one fixed correction across
load conditions — and that the paper requires an empirically validated capacity
estimate without deciding between offline calibration and online inference.

**5.2 Predict and eliminate — and the two constants are the whole argument.**

The correction applied to the sleep was the **pooled saturation-plateau-inferred
`δ` = 0.463 ms**; never write it as a bare 0.463. The *prediction* used
different constants: the experiment-1 probe values 0.4947 and 0.4914 ms,
measured by a different instrument on separate uncorrected runs. Show the
arithmetic in the text, two lines:

```
S=5:   conc = ceil(2000 × 0.004537) = 10
       4.537 + 0.4947 = 5.0317 ms    →  10 / 0.0050317  = 1987.4 rps
S=25:  conc = ceil(2000 × 0.024537) = 50
       24.537 + 0.4914 = 25.0284 ms  →  50 / 0.0250284  = 1997.7 rps
```

Measured, in the original single windows: 1987.4 and 1998.1. **These are
historical observations, not the paper's evidence.** A8 replicated both at ten
60-s windows per arm; the replicated medians are 1988.96 and 1997.70 and those
are what the candidate table adjudicates against. Registered in addendum 1 at
17:31:47 UTC;
reproduces to four decimals (1987.3999, 1997.7306), so not a rounding
coincidence. Concurrency is computed from the **corrected** service time,
which is what the downstream actually ran (records confirm 10 and 50 workers
at 4537 and 24537 µs).

**One sentence that closes a confound.** `ceil` absorbs the 9.26% reduction
without changing staffing: the corrected and uncorrected arms ran identical
worker counts and identical queue caps. The correction perturbs timing and
nothing else. A reviewer hunting for a confound in the corrected runs looks at
staffing first.

**The paragraph that answers the circularity objection.** A self-fulfilling
correction predicts exactly 2000.0 in both arms — that is the objection
rendered in arithmetic. Instead the registered prediction was that the
correction would *under-shoot*, by a computable amount, in a direction and
magnitude set by constants the corrected runs never used. It predicted two
different non-trivial values, and the short arm's satisfied its preregistered
A8 criterion on replication — not "confirmed", which reads as a statistical test
A8 never was. **Do not write "hit both".** The long arm's agreement is real and
selects nothing, because its observed spread (2.83 rps) exceeds the separation
between the candidates (1.60 rps). The registration commit predates the first
corrected run by 39 minutes — 17:31:47 UTC against a committed `startedAt` of
18:10:27; give both timestamps, and quote the committed bound rather than the
campaign log's tighter 18:07:30, which is not a committed artefact.

**A8 registered a different reading for each arm, and §5 must transcribe both.**
Short arm: containment — registered value inside the observed spread, rival
outside. Long arm: spread-versus-separation — the spread will exceed the 1.60 rps
between the candidates. Applied uniformly, the containment reading credits BOTH
arms (the long arm's rival falls outside its range too, by 0.39 rps against a
spread of 2.83), so presenting containment as "the" rule contradicts the
long-arm conclusion. Each arm is judged by its own registered reading. **Do not
add that the short arm also clears the long arm's criterion** — that rule was not
registered for the short arm, and citing it there is a post-hoc cross-check the
manuscript deliberately dropped.

**The pooled `δ` needs its rationale, stated as a consequence and not as
foresight.** One value was applied to both arms because on 2026-09-13 the seven
estimates were believed to be one population; the arms were found not to overlap
on 2026-09-14, after the corrected runs. A per-arm fit would have used the
service-time separation to remove the very between-arm effect under test, so the
common correction is the stricter one and the residual 4% survives as a result —
but that is a property discovered afterwards, not the reason for the choice, and
§5 must not claim the foresight.

Concede what must be conceded: 0.463 was estimated in-sample, with no cell
held out. **Any claim that `c/(S+δ)` "reproduces" the seven plateaus must name
the leave-one-out construction**, because each per-cell `δ` is recovered from
its own plateau by `δ = S(C_config/plateau − 1)` and substituting it back is
algebraic reconstruction, not a test. Report the leave-one-out result
alongside. **Every held-out
prediction lands within one bisection step** — worst case E2 c10@Q2500 at
−4.91 rps, 0.98 steps, −0.268%; RMS 2.44 rps. Report the sign pattern too
(S=5 over-predicted, three of four S=25 cells under-predicted), since it is
the same 4% residual named in the claim register and hiding it would be worse
than owning it.

**Plateau versus in-situ**, one short paragraph: the saturation plateau is
authoritative; in-situ probing diverged 0.3% in the short-S arm. It is the
cross-check that later caught A6.

**Do not** claim the c10 break "within 0.0004" confirmed the saturated
overhead. The 215 rps bracket contained both candidates. That over-claim was
caught in review and must not reappear.

---

## §6 The corrected boundary — 1,550 words, F5 + T2

<!-- plan-synced-to: section6 draft 9 -->

**Name the quantity the first time a per-cell ρ_eff appears**, before the
figure: it is the achieved utilisation of the last SAFE point against measured
capacity — `ρ_eff,safe` as defined in §IV — not a fitted transition point, a
bracket midpoint, or anything derived from a non-SAFE run. **No range spanning
the cells is quoted anywhere in the manuscript**; per-cell values at per-cell
resolution live in Table 2. And `C_measured` is a normalisation reference, not a
ceiling. **THE NAMED AGGREGATOR IS THE MAXIMUM**, per frozen §IV: the per-cell
scalar is the maximum achieved ρ across **all** of the last SAFE point's
repetitions — three where the search visited once, twelve or fifteen at the five
replicated endpoints, per §IV draft 22 —
and §IV names Fig. 5 as the place it is required. Under it **two cells read
1.0002**. A separate route — dividing by each cell's *lowest observed* plateau —
gives 1.0008 and belongs to §IV's denominator discussion, not here. A median
numerator would give 0.9999, and **the paper does not use it**; v6.0 of this
outline wrongly said it did. §IV also records that the choice is immaterial after
resolution-matched rounding, the largest within-point spread being 0.0010. So no
`[ρ_safe, 1]` interval is constructed and no cell is called degenerate or pinned
at saturation — **and since §6 draft 8 that guard is a CLAUSE of the sentence
reporting 1.0002, not a standalone sentence.** It belongs there because that is
where a reader meeting a value above unity would invent the interval. **Do not
restore it as its own sentence**: the W3 pass compressed it deliberately, and
§IV states the rule in full. §I is frozen and calls it "the safe drain
boundary"; §VI is where that phrase is cashed out, and §I stays frozen only if
§VI does this cleanly.

**F5 in the claim-register wording:** resolvable before, below resolution
after. Give both spreads — **0.0719 → 0.0071**, committed at `e04cbc9` under the
MAXIMUM on both axes, which frozen §IV names for exactly this figure. Two
superseded pairs must never be reinstated: the published 0.0719/0.0068 mixed a
MAX left axis with a MEDIAN right one, and the `3c00a6e` rebuild "fixed" the
wrong half by moving both to MEDIAN (0.0716/0.0068). **Quote no collapse
factor** — a ratio of two resolution-limited quantities carries its own
uncertainty question; the reportable claim is detectability. Then give E2b's
resolution of 0.0127, which exceeds the residual. The caption states that the
values are post-A6 and how they differ from the pre-A6 figures.

**F5 AND §V-F ARE NOT THE SAME EFFECT, AND §6 MUST NOT LET THEM READ AS ONE.**
This is the trap in this section. F5 takes the range across seven cells and
re-divides *the same boundaries* by `C_measured`, on the A4 estimator: an
accounting change. §V-F takes the gap between two arms at C0 on the drain-window
estimator and compares an uncorrected harness against a *physically corrected*
one: a different experiment. Taking F5's two C0 cells alone makes the collision
explicit — their gap against `C_config` is 0.0696, exactly W8's A4-route
"before", and against `C_measured` it is **0.0019**, while W8's "after" from
actually correcting the harness is 0.0043 (A4) or 0.0032 (drain-window).
**Renormalising closes the inter-arm gap further than correcting the harness
does.** That is awkward and it is real. §6 states it rather than leaving a
reviewer to find it, and never presents the two numbers as the same quantity
measured twice.

**The boundary result**, at resolution-matched precision, across two service times,
three capacities, two queue caps, **four** concurrency levels (7, 10, 35, 50 —
verified from the cell map; earlier text said three). 17 of 21 cell
pairs are indistinguishable at their own resolution; the two cells defining
the quoted residual are the *least* distinguishable of all; the highest
max-based cells, at 1.0002, are not distinguishable from unity at their own
resolution. **Do not write 0.9999** — that is the superseded median route.

**Table 2 — resolution table** (artefact `figures/T2-resolution.md`, generator `scripts/make_table2.py`; renamed from `T3-resolution.md` at `f44d2f1`), per cell: C_config, C_measured, bisection step in
rps, step as a fraction of C_measured, reported interval, interval width, n,
replicate spread, **the cell's ρ_eff at that cell's own precision**, and
**`C_measured`'s own range** (6–15 saturation measurements per cell, median).
State in the caption that the quoted resolution is the search step alone and
that the denominator term is reported separately — **not combined in
quadrature**, since a deterministic grid width and an observed range are not
variances — and that read conservatively they add linearly to 1.09×-1.80×.
Table 2 replaces the withdrawn headline range; it is where per-cell values live. Column headings use the rigid terminology — no `C_true`. This table is what makes the resolution-matched precision
discipline auditable rather than asserted.

**SLO-threshold sensitivity** — no resolvable movement — as a table with a Δ
column and one sentence, no figure.

**SCOPE LIMIT, and §6 states it rather than letting the table imply otherwise.**
The sweep covers 50, 100, 250 and 500 ms — tenfold. But a rule fixed *before the
sweep ran* admits a (cell, threshold) pair only where the healthy baseline live
p99 is at most half the threshold, below which the SLO is a question about idle
latency rather than recovery headroom. **Four pairs are excluded, all of them the
S = 25 ms cells at 50 ms**, whose 34 ms baseline is 68% of that threshold. The
S = 5 ms cells have a 7 ms baseline and are well-posed everywhere.

So the evidence spans tenfold in the short arm and **fivefold (100-500 ms) in the
long one**. Write it that way. Source: `results/E2C-REPORT.md` lines 56 and 70,
and `results/E2C-slo-sweep.json`, whose `wellPosed` flag carries the rule.

The framing: the residual disagreement between seven configurations and the
movement produced by changing the SLO threshold are **comparable in magnitude**
— 0.0071 against 0.0055. **Quote no ratio between them**: both are
resolution-limited, so a ratio carries its own uncertainty question. The four
pairwise excesses are **19% to 24%** of one step, not the superseded 11-17%.

**The residual, declared and not claimed.** Four of 21 pairwise differences
exceed the search-step-only threshold, by **19% to 24%** of one step, and all
four are capacity-regime comparisons with C1 cells consistently lower — a
consistent direction. **None remains resolved** under the conservative reading
that also includes the separately measured denominator variability. The residual
itself is **0.0071**, smaller than E2b's own bisection step of 0.0127. **Do not
argue from rounding** — that a value disappears at reported precision is a
reporting convention, not an inferential criterion, and §6 draft 3 dropped it.
State the
direction, state the magnitude, state that it is below the threshold this
experiment can resolve, and decline to claim it. Declaring something a reader
cannot see in the tables is what makes the rest of the tables trustworthy. §9 names
the experiment that would settle it. **This is deliberate.** An effect at the
edge of resolution, with a direction and a plausible story, is exactly the kind
of claim this campaign has twice had to withdraw after further measurement;
declared here, a reviewer meets it as a stated limit rather than discovering it.
**Do not restate the old "same shape as the three findings that already died"
line** — it came from the retired symmetric-trio story, and §IX's three
retractions are a different set with a different cause.

---

## §7 What warns, and what does not — 1,350 words, F6

<!-- plan-synced-to: section7 draft 7 -->

**F6** on a corrected cell. The DEEP threshold
(`drainQueueDepthMean ≥ 50`, `results/E1B-PLAN.md`, `09e41e5`, fixed before
the runs) evidences that the criterion was not chosen after seeing the data.

Three findings with three statuses, and the section must keep them apart.

**Confirmed:** timeout rate never crosses its criterion before the last safe
point — σ identically 0.00 in both corrected cells, replicated under addendum A7
on a corpus collected 34 h after the statistic froze.

**Exploratory:** the queue-depth lead over live p99 (+10 to +25 rps in three E1
cells). A5 chose its statistic with that corpus in view, and the corrected
corpus samples at 60–100 rps — too coarse to resolve a 10–25 rps lead in either
direction. State both reasons — the first prevents a confirmatory reading of the
E1 result, the second prevents the corrected corpus from adjudicating it. They do
different work; do not write "neither alone is sufficient".

**Observed — and the two cells differ, which IS the result.** **Never write "no
observable leads"**: it collapses two claims, and one of them is false. In
corrected c50 all five metrics first cross at the last safe point, so there is no
warning room. In corrected c10 mean queue depth, live p99, live p90 and mean
in-flight all cross at `rl` 1075 with the last safe point at 1185 still ahead —
**four metrics give one probe point of warning room**, roughly 110 rps. Only p50
crosses with no room; only timeout never crosses. What is absent in c10 is the
ordering, not the warning. State it as: the corrected corpus does not reproduce
the queue-before-latency ordering at its available resolution, and does not show
that no metric gives advance warning.

Two quantities must be kept apart: the registered DEEP threshold concerns **mean**
queue depth, which peaks at 23.1 against 50 inside c10's safe range, while F6
plots queue **peak**, which reaches 111. Say which is which, or a reader seeing
peak > 50 will think the DEEP statement is contradicted. DEEP is also a separate
preregistered marker, not a second condition a 3σ queue warning must satisfy.

**The hypothesis is about resolution of ordering, not absence of room** — the old
"a boundary at capacity leaves little room for a precursor" version is
contradicted by c10's own warning room. Write: the corpus samples too coarsely
near the boundary (60 and 100 rps against E1 margins of 10-25) to distinguish the
relative onset of the two signals even where both warn; a lead of E1's size would
vanish below that spacing; whether the original separation was related to the
calibration error remains untested. Named experiment (a 5 rps sweep over the top
50 rps of each corrected safe range, ~60 runs at n = 3), **not** a result. §VIII
may reference it; it is not a fourth retracted finding on this evidence.

F6's *pipeline* is unaffected either way: `make_figures.py` uses no noise
statistic anywhere, so the figure never depended on the quantity A5 chose or A7
re-examined. Say so — a figure that survives a downgrade because it never rested
on the downgraded thing is worth a sentence. **But F6's SURROUNDING TEXT is not
unaffected, in four places, and the same wrong claim propagated through all
four** because each was written from the previous one rather than from the data:
(1) the caption's lead, (2) the caption's "neither moves appreciably while the
system is safe" and "no advance warning", (3) the title drawn INSIDE the PDF at
`make_figures.py:383` — "both signals are flat until the last safe point, then
cliff" — and (4) a passage in `A7-REPORT.md` asserting that the figure and the A7
result agree, contradicted by A7's own table twenty lines above it. The cell
shows queue peak rising 7 → 111 and p99 8 → 58 ms inside the safe range, with
four metrics warning one probe point early. (1) and (2) are corrected at
`9583797`; (3) and (4) are pending. **§VII must never claim that F6's title
describes the corrected corpus's behaviour, or that the figure and A7 agree** —
an earlier version of this plan said to say so, and it was wrong.

§II establishes **live latency as a literature-grounded comparator**, not as
<!-- withdrawn-quote-ok: prohibition -->
"the conventional construction" — that stronger form was removed at v9.0 and
must not return. The section does not assert that latency "warns last".

---

## §8 How calibration changed the interpretation — 1,070 words, T3

<!-- plan-synced-to: section8 draft 4 -->

> ## BLOCKER RESOLVED 2026-09-20 — ruling below; §8 may be drafted once §1, §5,
> ## the claim register and this plan are all synchronised (they now are).
> ## The original blocker is kept for the record:
>
> ## BLOCKER — DO NOT DRAFT §8 UNTIL THIS IS SETTLED (raised 2026-09-20)
>
> Building Set A's table showed that **§I and §V-A both misdescribe the trio**,
> and §8's premise inherits the error.
>
> §I: "three successive findings — that the boundary depended on concurrency,
> then that it depended on the admission limit, then that it depended on service
> time … **Each survived that test.** All three were artefacts of that same
> omitted per-request timing bias."
> §V-A: "Three effects appeared in sequence … **each surviving that test**."
>
> What the record shows:
> - **Concurrency** — affirmed. E2's registered cap swap returned `f` = +0.000
>   and −0.006 against a CONCURRENCY-DRIVEN criterion of `f` ≤ 0.25. Dissolved by
>   calibration: the inter-arm gap falls 0.0670 → 0.0032 (95%).
> - **Admission limit** — **NOT affirmed. Refuted by its own registered test,
>   before calibration.** The same swap scored CAP-DRIVEN at `f` ≥ 0.75 and was
>   OFF-SCALE. E2's own title is "separating the queue-cap effect from the
>   concurrency effect", and what survived is the *negation*: the cap does not
>   govern the boundary. It did not survive its test, and it is not a calibration
>   artefact.
> - **Service time** — affirmed. E2b returned `h` = 0.980 against a criterion of
>   `h` ≥ 0.75. **But no artefact recomputes `h` post-calibration**, and the
>   corrected corpus has no `C` = 400 cell, so its dissolution is undocumented.
>   Row 1's collapse must not be borrowed for it — different statistic, different
>   cells.
>
> So the record supports **two** affirmed-then-dissolved findings, not three, and
> one of those two has no documented dissolution. If the cap hypothesis was ever
> held as a finding, it was killed by further measurement — which is **Set B's**
> character, not Set A's.
>
> This is a frozen-section claim in two places and the premise of this section.
> **It is for the reviewer, not for drafting around.** Source:
> `figures/calibration-artefact-findings.md` at `37d3849`.

**RETITLE: *How calibration changed the interpretation*.** The old title
promised three symmetric failures and the evidence does not contain them. Three
rows, **three different statuses, and the asymmetry is the point** — a section
that admits it is stronger than one that manufactures a pattern.

1. **Concurrency — the complete case.** Registered cap-swap challenge
   (CONCURRENCY-DRIVEN at `f` ≤ 0.25); returned `f` = +0.000 and −0.006;
   survived. Calibration then removes 94-95% of the inter-arm separation
   (0.0670 → 0.0032 drain-window; 0.0696 → 0.0043 delivery-span; 134.0 → 6.4 rps).
   This is the chain the paper's central lesson rests on.
2. **Service time — affirmed, not re-adjudicated.** Registered test `h` ≥ 0.75;
   returned `h` = 0.980; survived. **Do NOT write "dissolved".** The correct
   status is *affirmed pre-calibration; the later interpretation is superseded,
   but the exact registered statistic was never re-adjudicated* — no artefact
   recomputes `h`, and the corrected corpus has no `C` = 400 cell in which to
   recompute it. **Never borrow the concurrency row's collapse for this row:**
   different statistic, different cells.
3. **Admission limit — the CONTRAST, and it is not a false finding.** Its
   registered criterion (CAP-DRIVEN at `f` ≥ 0.75) **rejected it, before any
   calibration** — OFF-SCALE. It never survived, so it is neither a calibration
   artefact nor a retracted finding. It earns its place by making the
   methodological point sharper: *the same protocol that failed to expose the
   concurrency artefact did reject the admission-limit explanation.* The
   falsification machinery worked on a wrong explanation and could not see a
   hidden bias.
   **RESOLVED 2026-09-20 — it stays here as the contrast.** The executor's
   search was conclusive: no pre-E2 written result asserts that the admission
   limit governs the boundary. The only record is `STATUS.md` at `c823393`
   (lines 95-98), which lists it as a competing explanation *not yet ruled out*.
   A hypothesis with a test attached is not a finding, and it does not move to
   §9.
   **The queue/SLO arithmetic runs the other way from the obvious reading, and
   §8 draft 1 got it backwards.** A full queue is 50·S of delay: 250 ms at
   S = 5 ms, which IS the objective, and 1250 ms at S = 25 ms, five times it. So
   the correct asymmetry is that in the LONG arm the objective is crossed while
   substantial queue capacity remains — the cap is slack at the boundary — while
   in the short arm the two limits very nearly coincide. Do not write that
   "queue full was definitionally objective breached in the short arm but not in
   the long arm": a full queue at 25 ms breaches the objective more strongly,
   not less.

Prose explains **why each looked technically plausible at the time**; it does not
recite numbers the table already carries.

**A NEW TABLE, four columns, and deliberately not "what killed it".** The three
rows do not share an answer to that question, which is the whole point of the
section:

| Candidate explanation | Registered falsification / challenge | Pre-calibration outcome | **Post-calibration evidence and status** |

<!-- withdrawn-quote-ok: prohibition -->
**Column 1 is "Candidate explanation", never "Apparent finding".** The admission
limit was explicitly not a finding, and a column heading that calls it one
reinstates the symmetry this section exists to retire.

The fourth column is deliberately **not** "what the calibration correction
showed" — that phrasing forces a false symmetry and leaves the service-time row
nowhere to say *exact `h` not recomputed*. Rows carry different final statuses.

Rows: the boundary depends on concurrency (gap `D` = 0.0689, `E2-REPORT`); the
boundary depends on the admission limit (the E2 cap swap); the boundary is
governed by service time (E2b, `h` = 0.980). **Their post-calibration statuses
are three different things and the rows must not be levelled:** concurrency
affirmed then removed, service time affirmed and NOT re-adjudicated, admission
limit rejected before calibration ever happened.

**A6 is a separate correction and must be stated ONCE, structurally, and
accurately.** It is easy to conflate with the calibration because the two are
days apart. What A6 did: it established that the A4 utilisation estimator
**over-reads at collapsed points**, and the response was to **stop reporting
utilisation at those points**, not to re-estimate them. What A6 did NOT do: it
changed no candidate explanation's standing. Say it near the §8 opening —
conceptually: *A6 changed the treatment of collapsed points, not the
substantive status of these candidate explanations: concurrency and service time
remained affirmed, the admission limit remained rejected. What changed the
interpretation of the two affirmed results was the later replacement of the
configured capacity parameter by an empirically calibrated capacity reference.*
Then let the table's two right-hand columns carry it and move on. Do not
re-explain it per row, and **do not write that A6 "left all three findings
standing"** — one of the three was never a finding.

**No "when" column** — T1 owns chronology and registration provenance. **No
"final status" column** — the fourth column makes status obvious. The caption
carries the thesis rather than a fifth column, **and the thesis is the
asymmetry**: *Three candidate explanations of the boundary, their registered
falsification tests, and what calibration changed about each. One was rejected
by its own criterion before calibration; of the two that survived, one was
almost entirely removed when the boundary was expressed against measured service
capacity, and the other's registered statistic was never recomputed.* **The old
caption — "three second-order findings that survived their registered
falsification tests before calibration and disappeared" — is invalid and must
not be regenerated.**

Include briefly, without self-flagellation, the two-point "cap fraction
regularity" that did not hold on C1 cells (1.96% and 0.27%) — a pattern that
was never real.

**Close on the generalisation — it stays in §8, and the asymmetry sharpens it
rather than weakening it:** the protocol rejected one wrong explanation cleanly
on a criterion fixed in advance, and could not detect the calibration bias from
the effects that bias produced. Both halves are needed; neither alone is the
section. Then:
a study conducted under a public pre-registration and an explicit falsification
protocol could not detect a sub-millisecond bookkeeping error from its
consequences alone. (Single-author paper: no researcher count, here or
anywhere.) That is the implication paragraph, and it leads into §9.

---

## §9 Threats to validity — 1,650 words

<!-- plan-synced-to: section9 draft 6 -->

**SIX VALIDITY CATEGORIES PLUS A CLOSING FUTURE-WORK SUBSECTION — seven
labelled, A to G. Ruled at the §9 review and settled.** (v8.5 and v8.6 both said
"six subsections", which miscounted the closing one; corrected at v8.7.) Paper
1's construct / measurement / internal / external structure cannot hold two of
this section's items without distorting them: record and provenance corrections
are not measurement threats, and Table 4's retractions are not internal-validity
bullets. A Construct · B Measurement · C Provenance and corrections to the
record · D Claims overturned by independent checks · E Internal · F External ·
G What remains open, and what would settle it.

**BUDGET, raised from 1,100 and why.** Draft 1 came in at 1,607 with every item
owed by a forward reference or by this plan. The review ordered the option-(ii)
trim — Table 4 carries §IX-D, §IX-E's leave-one-out becomes a cross-reference —
which removed 160 words as costed. Two blockers then added ~160 back: §V-G's two
readings are longer than the A9/A10 paragraph they replaced, and the
finer-bisection reasoning is new. Draft 2 is **1,655**. Further compression
passes returned 44 and 32 words, so the length is structural. Do not cut owed
content to reach a round number; if it must come down, the only honest lever is
dropping an owed item and amending the frozen section that promises it.

Every item phrased as a finding. No apologies.

- **Construct.** One synthetic downstream; δ is specific to this
  implementation, host and Go runtime. What generalises is that a configured
  capacity figure was wrong by more than the safe margin — not the number.
- **Provenance of the saturation windows — new, and it constrains how §V may be
  worded.** `scripts/overhead_run/main.go` writes the label, offered rate,
  connection count and measurement, and **no commit, no dirty flag and no
  timestamp**. Both corrected plateau measurements and all twenty A8 windows use
  it. The runner's provenance guard does not cover it. Consequence: the committed
  record cannot establish that addendum 1 predates the plateau measurements — the
  bound is `c96f406` 16:31:55 to `f032f12` 18:50:07 UTC, which contains the
  17:31:47 registration. **Never write that the plateau test is timestamped, or
  that the registration provably predates it.** The supporting evidence is the
  registration's forward-looking language, its statement that no boundary run had
  started, and an uncommitted campaign log at 18:07:30. Addendum A9 records it.
  The fix for any future campaign is to stamp provenance in that tool.
- **Measurement.** The direct timing probe's repeatability is **measured at one
  condition and not at the two being compared.** The 90%-load and saturation
  figures are single 60-second windows; the in-situ figure aggregates 18 and 15
  runs, whose run means span 0.0053 and 0.0040 ms
  (`results/W9-probe-characterisation.json`). The load effect of 0.020-0.022 ms
  is four to five times that span. **State it as an indicative comparison, not as
  a verdict:** the span comes from 111-120-second runs under the bursty arrival
  process, not 60-second windows under the calibration driver, so it does not
  establish that the effect cannot be window scatter — it is the only
  repeatability evidence available, and §5 is worded to match. A repeatability measurement at the
  compared conditions would settle it and was not made. One superseded figure is recorded here
  rather than in §V:
  the corrected plateaus are replicated under addendum A8 (ten windows per arm,
  registered before the replication ran), so the earlier n=1 limitation is
  discharged and must not be restated. Also: an earlier committed analysis
  reported 96.3% of the inter-arm effect removed,
  using unmatched before-and-after estimators; it is superseded by the matched
  94–95% accounting in §V. One sentence, no more — §V should not spend space
  disproving a number the paper no longer claims. Also: the quoted per-cell
  resolution omits denominator
  variability: `C_measured` is a median over 6–15 saturation measurements whose
  range propagates to 0.09–0.80 of a bisection step. **Report the two terms
  separately; never combine them in quadrature.** Read conservatively they add
  linearly, giving 1.09×-1.80× the quoted figure. At the lowest observed plateau
  two cells place the safe-side estimate marginally above 1.0 — which is why the
  paper says "at or near" rather than "strictly below". The resolution floor
  belongs here too, cross-referenced to Table 2.
- **Claims overturned by independent checks — Table 4's set, moved here from §8 in
  v7.0.** Carry the existing three-row table: bimodality in both arms (killed by
  E1B replication at n = 12), occupancy as a fixed 4.1% of the queue cap (killed
  by the first cell that tested it), A4 valid at every probed point (killed by a
  plateau cross-check, then A6). **This table REPLACES the long estimator-history
  prose that used to sit here** — do not write both. Keep A6's support as the
  *count*, 18 of 20 unsafe points reporting rates above their own plateau: a
  count is resolution-independent, while the per-cell inversion magnitudes
  (0.0002 and 0.001 against a resolution of 0.0025) are evidence of nothing and
  must not be cited. Surviving the rounding rule is not the same as exceeding
  resolution.
  **Umbrella thesis: further measurement overturning claims already written
  down.** Do NOT use "an estimator cannot find its own blind spot" as the
  umbrella — it fits the A4 row and only that row. Use it as that row's
  implication, or in the subsection's close.
  §IV keeps only the method fact it needs — A4 is valid at safe points, over-reads
  collapsed ones, the cross-check found it, utilisation is not reported at
  collapsed endpoints — and cross-references here rather than retelling the story.
- **§IX owes §V-G's three, and they are NOT A9 and A10.** §9 draft 1 made
  exactly that substitution and it was caught in review. A9 and A10 are later
  record corrections, already carried by §IV and Table 1. The three §V-G means,
  verified in `results/E2E-PLAN.md`: (1) addendum 2's reading that **the
  bisection could not terminate**, corrected by addendum 3 on the first
  contradicting result, before that point completed — the queue peak had already
  gone 7 → 18 → 111 and live p99 8 → 14 → 58 ms across the three preceding
  probes, and the error was reading two flat points as an asymptote; (2)
  addendum 3's reading that **the saturated figure governed and the 90%-load
  figure was excluded**, corrected by addendum 4 **before the deciding probe
  ran**, with the reading for each outcome fixed in advance, because the 215 rps
  bracket [0.9883, 0.9941] contained both candidates; (3) the withdrawn claim
  that a break within 0.0004 of a registered prediction confirmed the saturated
  figure — a sentence of that same addendum 3. These are **not** Table 4's
  set and must not be folded into it — that table's own header excludes process
  errors, which is what made §V-G's earlier citation of it wrong. Give them their
  own short passage, sourced from the registration.
- **TWO documentation failures now, still one short paragraph.** Record what
  CAUGHT them, not self-criticism. (i) F6: a false reading propagated through
  report prose, caption, the title drawn into the PDF, the outline and an early
  §VII draft, because each layer copied the previous summary rather than the
  data. (ii) The candidate-explanation narrative: a summary generalised one
  evidentiary pattern
  across three findings, and source-asserted table generation showed one
  hypothesis had been refuted before calibration and another lacked a
  like-for-like post-calibration test. **The lesson is the control, not the
  error:** generated, source-checked tables — not intermediate prose — are the
  authority for multi-item claims. Neither is an experimental finding; do not
  enumerate instances theatrically.
- **The superseded one-paragraph version, kept for reference:**
  During close-out an incorrect reading of the corrected-corpus figure propagated
  through report prose, the figure caption, the title drawn inside the PDF, the
  outline and an early §VII draft, because each summary inherited the previous one
  rather than the source data; A7's own table contradicted it throughout. Record
  it as a documentation-provenance failure, **not** as an experimental finding and
  **not** as a fourth retracted result. Do not enumerate the instances
  theatrically. It belongs here and not in §8: the calibration bias produced false
  empirical effects, whereas this was a summary copied forward — different
  mechanisms, and merging them weakens §8.
- **Internal.** The in-sample estimation of δ and what the leave-one-out test
  showed. The
  in-sample estimation of δ and what the leave-one-out test showed. The
  harness defects caught and fixed, as evidence of the checking regime. **Only
  two are sourced and only two may be used**: the spin-wait admission profile
  that amplified a transient rejection into a sustained collapse (`NOTES.md`),
  and the overhead record's descriptive field contradicting its own arithmetic
  in every record it wrote until corrected at the source and in 43 records
  (METHOD-AUDIT item 20). v8.5 deleted three further examples this plan used to
  name — stale trace shadowing, an E2 run-ID collision, and an E1B median
  mis-stated as the sixth of twelve elements — because none has a source in the
  Paper 2 artefacts. Do not restore them without one.
- **External.** One implementation, one instance type, one broker, one cohort.
  No real dependency, no persistent state, no operational consequence
  measured.
- **Close §9 on its own lesson, distinct from §8's.** §8 concludes that a study
  under public pre-registration with an explicit falsification protocol could not
  detect a sub-millisecond calibration bias from its consequences alone. §9
  concludes that independent replication, orthogonal measurement and
  cross-estimator checks are necessary because an analysis chain can validate
  assumptions it shares with the instrument. Complementary, and kept visibly
  separate.
- **TWO named future experiments, and they are not the same study.** §VI and
  §VII each forward-reference one, and each must find its own here.
  (i) **The finer-bisection study** that would resolve the four-pair residual.
  **Its design is NOT specified in any artefact and must not be invented.** §6
  draft 6 therefore withdrew the promise to state what it would cost. What §IX-G
  may say, and no more: a finer search would reduce the **bisection** component
  of the resolution while the denominator variability would remain a **separate
  term**, which any such study must carry explicitly when adjudicating the
  residual. **WITHDRAWN at v8.6 — do not reinstate:** the claim that a finer
  search *alone* could not settle it, and that more saturation measurements
  would therefore be needed. A narrower step lowers the conservative threshold
  while the denominator term stays put, so a difference of about 1.2 steps may
  well become resolvable; the present record does not establish otherwise.
  (ii) **The near-boundary ordering sweep** — 5 rps over the top 50 rps of each
  corrected safe range, ~60 runs at n = 3 — which would resolve whether queue
  depth leads live p99, a question the corrected corpus samples too coarsely to
  answer in either direction (§VII points here). Naming both converts two gaps
  into declared future work and pre-empts the demand. **Do not merge them:** one
  is about where the boundary sits, the other about what warns before it.

- **The probe's own distribution and instrument limits — NEW in v8.4, and
  §IX owes them because a FROZEN section says so.** §V-B closes: *"§IX records
  the right-skew of the per-cycle distribution, the clock-resolution argument and
  the percentile-buffer caveat."* All three, sourced from
  `results/METHOD-AUDIT.md` item 25 and verified against the code and records:
  - **Right-skew.** Every reported δ is an untrimmed arithmetic mean over a
    right-skewed per-cycle distribution — p99 is about twice p50 in every
    condition and the maximum reaches roughly four times it. The mean is the
    correct statistic for a capacity model, which concerns total worker time per
    request rather than a typical one (§V-B says this), but §IX states plainly
    that every quoted δ therefore sits above the typical cycle.
  - **Clock resolution. Use §9 draft 2's wording; the earlier version of this
    bullet was replaced for two reasons and must not come back.** The probe uses
    the Go runtime's monotonic clock, which **represents** timestamps to the
    nanosecond — **representation granularity is not effective resolution, and
    the plan must not imply a 1 ns resolution the paper then disowns**. The
    effective resolution on the experiment host was never measured and is not
    recoverable from the records, so a sub-millisecond measurement is reported
    without a bound on its own quantisation error. **Do not write that
    estimating it from the same instrument would be the error this paper is
    about** — a clock can be characterised independently; this one was not. The
    concession is simply that no retrospective bound is supplied.
  - **Percentile buffer.** Means and sums are accumulated over every request,
    but percentiles come from a fixed 200,000-slot sample buffer
    (`OVERHEAD_SAMPLES`, `downstream/main.go`) that is filled in order and then
    stops accepting. It did **not** bind for the four direct figures, whose
    windows hold 115k-137k cycles. It **did** bind in situ: those records show
    `count = 232,349` against `samples = 200,000`, so every in-situ percentile
    describes the first 200,000 cycles of the run and not the whole of it. The
    in-situ *means* are unaffected. This distinction must be stated, not
    smoothed: one number in that record set is over the window and another is
    over its opening.

---

## §10 Conclusion — 460 words

<!-- plan-synced-to: section10 draft 3 -->

Margin, trap, consequence — one sentence each, in claim-register wording.
Then: the result depends on an **empirically validated capacity reference**
rather than on the configured parameter — **not** "measure capacity rather than
accept it", which mandates offline measurement while C2 deliberately leaves
offline-versus-online open. Timeout rate gave no advance warning, while the
queue-depth-versus-latency ordering remains unresolved on the corrected corpus.
**Offline calibration versus online inference is left to a separate future
study. Do NOT write "controller comparison as declared future work"** — making a
controller experiment the necessary discriminator between two capacity-
estimation strategies does not follow, and drifts toward the controller
recommendation this paper refuses to make. **§IX owns the two named experiments;
§10 adds no third.** The conclusion follows §I's contribution wording exactly —
it does not reintroduce an ordering claim §I has already downgraded. Close on
C4, but on what C4 establishes: **the pre-registered record made those reversals
explicit and auditable** before publication rather than after — **not** that
pre-registration *made the retractions possible*, which claims causation C4 does
not establish, since replication, additional test cells and cross-checks
produced them. That close is what an IEEE Access measurement reviewer is most
likely to value.

---

## Figures and tables

| Item | § | Status |
|---|---|---|
| F1 architecture | 3 | Vector PDF, redrawn after collision fix |
| F2 capacity model / where δ enters | 3 | Vector PDF |
| F3 constant-vs-proportional excess | 5.1 | Vector PDF, stacked total corrected 0.0004 ms |
| F4 predicted vs measured plateau | 5.2 | Vector PDF. **BUILT at `b59f83a` against A8.** Corrected measured plateaus are the median of ten 60-s windows per arm, whiskers drawn hinge-to-hinge so their width is the observed IQR and their position shows where the middle half sat; predictions are drawn as a point on a short rule, never as a bar. The v4.6 instruction to caption them as n = 1 with no error bars is obsolete and must not be reinstated. Caption states n = 10, the median convention, the IQRs numerically (1.71 / 1.29 rps) and that they are window-to-window scatter, not an inferential interval. **Caption must also carry the long-arm non-discrimination** — the annotation reads `+0.0 rps` and the figure alone would assert an exactness §V-D denies. **Y-axis stays at (1700, 2105): not compressed.** The whiskers are 0.42% and 0.32% of the span and read as hairlines; that is the honest scale, and the magnitudes are given in the caption instead. **Measured bars stay at their existing x-offset**, not re-centred after the predicted bars were removed — re-centring would move every placement matrix and destroy the structural PDF diff, which is how the one figure defect of this campaign was caught — METHOD-AUDIT item 20: the figures were never byte-reproducible, a wall-clock `/CreationDate` making every run differ. (The other candidate, the `tight_layout` reflow surfaced at `e04cbc9` when a shortened title moved 36 placement matrices, was explained as benign and is not recorded as a defect; the record supports one, not two or three.) **Both decisions are FINAL (ruled 2026-09-20, v10.2) and are no longer W5 choices: neither is to be reconsidered in cosmetic cleanup.** The y-axis is the honest scale and the caption carries the IQRs; the offsets are kept because the structural PDF diff depends on them, and are overridden only if an actual visual ambiguity is identified, not for tidiness. And must state that bars 1–2 are the seven-cell corpus and bars 3–4 the corrected-harness corpus, on different ρ estimators** — legitimate, since predicted vs measured plateau is direct throughput with no ρ estimator involved, but a reviewer who spots the mixture unaided will assume the worse reading |
| F5 the collapse | 6 | Vector PDF, post-A6 values, **caption rewritten to detectability wording** |
| F6 queue depth vs p99 | 7 | Vector PDF, redrawn after collision fix |
| T1 pre-registration amendments | 4 | **Ten rows at `9caf476`/`51026cc`. NO GENERATED ARTEFACT — T1 lives only in `paper/section4.md`.** |
| Table 4, claims overturned by independent checks | **9** (moved from §8 in v7.0) | **Generated, but the file is called `figures/T1-false-findings.md` by `scripts/make_table1.py`.** |
| Table 3, candidate explanations and what calibration changed | **8** | **BUILT at `c0a4eb2`** as `figures/calibration-artefact-findings.md`, generator `scripts/make_calibration_findings.py`, which asserts every quotation against its source artefact and aborts on a missing fragment. **Regenerate under the v8.2 schema:** column 1 is *Candidate explanation*, and the caption is the asymmetric one above. It is the manuscript's **Table 3** and its rows are candidate explanations. **RENAMED at `f44d2f1`** to `figures/T3-candidate-explanations.md`, generator `scripts/make_table3.py`; the names above are correct at `c0a4eb2` and stay. |

> **MANUSCRIPT TABLE NUMBERS — FIXED IN v7.1, IN CITATION ORDER:**
> **T1** amendments (§4) · **T2** per-cell resolution (§6) · **T3** candidate
> explanations and what calibration changed (§8) · **T4** claims overturned by
> independent checks (§9). §4 draft 23, §5 draft 21 and §6 draft 5 carry the new
> numbers. **The "Set A" / "Set B" labels are retired** and must not be used in
> active mapping — they carry the symmetric story v8.0 removed.
>
> **FILENAMES NOW MATCH (W5, `f44d2f1`).** `figures/T2-resolution.md` is the
> manuscript's **Table 2**, `figures/T3-candidate-explanations.md` **Table 3**, and
> `figures/T4-false-findings.md` **Table 4**, each generated by `make_tableN.py`.
> Commit-pinned references to the old names stay as written; METHOD-AUDIT item 33
> is resolved.

> **ARTEFACT NAME COLLISION — RESOLVED at `f44d2f1`; kept as a record of why the
> rename was needed.** The repository's `T1-false-findings.md` (now
> `T4-false-findings.md`) was the **manuscript's Table 4** (v7.1
> renumbering; it said Table 2 before that and the stale reading survived here
> until v8.2). The
> manuscript's **Table 1** (amendments, the A7 re-analysis, the A8 replication
> and the A9/A10 record corrections) has no generated artefact and is written by
> hand in `paper/section4.md`. Anyone told to "fix T1" has even odds of opening
> the wrong file, and both were edited on 2026-09-19. **DONE:** the artefact was
> renamed at `f44d2f1`, in the W5 pass as planned, and METHOD-AUDIT item 33 was
> rewritten as resolved in the same commit.
| Table 2, per-cell resolution | 6 | Built as `figures/T3-resolution.md`; **renamed at `f44d2f1`** to `figures/T2-resolution.md` (generator `make_table2.py`), matching the manuscript's **Table 2**. |

---

## Schedule

| Week | Deliverable |
|---|---|
| W2 Sept 22–28 | §3, §4, §8 drafted. T1, T2, T3 built. Leave-one-out folded into §5. Precision steps 2–4 applied. **Zenodo: DOI reserved on an empty draft, nothing uploaded.** |
| W3 Sept 29–Oct 5 | §5, §6, §7 drafted. |
| W4 Oct 6–12 | §1, §2, §9, §10. Abstract, index terms, biography. Full draft. |
| W5 Oct 13–19 | Revision. External review against this outline. Artifact package final. **Artefact renames — DONE at `f44d2f1` (pushed); generators `make_table2/3/4.py`, historical reports annotated not rewritten. Original instruction retained below:** **Artefact renames, to the v7.1 manuscript numbering — the v8.1 instruction pointed the false-findings table at Table 2, which v7.1 had already made Table 4. Correct set: `figures/T1-false-findings.md` -> `T4-false-findings.md` and `scripts/make_table1.py` -> `make_table4.py`; `figures/T3-resolution.md` -> `T2-resolution.md`; `figures/calibration-artefact-findings.md` -> `T3-candidate-explanations.md` with its generator. Resolves the collision noted in the deliverables table and in METHOD-AUDIT item 33.** |
| W6 Oct 20–26 | Final pass. **Re-stage the Zenodo package from the frozen commit, upload, verify, publish** — the reserved DOI must resolve before submission. Metadata to complete first: `description`, `related_identifiers` (repo URL, Paper 1's `10.5281/zenodo.22061184`), licence note covering `scripts/`, title naming the paper. **Hard pre-submission checks, each verified against a primary source and not against this outline:** (1) the abstract's "publicly archived" is true — the DOI resolves to a published record; (2) ~~the biography's first degree~~ **CLOSED 2026-09-20: the author confirmed the B.E.; the manuscript already reads B.E. and needs no change. The iCloud CV that says "B.S." is corrected separately so the question cannot reopen.** This row carries the check because the biography's editorial note is stripped before submission. Then submit. |

Note the W2/W3 swap against plan v4: §8 is now short and drafts easily from
Table 3, while §5 and §6 both depend on the leave-one-out result and the
resolution table (Table 2).
