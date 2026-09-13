// The 2026-08-19 changes in this file were reconstructed from the 2026-08-19 session log; original was never committed.
// See RECONSTRUCTION.md.

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"sort"
	"strconv"
	"sync"
	"sync/atomic"
	"time"
)

func envFloat(key string, def float64) float64 {
	if v := os.Getenv(key); v != "" {
		if f, err := strconv.ParseFloat(v, 64); err == nil {
			return f
		}
		log.Fatalf("invalid %s=%q: want a number", key, v)
	}
	return def
}

func envInt(key string, def int) int {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		log.Fatalf("invalid %s=%q: %v", key, v, err)
	}
	return n
}

func envStr(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

type job struct {
	enqueuedAt time.Time
	done       chan int // HTTP status
}

type stats struct {
	queued   atomic.Int64
	served   atomic.Int64
	rejected atomic.Int64
	timedOut atomic.Int64
}

type Server struct {
	mu          sync.Mutex
	capacity    float64
	serviceTime time.Duration
	timeout     time.Duration
	profile     string

	// Soft admission limit (profile × concurrency). Channel itself is sized once
	// at startup large enough for the initial profile; we never close/rebuild it
	// on capacity changes — that wedged the process under load during P0-B.
	queueCap atomic.Int64
	// Admission semaphore. Waiting requests PARK on a channel receive and are
	// woken one-per-release. The previous graceful path spun on
	// time.After(100us) per waiter, which allocated tens of millions of timers
	// per second under load, saturated the host, starved the worker pool, and
	// manufactured congestion collapse (see NOTES.md, 2026-08-19).
	slots    chan struct{}
	slotCap  atomic.Int64
	slotMu   sync.Mutex
	queue    chan *job
	targetW  atomic.Int64 // desired worker count
	liveW    atomic.Int64 // running workers
	workerWG sync.WaitGroup
	stopAll  chan struct{}
	stats    stats
	rngMu    sync.Mutex
	rng      *rand.Rand
}

func concurrencyFor(capacity float64, serviceTime time.Duration) int {
	c := int(math.Ceil(capacity * serviceTime.Seconds()))
	if c < 1 {
		c = 1
	}
	return c
}

// queueCapOverride is QUEUE_CAP: a fixed admission limit in requests,
// independent of concurrency. 0 (the default) keeps the historical
// profile-relative behaviour.
//
// Why this exists: with the profile-relative cap, graceful's full-queue delay is
// 50 x concurrency / (concurrency / S) = 50 x S, which is 250 ms at S=5 ms --
// exactly the SLO -- and 1250 ms at S=25 ms. "Queue full" is therefore
// definitionally "SLO breach" in the c10 arm and not in the c50 arm, which is a
// competing explanation for the concurrency effect that has nothing to do with
// concurrency. Holding the cap fixed across arms separates the two.
var queueCapOverride int

func queueCapFor(profile string, concurrency int) int {
	if queueCapOverride > 0 {
		return queueCapOverride
	}
	switch profile {
	case "cliff":
		return concurrency * 2
	default:
		return concurrency * 50
	}
}

// fullQueueDelayMs is the wait a request faces when it is admitted to a full
// queue: cap / service rate, where the service rate is concurrency / S. This is
// the quantity that coincides with the SLO under the default cap at S=5 ms.
func fullQueueDelayMs(queueCap, concurrency int, serviceTime time.Duration) float64 {
	if concurrency <= 0 || serviceTime <= 0 {
		return 0
	}
	serviceRate := float64(concurrency) / serviceTime.Seconds()
	if serviceRate <= 0 {
		return 0
	}
	return float64(queueCap) / serviceRate * 1000.0
}

// resizeSlots adjusts the number of admission tokens in flight. Shrinking only
// reclaims tokens that are currently free; held tokens drain naturally as their
// requests complete.
func (s *Server) resizeSlots(newCap int) {
	s.slotMu.Lock()
	defer s.slotMu.Unlock()
	cur := int(s.slotCap.Load())
	for i := cur; i < newCap; i++ {
		select {
		case s.slots <- struct{}{}:
		default:
		}
	}
	for i := newCap; i < cur; i++ {
		select {
		case <-s.slots:
		default:
		}
	}
	s.slotCap.Store(int64(newCap))
}

func NewServer(capacity float64, serviceTime, timeout time.Duration, profile string) *Server {
	conc := concurrencyFor(capacity, serviceTime)
	// Channel capacity: allow headroom above initial soft cap so later capacity
	// increases don't require rebuilding the channel.
	chCap := queueCapFor(profile, conc) * 4
	if chCap < 1024 {
		chCap = 1024
	}
	s := &Server{
		capacity:    capacity,
		serviceTime: serviceTime,
		timeout:     timeout,
		profile:     profile,
		queue:       make(chan *job, chCap),
		slots:       make(chan struct{}, 65536),
		stopAll:     make(chan struct{}),
		rng:         rand.New(rand.NewSource(time.Now().UnixNano())),
	}
	s.queueCap.Store(int64(queueCapFor(profile, conc)))
	s.resizeSlots(queueCapFor(profile, conc))
	s.targetW.Store(int64(conc))
	s.ensureWorkers()
	log.Printf("capacity=%.0f rps concurrency=%d queueCap=%d profile=%s serviceTime=%s timeout=%s",
		capacity, conc, s.queueCap.Load(), profile, serviceTime, timeout)
	return s
}

func (s *Server) ensureWorkers() {
	for {
		live := s.liveW.Load()
		target := s.targetW.Load()
		if live >= target {
			return
		}
		if s.liveW.CompareAndSwap(live, live+1) {
			s.workerWG.Add(1)
			go s.worker()
		}
	}
}

func (s *Server) worker() {
	defer s.workerWG.Done()
	idle := time.NewTimer(50 * time.Millisecond)
	defer idle.Stop()
	for {
		var tTop time.Time
		if overheadProbe {
			tTop = time.Now()
		}
		live := s.liveW.Load()
		target := s.targetW.Load()
		if live > target && s.liveW.CompareAndSwap(live, live-1) {
			return // shrink
		}
		if !idle.Stop() {
			select {
			case <-idle.C:
			default:
			}
		}
		idle.Reset(50 * time.Millisecond)
		var tAfterTimer time.Time
		if overheadProbe {
			tAfterTimer = time.Now()
		}
		select {
		case <-s.stopAll:
			s.liveW.Add(-1)
			return
		case j, ok := <-s.queue:
			if !ok {
				s.liveW.Add(-1)
				return
			}
			// Charged only when a job was actually received: an idle worker pays
			// the timer cost too, but that is not a per-request cost.
			if overheadProbe {
				ovTimer.add(tAfterTimer.Sub(tTop).Nanoseconds())
			}
			s.handleJob(j)
		case <-idle.C:
			// re-check shrink
		}
	}
}

// ---------------------------------------------------------------- overhead probe
//
// E2e experiment 1. OFF unless OVERHEAD_PROBE=1, in which case it records where
// a worker's per-request time goes beyond the sleep it was asked to perform.
// That excess is what makes true capacity fall short of `concurrency / S`, so it
// is measured on the worker path only: HTTP handling runs on the request
// goroutine, consumes no worker time, and cannot reduce capacity.
var overheadProbe = false

type ovStat struct {
	sum   atomic.Int64 // nanoseconds
	count atomic.Int64
	max   atomic.Int64
}

func (o *ovStat) add(ns int64) {
	o.sum.Add(ns)
	o.count.Add(1)
	for {
		m := o.max.Load()
		if ns <= m || o.max.CompareAndSwap(m, ns) {
			return
		}
	}
}

func (o *ovStat) report() map[string]any {
	n := o.count.Load()
	if n == 0 {
		return map[string]any{"count": 0}
	}
	return map[string]any{
		"count":  n,
		"meanNs": o.sum.Load() / n,
		"maxNs":  o.max.Load(),
	}
}

var (
	ovTimer, ovPreSleep, ovSleepExcess, ovPostSleep, ovTotal ovStat
	// Percentiles need samples. Written lock-free: each index is claimed once
	// by an atomic increment and written exactly once, and reads happen only
	// from /admin/overhead after the load has stopped.
	ovSampIdx   atomic.Int64
	ovSampSleep []int64
	ovSampTotal []int64
)

func ovSample(sleepExcess, total int64) {
	i := ovSampIdx.Add(1) - 1
	if i >= 0 && int(i) < len(ovSampTotal) {
		ovSampSleep[i] = sleepExcess
		ovSampTotal[i] = total
	}
}

func ovPct(v []int64, q float64) int64 {
	if len(v) == 0 {
		return 0
	}
	c := append([]int64(nil), v...)
	sort.Slice(c, func(a, b int) bool { return c[a] < c[b] })
	i := int(q * float64(len(c)-1))
	return c[i]
}

func overheadReport() map[string]any {
	n := int(ovSampIdx.Load())
	if n > len(ovSampTotal) {
		n = len(ovSampTotal)
	}
	sleep, total := ovSampSleep[:n], ovSampTotal[:n]
	out := map[string]any{
		"enabled":     overheadProbe,
		"samples":     n,
		"timer":       ovTimer.report(),
		"preSleep":    ovPreSleep.report(),
		"sleepExcess": ovSleepExcess.report(),
		"postSleep":   ovPostSleep.report(),
		"total":       ovTotal.report(),
		"note": "total = timer + preSleep + sleepExcess + postSleep, the worker-side " +
			"cost per request beyond the sleep it was asked to perform. HTTP handling " +
			"is excluded: it does not run on a worker and cannot reduce capacity.",
	}
	for name, v := range map[string][]int64{"sleepExcess": sleep, "total": total} {
		out[name+"Pct"] = map[string]any{
			"p50Ns": ovPct(v, 0.50), "p90Ns": ovPct(v, 0.90),
			"p99Ns": ovPct(v, 0.99), "p999Ns": ovPct(v, 0.999),
		}
	}
	return out
}

func (s *Server) handleJob(j *job) {
	var tRecv time.Time
	if overheadProbe {
		tRecv = time.Now()
	}
	s.stats.queued.Add(-1)
	// Release the admission token as soon as the job leaves the queue, waking
	// exactly one waiter.
	select {
	case s.slots <- struct{}{}:
	default:
	}
	waited := time.Since(j.enqueuedAt)
	timeout := s.timeout
	if waited >= timeout {
		s.stats.timedOut.Add(1)
		j.done <- http.StatusGatewayTimeout
		return
	}
	budget := timeout - waited
	st := s.jitteredServiceTime()
	if st > budget {
		time.Sleep(budget)
		s.stats.timedOut.Add(1)
		j.done <- http.StatusGatewayTimeout
		return
	}
	if !overheadProbe {
		time.Sleep(st)
		s.stats.served.Add(1)
		j.done <- http.StatusOK
		return
	}
	tSleep0 := time.Now()
	time.Sleep(st)
	tSleep1 := time.Now()
	s.stats.served.Add(1)
	j.done <- http.StatusOK
	tDone := time.Now()
	pre := tSleep0.Sub(tRecv).Nanoseconds()
	excess := tSleep1.Sub(tSleep0).Nanoseconds() - st.Nanoseconds()
	post := tDone.Sub(tSleep1).Nanoseconds()
	ovPreSleep.add(pre)
	ovSleepExcess.add(excess)
	ovPostSleep.add(post)
	ovTotal.add(pre + excess + post)
	ovSample(excess, pre+excess+post)
}

// serviceTimeJitterSigma is SERVICE_TIME_JITTER: the standard deviation of the
// per-request service-time multiplier, as a fraction of the mean. 0 makes the
// dependency deterministic. The default 0.15 is the value every Phase 0/1 run
// used, so leaving it unset reproduces those runs exactly.
//
// It was a hardcoded constant until 2026-09-11 and appeared in no run record,
// which meant the arrival-process-versus-service-process question could not be
// asked of the existing data at all.
var serviceTimeJitterSigma = 0.15

func (s *Server) jitteredServiceTime() time.Duration {
	if serviceTimeJitterSigma <= 0 {
		return s.serviceTime
	}
	s.rngMu.Lock()
	base := s.serviceTime
	j := s.rng.NormFloat64() * serviceTimeJitterSigma
	s.rngMu.Unlock()
	if j < -0.5 {
		j = -0.5
	}
	if j > 0.5 {
		j = 0.5
	}
	return time.Duration(float64(base) * (1 + j))
}

// SetCapacity resizes the worker pool in place. Never closes the request queue.
func (s *Server) SetCapacity(rate float64) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if rate < 1 {
		rate = 1
	}
	s.capacity = rate
	conc := concurrencyFor(rate, s.serviceTime)
	s.queueCap.Store(int64(queueCapFor(s.profile, conc)))
	s.resizeSlots(queueCapFor(s.profile, conc))
	s.targetW.Store(int64(conc))
	s.ensureWorkers()
	log.Printf("capacity=%.0f rps concurrency=%d queueCap=%d (liveWorkers≈%d)",
		rate, conc, s.queueCap.Load(), s.liveW.Load())
}

// queueCapMode records how the cap was chosen, so a run record shows whether
// QUEUE_CAP was in force rather than leaving it to be inferred.
func queueCapMode() string {
	if queueCapOverride > 0 {
		return "fixed"
	}
	return "profile_relative"
}

func (s *Server) CapacityInfo() map[string]any {
	s.mu.Lock()
	cap := s.capacity
	profile := s.profile
	st := s.serviceTime
	to := s.timeout
	s.mu.Unlock()
	return map[string]any{
		"trueCapacity":           cap,
		"concurrency":            s.targetW.Load(),
		"liveWorkers":            s.liveW.Load(),
		"queueCap":               s.queueCap.Load(),
		"queueCapMode":           queueCapMode(),
		"serviceTimeJitterSigma": serviceTimeJitterSigma,
		"serviceTimeJitterClamp": 0.5,
		"fullQueueDelayMs": math.Round(fullQueueDelayMs(
			int(s.queueCap.Load()), int(s.targetW.Load()), st)*10) / 10,
		"profile":       profile,
		"serviceTimeMs": st.Milliseconds(),
		"serviceTimeUs": st.Microseconds(),
		"timeoutMs":     to.Milliseconds(),
	}
}

func (s *Server) Stats() map[string]any {
	s.mu.Lock()
	cap := s.capacity
	s.mu.Unlock()
	return map[string]any{
		"queued":       s.stats.queued.Load(),
		"served":       s.stats.served.Load(),
		"rejected":     s.stats.rejected.Load(),
		"timedOut":     s.stats.timedOut.Load(),
		"trueCapacity": cap,
		"concurrency":  s.targetW.Load(),
		"queueCap":     s.queueCap.Load(),
	}
}

func (s *Server) softLen() int {
	return int(s.stats.queued.Load())
}

// arrivalLog optionally records the nanosecond arrival time of every request.
//
// It measures the arrival PROCESS as the dependency actually experiences it,
// which is the thing queueing behaviour depends on -- not the generator's mean
// rate, which is all the delivery guard checks. Two pacers can agree on rate to
// four figures and present completely different processes.
//
// Off unless ARRIVAL_LOG_CAP is set, and a plain atomic bump plus one slice
// append when on. The per-request sample stream is millisecond-resolution, which
// cannot resolve inter-arrival times at 1000 rps; this can.
type arrivalLog struct {
	mu  sync.Mutex
	ns  []int64
	cap int
	on  bool
}

func (a *arrivalLog) record() {
	if !a.on {
		return
	}
	now := time.Now().UnixNano()
	a.mu.Lock()
	if len(a.ns) < a.cap {
		a.ns = append(a.ns, now)
	}
	a.mu.Unlock()
}

// drain returns everything captured so far and resets, so a probe can mark off
// windows without restarting the server.
func (a *arrivalLog) drain() []int64 {
	a.mu.Lock()
	defer a.mu.Unlock()
	out := a.ns
	a.ns = make([]int64, 0, a.cap)
	return out
}

var arrivals = &arrivalLog{}

func (s *Server) AdminArrivals(w http.ResponseWriter, r *http.Request) {
	got := arrivals.drain()
	writeJSON(w, map[string]any{
		"enabled":      arrivals.on,
		"count":        len(got),
		"capacity":     arrivals.cap,
		"arrivalNanos": got,
	})
}

func (s *Server) Process(w http.ResponseWriter, r *http.Request) {
	arrivals.record()
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	j := &job{
		enqueuedAt: time.Now(),
		done:       make(chan int, 1),
	}

	s.mu.Lock()
	profile := s.profile
	timeout := s.timeout
	s.mu.Unlock()
	qCap := int(s.queueCap.Load())

	if profile == "cliff" {
		if s.softLen() >= qCap {
			s.stats.rejected.Add(1)
			http.Error(w, "queue full", http.StatusServiceUnavailable)
			return
		}
		select {
		case s.queue <- j:
			s.stats.queued.Add(1)
		default:
			s.stats.rejected.Add(1)
			http.Error(w, "queue full", http.StatusServiceUnavailable)
			return
		}
	} else {
		// Graceful admission: BLOCK on the semaphore. A waiting request parks on
		// a channel receive and is woken when a worker frees a slot — it costs
		// no CPU while waiting. One timer per request, not one per 100us per
		// request. Replaces a spin-wait that manufactured congestion collapse
		// (NOTES.md 2026-08-19: 1216% CPU and served/s falling 1837 -> 1463 at
		// offered 1950, versus ~100% and no collapse with the same load under
		// PROFILE=cliff).
		t := time.NewTimer(timeout)
		select {
		case <-s.slots:
			t.Stop()
		case <-t.C:
			s.stats.timedOut.Add(1)
			http.Error(w, "timeout waiting for queue", http.StatusGatewayTimeout)
			return
		case <-r.Context().Done():
			t.Stop()
			s.stats.timedOut.Add(1)
			http.Error(w, "client gone", http.StatusGatewayTimeout)
			return
		}
		// Token held => a queue slot is reserved for this request.
		select {
		case s.queue <- j:
			s.stats.queued.Add(1)
			goto enqueued
		default:
			// Physically full despite holding a token (only reachable if the
			// soft cap was raised past the channel). Return the token.
			select {
			case s.slots <- struct{}{}:
			default:
			}
			s.stats.timedOut.Add(1)
			http.Error(w, "queue full", http.StatusGatewayTimeout)
			return
		}
	}

enqueued:
	select {
	case status := <-j.done:
		w.WriteHeader(status)
		if status == http.StatusOK {
			_, _ = w.Write([]byte("ok"))
		} else {
			_, _ = w.Write([]byte("timeout"))
		}
	case <-time.After(timeout + 100*time.Millisecond):
		s.stats.timedOut.Add(1)
		http.Error(w, "timeout", http.StatusGatewayTimeout)
	case <-r.Context().Done():
		s.stats.timedOut.Add(1)
		return
	}
}

func (s *Server) AdminCapacity(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		writeJSON(w, s.CapacityInfo())
	case http.MethodPost:
		rateStr := r.URL.Query().Get("rate")
		if rateStr == "" {
			http.Error(w, "missing rate", http.StatusBadRequest)
			return
		}
		rate, err := strconv.ParseFloat(rateStr, 64)
		if err != nil || rate <= 0 {
			http.Error(w, "invalid rate", http.StatusBadRequest)
			return
		}
		s.SetCapacity(rate)
		writeJSON(w, s.CapacityInfo())
	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}

func (s *Server) AdminStats(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	writeJSON(w, s.Stats())
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	enc := json.NewEncoder(w)
	enc.SetIndent("", "  ")
	_ = enc.Encode(v)
}

func main() {
	capacity := float64(envInt("CAPACITY", 2000))
	// SERVICE_TIME_US takes precedence when set: E2e needs a sub-millisecond
	// correction (4537 us) that SERVICE_TIME_MS cannot express. Unset, behaviour
	// is exactly as before.
	serviceTime := time.Duration(envInt("SERVICE_TIME_MS", 5)) * time.Millisecond
	if us := envInt("SERVICE_TIME_US", 0); us > 0 {
		serviceTime = time.Duration(us) * time.Microsecond
	}
	timeout := time.Duration(envInt("TIMEOUT_MS", 2000)) * time.Millisecond
	profile := envStr("PROFILE", "graceful")
	port := envInt("PORT", 8080)
	queueCapOverride = envInt("QUEUE_CAP", 0)
	serviceTimeJitterSigma = envFloat("SERVICE_TIME_JITTER", 0.15)
	if envInt("OVERHEAD_PROBE", 0) > 0 {
		overheadProbe = true
		n := envInt("OVERHEAD_SAMPLES", 200000)
		ovSampSleep = make([]int64, n)
		ovSampTotal = make([]int64, n)
		log.Printf("overhead probe ON, %d sample slots", n)
	}
	// Arrival-process capture. 0 (default) leaves it off entirely.
	if n := envInt("ARRIVAL_LOG_CAP", 0); n > 0 {
		arrivals.cap = n
		arrivals.ns = make([]int64, 0, n)
		arrivals.on = true
		log.Printf("arrival log ENABLED, capacity %d timestamps", n)
	}

	if profile != "graceful" && profile != "cliff" {
		log.Fatalf("PROFILE must be graceful or cliff, got %q", profile)
	}

	s := NewServer(capacity, serviceTime, timeout, profile)

	mux := http.NewServeMux()
	mux.HandleFunc("/process", s.Process)
	mux.HandleFunc("/noop", func(w http.ResponseWriter, r *http.Request) {
		// Trivial 200 for injector ceiling tests — no queue, no service time.
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})
	mux.HandleFunc("/admin/arrivals", s.AdminArrivals)
	mux.HandleFunc("/admin/capacity", s.AdminCapacity)
	mux.HandleFunc("/admin/stats", s.AdminStats)
	mux.HandleFunc("/admin/overhead", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, overheadReport())
	})
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})

	addr := fmt.Sprintf(":%d", port)
	srv := &http.Server{Addr: addr, Handler: mux}
	log.Printf("downstream listening on %s", addr)
	log.Fatal(srv.ListenAndServe())
}
