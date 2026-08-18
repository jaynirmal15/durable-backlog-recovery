package main

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"math"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/nats-io/nats.go/jetstream"
)

type CapacityStep struct {
	AtSec int     `json:"atSec"`
	Rate  float64 `json:"rate"`
}

type HeadroomStep struct {
	AtSec    int     `json:"atSec"`
	Capacity float64 `json:"capacity"`
	Headroom float64 `json:"headroom"`
}

type TimelinePoint struct {
	TSec               float64 `json:"tSec"`
	Backlog            int64   `json:"backlog"` // deprecated alias of totalPending
	TotalPending       int64   `json:"totalPending"`
	RecoveryRemaining  int64   `json:"recoveryRemaining"`
	RecoveryAcked      int64   `json:"recoveryAcked"`
	LiveInFlight       int64   `json:"liveInFlight"`
	LiveRps            float64 `json:"liveRps"`
	RecoveryRps        float64 `json:"recoveryRps"`
	TrueCapacity       float64 `json:"trueCapacity"`
	OfferedRate        float64 `json:"offeredRate"`
	Queued             int64   `json:"queued"`
	Served             int64   `json:"served"`
	Rejected           int64   `json:"rejected"`
	TimedOut           int64   `json:"timedOut"`
	LiveP99Ms          float64 `json:"liveP99Ms"`
	RecoveryP99Ms      float64 `json:"recoveryP99Ms"`
	ErrorRate          float64 `json:"errorRate"`
}

type RunRecord struct {
	RunID             string          `json:"runId"`
	Condition         string          `json:"condition"`
	GitCommit         string          `json:"gitCommit"`
	GitDirty          bool            `json:"gitDirty"`
	StartedAt         string          `json:"startedAt"`
	Params            map[string]any  `json:"params"`
	BacklogAtRestore  int64           `json:"backlogAtRestore"`
	RestoreEpochMs    int64           `json:"restoreEpochMs"`
	CapacitySchedule  []CapacityStep  `json:"capacitySchedule"`
	HeadroomSchedule  []HeadroomStep  `json:"headroomSchedule"`
	Timeline          []TimelinePoint `json:"timeline"`
	TDrainSec         float64         `json:"tDrainSec"`
	TFullSec          float64         `json:"tFullSec"`          // primary: W from params.stabilizeSeconds
	TFullSecW30       float64         `json:"tFullSecW30"`       // sensitivity: same run, W=30s
	VSLO              float64         `json:"vSLO"`              // violations / tFullSec (W primary)
	VSLOW30           float64         `json:"vSLO_W30,omitempty"`
	PeakOfferedRate   float64         `json:"peakOfferedRate"`
	Amplification     float64         `json:"amplification"`
	LiveSLOPopulation string          `json:"liveSLOPopulation,omitempty"`
	Supplementary     *Supplementary  `json:"supplementary,omitempty"`
	Aborted           string          `json:"aborted,omitempty"`
	Invalid           bool            `json:"invalid,omitempty"`
	InvalidReason     string          `json:"invalidReason,omitempty"`
}

// Supplementary metrics for Phase 1 frontier axes (p99/V_SLO may be degenerate).
type Supplementary struct {
	TimeoutRate          float64 `json:"timeoutRate"`
	LiveP50Ms            float64 `json:"liveP50Ms"`
	LiveP90Ms            float64 `json:"liveP90Ms"`
	LiveP95Ms            float64 `json:"liveP95Ms"`
	LiveP99Ms            float64 `json:"liveP99Ms"`
	FractionUnderSLO     float64 `json:"fractionUnderSLO250ms"`
	QueueDepthMean       float64 `json:"queueDepthMean"`
	QueueDepthPeak       int64   `json:"queueDepthPeak"`
	GoodputRpsMean       float64 `json:"goodputRpsMean"` // successful & latency<=SLO / wall
	DrainTimeoutRate     float64 `json:"drainTimeoutRate"`
	DrainLiveP50Ms       float64 `json:"drainLiveP50Ms"`
	DrainLiveP90Ms       float64 `json:"drainLiveP90Ms"`
	DrainLiveP95Ms       float64 `json:"drainLiveP95Ms"`
	DrainLiveP99Ms       float64 `json:"drainLiveP99Ms"`
	DrainFractionUnderSLO float64 `json:"drainFractionUnderSLO250ms"`
	DrainGoodputRpsMean  float64 `json:"drainGoodputRpsMean"`
	DrainQueueDepthMean  float64 `json:"drainQueueDepthMean"`
	DrainQueueDepthPeak  int64   `json:"drainQueueDepthPeak"`
}

type Sample struct {
	TS        int64  `json:"ts"`
	Class     string `json:"class"`
	LatencyMs int64  `json:"latency_ms"`
	Status    int    `json:"status"`
	AgeMs     int64  `json:"age_ms"`
}

func main() {
	condition := flag.String("condition", "P0-A", "P0-A|P0-B|P0-C|P0-D")
	runID := flag.String("run-id", "", "run id (default: condition-timestamp)")
	liveRate := flag.Float64("live-rate", 1000, "live publish/inject rate")
	nominalCap := flag.Float64("capacity", 2000, "nominal downstream capacity")
	outageSec := flag.Int("outage", 120, "outage duration seconds")
	serviceTimeMs := flag.Int("service-time-ms", 5, "downstream service time")
	arm := flag.String("arm", "", "concurrency arm c10|c50 — asserts downstream S/concurrency match before start")
	profile := flag.String("profile", "graceful", "downstream profile")
	workers := flag.Int("workers", 64, "consumer workers")
	sloP99 := flag.Float64("slo-p99-ms", 250, "live p99 SLO")
	sloErr := flag.Float64("slo-error-rate", 0.01, "error rate SLO")
	warmupSec := flag.Int("warmup", 30, "warmup seconds")
	healthySec := flag.Int("healthy", 30, "required healthy seconds before outage")
	stabilizeSec := flag.Int("stabilize", 15, "post-drain healthy window W (primary T_full)")
	stabilizeW30Sec := flag.Int("stabilize-w30", 30, "sensitivity: also record T_full at this W")
	rateLimit := flag.Int("rate-limit", 0, "optional consumer recovery rate limit rps (0=off)")
	natsURL := flag.String("nats", env("NATS_URL", "nats://127.0.0.1:14222"), "NATS URL")
	downstream := flag.String("downstream", env("DOWNSTREAM_URL", "http://127.0.0.1:8080"), "downstream URL")
	resultsDir := flag.String("results", "results", "results directory")
	flag.Parse()

	if *runID == "" {
		*runID = fmt.Sprintf("%s-%s", strings.ToLower(*condition), time.Now().Format("20060102-150405"))
	}

	schedule := scheduleFor(*condition, *nominalCap, *liveRate)
	headroom := headroomSchedule(schedule, *liveRate)
	log.Printf("headroom schedule for %s (λ_L=%.0f):", *condition, *liveRate)
	for _, h := range headroom {
		log.Printf("  atSec=%d capacity=%.0f headroom=%.0f", h.AtSec, h.Capacity, h.Headroom)
	}
	if err := assertHeadroom(*condition, headroom); err != nil {
		log.Fatalf("misconfiguration: %v", err)
	}

	client := &http.Client{Timeout: 5 * time.Second}
	if err := waitHealthy(client, *downstream, 30*time.Second); err != nil {
		log.Fatalf("downstream: %v", err)
	}
	dsCap := getCapacity(client, *downstream)
	if err := assertDownstreamArm(*arm, *serviceTimeMs, *nominalCap, dsCap); err != nil {
		log.Fatalf("arm mismatch: %v", err)
	}
	dsConc := int(asFloat(dsCap["concurrency"]))
	dsSvcMs := int(asFloat(dsCap["serviceTimeMs"]))
	if *arm != "" {
		log.Printf("arm %s OK: downstream S=%dms concurrency=%d queueCap=%v at C=%.0f",
			*arm, dsSvcMs, dsConc, dsCap["queueCap"], asFloat(dsCap["trueCapacity"]))
	}

	commit, dirty := gitInfo()

	rec := RunRecord{
		RunID:            *runID,
		Condition:        *condition,
		GitCommit:        commit,
		GitDirty:         dirty,
		StartedAt:        time.Now().UTC().Format(time.RFC3339),
		CapacitySchedule: schedule,
		HeadroomSchedule: headroom,
		Params: map[string]any{
			"liveRatePerSec":  *liveRate,
			"nominalCapacity": *nominalCap,
			"outageSeconds":   *outageSec,
			"serviceTimeMs":   *serviceTimeMs,
			"concurrencyArm":  *arm,
			"downstreamServiceTimeMs": dsSvcMs,
			"downstreamConcurrency":   dsConc,
			"downstreamQueueCap":      asFloat(dsCap["queueCap"]),
			"profile":         *profile,
			"workers":         *workers,
			"sloP99Ms":        *sloP99,
			"sloErrorRate":    *sloErr,
			"rateLimitRps":    *rateLimit,
			"maxInFlight":     liveInjectorMaxInFlight,
			"sloErrorAccounting": "exclude_status_429_client_injector_drops",
			"stabilizeSeconds":   *stabilizeSec,
			"stabilizeW30Seconds": *stabilizeW30Sec,
			"stabilizeJustification": "W=15s = 3× observed post-drain settling (~5s queue/latency return) from p0b-pilot-arch2b; W=30 retained as sensitivity",
		},
	}

	nc, err := nats.Connect(*natsURL, nats.Name("rhc-runner"))
	if err != nil {
		log.Fatalf("nats: %v", err)
	}
	defer nc.Close()
	js, err := jetstream.New(nc)
	if err != nil {
		log.Fatalf("jetstream: %v", err)
	}
	ctx := context.Background()

	log.Printf("resetting stream/consumer and downstream capacity")
	if err := resetStream(ctx, js, "EVENTS", "rhc-consumer"); err != nil {
		log.Fatalf("reset: %v", err)
	}
	if err := setCapacity(client, *downstream, *nominalCap); err != nil {
		log.Fatalf("capacity: %v", err)
	}

	_ = os.MkdirAll(*resultsDir, 0o755)
	samplesPath := filepath.Join(*resultsDir, *runID+"-consumer.jsonl")
	_ = os.Remove(samplesPath)

	// Shared sample tailer state.
	var sampleMu sync.Mutex
	var samples []Sample

	consumerEnv := func(restoreMs int64) map[string]string {
		m := map[string]string{
			"NATS_URL":         *natsURL,
			"STREAM":           "EVENTS",
			"SUBJECT":          "events.orders",
			"DURABLE":          "rhc-consumer",
			"DOWNSTREAM_URL":   *downstream,
			"WORKERS":          strconv.Itoa(*workers),
			"BATCH":            "256",
			"RESTORE_EPOCH_MS": strconv.FormatInt(restoreMs, 10),
			"SAMPLES_OUT":      samplesPath,
		}
		if *rateLimit > 0 {
			m["RATE_LIMIT_RPS"] = strconv.Itoa(*rateLimit)
		}
		return m
	}

	// Architecture: live = injector only; JetStream = recovery backlog only.
	// Warmup/healthy: injector alone (do not also run producer→consumer or we
	// double-load the downstream at 2×λ_L and fail the healthy check).
	// Outage: start producer (builds backlog); injector continues.
	// Restore: stop producer; start consumer; injector continues through T_full.
	liveStop := make(chan struct{})
	var liveWG sync.WaitGroup
	var liveOnce sync.Once
	var injStats InjectorStats
	stopLive := func() {
		liveOnce.Do(func() {
			close(liveStop)
			liveWG.Wait()
			log.Printf("live injector stopped issued=%d completed=%d drops429=%d peakInFlight=%d",
				injStats.Issued.Load(), injStats.Completed.Load(), injStats.Drops429.Load(), injStats.PeakInFlight.Load())
		})
	}
	startLiveInjector(&liveWG, *downstream, *liveRate, samplesPath, &sampleMu, &samples, &injStats, liveStop)
	defer stopLive()
	go tailSamples(samplesPath, &sampleMu, &samples)

	log.Printf("warmup %ds (injector-only)", *warmupSec)
	time.Sleep(time.Duration(*warmupSec) * time.Second)

	log.Printf("verifying healthy for %ds", *healthySec)
	if ok, reason := waitSLO(client, *downstream, &sampleMu, &samples, time.Duration(*healthySec)*time.Second, *sloP99, *sloErr, "live"); !ok {
		rec.Aborted = "pre-outage unhealthy: " + reason
		writeRecord(*resultsDir, rec)
		log.Fatalf("abort: %s", rec.Aborted)
	}

	log.Printf("starting producer for outage=%ds (injector continues)", *outageSec)
	producer := startCmd("producer", "./bin/producer", map[string]string{
		"NATS_URL":     *natsURL,
		"SUBJECT":      "events.orders",
		"STREAM":       "EVENTS",
		"RATE_PER_SEC": fmt.Sprintf("%.0f", *liveRate),
	})
	producerAlive := true
	defer func() {
		if producerAlive {
			stopCmd(producer)
		}
	}()
	outageStart := time.Now()
	time.Sleep(time.Duration(*outageSec) * time.Second)

	// Stop producer BEFORE measuring backlog / setting epoch so in-flight
	// publishes land as pre-epoch recovery. Measuring then stopping left a
	// single post-epoch message (recLeft stuck at 1, pending=0).
	log.Printf("stopping producer at restore (injector continues at λ_L)")
	stopCmd(producer)
	producerAlive = false
	time.Sleep(time.Second) // drain producer in-flight publishes into JetStream

	backlog, err := pending(ctx, js, "EVENTS", "rhc-consumer")
	if err != nil {
		log.Fatalf("pending: %v", err)
	}
	rec.BacklogAtRestore = backlog
	restoreEpoch := time.Now().UnixMilli()
	rec.RestoreEpochMs = restoreEpoch
	log.Printf("restore backlog=%d epoch=%d (outage wall=%.1fs)", backlog, restoreEpoch, time.Since(outageStart).Seconds())
	rec.Params["producerStoppedAtRestore"] = true
	rec.Params["injectorContinuousThroughTFull"] = true
	rec.Params["liveSLOPopulation"] = "injector_direct"

	// Clear samples for drain phase metrics (keep file append-only for raw data).
	sampleMu.Lock()
	samples = nil
	sampleMu.Unlock()

	consumer := startCmd("consumer", "./bin/consumer", consumerEnv(restoreEpoch))
	defer stopCmd(consumer)

	t0 := time.Now()
	applySchedule(client, *downstream, schedule, 0)
	prevIssued := injStats.Issued.Load()

	// Baseline served counter so offered-rate deltas aren't polluted by prior runs.
	prevServed := int64(asFloat(getStats(client, *downstream)["served"]))
	prevSampleTS := time.Now()

	var (
		timeline       []TimelinePoint
		peakOffered    float64
		drainAt        time.Time
		fullAt         time.Time // primary W
		fullAtW30      time.Time
		healthyStreak  time.Duration
		violationSecs  float64
		zeroLiveStreak time.Duration
		zeroRecStreak  time.Duration
		queueSum       float64
		queueN         int64
		queuePeak      int64
		violationAtFull float64
		drainCompleteStreak time.Duration
	)

	stabilization := time.Duration(*stabilizeSec) * time.Second
	stabilizationW30 := time.Duration(*stabilizeW30Sec) * time.Second
	// Collect through the longer window so both T_full(W) and T_full(W30) exist.
	stopAfter := stabilization
	if stabilizationW30 > stopAfter {
		stopAfter = stabilizationW30
	}
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()

	for range ticker.C {
		tSec := time.Since(t0).Seconds()
		applySchedule(client, *downstream, schedule, tSec)

		totalPending, _ := pending(ctx, js, "EVENTS", "rhc-consumer")
		st := getStats(client, *downstream)
		capInfo := getCapacity(client, *downstream)

		sampleMu.Lock()
		window := trailing(samples, 5*time.Second)
		recAcked := countClass(samples, "recovery")
		sampleMu.Unlock()
		// Live SLO = injector-direct only (age_ms==0). NATS-live is excluded.
		liveP99, recP99, errRate := windowMetricsInjectorLive(window)
		liveRps, recRps := classRPSInjectorLive(window, 5.0)

		recoveryRemaining := rec.BacklogAtRestore - recAcked
		if recoveryRemaining < 0 {
			recoveryRemaining = 0
		}
		liveInFlight := injStats.CurrentInFlight.Load()

		served := int64(asFloat(st["served"]))
		dt := time.Since(prevSampleTS).Seconds()
		offered := 0.0
		if dt > 0 && served >= prevServed {
			offered = float64(served-prevServed) / dt
		}
		issued := injStats.Issued.Load()
		injRate := 0.0
		if dt > 0 && issued >= prevIssued {
			injRate = float64(issued-prevIssued) / dt
		}
		prevIssued = issued
		prevServed = served
		prevSampleTS = time.Now()
		if offered > peakOffered {
			peakOffered = offered
		}

		queued := int64(asFloat(st["queued"]))
		queueSum += float64(queued)
		queueN++
		if queued > queuePeak {
			queuePeak = queued
		}

		pt := TimelinePoint{
			TSec:              tSec,
			Backlog:           totalPending,
			TotalPending:      totalPending,
			RecoveryRemaining: recoveryRemaining,
			RecoveryAcked:     recAcked,
			LiveInFlight:      liveInFlight,
			LiveRps:           liveRps,
			RecoveryRps:       recRps,
			TrueCapacity:      asFloat(capInfo["trueCapacity"]),
			OfferedRate:       offered,
			Queued:            queued,
			Served:            served,
			Rejected:          int64(asFloat(st["rejected"])),
			TimedOut:          int64(asFloat(st["timedOut"])),
			LiveP99Ms:         liveP99,
			RecoveryP99Ms:     recP99,
			ErrorRate:         errRate,
		}
		timeline = append(timeline, pt)
		log.Printf("t=%6.1fs pending=%d recLeft=%d liveRps=%.0f injRate=%.0f recRps=%.0f cap=%.0f offered=%.0f liveP99=%.0f err=%.3f",
			tSec, totalPending, recoveryRemaining, liveRps, injRate, recRps, pt.TrueCapacity, offered, liveP99, errRate)

		if liveP99 > *sloP99 || errRate > *sloErr {
			violationSecs += 1
		}

		// Integrity: injector must keep issuing from restore through T_full.
		if injRate <= 0 {
			rec.Invalid = true
			rec.InvalidReason = "zero_injector_rate_before_tfull"
			rec.Aborted = "injector issue rate was zero between restore and T_full"
			log.Printf("INVALID: %s (t=%.1fs)", rec.Aborted, tSec)
			break
		}

		// Integrity: live traffic must remain present while recovery remains.
		if recoveryRemaining > 0 {
			if liveRps <= 0 {
				zeroLiveStreak += time.Second
			} else {
				zeroLiveStreak = 0
			}
			if zeroLiveStreak >= 3*time.Second {
				rec.Invalid = true
				rec.InvalidReason = "zero_live_traffic_during_recovery"
				rec.Aborted = "live request rate was zero for >=3s while recoveryRemaining>0"
				log.Printf("INVALID: %s", rec.Aborted)
				break
			}
			if recRps <= 0 && liveRps > 0 {
				zeroRecStreak += time.Second
			} else {
				zeroRecStreak = 0
			}
			// Ignore end-of-drain tail: with rem≪backlog a 5s RPS window can
			// read zero for ≥3s while the last messages finish (false INVALID on
			// p0b-v2-r2/r3 with rem=1). Require material remaining work.
			minRem := int64(100)
			if rec.BacklogAtRestore/100 > minRem {
				minRem = rec.BacklogAtRestore / 100 // 1% of backlog
			}
			if zeroRecStreak >= 3*time.Second && recoveryRemaining >= minRem {
				rec.Invalid = true
				rec.InvalidReason = "zero_recovery_traffic_during_drain"
				rec.Aborted = "recovery request rate was zero for >=3s while recoveryRemaining>0 and liveRps>0"
				log.Printf("INVALID: %s (rem=%d minRem=%d)", rec.Aborted, recoveryRemaining, minRem)
				break
			}
		} else {
			zeroRecStreak = 0
		}

		// T_drain: rem==0, or JetStream empty with only accounting residual
		// (producer-stop race / one misclassified sample left rem=1 forever).
		drained := recoveryRemaining == 0 ||
			(totalPending == 0 && recoveryRemaining > 0 && recoveryRemaining <= 5 && recRps <= 0)
		if drained {
			drainCompleteStreak += time.Second
		} else {
			drainCompleteStreak = 0
		}
		if drainCompleteStreak >= 2*time.Second && drainAt.IsZero() {
			drainAt = time.Now()
			if recoveryRemaining != 0 {
				log.Printf("recovery drained at t=%.1fs (accounting residual rem=%d recoveryAcked=%d backlogAtRestore=%d totalPending=%d)",
					tSec, recoveryRemaining, recAcked, rec.BacklogAtRestore, totalPending)
				recoveryRemaining = 0 // treat as clear for stabilize logic below
			} else {
				log.Printf("recovery drained at t=%.1fs (recoveryAcked=%d backlogAtRestore=%d totalPending=%d)",
					tSec, recAcked, rec.BacklogAtRestore, totalPending)
			}
		}
		drainDone := !drainAt.IsZero()
		if drainDone {
			recoveryRemaining = 0
		}

		liveOK := liveP99 <= *sloP99 && errRate <= *sloErr && liveP99 > 0
		if drainDone && liveOK {
			healthyStreak += time.Second
		} else {
			healthyStreak = 0
		}
		if drainDone && healthyStreak >= stabilization && fullAt.IsZero() {
			fullAt = time.Now()
			violationAtFull = violationSecs
			log.Printf("stabilized (W=%ds) at t=%.1fs", *stabilizeSec, tSec)
		}
		if drainDone && healthyStreak >= stabilizationW30 && fullAtW30.IsZero() {
			fullAtW30 = time.Now()
			log.Printf("stabilized (W=%ds sensitivity) at t=%.1fs", *stabilizeW30Sec, tSec)
		}
		if !fullAt.IsZero() && (stabilizationW30 <= stabilization || !fullAtW30.IsZero()) {
			break
		}
		if !fullAt.IsZero() && healthyStreak >= stopAfter {
			break
		}
		if tSec > 2700 {
			rec.Aborted = "timeout waiting for drain/stabilize"
			break
		}
	}

	stopLive()

	rec.Params["injectorIssued"] = injStats.Issued.Load()
	rec.Params["injectorCompleted"] = injStats.Completed.Load()
	rec.Params["injectorDrops429"] = injStats.Drops429.Load()
	rec.Params["injectorPeakInFlight"] = injStats.PeakInFlight.Load()
	rec.LiveSLOPopulation = "injector_direct"

	rec.Timeline = timeline
	if !drainAt.IsZero() {
		rec.TDrainSec = drainAt.Sub(t0).Seconds()
	}
	if !fullAt.IsZero() {
		rec.TFullSec = fullAt.Sub(t0).Seconds()
	} else {
		rec.TFullSec = time.Since(t0).Seconds()
	}
	if !fullAtW30.IsZero() {
		rec.TFullSecW30 = fullAtW30.Sub(t0).Seconds()
	} else if *stabilizeW30Sec <= *stabilizeSec && !fullAt.IsZero() {
		// W30 <= primary W: primary stabilization implies W30 already met earlier.
		// Approximate: T_full(W30) = T_drain + (T_full - T_drain) * W30/W
		// Better: T_full_W30 = time when streak first hit W30 = fullAt - (W - W30)
		rec.TFullSecW30 = rec.TFullSec - float64(*stabilizeSec-*stabilizeW30Sec)
		if rec.TFullSecW30 < rec.TDrainSec {
			rec.TFullSecW30 = rec.TFullSec
		}
	} else {
		rec.TFullSecW30 = rec.TFullSec // incomplete sensitivity
	}
	if rec.TFullSec > 0 {
		rec.VSLO = violationAtFull / rec.TFullSec
	}
	if rec.TFullSecW30 > 0 {
		rec.VSLOW30 = violationSecs / rec.TFullSecW30
	}
	rec.PeakOfferedRate = peakOffered
	if *liveRate > 0 {
		rec.Amplification = peakOffered / *liveRate
	}

	sampleMu.Lock()
	allSamples := append([]Sample(nil), samples...)
	sampleMu.Unlock()
	rec.Supplementary = computeSupplementary(allSamples, timeline, rec.TDrainSec, *sloP99, queueSum, queueN, queuePeak)

	path := writeRecord(*resultsDir, rec)
	log.Printf("wrote %s tDrain=%.1f tFull(W=%d)=%.1f tFull(W30)=%.1f vSLO=%.3f",
		path, rec.TDrainSec, *stabilizeSec, rec.TFullSec, rec.TFullSecW30, rec.VSLO)
}

func scheduleFor(cond string, nominal, live float64) []CapacityStep {
	switch cond {
	case "P0-A":
		return []CapacityStep{{AtSec: 0, Rate: nominal}}
	case "P0-B":
		return []CapacityStep{{AtSec: 0, Rate: nominal}, {AtSec: 20, Rate: math.Round(nominal * 0.70)}}
	case "P0-C":
		return []CapacityStep{
			{AtSec: 0, Rate: nominal},
			{AtSec: 20, Rate: math.Round(nominal * 0.65)},
			{AtSec: 60, Rate: nominal},
		}
	case "P0-D":
		// Must sit strictly below λ_L (infeasible). Default 900 with λ_L=1000.
		below := 900.0
		if live > 0 && below >= live {
			below = math.Floor(live - 100)
			if below < 1 {
				below = 1
			}
		}
		return []CapacityStep{{AtSec: 0, Rate: nominal}, {AtSec: 20, Rate: below}, {AtSec: 90, Rate: nominal}}
	default:
		log.Fatalf("unknown condition %s", cond)
		return nil
	}
}

func headroomSchedule(schedule []CapacityStep, live float64) []HeadroomStep {
	out := make([]HeadroomStep, 0, len(schedule))
	for _, s := range schedule {
		h := s.Rate - live
		out = append(out, HeadroomStep{AtSec: s.AtSec, Capacity: s.Rate, Headroom: h})
	}
	return out
}

// assertHeadroom refuses non-P0-D runs with any step headroom ≤ 0, and refuses
// P0-D if the fault window never goes negative.
func assertHeadroom(cond string, steps []HeadroomStep) error {
	if len(steps) == 0 {
		return fmt.Errorf("empty headroom schedule")
	}
	if cond == "P0-D" {
		neg := false
		for _, s := range steps {
			if s.Headroom < 0 {
				neg = true
				break
			}
		}
		if !neg {
			return fmt.Errorf("P0-D requires at least one schedule step with headroom < 0 (got %v)", steps)
		}
		return nil
	}
	for _, s := range steps {
		if s.Headroom <= 0 {
			return fmt.Errorf("%s has headroom=%.0f at atSec=%d (capacity=%.0f); only P0-D may be infeasible",
				cond, s.Headroom, s.AtSec, s.Capacity)
		}
	}
	return nil
}

// assertDownstreamArm refuses runs when declared arm does not match live downstream
// configuration (guards against forgotten SERVICE_TIME_MS toggles).
func assertDownstreamArm(arm string, declaredSvcMs int, nominalCap float64, ds map[string]any) error {
	if arm == "" {
		return nil
	}
	wantSvc, wantConc, err := armExpectations(arm, nominalCap)
	if err != nil {
		return err
	}
	gotSvc := int(asFloat(ds["serviceTimeMs"]))
	gotConc := int(asFloat(ds["concurrency"]))
	if gotSvc != wantSvc {
		return fmt.Errorf("arm %s expects serviceTimeMs=%d but downstream has %d", arm, wantSvc, gotSvc)
	}
	if gotConc != wantConc {
		return fmt.Errorf("arm %s expects concurrency=%d at C=%.0f but downstream has %d",
			arm, wantConc, nominalCap, gotConc)
	}
	if declaredSvcMs != wantSvc {
		return fmt.Errorf("arm %s expects -service-time-ms=%d but flag is %d", arm, wantSvc, declaredSvcMs)
	}
	return nil
}

func armExpectations(arm string, nominalCap float64) (serviceTimeMs, concurrency int, err error) {
	switch arm {
	case "c10":
		serviceTimeMs = 5
	case "c50":
		serviceTimeMs = 25
	default:
		return 0, 0, fmt.Errorf("unknown arm %q (use c10 or c50)", arm)
	}
	s := float64(serviceTimeMs) / 1000.0
	concurrency = int(math.Ceil(nominalCap * s))
	if concurrency < 1 {
		concurrency = 1
	}
	return serviceTimeMs, concurrency, nil
}

func applySchedule(client *http.Client, base string, schedule []CapacityStep, tSec float64) {
	var rate float64
	applied := false
	for _, s := range schedule {
		if tSec >= float64(s.AtSec) {
			rate = s.Rate
			applied = true
		}
	}
	if !applied {
		return
	}
	cur := getCapacity(client, base)
	if math.Abs(asFloat(cur["trueCapacity"])-rate) > 0.5 {
		_ = setCapacity(client, base, rate)
	}
}

func resetStream(ctx context.Context, js jetstream.JetStream, stream, durable string) error {
	_ = js.DeleteConsumer(ctx, stream, durable)
	_ = js.DeleteStream(ctx, stream)
	_, err := js.CreateStream(ctx, jetstream.StreamConfig{
		Name:      stream,
		Subjects:  []string{"events.>"},
		Storage:   jetstream.FileStorage,
		Retention: jetstream.LimitsPolicy,
		MaxAge:    24 * time.Hour,
	})
	if err != nil {
		return err
	}
	_, err = js.CreateConsumer(ctx, stream, jetstream.ConsumerConfig{
		Durable:       durable,
		FilterSubject: "events.orders",
		AckPolicy:     jetstream.AckExplicitPolicy,
		AckWait:       30 * time.Second,
	})
	return err
}

func pending(ctx context.Context, js jetstream.JetStream, stream, durable string) (int64, error) {
	cons, err := js.Consumer(ctx, stream, durable)
	if err != nil {
		return 0, err
	}
	info, err := cons.Info(ctx)
	if err != nil {
		return 0, err
	}
	return int64(info.NumPending), nil
}

func startCmd(name, bin string, envMap map[string]string) *exec.Cmd {
	cmd := exec.Command(bin)
	cmd.Env = os.Environ()
	for k, v := range envMap {
		cmd.Env = append(cmd.Env, k+"="+v)
	}
	cmd.Stdout = logWriter(name)
	cmd.Stderr = logWriter(name)
	if err := cmd.Start(); err != nil {
		log.Fatalf("start %s: %v", name, err)
	}
	log.Printf("started %s pid=%d", name, cmd.Process.Pid)
	return cmd
}

func stopCmd(cmd *exec.Cmd) {
	if cmd == nil || cmd.Process == nil {
		return
	}
	_ = cmd.Process.Signal(os.Interrupt)
	done := make(chan struct{})
	go func() {
		_ = cmd.Wait()
		close(done)
	}()
	select {
	case <-done:
	case <-time.After(3 * time.Second):
		_ = cmd.Process.Kill()
		<-done
	}
	log.Printf("stopped pid=%d", cmd.Process.Pid)
}

func logWriter(name string) io.Writer {
	return writerFunc(func(p []byte) (int, error) {
		log.Printf("[%s] %s", name, strings.TrimRight(string(p), "\n"))
		return len(p), nil
	})
}

type writerFunc func([]byte) (int, error)

func (f writerFunc) Write(p []byte) (int, error) { return f(p) }

const liveInjectorMaxInFlight = 4096 // sized from /noop ceiling ~8k rps; live λ_L=1000 needs headroom under ~2s latency

// InjectorStats is updated by the live injector for preflight / run records.
type InjectorStats struct {
	Issued          atomic.Int64
	Completed       atomic.Int64
	Drops429        atomic.Int64
	PeakInFlight    atomic.Int64
	CurrentInFlight atomic.Int64
}

// startLiveInjector open-loop POSTs to /process at the live rate and records
// samples as class=live into the JSONL file (tailed into memory once).
func startLiveInjector(wg *sync.WaitGroup, downstream string, rate float64, samplesPath string, mu *sync.Mutex, dst *[]Sample, stats *InjectorStats, stop <-chan struct{}) {
	_ = mu
	_ = dst
	if rate < 1 {
		rate = 1
	}
	transport := &http.Transport{
		MaxIdleConns:        4096,
		MaxIdleConnsPerHost: 4096,
		MaxConnsPerHost:     4096,
	}
	client := &http.Client{Timeout: 5 * time.Second, Transport: transport}

	f, err := os.OpenFile(samplesPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		log.Printf("live injector: open samples: %v", err)
		return
	}

	var bufMu sync.Mutex
	var buf bytes.Buffer
	flush := func() {
		bufMu.Lock()
		if buf.Len() == 0 {
			bufMu.Unlock()
			return
		}
		data := make([]byte, buf.Len())
		copy(data, buf.Bytes())
		buf.Reset()
		bufMu.Unlock()
		_, _ = f.Write(data) // syscall outside lock
	}

	interval := time.Duration(float64(time.Second) / rate)
	if interval < time.Microsecond {
		interval = time.Microsecond
	}

	log.Printf("live injector started rate=%.0f (open-loop, maxInFlight=%d)", rate, liveInjectorMaxInFlight)
	wg.Add(1)
	go func() {
		defer wg.Done()
		defer func() {
			flush()
			_ = f.Close()
		}()

		ticker := time.NewTicker(interval)
		defer ticker.Stop()
		flushTick := time.NewTicker(500 * time.Millisecond)
		defer flushTick.Stop()
		var inFlight sync.WaitGroup
		var nFlight atomic.Int64

		record := func(s Sample) {
			// File only — shared tailer loads into memory once (avoids double-count).
			b, _ := json.Marshal(s)
			bufMu.Lock()
			buf.Write(b)
			buf.WriteByte('\n')
			bufMu.Unlock()
		}

		for {
			select {
			case <-stop:
				inFlight.Wait()
				return
			case <-flushTick.C:
				flush()
			case <-ticker.C:
				stats.Issued.Add(1)
				cur := nFlight.Load()
				for {
					peak := stats.PeakInFlight.Load()
					if cur <= peak || stats.PeakInFlight.CompareAndSwap(peak, cur) {
						break
					}
				}
				if cur >= liveInjectorMaxInFlight {
					stats.Drops429.Add(1)
					record(Sample{TS: time.Now().UnixMilli(), Class: "live", LatencyMs: 0, Status: 429, AgeMs: 0})
					continue
				}
				nFlight.Add(1)
				stats.CurrentInFlight.Store(nFlight.Load())
				inFlight.Add(1)
				go func() {
					defer inFlight.Done()
					defer func() {
						nFlight.Add(-1)
						stats.CurrentInFlight.Store(nFlight.Load())
					}()
					start := time.Now()
					resp, err := client.Post(downstream+"/process", "text/plain", nil)
					lat := time.Since(start).Milliseconds()
					status := 0
					if err == nil {
						status = resp.StatusCode
						_, _ = io.Copy(io.Discard, resp.Body)
						resp.Body.Close()
					}
					stats.Completed.Add(1)
					record(Sample{
						TS:        time.Now().UnixMilli(),
						Class:     "live",
						LatencyMs: lat,
						Status:    status,
						AgeMs:     0,
					})
				}()
			}
		}
	}()
}

func tailSamples(path string, mu *sync.Mutex, dst *[]Sample) {
	var offset int64
	for {
		time.Sleep(200 * time.Millisecond)
		f, err := os.Open(path)
		if err != nil {
			continue
		}
		fi, err := f.Stat()
		if err != nil {
			f.Close()
			continue
		}
		if fi.Size() < offset {
			offset = 0
		}
		if _, err := f.Seek(offset, io.SeekStart); err != nil {
			f.Close()
			continue
		}
		buf, err := io.ReadAll(f)
		f.Close()
		if err != nil || len(buf) == 0 {
			continue
		}
		offset += int64(len(buf))
		lines := strings.Split(string(buf), "\n")
		mu.Lock()
		for _, line := range lines {
			line = strings.TrimSpace(line)
			if line == "" {
				continue
			}
			var s Sample
			if json.Unmarshal([]byte(line), &s) == nil {
				*dst = append(*dst, s)
			}
		}
		mu.Unlock()
	}
}

func trailing(samples []Sample, window time.Duration) []Sample {
	if len(samples) == 0 {
		return nil
	}
	cutoff := time.Now().UnixMilli() - window.Milliseconds()
	var out []Sample
	for i := len(samples) - 1; i >= 0; i-- {
		if samples[i].TS < cutoff {
			break
		}
		out = append(out, samples[i])
	}
	return out
}

func countClass(samples []Sample, class string) int64 {
	var n int64
	for _, s := range samples {
		if s.Class == class {
			n++
		}
	}
	return n
}

func classRPS(samples []Sample, windowSec float64) (liveRps, recRps float64) {
	if windowSec <= 0 {
		windowSec = 1
	}
	var live, rec int
	for _, s := range samples {
		if s.Status == 429 {
			continue // client drop — not an delivered live request
		}
		switch s.Class {
		case "live":
			live++
		case "recovery":
			rec++
		}
	}
	return float64(live) / windowSec, float64(rec) / windowSec
}

// classRPSInjectorLive counts only injector-direct live (age_ms==0).
func classRPSInjectorLive(samples []Sample, windowSec float64) (liveRps, recRps float64) {
	if windowSec <= 0 {
		windowSec = 1
	}
	var live, rec int
	for _, s := range samples {
		if s.Status == 429 {
			continue
		}
		switch s.Class {
		case "live":
			if s.AgeMs == 0 {
				live++
			}
		case "recovery":
			rec++
		}
	}
	return float64(live) / windowSec, float64(rec) / windowSec
}

func windowMetrics(samples []Sample) (liveP99, recP99, errRate float64) {
	var live, rec []float64
	var total, errs int
	for _, s := range samples {
		// Status 429 = live-injector client-side drop (maxInFlight). Not a
		// downstream signal — exclude from SLO error accounting (P0-B artifact).
		if s.Status == 429 {
			continue
		}
		total++
		if s.Status != 200 {
			errs++
			continue
		}
		if s.Class == "recovery" {
			rec = append(rec, float64(s.LatencyMs))
		} else {
			live = append(live, float64(s.LatencyMs))
		}
	}
	sort.Float64s(live)
	sort.Float64s(rec)
	return pct(live, 0.99), pct(rec, 0.99), float64(errs) / max1(float64(total))
}

// windowMetricsInjectorLive: live p99/error from injector-direct samples only;
// recovery p99 unchanged. Error rate is over injector+recovery (excl 429).
func windowMetricsInjectorLive(samples []Sample) (liveP99, recP99, errRate float64) {
	var live, rec []float64
	var total, errs int
	for _, s := range samples {
		if s.Status == 429 {
			continue
		}
		isInj := s.Class == "live" && s.AgeMs == 0
		isRec := s.Class == "recovery"
		if !isInj && !isRec {
			continue // NATS-live excluded from SLO accounting
		}
		total++
		if s.Status != 200 {
			errs++
			continue
		}
		if isRec {
			rec = append(rec, float64(s.LatencyMs))
		} else {
			live = append(live, float64(s.LatencyMs))
		}
	}
	sort.Float64s(live)
	sort.Float64s(rec)
	return pct(live, 0.99), pct(rec, 0.99), float64(errs) / max1(float64(total))
}

func computeSupplementary(samples []Sample, timeline []TimelinePoint, tDrain, sloP99 float64, queueSum float64, queueN, queuePeak int64) *Supplementary {
	s := &Supplementary{QueueDepthPeak: queuePeak}
	if queueN > 0 {
		s.QueueDepthMean = queueSum / float64(queueN)
	}
	// Whole-run injector-live from samples
	fillLiveSupp(samples, 0, math.MaxInt64, sloP99, &s.LiveP50Ms, &s.LiveP90Ms, &s.LiveP95Ms, &s.LiveP99Ms, &s.FractionUnderSLO, &s.GoodputRpsMean, &s.TimeoutRate)
	// Drain window: need restore epoch from sample timestamps — use timeline tDrain
	// Samples are post-clear; t=0 ≈ min sample ts. Approximate drain end = minTS + tDrain*1000.
	minTS := int64(0)
	for _, sm := range samples {
		if sm.Class == "live" && sm.AgeMs == 0 {
			minTS = sm.TS
			break
		}
	}
	if minTS == 0 && len(samples) > 0 {
		minTS = samples[0].TS
	}
	drainEnd := minTS + int64(tDrain*1000)
	fillLiveSupp(samples, minTS, drainEnd, sloP99, &s.DrainLiveP50Ms, &s.DrainLiveP90Ms, &s.DrainLiveP95Ms, &s.DrainLiveP99Ms, &s.DrainFractionUnderSLO, &s.DrainGoodputRpsMean, &s.DrainTimeoutRate)

	var dqSum float64
	var dqN, dqPeak int64
	for _, p := range timeline {
		if p.TSec <= tDrain+0.5 {
			dqSum += float64(p.Queued)
			dqN++
			if p.Queued > dqPeak {
				dqPeak = p.Queued
			}
		}
	}
	s.DrainQueueDepthPeak = dqPeak
	if dqN > 0 {
		s.DrainQueueDepthMean = dqSum / float64(dqN)
	}
	return s
}

func fillLiveSupp(samples []Sample, t0, t1 int64, sloP99 float64, p50, p90, p95, p99, frac, goodput, timeoutRate *float64) {
	var lats []float64
	var okSLO, total, timeouts, good int
	var minTS, maxTS int64
	for _, s := range samples {
		if s.Class != "live" || s.AgeMs != 0 {
			continue
		}
		if s.TS < t0 || s.TS > t1 {
			continue
		}
		if s.Status == 429 {
			continue
		}
		total++
		if minTS == 0 || s.TS < minTS {
			minTS = s.TS
		}
		if s.TS > maxTS {
			maxTS = s.TS
		}
		if s.Status == 504 {
			timeouts++
		}
		if s.Status == 200 {
			lats = append(lats, float64(s.LatencyMs))
			if float64(s.LatencyMs) <= sloP99 {
				okSLO++
				good++
			}
		}
	}
	sort.Float64s(lats)
	*p50 = pct(lats, 0.50)
	*p90 = pct(lats, 0.90)
	*p95 = pct(lats, 0.95)
	*p99 = pct(lats, 0.99)
	if total > 0 {
		*frac = float64(okSLO) / float64(total)
		*timeoutRate = float64(timeouts) / float64(total)
	}
	wall := float64(maxTS-minTS) / 1000.0
	if wall > 0 {
		*goodput = float64(good) / wall
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

func waitSLO(client *http.Client, base string, mu *sync.Mutex, samples *[]Sample, dur time.Duration, sloP99, sloErr float64, class string) (bool, string) {
	_ = client
	_ = base
	_ = class
	deadline := time.Now().Add(dur * 3) // allow retries before giving up
	okSince := time.Time{}
	var lastP99, lastErr float64
	for time.Now().Before(deadline) {
		time.Sleep(time.Second)
		mu.Lock()
		window := trailing(*samples, 5*time.Second)
		mu.Unlock()
		liveP99, _, errRate := windowMetricsInjectorLive(window)
		lastP99, lastErr = liveP99, errRate
		if liveP99 > 0 && liveP99 <= sloP99 && errRate <= sloErr {
			if okSince.IsZero() {
				okSince = time.Now()
			}
			if time.Since(okSince) >= dur {
				return true, ""
			}
		} else {
			okSince = time.Time{}
		}
	}
	return false, fmt.Sprintf("liveP99=%.1f err=%.3f", lastP99, lastErr)
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
	return nil
}

func getCapacity(client *http.Client, base string) map[string]any {
	return getJSON(client, base+"/admin/capacity")
}

func getStats(client *http.Client, base string) map[string]any {
	return getJSON(client, base+"/admin/stats")
}

func getJSON(client *http.Client, url string) map[string]any {
	resp, err := client.Get(url)
	if err != nil {
		return map[string]any{}
	}
	defer resp.Body.Close()
	var m map[string]any
	_ = json.NewDecoder(resp.Body).Decode(&m)
	return m
}

func asFloat(v any) float64 {
	switch x := v.(type) {
	case float64:
		return x
	case int:
		return float64(x)
	case int64:
		return float64(x)
	case json.Number:
		f, _ := x.Float64()
		return f
	default:
		return 0
	}
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
	return fmt.Errorf("healthz timeout")
}

func writeRecord(dir string, rec RunRecord) string {
	_ = os.MkdirAll(dir, 0o755)
	path := filepath.Join(dir, rec.RunID+".json")
	b, _ := json.MarshalIndent(rec, "", "  ")
	_ = os.WriteFile(path, b, 0o644)
	return path
}

func gitInfo() (string, bool) {
	commit := "unknown"
	out, err := exec.Command("git", "rev-parse", "--short", "HEAD").Output()
	if err == nil {
		commit = strings.TrimSpace(string(out))
	}
	dirty := false
	out, err = exec.Command("git", "status", "--porcelain").Output()
	if err == nil && len(strings.TrimSpace(string(out))) > 0 {
		dirty = true
	}
	return commit, dirty
}

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}
