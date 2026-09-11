# Raw per-request sample data (held outside repository)

Raw per-request sample files are **not stored in this repository**. They live in
a sibling directory next to the repo clone:

```
../rhc-raw-data/results/
```

## Why

Each run’s consumer trace is typically **20–60 MB**; the full campaign totals
**several GB**. That exceeds practical GitHub file and repository limits. The
repo retains **run records** (`.json`), summaries (`.md`), and small auxiliary
files only.

## Naming convention

| Run record (in repo) | Raw sample file (outside repo) |
|---|---|
| `<runId>.json` | `<runId>-consumer.jsonl` |

The run record’s `runId` field matches the prefix before `-consumer.jsonl`.
Aborted or invalid traces may carry suffixes on the jsonl side only, e.g.
`<runId>-consumer.jsonl.partial-aborted`, `.invalid-ts-stamp`, `.invalid-zerolive`.

Relative paths under `results/` are preserved in `rhc-raw-data/` (including
`partial-verifb-interrupted/`).

## Use

Raw jsonl is required to **recompute per-request metrics** (live vs recovery
classification, drain-window goodput, timeout rates, queue occupancy series).
The **live-population correction** in Phase 0 was only possible because these
files were retained.

## Publication

The raw archive will be published as a **Zenodo data deposit** alongside the
paper, with a DOI linked from the repository README.
