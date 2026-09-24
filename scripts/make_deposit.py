#!/usr/bin/env python3
"""Assemble the Zenodo deposit package for Paper 2 and write its manifest.

Scope, per the deposit brief: run records, per-request traces, analysis scripts,
the pre-registration with all six amendments, and the regression fixture.

Deliberately excluded:
  deploy/.terraform  a 692 MB provider binary, already gitignored
  Phase 0 traces     uncompressed .jsonl from earlier work, 7.2 GB, not the
                     campaigns this paper reports

Usage:
  python3 scripts/make_deposit.py --stage      build the tree and manifest
  python3 scripts/make_deposit.py --archive    also make the .zip
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.expanduser('~/Jay_NIW/durable-backlog-recovery')
RAW = os.path.expanduser('~/Jay_NIW/rhc-raw-data/results')
STAGE = os.path.expanduser('~/Jay_NIW/paper2-zenodo')

# The DOIs for this deposit. THE ARTICLE CITES THE CONCEPT DOI: the DOI printed
# in an accepted paper cannot be changed, so it must not name one version.
# 22761131 is v1.0.0, published 2026-09-23 and superseded by v1.0.1 for a build
# defect on page 20. See scripts/DEPOSIT-W6.md.
CONCEPT_DOI = '10.5281/zenodo.22761130'      # always the newest version
V1_0_0_DOI = '10.5281/zenodo.22761131'       # superseded by v1.0.1
V1_0_0_ID = 22761131
V1_0_1_DOI = '10.5281/zenodo.22923220'       # superseded by v1.1.0
V1_0_1_ID = 22923220                         # newversion is taken from THIS,
                                             # the current published record
RESERVED_DOI = CONCEPT_DOI
DEPOSITION_ID = V1_0_1_ID

META = {
    'title': 'Recovery Headroom Control: pre-registered boundary measurements, '
             'per-request traces and analysis code',
    'upload_type': 'dataset',
    'version': '1.1.0',
    'license': 'cc-by-4.0',
    'creators': [{'name': 'Nirmal, Jay Suresh',
                  'orcid': '0009-0003-0886-4663'}],
    'description': (
        '<p><strong>What this is.</strong> The complete measurement artifact for '
        'the Recovery Headroom Control study: the pre-registration and all six '
        'amendments, every run record and per-request trace from the reported '
        'campaigns, the analysis code that regenerates every reported number, the '
        'figures, and the regression fixture that pins the metrics path.</p>'
        '<p><strong>Campaigns.</strong> E1 locates four safe-recovery boundaries; '
        'E1B replicates two of them at n=12 and completes the 2x2; E2 swaps the '
        'queue caps between concurrency arms; E2b separates service time from '
        'concurrency at a reduced capacity; E2c sweeps the latency objective '
        'offline; E2d calibrates C_measured against C_config; E2e '
        'observes the per-request overhead directly and then eliminates it; '
        'amendment A6 establishes where the utilisation estimator is and is not '
        'valid.</p>'
        '<p><strong>Reproducibility.</strong> Every committed report regenerates '
        'byte-identically from the committed data by running its own script. '
        'MANIFEST.json lists every file with its SHA-256 and records the git '
        'commit the package was built from. README.md gives the layout and the '
        'exact commands.</p>'
        '<p><strong>Licensing.</strong> The data, traces, reports and figures are '
        'released under CC BY 4.0. The source code under scripts/ and harness/ is '
        'released under the MIT License, reproduced in LICENSE in this package and '
        'in the repository. Where the two differ, the MIT License governs the '
        'code.</p>'
        '<p><strong>Caveats carried in the record.</strong> The utilisation '
        'estimator is valid at safe points only and over-reads on collapsed runs, '
        'so boundary intervals are reported in rate. Three findings entered the '
        'record and were later refuted by further measurement; they are listed '
        'with what killed them in figures/T4-false-findings.md.</p>'),
    'related_identifiers': [
        {'relation': 'isSupplementedBy',
         'identifier': 'https://github.com/jaynirmal15/durable-backlog-recovery',
         'scheme': 'url'},
        {'relation': 'references',
         'identifier': '10.5281/zenodo.22061184',
         'scheme': 'doi'},
    ],
    # The article's own DOI is unknown until acceptance. In W6 add
    #   {'relation': 'isSupplementTo', 'identifier': '<article DOI>', 'scheme': 'doi'}
    # Do NOT invent one.
}



# THE ZENODO NOTES FIELD, COMPOSED -- NOT SLICED FROM THE README.
#
# For v1.0.1 the Notes were produced by slicing README.md and truncating at
# 4,000 characters, which ended the field mid-word on "MANIFEST.j". A slice
# has no idea where a sentence ends. This is written as its own text, lives in
# git so it can be diffed against what the record actually carries, and ends
# where it means to.
NOTES = """Version 1.1.0, staged from git commit {commit}.

This version supersedes v1.0.1 (record 22923220, published 2026-09-23), which superseded v1.0.0 (record 22761131). All three remain available and each keeps its own DOI. The concept DOI 10.5281/zenodo.22761130 always resolves to the newest version, and it is the DOI the article cites.

Why a minor version rather than a patch: v1.0.1 corrected a single build defect and left the manuscript's text untouched. This version follows two independent adversarial reviews. Seven mechanical defects were corrected against the committed records, seven rulings were applied that narrow what the paper claims, and the checking tooling gained four invariants. v1.0.1 carries the pre-review PDFs, and because the concept DOI resolves to whatever is newest, leaving v1.0.1 newest would send a reader following the article's own DOI to an artifact whose PDFs contradict the paper that cites it.

What did not change, measured by diffing v1.0.1's manifest against this one rather than asserted: both versions contain 809 files, nothing added and nothing removed, and 797 are byte-identical. That includes all 521 files under results/, all 205 per-request traces, all four harness sources, the regression fixture, all six figure PDFs, PRE-REGISTRATION.md and LICENSE. Of the 62 files under scripts/, 55 are byte-identical, including every script that computes a reported number.

Twelve files changed: both PDFs, this record's README.md, two manuscript artefacts under figures/, and seven scripts. The seven are the manuscript-build, checking and deposit tooling. One of them, make_table3.py, renders a manuscript table and computes no measurement; the operand it printed for one identity had been rounded while the result had not, and is now the unrounded value the boundary artefact records. That artefact is unchanged.

The archive is renamed paper2-rhc-artifact-1.1.0.zip to match the version it belongs to.

MANIFEST.json hashes the files that ship. pdfTeX embeds a creation timestamp and a document identifier, so recompiling the sources reproduces the layout and the text but not the bytes. The full account is the Version note in README.md."""


README = """# Recovery Headroom Control — measurement artifact

Everything needed to check the reported numbers, and to re-derive them from the
raw per-request traces.

(This heading carried "v1.0.0" through v1.0.1, where it was already two
versions stale. The version notes below carry the version; the heading no
longer pretends to.)

## Version note — v1.1.0, 2026-09-24

**All dates in this note are UTC.** The repository clock runs at −0400. Every
date below falls on the same day under both clocks, so unlike the v1.0.1 note
there is no offset to reconcile here.

**This is version 1.1.0. It supersedes version 1.0.1**, record `22923220`,
published 2026-09-23, which superseded version 1.0.0, record `22761131`. All
three remain available and each keeps its own DOI. The concept DOI
`10.5281/zenodo.22761130` always resolves to the newest version, and it is the
DOI the article cites.

**Why a minor version and not a patch.** v1.0.1 was a patch: one build defect,
corrected, with the manuscript's text untouched. This is not that. The
manuscript went through two independent adversarial reviews and changed
substantively — seven mechanical defects corrected against the committed
records, and seven rulings applied that narrow what the paper claims. The
checking tooling gained four invariants. Someone holding v1.0.1's
`article.pdf` is not holding this paper with a tidier reference list.

**Why there is a third version at all.** v1.0.1 carries the pre-review PDFs.
The concept DOI resolves to whatever is newest, so leaving v1.0.1 newest would
send every reader who follows the DOI printed in the article to an artifact
whose PDFs contradict the paper that cites it.

**What did not change, measured by diffing v1.0.1's manifest against this
one — not asserted.** Both versions contain **809 files. Nothing was added and
nothing was removed.** **797 are byte-identical.** Specifically:

    results/     521 files   all byte-identical
    traces/      205 files   all byte-identical
    harness/       4 files   all byte-identical
    tests/         2 files   all byte-identical
    figures/*.pdf  6 files   all byte-identical
    PRE-REGISTRATION.md      byte-identical
    LICENSE                  byte-identical

**No data, no per-request traces, no run records, no results, no analysis
code, no figure generators, no regression fixture and no pre-registration
text.** Of the 62 files under `scripts/`, **55 are byte-identical**, including
every script that computes a reported number: `make_figures.py`,
`make_table2.py`, `make_table4.py`, `e2e_analysis.py`,
`capacity_calibration.py`, `locate_boundary.py`, `recompute_rho.py`,
`slo_sweep.py`, `e2c_report.py` and `collapsed_estimator_audit.py`.

**What did change: twelve files, none of them data.** Two of the twelve have
no "after" size printed here, and deliberately: this file is one of them, and
`make_deposit.py` is the script that holds this file's text. Writing either
size into this note changes the thing the number describes. `MANIFEST.json`
records both, measured after the fact, which is where a size belongs.

    article.pdf                            544934 -> 547913
    supplement-S1.pdf                      362257 -> 362979
    README.md                               8034 ->  see MANIFEST.json
    figures/CAPTIONS.md                     11959 ->  12097
    figures/T3-candidate-explanations.md     7498 ->   7732
    scripts/build_article.py                62414 ->  64728
    scripts/check_manuscript.py             33491 ->  51617
    scripts/make_deposit.py                 19753 ->  see MANIFEST.json
    scripts/make_table3.py                  14137 ->  15479
    scripts/test_check_manuscript.py        14536 ->  23484
    scripts/test_zenodo_guard.py             8182 ->  13072
    scripts/zenodo_deposit.py               35524 ->  39271

**One of those needs stating precisely rather than being left inside a
count.** `scripts/make_table3.py` is a generator, and its output changed:
`figures/T3-candidate-explanations.md` is what it writes. It renders a
manuscript table from committed artefacts and computes no measurement. What
changed in it is that the table printed the identity
`h = (0.98 − 0.9137) / 0.0689 = +0.980`, in which the first operand had been
rounded while the result had not — so as printed it evaluates to 0.962 and
read as false. The boundary artefact `results/e2b/boundaries/c50-C0.json`
records ρ* as the interval [0.975, 0.9875], midpoint **0.98125**, which is the
operand that yields 0.980. **The artefact did not change; the printed operand
was wrong and is now the unrounded one, and the registered verdict is
unaffected.** The generator now reads both operands from that artefact and
asserts the identity, so it cannot drift again. `figures/CAPTIONS.md` is
caption text and changed for the same class of reason.

**The remaining six scripts are the manuscript-build, checking and deposit
tooling**, and they are the substance of this version rather than noise beside
it. `check_manuscript.py` grew from five invariants to seven; counting the two
retired-phrase rules, **four new invariants**:

1. **Float references must be keyed.** A literal "Table 8" survived a length
   cut that had renumbered the table it named. A literal cannot be checked
   against the float that would carry that number and cannot survive
   renumbering; the keyed form can.
2. **Section references must resolve.** Every §X and §X-Y, in either document,
   must name a section the article actually has. Three in the supplement
   pointed at a §V-G and a §VII-D the same cut had removed.
3. **Registered values must name their semantic key.** Four defects across the
   two reviews were one failure: a value staying numerically correct while
   crossing an estimator, population, denominator or operation boundary.
   Sixteen values now carry the dimensions their context must name.
4. **Retired phrases cannot reappear in live text.** Two formulations were
   withdrawn — a percentage range asserted across seven cells of different
   resolution, and a prospectivity claim the archive cannot support — and the
   phrase list now rejects both wherever they are not explicitly marked as
   historical.

**None of it touches how a reported number is computed.** Every script that
computes one is byte-identical, and that is checked above rather than claimed.

**Both PDFs were rebuilt**, because the manuscript changed. `MANIFEST.json`
and the archive follow from them.

**The archive was renamed** from `paper2-rhc-artifact-1.0.1.zip` to
`paper2-rhc-artifact-1.1.0.zip`, so that its name matches the version it
belongs to.

**Why the PDFs are not byte-reproducible.** pdfTeX embeds a creation timestamp
and a document identifier, so no two builds of the same `.tex` are ever
byte-identical. **`MANIFEST.json` therefore hashes the files that ship, not a
rebuild of them.** A reader checking the manifest should hash the delivered
files; recompiling the `.tex` reproduces the layout and the text but not the
bytes.

**Commits.** The two review passes are `22f52a3` (2026-09-23T20:21:24Z) and
`9698759` (2026-09-23T21:11:40Z); the length trim is `e3f90b6`
(2026-09-24T13:18:55Z) and the supplement formatting fix `afde18a`
(2026-09-24T13:49:33Z). v1.0.1 was staged from `b7731a32c16c444a097a97028f72051def33b538`.
The commit this version was staged from is recorded in `MANIFEST.json` as
`gitCommit`.

## Version note — v1.0.1, 2026-09-23

**All dates in this note are UTC.** The repository clock runs at −0400, so
2026-09-23 UTC is 2026-09-22 locally; they are one date under two clocks.

**This is version 1.0.1. It supersedes version 1.0.0**, published earlier the
same day as record `22761131`. Both versions remain available and both keep
their own DOI. The concept DOI `10.5281/zenodo.22761130` always resolves to
the newest version, and it is the DOI the article cites.

**Why there is a second version.** v1.0.0's `article.pdf` carried a build
defect: the last bibliography entry had no end bound, so reference [14]
absorbed 726 words of drafting apparatus from the source file and typeset it
in the right column of page 20. The count is measured from the typeset page.
The defect was in the build script, not in the manuscript. It is corrected in
v1.0.1.

**Why a new version rather than a correction in place.** Zenodo does not
permit files on a published record to be replaced by their owner: *"Files in
the record however can only be edited (added, modified or deleted) after
publication by contacting support."* A new version is the documented route,
and unlike deletion it is reversible in the only sense that matters — nothing
is destroyed and v1.0.0 stays citable.

**What did not change, measured by diffing v1.0.0's manifest against this
one — not asserted.** Every file under `results/` (521), `traces/` (205),
`figures/` (10), `harness/` (4) and `tests/` (2) is **byte-identical**, and so
is `PRE-REGISTRATION.md` and `LICENSE`. **No data, no per-request traces, no
results, no run records, no analysis code, no figure generators, no regression
fixture and no pre-registration text.** Of the 62 files under `scripts/`, **53
are byte-identical**, including every analysis script and every figure and
table generator — `make_figures.py`, `make_table2/3/4.py`, `e2e_analysis.py`,
`capacity_calibration.py`, `locate_boundary.py` and the rest.

**What did change, in full.** One file added and eleven changed:

    added    scripts/test_zenodo_guard.py

    changed  article.pdf            548234 -> 544934
             supplement-S1.pdf      362084 -> 362257
             README.md                3687 -> 6237     (this file)
             scripts/build_article.py
             scripts/check_manuscript.py
             scripts/make_deposit.py
             scripts/promotion_scan.py
             scripts/section_wordcount.py
             scripts/test_check_manuscript.py
             scripts/zenodo_deposit.py
             scripts/zenodo_verify.py

**The nine files under `scripts/` are the manuscript-build and deposit
tooling, and they are the substance of this version rather than noise beside
it.** The defect that made v1.0.1 necessary was a defect in exactly that
tooling: `build_article.py` ended the last bibliography entry at end of file.
Fixing it, and fixing the same shape wherever else it appeared, is what these
diffs are. The deposit tooling changed alongside because this version is also
how the replacement was carried out. None of it touches how a reported number
is computed — every script that computes one is byte-identical.

**Both PDFs were rebuilt**, because both carry the DOI in their text.
`MANIFEST.json` and the archive follow from them.

**The archive was renamed** from `paper2-rhc-artifact-1.0.0.zip` to
`paper2-rhc-artifact-1.0.1.zip`, so that its name matches the version it
belongs to. Nothing went missing: a reader comparing the two file lists sees
one name replace the other, not a deletion and an unexplained addition.

**Toolchain, and why the PDFs are not reproducible byte-for-byte.** v1.0.1 was
compiled with pdfTeX 1.40.25; v1.0.0 with pdfTeX 1.40.22. pdfTeX embeds a
creation timestamp and a document identifier, so no two builds of the same
`.tex` are ever byte-identical, even on one machine with one toolchain.
**`MANIFEST.json` therefore hashes the files that ship, not a rebuild of
them.** A reader checking the manifest should hash the delivered files;
recompiling the `.tex` reproduces the layout and the text but not the bytes.

**Commits.** v1.0.0 was staged from
`e22e779547d19b462627cb06acfd07246c4d58ef`. The defect was fixed at
`79aaa680d15f0c4bf33e903f4962d4df0f796c30`. The commit this version was staged
from is recorded in `MANIFEST.json` as `gitCommit`.

---

## How this record is stored

Zenodo stores this deposit as **seven objects**, because its file API will not
accept a key containing a slash. Six files are deposited individually so they
can be read without downloading 400 MB:

    README.md             this file
    LICENSE
    PRE-REGISTRATION.md   the contract, with all six amendments A1-A6
    MANIFEST.json         every file with its SHA-256, plus the git commit
    article.pdf           the submitted article
    supplement-S1.pdf     its supplement

The seventh object, **paper2-rhc-artifact-1.1.0.zip**, holds the complete tree
with the directory paths below intact. Nothing is flattened: extract the
archive and the paths in this README, in MANIFEST.json and in the paper's
reproducibility statement are the paths you get.

**MANIFEST.json's SHA-256s verify against the extracted files.** Extract the
archive first, then hash; the manifest describes the tree, not the archive.
The six individual objects are also inside the archive, so an extracted copy
is complete on its own.

## Layout, inside the archive

    PRE-REGISTRATION.md   the contract, with all six amendments A1-A6
    results/              run records, boundary files, derived JSON, reports
    traces/               per-request consumer traces, gzip, one per run
    scripts/              analysis code; every reported number comes from here
    tests/                the Aug-18 regression fixture pinning the metrics path
    harness/              Go source for the runner, downstream, consumer, producer
    figures/              paper figures as vector PDF, and their captions
    article.pdf           the submitted article, as compiled
    supplement-S1.pdf     its supplement
    MANIFEST.json         every file with its SHA-256, plus the git commit

## Reproducing

Every committed report regenerates byte-identically from committed data:

    python3 scripts/collapsed_estimator_audit.py     # A6 audit
    python3 scripts/capacity_calibration.py          # E2d
    python3 scripts/slo_sweep.py                     # E2c
    python3 scripts/e2e_analysis.py                  # E2e
    python3 scripts/e2c_report.py > results/E2C-REPORT.md
    python3 scripts/make_figures.py                  # all six figures

Scripts that read raw traces default to the layout of the working repository,
where traces live beside it in `../rhc-raw-data/results`. In this package they
are under `traces/`, so pass it explicitly:

    python3 scripts/recompute_rho.py --boundary results/boundaries/c10-C0.json \
        --results results --raw-dir traces --write

## What the campaigns are

    E1    four boundaries on the fixed harness
    E1B   replication at n=12, and completing the 2x2
    E2    swapping the queue caps between arms
    E2b   separating service time from concurrency at C=400
    E2c   SLO threshold sweep, analysis only
    E2d   capacity calibration, analysis only
    E2e   observing the per-request overhead, then eliminating it
    A6    estimator validity at collapsed points

## Caveats carried in the record

- A4 achieved utilisation is valid at SAFE points only. At collapsed points it
  over-reads; see amendment A6. Boundary intervals are reported in rate.
- E2e runs on a later harness commit than E1-E2b, because it needed
  instrumentation that did not exist earlier. Comparisons across that line are
  flagged where they are made.
- Three findings entered the record and were later refuted. They are listed with
  what killed them in figures/T4-false-findings.md.
"""


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def copy_into(src, dst, pred=None):
    n = b = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.terraform', '.git')]
        for f in files:
            sp = os.path.join(root, f)
            if pred and not pred(sp):
                continue
            rel = os.path.relpath(sp, src)
            dp = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(sp, dp)
            n += 1
            b += os.path.getsize(sp)
    return n, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', action='store_true')
    ap.add_argument('--archive', action='store_true')
    a = ap.parse_args()

    if os.path.isdir(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)
    parts = {}

    # 1. pre-registration and amendments
    shutil.copy2(os.path.join(REPO, 'PRE-REGISTRATION.md'), STAGE)
    amend = subprocess.run(['grep', '-c', '^### A[0-9]',
                            os.path.join(REPO, 'PRE-REGISTRATION.md')],
                           capture_output=True, text=True).stdout.strip()
    parts['pre-registration'] = {'files': 1, 'amendments': int(amend)}

    # The repo LICENSE ships with the package so the MIT terms travel with the
    # code, which CC BY 4.0 on the record does not cover.
    shutil.copy2(os.path.join(REPO, 'LICENSE'), STAGE)

    # 2. run records, boundary files, derived JSON, reports.
    # Traces are excluded here and collected once under traces/: some were
    # committed into the repo as well as living in the raw corpus, and copying
    # both put 117 MB of byte-identical duplicates in the package.
    n, b = copy_into(os.path.join(REPO, 'results'), os.path.join(STAGE, 'results'),
                     lambda q: not q.endswith(('.gz', '.jsonl')))
    parts['results'] = {'files': n, 'bytes': b}

    # 3. analysis code
    n, b = copy_into(os.path.join(REPO, 'scripts'), os.path.join(STAGE, 'scripts'),
                     lambda p: p.endswith(('.py', '.sh', '.go')))
    parts['scripts'] = {'files': n, 'bytes': b}

    # 4. regression fixture
    n, b = copy_into(os.path.join(REPO, 'tests'), os.path.join(STAGE, 'tests'))
    parts['tests'] = {'files': n, 'bytes': b}

    # 5. harness source, so the traces can be regenerated
    for d in ('runner', 'downstream', 'consumer', 'producer'):
        n, b = copy_into(os.path.join(REPO, d), os.path.join(STAGE, 'harness', d),
                         lambda p: p.endswith('.go'))
        parts.setdefault('harness', {'files': 0, 'bytes': 0})
        parts['harness']['files'] += n
        parts['harness']['bytes'] += b

    # 6. figures
    n, b = copy_into(os.path.join(REPO, 'figures'), os.path.join(STAGE, 'figures'))
    parts['figures'] = {'files': n, 'bytes': b}

    # 7. the submitted article and supplement, as compiled.
    # These are BUILD PRODUCTS, not committed artefacts: build/access is
    # gitignored apart from the two .tex sources, so unlike everything else in
    # this package they are not regenerable from the recorded commit alone --
    # they need a TeX installation and the vendored IEEE Access class. They are
    # included because a reader who has the DOI should be able to read the
    # paper the data belongs to without finding it elsewhere.
    # AT THE STAGE ROOT, not under article/: these two are deposited as
    # individual Zenodo objects, and Zenodo will not take a key with a slash
    # in it. Keeping them flat here makes the manifest path and the object key
    # the same string, so the verifier compares like with like.
    n = b = 0
    for name in ('article.pdf', 'supplement-S1.pdf'):
        src = os.path.join(REPO, 'build', 'access', name)
        if not os.path.isfile(src):
            print('  MISSING: %s -- compile before staging' % name)
            continue
        # KNOWN FALSE POSITIVE, LOGGED RATHER THAN FIXED. This compares
        # MTIMES, and a regeneration that produces byte-identical .tex still
        # bumps its mtime -- so a PDF compiled from exactly this .tex is
        # reported stale after any rebuild. It fired on supplement-S1.pdf
        # during the 2026-09-23 replacement, where the PDF was the published,
        # correct one. The check should compare CONTENT lineage: record the
        # .tex's SHA-256 beside the PDF at compile time and compare that.
        # Until then, treat this as a prompt to check the digest by hand, not
        # as a finding.
        tex = src[:-4] + '.tex'
        if os.path.isfile(tex) and os.path.getmtime(src) < os.path.getmtime(tex):
            print('  STALE(mtime, may be a false positive): %s is older than '
                  'the .tex beside it -- verify by digest, not by date' % name)
        shutil.copy2(src, os.path.join(STAGE, name))
        n += 1
        b += os.path.getsize(src)
    parts['article'] = {'files': n, 'bytes': b}

    # 8. per-request traces: the campaigns this paper reports, gzip only
    n, b = copy_into(RAW, os.path.join(STAGE, 'traces'),
                     lambda p: p.endswith('.gz'))
    parts['traces'] = {'files': n, 'bytes': b}

    open(os.path.join(STAGE, 'README.md'), 'w').write(README)

    # manifest with a hash for every file
    files = []
    for root, dirs, fs in os.walk(STAGE):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in sorted(fs):
            p = os.path.join(root, f)
            files.append({'path': os.path.relpath(p, STAGE),
                          'bytes': os.path.getsize(p), 'sha256': sha256(p)})
    commit = subprocess.run(['git', '-C', REPO, 'rev-parse', 'HEAD'],
                            capture_output=True, text=True).stdout.strip()
    man = {'metadata': META, 'gitCommit': commit, 'components': parts,
           'fileCount': len(files),
           'totalBytes': sum(f['bytes'] for f in files), 'files': files}
    json.dump(man, open(os.path.join(STAGE, 'MANIFEST.json'), 'w'), indent=2)

    print('staged at %s' % STAGE)
    print('%-18s %8s %16s' % ('component', 'files', 'size'))
    for k, v in parts.items():
        print('%-18s %8s %12.1f MiB' % (k, v.get('files', '-'),
                                        v.get('bytes', 0) / 1048576.0))
    print('%-18s %8d %12.1f MiB' % ('TOTAL', len(files),
                                    sum(f['bytes'] for f in files) / 1048576.0))
    print('git commit %s' % commit[:12])

    if a.archive:
        # The archive is named for the version it belongs to. v1.0.0's
        # object stays on v1.0.0's record and is never seen beside this one,
        # so there is no continuity to preserve -- and an archive named 1.0.0
        # inside a record labelled 1.0.1, beside a manifest that says 1.0.1,
        # would misdescribe itself.
        base = os.path.expanduser('~/Jay_NIW/paper2-rhc-artifact-%s'
                                  % META['version'])
        print('archiving...')
        shutil.make_archive(base, 'zip', STAGE)
        z = base + '.zip'
        print('%s\n  %.1f MiB  sha256 %s'
              % (z, os.path.getsize(z) / 1048576.0, sha256(z)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
