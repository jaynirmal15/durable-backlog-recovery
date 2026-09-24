# §2 — Background and related work

*Draft 11 — FINAL TRIM, 2026-09-24. §II-A's closing paragraph and §II-B's closing paragraph are replaced by one sentence each: the first restated the paragraph above it, the second re-summarised §VII's results, which §VII owns in full. Every literature claim is preserved and no citation marker is removed — all fourteen reference numbers are byte-identical before and after, verified by dumping the bibitem order and the first-appearance order both ways.*

*Draft 10 — TWO-REVIEW REVISION, 2026-09-23. B4: §II-C's universal "the paper therefore requires an empirically validated capacity estimate" is brought into the same conditional form as §I and §X. No number changes.*

*Draft 9 — ACRONYM COMPLIANCE, 2026-09-20, ruled by review. §II-B's heading no longer uses `SLO` before its expansion — "Overload control and admission under service level objectives" — and its first sentence pairs the two: "a service level objective (SLO)". Required by the IEEE Access checklist; no other change.*
*Draft 8 — CUT PASS, increment 6, 2026-09-20. §II-E's second paragraph tightened; both objections and the answer to each are unchanged in substance. No other section text changes.*
*Draft 7 — CITATION MARKERS ONLY, 2026-09-20. Keyed markers `[@key]` inserted at twelve citing sentences of §II-A to §II-D, carrying thirteen of the fourteen references (Little is keyed in §I and §III) (the GitLab pair on "recurring"; Papadopoulos on the general measurement-bias clause before the colon of §II-D's opening sentence, Mytkowicz on the concrete compiler example after it — reviewer ruling 2026-09-20, moved off the Heiser sentence, where the catalogue was the grammatical subject). The move puts Papadopoulos ahead of Mytkowicz in first-appearance order. **No prose changed**; each marker attaches to a sentence the frozen draft already carries. Keys render to IEEE numbers by order of first appearance in a separate mechanical pass after review.*
*Draft 6 — SCIENCE FROZEN, citation-inventory sync only. 2026-09-20. The
reference list added Papadopoulos et al. at [14] — **the draft-5 numbering;
Papadopoulos is [11] after the citation pass renumbered by first appearance, and
the old->new map is in `references.md`** — and recorded that it attaches
to §II-D — and this section's own citation inventory did not know it existed.
Added here; no body prose changed, because it attaches to a claim §II-D already
makes. Caught in review, and now enforced by
`scripts/check_withdrawn_phrases.py`, which fails when a work in
`references.md` is missing from this inventory or the outline's anchor list.
Draft 5 made two edits, both
narrowing a claim to what the cited records actually show, neither changing the
science.
(i) The sourcing note said GitLab's violations "recur across 2025". One of the
two incidents now cited is January 2026, so the span is **late 2025 and early
2026**.
(ii) §II-A said violations recur "in production message-processing **systems**".
Both records are from one organisation's Sidekiq environment: they establish
recurrence in production message processing, not across multiple distinct
production systems. The plural was an accidental generalisation and is removed.
Draft 4 made two body edits after review of draft 3.
(i) The section opened "This paper sits at the intersection of four literatures,
and is a contribution to only one of them" — unnecessarily false, and
contradicted by §II-A and §II-C in the same section. The paper has two
identities by design. It now reads "its methodological home is the fourth".
(ii) "recovery-driven objective violations" over-read the incident records: they
show backlogs, saturation, queueing delay and queueing-SLO violations recurring,
not that a recovery drain caused them. Now "backlogs and queueing-objective
violations".
Also synced: the C3 note in this header still described the debt in the
withdrawn "conventional construction" form.
Draft 3 applied four small edits after review of draft 2.
(i) **"External measurement was sound; the internally assumed capacity model was
not" is withdrawn** — I introduced that sentence in draft 2 while fixing a
different contradiction, and it contradicts frozen §IX, which concedes that the
probe's effective clock resolution was never measured and that repeatability was
not measured at the two conditions compared. The paper cannot declare the
diagnostic instrument sound. The causal point survives without it: the probe
**exposed** the bias rather than generating it.
(ii) §II-A's "what is scarce is published guidance on where to set them" was a
second residual corpus-wide claim of the kind this section's sourcing note
forbids; it is now source-bounded. And "production systems that already follow
such advice" conflated two evidentiary jobs — AWS supports the techniques, the
incident records support recurrence, and neither shows the affected systems had
implemented the AWS advice. Those are now separate sentences.
(iii) §II-B's close no longer says §VII observes "a construction the literature
already uses" — only live latency is literature-backed; timeout rate and queue
depth are signals this experiment examines. It now states exactly what C3 needs:
live latency is a literature-grounded comparator, not an invented baseline.
(iv) *The Tail at Scale* no longer carries "performance near saturation is not
predictable from nominal specifications", which is this paper's thesis rather
than that paper's result. It supports the context only.
Draft 2 applied four substantive corrections from review of draft 1.
(i) **§II-A made the gap claim the draft's own sourcing note forbade.** "We are
not aware of a published measurement" and "a first measurement" are functionally
the claim I said two queries could not support. Replaced with a source-bounded
statement: the operational sources reviewed do not quantify the boundary or
report it with experimental resolution, and this paper supplies such a
measurement. No "first", no "no published measurement", no "no prior work".
(ii) **The latency-feedback claim was stronger than its citations.** DAGOR and
Breakwater both key on *queueing delay*; §VII concerns live *response-time*
percentiles, so "the default answer supplied by this literature and production
practice" over-read them. Bouncer (SIGMOD 2024), which admits on estimated
percentile response times against response-time objectives, is added, and the
claim is softened to "an established construction". The §VII sentence is also
resynced to the claim register: the queue-depth lead **remains exploratory
because the corrected corpus cannot resolve an effect of that size** — draft 1's
"does not survive as a supported claim" read as a failed replication.
(iii) **Autopilot and The Tail at Scale were over-attributed.** Autopilot now
supports only what it shows — manually managed jobs carry more slack than
autopiloted ones, for CPU and memory limits, so the analogy is to the practice
and not the quantity — and "engineer-supplied limits are routinely wrong" is
gone. The overhead mechanism now cites Barroso et al.'s killer-microseconds
result, which is about small overheads growing large relative to short service
times; The Tail at Scale supports only the high-utilisation context.
(iv) **§II-D contradicted frozen §IX.** It said the bias "was not in the
measurement apparatus", while §IX-A calls the synthetic downstream an instrument
built for the experiment. The real distinction is external measurement versus
internally assumed capacity model, and it now says that.
Also: "broker-side replication" is struck from §II-A's mechanism list — it is a
durability mechanism, not a drain-rate one; §II-C's contribution is "a
measurement of what the error cost in one instrument" rather than "a bound".
Outline budget 1,500 words; draft 4 is **1,407** of body (draft 1: 1,245;
draft 2: 1,404 — the jump was the Bouncer and killer-microseconds material;
draft 3: 1,409).
Still under budget, and thread one stays short deliberately: the literature to compare
against is thin, and padding it would mean asserting more than the search
supports. No figure. Written against outline v9.1.*

<!-- citation-inventory:start -->
*CITATIONS ARE NAMED IN PROSE AND NOT YET FORMATTED. The works are identified by
author and system so the argument can be reviewed now; the IEEE reference list
is a W4 task with the bibliography. Verified to venue and year:
Mytkowicz, Diwan, Hauswirth and Sweeney, "Producing wrong data without doing
anything obviously wrong!", ASPLOS 2009 (doi 10.1145/1508244.1508275);
Ousterhout, "Always measure one level deeper", CACM 2018 (doi 10.1145/3213770);
Heiser, "Systems benchmarking crimes" (standing catalogue, UNSW);
Papadopoulos, Versluis, Bauer, Herbst, von Kistowski, Ali-Eldin, Abad, Amaral,
Tuma and Iosup, "Methodological principles for reproducible performance
evaluation in cloud computing", IEEE Trans. Softw. Eng., vol. 47, no. 8,
pp. 1528-1543, Aug. 2021 (doi 10.1109/TSE.2019.2927908) — **added at draft 6**;
methodological and reproducibility support for §II-D, attaching to the existing
measurement-validity paragraph beside Mytkowicz and Ousterhout. **No new prose**;
Zhou et al., "Overload control for scaling WeChat microservices", SoCC 2018
(doi 10.1145/3267809.3267823, the DAGOR system; arXiv 1806.04075);
Cho, Saeed, Fried, Park, Alizadeh and Belay, "Overload Control for µs-scale RPCs
with Breakwater", OSDI 2020, pp. 299-314 — **verified at draft 2; the draft 1
placeholder is closed**;
"Bouncer: Admission Control with Response Time Objectives for Low-latency Online
Data Systems", SIGMOD Companion 2024 (doi 10.1145/3626246.3653384; arXiv
2312.15123) — **added at draft 2**, because DAGOR and Breakwater both key on
queueing delay while §VII concerns live response-time percentiles, and the
section should not rest a response-time claim on queueing-delay systems alone;
Rzadca et al., "Autopilot: workload autoscaling at Google", EuroSys 2020
(doi 10.1145/3342195.3387524);
Barroso, Marty, Patterson and Ranganathan, "Attack of the killer microseconds",
CACM 2017 (doi 10.1145/3015146) — **added at draft 2** as the anchor for small
overheads growing large relative to short service times, which is this paper's
actual mechanism;
Dean and Barroso, "The tail at scale", CACM 2013, which now supports only the
high-utilisation tail-latency context and not the overhead mechanism.
**Heiser's catalogue is a maintained web resource, not a peer-reviewed paper**,
and must not be listed as though it were.
Thread one's two non-academic sources are the AWS Builders' Library article on
avoiding insurmountable queue backlogs, and GitLab's public Sidekiq queueing SLO
incident records. **Both are cited as evidence that the problem recurs
operationally, never as technical authority.***
<!-- citation-inventory:end -->

*SOURCING NOTE, and one finding the search produced. Threads two, three and four
have substantial peer-reviewed literature and the citations below are verified
to venue and year. **Thread one does not.** Searching for peer-reviewed work on
the drain-rate question — how fast a recovering consumer may work off a backlog
without violating a live latency objective — returns practitioner guidance (the
AWS Builders' Library on queue backlogs) and public incident reports (GitLab's
Sidekiq queueing SLO violations recur across late 2025 and early 2026), not
research. I have NOT
written "no prior work exists": absence of evidence from two searches is not a
literature gap, and asserting one is the kind of claim this campaign has twice
had to withdraw. §2 instead says what is defensible — the problem is documented
operationally and the guidance for it is qualitative — and leaves the stronger
claim unmade. **If the reviewer wants a gap claim, it needs a systematic search
with its scope recorded, not two queries.***

*A NOTE ON C3's DEBT, in its settled form. §2 establishes **live latency as a
literature-grounded comparator** for §VII — not as "the conventional
construction", which no cited work supports and which was withdrawn at draft 2.
That is what lets §VII's findings — timeout rate gives no advance warning, and
the queue-depth ordering is exploratory — land as results about a signal the
literature already uses rather than about a strawman. §VII examines that
comparator alongside timeout rate and queue depth, which are this experiment's
signals. §II-B's last paragraph carries it. Source comments strip in W6.*

---

## 2. BACKGROUND AND RELATED WORK

This paper sits at the intersection of four literatures; its methodological home
is the fourth.

### A. Recovery and backlog staging in durable log systems

A durable log decouples producer from consumer, which is what makes it valuable
during an outage and what creates the problem afterwards. When the consumer
returns, the accumulated backlog and the live arrival stream compete for the
same downstream capacity, and the recovery can degrade service for users the
original incident never touched.

The mechanisms for controlling that competition are standard and widely
deployed: consumer-side rate limits, bounded in-flight windows, batch sizing,
client quotas, prioritisation, and isolation of recovery work from live work.
The operational sources reviewed here do not provide a quantitative rule for
setting those controls. They treat backlog drain as a capacity-planning and
prioritisation problem: Amazon's Builders' Library [@yanacek] describes separate and
spillover queues, throttling, and processing fresh work ahead of old backlog,
rather than metering a shared path. Separately, public incident records show backlogs and
queueing-objective violations recurring in production message processing [@gitlab-20797], [@gitlab-21046].

These sources establish the operational problem and qualitative mitigation, not
a quantitative safe-drain rule. This paper measures that boundary and reports
the measurement at its experimental resolution.

### B. Overload control and admission under service level objectives

Where a shared downstream must protect a service level objective (SLO), the
established answer is
to shed or delay work. Production and research overload controllers make that
decision from an observed signal and a target: DAGOR [@dagor], deployed across WeChat's
microservice fleet, detects overload from average request queueing time and
applies admission control with per-service priority thresholds; Breakwater
[@breakwater] adjusts server-issued credits from measured queueing delay against a target, to
hold tail latency under heavy load; and Bouncer [@bouncer] admits or rejects queries using
estimated percentile *response* times against response-time objectives. The
design pattern these share is a feedback loop closed on a latency-derived
signal — queueing delay in the first two, response-time percentiles in the
third.

Two things follow for this paper, one narrow and one not.

The narrow one is scope. Those systems decide *which requests to admit* under
overload. This paper measures *where the boundary sits* for a workload that is
already admitted and is being paced deliberately. The recovery path here is
open-loop rate-limited — a fixed rate per run, varied between runs by the search
— precisely so that the boundary is a property of the system rather than of a
controller's dynamics. No controller is evaluated here and none is recommended.

Together, DAGOR, Breakwater and Bouncer establish latency-derived feedback as a
literature-grounded comparator for §VII, which examines live latency alongside
timeout rate and queue depth.

### C. Capacity estimation and self-tuning

The third thread is where this paper's conclusion joins. Systems that size
themselves must estimate how much work they can do. Google's Autopilot [@autopilot] sets
resource limits and replica counts for production workloads from observed usage
history rather than from declared configuration, and reports that manually
managed jobs carried substantially more slack relative to observed need than
autopiloted ones — motivation for estimating a resource requirement empirically
rather than accepting a declared one. That concerns CPU and memory limits rather
than downstream service capacity, and the analogy is to the practice, not to the
quantity.

A second observation is closer to this paper's mechanism. Barroso and colleagues
[@killer-microseconds] show that small software overheads become large *relative* to service times as
those times shrink toward the microsecond range, sharply reducing achievable
throughput efficiency — the same arithmetic that makes an approximately
constant per-request cost a 9.26% capacity error at a 5 ms service time and
1.85% at 25 ms. The tail-latency literature supplies the surrounding context: rising
utilisation and scale make latency increasingly sensitive at the margin [@tail-at-scale].

This paper's contribution to that thread is a measurement of what the error
cost in one instrument, not a new estimator and not a general bound. The finding
is that a purpose-built instrument,
whose capacity parameter was chosen by its author and whose worker count was
derived from it by Little's law, overstated its own service capacity by 9.26% at
one service time and 1.85% at another — while the safety margin being
characterised was under one percent. The paper therefore reports what
interpreting that margin required — a capacity reference validated against
observed throughput rather than the configured parameter — and deliberately does
not decide whether such an estimate should be supplied offline or inferred online, because the measurement
reported in §V bears on that question without settling it: the per-request cost
is not a fixed constant but varies with offered load, so an offline benchmark
would itself have to be run at the load condition that matters.

### D. Measurement validity in systems experiments

The fourth thread is the paper's home.

The canonical result is Mytkowicz and colleagues' demonstration that measurement
bias in systems experiments is commonplace and large enough to invert
conclusions [@papadopoulos]: changing the size of an environment variable or the link order of
object files was sufficient to reverse the apparent effect of a compiler
optimisation, in experiments that looked methodologically sound [@mytkowicz]. Ousterhout's
argument that one should always measure one level deeper is the constructive
form of the same point — that a top-level number should be checked against the
mechanism that produces it, because an aggregate can be right for the wrong
reason [@ousterhout]. Heiser's catalogue of benchmarking crimes [@heiser] makes the failure modes
enumerable, and much of the catalogue concerns exactly this: quantities reported
without the conditions under which they were obtained.

What this paper adds to that thread is a specific and, we think,
under-appreciated shape of the problem. **When the safety margin being
characterised is sub-percent, a small and approximately service-time-independent
per-request timing bias can exceed the phenomenon under study, generate a stable
but false second-order effect, survive deliberate falsification, and invalidate
conclusions about which signals are usable for control.**

Two features distinguish it from the established examples. The independent
timing probe exposed the bias rather than generating it: the bias under study
was embedded in the synthetic downstream's own capacity accounting, so every
quantity normalised by configured capacity inherited it consistently and nothing
looked anomalous. §IX records what the probe itself cannot establish, which is a
separate matter from where the false finding originated. And the false effect it
produced was not noise: it was stable across
repetitions, ordered in a physically sensible direction, and it passed a
falsification test registered before the data that tested it were collected.
§VIII gives that case in full, together with the two that behaved differently.

### E. What this paper does not claim

This is not a queueing-theory contribution. We claim no new model, no new bound,
and no result about M/M/c. That a saturating server degrades sharply as
utilisation approaches unity is textbook, and the observation that the boundary
sits near capacity is not offered as a discovery. The contribution is that the
utilisation a system computes for itself can be wrong by far more than the
operating margin being characterised, and that we demonstrate this by falling
into it under a public pre-registration with an explicit falsification protocol
and a standing commitment to retract.

That disclaimer answers the reader who observes that Erlang-C already predicts
sharp degradation near saturation. It does not answer the reader who observes
that a runtime timer overrun is an implementation defect rather than a research
result; the scale-mismatch claim above answers that one, since the interesting
fact is not the defect's cause but that a sub-millisecond bookkeeping error was
large enough, relative to the quantity under study, to manufacture a
second-order finding that survived a test designed to kill it.
