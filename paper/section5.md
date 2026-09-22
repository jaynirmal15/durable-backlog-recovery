# §5 — The calibration defect

*Draft 23 — CUT PASS, increment 7, 2026-09-20, the last authorised cut. §V
compressed from ~2,710 to ~1,900 words against the reviewer's content floor,
which is kept in full: the direct measurement and its limitations; the
constant-versus-proportional result and the timer attribution; δ's variation with
load; the distinction between the pooled correction and the separate prediction
constants; the registered 1987.4 / 1997.7 predictions; A8's different registered
reading per arm; the replicated medians and ranges, with short-arm discrimination
against long-arm non-discrimination; leave-one-out and its limitation; the failed
finer boundary prediction under both estimators; the matched 94-95% elimination;
and the provenance qualification. Compressed: narration and chronology around
those. §V-G moves to S1-J, its content already carried by §IX. No number, finding
or rule changes.*
*Draft 23.1 — APPROVED AND FROZEN by review, 2026-09-20, after two synchronisation fixes: the claim register's exact C2 sentence (per-arm medians 0.4690 / 0.4505, probe constants 0.5165 / 0.5114, load range 0.463 to 0.517 ms) is restored verbatim in §V-C, replacing the dispersed and rounded wording; and `c = ceil(C·S)` is written `c = ceil(C_config · S)`, since the four capacity terms are never interchanged. The cut pass is closed at 20 pages.*
*Draft 23 — KEYED FIGURE AND TABLE REFERENCES, 2026-09-20. Every literal "Fig. N", "Figure N" and "Table N" in the body is replaced by a key (`[@fig:…]`, `[@tab:…]`) that the build renders as "Fig. N" / "Table N" from order of first appearance — the citation design, applied to floats, so numbering cannot go stale when tables are added. §V's four tables gain labels and in-text references, as the reviewer's ruling to number every article table requires: three references are parenthetical insertions into existing sentences; **one is a new sentence** introducing the δ-predictions table, which had no introducing sentence to attach to — worded, on review, as "the registered and comparison predictions" rather than "each candidate correction's prediction", because the table also carries the pooled correction and the in-situ estimate, which was explicitly not a candidate. It is the only new prose in this pass. No other wording changed.*
*Draft 22 — SCIENCE FROZEN. 2026-09-20.
Draft 22: §V-A said three effects each survived their falsification test. One of
the three — the admission-limit explanation — was refuted by its own registered
test. Corrected; see §I draft 15 and §VIII.*
*Draft 21 — SCIENCE FROZEN. 2026-09-20.
Draft 21: §V-G cited "Table 2" for three items that table explicitly excludes —
its own header says process errors "are not included here; they are recorded in
the plan addenda". The citation pointed at a table holding three different
claims. Replaced with §IX and the registration, which do carry them. Mechanical.*
*Draft 20 — provenance gap disclosed. 2026-09-18.
Draft 20: the provenance field list names all four (commit, branch, dirty flag,
start time), matching A9.*
*Draft 19 — provenance gap disclosed. 2026-09-18.
Draft 19: the plateau measurements carry NO provenance — `overhead_run` writes no
commit, no dirty flag and no timestamp — so the committed record cannot establish
that the registration predates them. Draft 15's compression had dropped the
caveat that draft 10 carried; this restores it and states the gap plainly. The
same gap applies to A8's twenty windows.*
*Draft 18 — COMPRESSION PASS + provenance precision. 2026-09-18.
Draft 18: the A8-preamble parenthetical reduced to one sentence; A9 and §IX carry
the provenance detail.*
*Draft 17 — COMPRESSION PASS + provenance precision. 2026-09-18.
Draft 17: every numerical 0.463 now carries instrument and condition —
"pooled saturation-plateau-inferred" — as the claim register requires. Where the
direct probe's own saturation values appear nearby they keep "direct timing
probe" attached, so the two instruments cannot be read as one.*
*Draft 16 — COMPRESSION PASS + provenance precision. 2026-09-18.
Draft 16: `pooled` restored to the correction's δ, the leave-one-out estimator
named as the median over the other six cells, "reproduces" -> "predicts", and the
candidate table's adjudication sentence corrected — A8's rules turn on the spread
as well as the median, which the earlier sentence did not say.*
*Draft 15 — COMPRESSION PASS. 2026-09-18. Outline budget 1,600 words; this draft
is ~2,250 of body, down from ~3,750. No claim, number, qualification or adverse
result was removed. What moved out, to §IX or the artefact record: the clock-
resolution argument and the percentile-buffer caveat (§V-B), the full A8-preamble
correction (one sentence retained here), the repository-versus-deposit
reproducibility discussion (§IV already owns it), and §V-G's campaign diary (one
sentence retained). What was compressed in place: the direct-timing commentary,
the A8 narrative, and the twice-told chronology of the original single windows.
The science is unchanged from draft 14 and remains frozen; the next review is a
claim-preserving audit, not another flaw hunt. Source comments strip in W6.*

---

## 5. THE CALIBRATION DEFECT

### A. Why the instrument was measured

Two of the three registered candidate explanations survived their falsification
tests (§VIII). Having failed to kill them by attacking the hypotheses, we turned
the instrument on itself and asked what a worker actually costs per request. The
defect was found by measuring the apparatus, not by reasoning about the results
it produced.

### B. Measuring the overhead directly

A per-request probe records the interval a worker is occupied beyond the service
time it emulates, decomposed into bookkeeping before the wait, the amount by
which the runtime's timed wait overruns its requested duration, and bookkeeping
after it. The probe is off by default and every change to the harness is
additive. Each 90%-load and saturation figure is an untrimmed arithmetic mean
over roughly 115,000 to 137,000 worker cycles in a single 60-second window; the
mean is the correct statistic because the capacity model concerns total worker
time per request rather than a typical one. §IX records the right-skew of the
per-cycle distribution, the clock-resolution argument and the percentile-buffer
caveat.

**The instrument was controlled before it was trusted, though the control is
weaker than it looks.** A criterion registered in advance required the saturation
plateau to move by less than 0.5% between probe on and probe off; it moved 0.04%
at `S` = 5 ms and 0.09% at 25 ms. But the comparison is single-shot, and the
plateau's own window-to-window scatter is now known to be larger than the shift
reported, at 0.16% and 0.14% of capacity. The check detects no probe effect above
a comparable scale of empirical variability; it does not bound the intrusion
below that scale, and does not claim to.

**The cost is approximately service-time-independent over the tested fivefold
range.** At 90% of capacity a constant cost predicts
`excess(25 ms) − excess(5 ms) = 0` and a proportional one a ratio of five. The
measured difference is **−0.0051 ms** and the measured ratio is **0.990**, the
residual running *opposite* to what proportionality requires. **It is almost
entirely timer overshoot**: the runtime's late return accounts for **99.81%** of
the excess at `S` = 5 ms and 99.79% at 25 ms, with queue and slot bookkeeping and
the completion signal together contributing 1.29 and 1.38 µs. The attribution is
not condition-free — at saturation the long arm falls to 99.75% — and every
figure is quoted with its load condition, as every `δ` in this paper is.
[@fig:overhead] carries the decomposition and the constant-versus-proportional
test.

### C. One cost, three values, two instruments

`δ` is not a single number and is never reported as one. The **direct timing
probe** measured it under three conditions, and the reported estimate decreases
across them ([@tab:delta-conditions]):

<!-- table:tab:delta-conditions -->
| condition | `S` = 5 ms | `S` = 25 ms | estimator |
|---|---:|---:|---|
| at 90% of capacity | 0.5165 ms | 0.5114 ms | mean over one 60 s window |
| at saturation | 0.4947 ms | 0.4914 ms | mean over one 60 s window |
| in situ, during a drain | 0.4775 ms | 0.4746 ms | median across runs of per-run medians of means |

The estimator column is not decoration: the first two rows are single-window
means, the third aggregates three deep across 15 to 18 runs, so the in-situ
figure's stability is partly estimator rather than condition.

Two of the three isolate offered load, sharing an estimator and a construction:
between 90% of capacity and saturation the estimate falls by 0.022 ms in the
short arm and 0.020 ms in the long one, the same direction in both. The probe's
run-to-run repeatability is available at the third condition, where the in-situ
figure aggregates 18 and 15 runs whose run means span 0.0053 and 0.0040 ms.
**The load effect is four to five times that full span**, and nine to ten times
its interquartile range. The comparison is indicative rather than exact — those
runs are 111 to 120 seconds under bursty arrivals, not 60-second windows under
the calibration driver, and repeatability at the two compared conditions was not
measured (§IX).

A separate and weaker instrument infers `δ` from throughput rather than timing.
The **pooled saturation-plateau-inferred** value is 0.463 ms, the median of seven
per-cell estimates whose range is 0.032 ms; they separate cleanly by service time
and do not overlap — 0.465, 0.469 and 0.473 ms in the short arm against 0.441,
0.447, 0.454 and 0.463 in the long one. Taking the two instruments together:
a per-request overhead **approximately service-time-independent — constant
to within 4% across a fivefold service-time range** — (per-arm medians 0.4690 ms at S=5 against 0.4505 at
S=25; probe constants 0.5165 against 0.5114), and **varying with offered
load** (0.463 to 0.517 ms across four measurements by two instruments). That
arm-level difference is the same one the residuals report below, seen here in the
inputs, and it is why the paper calls service-time independence approximate.

**One pooled value was nonetheless applied to both arms, and that was not a
considered choice.** When the correction was made the seven estimates were
believed to describe one population; the arms were found not to overlap the
following day, after the corrected runs had been taken. An arm-specific
correction estimated from those same plateaus would have fitted
service-time-specific information back into the comparison, so the common
correction avoids that circularity and the residual 4% survives as a result
rather than being fitted away — a consequence recognised only afterwards.

The two instruments are kept distinct throughout, because §V-D depends on which
supplied which quantity. The variation also matters beyond bookkeeping: a merely
constant cost could be measured once and folded into a capacity model
permanently, whereas one that moves with the operating condition cannot be
represented reliably by a single fixed correction — which is why §I declines to
claim either that capacity must be estimated online or that an offline benchmark
would suffice.

### D. The prospective plateau prediction

The correction applied to the emulated service time was the **pooled
saturation-plateau-inferred** 0.463 ms, with the worker count held fixed by
construction so that integer rounding in `c = ceil(C_config · S)` could not blur the
prediction; corrected and uncorrected arms ran with identical staffing and
identical admission limits.

**The prediction did not use that constant.** It used the **direct timing
probe's saturation values**, 0.4947 and 0.4914 ms, measured on separate
uncorrected runs by a different instrument from the one that produced the
correction:

```
S = 5:   c = 10   4.537 + 0.4947 = 5.0317 ms   →  10 / 0.0050317 = 1987.4 rps
S = 25:  c = 50   24.537 + 0.4914 = 25.0284 ms →  50 / 0.0250284 = 1997.7 rps
```

**Both plateau figures were registered as plateaus, not derived afterwards.**
Addendum 1 of the E2e plan, commit `67c448b`, tabulates 1987.4 and 1997.7 rps and
states the check they govern: *each corrected cell's saturation plateau must
match 1987.4 and 1997.7 before its boundary is read.* No parameter was estimated
from the corrected runs. The same registration designated the saturation pair
over its rival, tabulated the rival's 90%-load prediction, and pre-committed the
reading if the rival won: *if the boundaries land nearer the 90%-load predictions
instead, that is reported as the finding.* Registered at 17:31:47 UTC on
2026-09-13, it precedes the first corrected *boundary* run by 39 minutes against
that record's committed `startedAt`. The in-situ figure was not a candidate — it
did not exist in the code until three hours later.

**The plateau measurements themselves are not timestamped, and the paper does not
claim otherwise.** They are written by a standalone tool that records no
provenance, so the committed record bounds them only to a window, 16:31:55 to
18:50:07 UTC, that contains the registration time; the ordering rests on the
registration's forward-looking language, on its statement that no boundary run
had started, and on an uncommitted campaign log. A8's twenty replication windows
are likewise untimed. Addendum A9 records the gap, and §IX carries it as a threat
to validity.

**Measured: 1987.4 and 1998.1 rps.** That was the original prospective test and,
for the remainder of the campaign, the whole of the evidence: one 60-second
window per arm, so the agreement could not be set against the scatter of the
quantity it agreed with. Both plateaus were therefore replicated under addendum
A8, registered in commit `590d1cc` before the harness was rebuilt and before any
window was run — ten 60-second windows per arm, median convention, with the
reading fixed in advance for every outcome, including the one that would have
withdrawn the claim made here ([@tab:a8-replication]):

<!-- table:tab:a8-replication -->
| arm | n | min | median | max | range | IQR |
|---|---:|---:|---:|---:|---:|---:|
| `S` = 5 | 10 | 1987.27 | **1988.96** | 1990.38 | 3.11 | 1.71 |
| `S` = 25 | 10 | 1996.52 | **1997.70** | 1999.35 | 2.83 | 1.29 |

**A8 registered a separate reading for each arm, and the asymmetry is reproduced
rather than smoothed into one rule.** For the short arm the reading is
containment: registered 1987.40 lies inside the observed [1987.27, 1990.38] and
the rival 1978.83 lies 8.4 rps outside. For the long arm the reading is a
different quantity — that the spread would exceed the 1.60 rps separating the two
implied plateaus — and it does, at 2.83 rps, so that arm cannot distinguish the
candidates. Applied uniformly, containment would credit both arms, but in the
long arm by 0.39 rps against a spread of 2.83, a margin seven times smaller than
the scatter; that is why A8 registered spread-versus-separation there instead.
(A8's preamble misstates these figures as unregistered; addendum A9 records the
correction.)

**Two qualifications the replication supplies and the single windows could not.**
The registered value sits near the *lower bound* of the observed range rather
than at its centre, which is why the original short-arm agreement read as 0.02
rps; replication puts the prediction 1.6 rps below the central estimate and the
rival 10.1 rps from it. **The discrimination is robust; the apparent exactness
was not.** The long arm shows the reverse — its replicated median agrees to 0.03
rps and selects nothing. **The arm that discriminates has the larger prediction
error, and the arm with near-exact agreement cannot discriminate at all.**

Both original observations fall within the corresponding A8 ranges, and the
spreads — 0.16% and 0.14% of capacity — fall inside the seven-cell corpus's
0.10–0.24% repeatability. [@tab:delta-predictions] sets the registered and
comparison predictions beside the replicated measured plateau.

<!-- table:tab:delta-predictions -->
| `δ` source | predicted at `S` = 5 | predicted at `S` = 25 |
|---|---:|---:|
| pooled saturation-plateau-inferred correction, 0.463 ms | 2000.0 | 2000.0 |
| **saturation probe — registered choice** | **1987.4** | **1997.7** |
| 90% load — the rival registered alongside it | 1978.8 | 1996.1 |
| in situ — measured later, not a candidate | 1994.2 | 1999.1 |
| **measured — replicated median of ten windows** | **1988.96** | **1997.70** |
| observed range across those ten windows | [1987.27, 1990.38] | [1996.52, 1999.35] |

A correction fitted to produce the expected answer predicts exactly `C_config`,
2000.0, in both arms — the circularity objection rendered in numbers. The
registered prediction instead placed the plateau *below* that, at a value set by
a constant the corrected runs never used. A8's adjudication uses the
arm-specific registered rules above, not the original single-window observations,
because one observation cannot be compared with a spread. [@fig:plateau] shows
predicted against measured plateau, uncorrected and corrected, for both arms.

**Internal stability.** Taking the median saturation-plateau-inferred `δ` over
the other six cells and predicting the held-out seventh places every held-out
plateau within one bisection step — worst case 0.98 steps, RMS 2.44 rps. This is
cross-validation *within* the campaign against the same error model: it shows the
inferred correction is stable across those cells, not that the model is
independently confirmed. The prospective, now replicated, plateau prediction is
the out-of-sample evidence. The residuals show an arm-aligned sign pattern — the
short-service arm over-predicted, three of four long-service cells
under-predicted, a per-arm gap of 4% — so service-time independence is
approximate rather than exact, and the paper quotes the 4%.

### E. A registered boundary prediction fails

A separately registered, finer prediction — that the corrected boundary would
land at `ρ*` = 0.9937 in the short arm and 0.9989 in the long one — **did not
survive.** The registration named the delivery-span estimator as the adjudicator;
the campaign reported under the drain-window estimator instead. **The prediction
fails under both estimators.** Under drain-window accounting the registered
values sit outside the brackets [0.988, 0.992] and [0.992, 0.994], by 1.4 and 2.4
steps. Under delivery-span accounting the last-SAFE values alone already exceed
the registered predictions, so those predictions are excluded without assigning
any utilisation to the collapsed upper endpoints, which §IV forbids.

**Post-hoc sensitivity analysis does not alter that verdict.** The two available
utilisation estimators differ by approximately 0.008 in `ρ`, comparable to the
separation among the candidate predictions, so the corpus cannot use the failed
prediction to identify which load-conditioned `δ` describes the boundary. That
dependence is a property of the accounting, not a confidence statement, and it is
reported at SAFE points only. One result is reported because it went against the
reasoning that produced it: the in-situ probe, motivated as potentially more
representative and the most stable of the three, nonetheless predicts a higher
boundary than the registered drain-window brackets support.

### F. What is and is not established

**Established.** A per-request component of worker occupancy: 0.47 to 0.52 ms by
the direct timing probe across its three conditions, 0.463 ms from the pooled
saturation-plateau-inferred estimate, with no unqualified single value
claimed. It is
approximately service-time-independent over the tested fivefold range and
dominated by timer overshoot. Under leave-one-out — the median of the other six
cells' estimates — `c/(S+δ)` predicts every held-out plateau to within one
bisection step; no cell is ever predicted from its
own inverse `δ = S(C_config/plateau − 1)`, which would reconstruct that plateau
algebraically rather than test it. In the short arm the replicated plateaus place the registered
constant's implied value inside the observed range and its rival outside; the
long arm cannot separate them.

**Established, under matched accounting.** The correction largely removes the
inter-arm difference, reported under each estimator separately in
[@tab:accounting]. The four-decimal
quantities are derived inter-arm differences, not measured per-cell utilisations;
the extra digit keeps the subtraction from erasing the effect, and the underlying
measured utilisations remain resolution-matched.

<!-- table:tab:accounting -->
| accounting | before | after | removed |
|---|---:|---:|---:|
| drain-window, utilisation | 0.0670 | 0.0032 | 95% |
| drain-window, throughput | 134.0 rps | 6.4 rps | 95% |
| delivery-span, utilisation | 0.0696 | 0.0043 | 94% |

Every row compares like with like — the last SAFE point only, one estimator on
both sides, the same aggregator and denominator. The throughput row carries no
utilisation denominator at all and agrees exactly with its utilisation
counterpart, which is the check worth having. **94 to 95% of the apparent effect
is removed, depending on estimator.** An earlier analysis reported 96.3% using
unmatched estimators; §IX records the supersession.

**Not established.** Which load-conditioned `δ` governs the boundary in the final
few tenths of a percent. The registered boundary prediction fails and the
estimator spread is too wide to adjudicate the candidates.

