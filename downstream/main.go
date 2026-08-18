package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"sync"
	"sync/atomic"
	"time"
)

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
	queueCap  atomic.Int64
	queue     chan *job
	targetW   atomic.Int64 // desired worker count
	liveW     atomic.Int64 // running workers
	workerWG  sync.WaitGroup
	stopAll   chan struct{}
	stats     stats
	rngMu     sync.Mutex
	rng       *rand.Rand
}

func concurrencyFor(capacity float64, serviceTime time.Duration) int {
	c := int(math.Ceil(capacity * serviceTime.Seconds()))
	if c < 1 {
		c = 1
	}
	return c
}

func queueCapFor(profile string, concurrency int) int {
	switch profile {
	case "cliff":
		return concurrency * 2
	default:
		return concurrency * 50
	}
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
		stopAll:     make(chan struct{}),
		rng:         rand.New(rand.NewSource(time.Now().UnixNano())),
	}
	s.queueCap.Store(int64(queueCapFor(profile, conc)))
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
		select {
		case <-s.stopAll:
			s.liveW.Add(-1)
			return
		case j, ok := <-s.queue:
			if !ok {
				s.liveW.Add(-1)
				return
			}
			s.handleJob(j)
		case <-idle.C:
			// re-check shrink
		}
	}
}

func (s *Server) handleJob(j *job) {
	s.stats.queued.Add(-1)
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
	time.Sleep(st)
	s.stats.served.Add(1)
	j.done <- http.StatusOK
}

func (s *Server) jitteredServiceTime() time.Duration {
	s.rngMu.Lock()
	base := s.serviceTime
	j := s.rng.NormFloat64() * 0.15
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
	s.targetW.Store(int64(conc))
	s.ensureWorkers()
	log.Printf("capacity=%.0f rps concurrency=%d queueCap=%d (liveWorkers≈%d)",
		rate, conc, s.queueCap.Load(), s.liveW.Load())
}

func (s *Server) CapacityInfo() map[string]any {
	s.mu.Lock()
	cap := s.capacity
	profile := s.profile
	st := s.serviceTime
	to := s.timeout
	s.mu.Unlock()
	return map[string]any{
		"trueCapacity":  cap,
		"concurrency":   s.targetW.Load(),
		"liveWorkers":   s.liveW.Load(),
		"queueCap":      s.queueCap.Load(),
		"profile":       profile,
		"serviceTimeMs": st.Milliseconds(),
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

func (s *Server) Process(w http.ResponseWriter, r *http.Request) {
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
		deadline := time.Now().Add(timeout)
		for {
			if s.softLen() < qCap {
				select {
				case s.queue <- j:
					s.stats.queued.Add(1)
					goto enqueued
				default:
					// channel physically full — brief yield
				}
			}
			if time.Now().After(deadline) {
				s.stats.timedOut.Add(1)
				http.Error(w, "timeout waiting for queue", http.StatusGatewayTimeout)
				return
			}
			select {
			case <-r.Context().Done():
				s.stats.timedOut.Add(1)
				http.Error(w, "client gone", http.StatusGatewayTimeout)
				return
			case <-time.After(100 * time.Microsecond):
			}
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
	serviceTime := time.Duration(envInt("SERVICE_TIME_MS", 5)) * time.Millisecond
	timeout := time.Duration(envInt("TIMEOUT_MS", 2000)) * time.Millisecond
	profile := envStr("PROFILE", "graceful")
	port := envInt("PORT", 8080)

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
	mux.HandleFunc("/admin/capacity", s.AdminCapacity)
	mux.HandleFunc("/admin/stats", s.AdminStats)
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})

	addr := fmt.Sprintf(":%d", port)
	srv := &http.Server{Addr: addr, Handler: mux}
	log.Printf("downstream listening on %s", addr)
	log.Fatal(srv.ListenAndServe())
}
