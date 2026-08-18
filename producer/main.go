package main

import (
	"context"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

func env(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func envFloat(key string, def float64) float64 {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	f, err := strconv.ParseFloat(v, 64)
	if err != nil {
		log.Fatalf("invalid %s=%q: %v", key, v, err)
	}
	return f
}

func main() {
	natsURL := env("NATS_URL", "nats://127.0.0.1:4222")
	subject := env("SUBJECT", "events.orders")
	stream := env("STREAM", "EVENTS")
	rate := envFloat("RATE_PER_SEC", 1400)

	nc, err := nats.Connect(natsURL, nats.Name("rhc-producer"), nats.MaxReconnects(-1))
	if err != nil {
		log.Fatalf("nats connect: %v", err)
	}
	defer nc.Close()

	js, err := jetstream.New(nc)
	if err != nil {
		log.Fatalf("jetstream: %v", err)
	}

	ctx := context.Background()
	_, err = js.CreateOrUpdateStream(ctx, jetstream.StreamConfig{
		Name:      stream,
		Subjects:  []string{"events.>"},
		Storage:   jetstream.FileStorage,
		Retention: jetstream.LimitsPolicy,
		MaxAge:    24 * time.Hour,
	})
	if err != nil {
		log.Fatalf("create stream: %v", err)
	}
	log.Printf("producer ready stream=%s subject=%s rate=%.0f/s", stream, subject, rate)

	payload := []byte(`{"op":"order","v":1}`)
	interval := time.Duration(float64(time.Second) / rate)
	if interval < time.Microsecond {
		interval = time.Microsecond
	}
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	var published int64
	lastReport := time.Now()
	for range ticker.C {
		msg := &nats.Msg{
			Subject: subject,
			Data:    payload,
			Header:  nats.Header{},
		}
		msg.Header.Set("X-Pub-Ms", strconv.FormatInt(time.Now().UnixMilli(), 10))
		if _, err := js.PublishMsg(ctx, msg); err != nil {
			log.Printf("publish error: %v", err)
			continue
		}
		published++
		if time.Since(lastReport) >= time.Second {
			log.Printf("published_total=%d", published)
			lastReport = time.Now()
		}
	}
}
