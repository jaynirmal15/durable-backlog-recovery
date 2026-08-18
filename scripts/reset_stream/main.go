package main

import (
	"context"
	"flag"
	"log"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

func main() {
	natsURL := flag.String("nats", "nats://127.0.0.1:14222", "")
	flag.Parse()
	nc, err := nats.Connect(*natsURL)
	if err != nil {
		log.Fatal(err)
	}
	defer nc.Close()
	js, err := jetstream.New(nc)
	if err != nil {
		log.Fatal(err)
	}
	ctx := context.Background()
	_ = js.DeleteConsumer(ctx, "EVENTS", "rhc-consumer")
	_ = js.DeleteStream(ctx, "EVENTS")
	_, err = js.CreateStream(ctx, jetstream.StreamConfig{
		Name:      "EVENTS",
		Subjects:  []string{"events.>"},
		Storage:   jetstream.FileStorage,
		Retention: jetstream.LimitsPolicy,
		MaxAge:    24 * time.Hour,
	})
	if err != nil {
		log.Fatal(err)
	}
	_, err = js.CreateConsumer(ctx, "EVENTS", jetstream.ConsumerConfig{
		Durable:       "rhc-consumer",
		FilterSubject: "events.orders",
		AckPolicy:     jetstream.AckExplicitPolicy,
		AckWait:       30 * time.Second,
	})
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("stream reset ok")
}
