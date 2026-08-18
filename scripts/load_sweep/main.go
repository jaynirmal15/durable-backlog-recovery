// Standalone load sweep against the downstream — no NATS.
// Usage:
//   go run ./downstream &
//   go run ./scripts/load_sweep -url http://127.0.0.1:8080 -capacity 2000
package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"sort"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	url := flag.String("url", "http://127.0.0.1:8080", "downstream base URL")
	capacity := flag.Float64("capacity", 2000, "configured capacity (rps)")
	duration := flag.Duration("duration", 5*time.Second, "duration per load point")
	out := flag.String("out", "results/load_sweep.csv", "CSV output path")
	flag.Parse()

	transport := &http.Transport{
		MaxIdleConns:        10000,
		MaxIdleConnsPerHost: 10000,
		MaxConnsPerHost:     10000,
		IdleConnTimeout:     90 * time.Second,
	}
	client := &http.Client{Timeout: 5 * time.Second, Transport: transport}

	// Confirm health.
	if err := waitHealthy(client, *url, 10*time.Second); err != nil {
		fmt.Fprintf(os.Stderr, "downstream not healthy: %v\n", err)
		os.Exit(1)
	}

	// Reset to nominal capacity.
	if err := setCapacity(client, *url, *capacity); err != nil {
		fmt.Fprintf(os.Stderr, "set capacity: %v\n", err)
		os.Exit(1)
	}

	// Include ≥2× so graceful admission-wait exceeds TIMEOUT_MS and errors appear.
	fractions := []float64{0.20, 0.40, 0.60, 0.80, 0.90, 0.95, 1.00, 1.05, 1.10, 1.25, 1.50, 2.00, 2.50}
	var rows []rowT

	runSweep := func(label string, cap float64) {
		fmt.Printf("\n=== sweep %s capacity=%.0f ===\n", label, cap)
		if err := setCapacity(client, *url, cap); err != nil {
			fmt.Fprintf(os.Stderr, "set capacity: %v\n", err)
			os.Exit(1)
		}
		time.Sleep(500 * time.Millisecond)
		for _, f := range fractions {
			offered := cap * f
			res := flood(client, *url+"/process", offered, *duration)
			r := rowT{
				Label: label, Capacity: cap, OfferedRPS: offered, Util: f,
				P50: res.p50, P95: res.p95, P99: res.p99,
				ErrorRate: res.errRate, N: res.n,
			}
			rows = append(rows, r)
			fmt.Printf("util=%5.0f%% offered=%7.0f  n=%6d  p50=%6.1fms p95=%6.1fms p99=%6.1fms  err=%5.1f%%\n",
				f*100, offered, res.n, res.p50, res.p95, res.p99, res.errRate*100)
		}
	}

	runSweep("nominal", *capacity)
	// Move the knee: drop capacity to 70% and re-sweep.
	runSweep("reduced70", *capacity*0.70)

	if err := writeCSV(*out, rows); err != nil {
		fmt.Fprintf(os.Stderr, "write csv: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("\nwrote %s\n", *out)

	// Gate checks (heuristic).
	nominal := filter(rows, "nominal")
	reduced := filter(rows, "reduced70")
	ok1 := flatBelow(nominal, 0.60, 50)       // p99 < 50ms below 60% util
	ok2 := kneeNearOne(nominal)               // p99 rises sharply near util≈1
	ok3 := errorsAboveSat(nominal)            // errors appear above saturation
	ok4 := kneeMoved(nominal, reduced, *capacity)

	fmt.Println("\n=== VALIDATION GATE ===")
	fmt.Printf("1. flat low latency below capacity: %v\n", ok1)
	fmt.Printf("2. clear knee near util=1:         %v\n", ok2)
	fmt.Printf("3. errors above saturation:        %v\n", ok3)
	fmt.Printf("4. capacity change moves knee:     %v\n", ok4)
	if !(ok1 && ok2 && ok3 && ok4) {
		fmt.Println("GATE FAILED — fix downstream before proceeding")
		os.Exit(2)
	}
	fmt.Println("GATE PASSED")
}

type sweepResult struct {
	p50, p95, p99 float64
	errRate       float64
	n             int
}

func flood(client *http.Client, url string, rps float64, dur time.Duration) sweepResult {
	if rps < 1 {
		rps = 1
	}

	var latMu sync.Mutex
	var lats []float64
	var okN, errN atomic.Int64
	var inFlight atomic.Int64
	var wg sync.WaitGroup

	// Open-loop: fire at target RPS regardless of completion. Cap in-flight so a
	// saturated queue cannot unbounded-grow the client.
	const maxInFlight = 8000
	stopAt := time.Now().Add(dur)
	interval := time.Duration(float64(time.Second) / rps)
	if interval < time.Microsecond {
		interval = time.Microsecond
	}
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for time.Now().Before(stopAt) {
		<-ticker.C
		if inFlight.Load() >= maxInFlight {
			errN.Add(1) // count as overload / dropped offer
			continue
		}
		inFlight.Add(1)
		wg.Add(1)
		go func() {
			defer wg.Done()
			defer inFlight.Add(-1)
			start := time.Now()
			resp, err := client.Post(url, "text/plain", nil)
			elapsed := time.Since(start).Seconds() * 1000
			if err != nil {
				errN.Add(1)
				return
			}
			_, _ = io.Copy(io.Discard, resp.Body)
			resp.Body.Close()
			if resp.StatusCode != 200 {
				errN.Add(1)
				return
			}
			okN.Add(1)
			latMu.Lock()
			lats = append(lats, elapsed)
			latMu.Unlock()
		}()
	}
	wg.Wait()

	total := okN.Load() + errN.Load()
	sort.Float64s(lats)
	return sweepResult{
		p50:     pct(lats, 0.50),
		p95:     pct(lats, 0.95),
		p99:     pct(lats, 0.99),
		errRate: float64(errN.Load()) / max1(float64(total)),
		n:       int(total),
	}
}

func pct(xs []float64, p float64) float64 {
	if len(xs) == 0 {
		return 0
	}
	i := int(float64(len(xs)-1) * p)
	return xs[i]
}

func max1(x float64) float64 {
	if x < 1 {
		return 1
	}
	return x
}

func setCapacity(client *http.Client, base string, rate float64) error {
	resp, err := client.Post(fmt.Sprintf("%s/admin/capacity?rate=%.0f", base, rate), "", nil)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		b, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("status %d: %s", resp.StatusCode, b)
	}
	var info map[string]any
	return json.NewDecoder(resp.Body).Decode(&info)
}

func waitHealthy(client *http.Client, base string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		resp, err := client.Get(base + "/healthz")
		if err == nil {
			resp.Body.Close()
			if resp.StatusCode == 200 {
				return nil
			}
		}
		time.Sleep(200 * time.Millisecond)
	}
	return fmt.Errorf("timeout waiting for healthz")
}

type rowT struct {
	Label      string
	Capacity   float64
	OfferedRPS float64
	Util       float64
	P50        float64
	P95        float64
	P99        float64
	ErrorRate  float64
	N          int
}

func filter(rows []rowT, label string) []rowT {
	var out []rowT
	for _, r := range rows {
		if r.Label == label {
			out = append(out, r)
		}
	}
	return out
}

func flatBelow(rows []rowT, maxUtil, maxP99 float64) bool {
	for _, r := range rows {
		if r.Util <= maxUtil && r.P99 > maxP99 {
			return false
		}
	}
	return len(rows) > 0
}

func kneeNearOne(rows []rowT) bool {
	var low, high float64
	for _, r := range rows {
		if r.Util <= 0.80 {
			if r.P99 > low {
				low = r.P99
			}
		}
		if r.Util >= 1.10 {
			if r.P99 > high {
				high = r.P99
			}
		}
	}
	// Knee: latency at >110% util should be >> latency at ≤80%.
	return high > low*3 && high > 20
}

func errorsAboveSat(rows []rowT) bool {
	// Graceful profile: in-queue wait maxes around 50×serviceTime (~250ms), so
	// timeouts need sustained overload hard enough for admission wait > TIMEOUT.
	for _, r := range rows {
		if r.Util >= 2.00 && r.ErrorRate > 0.01 {
			return true
		}
	}
	return false
}

func kneeMoved(nominal, reduced []rowT, nominalCap float64) bool {
	// At offered ≈ 0.85 * nominalCap: should be healthy at nominal, degraded at reduced70.
	target := nominalCap * 0.85
	n := nearest(nominal, target)
	r := nearest(reduced, target)
	if n.N == 0 || r.N == 0 {
		return false
	}
	// Reduced capacity should show higher p99 or errors at same absolute offered load.
	return r.P99 > n.P99*1.5 || r.ErrorRate > n.ErrorRate+0.05
}

func nearest(rows []rowT, offered float64) rowT {
	var best rowT
	bestDelta := 1e18
	for _, r := range rows {
		d := r.OfferedRPS - offered
		if d < 0 {
			d = -d
		}
		if d < bestDelta {
			bestDelta = d
			best = r
		}
	}
	return best
}

func writeCSV(path string, rows []rowT) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	_ = w.Write([]string{"label", "capacity", "offered_rps", "util", "p50_ms", "p95_ms", "p99_ms", "error_rate", "n"})
	for _, r := range rows {
		_ = w.Write([]string{
			r.Label,
			fmt.Sprintf("%.0f", r.Capacity),
			fmt.Sprintf("%.1f", r.OfferedRPS),
			fmt.Sprintf("%.2f", r.Util),
			fmt.Sprintf("%.2f", r.P50),
			fmt.Sprintf("%.2f", r.P95),
			fmt.Sprintf("%.2f", r.P99),
			fmt.Sprintf("%.4f", r.ErrorRate),
			fmt.Sprintf("%d", r.N),
		})
	}
	w.Flush()
	return w.Error()
}
