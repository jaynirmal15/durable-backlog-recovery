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

## Abstract

*249 words, against a 150-250 limit — **measured, not asserted**. This header has now been wrong twice: draft 1 claimed 247 without counting (it was 259), and the first fix claimed "inside the limit" at 251. Recount after every edit to this section; it sits at the ceiling and three of the review edits added words.*

When a consumer recovers from an outage, its accumulated backlog and the live
traffic it still serves compete for the same downstream capacity. Draining too
fast turns the recovery into a second incident; draining too slowly leaves the
backlog outliving the outage. The operator's question is a rate, usually answered
by a chosen number, adjusted after it goes wrong.

We locate that boundary empirically. Across seven cells spanning two service
times, three configured capacities, two admission limits and four concurrency
levels, the safe drain boundary lay within one percent of measured service
capacity and was indistinguishable from capacity itself at the experiment's
resolution. Varying the latency objective produced no resolvable movement where
the question is well posed.

That result depends on an empirically validated capacity reference rather than
on the configured parameter. The instrument used here — purpose-built, with an explicit
capacity parameter staffed by Little's law — overstated its service capacity
because of a per-request timing bias; using the pooled saturation-plateau
estimate, the overstatement is 9.26 percent at a
five-millisecond service time and 1.85 percent at twenty-five, against a margin
under one percent. That bias generated a stable second-order effect, which survived a falsification
test registered before the data that tested it were collected, and which
calibration then removed almost entirely.

We report the measurement, the trap, and three further written claims that later
measurement overturned during the pre-registered campaign. The harness, the pre-registration with its dated amendments, the
analysis scripts and the figure generators are publicly archived.

---

## Index terms

Alphabetical, IEEE taxonomy:

**admission control, capacity planning, measurement, message queueing,
performance evaluation, reproducibility, service level agreements**

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
Access takes it from the submitting author's account.*

**JAY NIRMAL** (Member, IEEE) received the B.E. degree in computer engineering
from the University of Mumbai, Mumbai, India, in 2017, and the M.S. degree in
information systems from Northeastern University, Boston, MA, USA, in 2019. He is
currently a Senior Software Engineer in Boston, MA, USA, with experience in
distributed systems, real-time communication, back-end engineering, and production
reliability. His engineering work includes real-time communication systems, cloud
infrastructure, failure recovery, observability, and reliability improvement for
a large-scale online assessment platform. He also conducts independent systems
research. His research interests include distributed systems, failure recovery and
fault tolerance, systems measurement, observability, and reproducible experimental
methods.

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

**The abstract's closing sentence — "publicly archived" — is not yet true.** The
Zenodo deposit is a W6 task and the reserved DOI must resolve before submission.
This is a **hard pre-submission check**, not a rewrite: verify the deposit is
published, then verify this sentence, then submit. If the deposit slips, this
sentence is false at the moment of submission.
