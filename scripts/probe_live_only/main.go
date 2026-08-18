// Live-only SLO capacity curve (Probe 1). No NATS / no recovery.
// Usage:
//   go run ./scripts/probe_live_only -url http://127.0.0.1:8080 -capacity 2000
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"math"
	"net/http"
	"os"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	url := flag.String("url", "http://127.0.0.1:8080", "")
	capacity := flag.Float64("capacity", 2000, "")
	warmup := flag.Duration("warmup", 30*time.Second, "")
	measure := flag.Duration("measure", 60*time.Second, "")
	out := flag.String("out", "results/probe1-live-only.json", "")
	sloP99 := flag.Float64("slo-p99-ms", 250, "")
	sloErr := flag.Float64("slo-error-rate", 0.01, "")
	ratesCSV := flag.String("rates", "250,500,750,900,1000,1200,1400,1600", "comma-separated offered rates")
	flag.Parse()

	rates, err := parseRates(*ratesCSV)
	if err != nil {
		fatal(err)
	}

	client := &http.Client{
		Timeout: 5 * time.Second,
		Transport: &http.Transport{
			MaxIdleConns: 8192, MaxIdleConnsPerHost: 8192, MaxConnsPerHost: 8192,
		},
	}
	if err := setCapacity(client, *url, *capacity); err != nil {
		fatal(err)
	}
	info := getJSON(client, *url+"/admin/capacity")
	fmt.Printf("capacity=%.0f queueCap=%v concurrency=%v\n", *capacity, info["queueCap"], info["concurrency"])

	var points []map[string]any
	var cSLO float64
	var gAt987 float64

	for _, rate := range rates {
		fmt.Printf("\n=== offered=%.0f warmup=%s measure=%s ===\n", rate, *warmup, *measure)
		_ = setCapacity(client, *url, *capacity)
		time.Sleep(500 * time.Millisecond)

		// Warmup (discard samples)
		flood(client, *url+"/process", rate, *warmup, nil)

		st0 := getJSON(client, *url+"/admin/stats")
		res := flood(client, *url+"/process", rate, *measure, pollQueue(client, *url))
		st1 := getJSON(client, *url+"/admin/stats")

		achieved := float64(res.n) / measure.Seconds()
		good := 0
		for i, lat := range res.lats {
			if res.statuses[i] == 200 && lat <= *sloP99 {
				good++
			}
		}
		goodput := float64(good) / measure.Seconds()
		frac := float64(good) / math.Max(1, float64(res.n))
		toRate := float64(res.timeouts) / math.Max(1, float64(res.n))
		errRate := float64(res.errs) / math.Max(1, float64(res.n))

		pt := map[string]any{
			"offeredRps":       rate,
			"achievedRps":      achieved,
			"n":                res.n,
			"p50Ms":            percentile(res.lats, 0.50),
			"p90Ms":            percentile(res.lats, 0.90),
			"p95Ms":            percentile(res.lats, 0.95),
			"p99Ms":            percentile(res.lats, 0.99),
			"fractionUnderSLO": frac,
			"goodputRps":       goodput,
			"timeoutRate":      toRate,
			"errorRate":        errRate,
			"queueMean":        res.qMean,
			"queuePeak":        res.qPeak,
			"deltaTimedOut":    asInt(st1["timedOut"]) - asInt(st0["timedOut"]),
			"deltaRejected":    asInt(st1["rejected"]) - asInt(st0["rejected"]),
			"sloOK":            percentile(res.lats, 0.99) <= *sloP99 && errRate <= *sloErr,
		}
		points = append(points, pt)
		fmt.Printf("  achieved=%.1f p50=%.0f p90=%.0f p95=%.0f p99=%.0f frac=%.3f gp=%.1f to=%.3f err=%.3f qMean=%.1f qPeak=%d sloOK=%v\n",
			achieved, pt["p50Ms"], pt["p90Ms"], pt["p95Ms"], pt["p99Ms"], frac, goodput, toRate, errRate, res.qMean, res.qPeak, pt["sloOK"])

		if pt["sloOK"].(bool) {
			cSLO = rate
		}
		if rate == 1000 {
			gAt987 = goodput // nearest offered; also interpolate below
		}
	}

	// Goodput at ~987: use 1000 point (closest); also linear interp 900–1000 if both exist
	g987 := gAt987
	var p900, p1000 map[string]any
	for _, p := range points {
		if p["offeredRps"].(float64) == 900 {
			p900 = p
		}
		if p["offeredRps"].(float64) == 1000 {
			p1000 = p
		}
	}
	if p900 != nil && p1000 != nil {
		g987 = p900["goodputRps"].(float64) + (p1000["goodputRps"].(float64)-p900["goodputRps"].(float64))*(987-900)/(1000-900)
	}

	rel := "below"
	if 1000 > cSLO {
		rel = "above"
	} else if 1000 == cSLO {
		rel = "at"
	}

	outDoc := map[string]any{
		"capacity":            *capacity,
		"warmupSec":           warmup.Seconds(),
		"measureSec":          measure.Seconds(),
		"sloP99Ms":            *sloP99,
		"sloErrorRate":        *sloErr,
		"points":              points,
		"C_SLO_live":          cSLO,
		"lambda_L":            1000,
		"lambda_L_vs_C_SLO":   rel,
		"G_SLO_live_only_987": g987,
		"G_SLO_live_only_1000": gAt987,
		"queueCapAtC2000":     info["queueCap"],
		"queueCensoring":      "soft queued counter hard-bounded at queueCap (concurrency×50=500 @C=2000); graceful waits outside queue until timeout — qPeak is censored",
	}
	b, _ := json.MarshalIndent(outDoc, "", "  ")
	if err := os.WriteFile(*out, b, 0o644); err != nil {
		fatal(err)
	}
	fmt.Printf("\n=== SUMMARY ===\n")
	fmt.Printf("C_SLO,live (max offered with p99≤%.0f & err≤%.0f%%) = %.0f rps\n", *sloP99, *sloErr*100, cSLO)
	fmt.Printf("λ_L=1000 is %s C_SLO,live\n", rel)
	fmt.Printf("G_SLO,live-only @987 ≈ %.1f rps (at offered=1000: %.1f)\n", g987, gAt987)
	fmt.Printf("wrote %s\n", *out)
}

type floodResult struct {
	n, errs, timeouts int
	lats              []float64
	statuses          []int
	qMean             float64
	qPeak             int64
}

func pollQueue(client *http.Client, base string) *queuePoller {
	qp := &queuePoller{client: client, base: base}
	qp.stop = make(chan struct{})
	go func() {
		t := time.NewTicker(200 * time.Millisecond)
		defer t.Stop()
		for {
			select {
			case <-qp.stop:
				return
			case <-t.C:
				st := getJSON(client, base+"/admin/stats")
				q := asInt(st["queued"])
				qp.mu.Lock()
				qp.sum += float64(q)
				qp.n++
				if q > qp.peak {
					qp.peak = q
				}
				qp.mu.Unlock()
			}
		}
	}()
	return qp
}

type queuePoller struct {
	client      *http.Client
	base        string
	stop        chan struct{}
	mu          sync.Mutex
	sum         float64
	n           int
	peak        int64
}

func (q *queuePoller) finish() (mean float64, peak int64) {
	close(q.stop)
	time.Sleep(50 * time.Millisecond)
	q.mu.Lock()
	defer q.mu.Unlock()
	if q.n > 0 {
		mean = q.sum / float64(q.n)
	}
	return mean, q.peak
}

func flood(client *http.Client, endpoint string, rate float64, dur time.Duration, qp *queuePoller) floodResult {
	var issued atomic.Int64
	var nFlight atomic.Int64
	const maxInFlight = 4096
	interval := time.Duration(float64(time.Second) / rate)
	if interval < time.Microsecond {
		interval = time.Microsecond
	}
	deadline := time.Now().Add(dur)
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	type sample struct {
		lat float64
		st  int
	}
	var mu sync.Mutex
	var samples []sample
	var wg sync.WaitGroup

	for time.Now().Before(deadline) {
		<-ticker.C
		if nFlight.Load() >= maxInFlight {
			continue
		}
		issued.Add(1)
		nFlight.Add(1)
		wg.Add(1)
		go func() {
			defer wg.Done()
			defer nFlight.Add(-1)
			start := time.Now()
			resp, err := client.Post(endpoint, "text/plain", nil)
			lat := float64(time.Since(start).Milliseconds())
			st := 0
			if err == nil {
				st = resp.StatusCode
				_, _ = io.Copy(io.Discard, resp.Body)
				resp.Body.Close()
			}
			mu.Lock()
			samples = append(samples, sample{lat, st})
			mu.Unlock()
		}()
	}
	wg.Wait()

	res := floodResult{}
	for _, s := range samples {
		res.n++
		res.lats = append(res.lats, s.lat)
		res.statuses = append(res.statuses, s.st)
		if s.st == 504 || s.st == 0 {
			res.timeouts++
		}
		if s.st != 200 && s.st != 429 {
			res.errs++
		}
	}
	if qp != nil {
		res.qMean, res.qPeak = qp.finish()
	}
	return res
}

func percentile(xs []float64, p float64) float64 {
	if len(xs) == 0 {
		return math.NaN()
	}
	cp := append([]float64(nil), xs...)
	sort.Float64s(cp)
	i := int(float64(len(cp)-1) * p)
	return cp[i]
}

func setCapacity(client *http.Client, base string, rate float64) error {
	resp, err := client.Post(fmt.Sprintf("%s/admin/capacity?rate=%.0f", base, rate), "", nil)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	io.Copy(io.Discard, resp.Body)
	return nil
}

func getJSON(client *http.Client, u string) map[string]any {
	resp, err := client.Get(u)
	if err != nil {
		return map[string]any{}
	}
	defer resp.Body.Close()
	var m map[string]any
	_ = json.NewDecoder(resp.Body).Decode(&m)
	return m
}

func asInt(v any) int64 {
	switch x := v.(type) {
	case float64:
		return int64(x)
	case int64:
		return x
	case json.Number:
		i, _ := x.Int64()
		return i
	}
	return 0
}

func parseRates(csv string) ([]float64, error) {
	parts := strings.Split(csv, ",")
	out := make([]float64, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p == "" {
			continue
		}
		f, err := strconv.ParseFloat(p, 64)
		if err != nil {
			return nil, fmt.Errorf("bad rate %q: %w", p, err)
		}
		out = append(out, f)
	}
	if len(out) == 0 {
		return nil, fmt.Errorf("no rates provided")
	}
	return out, nil
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}
