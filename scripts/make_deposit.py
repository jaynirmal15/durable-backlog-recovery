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

# NO DOI CONSTANTS. Every record this project made -- 22761130 (concept),
# 22761131, 22923220 and 22941578 -- was deleted on 2026-09-24 and every one
# now returns HTTP 410 with a Zenodo tombstone; DataCite 404s all four. They
# are gone permanently and cannot be reinstated by anyone, including Zenodo.
# This is a FRESH deposit with no ancestry, so there is nothing to point at
# until it is published and a DOI exists. Do not write one here from memory.
#
# The deposit is also DESIGNED NEVER TO BE VERSIONED AGAIN, which is what
# dropping the manuscript PDFs buys: with no article.pdf and no
# supplement-S1.pdf the package does not depend on the manuscript, so no
# future revision of the paper can ever require touching it.

META = {
    'title': 'Recovery Headroom Control: pre-registered boundary measurements, '
             'per-request traces and analysis code',
    'upload_type': 'dataset',
    'version': '1.0.0',
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
NOTES = """Generated from git commit {commit}. Every file in the package is
listed in MANIFEST.json with its SHA-256 and its size, together with the commit
the package was built from.

This deposit is the measurement record for a study of the safe drain boundary \
in durable-backlog recovery: the pre-registration with its amendments and \
addenda, every run record and per-request trace from the reported campaigns, \
the analysis code that regenerates every reported number, the figure \
generators, and the regression fixture that pins the metrics path.

It contains no manuscript PDF. The paper is published separately and cites \
this deposit; nothing here depends on the paper's text, so no revision of the \
paper changes anything in this package.

Zenodo stores it as five objects, because the file API will not accept a key \
containing a slash: README.md, LICENSE, PRE-REGISTRATION.md and MANIFEST.json \
individually, so they can be read without downloading the archive, and \
paper2-rhc-artifact.zip holding the complete tree with its directory paths \
intact. The four individual files are also inside the archive, so an \
extracted copy is complete on its own.

MANIFEST.json's checksums verify against the EXTRACTED files, not against the \
archive: extract first, then hash. README.md gives the layout, the commands \
that regenerate each report, and the caveats carried in the record."""


README = """# Recovery Headroom Control — measurement artifact

Everything needed to check the reported numbers, and to re-derive them from the
raw per-request traces.

**This package contains no manuscript PDF.** It is the measurement record: the
pre-registration, the run records, the per-request traces, the analysis code
that turns one into the other, the figures and the regression fixture. The
paper is published separately and cites this deposit; nothing here depends on
the paper's text, and no revision of it changes anything in this package.

## How this record is stored

Zenodo stores this deposit as **five objects**, because its file API will not
accept a key containing a slash. Four files are deposited individually so they
can be read without downloading 400 MB:

    README.md             this file
    LICENSE
    PRE-REGISTRATION.md   the contract, with all amendments and addenda
    MANIFEST.json         every file with its SHA-256, plus the git commit

The fifth object, **paper2-rhc-artifact.zip**, holds the complete tree with the
directory paths below intact. Nothing is flattened: extract the archive and the
paths in this README, in MANIFEST.json and in the paper's reproducibility
statement are the paths you get.

**MANIFEST.json's SHA-256s verify against the extracted files.** Extract the
archive first, then hash; the manifest describes the tree, not the archive. The
four individual objects are also inside the archive, so an extracted copy is
complete on its own.

## Layout, inside the archive

    PRE-REGISTRATION.md   the contract, with all amendments and addenda
    results/              run records, boundary files, derived JSON, reports
    traces/               per-request consumer traces, gzip, one per run
    scripts/              analysis code; every reported number comes from here
    tests/                the Aug-18 regression fixture pinning the metrics path
    harness/              Go source for the runner, downstream, consumer, producer
    figures/              paper figures as vector PDF, and their captions
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

    python3 scripts/recompute_rho.py --boundary results/boundaries/c10-C0.json \\
        --results results --raw-dir traces --write

**The figures are the one thing that was not byte-reproducible, and it was
fixed rather than excused.** The plotting library stamped a wall-clock creation
time into each file, so two runs over unchanged inputs produced different bytes
with identical drawn content. The metadata is now suppressed and determinism is
verified over consecutive runs.

## What the campaigns are

    E1    four boundaries on the fixed harness
    E1B   replication at n=12, and completing the 2x2
    E2    swapping the queue caps between arms
    E2b   separating service time from concurrency at C=400
    E2c   SLO threshold sweep, analysis only
    E2d   capacity calibration, analysis only
    E2e   observing the per-request overhead, then eliminating it
    A6    estimator validity at collapsed points

## Licensing

The data, traces, reports and figures are released under CC BY 4.0. The source
code under `scripts/` and `harness/` is released under the MIT License,
reproduced in `LICENSE` in this package and in the repository. Where the two
differ, the MIT License governs the code.

## Caveats carried in the record

- A4 achieved utilisation is valid at SAFE points only. At collapsed points it
  over-reads; see amendment A6. Boundary intervals are reported in rate.
- E2e runs on a later harness commit than E1-E2b, because it needed
  instrumentation that did not exist earlier. Comparisons across that line are
  flagged where they are made.
- Three findings entered the record and were later refuted by further
  measurement. They are listed with what killed them in
  `figures/T4-false-findings.md`.
- The per-request timing bias measured here is a property of this
  implementation, this host and this Go runtime. Every run reported ran on one
  AWS EC2 c6i.2xlarge instance under Go 1.25.3; the platform block in every run
  record gives the full detail.
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

    # 7. NO MANUSCRIPT PDFs. Removed 2026-09-24, and it is the point of
    # this rebuild rather than an omission.
    #
    # Earlier versions shipped article.pdf and supplement-S1.pdf so a reader
    # holding the DOI could read the paper the data belongs to. That coupling
    # cost three re-versions in two days -- a build defect in the
    # bibliography, then two adversarial review passes -- each of which
    # changed the PDFs and so required a new version of a package whose DATA
    # had not moved by a single byte. 797 of 809 files were byte-identical
    # across the last pair.
    #
    # Without the PDFs the deposit does not depend on the manuscript at all.
    # It can be published before the paper is submitted, and no revision of
    # the paper can ever require touching it again. The paper points at the
    # deposit; the deposit does not point back.
    #
    # The reader still gets there: once the article has a DOI the record
    # metadata can carry an isSupplementTo relation, which is a metadata edit
    # and needs no new version.

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
        # NO VERSION IN THE ARCHIVE NAME. It was -1.0.0, then -1.0.1, then
        # -1.1.0, and the rename cost something real every time: a
        # new-version draft INHERITS the previous version's files, so a
        # renamed archive ADDS an object instead of replacing one. That trap
        # had to be caught and swept on both re-versions. This deposit is not
        # going to be versioned again, and the version lives in the record
        # metadata, where release identity belongs and where it can change
        # without renaming a 325 MiB object.
        base = os.path.expanduser('~/Jay_NIW/paper2-rhc-artifact')
        print('archiving...')
        shutil.make_archive(base, 'zip', STAGE)
        z = base + '.zip'
        print('%s\n  %.1f MiB  sha256 %s'
              % (z, os.path.getsize(z) / 1048576.0, sha256(z)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
