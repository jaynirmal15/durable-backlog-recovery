package main

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

type Sample struct {
	TS        int64  `json:"ts"`
	Class     string `json:"class"` // "live" | "recovery"
	LatencyMs int64  `json:"latency_ms"`
	Status    int    `json:"status"`
	AgeMs     int64  `json:"age_ms"`
}

func env(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
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

func envInt64(key string, def int64) int64 {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	n, err := strconv.ParseInt(v, 10, 64)
	if err != nil {
		log.Fatalf("invalid %s=%q: %v", key, v, err)
	}
	return n
}

func main() {
	natsURL := env("NATS_URL", "nats://127.0.0.1:4222")
	stream := env("STREAM", "EVENTS")
	subject := env("SUBJECT", "events.orders")
	durable := env("DURABLE", "rhc-consumer")
	downstream := env("DOWNSTREAM_URL", "http://127.0.0.1:8080")
	workers := envInt("WORKERS", 64)
	batch := envInt("BATCH", 256)
	restoreEpoch := envInt64("RESTORE_EPOCH_MS", 0)
	samplesOut := env("SAMPLES_OUT", "/results/consumer.jsonl")
	rateLimit := envInt("RATE_LIMIT_RPS", 0) // 0 = unrestricted (Phase 0 default)

	if restoreEpoch == 0 {
		log.Printf("WARN: RESTORE_EPOCH_MS unset; all traffic classified as live")
	}

	f, err := os.OpenFile(samplesOut, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		log.Fatalf("open samples: %v", err)
	}
	defer f.Close()

	var sampleMu sync.Mutex
	var sampleBuf bytes.Buffer
	flush := func() {
		sampleMu.Lock()
		if sampleBuf.Len() == 0 {
			sampleMu.Unlock()
			return
		}
		data := make([]byte, sampleBuf.Len())
		copy(data, sampleBuf.Bytes())
		sampleBuf.Reset()
		sampleMu.Unlock()
		// Sync outside the lock — holding sampleMu across Sync stalled all
		// workers once the JSONL grew large (P0-B recovery dropout ~t=126s).
		if _, err := f.Write(data); err != nil {
			log.Printf("sample write: %v", err)
			return
		}
		_ = f.Sync()
	}
	defer flush()
	go func() {
		// 500ms matches the live injector flush so low rate-limit RPS windows
		// see recovery samples promptly (was 2s).
		t := time.NewTicker(500 * time.Millisecond)
		defer t.Stop()
		for range t.C {
			flush()
		}
	}()

	writeSample := func(s Sample) {
		b, _ := json.Marshal(s)
		sampleMu.Lock()
		sampleBuf.Write(b)
		sampleBuf.WriteByte('\n')
		sampleMu.Unlock()
	}

	nc, err := nats.Connect(natsURL, nats.Name("rhc-consumer"), nats.MaxReconnects(-1))
	if err != nil {
		log.Fatalf("nats connect: %v", err)
	}
	defer nc.Close()

	js, err := jetstream.New(nc)
	if err != nil {
		log.Fatalf("jetstream: %v", err)
	}

	ctx := context.Background()
	cons, err := js.CreateOrUpdateConsumer(ctx, stream, jetstream.ConsumerConfig{
		Durable:       durable,
		FilterSubject: subject,
		AckPolicy:     jetstream.AckExplicitPolicy,
		AckWait:       30 * time.Second,
		MaxAckPending: workers * batch,
	})
	if err != nil {
		log.Fatalf("create consumer: %v", err)
	}

	transport := &http.Transport{
		MaxIdleConns:        4096,
		MaxIdleConnsPerHost: 4096,
		MaxConnsPerHost:     4096,
	}
	client := &http.Client{Timeout: 5 * time.Second, Transport: transport}

	jobs := make(chan jetstream.Msg, batch*2)
	var limiter <-chan time.Time
	if rateLimit > 0 {
		ticker := time.NewTicker(time.Duration(float64(time.Second) / float64(rateLimit)))
		defer ticker.Stop()
		limiter = ticker.C
	}

	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for msg := range jobs {
				processOne(client, downstream, restoreEpoch, msg, writeSample, limiter)
			}
		}()
	}

	log.Printf("consumer started durable=%s workers=%d batch=%d restoreEpoch=%d rateLimit=%d out=%s",
		durable, workers, batch, restoreEpoch, rateLimit, samplesOut)

	for {
		msgs, err := cons.Fetch(batch, jetstream.FetchMaxWait(2*time.Second))
		if err != nil {
			continue
		}
		for msg := range msgs.Messages() {
			jobs <- msg
		}
		if err := msgs.Error(); err != nil && err != context.DeadlineExceeded {
			// Fetch timeout is normal when idle.
		}
	}
}

func processOne(client *http.Client, downstream string, restoreEpoch int64, msg jetstream.Msg, write func(Sample), limiter <-chan time.Time) {
	pubMs := int64(0)
	if v := msg.Headers().Get("X-Pub-Ms"); v != "" {
		pubMs, _ = strconv.ParseInt(v, 10, 64)
	}
	class := "live"
	if restoreEpoch > 0 && pubMs > 0 && pubMs < restoreEpoch {
		class = "recovery"
	}

	// Static-rate sweep: limit recovery work only; live traffic stays unrestricted.
	// Wait BEFORE stamping TS — otherwise a Fetch burst of N workers all share one
	// pre-limiter timestamp, fall out of the runner's 5s RPS window together, and
	// trip zero_recovery_traffic_during_drain at low rate limits (C1 rl=150).
	if class == "recovery" && limiter != nil {
		<-limiter
	}

	start := time.Now()
	resp, err := client.Post(downstream+"/process", "application/json", bytes.NewReader(msg.Data()))
	lat := time.Since(start).Milliseconds()
	status := 0
	if err != nil {
		status = 0
	} else {
		status = resp.StatusCode
		_, _ = io.Copy(io.Discard, resp.Body)
		resp.Body.Close()
	}

	// TS = request start (post-limiter) so trailing-window RPS matches offered recovery.
	ts := start.UnixMilli()
	age := ts - pubMs
	if pubMs == 0 {
		age = 0
	}
	write(Sample{
		TS:        ts,
		Class:     class,
		LatencyMs: lat,
		Status:    status,
		AgeMs:     age,
	})

	// Ack regardless of downstream status — Phase 0 is not about delivery semantics.
	_ = msg.Ack()
}
