# References — IEEE style

*Draft 5 — SOURCE SET AND METADATA FROZEN at 14. 2026-09-20. W4 deliverable.
Written against outline v9.7.*

*Draft 5 is three mechanical fixes, and the first two are the same failure this
file exists to document.
(i) **"independent" → "distinct" did not propagate.** Draft 4 corrected the [13]
note where the reviewer pointed and left the word standing in the distribution
table and in its own change log. Fixed where a drafter reads, not where the
reviewer looked — which is the rule this project wrote down five times before
writing a checker for it.
(ii) **Papadopoulos did not propagate into the live citation inventories.** The
bibliography said [14] attaches to §II-D; neither §2's own citation inventory nor
the outline's Thread-4 anchor list knew it existed. Added to both. **A new
check now enforces this** — see below.
(iii) **The predicted numbering sequence is deleted**, not corrected. It was
wrong when written.*

*Draft 4 is three corrections and one deferral.
(i) **My draft 3 note said [12] and [13] were "fourteen months apart". They are
68 days apart.** An arithmetic error, in a working note whose entire subject was
the standard of evidence required to say "recurring". Corrected to "about two
months", which is still sufficient for recurrence.
(ii) **"independent" → "distinct"**, which is what the record supports; the
stronger word implies an independence neither claimed nor needed.
(iii) **§II's working header and §II-A's body are source-aligned** — see below.
(iv) **Reference NUMBERS are not locked.** See the numbering note.*

*Draft 3 closes the one substantive blocker and adds the work whose earlier
recommendation carried a mismatched link.
(i) **One GitLab incident establishes occurrence, not recurrence** — my draft 2
note claimed a single dated record supports §II-A's "recurring". It does not,
and the fix needs no change to frozen §II: a second incident is added at [13].
(ii) **Papadopoulos et al. is in at [14]**, now verified. I withheld it at draft
2 because the recommendation arrived with a link to a different paper; the
metadata is now confirmed directly and the work belongs in §II-D beside
Mytkowicz and Ousterhout.
(iii) **Access dates are no longer "re-dated" if W5 slips.** An access date
records when a page was actually accessed. The draft 2 instruction to update it
was wrong and is removed from [3], [11], [12] and [13].*

*PROVENANCE IS MARKED PER ENTRY, because draft 1's rule — a field appears only
if verified — has to survive a review that supplied the missing fields. Review
supplied page ranges and author lists with sources. I re-verified the two that
were wholly absent in draft 1 and accepted the rest on the review's sources
without opening each publisher page myself. Each entry says which. `[R]` = from
review, source cited, not independently re-checked by me. `[V]` = I verified it
against a publisher or preprint page in this session. Nothing is marked as
verified that I did not open.*

---

## The list

**[1]** T. Mytkowicz, A. Diwan, M. Hauswirth, and P. F. Sweeney, "Producing
wrong data without doing anything obviously wrong!" in *Proc. 14th Int. Conf.
Architectural Support for Programming Languages and Operating Systems (ASPLOS)*,
2009, pp. 265–276, doi: 10.1145/1508244.1508275.
<!-- authors/title/venue/DOI [V] · pp. [R], DBLP -->

**[2]** J. Ousterhout, "Always measure one level deeper," *Commun. ACM*, vol. 61,
no. 7, pp. 74–83, Jul. 2018, doi: 10.1145/3213770.
<!-- authors/title/venue/DOI [V] · vol/no/pp [R], author's own publication list -->

**[3]** G. Heiser, "Systems benchmarking crimes," UNSW Sydney. [Online].
Available: https://gernot-heiser.org/benchmarking-crimes.html. Accessed:
Sep. 20, 2026.
<!-- [V] · A maintained web catalogue, NOT peer-reviewed. Must never be given a
     venue and year. **Do not re-date the access date at W5** — it records when
     the page was actually accessed, not when the manuscript was last touched.
     Change it only if someone genuinely revisits the page. Same for [11]-[13]. -->

**[4]** H. Zhou, M. Chen, Q. Lin, Y. Wang, X. She, S. Liu, R. Gu, B. C. Ooi, and
J. Yang, "Overload control for scaling WeChat microservices," in *Proc. ACM
Symp. Cloud Computing (SoCC)*, 2018, pp. 149–161, doi: 10.1145/3267809.3267823.
<!-- title/venue/DOI [V] · full author list and pp. [R], authors' own page.
     Preprint arXiv:1806.04075. The DAGOR system. -->

**[5]** I. Cho, A. Saeed, J. Fried, S. J. Park, M. Alizadeh, and A. Belay,
"Overload control for µs-scale RPCs with Breakwater," in *Proc. 14th USENIX
Symp. Operating Systems Design and Implementation (OSDI)*, 2020, pp. 299–314.
<!-- [V] authors/title/venue via USENIX · pp. [R], cross-checked in review.
     USENIX assigns no DOI here — do NOT invent one. -->

**[6]** H. Xu and J. A. Colmenares, "Bouncer: Admission control with response
time objectives for low-latency online data systems," in *Companion Proc. Int.
Conf. Management of Data (SIGMOD)*, 2024, pp. 400–413,
doi: 10.1145/3626246.3653384.
<!-- authors [V] — I fetched arXiv:2312.15123 directly, because draft 1 had NO
     author list at all and that is the entry most likely to be wrong.
     Confirmed: Hao Xu, Juan A. Colmenares. NOTE the arXiv version's title omits
     the "Bouncer:" prefix that the SIGMOD version carries; use the SIGMOD form
     above. · pp. [R] -->

**[7]** K. Rzadca, P. Findeisen, J. Swiderski, P. Zych, P. Broniek,
J. Kusmierek, P. Nowak, B. Strack, P. Witusowski, S. Hand, and J. Wilkes,
"Autopilot: Workload autoscaling at Google," in *Proc. 15th European Conf.
Computer Systems (EuroSys)*, 2020, Art. no. 16, pp. 1–16,
doi: 10.1145/3342195.3387524.
<!-- title/venue/DOI [V] · 11-author list and article number [R], Google
     Research page. Formatted as "Art. no. 16, pp. 1-16" per IEEE practice;
     DBLP's "16:1-16:16" is its own rendering of ACM article numbering and is
     not IEEE style. -->

**[8]** L. Barroso, M. Marty, D. Patterson, and P. Ranganathan, "Attack of the
killer microseconds," *Commun. ACM*, vol. 60, no. 4, pp. 48–54, Apr. 2017,
doi: 10.1145/3015146.
<!-- authors/title/venue/DOI [V] · pp. [R], Google Research page -->

**[9]** J. Dean and L. A. Barroso, "The tail at scale," *Commun. ACM*, vol. 56,
no. 2, pp. 74–80, Feb. 2013, doi: 10.1145/2408776.2408794.
<!-- authors/title/venue [V] · pp. and DOI [R], DBLP. Draft 1 flagged the page
     range as unverified because it came from a course reading list; the review
     confirmed it against DBLP. -->

**[10]** J. D. C. Little, "A proof for the queuing formula: L = λW," *Operations
Research*, vol. 9, no. 3, pp. 383–387, 1961, doi: 10.1287/opre.9.3.383.
<!-- [V] — I confirmed volume, issue, pages and DOI against INFORMS and the ACM
     DL listing. NEW at draft 2: the review ruled that Little's law is used to
     justify the harness staffing relation in §III, not merely mentioned, so it
     earns a citation. -->

**[11]** D. Yanacek, "Avoiding insurmountable queue backlogs," *Amazon Builders'
Library*. [Online]. Available:
https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/.
Accessed: Sep. 20, 2026.
<!-- [R] author attribution. NEW at draft 2 — see the ruling below. -->

**[12]** GitLab, "2025-10-30: Sidekiq queueing SLO violation on multiple
shards," GitLab Infrastructure Production issue tracker, issue 20797. [Online].
Available: https://gitlab.com/gitlab-com/gl-infra/production/-/issues/20797.
Accessed: Sep. 20, 2026.
<!-- [R]. Multiple shards at full capacity, backlog, queueing-SLO violation,
     capacity temporarily raised to clear it. -->

**[13]** GitLab, "2026-01-06: Sidekiq queueing SLO violation on urgent-cpu-bound
shard (apdex 73.88%)," GitLab Infrastructure Production issue tracker, issue
21046. [Online]. Available:
https://gitlab.com/gitlab-com/gl-infra/production/-/issues/21046. Accessed:
Sep. 20, 2026.
<!-- [V] — I opened this one. Title, date and figures confirmed: apdex 73.88%,
     backlog peaking at 600,000-700,000 jobs, root cause an index dropped in a
     post-deployment migration. NEW at draft 3, and it is what makes §II-A's
     "recurring" true: [12] and [13] are distinct incidents about two months
     apart, so together they establish recurrence where one established only
     occurrence. TWO CORRECTIONS TO MY OWN DRAFT 3 NOTE: it said "fourteen
     months" (30 Oct 2025 to 6 Jan 2026 is 68 days) and "independent", which
     implies a statistical or organisational independence not claimed and not
     needed. Both are the same failure the note was describing. -->

**[14]** A. V. Papadopoulos, L. Versluis, A. Bauer, N. Herbst,
J. von Kistowski, A. Ali-Eldin, C. L. Abad, J. N. Amaral, P. Tůma, and
A. Iosup, "Methodological principles for reproducible performance evaluation in
cloud computing," *IEEE Trans. Softw. Eng.*, vol. 47, no. 8, pp. 1528–1543,
Aug. 2021, doi: 10.1109/TSE.2019.2927908.
<!-- [V] — full metadata confirmed independently against the authors'
     institutional record: 10 authors in this order, TSE vol. 47 no. 8,
     pp. 1528-1543, Aug. 2021, that DOI. NEW at draft 3. Attaches to §II-D's
     measurement-validity paragraph beside Mytkowicz and Ousterhout; it proposes
     methodological principles for reproducible cloud-performance experiments
     and examines how such experiments are reported. **A citation added to an
     existing claim — no §II prose changes.** -->

---

## Rulings applied at draft 2

**Little's law: cited.** It is load-bearing in §III's staffing relation, not
decorative. **Erlang-C: not cited.** §II invokes it only to say this is not a
queueing-theory contribution; adding a reference to support a disclaimer about a
textbook model would be padding. If §II ever derives from it, that changes.

**AWS and GitLab: formally cited, reversing my draft 1 inclination.** I had
proposed keeping them as prose with footnote URLs, on the grounds that numbering
them would lend weight §II-A's wording refuses. The review's counter is better:
a numbered reference does not confer authority — the prose does — and what
matters is labelling the source accurately and making the claim traceable.
§II-A's own sentences already state their evidentiary role.

---

## Numbering is NOT settled, and must not be locked yet

**IEEE numbers references by order of first citation. The numbers in this file
are NOT in that order, and no predicted order is recorded here.**

Draft 4 carried a predicted sequence. It was **already wrong**: it placed Little
last, when §II-C mentions Little's law before §II-D reaches the
measurement-validity set, and a §I marker could move it earlier still. A
speculative mapping that is wrong on the day it is written is worse than none,
and maintaining it is another thing to keep in sync.

**The rule, and nothing more than the rule:** reference numbers are assigned
after citation markers are inserted, from order of first appearance. **Do not
hand-renumber beforehand.**

---

## Size: settled at 14, and the bibliography is closed

The ruling: **stop at 14.** Every entry does a specific job and the distribution
is defensible across §II's four threads —

| thread | references |
|---|---|
| overload and admission control | [4] DAGOR · [5] Breakwater · [6] Bouncer |
| capacity estimation and performance context | [7] Autopilot · [8] killer microseconds · [9] tail at scale |
| measurement validity (§II-D, the paper's home) | [1] Mytkowicz · [2] Ousterhout · [14] Papadopoulos · [3] Heiser's practitioner catalogue |
| operational backlog evidence (§II-A) | [11] AWS · [12] and [13] two distinct GitLab incidents |
| used in the method | [10] Little |

**Do not search for three more to reach 17.** Further literature enters only if
a reviewer identifies an actual missing neighbouring work. A reference added to
reach a count, in a section that does not use it, is the padding both reviews
have been trying to avoid.

**No §II prose was reopened.** [14] attaches to a claim §II-D already makes;
[13] supports a word §II-A already uses. Both are citation-strengthening
changes to a frozen section, which is the only kind permitted.

---

## What is still genuinely open

**Nothing in the bibliography.** The remaining front-matter item is the
biography, which waits on Jay rather than on verification: he has confirmed he
has never been an IEEE Associate Editor, and the draft claims no editorial role
and no publications.

**The artifact citations** — repository, pre-registration commit `371e477`,
Zenodo DOI `10.5281/zenodo.22761131`, regression fixture — are cited in §IV's
reproducibility statement rather than numbered here. **The DOI does not resolve
until the W6 deposit is published**, which is a hard pre-submission check
shared with the abstract's "publicly archived" sentence.
