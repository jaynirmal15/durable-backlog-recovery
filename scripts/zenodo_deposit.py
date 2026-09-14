#!/usr/bin/env python3
"""Create or resume a Zenodo draft, upload the package, and stop before publishing.

NEVER PUBLISHES. A published Zenodo record cannot be deleted and its files cannot
be changed, so this script has no publish path at all. It leaves a complete draft
and prints the DOI and review URL.

  export ZENODO_TOKEN=...                       scopes: deposit:write, deposit:actions
  python3 scripts/zenodo_deposit.py --probe --deposition-id 22740491
  python3 scripts/zenodo_deposit.py --stage-dir ~/Jay_NIW/paper2-zenodo \
      --deposition-id 22740491
  python3 scripts/zenodo_deposit.py --list-drafts
  python3 scripts/zenodo_deposit.py --delete-draft 12345678

Directory structure is preserved. The package README documents paths like
`--raw-dir traces`, and the reproducibility statement depends on them, so keys
keep their slashes. If the API refuses nested keys this script STOPS and says so
rather than flattening.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

LIVE = 'https://zenodo.org/api'
SANDBOX = 'https://sandbox.zenodo.org/api'
CHUNK = 1 << 20


RETRY_STATUS = (0, 429, 500, 502, 503, 504)


def request(url, token, method='GET', payload=None, body=None, ctype=None,
            length=None, verbose=False, retries=4, backoff=5.0):
    """One API call, retried on transient failures.

    Zenodo returns 504 across the whole API during an outage, including
    unauthenticated reads, and a 758-file upload is long enough that a transient
    5xx partway through is likely rather than exceptional. A body that is a file
    object is re-opened per attempt, since a consumed stream cannot be replayed.
    """
    path = None
    if hasattr(body, 'read'):
        path = body.name
        body.close()
    last = (0, {'error': 'no attempt made'})
    for attempt in range(retries + 1):
        payload_body = open(path, 'rb') if path else body
        st, out = _once(url, token, method, payload, payload_body, ctype, length,
                        verbose and attempt == retries)
        if st not in RETRY_STATUS:
            return st, out
        last = (st, out)
        if attempt < retries:
            wait = backoff * (2 ** attempt)
            if verbose:
                sys.stderr.write('    %s on %s, retrying in %.0fs (attempt %d/%d)\n'
                                 % (st, method, wait, attempt + 1, retries))
            time.sleep(wait)
    return last


def _once(url, token, method='GET', payload=None, body=None, ctype=None,
          length=None, verbose=False):
    """One API call. Auth goes in the header: Zenodo's files API answers 404,
    not 401, when a request is unauthorised, so a token passed only as a query
    parameter fails in a way that looks exactly like a missing object."""
    data = body if body is not None else (
        json.dumps(payload).encode() if payload is not None else None)
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', 'Bearer %s' % token)
    if ctype:
        req.add_header('Content-Type', ctype)
    elif payload is not None:
        req.add_header('Content-Type', 'application/json')
    if length is not None:
        req.add_header('Content-Length', str(length))
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', 'replace')
        if verbose:
            sys.stderr.write('\n--- %s %s\n    status %s %s\n    headers %s\n    body %s\n'
                             % (method, url.split('?')[0], e.code, e.reason,
                                dict(e.headers), detail[:800]))
        return e.code, {'error': detail}
    except urllib.error.URLError as e:
        if verbose:
            sys.stderr.write('\n--- %s %s\n    transport error %s\n'
                             % (method, url.split('?')[0], e.reason))
        return 0, {'error': str(e.reason)}


def api(base, token, method, path, **kw):
    return request(base + path, token, method, **kw)


def put_file(bucket, token, key, path, size, verbose=False):
    """Bucket API: PUT {bucket}/{key}. Keys keep their slashes."""
    with open(path, 'rb') as fh:
        return request('%s/%s' % (bucket, key), token, 'PUT', body=fh,
                       ctype='application/octet-stream', length=size,
                       verbose=verbose)


def probe(base, token, dep_id):
    """Upload two tiny objects, one flat and one nested, and report both.

    This separates "the API will not take nested keys" from "the request is
    being rejected for some other reason" for a couple of kilobytes, instead of
    inferring it from a 407 MB failure.
    """
    st, dep = api(base, token, 'GET', '/deposit/depositions/%s' % dep_id, verbose=True)
    if st != 200:
        print('cannot read deposition %s: status %s' % (dep_id, st))
        return 1
    bucket = (dep.get('links') or {}).get('bucket')
    print('deposition %s state=%s submitted=%s' % (dep_id, dep.get('state'), dep.get('submitted')))
    print('bucket link: %s' % bucket)
    if not bucket:
        print('NO BUCKET LINK. links present: %s' % sorted((dep.get('links') or {})))
        return 1
    tmp = '/tmp/_zenodo_probe.txt'
    open(tmp, 'w').write('probe\n')
    n = os.path.getsize(tmp)
    for key in ('_probe_flat.txt', '_probe_dir/_probe_nested.txt'):
        st, body = put_file(bucket, token, key, tmp, n, verbose=True)
        print('  PUT %-34s -> %s %s' % (key, st, 'OK' if st in (200, 201) else body.get('error', '')[:120]))
    print()
    print('legacy files API, same two keys:')
    for key in ('_probe_flat2.txt', '_probe_dir2/_probe_nested2.txt'):
        st, body = legacy_put(base, token, dep_id, key, tmp, verbose=True)
        print('  POST %-33s -> %s %s' % (key, st, 'OK' if st in (200, 201) else str(body)[:120]))
    print()
    print('Interpretation: if the flat key succeeds and the nested one 404s, the')
    print('API will not take slashes. If both fail the same way, the problem is')
    print('not nesting. Delete the probe objects before the real upload.')
    return 0


def legacy_put(base, token, dep_id, key, path, verbose=False):
    """Legacy deposit files API: multipart POST with a `name` field."""
    boundary = '----zenodo%d' % os.getpid()
    with open(path, 'rb') as fh:
        payload = fh.read()
    parts = []
    parts.append(('--%s\r\nContent-Disposition: form-data; name="name"\r\n\r\n%s\r\n'
                  % (boundary, key)).encode())
    parts.append(('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
                  'Content-Type: application/octet-stream\r\n\r\n' % (boundary, key)).encode())
    parts.append(payload)
    parts.append(('\r\n--%s--\r\n' % boundary).encode())
    body = b''.join(parts)
    return request('%s/deposit/depositions/%s/files' % (base, dep_id), token, 'POST',
                   body=body, ctype='multipart/form-data; boundary=%s' % boundary,
                   length=len(body), verbose=verbose)


def existing_files(base, token, dep_id):
    """Key -> size for what is already uploaded, so a resume skips it."""
    st, body = api(base, token, 'GET', '/deposit/depositions/%s/files' % dep_id)
    if st != 200 or not isinstance(body, list):
        return {}
    out = {}
    for f in body:
        key = f.get('filename') or f.get('key')
        size = f.get('filesize') or f.get('size')
        if key:
            out[key] = size
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage-dir')
    ap.add_argument('--deposition-id', type=int,
                    help='resume into this draft instead of creating one')
    ap.add_argument('--sandbox', action='store_true')
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--list-drafts', action='store_true')
    ap.add_argument('--delete-draft', type=int)
    ap.add_argument('--verbose', action='store_true', default=True)
    a = ap.parse_args()

    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        print('ZENODO_TOKEN is not set in this process environment. Nothing was sent.')
        return 2
    base = SANDBOX if a.sandbox else LIVE

    if a.list_drafts:
        st, body = api(base, token, 'GET', '/deposit/depositions?size=100', verbose=True)
        if st != 200:
            print('list failed: %s' % st)
            return 1
        print('%-12s %-10s %-12s %-46s %s' % ('id', 'state', 'submitted', 'title', 'doi'))
        for d in body:
            print('%-12s %-10s %-12s %-46s %s'
                  % (d.get('id'), d.get('state'), d.get('submitted'),
                     (d.get('title') or '(untitled)')[:46],
                     (d.get('metadata') or {}).get('prereserve_doi', {}).get('doi')
                     or d.get('doi') or ''))
        print()
        print('Unpublished drafts have state=unsubmitted. Published records are never')
        print('deletable and are listed here only so they can be recognised and left alone.')
        return 0

    if a.delete_draft:
        st, dep = api(base, token, 'GET', '/deposit/depositions/%s' % a.delete_draft)
        if st != 200:
            print('cannot read %s: %s' % (a.delete_draft, st))
            return 1
        if dep.get('submitted'):
            print('REFUSING: deposition %s is submitted/published and cannot be deleted.'
                  % a.delete_draft)
            return 1
        print('deleting draft %s  title=%r' % (a.delete_draft,
                                               (dep.get('title') or '')[:60]))
        st, body = api(base, token, 'DELETE', '/deposit/depositions/%s' % a.delete_draft,
                       verbose=True)
        print('  -> %s' % ('deleted' if st in (201, 204) else 'failed %s %s' % (st, body)))
        return 0 if st in (201, 204) else 1

    if a.probe:
        if not a.deposition_id:
            print('--probe needs --deposition-id')
            return 2
        return probe(base, token, a.deposition_id)

    if not a.stage_dir:
        print('--stage-dir is required to upload')
        return 2
    man = json.load(open(os.path.join(a.stage_dir, 'MANIFEST.json')))

    if a.deposition_id:
        dep_id = a.deposition_id
        st, dep = api(base, token, 'GET', '/deposit/depositions/%s' % dep_id, verbose=True)
        if st != 200:
            print('cannot resume %s: status %s' % (dep_id, st))
            return 1
        if dep.get('submitted'):
            print('REFUSING: %s is already submitted. This script never modifies a '
                  'published record.' % dep_id)
            return 1
        print('resuming draft %s' % dep_id)
    else:
        st, dep = api(base, token, 'POST', '/deposit/depositions', payload={}, verbose=True)
        if st not in (200, 201):
            print('create failed: %s %s' % (st, dep))
            return 1
        dep_id = dep['id']
        print('created draft %s' % dep_id)

    meta = dict(man['metadata'])
    meta['notes'] = ('Generated from git commit %s. Every file hashed in MANIFEST.json.'
                     % man['gitCommit'])
    st, _ = api(base, token, 'PUT', '/deposit/depositions/%s' % dep_id,
                payload={'metadata': meta}, verbose=True)
    if st != 200:
        print('metadata PUT failed: %s' % st)
        return 1

    st, dep = api(base, token, 'GET', '/deposit/depositions/%s' % dep_id)
    doi = ((dep.get('metadata') or {}).get('prereserve_doi') or {}).get('doi') or dep.get('doi')
    bucket = (dep.get('links') or {}).get('bucket')
    print('  DOI reserved: %s' % doi)
    if not bucket:
        print('  no bucket link; links: %s' % sorted(dep.get('links') or {}))
        return 1

    # MANIFEST.json is written after the file walk, so it is absent from its own
    # list. The README points at it and the reproducibility statement depends on
    # it, so it is added explicitly rather than silently dropped.
    files = list(man['files'])
    if not any(f['path'] == 'MANIFEST.json' for f in files):
        mp = os.path.join(a.stage_dir, 'MANIFEST.json')
        files.append({'path': 'MANIFEST.json', 'bytes': os.path.getsize(mp)})

    have = existing_files(base, token, dep_id)
    print('  already uploaded: %d files' % len(have))

    todo = [f for f in files
            if not (f['path'] in have and have[f['path']] == f['bytes'])]
    skipped = len(files) - len(todo)
    print('  skipping %d unchanged, uploading %d (%.1f MB)'
          % (skipped, len(todo), sum(f['bytes'] for f in todo) / 1048576.0))

    failed = []
    for i, f in enumerate(todo, 1):
        p = os.path.join(a.stage_dir, f['path'])
        st, body = put_file(bucket, token, f['path'], p, f['bytes'],
                            verbose=(a.verbose and len(failed) < 3))
        if st not in (200, 201):
            failed.append((f['path'], st, str(body)[:160]))
            if len(failed) >= 3:
                print()
                print('STOPPING after 3 failures. Nothing was flattened.')
                for k, s, b in failed:
                    print('  %-52s %s %s' % (k, s, b[:80]))
                nested = [k for k, _, _ in failed if '/' in k]
                flat = [k for k, _, _ in failed if '/' not in k]
                print()
                if nested and not flat:
                    print('Every failure has a nested key. Run --probe to confirm whether a')
                    print('flat key succeeds on the same draft before concluding.')
                    print('Flattening would break the documented layout (traces/, results/,')
                    print('scripts/) that the package README and the reproducibility')
                    print('statement depend on, so it is NOT done automatically.')
                else:
                    print('Failures include flat keys, so nesting is not the cause.')
                return 1
        if i % 25 == 0 or i == len(todo):
            print('  uploaded %d/%d' % (i, len(todo)))

    print()
    print('DRAFT COMPLETE, NOT PUBLISHED')
    print('  deposition : %s' % dep_id)
    print('  DOI        : %s' % doi)
    print('  review at  : %s/deposit/%s'
          % ('https://sandbox.zenodo.org' if a.sandbox else 'https://zenodo.org', dep_id))
    print('  files      : %d, %.1f MB' % (len(files),
                                          man['totalBytes'] / 1048576.0))
    print()
    print('Publishing is irreversible and this script will not do it. Publish from')
    print('the web interface after review.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
