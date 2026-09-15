# W6 — Zenodo deposit checklist

## The reserved deposit — cite this

| | |
|---|---|
| **Reserved DOI** | **`10.5281/zenodo.22761131`** |
| **Deposition ID** | **`22761131`** |
| State | `unsubmitted` — a draft, not published |
| Files uploaded | **0**, by design; the package goes up in W6 |
| Draft created | 2026-09-14 23:20:55 −0400 (2026-09-15T03:20:55Z) |
| Metadata from | git commit `349234c` |

This is the DOI §4 cites. **It does not resolve until the record is published**,
which happens in W6, from the web interface, by hand.

An earlier draft, **22740491**, was created during the 2026-09-13 Zenodo outage
(2026-09-14T02:17:53Z, i.e. 2026-09-13 22:17 −0400) and left broken: three
leftover `_probe_*` test objects from a nesting probe, two partially-uploaded
real files, and metadata predating the `related_identifiers` addition. It was
deleted on 2026-09-14 and its reserved
DOI `10.5281/zenodo.22740491` went with it; that DOI was never cited anywhere
and never published. `scripts/zenodo_deposit.py --show <id>` will now inspect a
deposition read-only, which is what should have been used instead of `--probe`,
whose whole job is to upload test objects.

---

The DOI is reserved in W2 so the paper can cite it. **The files are uploaded and
the record published in W6, after drafting freezes**, because what is deposited
must match the commit the reproducibility statement cites.

Token comes from the keychain, per command, and is never echoed, written to a
file, or committed:

```
ZENODO_TOKEN=$(security find-generic-password -a "$USER" -s zenodo-live -w) \
  python3 scripts/zenodo_deposit.py ...
```

## 1. Freeze, then re-stage from the frozen commit

The staged package records the commit it was built from, and that commit is what
the paper must cite. Re-stage **after** the last content change:

```
git log --oneline -1                     # this is the commit the paper cites
python3 scripts/make_deposit.py --stage
```

Confirm the manifest agrees with the frozen commit:

```
python3 -c "import json,subprocess; \
  m=json.load(open('$HOME/Jay_NIW/paper2-zenodo/MANIFEST.json')); \
  h=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(); \
  print('manifest', m['gitCommit']); print('HEAD    ', h); \
  print('MATCH' if m['gitCommit']==h else 'STALE - RE-STAGE')"
```

**This is the step that already went wrong once.** The first staging sat at
`4975422` while main had moved on four commits, and it carried the reports as
they were before the precision fix. Depositing it would have shipped figures
that contradict the paper.

## 2. Verify MANIFEST.json is in its own file list

The manifest is written *after* the file walk, so it is absent from the list it
generates. `zenodo_deposit.py` adds it explicitly; confirm the upload count
reflects that:

```
python3 -c "import json; m=json.load(open('$HOME/Jay_NIW/paper2-zenodo/MANIFEST.json')); \
  print('in list:', any(f['path']=='MANIFEST.json' for f in m['files'])); \
  print('will upload:', m['fileCount'] + (0 if any(f['path']=='MANIFEST.json' for f in m['files']) else 1))"
```

If that ever prints `in list: True`, the manifest has become self-referential and
its own hash is wrong. Investigate before uploading.

## 3. Confirm the upload path still works

Cheap, before moving 407 MB:

```
python3 scripts/zenodo_deposit.py --probe --deposition-id <id>
```

Two five-byte objects, one flat key and one nested, on both the bucket and legacy
APIs, with full status, headers and body. Delete the probe objects afterwards
from the web interface or with the files API.

**Do not flatten keys to make an upload succeed.** The README documents
`traces/`, `results/`, `scripts/` and gives commands such as `--raw-dir traces`.
Flattening breaks the reproducibility statement. If nested keys are refused,
stop and raise it.

## 4. Upload, resumably

```
python3 scripts/zenodo_deposit.py --stage-dir ~/Jay_NIW/paper2-zenodo \
    --deposition-id <id>
```

Files already present are skipped, matched on key **and** size, so an
interrupted run resumes without re-sending 407 MB. Transient 5xx are retried
with exponential backoff.

## 5. Verify file count and hashes against the manifest

After upload, before publishing:

```
python3 scripts/zenodo_verify.py --deposition-id <id> \
    --stage-dir ~/Jay_NIW/paper2-zenodo
```

It compares every key, size and checksum in the deposition against
MANIFEST.json and reports anything missing, extra, or mismatched. **Zenodo
reports MD5 for uploaded objects while the manifest carries SHA-256**, so the
script recomputes MD5 locally to compare like with like; a SHA-256 in the
manifest is still what a reader verifies against.

Expect zero missing, zero extra, zero mismatched. Probe objects count as extra
and must be deleted.

## 6. Add the article DOI, then publish

Once the article is accepted and has a DOI, add it to the deposition metadata:

```
{'relation': 'isSupplementTo', 'identifier': '<article DOI>', 'scheme': 'doi'}
```

Do not invent or guess it.

**Publish from the web interface.** `zenodo_deposit.py` has no publish path, by
design: a published record cannot be deleted and its files cannot be changed.

> **Publishing must happen before submission.** A reserved DOI does not resolve
> until the record is published. A reviewer following the DOI in the
> reproducibility statement before publication gets a dead link, which reads as
> a fabricated citation.

## 7. After publishing

- Check `https://doi.org/<DOI>` resolves to the record.
- Check the record's file count matches the manifest.
- Record the published DOI and date in the paper and in the repository.

## Standing constraints

- Never publish from a script.
- Never flatten keys.
- Never re-round a registered value to make a report tidier.
- Never deposit a package whose manifest commit differs from the cited commit.
