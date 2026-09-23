#!/usr/bin/env python3
"""Verify a HYBRID Zenodo deposition against the staged MANIFEST.json.

THE DEPOSITION HAS TWO SHAPES AND BOTH HAVE TO BE CHECKED. Zenodo's file API
refuses a key containing a slash -- the bucket route 404s on `traces/x.gz`
whether the slash is raw or percent-encoded, and the legacy files API accepts
the upload and SILENTLY RENAMES it to `traces_x.gz`, returning 201. That last
behaviour is why this script exists in this form: a verifier that trusted the
status code would have passed 806 mangled names.

So the record is seven objects: six files deposited individually, and one zip
holding the whole tree with its documented paths intact. Nothing is flattened.

WHAT IS CHECKED, AND HOW THE CHAIN CLOSES:

  individual objects   size and MD5 against the staged file, as before
  the archive object   size and MD5 against the local zip
  the archive CONTENTS the manifest's per-file size and SHA-256 against the
                       zip's members, read locally

The third check is local, so on its own it says nothing about what Zenodo
holds. It closes only in combination with the second: if the uploaded archive
has the same MD5 as the local zip, and the local zip's members match the
manifest, then the uploaded archive contains the manifest's tree. The script
prints that chain rather than leaving a reader to assume it.

ANYTHING IT CANNOT CHECK IS REPORTED AS UNCHECKED, NEVER AS PASSED, and
unchecked is not a clean exit. A verifier whose silence means "fine" is the
same defect as the 201 above.

Read-only. Never publishes, never deletes.

  ZENODO_TOKEN=$(security find-generic-password -a "$USER" -s zenodo-live -w) \
    python3 scripts/zenodo_verify.py --deposition-id 123 \
      --stage-dir ~/Jay_NIW/paper2-zenodo \
      --archive ~/Jay_NIW/paper2-rhc-artifact-1.0.1.zip

  python3 scripts/zenodo_verify.py --self-test    corrupt an entry, prove it fails
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zenodo_deposit import LIVE, SANDBOX, api  # noqa: E402

# Deposited as their own objects so a reader can take any of them without
# pulling 400 MB. Every one is a flat key, which is the only kind Zenodo keeps.
INDIVIDUAL = ('README.md', 'LICENSE', 'PRE-REGISTRATION.md', 'MANIFEST.json',
              'article.pdf', 'supplement-S1.pdf')


def digest(path, algo):
    h = hashlib.new(algo)
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_of(fh):
    h = hashlib.sha256()
    for chunk in iter(lambda: fh.read(1 << 20), b''):
        h.update(chunk)
    return h.hexdigest()


class Result(object):
    def __init__(self):
        self.missing, self.extra = [], []
        self.bad_size, self.bad_hash = [], []
        self.unchecked = []
        self.checked = 0

    @property
    def failed(self):
        return bool(self.missing or self.extra or self.bad_size or self.bad_hash)

    @property
    def clean(self):
        return not self.failed and not self.unchecked


def check_objects(base, token, dep_id, stage, archive, r):
    """The deposition's own objects: the six individuals and the archive."""
    st, files = api(base, token, 'GET', '/deposit/depositions/%s/files' % dep_id)
    if st != 200 or not isinstance(files, list):
        r.unchecked.append('deposition file list unavailable (status %s)' % st)
        return
    have = {(f.get('filename') or f.get('key')): f for f in files}

    want = {}
    for name in INDIVIDUAL:
        p = os.path.join(stage, name)
        if os.path.isfile(p):
            want[name] = p
        else:
            r.unchecked.append('%s is not in the stage directory' % name)
    if archive:
        want[os.path.basename(archive)] = archive
    else:
        r.unchecked.append('no --archive given: the archive object\'s size and '
                           'checksum, and every file inside it, are unchecked')

    r.missing += sorted(k for k in want if k not in have)
    r.extra += sorted(k for k in have if k not in want)
    for key, path in sorted(want.items()):
        if key not in have:
            continue
        h = have[key]
        size = h.get('filesize') or h.get('size')
        if size is None:
            r.unchecked.append('%s: deposition reports no size' % key)
            continue
        if size != os.path.getsize(path):
            r.bad_size.append((key, os.path.getsize(path), size))
            continue
        remote = (h.get('checksum') or '').replace('md5:', '')
        if not remote:
            r.unchecked.append('%s: deposition reports no checksum' % key)
            continue
        local = digest(path, 'md5')
        if local != remote:
            r.bad_hash.append((key, local, remote))
        else:
            r.checked += 1


def check_archive_contents(archive, man, r):
    """The manifest's per-file size and SHA-256 against the zip's members."""
    if not archive:
        return
    if not os.path.isfile(archive):
        r.unchecked.append('archive %s not found; its contents are unchecked'
                           % archive)
        return
    want = {f['path']: f for f in man['files']}
    with zipfile.ZipFile(archive) as z:
        inside = {i.filename: i for i in z.infolist() if not i.is_dir()}
        for path in sorted(set(want) - set(inside)):
            r.missing.append('%s (inside the archive)' % path)
        # MANIFEST.json is written before the archive and cannot contain its
        # own hash, so it is legitimately inside the archive and absent from
        # the list the archive is checked against. Its own integrity is
        # checked where it can be: as one of the individual objects.
        for path in sorted(set(inside) - set(want) - {'MANIFEST.json'}):
            r.extra.append('%s (inside the archive)' % path)
        for path, w in sorted(want.items()):
            info = inside.get(path)
            if info is None:
                continue
            if info.file_size != w['bytes']:
                r.bad_size.append((path + ' (in archive)', w['bytes'],
                                   info.file_size))
                continue
            if not w.get('sha256'):
                r.unchecked.append('%s: manifest carries no SHA-256' % path)
                continue
            with z.open(info) as fh:
                got = sha256_of(fh)
            if got != w['sha256']:
                r.bad_hash.append((path + ' (in archive)', got, w['sha256']))
            else:
                r.checked += 1


def report(r, dep_id, archive):
    print('deposition %s' % dep_id)
    print('  objects verified  : %d' % r.checked)
    print('  missing           : %d' % len(r.missing))
    print('  extra             : %d' % len(r.extra))
    print('  wrong size        : %d' % len(r.bad_size))
    print('  wrong hash        : %d' % len(r.bad_hash))
    print('  UNCHECKED         : %d' % len(r.unchecked))
    for k in r.missing[:10]:
        print('    MISSING   %s' % k)
    for k in r.extra[:10]:
        print('    EXTRA     %s' % k)
    for k, w, g in r.bad_size[:10]:
        print('    SIZE      %s want %s got %s' % (k, w, g))
    for k, a, b in r.bad_hash[:10]:
        print('    HASH      %s  %s... vs %s...' % (k, str(a)[:12], str(b)[:12]))
    for m in r.unchecked[:10]:
        print('    UNCHECKED %s' % m)
    print()
    if r.clean and archive:
        print('The uploaded archive has the same checksum as the local zip, and')
        print('the local zip\'s members match MANIFEST.json, so the uploaded')
        print('archive holds the manifest\'s tree with its paths intact.')
        print('VERIFIED - safe to publish')
    elif r.failed:
        print('NOT VERIFIED - do not publish')
    else:
        print('INCOMPLETE - %d thing(s) unchecked; do not publish on this'
              % len(r.unchecked))


def self_test():
    """Corrupt one manifest entry and prove the archive check catches it."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix='zverify-')
    payload = {'traces/a.gz': b'alpha' * 100, 'results/b.json': b'{"x":1}'}
    zpath = os.path.join(tmp, 'pkg.zip')
    with zipfile.ZipFile(zpath, 'w') as z:
        for name, data in payload.items():
            z.writestr(name, data)
    files = [{'path': n, 'bytes': len(d),
              'sha256': hashlib.sha256(d).hexdigest()}
             for n, d in payload.items()]

    ok = True
    r = Result()
    check_archive_contents(zpath, {'files': files}, r)
    good = r.clean and r.checked == 2
    print('  %-5s intact archive         -> %d verified, %d bad'
          % ('PASS' if good else 'FAIL', r.checked,
             len(r.bad_hash) + len(r.bad_size)))
    ok = ok and good

    bad = json.loads(json.dumps(files))
    bad[0]['sha256'] = 'deadbeef' * 8          # a wrong hash, right size
    r = Result()
    check_archive_contents(zpath, {'files': bad}, r)
    caught = len(r.bad_hash) == 1 and r.failed
    print('  %-5s corrupted SHA-256      -> %s'
          % ('PASS' if caught else 'FAIL',
             ('caught: %s' % r.bad_hash[0][0]) if r.bad_hash else 'NOT CAUGHT'))
    ok = ok and caught

    bad = json.loads(json.dumps(files))
    bad[1]['bytes'] = 999999
    r = Result()
    check_archive_contents(zpath, {'files': bad}, r)
    caught = len(r.bad_size) == 1 and r.failed
    print('  %-5s corrupted size         -> %s'
          % ('PASS' if caught else 'FAIL',
             ('caught: %s' % r.bad_size[0][0]) if r.bad_size else 'NOT CAUGHT'))
    ok = ok and caught

    bad = json.loads(json.dumps(files)) + [
        {'path': 'traces/ghost.gz', 'bytes': 1, 'sha256': 'ab' * 32}]
    r = Result()
    check_archive_contents(zpath, {'files': bad}, r)
    caught = any('ghost' in m for m in r.missing)
    print('  %-5s manifest entry absent from the archive -> %s'
          % ('PASS' if caught else 'FAIL', 'caught' if caught else 'NOT CAUGHT'))
    ok = ok and caught

    r = Result()
    check_archive_contents(zpath, {'files': files[:1]}, r)
    caught = any('results/b.json' in m for m in r.extra)
    print('  %-5s archive member absent from the manifest -> %s'
          % ('PASS' if caught else 'FAIL', 'caught' if caught else 'NOT CAUGHT'))
    ok = ok and caught

    r = Result()
    check_archive_contents(None, {'files': files}, r)
    r2 = Result()
    r2.unchecked.append('x')
    silent = r2.clean
    print('  %-5s unchecked does not count as clean -> %s'
          % ('PASS' if not silent else 'FAIL',
             'correct' if not silent else 'UNCHECKED READS AS PASS'))
    ok = ok and not silent

    print('self-test %s' % ('passed' if ok else 'FAILED'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deposition-id', type=int)
    ap.add_argument('--stage-dir')
    ap.add_argument('--archive', help='the local zip that was deposited')
    ap.add_argument('--sandbox', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.deposition_id and a.stage_dir):
        ap.error('--deposition-id and --stage-dir are required')

    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        print('ZENODO_TOKEN not set.')
        return 2
    base = SANDBOX if a.sandbox else LIVE
    archive = os.path.expanduser(a.archive) if a.archive else None
    man = json.load(open(os.path.join(a.stage_dir, 'MANIFEST.json')))

    r = Result()
    check_objects(base, token, a.deposition_id, a.stage_dir, archive, r)
    check_archive_contents(archive, man, r)
    report(r, a.deposition_id, archive)
    return 0 if r.clean else 1


if __name__ == '__main__':
    sys.exit(main())
