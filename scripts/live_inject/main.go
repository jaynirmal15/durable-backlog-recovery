package main

import (
	"encoding/json"
	"flag"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"
)

func main() {
	base := flag.String("url", "http://127.0.0.1:8080", "")
	path := flag.String("path", "/process", "endpoint path e.g. /process or /noop")
	rate := flag.Float64("rate", 1000, "")
	out := flag.String("out", "results/live.jsonl", "")
	maxInFlight := flag.Int64("max-inflight", 4096, "")
	flag.Parse()

	f, err := os.Create(*out)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	endpoint := *base + *path
	transport := &http.Transport{MaxIdleConns: 8192, MaxIdleConnsPerHost: 8192, MaxConnsPerHost: 8192}
	client := &http.Client{Timeout: 5 * time.Second, Transport: transport}

	var bufMu sync.Mutex
	var buf []byte
	flush := func() {
		bufMu.Lock()
		data := buf
		buf = nil
		bufMu.Unlock()
		if len(data) > 0 {
			_, _ = f.Write(data)
		}
	}

	var issued, completed, drops, peak atomic.Int64
	var nFlight atomic.Int64
	var stop atomic.Bool

	go func() {
		t := time.NewTicker(500 * time.Millisecond)
		defer t.Stop()
		for !stop.Load() {
			<-t.C
			flush()
		}
		flush()
	}()
	go func() {
		t := time.NewTicker(5 * time.Second)
		defer t.Stop()
		for !stop.Load() {
			<-t.C
			log.Printf("stats issued=%d completed=%d drops429=%d peakInFlight=%d inFlight=%d",
				issued.Load(), completed.Load(), drops.Load(), peak.Load(), nFlight.Load())
		}
	}()

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sig
		stop.Store(true)
	}()

	interval := time.Duration(float64(time.Second) / *rate)
	if interval < time.Microsecond {
		interval = time.Microsecond
	}
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	var wg sync.WaitGroup
	for !stop.Load() {
		<-ticker.C
		if stop.Load() {
			break
		}
		issued.Add(1)
		cur := nFlight.Load()
		for {
			p := peak.Load()
			if cur <= p || peak.CompareAndSwap(p, cur) {
				break
			}
		}
		if cur >= *maxInFlight {
			drops.Add(1)
			rec := map[string]any{"ts": time.Now().UnixMilli(), "class": "live", "latency_ms": 0, "status": 429, "age_ms": 0}
			b, _ := json.Marshal(rec)
			bufMu.Lock()
			buf = append(buf, b...)
			buf = append(buf, '\n')
			bufMu.Unlock()
			continue
		}
		nFlight.Add(1)
		wg.Add(1)
		go func() {
			defer wg.Done()
			defer nFlight.Add(-1)
			start := time.Now()
			resp, err := client.Post(endpoint, "text/plain", nil)
			lat := time.Since(start).Milliseconds()
			status := 0
			if err == nil {
				status = resp.StatusCode
				_, _ = io.Copy(io.Discard, resp.Body)
				resp.Body.Close()
			}
			completed.Add(1)
			rec := map[string]any{"ts": time.Now().UnixMilli(), "class": "live", "latency_ms": lat, "status": status, "age_ms": 0}
			b, _ := json.Marshal(rec)
			bufMu.Lock()
			buf = append(buf, b...)
			buf = append(buf, '\n')
			bufMu.Unlock()
		}()
	}
	wg.Wait()
	flush()
	log.Printf("FINAL issued=%d completed=%d drops429=%d peakInFlight=%d",
		issued.Load(), completed.Load(), drops.Load(), peak.Load())
}
