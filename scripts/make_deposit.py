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

# The reserved DOI for this deposit, and the draft it belongs to. Recorded here
# because this is where the deposit metadata lives; the paper cites the DOI in
# section 4. Reserved 2026-09-14 on an empty draft: it does NOT resolve until
# the record is published by hand in W6. See scripts/DEPOSIT-W6.md.
RESERVED_DOI = '10.5281/zenodo.22761131'
DEPOSITION_ID = 22761131

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
        'offline; E2d calibrates true capacity against configured capacity; E2e '
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
        'with what killed them in figures/T1-false-findings.md.</p>'),
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



README = """# Recovery Headroom Control — measurement artifact v1.0.0

Everything needed to check the reported numbers, and to re-derive them from the
raw per-request traces.

## Layout

    PRE-REGISTRATION.md   the contract, with all six amendments A1-A6
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
  what killed them in figures/T1-false-findings.md.
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

    # 7. per-request traces: the campaigns this paper reports, gzip only
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
    print('%-18s %8s %14s' % ('component', 'files', 'size'))
    for k, v in parts.items():
        print('%-18s %8s %13.1f MB' % (k, v.get('files', '-'),
                                       v.get('bytes', 0) / 1048576.0))
    print('%-18s %8d %13.1f MB' % ('TOTAL', len(files),
                                   sum(f['bytes'] for f in files) / 1048576.0))
    print('git commit %s' % commit[:12])

    if a.archive:
        base = os.path.expanduser('~/Jay_NIW/paper2-rhc-artifact-1.0.0')
        print('archiving...')
        shutil.make_archive(base, 'zip', STAGE)
        z = base + '.zip'
        print('%s  %.1f MB  sha256 %s' % (z, os.path.getsize(z) / 1048576.0, sha256(z)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
