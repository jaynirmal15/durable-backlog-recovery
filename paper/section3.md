# §3 — The harness, the capacity model, and its error model

*Draft 10 — FROZEN.
Draft 10: "rate-limited but not rate-controlled" replaced with "open-loop
rate-limited" — open-loop fixed-rate control is still rate control, so the earlier
phrasing left the objection open.*
*Draft 9 —
Draft 9: two architecture statements corrected against the code. The consumer is
NOT unrestricted — `consumer/main.go` carries a `RATE_LIMIT_RPS` limiter applied
to recovery-class messages, and that limit is the boundary search's independent
variable; what the consumer lacks is a *controller*. And the injector runs inside
the runner, so "four-component" plus five named parts was leaving the reader to
count.*
*Draft 8 —
Draft 8: the live injector is named. Draft 7 described only producer, consumer,
downstream and runner, so a reader necessarily concluded that live traffic
arrived through the broker; §IV meanwhile defined live as injector-direct. The
code is authoritative (`runner/main.go`: "live = injector only; JetStream =
recovery backlog only"), and post-restoration brokered messages are now named as
a separate population that the objective excludes. §III-E no longer calls the
pooled check independent validation.
Draft 7: the plateau check names its construction — one pooled constant across
all seven cells — so it cannot be read as substituting each cell's own inferred
delta back into itself.*
*Draft 6 — Sept 14 2026. Target 1,200 words; this draft is ~1,320. Figures F1, F2.
Draft 6: integrality of C_config·S confirmed for all seven cells. Draft 5: "achievable capacity" around C_model replaced with the model's own
prediction; section frozen. Draft 4: C_actual renamed C_model and added to the terminology set;
controller sentence aligned with §I; "are not the third" softened. Draft 3: nominal/staffed/measured capacity terminology made rigid;
`ceil` quantisation handled algebraically via staffed capacity; full-queue delay
given under both the intended and the corrected occupancy model; the "not a
post-hoc rationalisation" claim removed. Source comments strip in W6.*

---

## 3. THE HARNESS AND ITS CAPACITY MODEL

### A. Architecture

The harness is four services in Go, orchestrated by Docker Compose, plus a
runner that drives each run and also generates the live traffic (Fig. 1). A *producer* publishes events to a subject on a NATS JetStream stream
at a constant configured rate, and continues publishing throughout the
experiment, including while the consumer is stopped — that is what accumulates
the backlog. Every message carries a header recording its publish time in
milliseconds. A *consumer* is a durable pull consumer with a fixed worker pool and a
configured recovery rate limit `r_l`, applied to recovery-class messages only.
**The recovery path is open-loop rate-limited.** `r_l` is fixed for the duration
of each run and varied between runs by the boundary search; no within-run feedback
path adapts it in response to latency, queue depth, timeout rate or error rate.
The live injector is independently paced at its configured live rate. The
experiment therefore varies two independently configured open-loop rates that
compete at the shared downstream; it does not implement an adaptive recovery
controller. For each message it
compares the publish timestamp against a restoration epoch supplied by the
orchestrator and classifies the message as *recovery* if it was published before
the consumer was restarted. It then issues the work request to the *downstream*
and records a sample carrying the class, the observed latency, the returned
status and the message age. A *live injector* produces the live traffic: open-loop
HTTP requests at a configured rate, issued directly to the downstream and never
through the broker; it runs inside the runner process rather than as a fifth
service. The *runner* drives one run end to end and writes the run record.

**Live traffic means injector-direct requests, and only those.** The live and
recovery paths reach the shared downstream independently and are independently
paced: the recovery path is the consumer draining the broker under `r_l`, which
governs the recovery class only, and the live path is the injector at its own
configured rate. The consumer
also encounters messages published after the restoration epoch; these are *post-restoration brokered messages*, recorded but
excluded from the service-level objective, which is evaluated over the
injector-direct population alone. §IV gives the accounting. Classification by
publish timestamp rather than by arrival order is what separates recovery work
from the rest, and a harness reporting one blended latency could not evaluate the
objective at all. Messages are acknowledged regardless of the status
the downstream returns, since redelivery would confound the backlog count.

### B. Capacity: four distinct quantities

Four quantities are distinguished throughout this paper and are not
interchangeable.

- **C_config** — the capacity parameter the downstream is configured with.
- **C_staffed** — the capacity implied by the resulting worker count under the
  intended service time.
- **C_model** — the capacity predicted by the error model of §III-D,
  `c / (S + δ)`. A model prediction, kept distinct from `C_measured` even where
  the two agree closely.
- **C_measured** — the saturation plateau observed empirically.

A central finding of this paper is that, in this harness, the first two did not
equal the fourth.

The downstream is a synthetic service whose capacity parameter is settable at
run time. It is not a model of any particular dependency; it is an instrument
built so that the quantity the experiment varies is the quantity under study.
Capacity is realised as a bounded worker pool in front of an admission-limited
queue. Under an idealised worker model, in which a worker is occupied for exactly
the emulated service time `S` and is otherwise immediately available, Little's
law gives a mean in-service concurrency of `C_config · S`. The pool is therefore
staffed with

    c = ceil(C_config · S)                                                  (1)

workers, and the capacity that staffing implies under the idealised model is

    C_staffed = c / S                                                       (2)

Where `C_config · S` is integral, `C_staffed = C_config` exactly; otherwise the
ceiling in (1) makes `C_staffed` marginally larger. **In all seven cells of this
campaign the product is integral**, so `C_staffed` and `C_config` coincide
throughout and the ceiling contributes nothing to any reported quantity. All
subsequent algebra is nonetheless expressed in terms of `c` and `C_staffed`, so
that the quantisation in (1) cannot enter a derivation in a configuration where
it would not vanish.

The assumption embedded in (1) — that a worker's occupancy per request equals
the service time it emulates — is stated explicitly because §III-D shows it to be
false, and that falsity is the subject of this paper.

### C. Admission, and what the admission rule cannot explain

Admission is bounded separately from staffing. Under the *graceful* profile used
throughout this work the admission limit is

    queueCap = 50 · c                                                       (3)

and under the *cliff* profile it is `2 · c`, returning an immediate rejection
once full. The queue channel itself is allocated at four times the admission
limit; admission is enforced by a token pool rather than by channel capacity, so
the limit can be changed without reallocating.

<!-- downstream/main.go queueCapFor(), NewServer(), fullQueueDelayMs() -->

The time to traverse a full queue is the admission limit divided by the service
rate. Under the intended occupancy model the service rate is `c / S` and the
traversal time is `50 · S` — 250 ms at `S = 5` ms. Under the corrected occupancy
model of §III-D the service rate is `c / (S + δ)` and the traversal time is
`50 · (S + δ)`. In both cases the worker count cancels. **The admission rule
therefore cannot by itself produce a capacity-dependent or concurrency-dependent
queue-delay scale, under either the intended model or the corrected one** — a
point §VIII returns to, since one of the retracted findings proposed exactly that
mechanism.

One separation is deliberate and load-bearing. The configured capacity parameter
is exposed only on an administrative endpoint, which the consumer never reads.
The harness was built so that a recovery controller could not rely on the
configured capacity parameter and would have to operate from observations
instead. The results later justify distrust of that configured value, while not
determining whether a validated estimate should be supplied offline or inferred
online — a distinction §I leaves open and this paper does not settle. The
decision was taken before any measurement, for a reason narrower than the one
that ultimately justified it.

It is worth recording that the endpoint's response field is named `trueCapacity`,
and the specification describes it as exposing true capacity. It does not: it
returns `C_config`. The name is itself a residue of the assumption this paper
falsifies, and it is preserved unaltered in the archived artefact.

### D. Service-time emulation, and where the error enters

A request that reaches a worker is held for a jittered service time and then
returned. The jitter is a multiplicative Gaussian factor with a standard
deviation of 0.15, clamped symmetrically at ±0.5, so the emulated service time is
mean-preserving: jitter broadens the latency distribution without shifting its
mean, and contributes nothing to the discrepancy below.

<!-- downstream/main.go jitteredServiceTime(), serviceTimeJitterSigma -->

The worker's cycle, however, is longer than the service time it emulates
(Fig. 2). Each request occupies its worker for the intended interval plus three
further components: bookkeeping before the wait begins, the amount by which the
runtime's timed wait overruns its requested duration, and bookkeeping after it
ends. Writing the sum of those three as `δ`, the interval a worker is actually
occupied per request is

    S_actual = S + δ                                                        (4)

so the capacity the error model predicts the pool can sustain is

    C_model = c / (S + δ)                                                   (5)

while (1) and (2) staff and describe the pool as though occupancy were `S`. The
staffed capacity therefore exceeds the capacity the error model predicts by

    C_staffed / C_model = 1 + δ / S                                         (6)

Equations (4)–(6) are not specific to this implementation. They apply to any
fixed-concurrency service staffed from an assumed per-request occupancy that
omits some component of the actual occupancy, whatever the source of that
component. What is specific is the size of `δ` and its behaviour: it is
approximately independent of `S` rather than proportional to it. Equation (6)
then gives a large relative error at short service times and a small one at long
ones. With the pooled saturation-plateau-inferred `δ = 0.463` ms used for the
correction, the overstatement is
**9.26% at `S = 5` ms and 1.85% at `S = 25` ms**.

<!-- delta from results/E2d-REPORT.md, median of seven per-cell plateau estimates -->

### E. Checking the error model against the plateaus

The model's explanatory accuracy can be checked against the campaign's own
plateaus, and what that check is worth depends entirely on how the constant was
obtained. Taking the **pooled** plateau-inferred `δ` = 0.463 ms — one
constant applied unchanged to all seven cells, spanning two service times, three
configured capacities and four concurrency levels — `C_model` reproduces
`C_measured` for every cell to within 0.19%, with no cell failing. The per-cell
inferred values are not used: each is recovered from its own cell's plateau, so
substituting one back would reconstruct that plateau algebraically rather than
check anything. §V reports the leave-one-out form of this test, in which the
constant predicting each cell is estimated from the other six.

**This is an in-sample common-parameter check, not independent validation:** the
pooled constant was itself inferred from these seven plateaus, so applying it
back to them tests whether one number suffices across the set, not whether the
model holds outside it. What it does establish is that the pooled-model residual
is smaller than one boundary-bisection step in every cell. A stronger test — a correction predicted in
advance of the runs that tested it, using constants obtained from a separate
instrument — is presented in §V.

<!-- results/REVIEWER-RESPONSE-W2.md task 3 -->

### F. What the downstream is not

It has no persistent state, no I/O, no dependency of its own, and no failure
modes beyond queue rejection and request timeout. It is a timing instrument. The
threats this poses to the generality of the results are set out in §IX; the point
to carry forward is narrower and, for the argument of this paper, sufficient: a
purpose-built service with an explicit capacity parameter, constructed for this
study and measured by its author, was wrong about its own capacity by an amount
larger than the margin under measurement.
