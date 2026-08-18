# Default NATS URL uses remapped host port from docker-compose.yml
NATS_URL ?= nats://127.0.0.1:14222
DOWNSTREAM_URL ?= http://127.0.0.1:8080
WORKERS ?= 1024

.PHONY: build tidy up down sweep smoke run-p0a run-p0b run-p0c run-p0d

build: tidy
	mkdir -p bin
	go build -o bin/downstream ./downstream
	go build -o bin/producer ./producer
	go build -o bin/consumer ./consumer
	go build -o bin/runner ./runner
	go build -o bin/load_sweep ./scripts/load_sweep

tidy:
	go mod tidy

up:
	docker compose -p rhc-phase0 up -d --build

down:
	docker compose -p rhc-phase0 down

# Downstream-only validation (no NATS).
sweep: build
	@echo "Start downstream first: CAPACITY=2000 ./bin/downstream"
	./bin/load_sweep -url $(DOWNSTREAM_URL) -capacity 2000 -duration 4s -out results/load_sweep.csv

# Short end-to-end smoke. Requires: make up && make build
smoke: build
	./bin/runner -condition P0-A -run-id smoke-p0a \
		-nats $(NATS_URL) -downstream $(DOWNSTREAM_URL) \
		-live-rate 400 -capacity 800 -outage 15 \
		-warmup 10 -healthy 10 -stabilize 10 \
		-workers 32

run-p0a: build
	./bin/runner -condition P0-A -run-id p0a-001 -nats $(NATS_URL) -downstream $(DOWNSTREAM_URL) -workers $(WORKERS)

run-p0b: build
	./bin/runner -condition P0-B -run-id p0b-001 -nats $(NATS_URL) -downstream $(DOWNSTREAM_URL) -workers $(WORKERS)

run-p0c: build
	./bin/runner -condition P0-C -run-id p0c-001 -nats $(NATS_URL) -downstream $(DOWNSTREAM_URL) -workers $(WORKERS)

run-p0d: build
	./bin/runner -condition P0-D -run-id p0d-001 -nats $(NATS_URL) -downstream $(DOWNSTREAM_URL) -workers $(WORKERS)
