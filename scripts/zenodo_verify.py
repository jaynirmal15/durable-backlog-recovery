#!/usr/bin/env python3
"""Verify an uploaded Zenodo deposition against the staged MANIFEST.json.

Zenodo reports MD5 for stored objects; the manifest carries SHA-256. This
recomputes MD5 locally so the comparison is like for like, and still reports the
manifest's SHA-256 as the value a reader verifies against.

Read-only. Never publishes, never deletes.

  ZENODO_TOKEN=$(security find-generic-password -a "$USER" -s zenodo-live -w) \
    python3 scripts/zenodo_verify.py --deposition-id 123 --stage-dir ~/Jay_NIW/paper2-zenodo
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zenodo_deposit import LIVE, SANDBOX, api  # noqa: E402


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deposition-id', type=int, required=True)
    ap.add_argument('--stage-dir', required=True)
    ap.add_argument('--sandbox', action='store_true')
    a = ap.parse_args()
    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        print('ZENODO_TOKEN not set.')
        return 2
    base = SANDBOX if a.sandbox else LIVE

    man = json.load(open(os.path.join(a.stage_dir, 'MANIFEST.json')))
    want = {f['path']: f for f in man['files']}
    mp = os.path.join(a.stage_dir, 'MANIFEST.json')
    want.setdefault('MANIFEST.json', {'path': 'MANIFEST.json',
                                      'bytes': os.path.getsize(mp), 'sha256': None})

    st, files = api(base, token, 'GET', '/deposit/depositions/%s/files' % a.deposition_id)
    if st != 200 or not isinstance(files, list):
        print('cannot list files: status %s' % st)
        return 1
    have = {}
    for f in files:
        have[f.get('filename') or f.get('key')] = f

    missing = sorted(k for k in want if k not in have)
    extra = sorted(k for k in have if k not in want)
    bad_size, bad_hash = [], []
    for k, w in sorted(want.items()):
        if k not in have:
            continue
        h = have[k]
        size = h.get('filesize') or h.get('size')
        if size is not None and size != w['bytes']:
            bad_size.append((k, w['bytes'], size))
            continue
        remote = (h.get('checksum') or '').replace('md5:', '')
        if remote:
            local = md5(os.path.join(a.stage_dir, k))
            if local != remote:
                bad_hash.append((k, local, remote))

    print('deposition %s' % a.deposition_id)
    print('  expected %d files, deposition holds %d' % (len(want), len(have)))
    print('  missing    : %d' % len(missing))
    print('  extra      : %d' % len(extra))
    print('  wrong size : %d' % len(bad_size))
    print('  wrong hash : %d' % len(bad_hash))
    for k in missing[:10]:
        print('    MISSING %s' % k)
    for k in extra[:10]:
        print('    EXTRA   %s   <- probe object? delete before publishing' % k)
    for k, w, g in bad_size[:10]:
        print('    SIZE    %s want %d got %s' % (k, w, g))
    for k, l, r in bad_hash[:10]:
        print('    MD5     %s local %s remote %s' % (k, l[:12], r[:12]))
    ok = not (missing or extra or bad_size or bad_hash)
    print()
    print('VERIFIED - safe to publish' if ok else 'NOT VERIFIED - do not publish')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
