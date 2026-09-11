# results/ — committed run records, summaries, memos

Committed here (from `results.zip` at commit d09049a, extracted 2026-09-11):

- run records `*.json` (140 files with a `runId`; 7 runIds also appear as
  `.invalid-*` / `partial-verifb-interrupted/` copies, retained per protocol)
- summary JSONs (`PHASE1*.json`, `GATE0-*.json`, `p0*-corrected-timeline.json`,
  `probe*.json`, `injector-ceiling.json`, `preflight-instr-report.json`)
- memos `*.md` (18), probe logs `*.log` (17), `load_sweep.csv`,
  `diagnostics/p0b-rate-200-20260814-000928/`
- nothing newer than 2026-08-18 12:49 (`RAW-DATA.md`)

**Not committed:** raw per-request consumer traces (`*-consumer.jsonl` and the
`.invalid-*` / `.partial-aborted` / `.hung-rem1` variants). They live outside
the repo in `../rhc-raw-data/results/`: 7.2 GB, 157 files, 99,332,883 lines,
run dates 2026-08-13 13:17 to 2026-08-18 12:14, every file parses. See
`RAW-DATA.md` for the naming convention (`<runId>-consumer.jsonl`).

Archive of the raw data: `rhc-raw-data.zip`, 466302099 bytes, 157 JSONL entries
(7.75 GB uncompressed), attached to GitHub release `raw-data-2026-08-18`.

    sha256  b7fb98d696ea4fbc24f144300779ad8b0fe39712c130776c50c837db8dc7d69c  rhc-raw-data.zip

Verify with `shasum -a 256 -c` against the `.sha256` file on the release.
