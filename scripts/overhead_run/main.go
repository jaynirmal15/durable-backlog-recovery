// E2e experiment 1 driver: hold a load level, report achieved throughput, and
// dump the downstream's overhead probe.
//
// Two modes:
//
//	-rate N   open loop at N rps, for measuring the overhead under stated load
//	-rate 0   closed loop with -conns workers, which saturates the server and
//	          gives the throughput plateau
//
// Throughput is read from the downstream's own `served` counter rather than from
// client-side completions, so a slow client cannot be mistaken for a slow server.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

func getJSON(c *http.Client, url string) map[string]any {
	resp, err := c.Get(url)
	if err != nil {
		return nil
	}
	defer resp.Body.Close()
	var m map[string]any
	b, _ := io.ReadAll(resp.Body)
	_ = json.Unmarshal(b, &m)
	return m
}

func f(m map[string]any, k string) float64 {
	if m == nil {
		return 0
	}
	if v, ok := m[k].(float64); ok {
		return v
	}
	return 0
}

func main() {
	url := flag.String("url", "http://127.0.0.1:8080", "downstream base URL")
	rate := flag.Float64("rate", 0, "offered rps; 0 = closed-loop saturation")
	conns := flag.Int("conns", 400, "closed-loop workers when -rate 0")
	warmup := flag.Duration("warmup", 10*time.Second, "discarded before measuring")
	dur := flag.Duration("duration", 60*time.Second, "measurement window")
	label := flag.String("label", "", "printed with the result")
	flag.Parse()

	tr := &http.Transport{MaxIdleConns: 20000, MaxIdleConnsPerHost: 20000,
		MaxConnsPerHost: 20000, IdleConnTimeout: 90 * time.Second}
	client := &http.Client{Timeout: 10 * time.Second, Transport: tr}

	var stop atomic.Bool
	var sent atomic.Int64
	body := strings.NewReader("{}")
	_ = body
	fire := func() {
		req, _ := http.NewRequest("POST", *url+"/process", strings.NewReader("{}"))
		resp, err := client.Do(req)
		if err == nil {
			io.Copy(io.Discard, resp.Body)
			resp.Body.Close()
		}
		sent.Add(1)
	}

	var wg sync.WaitGroup
	if *rate <= 0 {
		for i := 0; i < *conns; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for !stop.Load() {
					fire()
				}
			}()
		}
	} else {
		// Open loop, multi-lane deadline pacer: the same shape as the harness's
		// `lanes` injector, so the arrival process matches the campaigns.
		lanes := 64
		per := *rate / float64(lanes)
		for i := 0; i < lanes; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				iv := time.Duration(float64(time.Second) / per)
				next := time.Now()
				for !stop.Load() {
					next = next.Add(iv)
					if d := time.Until(next); d > 0 {
						time.Sleep(d)
					}
					go fire()
				}
			}()
		}
	}

	time.Sleep(*warmup)
	s0 := getJSON(client, *url+"/admin/stats")
	t0 := time.Now()
	time.Sleep(*dur)
	s1 := getJSON(client, *url+"/admin/stats")
	el := time.Since(t0).Seconds()
	stop.Store(true)

	served := (f(s1, "served") - f(s0, "served")) / el
	rej := f(s1, "rejected") - f(s0, "rejected")
	to := f(s1, "timedOut") - f(s0, "timedOut")

	cap := getJSON(client, *url+"/admin/capacity")
	ov := getJSON(client, *url+"/admin/overhead")

	out := map[string]any{
		"label": *label, "offeredRate": *rate, "closedLoopConns": *conns,
		"windowSec": el, "servedRps": served, "rejected": rej, "timedOut": to,
		"serviceTimeUs": f(cap, "serviceTimeUs"), "concurrency": f(cap, "concurrency"),
		"configuredCapacity": f(cap, "trueCapacity"), "queueCap": f(cap, "queueCap"),
		"overhead": ov,
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	_ = enc.Encode(out)
	fmt.Fprintf(os.Stderr, "%s: served %.1f rps (offered %.0f), S=%.0fus conc=%.0f\n",
		*label, served, *rate, f(cap, "serviceTimeUs"), f(cap, "concurrency"))
	wg.Wait()
}
