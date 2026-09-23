# §3 — The harness, the capacity model, and its error model

*Draft 16 — TWO-REVIEW REVISION, 2026-09-23. A6: §III-A names the execution environment — instance type, CPU, memory, kernel, Go and Docker versions — read from the platform block every run record carries, identical across all 171 runs behind the seven cells. The paper had attributed the bias to "this host and this Go runtime" without naming either.*

*Draft 15 — CUT PASS, review fixes applied; see the approval note below. Originally Draft 14 — CUT PASS, increment 4, 2026-09-20, under the reviewer's 18-page
authorisation. §III compressed from ~1,700 to ~1,200 words. Kept: the four
services, open-loop rate-limited recovery with no within-run controller,
injector-direct live traffic and the population separation, the four capacity
terms, equations (1)–(6) and the cancellation argument on (3), the δ components,
the 9.26% / 1.85% overstatement, the in-sample caveat on the pooled check, and
the implementation-specificity of δ. Moved to S1-G: the cliff profile, the token
pool, the configured-capacity endpoint and its `trueCapacity` field. No number
or finding changes.*
*Draft 14.1 — APPROVED by review with two fixes: "retracted findings" → "candidate explanations" in §III-C, since the admission-limit explanation was never a finding; and the jitter parameters (σ = 0.15, clamp ±0.5) restored to §III-D. Frozen.*
*Draft 13 — CUT PASS, 2026-09-20. Fig. 2 moves to Supplement S1 by the reviewer's ruling: it carries no measured result, and equations (4)–(6) state what it pictures. Its one reference is removed; the following sentences already name the three components of `δ`, which is the one sentence the ruling requires near (4).*
*Draft 12 — KEYED FIGURE AND TABLE REFERENCES, 2026-09-20. Every literal "Fig. N", "Figure N" and "Table N" in the body is replaced by a key (`[@fig:…]`, `[@tab:…]`) that the build renders as "Fig. N" / "Table N" from order of first appearance — the citation design, applied to floats, so numbering cannot go stale when tables are added. No other wording changed.*
*Draft 11 — CITATION MARKERS ONLY, 2026-09-20. Keyed markers `[@key]` inserted at Little's law in the staffing relation (1), where §III uses it. **No prose changed**; each marker attaches to a sentence the frozen draft already carries. Keys render to IEEE numbers by order of first appearance in a separate mechanical pass after review.*
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
runner that drives each run and also generates the live traffic ([@fig:harness]).
A *producer* publishes events to a NATS JetStream stream at a constant configured
rate throughout the experiment, including while the consumer is stopped — that is
what accumulates the backlog — and every message carries its publish time. A
*consumer*, a durable pull consumer with a fixed worker pool, classifies a message
as *recovery* if it was published before the consumer was restarted, applies the
recovery rate limit `r_l` to that class only, and issues the work request to the
*downstream*, recording the class, latency, status and message age. A *live
injector*, running inside the runner, issues open-loop HTTP requests at its own
configured rate directly to the downstream, never through the broker.

**The execution environment.** Every run reported here ran on one AWS EC2
`c6i.2xlarge` instance — 8 vCPUs of Intel Xeon Platinum 8375C at 2.90 GHz,
15.3 GB of memory — under Linux kernel `7.0.0-1012-aws` on `linux/amd64`, with
Go 1.25.3 and Docker 29.1.3. Every run record carries this block, and it is
identical across all 171 runs behind the seven cells.

**The recovery path is open-loop rate-limited.** `r_l` is fixed for the duration
of each run and varied between runs by the boundary search; no within-run feedback
path adapts it in response to latency, queue depth, timeout rate or error rate.
The experiment therefore varies two independently configured open-loop rates that
compete at the shared downstream; it does not implement an adaptive recovery
controller.

**Live traffic means injector-direct requests, and only those.** Messages the
consumer meets that were published after restoration are recorded but excluded
from the service-level objective, which is evaluated over the injector-direct
population alone (§IV). Classification by publish timestamp rather than by arrival
order is what separates recovery work from the rest. Messages are acknowledged
regardless of the status the downstream returns, since redelivery would confound
the backlog count.

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

The downstream is a synthetic service, built so that the quantity the experiment
varies is the quantity under study: a bounded worker pool in front of an
admission-limited queue. Under an idealised worker model, in which a worker is
occupied for exactly the emulated service time `S` and is otherwise immediately
available, Little's law [@little] gives a mean in-service concurrency of
`C_config · S`. The pool is therefore staffed with

    c = ceil(C_config · S)                                                  (1)

workers, and the capacity that staffing implies under the idealised model is

    C_staffed = c / S                                                       (2)

Where `C_config · S` is integral, `C_staffed = C_config` exactly. **In all seven
cells of this campaign the product is integral**, so the two coincide throughout;
the algebra is nonetheless written in `c` and `C_staffed` so that the quantisation
in (1) cannot enter a derivation where it would not vanish. The assumption
embedded in (1) — that a worker's occupancy per request equals the service time
it emulates — is stated explicitly because §III-D shows it to be false, and that
falsity is the subject of this paper.

### C. Admission, and what the admission rule cannot explain

Admission is bounded separately from staffing. Under the *graceful* profile used
throughout this work the admission limit is

    queueCap = 50 · c                                                       (3)

The time to traverse a full queue is the admission limit divided by the service
rate. Under the intended occupancy model that is `50 · S` — 250 ms at `S = 5` ms;
under the corrected model of §III-D it is `50 · (S + δ)`. In both cases the
worker count cancels. **The admission rule therefore cannot by itself produce a
capacity-dependent or concurrency-dependent queue-delay scale, under either the
intended model or the corrected one** — a point §VIII returns to, since one of the
candidate explanations proposed exactly that mechanism. Supplement S1 gives the
admission implementation and the history of the configured-capacity endpoint.

<!-- downstream/main.go queueCapFor(), NewServer(), fullQueueDelayMs() -->

### D. Service-time emulation, and where the error enters

A request that reaches a worker is held for a jittered service time and then
returned. The jitter is a multiplicative Gaussian factor (`σ = 0.15`), clamped
symmetrically at ±0.5 and mean-preserving, so it broadens the latency
distribution without contributing to the discrepancy below.

<!-- downstream/main.go jitteredServiceTime(), serviceTimeJitterSigma -->

The worker's cycle, however, is longer than the service time it emulates.
Each request occupies its worker for the intended interval plus three
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

Taking the **pooled** plateau-inferred `δ` = 0.463 ms — one constant applied
unchanged to all seven cells — `C_model` reproduces `C_measured` for every cell
to within 0.19%, a residual smaller than one boundary-bisection step. **This is
an in-sample common-parameter check, not independent validation:** the pooled
constant was inferred from these seven plateaus, so the check tests whether one
number suffices across the set, not whether the model holds outside it. §V gives
the leave-one-out form and a stronger test: a correction predicted in advance of
the runs that tested it, using constants from a separate instrument.

<!-- results/REVIEWER-RESPONSE-W2.md task 3 -->

### F. What the downstream is not

It is a timing instrument with no persistent state, no I/O and no dependency of
its own, so the numeric value of `δ` is specific to this implementation (§IX);
what carries forward is that a purpose-built service, measured by its author, was
wrong about its own capacity by more than the margin under measurement.
