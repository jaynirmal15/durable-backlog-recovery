// This file was reconstructed from session transcript 2026-08-19; original was never committed.
// See RECONSTRUCTION.md.

// Hysteresis probe: does backing off to a previously-safe rate restore health?
//
// Drives a CONTINUOUS stepped load profile with no gap between steps and no
// capacity reset, so a collapsed state persists into the next step. The
// live-only sweeps could not answer this: they warm up afresh per point, which
// lets the queue drain between rates.
//
//	go run ./scripts/hysteresis -url http://127.0.0.1:8080 -capacity 2000 \
//	  -profile 1850:30,1950:60,1900:45,1850:45,1800:45,1750:45,1700:45
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

type stepResult struct {
	Rate         float64 `json:"rate"`
	StartSec     int     `json:"startSec"`
	EndSec       int     `json:"endSec"`
	P50          float64 `json:"p50Ms"`
	P95          float64 `json:"p95Ms"`
	P99          float64 `json:"p99Ms"`
	FracUnderSLO float64 `json:"fractionUnderSLO"`
	AchievedRps  float64 `json:"achievedRps"`
	QMean        float64 `json:"queueMean"`
	Healthy      bool    `json:"healthy"`
}

type step struct {
	Rate float64
	Sec  int
}

type secBucket struct {
	mu    sync.Mutex
	lats  []float64
	codes map[int]int
}

func main() {
	url := flag.String("url", "http://127.0.0.1:8080", "")
	capacity := flag.Float64("capacity", 2000, "")
	profileCSV := flag.String("profile", "1850:30,1950:60,1900:45,1850:45,1800:45,1750:45,1700:45", "rate:seconds,...")
	sloP99 := flag.Float64("slo-p99-ms", 250, "")
	out := flag.String("out", "results/hysteresis.json", "")
	flag.Parse()

	steps := parseProfile(*profileCSV)
	maxRate := 0.0
	total := 0
	for _, s := range steps {
		if s.Rate > maxRate {
			maxRate = s.Rate
		}
		total += s.Sec
	}

	client := &http.Client{Timeout: 10 * time.Second, Transport: &http.Transport{
		MaxIdleConns: 8192, MaxIdleConnsPerHost: 8192, MaxConnsPerHost: 8192}}
	setCapacity(client, *url, *capacity)
	info := getJSON(client, *url+"/admin/capacity")
	fmt.Printf("capacity=%.0f concurrency=%v serviceTimeMs=%v  profile=%s (%ds)\n",
		*capacity, info["concurrency"], info["serviceTimeMs"], *profileCSV, total)

	lanes := int(math.Ceil(maxRate / 200.0))
	if lanes < 1 {
		lanes = 1
	}
	var laneIntervalNs atomic.Int64
	laneIntervalNs.Store(int64(float64(lanes) * float64(time.Second) / steps[0].Rate))

	buckets := make([]*secBucket, total+2)
	for i := range buckets {
		buckets[i] = &secBucket{codes: map[int]int{}}
	}
	queued := make([]int64, total+2)
	servedPS := make([]int64, total+2)
	timedOutPS := make([]int64, total+2)

	var nFlight atomic.Int64
	var issued atomic.Int64
	const maxInFlight = 8192
	done := make(chan struct{})
	t0 := time.Now()
	var wg sync.WaitGroup

	// per-second queue sampler
	var prevServed, prevTimedOut int64
	go func() {
		t := time.NewTicker(time.Second)
		defer t.Stop()
		for {
			select {
			case <-done:
				return
			case <-t.C:
				sec := int(time.Since(t0).Seconds())
				st := getJSON(client, *url+"/admin/stats")
				sv, to := asInt(st["served"]), asInt(st["timedOut"])
				if sec >= 0 && sec < len(queued) {
					queued[sec] = asInt(st["queued"])
					// per-second deltas separate USEFUL service from timeouts:
					// if served/s stays near capacity during collapse the pool is
					// fine and admission is merely unfair; if it drops, effective
					// capacity itself degraded.
					servedPS[sec] = sv - prevServed
					timedOutPS[sec] = to - prevTimedOut
				}
				prevServed, prevTimedOut = sv, to
			}
		}
	}()

	for L := 0; L < lanes; L++ {
		wg.Add(1)
		go func(L int) {
			defer wg.Done()
			time.Sleep(time.Duration(int64(L) * laneIntervalNs.Load() / int64(lanes)))
			next := time.Now()
			for {
				li := time.Duration(laneIntervalNs.Load())
				next = next.Add(li)
				// Bounded catch-up: never discharge missed slots as a burst.
				if time.Since(next) > li {
					next = time.Now()
				}
				if d := time.Until(next); d > 0 {
					time.Sleep(d)
				}
				select {
				case <-done:
					return
				default:
				}
				if nFlight.Load() >= maxInFlight {
					continue
				}
				issued.Add(1)
				nFlight.Add(1)
				go func() {
					defer nFlight.Add(-1)
					st := time.Now()
					resp, err := client.Post(*url+"/process", "text/plain", nil)
					lat := float64(time.Since(st).Milliseconds())
					code := 0
					if err == nil {
						code = resp.StatusCode
						_, _ = io.Copy(io.Discard, resp.Body)
						resp.Body.Close()
					}
					sec := int(time.Since(t0).Seconds())
					if sec >= 0 && sec < len(buckets) {
						b := buckets[sec]
						b.mu.Lock()
						b.lats = append(b.lats, lat)
						b.codes[code]++
						b.mu.Unlock()
					}
				}()
			}
		}(L)
	}

	// walk the profile
	var results []stepResult
	elapsed := 0
	for _, sp := range steps {
		laneIntervalNs.Store(int64(float64(lanes) * float64(time.Second) / sp.Rate))
		fmt.Printf("\n--- offered=%.0f for %ds (t=%d..%d) ---\n", sp.Rate, sp.Sec, elapsed, elapsed+sp.Sec)
		time.Sleep(time.Duration(sp.Sec) * time.Second)
		st, en := elapsed, elapsed+sp.Sec
		// skip the first 5s of each step (transient) for the step summary
		results = append(results, summarise(buckets, queued, st+5, en, sp.Rate, *sloP99))
		r := results[len(results)-1]
		var sv, to int64
		var nsec int64
		for i := st + 5; i < en && i < len(servedPS); i++ {
			sv += servedPS[i]
			to += timedOutPS[i]
			nsec++
		}
		svRate, toRate := 0.0, 0.0
		if nsec > 0 {
			svRate, toRate = float64(sv)/float64(nsec), float64(to)/float64(nsec)
		}
		fmt.Printf("    achieved=%.1f p50=%.0f p95=%.0f p99=%.0f frac=%.3f qMean=%.1f served/s=%.0f timedOut/s=%.0f healthy=%v\n",
			r.AchievedRps, r.P50, r.P95, r.P99, r.FracUnderSLO, r.QMean, svRate, toRate, r.Healthy)
		elapsed = en
	}
	close(done)
	wg.Wait()

	// per-second series for the transition
	var series []map[string]any
	for i := 0; i < elapsed && i < len(buckets); i++ {
		b := buckets[i]
		b.mu.Lock()
		l := append([]float64(nil), b.lats...)
		b.mu.Unlock()
		sort.Float64s(l)
		good := 0
		for _, x := range l {
			if x <= *sloP99 {
				good++
			}
		}
		series = append(series, map[string]any{
			"tSec": i, "n": len(l), "p50Ms": pct(l, .50), "p99Ms": pct(l, .99),
			"fractionUnderSLO": frac(good, len(l)), "queued": queued[i],
			"servedPerSec": servedPS[i], "timedOutPerSec": timedOutPS[i],
		})
	}
	doc := map[string]any{
		"capacity": *capacity, "serviceTimeMs": info["serviceTimeMs"],
		"concurrency": info["concurrency"], "profile": *profileCSV,
		"sloP99Ms": *sloP99, "steps": results, "perSecond": series,
		"note": "continuous load, no gap or capacity reset between steps; step summaries skip the first 5s of each step",
	}
	b, _ := json.MarshalIndent(doc, "", "  ")
	os.WriteFile(*out, b, 0o644)
	fmt.Printf("\nwrote %s\n", *out)
}

func summarise(buckets []*secBucket, queued []int64, st, en int, rate, slo float64) (r stepResult) {
	var all []float64
	good, n := 0, 0
	var qs float64
	var qn int
	for i := st; i < en && i < len(buckets); i++ {
		b := buckets[i]
		b.mu.Lock()
		all = append(all, b.lats...)
		b.mu.Unlock()
		if i < len(queued) {
			qs += float64(queued[i])
			qn++
		}
	}
	sort.Float64s(all)
	n = len(all)
	for _, x := range all {
		if x <= slo {
			good++
		}
	}
	r.Rate, r.StartSec, r.EndSec = rate, st, en
	r.P50, r.P95, r.P99 = pct(all, .50), pct(all, .95), pct(all, .99)
	r.FracUnderSLO = frac(good, n)
	if en > st {
		r.AchievedRps = float64(n) / float64(en-st)
	}
	if qn > 0 {
		r.QMean = qs / float64(qn)
	}
	r.Healthy = r.P99 <= slo
	return r
}

func frac(a, b int) float64 {
	if b == 0 {
		return 0
	}
	return float64(a) / float64(b)
}
func pct(xs []float64, p float64) float64 {
	if len(xs) == 0 {
		return 0
	}
	return xs[int(float64(len(xs)-1)*p)]
}
func parseProfile(s string) []step {
	var out []step
	for _, part := range strings.Split(s, ",") {
		kv := strings.Split(strings.TrimSpace(part), ":")
		r, _ := strconv.ParseFloat(kv[0], 64)
		d, _ := strconv.Atoi(kv[1])
		out = append(out, step{Rate: r, Sec: d})
	}
	return out
}
func setCapacity(c *http.Client, base string, rate float64) {
	resp, err := c.Post(fmt.Sprintf("%s/admin/capacity?rate=%.0f", base, rate), "text/plain", nil)
	if err == nil {
		io.Copy(io.Discard, resp.Body)
		resp.Body.Close()
	}
}
func getJSON(c *http.Client, u string) map[string]any {
	resp, err := c.Get(u)
	if err != nil {
		return map[string]any{}
	}
	defer resp.Body.Close()
	var m map[string]any
	json.NewDecoder(resp.Body).Decode(&m)
	return m
}
func asInt(v any) int64 {
	if f, ok := v.(float64); ok {
		return int64(f)
	}
	return 0
}
