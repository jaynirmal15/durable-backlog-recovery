#!/usr/bin/env python3
"""Create the Zenodo deposition, reserve a DOI, and upload the package.

Requires a Zenodo personal access token with `deposit:write` and
`deposit:actions`, in ZENODO_TOKEN. No token exists on the machine this was
written on, so the deposit has NOT been created.

This script does not publish. It creates a draft, reserves the DOI, uploads
every file and prints the reserved DOI and the manifest. Publishing is
irreversible on Zenodo — a published record cannot be deleted and its files
cannot be changed — so that step is left to a human, deliberately.

  export ZENODO_TOKEN=...
  python3 scripts/zenodo_deposit.py --stage-dir ~/Jay_NIW/paper2-zenodo
  python3 scripts/zenodo_deposit.py --stage-dir ... --sandbox   # dry run first

Use --sandbox against sandbox.zenodo.org to rehearse the whole flow against a
throwaway record before touching the real one.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

LIVE = 'https://zenodo.org/api'
SANDBOX = 'https://sandbox.zenodo.org/api'


def api(base, token, method, path, payload=None, raw=None, ctype=None):
    url = '%s%s' % (base, path)
    sep = '&' if '?' in url else '?'
    url = '%s%saccess_token=%s' % (url, sep, token)
    data = raw if raw is not None else (json.dumps(payload).encode() if payload else None)
    req = urllib.request.Request(url, data=data, method=method)
    if ctype:
        req.add_header('Content-Type', ctype)
    elif payload is not None:
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        sys.stderr.write('%s %s -> %s\n%s\n' % (method, path, e.code, e.read().decode()[:600]))
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage-dir', required=True)
    ap.add_argument('--sandbox', action='store_true')
    a = ap.parse_args()

    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        print('ZENODO_TOKEN is not set. Nothing was sent.')
        print('Create one at https://zenodo.org/account/settings/applications/tokens/new/')
        print('with scopes deposit:write and deposit:actions, then re-run.')
        return 2
    base = SANDBOX if a.sandbox else LIVE
    man = json.load(open(os.path.join(a.stage_dir, 'MANIFEST.json')))

    print('creating draft on %s' % base)
    dep = api(base, token, 'POST', '/deposit/depositions', payload={})
    dep_id = dep['id']
    print('  deposition %s' % dep_id)

    meta = dict(man['metadata'])
    meta['notes'] = 'Generated from git commit %s. Every file hashed in ' \
                    'MANIFEST.json.' % man['gitCommit']
    api(base, token, 'PUT', '/deposit/depositions/%s' % dep_id,
        payload={'metadata': meta})

    doi = api(base, token, 'POST',
              '/deposit/depositions/%s/actions/newversion' % dep_id) \
        if False else dep.get('metadata', {}).get('prereserve_doi', {})
    # Zenodo reserves the DOI when metadata is first saved; read it back.
    dep = api(base, token, 'GET', '/deposit/depositions/%s' % dep_id)
    doi = (dep.get('metadata', {}).get('prereserve_doi') or {}).get('doi') or dep.get('doi')
    print('  reserved DOI: %s' % doi)

    bucket = dep['links']['bucket']
    total = len(man['files'])
    for i, f in enumerate(man['files'], 1):
        p = os.path.join(a.stage_dir, f['path'])
        with open(p, 'rb') as fh:
            req = urllib.request.Request(
                '%s/%s?access_token=%s' % (bucket, f['path'], token),
                data=fh, method='PUT')
            req.add_header('Content-Type', 'application/octet-stream')
            req.add_header('Content-Length', str(f['bytes']))
            urllib.request.urlopen(req).read()
        if i % 25 == 0 or i == total:
            print('  uploaded %d/%d' % (i, total))

    print()
    print('DRAFT READY, NOT PUBLISHED')
    print('  DOI (reserved): %s' % doi)
    print('  review at: %s/deposit/%s'
          % ('https://sandbox.zenodo.org' if a.sandbox else 'https://zenodo.org', dep_id))
    print('  %d files, %.1f MB' % (total, man['totalBytes'] / 1048576.0))
    print()
    print('Publishing is irreversible. To publish, from the web interface or:')
    print('  curl -X POST "%s/deposit/depositions/%s/actions/publish?access_token=$ZENODO_TOKEN"'
          % (base, dep_id))
    return 0


if __name__ == '__main__':
    sys.exit(main())
