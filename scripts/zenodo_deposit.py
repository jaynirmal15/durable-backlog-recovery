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
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

class WouldWrite(Exception):
    """A read-only path tried to issue a write. Never caught; always fatal."""


LIVE = 'https://zenodo.org/api'
SANDBOX = 'https://sandbox.zenodo.org/api'
CHUNK = 1 << 20


RETRY_STATUS = (0, 429, 500, 502, 503, 504)


READ_ONLY = [False]             # set while --plan-only runs; see WouldWrite


def request(url, token, method='GET', payload=None, body=None, ctype=None,
            length=None, verbose=False, retries=4, backoff=5.0):
    """One API call, retried on transient failures.

    Zenodo returns 504 across the whole API during an outage, including
    unauthenticated reads, and a 758-file upload is long enough that a transient
    5xx partway through is likely rather than exceptional. A body that is a file
    object is re-opened per attempt, since a consumed stream cannot be replayed.
    """
    # READ-ONLY IS ENFORCED HERE, not promised by each caller. Every request
    # in this module goes through this function, so a write attempted while
    # the flag is set cannot reach the network -- including one added later by
    # someone who did not read the docstring of the mode they were editing.
    if READ_ONLY[0] and method != 'GET':
        raise WouldWrite('%s %s attempted in a read-only mode'
                         % (method, url.split('?')[0]))
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


# Deposited as their own objects: every one is a flat key, which is the only
# kind Zenodo keeps. zenodo_verify.py holds the same list and checks it.
# FOUR, not six: the manuscript PDFs left the deposit on 2026-09-24 so that
# the package stops depending on the paper. With the archive that is FIVE
# objects on the record, not seven.
HYBRID_INDIVIDUAL = ('README.md', 'LICENSE', 'PRE-REGISTRATION.md',
                     'MANIFEST.json')


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


EDIT_WINDOW_DAYS = 30           # Zenodo's self-service file-edit window


def read_only(base, token, path):
    """GET, and nothing but GET.

    --plan-only must be provably read-only, so it cannot reach `api()` at all:
    it goes through here, and this refuses any verb but GET by construction
    rather than by care. A read-only mode that merely "does not happen to
    write" is a promise; one that cannot express a write is a property.
    """
    st, body = request(base + path, token, 'GET')
    return st, body


def plan_only(base, token, dep_id, stage_dir, archive):
    """Print what a replacement WOULD change. Read-only, and always non-zero.

    It exists because conditions 5 and 6 of --publish-edit are post-upload
    facts -- the record holding the staged sizes, and zenodo_verify passing
    against it -- so a gate built from them cannot fire before the upload.
    This gate can: it compares the record as it is now against the staging as
    it is now, and asks a person to rule before anything moves.

    IT SATISFIES NO PRECONDITION OF --publish-edit. It writes no flag file,
    caches nothing, and shares no state with it. Running this does not make
    the next command easier, and that is deliberate: a review step that
    unlocks something is a step people learn to skip.
    """
    if not os.path.isdir(stage_dir):
        print('stage directory not found: %s' % stage_dir)
        return 1
    if not (archive and os.path.isfile(archive)):
        print('archive not found: %s' % archive)
        return 1

    READ_ONLY[0] = True
    try:
        return _plan(base, token, dep_id, stage_dir, archive)
    finally:
        READ_ONLY[0] = False


def _plan(base, token, dep_id, stage_dir, archive):
    st, dep = read_only(base, token, '/deposit/depositions/%s' % dep_id)
    if st != 200:
        print('cannot read deposition %s: status %s' % (dep_id, st))
        return 1
    st, files = read_only(base, token,
                          '/deposit/depositions/%s/files' % dep_id)
    if st != 200 or not isinstance(files, list):
        print('cannot read the file list: status %s' % st)
        return 1

    live = {}
    for f in files:
        live[f.get('filename') or f.get('key')] = (
            int(f.get('filesize') or f.get('size') or 0),
            (f.get('checksum') or '').replace('md5:', ''))

    staged = {}
    for name in HYBRID_INDIVIDUAL:
        fp = os.path.join(stage_dir, name)
        staged[name] = ((os.path.getsize(fp), md5_of(fp))
                        if os.path.isfile(fp) else (None, None))
    staged[os.path.basename(archive)] = (os.path.getsize(archive),
                                         md5_of(archive))

    doi = dep.get('doi') or ((dep.get('metadata') or {}).get('doi')) or '(none)'
    print('PLAN ONLY -- read-only, nothing was sent, nothing is unlocked.')
    print()
    print('deposition %s   DOI %s' % (dep_id, doi))
    print('state %r   submitted %s   published %s'
          % (dep.get('state'), dep.get('submitted'),
             (dep.get('metadata') or {}).get('publication_date')))
    print()
    keys = sorted(set(live) | set(staged))
    print('%-32s %12s %-34s %s' % ('key', 'bytes', 'md5', 'verdict'))
    replace = 0
    for k in keys:
        lsz, lmd5 = live.get(k, (None, None))
        ssz, smd5 = staged.get(k, (None, None))
        if lsz is None:
            verdict = 'ADD -- not on the record'
        elif ssz is None:
            verdict = 'NOT STAGED -- would be left as is'
        elif (lsz, lmd5) == (ssz, smd5):
            verdict = 'unchanged'
        else:
            verdict = 'REPLACE'
            replace += 1
        print('%-32s %12s %-34s   live' % (k, lsz if lsz is not None else '-',
                                           lmd5 or '-'))
        print('%-32s %12s %-34s   staged -> %s'
              % ('', ssz if ssz is not None else '-', smd5 or '-', verdict))
    print()
    print('%d of %d object(s) would be replaced.' % (replace, len(keys)))
    print()
    print('Nothing has been sent. This mode issues GET only and always exits')
    print('non-zero, so it can never read as success and can never stand in')
    print('for the checks --publish-edit makes against real uploaded state.')
    return 1


def publish_edit(base, token, dep_id, expect_doi, stage_dir, archive,
                 confirm=False):
    """Publish a file edit on an ALREADY-PUBLISHED record. The only publish path.

    THIS SCRIPT HAS NO GENERAL PUBLISH PATH AND MUST NOT ACQUIRE ONE. First
    publication is irreversible, needs a human reading the record, and happens
    from the web interface. This exception exists for one situation only:
    replacing files on a record that is already published, inside Zenodo's
    30-day window, where the edit does not take effect until it is published.
    Every condition below is checked against a FRESH READ of the record, never
    against an argument, and every branch refuses by default.

    A DRY RUN IS THE DEFAULT. Without --confirm it prints the plan and exits
    NON-ZERO. The value of printing the plan is that a person can stop it, and
    a plan that proceeds on its own has no such value.
    """
    st, dep = api(base, token, 'GET', '/deposit/depositions/%s' % dep_id)
    if st != 200:
        print('cannot read deposition %s: status %s' % (dep_id, st))
        return 1

    # 1. already published, so this can never create a first publication
    if not dep.get('submitted'):
        print('REFUSED: deposition %s has never been published. This flag '
              'edits an existing record; it does not publish a new one.'
              % dep_id)
        return 1

    # 2. an edit must be open, or there is nothing to commit
    if dep.get('state') != 'inprogress':
        print('REFUSED: state is %r, not "inprogress". Open the edit first '
              '(POST /actions/edit); publishing without an open edit would '
              'republish whatever is there.' % dep.get('state'))
        return 1

    # 3. inside the window, computed from the record
    created = (dep.get('created') or '')[:10]
    pub = (dep.get('metadata') or {}).get('publication_date') or created
    try:
        age = (datetime.date.today()
               - datetime.date(*[int(x) for x in pub.split('-')[:3]])).days
    except Exception:
        print('REFUSED: cannot read a publication date from the record.')
        return 1
    if age > EDIT_WINDOW_DAYS:
        print('REFUSED: the record was published %s, %d days ago. Zenodo\'s '
              'self-service file edit is %d days; past it, files change only '
              'by contacting support.' % (pub, age, EDIT_WINDOW_DAYS))
        return 1

    # 4. the DOI must be the one expected, and must not move
    doi = dep.get('doi') or ((dep.get('metadata') or {}).get('doi'))
    if not doi:
        print('REFUSED: the record reports no DOI.')
        return 1
    if doi != expect_doi:
        print('REFUSED: --expect-doi is %r but the record holds %r.'
              % (expect_doi, doi))
        return 1

    # 5. the record must hold exactly the seven expected keys, at the sizes
    #    the staging says, so a partial upload cannot be published
    want = {}
    for name in HYBRID_INDIVIDUAL:
        fp = os.path.join(stage_dir, name)
        if not os.path.isfile(fp):
            print('REFUSED: %s is not in the stage directory.' % name)
            return 1
        want[name] = os.path.getsize(fp)
    if not (archive and os.path.isfile(archive)):
        print('REFUSED: --archive is required and must exist.')
        return 1
    want[os.path.basename(archive)] = os.path.getsize(archive)

    have = existing_files(base, token, dep_id)
    missing = sorted(set(want) - set(have))
    extra = sorted(set(have) - set(want))
    wrong = sorted(k for k in want if k in have and have[k] != want[k])
    if missing or extra:
        print('REFUSED: the record does not hold exactly the %d expected '
              'objects.' % len(want))
        for k in missing:
            print('   missing  %s' % k)
        for k in extra:
            print('   extra    %s' % k)
        return 1
    if wrong:
        print('REFUSED: %d object(s) are uploaded at the wrong size; the '
              'upload is incomplete.' % len(wrong))
        for k in wrong:
            print('   %-34s record %s, staged %s' % (k, have[k], want[k]))
        return 1

    # 6. the verifier must pass in THIS invocation, not a remembered one
    verify = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'zenodo_verify.py')
    rc = subprocess.call([sys.executable, verify,
                          '--deposition-id', str(dep_id),
                          '--stage-dir', stage_dir, '--archive', archive]
                         + (['--sandbox'] if base == SANDBOX else []))
    if rc != 0:
        print('\nREFUSED: zenodo_verify.py did not pass (exit %d).' % rc)
        return 1

    # 7. the plan, printed so a person can stop it
    print()
    print('PLAN for deposition %s, DOI %s' % (dep_id, doi))
    print('  published %s, %d day(s) ago, inside the %d-day window'
          % (pub, age, EDIT_WINDOW_DAYS))
    print('  %d objects; digests before and after:' % len(want))
    changed = 0
    for key in sorted(want):
        local = os.path.join(stage_dir, key) if key in HYBRID_INDIVIDUAL else archive
        new = md5_of(local)
        old = have_md5(base, token, dep_id).get(key, '(unknown)')
        mark = '  CHANGES' if old != new else ''
        changed += 1 if old != new else 0
        print('    %-34s %s -> %s%s' % (key, old[:12], new[:12], mark))
    print('  %d of %d objects change.' % (changed, len(want)))
    if not confirm:
        print()
        print('DRY RUN. Nothing was published. Re-run with --confirm to '
              'publish this edit.')
        return 1

    st, out = api(base, token, 'POST',
                  '/deposit/depositions/%s/actions/publish' % dep_id)
    if st not in (200, 202):
        print('publish failed: status %s %s' % (st, str(out)[:200]))
        return 1
    st2, after = api(base, token, 'GET', '/deposit/depositions/%s' % dep_id)
    now = after.get('doi') or ((after.get('metadata') or {}).get('doi'))
    print('published. DOI before %s, after %s -- %s'
          % (doi, now, 'UNCHANGED' if now == doi else '** DOI MOVED **'))
    return 0 if now == doi else 1


def md5_of(path):
    h = hashlib.md5()
    with open(path, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def have_md5(base, token, dep_id):
    st, files = api(base, token, 'GET',
                    '/deposit/depositions/%s/files' % dep_id)
    if st != 200 or not isinstance(files, list):
        return {}
    return {(f.get('filename') or f.get('key')):
            (f.get('checksum') or '').replace('md5:', '') for f in files}


def existing_files(base, token, dep_id):
    """Key -> (size, md5) for what is already uploaded.

    IT RETURNS THE DIGEST BECAUSE SIZE IS NOT IDENTITY. MANIFEST.json was
    141,778 bytes before and after a correction, with entirely different
    content: the old one certified the superseded article.pdf. A resume that
    skipped on key and size would have left that stale object in place and
    published it. Same defect class as the size-only comparison named in
    OUTLINE.md -- a check that passes while measuring the wrong property.
    """
    st, body = api(base, token, 'GET', '/deposit/depositions/%s/files' % dep_id)
    if st != 200 or not isinstance(body, list):
        return {}
    out = {}
    for f in body:
        key = f.get('filename') or f.get('key')
        if key:
            out[key] = (int(f.get('filesize') or f.get('size') or 0),
                        (f.get('checksum') or '').replace('md5:', ''))
    return out


class ReadbackMismatch(Exception):
    """The record holds something other than what was sent. Contents suspect."""


class TransportFailure(Exception):
    """The wire broke. Whether the server accepted the body is UNKNOWN."""


class HTTPRefusal(Exception):
    """The server answered with a status and refused. A premise, not a hiccup."""


def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def put_verified(base, token, dep_id, bucket, key, path, log=print):
    """PUT one object and prove the record holds it. Three failure branches.

    THE BRANCHES ARE NOT INTERCHANGEABLE, and collapsing them cost a draft:

      readback mismatch   the record's contents are untrustworthy. Raise
                          ReadbackMismatch; the caller deletes the draft.
      transport failure   the wire broke and what the server did is UNKNOWN --
                          a broken pipe can land AFTER the body was accepted,
                          so the object may well exist. RESOLVE BY READING,
                          never by inference: re-read the object and re-PUT
                          only if it is absent or wrong.
      HTTP status error   the server answered and refused. 403 "bucket is
                          locked" is a premise failure, not a hiccup. Raise
                          HTTPRefusal; stop and report, delete nothing.
    """
    if '/' in key:
        raise HTTPRefusal('key %r contains a slash; the bucket 404s on those'
                          % key)
    size, want = os.path.getsize(path), md5_file(path)
    for attempt in (1, 2):
        st, body = put_file(bucket, token, key, path, size)
        if st in (200, 201):
            break
        if st == 0:
            log('  transport failure on %s (%s); re-reading the record rather '
                'than assuming' % (key, str(body.get('error'))[:60]))
            have = existing_files(base, token, dep_id).get(key)
            if have == (size, want):
                log('  %s is present and correct despite the broken pipe; '
                    'moving on' % key)
                return 'landed-after-transport-failure'
            log('  %s is %s; re-sending'
                % (key, 'absent' if have is None else 'present but wrong'))
            if attempt == 2:
                raise TransportFailure('%s still not correct after a re-send'
                                       % key)
            continue
        raise HTTPRefusal('PUT %s returned %s: %s'
                          % (key, st, str(body)[:200]))
    have = existing_files(base, token, dep_id).get(key)
    if have is None:
        raise ReadbackMismatch('%s is absent after a success status -- the key '
                               'was renamed or dropped' % key)
    if have != (size, want):
        raise ReadbackMismatch('%s read back %s/%s, sent %s/%s'
                               % (key, have[0], have[1], size, want))
    return 'uploaded'





def metadata_only(base, token, dep_id, man):
    """Create or resume a draft, set metadata, reserve the DOI, and stop.

    Uploads nothing. This function never reaches put_file() or legacy_put(),
    and there is no publish action anywhere in this module to reach either.
    """
    if dep_id:
        st, dep = api(base, token, 'GET', '/deposit/depositions/%s' % dep_id,
                      verbose=True)
        if st != 200:
            print('cannot resume %s: status %s' % (dep_id, st))
            return 1
        if dep.get('submitted'):
            print('REFUSING: %s is already submitted.' % dep_id)
            return 1
        print('resuming draft %s' % dep_id)
    else:
        st, dep = api(base, token, 'POST', '/deposit/depositions', payload={},
                      verbose=True)
        if st not in (200, 201):
            print('create failed: %s %s' % (st, dep))
            return 1
        dep_id = dep['id']
        print('created draft %s' % dep_id)

    meta = dict(man['metadata'])
    meta['notes'] = ('Generated from git commit %s. Every file hashed in '
                     'MANIFEST.json.' % man['gitCommit'])
    # Ask Zenodo to mint the reserved DOI now, so the manuscript can cite it
    # before the package is uploaded. Reserving does not publish anything.
    meta['prereserve_doi'] = True
    st, _ = api(base, token, 'PUT', '/deposit/depositions/%s' % dep_id,
                payload={'metadata': meta}, verbose=True)
    if st != 200:
        print('metadata PUT failed: %s' % st)
        return 1

    st, dep = api(base, token, 'GET', '/deposit/depositions/%s' % dep_id)
    md = dep.get('metadata') or {}
    doi = (md.get('prereserve_doi') or {}).get('doi') or dep.get('doi')
    st2, files = api(base, token, 'GET',
                     '/deposit/depositions/%s/files' % dep_id)
    nfiles = len(files) if st2 == 200 and isinstance(files, list) else '?'
    print()
    print('deposition id   %s' % dep_id)
    print('reserved DOI    %s' % doi)
    print('state           %s' % dep.get('state'))
    print('files uploaded  %s' % nfiles)
    print()
    print('METADATA ONLY. Nothing was uploaded and nothing was published.')
    print('The package is uploaded at W6, from the frozen commit.')
    return 0 if doi else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage-dir')
    ap.add_argument('--hybrid', action='store_true',
                    help='upload the six flat-keyed files plus --archive, '
                         'instead of walking the tree into nested keys')
    ap.add_argument('--archive', help='the zip holding the full tree')
    ap.add_argument('--deposition-id', type=int,
                    help='resume into this draft instead of creating one')
    ap.add_argument('--sandbox', action='store_true')
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--list-drafts', action='store_true')
    ap.add_argument('--delete-draft', type=int)
    ap.add_argument('--show', type=int,
                    help='READ-ONLY. GET one deposition and its file list and '
                         'print what state it is actually in. Sends no write of '
                         'any kind, unlike --probe, which uploads test objects.')
    ap.add_argument('--metadata-only', action='store_true',
                    help='create (or resume with --deposition-id) a draft, set '
                         'metadata, reserve the DOI, and STOP. Uploads nothing. '
                         'The package goes up separately at W6 from the frozen '
                         'commit; uploading earlier only guarantees it goes stale.')
    ap.add_argument('--publish-edit', type=int, metavar='ID',
                    help='publish a FILE EDIT on an already-published record, '
                         'inside Zenodo\'s 30-day window. Dry run unless '
                         '--confirm. The only publish path in this script.')
    ap.add_argument('--expect-doi',
                    help='the DOI the record must already hold; a precondition '
                         'checked against a fresh read, not an attestation')
    ap.add_argument('--plan-only', type=int, metavar='ID',
                    help='print what a replacement would change, GET only, '
                         'always exits non-zero. Satisfies no precondition of '
                         '--publish-edit.')
    ap.add_argument('--confirm', action='store_true',
                    help='with --publish-edit, actually publish the edit')
    ap.add_argument('--verbose', action='store_true', default=True)
    a = ap.parse_args()

    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        print('ZENODO_TOKEN is not set in this process environment. Nothing was sent.')
        return 2
    base = SANDBOX if a.sandbox else LIVE

    if a.plan_only:
        if not (a.stage_dir and a.archive):
            print('--plan-only requires --stage-dir and --archive.')
            return 1
        return plan_only(base, token, a.plan_only,
                         os.path.expanduser(a.stage_dir),
                         os.path.expanduser(a.archive))

    if a.publish_edit:
        if not a.expect_doi:
            print('--publish-edit requires --expect-doi: the DOI the record '
                  'must already hold, checked against a fresh read.')
            return 1
        if not (a.stage_dir and a.archive):
            print('--publish-edit requires --stage-dir and --archive: the '
                  'record is checked against what was actually staged.')
            return 1
        return publish_edit(base, token, a.publish_edit, a.expect_doi,
                            os.path.expanduser(a.stage_dir),
                            os.path.expanduser(a.archive), a.confirm)

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

    if a.show:
        st, dep = api(base, token, 'GET', '/deposit/depositions/%s' % a.show,
                      verbose=True)
        if st != 200:
            print('cannot read deposition %s: status %s' % (a.show, st))
            return 1
        md = dep.get('metadata') or {}
        pre = (md.get('prereserve_doi') or {})
        print()
        print('deposition   %s' % dep.get('id'))
        print('state        %s' % dep.get('state'))
        print('submitted    %s' % dep.get('submitted'))
        print('title        %r' % (dep.get('title') or '(untitled)'))
        print('created      %s' % dep.get('created'))
        print('modified     %s' % dep.get('modified'))
        print('doi          %s' % (dep.get('doi') or '(none)'))
        print('prereserved  %s' % (pre.get('doi') or '(none)'))
        # The bucket link is the upload path itself. Printing it is what lets
        # --show answer the question DEPOSIT-W6 step 3 asks -- "does the upload
        # path still work" -- without --probe uploading anything to find out.
        bucket = (dep.get('links') or {}).get('bucket')
        print('bucket       %s' % (bucket or '(none -- uploads would fail)'))
        print('metadata keys present: %s' % (sorted(md.keys()) or '(none)'))
        for k in ('title', 'upload_type', 'license', 'version', 'description'):
            v = md.get(k)
            print('   %-14s %s' % (k, ('(unset)' if v is None
                                       else str(v)[:70] + ('...' if len(str(v)) > 70 else ''))))
        print('creators     %s' % (md.get('creators') or '(unset)'))
        st2, files = api(base, token, 'GET',
                         '/deposit/depositions/%s/files' % a.show)
        if st2 == 200 and isinstance(files, list):
            print('files        %d' % len(files))
            for f in files:
                print('   %-44s %s' % (f.get('filename'), f.get('checksum')))
        else:
            print('files        could not list (status %s)' % st2)
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
    if a.metadata_only:
        return metadata_only(base, token, a.deposition_id, man)

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

    # HYBRID DEPOSIT. Zenodo will not store a key containing a slash: the
    # bucket route 404s whether the slash is raw or percent-encoded, and the
    # legacy files API accepts the upload and SILENTLY RENAMES traces/x.gz to
    # traces_x.gz, returning 201. Flattening is forbidden -- the README, the
    # manifest and the paper's reproducibility statement all document the
    # paths -- so the tree goes up as one archive and only flat-keyed files go
    # up individually. See scripts/DEPOSIT-W6.md.
    if a.hybrid:
        chosen = [f for f in files if f['path'] in HYBRID_INDIVIDUAL]
        names = {f['path'] for f in chosen}
        for want in HYBRID_INDIVIDUAL:
            if want not in names:
                print('  MISSING from the stage: %s' % want)
                return 1
        if not a.archive:
            print('  --hybrid needs --archive <zip>')
            return 1
        zp = os.path.expanduser(a.archive)
        if not os.path.isfile(zp):
            print('  archive not found: %s' % zp)
            return 1
        chosen.append({'path': os.path.basename(zp),
                       'bytes': os.path.getsize(zp), 'abs': zp})
        files = chosen
        print('  hybrid: %d individual object(s) + the archive'
              % len(HYBRID_INDIVIDUAL))

    have = existing_files(base, token, dep_id)
    print('  already uploaded: %d files' % len(have))

    # Skip on DIGEST, never on size: see existing_files().
    todo = []
    for f in files:
        p = f.get('abs') or os.path.join(a.stage_dir, f['path'])
        cur = have.get(f['path'])
        if cur and cur == (f['bytes'], md5_file(p)):
            continue
        todo.append(f)
    skipped = len(files) - len(todo)
    print('  skipping %d unchanged, uploading %d (%.1f MB)'
          % (skipped, len(todo), sum(f['bytes'] for f in todo) / 1048576.0))

    failed = []
    for i, f in enumerate(todo, 1):
        p = f.get('abs') or os.path.join(a.stage_dir, f['path'])
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
    # The SELECTED objects' own bytes, not the staged tree's. These differed
    # once hybrid mode arrived: the line read "files: 7, 408.2 MB", pairing a
    # count of seven deposited objects with the size of all 808 staged files,
    # which is neither what was uploaded nor what the record holds. Labelled
    # MiB because that is what the divisor produces.
    print('  files      : %d object(s), %.1f MiB'
          % (len(files), sum(f['bytes'] for f in files) / 1048576.0))
    if a.hybrid:
        print('  staged tree: %d files, %.1f MiB, inside the archive'
              % (man['fileCount'], man['totalBytes'] / 1048576.0))
    print()
    print('Publishing is irreversible and this script will not do it. Publish from')
    print('the web interface after review.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
