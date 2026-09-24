# Front matter — abstract, index terms, biography

*Draft 1. 2026-09-20. W4 deliverable. Written against outline v9.6, with all ten
sections scientifically frozen, so every claim below is transcribed from a
frozen section rather than composed fresh.*

*CONSTRAINTS. Abstract 150-250 words, no citations, no undefined acronyms — so
"SLO" is spelled out and `rho` never appears. Skeleton per the plan: problem →
headline claim in resolution-aware wording → scale mismatch → consequence for
control → artifact availability. Index terms from the IEEE taxonomy,
alphabetical. No controller-performance verb anywhere, including here. The
configured parameter is never called true capacity. Source comments strip in W6.*

---

## Title and author block

*Chosen by the author 2026-09-20. The author block follows Paper 1's
submission exactly, so the two papers present the same affiliation, contact
and ORCID. Everything between the `article:` delimiters below is article text;
everything outside them, including this note, is drafting apparatus the build
never emits.*

<!-- article:title:start -->
Measuring the Safe Drain Boundary for Durable Backlog Recovery Under a Live Latency Objective
<!-- article:title:end -->

<!-- article:short-title:start -->
Nirmal: Measuring the Safe Drain Boundary for Durable Backlog Recovery
<!-- article:short-title:end -->

<!-- article:author:start -->
Jay Suresh Nirmal
<!-- article:author:end -->

<!-- article:address:start -->
Independent Researcher, Boston, MA, USA (e-mail: jaynirmal15@gmail.com; ORCID: 0009-0003-0886-4663)
<!-- article:address:end -->

<!-- article:corresp:start -->
Corresponding author: Jay Suresh Nirmal (e-mail: jaynirmal15@gmail.com).
<!-- article:corresp:end -->

---

## Abstract

*249 words, against a 150-250 limit — **measured, not asserted**. This header has now been wrong twice: draft 1 claimed 247 without counting (it was 259), and the first fix claimed "inside the limit" at 251. Recount after every edit to this section; it sits at the ceiling and three of the review edits added words.*

<!-- article:abstract:start -->
When a consumer recovers from an outage, its accumulated backlog and the live
traffic it still serves compete for the same downstream capacity. Draining too
fast turns the recovery into a second incident; draining too slowly leaves the
backlog outliving the outage. The operator's question is a rate, usually answered
by a chosen number, adjusted after it goes wrong.

We locate that boundary empirically. Across seven cells spanning two service
times, three configured capacities, two admission limits and four concurrency
levels, the safe drain boundary lay at or near measured service capacity and was
indistinguishable from it at each cell's experimental resolution. Varying the latency objective produced no resolvable movement where
the question is well posed.

That result depends on an empirically validated capacity reference rather than
on the configured parameter. The instrument used here — purpose-built, with an explicit
capacity parameter staffed by Little's law — overstated its service capacity
because of a per-request timing bias; using the pooled saturation-plateau
estimate, the overstatement is 9.26 percent at a
five-millisecond service time and 1.85 percent at twenty-five, against a margin
under one percent. That bias generated a stable second-order effect, which survived a falsification
test registered before the data that tested it were collected, and which
calibration then reduced to below the corrected search resolution.

We report the measurement, the trap, and three further written claims that later
measurement overturned during the pre-registered campaign. The harness, the pre-registration with its dated amendments, the
analysis scripts and the figure generators are publicly archived.
<!-- article:abstract:end -->

---

## Index terms

Alphabetical, IEEE taxonomy:

<!-- article:index-terms:start -->
admission control, capacity planning, measurement, message queueing,
performance evaluation, reproducibility, service level agreements
<!-- article:index-terms:end -->

---

## Author biography — Jay Nirmal

*Draft 3.1, 2026-09-20. **Wording supplied by the author**, checked line by
line against `Jay_Nirmal_IEEE_Associate_Editor_CV_Final.pdf` — **the copy attached to this
project's workspace, not the one on the author's disk**. The executor checked a second CV,
`Jay_Nirmal_CV.pdf` (3 Sep 2026, iCloud), which differs: it gives the first degree
as **B.S.**, not B.E., the location as Maharashtra, no member number, and no
"fault-tolerance" term (the project CV has "Network Failure & Fault-Tolerance
Testing"). Both CVs name one employer, so "platforms" was made singular at
draft 3.1. **CLOSED 2026-09-20: the degree is the B.E.**, confirmed by
the author; the body already reads "B.E." and is unchanged. The iCloud CV
`Jay_Nirmal_CV.pdf`, which says "B.S.", is the one to correct — that is a CV
task, not a manuscript one. Four edits, all
conventions or corrections, none adding a claim: "the Mumbai University" -> "the
University of Mumbai" (the CV's and the institution's name); degree years 2017 and
2019 restored (IEEE Access biographies carry them; both are on the CV); "(Member,
IEEE)" added after the name (IEEE Access convention; CV: Member #101719233);
"backend" -> "back-end" (IEEE style). Employer deliberately not named. Still no
editorial role and no publications. **APPROVED AS WRITTEN by the author,
2026-09-20.** ORCID for the submission record:
`https://orcid.org/0009-0003-0886-4663` — not printed in the biography; IEEE
Access takes it from the submitting author's account. **Draft 3.2:** the
name now reads JAY SURESH NIRMAL, matching the byline, the ORCID record and
Paper 1's author block — an IEEE biography opens with the author's name as it
appears in the byline. No other word changed.*

## SPE front matter

*Added 2026-09-24. Software: Practice and Experience is the target venue; IEEE
Access is the fallback and its build is untouched. SPE takes a free-format
submission, so the body does not change and the template does not change — only
what is below. **The abstract and the index terms are NOT duplicated here.**
The SPE build derives both from the article blocks above by removing exactly
one sentence and exactly one term, and asserts that each was present before it
went. Two hand-maintained copies of an abstract is how they drift.*

<!-- spe:practitioner-points:start -->
1. Validate the capacity reference before using it to set a recovery drain
   rate. In this harness the configured figure overstated service capacity by
   9.26% at a 5 ms service time and 1.85% at 25 ms, both against measured
   capacity from the pooled saturation-plateau estimate; at 5 ms that error was
   more than an order of magnitude larger than the sub-percent margin being
   characterised.

2. Across all seven tested cells the safe drain boundary lay at or near
   measured service capacity, and was indistinguishable from it at each cell's
   own experimental resolution. Differences among the tested configurations —
   service time, configured capacity, admission limit, concurrency and the
   latency objective — were not resolved by the experiment.

3. Request timeout rate gave no advance warning of the boundary in any of the
   six cells evaluated for leading indicators — the four E1 boundaries and the
   two corrected-harness cells — remaining below its criterion through every
   safe point, with a total sigma of 0.00 in all six. The result reproduced on
   the corrected-harness corpus, which was collected after the analysis
   statistic was frozen and played no part in choosing it.
<!-- spe:practitioner-points:end -->

<!-- spe:statements:start -->
**Data availability.** The harness, the pre-registration with its amendments
and addenda, every run record and per-request trace, the analysis code, the
figure generators, and the regression fixture are archived under concept DOI
`10.5281/zenodo.22761130`. `MANIFEST.json` records a SHA-256 for every archived
file and the commit from which the package was built. Every reported artefact
regenerates byte-identically from the committed data by running its associated
script.

**Funding.** This research received no external funding.

**Conflict of interest.** The author declares no conflict of interest.

**Ethics approval.** Not applicable; the study involved no human or animal
subjects.

**Permission to reproduce.** Not applicable; no material from other sources is
reproduced.
<!-- spe:statements:end -->

<!-- article:biography:start -->
**JAY SURESH NIRMAL** (Member, IEEE) received the B.E. degree in computer engineering
from the University of Mumbai, Mumbai, India, in 2017, and the M.S. degree in
information systems from Northeastern University, Boston, MA, USA, in 2019. He is
currently a Senior Software Engineer in Boston, MA, USA, working on distributed
systems, real-time communication, failure recovery and observability for a
large-scale online assessment platform, and conducts independent systems
research in systems measurement and reproducible experimental methods.
<!-- article:biography:end -->

---

## BLOCKER — a false credential was in draft 1, and the filename is why

**Draft 1 said: "He is an Associate Editor for the IEEE Access journal." The CV
does not say that.** I wrote it from the file's NAME —
`Jay_Nirmal_IEEE_Associate_Editor_CV_Final.pdf` — without reading the document.
Reading it shows a CV **prepared to apply for** such a role: its summary says
Jay is *"interested in contributing to IEEE through editorial review, technical
evaluation, and dissemination,"* and its headings are *"Technical Research &
Editorial Interests"* and *"Review interests."* There is no appointment on it.

**That sentence must not enter the manuscript unless Jay holds the position and
can evidence it.** An unearned editorial title in an IEEE author biography, in a
paper submitted to that same publisher, is the most damaging single sentence
this manuscript could carry — and its only source was a filename.

**Draft 1's second unsupported claim:** *"has published on failure testing and
recovery policy."* The CV lists *Reproducible WebRTC Failure Testing With
Playwright* as **"Submitted / Under Editorial Review,"** and the getStats and
SDP items as technical articles. Nothing there is a published peer-reviewed
paper on that topic. The draft 2 biography above therefore claims no
publications at all.

**What the CV does support, if Jay wants any of it added:**
- One peer-reviewed conference publication: S. Harale, A. S. Dhillon, J. Nirmal,
  and N. Kunte, *"Detection of Heart Disease using Classification Algorithm,"*
  IJERT, ICIATE 2017 Conference Proceedings, vol. 5, no. 1.
- IEEE Member #101719233; IEEE Young Professionals, IEEE Cloud Computing, IEEE
  Computer Society Technical Community.
- Judging service: Columbia University DivHacks (September 2026) and Impact
  Forge Virtual Code Sprint (August 2026).
- Seven-plus years of industry experience; at Meazure Learning since Nov 2021.

I have left all of it out. An IEEE biography is conventionally degrees, current
position, research interests and membership grade, and the shortest defensible
version is the one that cannot be challenged. **The author approved the paragraph above as written
on 2026-09-20 and added none of it.**

---

## The other pre-submission assertion check

**The abstract's closing sentence — "publicly archived" — is now true.
SATISFIED 2026-09-23.** The Zenodo record is published and the article cites
the concept DOI `https://doi.org/10.5281/zenodo.22761130`, which always
resolves to the newest version: CC BY 4.0, seven objects. v1.0.0 was record
`22761131`; **v1.0.1 was published 2026-09-23 as record `22923220`** for a
build defect on page 20; **v1.1.0 was published 2026-09-24 as record
`22941578`**, and the concept DOI resolves there now. The check was: verify the deposit is published,
then verify this sentence, then submit. The first two are done and the
sentence stands as written; no rewrite was needed.

*(The publication date is Zenodo's own, which is UTC. The commit recording it
here is dated 2026-09-22 by the repository clock at −0400. Both are correct
and they differ by the offset, which this project has mistaken for drift three
times.)*
