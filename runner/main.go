// The 2026-08-19 changes in this file were reconstructed from the 2026-08-19 session log; original was never committed.
// See RECONSTRUCTION.md.

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
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"syscall"
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
	TSec              float64 `json:"tSec"`
	Backlog           int64   `json:"backlog"` // deprecated alias of totalPending
	TotalPending      int64   `json:"totalPending"`
	RecoveryRemaining int64   `json:"recoveryRemaining"`
	RecoveryAcked     int64   `json:"recoveryAcked"`
	LiveInFlight      int64   `json:"liveInFlight"`
	LiveRps           float64 `json:"liveRps"`
	// Injector ISSUE rate — authoritative. LiveRps is a 5s trailing
	// completion-window estimate and reads ~0.8x truth by construction.
	InjRate       float64 `json:"injRate"`
	RecoveryRps   float64 `json:"recoveryRps"`
	TrueCapacity  float64 `json:"trueCapacity"`
	OfferedRate   float64 `json:"offeredRate"`
	Queued        int64   `json:"queued"`
	Served        int64   `json:"served"`
	Rejected      int64   `json:"rejected"`
	TimedOut      int64   `json:"timedOut"`
	LiveP99Ms     float64 `json:"liveP99Ms"`
	RecoveryP99Ms float64 `json:"recoveryP99Ms"`
	ErrorRate     float64 `json:"errorRate"`
	// Host-stall (measurement-artifact) detection, per second.
	LiveP99Ms1s     float64 `json:"liveP99Ms1s"`
	RecoveryP99Ms1s float64 `json:"recoveryP99Ms1s"`
	MaxGapMs        int64   `json:"maxGapMs"`
	StallSecond     bool    `json:"stallSecond,omitempty"`
	Contaminated    bool    `json:"contaminated,omitempty"`
}

type RunRecord struct {
	RunID            string          `json:"runId"`
	Condition        string          `json:"condition"`
	GitCommit        string          `json:"gitCommit"` // short (12-hex) HEAD; runner refuses to start if unresolvable
	GitCommitFull    string          `json:"gitCommitFull"`
	GitBranch        string          `json:"gitBranch"`
	GitDirty         bool            `json:"gitDirty"` // uncommitted changes outside results/ and bin/
	GitDirtyFiles    []string        `json:"gitDirtyFiles,omitempty"`
	StartedAt        string          `json:"startedAt"`
	Params           map[string]any  `json:"params"`
	BacklogAtRestore int64           `json:"backlogAtRestore"`
	RestoreEpochMs   int64           `json:"restoreEpochMs"`
	CapacitySchedule []CapacityStep  `json:"capacitySchedule"`
	HeadroomSchedule []HeadroomStep  `json:"headroomSchedule"`
	Timeline         []TimelinePoint `json:"timeline"`
	TDrainSec        float64         `json:"tDrainSec"`
	TFullSec         float64         `json:"tFullSec"`    // primary: W from params.stabilizeSeconds
	TFullSecW30      float64         `json:"tFullSecW30"` // sensitivity: same run, W=30s
	VSLO             float64         `json:"vSLO"`        // violations / tFullSec (W primary), artifact-excluded
	VSLORaw          float64         `json:"vSLO_raw"`    // before host-stall exclusion
	// vSLO decomposed by which predicate fired. vSLO alone cannot distinguish
	// "dependency sheds load, live stays fast" (cliff: p99 19ms, error-driven)
	// from "live traffic times out" (graceful: p99 ~2000ms, latency-driven) --
	// it read 0.778 vs 0.868 across a 100x p99 difference. Always report both.
	VSLOLatency       float64        `json:"vSLO_latency"`
	VSLOError         float64        `json:"vSLO_error"`
	VSLOBoth          float64        `json:"vSLO_both"`
	VSLOW30           float64        `json:"vSLO_W30,omitempty"`
	TDrainReached     bool           `json:"tDrainReached"`
	FaultWindowSec    []float64      `json:"faultWindowSec,omitempty"`
	FaultVSLO         float64        `json:"faultVSLO"`
	TimeToHealthSec   float64        `json:"timeToHealthAfterRestoreSec"`
	StallSeconds      int            `json:"stallSeconds"`
	ContaminatedSecs  int            `json:"contaminatedSeconds"`
	StallDetector     map[string]any `json:"stallDetector,omitempty"`
	PeakOfferedRate   float64        `json:"peakOfferedRate"`
	Amplification     float64        `json:"amplification"`
	LiveSLOPopulation string         `json:"liveSLOPopulation,omitempty"`
	Supplementary     *Supplementary `json:"supplementary,omitempty"`
	Aborted           string         `json:"aborted,omitempty"`
	Invalid           bool           `json:"invalid,omitempty"`
	InvalidReason     string         `json:"invalidReason,omitempty"`
}

// Supplementary metrics for Phase 1 frontier axes (p99/V_SLO may be degenerate).
type Supplementary struct {
	TimeoutRate             float64 `json:"timeoutRate"`
	LiveP50Ms               float64 `json:"liveP50Ms"`
	LiveP90Ms               float64 `json:"liveP90Ms"`
	LiveP95Ms               float64 `json:"liveP95Ms"`
	LiveP99Ms               float64 `json:"liveP99Ms"`
	FractionUnderSLO        float64 `json:"fractionUnderSLO250ms"`
	QueueDepthMean          float64 `json:"queueDepthMean"`
	QueueDepthPeak          int64   `json:"queueDepthPeak"`
	GoodputRpsMean          float64 `json:"goodputRpsMean"` // successful & latency<=SLO / wall
	DrainTimeoutRate        float64 `json:"drainTimeoutRate"`
	DrainLiveP50Ms          float64 `json:"drainLiveP50Ms"`
	DrainLiveP90Ms          float64 `json:"drainLiveP90Ms"`
	DrainLiveP95Ms          float64 `json:"drainLiveP95Ms"`
	DrainLiveP99Ms          float64 `json:"drainLiveP99Ms"`
	DrainFractionUnderSLO   float64 `json:"drainFractionUnderSLO250ms"`
	DrainGoodputRpsMean     float64 `json:"drainGoodputRpsMean"`
	DrainQueueDepthMean     float64 `json:"drainQueueDepthMean"`
	DrainQueueDepthPeak     int64   `json:"drainQueueDepthPeak"`
	ArtifactExcludedSamples int64   `json:"artifactExcludedSamples"`
	FaultLiveP50Ms          float64 `json:"faultLiveP50Ms"`
	FaultLiveP99Ms          float64 `json:"faultLiveP99Ms"`
	FaultFractionUnderSLO   float64 `json:"faultFractionUnderSLO250ms"`
	FaultGoodputRpsMean     float64 `json:"faultGoodputRpsMean"`
	FaultTimeoutRate        float64 `json:"faultTimeoutRate"`
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
	rateLimit := flag.Int("rate-limit", 0, "consumer recovery rate limit rps (0=unrestricted, -1=suspended: admit nothing)")
	horizonSec := flag.Int("horizon", 0, "fixed run horizon in seconds (0=run until drain+stabilize). Required for -rate-limit -1, which never drains.")
	natsURL := flag.String("nats", env("NATS_URL", "nats://127.0.0.1:14222"), "NATS URL")
	downstream := flag.String("downstream", env("DOWNSTREAM_URL", "http://127.0.0.1:8080"), "downstream URL")
	resultsDir := flag.String("results", "results", "results directory")
	stallP99Factor := flag.Float64("stall-p99-factor", 5.0, "host-stall: live AND recovery 1s p99 must exceed this factor over rolling baseline")
	stallQueuedMax := flag.Int64("stall-queued-max", 5, "host-stall: downstream queued must be at or below this")
	stallGapMs := flag.Int64("stall-gap-ms", 150, "host-stall: max inter-sample gap in the request stream must exceed this")
	rateDevFrac := flag.Float64("rate-dev-frac", 0.90, "integrity: achieved live rps below this fraction of target for >=N consecutive seconds is INVALID")
	injectorPacer := flag.String("injector-pacer", "ticker", "ticker|lanes — live injector arrival process. DEFAULT ticker: what all of Phase 1 used. It drops ticks under load (98.4-99.8% of lambda_L, arm-dependent) but stays evenly spaced. `lanes` delivers the exact rate in isolation (qMean 0.1 at 1000 rps vs ticker's 20) but degrades under the consumer's 1024 competing goroutines, collapsing the rl=840 safe anchor even at rho_ach=0.906.")
	genTolerance := flag.Float64("gen-tolerance", 0.01, "generator self-check: injector rate must be within this fraction of target during warm-up, else refuse the run")
	maxLoad5Frac := flag.Float64("max-load5-per-core", 1.0, "integrity: refuse to start if the 5-minute load average exceeds cores x this. 0 disables")
	minFreeDiskGB := flag.Float64("min-free-disk-gb", 5.0, "integrity: refuse to start if free disk is below this. 0 disables")
	rateDevSecs := flag.Int("rate-dev-secs", 2, "integrity: consecutive seconds of sustained live-rate deviation before INVALID")
	flag.Parse()

	// Provenance first: refuse before touching NATS or the downstream.
	gi, err := gitInfo()
	if err != nil {
		log.Fatalf("provenance: %v — results must be tied to a revision; run the runner from inside the git checkout that built it", err)
	}
	if gi.dirty {
		log.Printf("WARNING: working tree is DIRTY at %s (%d uncommitted change(s) outside results/ and bin/): %s — the run record marks gitDirty=true; results are not reproducible from the recorded commit",
			gi.short, len(gi.dirtyFiles), strings.Join(gi.dirtyFiles, ", "))
	} else {
		log.Printf("provenance: clean at %s (%s)", gi.short, gi.branch)
	}

	if *runID == "" {
		*runID = fmt.Sprintf("%s-%s", strings.ToLower(*condition), time.Now().Format("20060102-150405"))
	}

	schedule := scheduleFor(*condition, *nominalCap, *liveRate)
	headroom := headroomSchedule(schedule, *liveRate)
	host, hostErr := hostState()
	if hostErr != nil {
		log.Printf("WARNING: host state unavailable (%v); load and disk guards skipped", hostErr)
	} else {
		log.Printf("host: load %.2f/%.2f/%.2f on %d cores, free disk %.1f GB",
			host.Load1, host.Load5, host.Load15, host.Cores, host.FreeDiskGB)
		if *maxLoad5Frac > 0 && host.Load5 > float64(host.Cores)**maxLoad5Frac {
			log.Fatalf("host load too high: 5-minute average %.2f exceeds %d cores x %.2f = %.2f. "+
				"Measurements taken under self-inflicted load are not trustworthy -- the 2026-08-19 "+
				"pacer conclusions were withdrawn for exactly this reason. Wait for the load to fall, "+
				"or pass -max-load5-per-core 0 to record an explicitly untrustworthy run.",
				host.Load5, host.Cores, *maxLoad5Frac, float64(host.Cores)**maxLoad5Frac)
		}
		if *minFreeDiskGB > 0 && host.FreeDiskGB < *minFreeDiskGB {
			log.Fatalf("free disk %.1f GB is below the %.1f GB floor. A full disk silently truncates "+
				"consumer traces to 0 bytes, which is how several 2026-08-19 runs lost their raw data. "+
				"Free space, or pass -min-free-disk-gb 0.", host.FreeDiskGB, *minFreeDiskGB)
		}
	}

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
	// SPEC step 1: reset the downstream to nominal capacity BEFORE asserting the
	// arm. A preceding P0-B/C/D run leaves capacity at its fault value, and the
	// arm guard reads live concurrency — so without this reset the guard refuses
	// the next run with a spurious mismatch (observed: "expects concurrency=10
	// but downstream has 7" after a P0-B run left C=1400).
	setCapacity(client, *downstream, *nominalCap)
	time.Sleep(300 * time.Millisecond)
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

	commit, dirty := gi.short, gi.dirty

	rec := RunRecord{
		RunID:            *runID,
		Condition:        *condition,
		GitCommit:        commit,
		GitCommitFull:    gi.commit,
		GitBranch:        gi.branch,
		GitDirty:         dirty,
		GitDirtyFiles:    gi.dirtyFiles,
		StartedAt:        time.Now().UTC().Format(time.RFC3339),
		CapacitySchedule: schedule,
		HeadroomSchedule: headroom,
		Params: map[string]any{
			"liveRatePerSec":          *liveRate,
			"nominalCapacity":         *nominalCap,
			"outageSeconds":           *outageSec,
			"serviceTimeMs":           *serviceTimeMs,
			"concurrencyArm":          *arm,
			"downstreamServiceTimeMs": dsSvcMs,
			"downstreamConcurrency":   dsConc,
			"downstreamQueueCap":      asFloat(dsCap["queueCap"]),
			// How the cap was chosen, and the wait a request faces when it is
			// admitted to a full queue. Under the default profile-relative cap
			// this delay is 50 x S, which equals the 250 ms SLO at S=5 ms and is
			// 1250 ms at S=25 ms -- so "queue full" means "SLO breach" in one arm
			// and not the other. Recorded per run so the two can be separated.
			"downstreamQueueCapMode":     dsCap["queueCapMode"],
			"downstreamFullQueueDelayMs": asFloat(dsCap["fullQueueDelayMs"]),
			"profile":                    *profile,
			"workers":                    *workers,
			// Host condition at run start. A busy host distorts timing windows and a
			// full disk truncates traces, and neither is visible in the results
			// afterwards -- both happened on 2026-08-19.
			"hostLoad1":              host.Load1,
			"hostLoad5":              host.Load5,
			"hostLoad15":             host.Load15,
			"hostCores":              host.Cores,
			"hostFreeDiskGB":         host.FreeDiskGB,
			"sloP99Ms":               *sloP99,
			"sloErrorRate":           *sloErr,
			"rateLimitRps":           *rateLimit,
			"maxInFlight":            liveInjectorMaxInFlight,
			"sloErrorAccounting":     "exclude_status_429_client_injector_drops",
			"stabilizeSeconds":       *stabilizeSec,
			"stabilizeW30Seconds":    *stabilizeW30Sec,
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
		if *rateLimit != 0 {
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
	rec.Params["injectorPacer"] = *injectorPacer
	startLiveInjector(&liveWG, *downstream, *liveRate, samplesPath, &sampleMu, &samples, &injStats, liveStop, *injectorPacer)
	defer stopLive()
	go tailSamples(samplesPath, &sampleMu, &samples)

	log.Printf("warmup %ds (injector-only)", *warmupSec)
	warmIssued0 := injStats.Issued.Load()
	warmT0 := time.Now()
	time.Sleep(time.Duration(*warmupSec) * time.Second)

	// Generator self-check. The load generator must deliver the rate it claims:
	// a time.Ticker-based pacer silently under-delivers under its own
	// concurrency pressure and that went unnoticed for an entire campaign.
	// Measured on the injector issue counter over the warm-up window.
	warmRate := float64(injStats.Issued.Load()-warmIssued0) / time.Since(warmT0).Seconds()
	warmAcc := warmRate / *liveRate
	rec.Params["warmupInjectorRps"] = warmRate
	rec.Params["warmupInjectorAccuracy"] = warmAcc
	log.Printf("generator self-check: injector %.1f rps vs target %.0f (%.2f%% of target)",
		warmRate, *liveRate, warmAcc*100)
	if math.Abs(warmAcc-1.0) > *genTolerance {
		rec.Invalid = true
		rec.InvalidReason = "generator_rate_deviation_at_warmup"
		rec.Aborted = fmt.Sprintf("injector delivered %.1f rps vs target %.0f (%.2f%%), outside +/-%.1f%%",
			warmRate, *liveRate, warmAcc*100, *genTolerance*100)
		writeRecord(*resultsDir, rec)
		log.Fatalf("abort: %s", rec.Aborted)
	}

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
		timeline            []TimelinePoint
		peakOffered         float64
		drainAt             time.Time
		fullAt              time.Time // primary W
		fullAtW30           time.Time
		healthyStreak       time.Duration
		violationSecs       float64
		zeroLiveStreak      time.Duration
		zeroRecStreak       time.Duration
		queueSum            float64
		queueN              int64
		queuePeak           int64
		violationAtFull     float64
		drainCompleteStreak time.Duration
		// Host-stall (measurement-artifact) detector state.
		p99Baseline        []float64 // rolling history of healthy 1s live p99
		recBaseline        []float64
		stallSecs          int
		contamSecs         int
		lastStallTSec      = math.Inf(-1)
		violationsRaw      float64
		violationAtFullRaw float64
		contamAtFull       int
		rateDevStreak      int
		violLatency        float64
		violError          float64
		violBoth           float64
		faultSecs          float64
		faultViolations    float64
		postRestoreHealthy int
		timeToHealth       = -1.0
	)
	faultStart, faultEnd := faultWindow(schedule, *nominalCap)
	if faultStart >= 0 {
		log.Printf("fault window: t=[%.0f,%.0f)s", faultStart, faultEnd)
	}

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

		// --- Host-stall (measurement-artifact) detection -------------------
		// A second is a stall when ALL hold: live AND recovery 1s p99 both
		// spike by >= stallP99Factor over their rolling healthy baseline, the
		// downstream queue is at/near zero (so the dependency was idle, i.e.
		// this is not saturation), and the request stream itself shows an
		// inter-sample gap above stallGapMs. Criteria are fixed in advance;
		// flagged seconds are counted and reported, never silently dropped.
		sampleMu.Lock()
		win1 := trailing(samples, time.Second)
		win2 := trailing(samples, 2*time.Second)
		sampleMu.Unlock()
		liveP99_1s, recP99_1s, _ := windowMetricsInjectorLive(win1)
		maxGapMs := maxInterSampleGapMs(win2)

		isStall := false
		if len(p99Baseline) >= 10 && len(recBaseline) >= 10 {
			bl := median(p99Baseline)
			br := median(recBaseline)
			if bl > 0 && br > 0 &&
				liveP99_1s >= *stallP99Factor*bl &&
				recP99_1s >= *stallP99Factor*br &&
				int64(asFloat(st["queued"])) <= *stallQueuedMax &&
				maxGapMs > *stallGapMs {
				isStall = true
			}
		}
		if isStall {
			stallSecs++
			lastStallTSec = tSec
			log.Printf("STALL t=%.1fs liveP99_1s=%.0f recP99_1s=%.0f queued=%d maxGap=%dms (measurement artifact)",
				tSec, liveP99_1s, recP99_1s, int64(asFloat(st["queued"])), maxGapMs)
		} else if liveP99_1s > 0 && recP99_1s > 0 {
			p99Baseline = appendCapped(p99Baseline, liveP99_1s, 30)
			recBaseline = appendCapped(recBaseline, recP99_1s, 30)
		}
		// The reported liveP99/errRate come from a 5s trailing window, so a
		// single stalled second contaminates the following 5 seconds too.
		contaminated := isStall || (tSec-lastStallTSec) < 5.0
		if contaminated {
			contamSecs++
		}

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
			InjRate:           injRate,
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
			LiveP99Ms1s:       liveP99_1s,
			RecoveryP99Ms1s:   recP99_1s,
			MaxGapMs:          maxGapMs,
			StallSecond:       isStall,
			Contaminated:      contaminated,
		}
		timeline = append(timeline, pt)
		log.Printf("t=%6.1fs pending=%d recLeft=%d liveRps=%.0f injRate=%.0f recRps=%.0f cap=%.0f offered=%.0f liveP99=%.0f err=%.3f",
			tSec, totalPending, recoveryRemaining, liveRps, injRate, recRps, pt.TrueCapacity, offered, liveP99, errRate)

		latBreach := liveP99 > *sloP99
		errBreach := errRate > *sloErr
		liveViolating := latBreach || errBreach
		if liveViolating {
			violationsRaw += 1
			if !contaminated {
				violationSecs += 1
				if latBreach {
					violLatency += 1
				}
				if errBreach {
					violError += 1
				}
				if latBreach && errBreach {
					violBoth += 1
				}
			}
		}
		// Fault-window SLO, reported separately from the whole run. Under C3
		// the fault capacity sits below lambda_L, so live alone is over
		// capacity even with zero recovery admission.
		if faultStart >= 0 && tSec >= faultStart && tSec < faultEnd {
			faultSecs++
			if liveViolating && !contaminated {
				faultViolations++
			}
		}
		// Time to health after capacity restoration: first second of a 3s
		// healthy streak at or after the fault window ends.
		if faultEnd >= 0 && tSec >= faultEnd {
			if !liveViolating && liveP99 > 0 && !contaminated {
				postRestoreHealthy++
				if postRestoreHealthy == 3 && timeToHealth < 0 {
					timeToHealth = (tSec - 2) - faultEnd
				}
			} else {
				postRestoreHealthy = 0
			}
		}

		if *horizonSec > 0 && tSec >= float64(*horizonSec) {
			log.Printf("horizon %ds reached at t=%.1fs (drainReached=%v)", *horizonSec, tSec, !drainAt.IsZero())
			violationAtFull = violationSecs
			violationAtFullRaw = violationsRaw
			contamAtFull = contamSecs
			break
		}

		// Integrity: injector must keep issuing from restore through T_full.
		if injRate <= 0 {
			rec.Invalid = true
			rec.InvalidReason = "zero_injector_rate_before_tfull"
			rec.Aborted = "injector issue rate was zero between restore and T_full"
			log.Printf("INVALID: %s (t=%.1fs)", rec.Aborted, tSec)
			break
		}

		// Integrity: sustained live-rate deviation. The zero-rate checks only
		// fire on a full stall; partial degradation (e.g. 517/s against a
		// 1000/s target) passed every previous check. Uses the injector issue
		// counter, not the 5s completion window, which reads ~0.8x by design.
		if injRate < (*rateDevFrac)*(*liveRate) && !contaminated {
			rateDevStreak++
		} else {
			rateDevStreak = 0
		}
		if rateDevStreak >= *rateDevSecs {
			rec.Invalid = true
			rec.InvalidReason = "sustained_live_rate_deviation"
			rec.Aborted = fmt.Sprintf("injector issue rate below %.0f%% of target (%.0f rps) for >=%ds",
				*rateDevFrac*100, *liveRate, *rateDevSecs)
			log.Printf("INVALID: %s (t=%.1fs injRate=%.0f)", rec.Aborted, tSec, injRate)
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
			if zeroRecStreak >= 3*time.Second && recoveryRemaining >= minRem && *rateLimit >= 0 {
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
			violationAtFullRaw = violationsRaw
			contamAtFull = contamSecs
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
	rec.TDrainReached = !drainAt.IsZero()
	if !rec.TDrainReached {
		rec.TDrainSec = -1 // not reached (suspended recovery / horizon stop)
	}
	if faultStart >= 0 {
		rec.FaultWindowSec = []float64{faultStart, faultEnd}
		if faultSecs > 0 {
			rec.FaultVSLO = faultViolations / faultSecs
		}
	}
	rec.TimeToHealthSec = timeToHealth
	rec.StallSeconds = stallSecs
	rec.ContaminatedSecs = contamAtFull
	rec.StallDetector = map[string]any{
		"p99Factor":        *stallP99Factor,
		"queuedMax":        *stallQueuedMax,
		"gapMs":            *stallGapMs,
		"contaminationSec": 5,
		"baselineWindow":   30,
		"rateDevFrac":      *rateDevFrac,
		"rateDevSecs":      *rateDevSecs,
		"note":             "second flagged when live AND recovery 1s p99 both exceed p99Factor x rolling baseline while downstream queued<=queuedMax and max inter-sample gap>gapMs; the 5s reporting window means each stall contaminates the following contaminationSec seconds. Flagged seconds are excluded from vSLO (numerator and denominator) and from latency percentiles. vSLO_raw is the unexcluded value.",
	}
	if rec.TFullSec > 0 {
		den := rec.TFullSec - float64(contamAtFull)
		if den <= 0 {
			den = rec.TFullSec
		}
		rec.VSLO = violationAtFull / den
		rec.VSLORaw = violationAtFullRaw / rec.TFullSec
		rec.VSLOLatency = violLatency / den
		rec.VSLOError = violError / den
		rec.VSLOBoth = violBoth / den
	}
	if rec.TFullSecW30 > 0 {
		denW30 := rec.TFullSecW30 - float64(contamSecs)
		if denW30 <= 0 {
			denW30 = rec.TFullSecW30
		}
		rec.VSLOW30 = violationSecs / denW30
	}
	rec.PeakOfferedRate = peakOffered
	if *liveRate > 0 {
		rec.Amplification = peakOffered / *liveRate
	}

	sampleMu.Lock()
	allSamples := append([]Sample(nil), samples...)
	sampleMu.Unlock()
	rec.Supplementary = computeSupplementary(allSamples, timeline, rec.TDrainSec, *sloP99, queueSum, queueN, queuePeak, artifactRanges(timeline, rec.RestoreEpochMs), rec.FaultWindowSec, rec.RestoreEpochMs)

	path := writeRecord(*resultsDir, rec)
	log.Printf("wrote %s tDrain=%.1f tFull(W=%d)=%.1f tFull(W30)=%.1f vSLO=%.3f (lat %.3f err %.3f) faultVSLO=%.3f t2health=%.0f stallSec=%d contamSec=%d",
		path, rec.TDrainSec, *stabilizeSec, rec.TFullSec, rec.TFullSecW30, rec.VSLO, rec.VSLOLatency, rec.VSLOError, rec.FaultVSLO, rec.TimeToHealthSec, rec.StallSeconds, rec.ContaminatedSecs)
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

// faultWindow returns [start,end) seconds where scheduled capacity is below
// nominal. For P0-D (C3) that is [20,90); for P0-C (C2) [20,60).
func faultWindow(schedule []CapacityStep, nominal float64) (float64, float64) {
	start, end := -1.0, -1.0
	for _, st := range schedule {
		if st.Rate < nominal && start < 0 {
			start = float64(st.AtSec)
		} else if st.Rate >= nominal && start >= 0 && end < 0 {
			end = float64(st.AtSec)
		}
	}
	return start, end
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
func startLiveInjector(wg *sync.WaitGroup, downstream string, rate float64, samplesPath string, mu *sync.Mutex, dst *[]Sample, stats *InjectorStats, stop <-chan struct{}, pacer string) {
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

	log.Printf("live injector started rate=%.0f (open-loop, maxInFlight=%d)", rate, liveInjectorMaxInFlight)
	wg.Add(1)
	go func() {
		defer wg.Done()
		defer func() {
			flush()
			_ = f.Close()
		}()

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

		// Multi-lane deadline pacer. A single time.Ticker DROPS ticks when the
		// receiver is late, so delivered rate degraded with in-flight count:
		// 99.2-100% of lambda_L at S=5 but only 98.4-98.7% at S=25 (~25 vs ~5
		// goroutines in flight), a systematic between-arm bias in every c10/c50
		// comparison. Splitting the rate across lanes keeps each lane's interval
		// >= ~5ms (above OS timer granularity) and phase-staggers them; each lane
		// sleeps to its own next deadline and issues exactly one request, so
		// lateness self-corrects without bunching arrivals.
		lanes := int(math.Ceil(rate / 200.0))
		if lanes < 1 {
			lanes = 1
		}
		if lanes > 64 {
			lanes = 64
		}
		laneInterval := time.Duration(float64(lanes) * float64(time.Second) / rate)

		issueOne := func() {
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
				return
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

		var pacers sync.WaitGroup
		if pacer == "ticker" {
			pacers.Add(1)
			go func() {
				defer pacers.Done()
				tk := time.NewTicker(time.Duration(float64(time.Second) / rate))
				defer tk.Stop()
				for {
					select {
					case <-stop:
						return
					case <-tk.C:
						issueOne()
					}
				}
			}()
			goto paced
		}
		for L := 0; L < lanes; L++ {
			pacers.Add(1)
			go func(L int) {
				defer pacers.Done()
				time.Sleep(time.Duration(int64(L) * int64(laneInterval) / int64(lanes)))
				next := time.Now()
				for {
					next = next.Add(laneInterval)
					// BOUNDED catch-up. An unbounded pacer that is late fires the
					// missed slots back-to-back, which restores the mean rate but
					// bunches arrivals: at offered 1850 that produced qMean 44.8
					// against the ticker's 2.1 (21x), and collapsed the rl=840
					// safe anchor. If a lane is more than one interval late, drop
					// the missed slots instead of discharging them as a burst.
					// Rate loss is confined to genuine stalls, which the
					// generator self-check and sustained-rate check already catch.
					if time.Since(next) > laneInterval {
						next = time.Now()
					}
					if d := time.Until(next); d > 0 {
						t := time.NewTimer(d)
						select {
						case <-stop:
							t.Stop()
							return
						case <-t.C:
						}
					}
					select {
					case <-stop:
						return
					default:
					}
					issueOne()
				}
			}(L)
		}

	paced:
		for {
			select {
			case <-stop:
				pacers.Wait()
				inFlight.Wait()
				flush()
				return
			case <-flushTick.C:
				flush()
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

type tsRange struct{ lo, hi int64 }

// artifactRanges converts contaminated timeline seconds into absolute-time
// windows so their samples can be excluded from latency percentiles.
func artifactRanges(timeline []TimelinePoint, restoreEpochMs int64) []tsRange {
	var out []tsRange
	for _, p := range timeline {
		if !p.Contaminated {
			continue
		}
		hi := restoreEpochMs + int64(p.TSec*1000)
		out = append(out, tsRange{lo: hi - 1000, hi: hi})
	}
	return out
}

func inRanges(ts int64, rs []tsRange) bool {
	for _, r := range rs {
		if ts >= r.lo && ts < r.hi {
			return true
		}
	}
	return false
}

func computeSupplementary(samples []Sample, timeline []TimelinePoint, tDrain, sloP99 float64, queueSum float64, queueN, queuePeak int64, excl []tsRange, faultWin []float64, restoreEpochMs int64) *Supplementary {
	s := &Supplementary{QueueDepthPeak: queuePeak}
	for _, sm := range samples {
		if sm.Class == "live" && sm.AgeMs == 0 && inRanges(sm.TS, excl) {
			s.ArtifactExcludedSamples++
		}
	}
	if queueN > 0 {
		s.QueueDepthMean = queueSum / float64(queueN)
	}
	// Whole-run injector-live from samples
	fillLiveSupp(samples, 0, math.MaxInt64, sloP99, excl, &s.LiveP50Ms, &s.LiveP90Ms, &s.LiveP95Ms, &s.LiveP99Ms, &s.FractionUnderSLO, &s.GoodputRpsMean, &s.TimeoutRate)
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
	// tDrain < 0 means drain was never reached (recovery suspended / horizon
	// stop). "Drain window" is then undefined, so fall back to the whole
	// post-restore window rather than emitting an empty window of zeros.
	drainEnd := int64(math.MaxInt64)
	if tDrain > 0 {
		drainEnd = minTS + int64(tDrain*1000)
	}
	fillLiveSupp(samples, minTS, drainEnd, sloP99, excl, &s.DrainLiveP50Ms, &s.DrainLiveP90Ms, &s.DrainLiveP95Ms, &s.DrainLiveP99Ms, &s.DrainFractionUnderSLO, &s.DrainGoodputRpsMean, &s.DrainTimeoutRate)

	if len(faultWin) == 2 && faultWin[0] >= 0 {
		fs := restoreEpochMs + int64(faultWin[0]*1000)
		fe := restoreEpochMs + int64(faultWin[1]*1000)
		var dummy float64
		fillLiveSupp(samples, fs, fe, sloP99, excl, &s.FaultLiveP50Ms, &dummy, &dummy,
			&s.FaultLiveP99Ms, &s.FaultFractionUnderSLO, &s.FaultGoodputRpsMean, &s.FaultTimeoutRate)
	}

	var dqSum float64
	var dqN, dqPeak int64
	for _, p := range timeline {
		if tDrain <= 0 || p.TSec <= tDrain+0.5 {
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

func fillLiveSupp(samples []Sample, t0, t1 int64, sloP99 float64, excl []tsRange, p50, p90, p95, p99, frac, goodput, timeoutRate *float64) {
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
		if inRanges(s.TS, excl) {
			continue // measurement artifact (host stall)
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

// maxInterSampleGapMs returns the largest gap between consecutive injector-live
// request completions in the window. A gap far above the inter-arrival time at
// lambda_L means the measurement process itself paused.
func maxInterSampleGapMs(win []Sample) int64 {
	var ts []int64
	for _, s := range win {
		if s.Class == "live" && s.AgeMs == 0 {
			ts = append(ts, s.TS)
		}
	}
	if len(ts) < 2 {
		return 0
	}
	sort.Slice(ts, func(i, j int) bool { return ts[i] < ts[j] })
	var mx int64
	for i := 1; i < len(ts); i++ {
		if d := ts[i] - ts[i-1]; d > mx {
			mx = d
		}
	}
	return mx
}

func median(xs []float64) float64 {
	if len(xs) == 0 {
		return 0
	}
	c := append([]float64(nil), xs...)
	sort.Float64s(c)
	return c[len(c)/2]
}

func appendCapped(xs []float64, v float64, n int) []float64 {
	xs = append(xs, v)
	if len(xs) > n {
		xs = xs[len(xs)-n:]
	}
	return xs
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

// hostStateInfo is the machine's condition at run start. Recorded in every run
// record because a busy host distorts timing windows and a full disk truncates
// traces, and neither is visible in the results afterwards.
type hostStateInfo struct {
	Load1, Load5, Load15 float64
	Cores                int
	FreeDiskGB           float64
}

// hostState reads the load averages and the free space on the results volume.
func hostState() (hostStateInfo, error) {
	h := hostStateInfo{Cores: runtime.NumCPU()}
	loaded := false
	if out, err := exec.Command("sysctl", "-n", "vm.loadavg").Output(); err == nil {
		fields := strings.Fields(strings.Trim(strings.TrimSpace(string(out)), "{}"))
		var vals []float64
		for _, f := range fields {
			if v, e := strconv.ParseFloat(f, 64); e == nil {
				vals = append(vals, v)
			}
		}
		if len(vals) >= 3 {
			h.Load1, h.Load5, h.Load15 = vals[0], vals[1], vals[2]
			loaded = true
		}
	}
	if !loaded {
		if b, e := os.ReadFile("/proc/loadavg"); e == nil {
			fields := strings.Fields(string(b))
			if len(fields) >= 3 {
				h.Load1, _ = strconv.ParseFloat(fields[0], 64)
				h.Load5, _ = strconv.ParseFloat(fields[1], 64)
				h.Load15, _ = strconv.ParseFloat(fields[2], 64)
				loaded = true
			}
		}
	}
	if !loaded {
		return h, fmt.Errorf("no load average source (tried sysctl vm.loadavg and /proc/loadavg)")
	}
	var st syscall.Statfs_t
	wd, err := os.Getwd()
	if err != nil {
		return h, err
	}
	if err := syscall.Statfs(wd, &st); err != nil {
		return h, err
	}
	h.FreeDiskGB = float64(st.Bavail) * float64(st.Bsize) / (1 << 30)
	return h, nil
}

// gitProvenance is what gets stamped into every run record.
type gitProvenance struct {
	commit     string // full 40-hex
	short      string // first 12
	branch     string
	dirty      bool     // any uncommitted change outside provenanceOutputPrefixes
	dirtyFiles []string // those changes, "XY path"
}

// Paths that may differ from HEAD without marking the tree dirty: run output,
// not code.
var provenanceOutputPrefixes = []string{"results/", "bin/"}

// gitInfo resolves the commit the runner is executing from. It is deliberately
// strict, mirroring the voice harness rule (webrtc-recovery-harness
// voice/lib/env.mjs gitInfo):
//
//   - HEAD must resolve to a full 40-hex commit or an error is returned and
//     the caller refuses to run. The previous version swallowed every error
//     and wrote "unknown" — which is how 137 of the 140 Phase 0/1 run records
//     came to carry gitCommit="unknown", gitDirty=true: they were produced in
//     a checkout whose HEAD was unborn (git init, no commit yet), where
//     `git status` succeeds (everything untracked, hence dirty=true) but
//     `git rev-parse HEAD` fails with "Needed a single revision".
//   - Commands run with -C at the repository root, so any cwd inside the tree
//     resolves the same way.
//   - Dirty is computed from `git status --porcelain` excluding output paths,
//     and the offending files are recorded so a dirty run is never mistaken
//     for a clean one.
func gitInfo() (gitProvenance, error) {
	var gp gitProvenance
	run := func(args ...string) (string, error) {
		cmd := exec.Command("git", args...)
		var stderr bytes.Buffer
		cmd.Stderr = &stderr
		out, err := cmd.Output()
		if err != nil {
			return "", fmt.Errorf("git %s: %v: %s", strings.Join(args, " "), err, strings.TrimSpace(stderr.String()))
		}
		return string(out), nil
	}
	root, err := run("rev-parse", "--show-toplevel")
	if err != nil {
		return gp, fmt.Errorf("git_commit_unavailable: not inside a git work tree (%v)", err)
	}
	root = strings.TrimSpace(root)
	runC := func(args ...string) (string, error) { return run(append([]string{"-C", root}, args...)...) }
	commit, err := runC("rev-parse", "HEAD")
	if err != nil {
		return gp, fmt.Errorf("git_commit_unavailable: HEAD does not resolve (%v)", err)
	}
	commit = strings.TrimSpace(commit)
	if len(commit) != 40 || strings.Trim(commit, "0123456789abcdef") != "" {
		return gp, fmt.Errorf("git_commit_unavailable: unexpected commit format %q", commit)
	}
	gp.commit = commit
	gp.short = commit[:12]
	branch, err := runC("rev-parse", "--abbrev-ref", "HEAD")
	if err != nil {
		return gp, fmt.Errorf("git_commit_unavailable: branch does not resolve (%v)", err)
	}
	gp.branch = strings.TrimSpace(branch)
	status, err := runC("status", "--porcelain")
	if err != nil {
		return gp, fmt.Errorf("git_commit_unavailable: status failed (%v)", err)
	}
	for _, line := range strings.Split(status, "\n") {
		if len(line) <= 3 {
			continue
		}
		path := line[3:]
		if i := strings.Index(path, " -> "); i >= 0 {
			path = path[i+4:]
		}
		path = strings.Trim(path, "\"")
		isOutput := false
		for _, pfx := range provenanceOutputPrefixes {
			if strings.HasPrefix(path, pfx) {
				isOutput = true
				break
			}
		}
		if !isOutput {
			gp.dirtyFiles = append(gp.dirtyFiles, strings.TrimSpace(line[:2])+" "+path)
		}
	}
	gp.dirty = len(gp.dirtyFiles) > 0
	return gp, nil
}

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}
