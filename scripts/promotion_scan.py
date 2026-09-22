#!/usr/bin/env python3
"""The promotion scan: withdrawn and superseded claims in the ASSEMBLED PDFs.

WHY THIS EXISTS, AND WHY IT IS NOT check_manuscript.py. That checker reads the
markdown sources and deliberately excludes results/, because registrations are
immutable and a correction notice quoting the wording it corrects is doing its
job. The boundary that matters is PROMOTION: nothing quoted out of the record
into reader-facing text may carry an unqualified withdrawn claim. Only the
assembled PDF shows what actually reached a reader, and it is the only artefact
that contains all three of the places a claim can hide:

  prose          which the source checker already covers
  captions and   which it covers in the markdown, but not as typeset, and not
  table cells    after a generator rewrites a table
  FIGURE LABELS  which it cannot see at all, because they are drawn inside a
                 PDF by matplotlib and exist nowhere in the markdown

That last one is not hypothetical. Fig. S1 drew the overhead as "ov" five
times for weeks after the caption had been corrected to delta, and the
caption's own note asserted it was "the only place in the paper" still using
the old symbol. Nothing that reads markdown could have caught it.

IT REPORTS; IT DOES NOT JUDGE. Every occurrence here is expected to be
legitimate most of the time: SS-IX's job is to state what was withdrawn, and
Table 8's job is to record what superseded what, so both must name the very
strings this scan looks for. Deciding whether a given occurrence is qualified
needs the sentence around it, so the scan prints the sentence around it and
stops there. A scan that tried to classify would be wrong quietly; a scan that
prints six hits is read in a minute.

THE LIST COMES FROM THE RECORD, NOT FROM MEMORY. Withdrawn phrases are
imported from check_manuscript.py, which is where they are maintained.
Superseded values each carry the file and phrase in the record that supersedes
them, and EVERY ANCHOR IS VERIFIED AT STARTUP: if the record stops saying what
an entry claims it says, the scan fails instead of going on scanning for
something nobody asserts any more.

  python3 scripts/promotion_scan.py                 both documents
  python3 scripts/promotion_scan.py --self-test     plant a hit, prove it is caught
Exit 0 if the scan ran, 2 if an anchor no longer holds, 1 on a bad invocation.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_manuscript import WITHDRAWN  # noqa: E402  -- the maintained list

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = [('article', os.path.join(ROOT, 'build', 'access', 'article.pdf')),
        ('supplement S1', os.path.join(ROOT, 'build', 'access',
                                       'supplement-S1.pdf'))]

# (pattern, what it is, the file that supersedes it, the phrase that does so).
# The anchor is not decoration: it is checked before the scan runs.
SUPERSEDED = [
    ('0.0068',
     'superseded F5 spread: the published 0.0719/0.0068 mixed a MAX left axis '
     'with a MEDIAN right one. Current pair: 0.0719/0.0071',
     'paper/OUTLINE.md', 'superseded pairs must never be reinstated'),
    ('0.0716',
     'superseded F5 left-axis spread from the 3c00a6e rebuild (0.0716/0.0068). '
     'NOTE: 0.0716 is ALSO the corrected A6 numerator, where it is current -- '
     'the surrounding text decides which is which',
     'paper/OUTLINE.md', '(0.0716/0.0068)'),
    ('0.0706',
     'superseded A6 numerator, recomputed SAFE-side to 0.0716; separately, a '
     'seven-cell range once mislabelled as a two-arm gap, which is 0.0689',
     'results/METHOD-AUDIT.md', '0.0706 → 0.0716'),
    ('10.3',
     'superseded collapse factor: A6 first reported 10.3x, corrected to 10.5x '
     'under matched estimators by A10',
     'results/METHOD-AUDIT.md', '10.3× → **10.5×**'),
    ('21.4',
     'pre-A6 collapse factor, halved to 10.5x when A6 invalidated A4 at '
     'collapsed points',
     'figures/T4-false-findings.md', '21.4x to 10.5x'),
    ('quadrature',
     'withdrawn error-combination construction: the terms are reported '
     'separately and never combined in quadrature',
     'paper/OUTLINE.md', 'never combine them in quadrature'),
    ('0.0004',
     'withdrawn confirmation claim: a break within 0.0004 of a registered '
     'prediction was said to confirm it, when the bracket contained both '
     'candidates',
     'paper/OUTLINE.md', 'within 0.0004'),
]


def check_anchors():
    """Every superseded entry must still be superseded BY something."""
    bad = []
    for pattern, _why, path, anchor in SUPERSEDED:
        full = os.path.join(ROOT, path)
        if not os.path.isfile(full):
            bad.append((pattern, '%s is missing' % path))
            continue
        with open(full, encoding='utf-8') as fh:
            if anchor not in fh.read():
                bad.append((pattern, '%s no longer contains %r' % (path, anchor)))
    return bad


def pages_of(path):
    try:
        import fitz
    except ImportError:
        print('PyMuPDF (fitz) is required: python3 -m pip install pymupdf')
        raise SystemExit(1)
    doc = fitz.open(path)
    return [page.get_text() for page in doc]


def sentence_around(text, start, end):
    """The sentence the hit sits in, so a reader can judge it in one glance."""
    flat = re.sub(r'\s+', ' ', text)
    # map into the flattened text by re-finding the hit's immediate neighbours
    left = re.sub(r'\s+', ' ', text[:start]).rstrip()
    frag = re.sub(r'\s+', ' ', text[start:end])
    i = len(left) + (1 if left and not left.endswith(' ') else 0)
    lo = max(0, max(flat.rfind('. ', 0, i), flat.rfind('] ', 0, i)) + 1)
    hi = flat.find('. ', i + len(frag))
    hi = len(flat) if hi < 0 else hi + 1
    if hi - lo > 420:                      # a table row has no full stops
        lo, hi = max(0, i - 150), min(len(flat), i + len(frag) + 150)
    return flat[lo:hi].strip()


def scan(docs, targets):
    hits = []
    for label, path in docs:
        if not os.path.isfile(path):
            hits.append((label, None, None, 'PDF not built: %s'
                         % os.path.relpath(path, ROOT), ''))
            continue
        for number, text in enumerate(pages_of(path), 1):
            low = text.lower()
            for pattern, why in targets:
                for m in re.finditer(re.escape(pattern.lower()), low):
                    hits.append((label, number, pattern, why,
                                 sentence_around(text, m.start(), m.end())))
    return hits


def report(hits):
    if not hits:
        print('no withdrawn or superseded string occurs in either document.')
        return
    print('%d occurrence(s). EVERY ONE NEEDS A HUMAN: the sections that record '
          'a withdrawal\nmust name the thing withdrawn, so a legitimate hit '
          'looks exactly like a defect\nuntil you read the sentence.\n' % len(hits))
    last = None
    for label, page, pattern, why, context in hits:
        if label != last:
            print('--- %s ---' % label)
            last = label
        if page is None:
            print('  %s' % why)
            continue
        print('  p.%-3d %s' % (page, pattern))
        print('        %s' % why)
        print('        "%s"' % context)
        print()


def self_test():
    """Plant an unqualified occurrence in a copy of the PDF and catch it.

    A scan is worth what its failure mode is worth. This builds a one-page PDF
    carrying a bare superseded number with no withdrawal language anywhere
    near it -- the exact thing the scan exists to catch -- and asserts it is
    reported, then asserts a clean page is not.
    """
    try:
        import fitz
    except ImportError:
        print('PyMuPDF (fitz) is required for --self-test')
        return 1
    import tempfile
    ok = True
    cases = [('The collapse factor is 21.4x across the seven cells.',
              '21.4', True),
             ('The corrected spread is 0.0071 against 0.0719.', '21.4', False)]
    tmp = tempfile.mkdtemp(prefix='promotion-')
    for body, pattern, expected in cases:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 144), body, fontsize=11)
        path = os.path.join(tmp, 'planted.pdf')
        doc.save(path)
        doc.close()
        found = scan([('planted', path)],
                     [(p, w) for p, w, _f, _a in SUPERSEDED])
        got = any(h[2] == pattern for h in found)
        status = 'PASS' if got == expected else 'FAIL'
        ok = ok and got == expected
        print('  %-5s %-48s %s %r'
              % (status, body[:46],
                 'caught' if got else 'not caught', pattern))
        if got and expected:
            print('        context reported: "%s"'
                  % next(h[4] for h in found if h[2] == pattern))
    print('self-test %s' % ('passed' if ok else 'FAILED'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true',
                    help='plant an unqualified occurrence and prove it is caught')
    args = ap.parse_args()

    bad = check_anchors()
    if bad:
        print('THE RECORD NO LONGER SUPPORTS THIS LIST\n')
        for pattern, msg in bad:
            print('  %-12s %s' % (pattern, msg))
        print('\nEvery superseded entry names the file and phrase that '
              'supersedes it.\nFix the entry or the record; do not scan for '
              'something nobody asserts.')
        return 2

    if args.self_test:
        return self_test()

    targets = [(p, 'withdrawn phrase -- %s' % w) for p, w in WITHDRAWN]
    targets += [(p, w) for p, w, _f, _a in SUPERSEDED]
    print('promotion scan: %d withdrawn phrase(s) + %d superseded value(s), '
          'all anchored in the record\n'
          % (len(WITHDRAWN), len(SUPERSEDED)))
    report(scan(DOCS, targets))
    return 0


if __name__ == '__main__':
    sys.exit(main())
