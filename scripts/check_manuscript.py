#!/usr/bin/env python3
"""Three invariants over the manuscript's live text. Renamed from
check_withdrawn_phrases.py, which understated what it does.

WHY THIS EXISTS. Five times in this project a phrase was withdrawn from the
place a reviewer was looking at and left standing somewhere else: the F6 caption
through five layers; the Set A narrative; "the conventional construction" banned
in a version header while two planning lines still taught it; "the probe was
sound" surviving in the plan that withdrew it; and that same phrase in frozen
section7.md after only the outline had been swept. A remembered rule failed five
times, so this is the rule as a check.

FOUR BUGS FOUND IN CODE REVIEW, all of which this version fixes. They are worth
recording because three of them are the same defect the checks exist to catch,
committed inside the checks themselves:

  1. PHRASE MATCHING DID NOT CROSS LINE BREAKS. The old version built a
     three-line window to evaluate EXEMPTIONS but matched the phrase itself with
     `phrase in line`. These files hard-wrap at ~78 columns, so
         "latency is the conventional\\nconstruction in overload"
     produced zero hits. The checker accounted for wrapping when excusing a
     phrase and not when finding one. Now: match against a whitespace-normalised
     multi-line window, and report the line the match starts on.

  2. EXEMPTIONS WERE LEXICAL GUESSES. Patterns like "said", "read", "never",
     "corrected" meant a live assertion sitting one line from any of those words
     became exempt. Replaced by an explicit marker, WITHDRAWN_OK below. Explicit
     exemptions are auditable; contextual guesses are not.

  3. plan_sync() ONLY ITERATED OVER MARKERS THAT EXIST. Deleting a marker
     escaped silently while the script still printed "all 10 section plans
     marked current". Absence of the claim was not a signal. Now: every section
     1-10 must have exactly one marker, it must sit under that section's own
     plan heading, and it must equal the section's current draft -- a marker of
     draft 99 fails too.

  4. THE CITATION INVENTORY READ SS-2's VERSION HISTORY. The outline side was
     scoped below its version header, but the SS-2 side searched the whole
     header block, which contains both the live inventory and the change log
     naming the same work. Deleting Papadopoulos from the live inventory still
     passed. Now both inventories are delimited explicitly. Exact scopes beat
     inferred scopes for a check whose whole purpose is stopping stale text from
     passing as live text.

STILL OPEN, deliberately: no scan of the assembled manuscript. `results/` is
excluded on principle -- registrations are immutable and reports are the
historical record, so a correction notice quoting the wording it corrects is
doing its job. The boundary that matters is PROMOTION: nothing quoted out of a
report into manuscript-facing text may carry an unqualified withdrawn claim. A
W6 pass over the assembled submission text is the right place for that, and does
not exist yet.

Usage: python3 scripts/check_manuscript.py
Exit 0 if clean, 1 on any violation.
"""
import hashlib
import os
import re
import sys

PAPER = 'paper'
FIGURES = 'figures'
SCRIPTS = 'scripts'

WITHDRAWN_OK = 'withdrawn-quote-ok'
INV_START = 'citation-inventory:start'
INV_END = 'citation-inventory:end'

# phrase, why it was withdrawn and what replaces it.
WITHDRAWN = [
    ('the conventional construction',
     'No cited work establishes an industry default: DAGOR and Breakwater key on '
     'queueing delay, Bouncer on response-time percentiles. Use "an established '
     'construction", and live latency as a literature-grounded comparator.'),
    ('the default answer',
     'Same reason as "the conventional construction".'),
    ('which was sound',
     "Frozen SS-IX-B concedes the probe's effective clock resolution was never "
     'measured and its repeatability was not measured at the two conditions '
     'compared. Say the probe exposed rather than generated the bias.'),
    ('which is impossible',
     'SS-VI states C_measured is a normalisation reference, not a physical '
     'ceiling, and two cells read 1.0002. Say: a pattern incompatible with '
     'treating the estimator as physically interpretable at collapsed points.'),
    ('apparent finding',
     'Table 3 column 1 is "Candidate explanation": the admission limit was '
     'explicitly not a finding.'),
]


def targets():
    out = []
    for name in sorted(os.listdir(PAPER)):
        if name.endswith('.md'):
            out.append((os.path.join(PAPER, name), True))
    for d in (FIGURES, SCRIPTS):
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if d == FIGURES and name.endswith('.md'):
                out.append((os.path.join(d, name), False))
            elif d == SCRIPTS and name.startswith('make_') and name.endswith('.py'):
                out.append((os.path.join(d, name), False))
    return out


def body_of(lines, skip_header):
    """Drop the leading header block: it is a change log, not manuscript text."""
    if not skip_header:
        return list(enumerate(lines, 1))
    for i, line in enumerate(lines):
        if line.strip() == '---':
            return list(enumerate(lines[i + 1:], i + 2))
    return list(enumerate(lines, 1))


def phrase_hits(path, skip_header):
    """Withdrawn phrases in live text, matched ACROSS line breaks (bug 1).

    Matching is per PARAGRAPH, not over the whole file. Joining across a blank
    line let two unrelated sentences collide into a forbidden phrase -- the tail
    of one paragraph plus the head of the next. A hard-wrapped phrase never
    spans a paragraph break, so nothing real is lost. (Found by control, 2026-09-20.)

    The exemption window covers the WHOLE match, start line to end line, plus
    one either side. Keying it to the start line alone meant a marker placed
    after a wrapped quote was not seen. (Same date, same method.)
    """
    hits = []
    with open(path, encoding='utf-8') as fh:
        lines = fh.readlines()
    numbered = body_of(lines, skip_header)
    if not numbered:
        return hits

    paragraphs, current = [], []
    for n, line in numbered:
        if line.strip():
            current.append((n, line))
        elif current:
            paragraphs.append(current)
            current = []
    if current:
        paragraphs.append(current)

    for para in paragraphs:
        buf, origin = [], []
        for n, line in para:
            for ch in line.rstrip('\n'):
                buf.append(ch)
                origin.append(n)
            buf.append(' ')
            origin.append(n)
        raw = ''.join(buf)
        flat = re.sub(r'\s+', ' ', raw).lower()
        mapped, prev_ws = [], False
        for ch, n in zip(raw, origin):
            if ch.isspace():
                if not prev_ws:
                    mapped.append(n)
                prev_ws = True
            else:
                mapped.append(n)
                prev_ws = False
        for phrase, why in WITHDRAWN:
            start = 0
            while True:
                i = flat.find(phrase, start)
                if i < 0:
                    break
                start = i + 1
                j = min(i + len(phrase) - 1, len(mapped) - 1)
                first = mapped[i] if i < len(mapped) else 0
                last = mapped[j] if j >= 0 else first
                window = ' '.join(l for n, l in numbered
                                  if first - 1 <= n <= last + 1)
                if WITHDRAWN_OK in window:
                    continue
                hits.append((path, first, phrase, why))
    return hits


def delimited(text, start_tag, end_tag):
    """The block between the tags, where each tag is ALONE ON ITS LINE.

    text.find() matched the tag named in prose. OUTLINE.md's version header
    describes the convention as `citation-inventory:start/end`, which contains
    the start tag, so the block began at line 22 and ran 752 lines instead of
    66 -- every mention anywhere above the real inventory counted as being in
    it, which is bug 4 reintroduced by the sentence announcing the fix for it.
    Requiring an own-line HTML comment excludes prose. (Control, 2026-09-20.)
    """
    def own_line(tag):
        return re.search(r'^[ \t]*<!--[ \t]*' + re.escape(tag) + r'[ \t]*-->[ \t]*$',
                         text, re.M)
    a, b = own_line(start_tag), own_line(end_tag)
    if not a or not b or b.start() < a.end():
        return None
    return text[a.end():b.start()].lower()


def plan_sync():
    """Every section 1-10 needs exactly one marker, placed right, and equal (bug 3)."""
    problems = []
    outline = os.path.join(PAPER, 'OUTLINE.md')
    if not os.path.isfile(outline):
        return [('OUTLINE.md', 'missing')]
    with open(outline, encoding='utf-8') as fh:
        text = fh.read()

    # Split the outline into its per-section plans, so placement is checkable.
    plans = {}
    heads = list(re.finditer(r'^## §(\d{1,2}) [^\n]*$', text, re.M))
    for k, m in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(text)
        plans.setdefault(int(m.group(1)), text[m.start():end])

    for sec in range(1, 11):
        path = os.path.join(PAPER, 'section%d.md' % sec)
        if not os.path.isfile(path):
            problems.append(('§%d' % sec, 'section file missing'))
            continue
        with open(path, encoding='utf-8') as fh:
            head = fh.read(4000)
        d = re.search(r'\*+\s*Draft\s+(\d+)', head, re.I)
        if not d:
            problems.append(('§%d' % sec, 'no Draft number in its header'))
            continue
        current = int(d.group(1))

        if sec not in plans:
            problems.append(('§%d' % sec, 'no plan heading in OUTLINE.md'))
            continue
        found = re.findall(
            r'<!--\s*plan-synced-to:\s*section(\d{1,2})\s+draft\s+(\d+)\s*-->',
            plans[sec])
        owned = [(int(a), int(b)) for a, b in found if int(a) == sec]
        if len(owned) != 1:
            problems.append(('§%d' % sec,
                             'expected exactly 1 marker under its own plan '
                             'heading, found %d' % len(owned)))
            continue
        marked = owned[0][1]
        if marked != current:
            problems.append(('§%d' % sec,
                             'marker says draft %d, section is at draft %d'
                             % (marked, current)))
    return problems


def bibliography():
    """Parse references.md for entries AND their cite keys (bug 5: one source)."""
    path = os.path.join(PAPER, 'references.md')
    if not os.path.isfile(path):
        return [], [('references.md', 'missing')]
    with open(path, encoding='utf-8') as fh:
        text = fh.read()
    entries, problems = [], []
    for m in re.finditer(r'^\*\*\[(\d+)\]\*\*', text, re.M):
        num = int(m.group(1))
        end = text.find('\n\n**[', m.start() + 1)
        block = text[m.start():end if end > 0 else len(text)]
        k = re.search(r'<!--\s*cite-key:\s*([^>]+?)\s*-->', block)
        if not k:
            problems.append(('[%d]' % num,
                             'no <!-- cite-key: ... --> in references.md; the '
                             'checker cannot know how this work is named'))
            continue
        spec = k.group(1)
        scope = 'both'
        if '|scope=' in spec:
            spec, scope = spec.split('|scope=', 1)
            scope = scope.strip()
        tokens = [t.strip().lower() for t in spec.split('|') if t.strip()]
        entries.append((num, tokens, scope))
    return entries, problems


def citation_inventory(entries):
    """Both inventories are DELIMITED explicitly (bug 4)."""
    missing = []
    outline = os.path.join(PAPER, 'OUTLINE.md')
    sec2 = os.path.join(PAPER, 'section2.md')
    for p in (outline, sec2):
        if not os.path.isfile(p):
            return [('-', 'missing %s' % p)]

    with open(outline, encoding='utf-8') as fh:
        obody = delimited(fh.read(), INV_START, INV_END)
    with open(sec2, encoding='utf-8') as fh:
        sbody = delimited(fh.read(), INV_START, INV_END)
    if obody is None:
        return [('-', 'OUTLINE.md has no %s / %s block' % (INV_START, INV_END))]
    if sbody is None:
        return [('-', 'section2.md has no %s / %s block' % (INV_START, INV_END))]

    for num, tokens, scope in entries:
        checks = [('OUTLINE.md inventory', obody)]
        if scope == 'both':
            checks.append(('section2.md inventory', sbody))
        for where, hay in checks:
            if not any(t in hay for t in tokens):
                missing.append(('[%d]' % num, where))
    return missing


def main():
    hits = []
    for path, skip in targets():
        if os.path.basename(path) == os.path.basename(__file__):
            continue
        try:
            hits.extend(phrase_hits(path, skip))
        except (UnicodeDecodeError, OSError):
            continue

    stale = plan_sync()
    entries, bib_problems = bibliography()
    uncited = citation_inventory(entries) if entries else []

    ok = not (hits or stale or bib_problems or uncited)
    if ok:
        print('clean.')
        print('  withdrawn phrases : none in live manuscript-facing text '
              '(%d files, matched across line breaks)' % len(targets()))
        print('  plan freshness    : 10/10 sections have exactly one marker, '
              'correctly placed, equal to the section draft')
        print('  citations         : %d bibliography entries, all present in '
              'their delimited inventories' % len(entries))
        return 0

    if hits:
        print('WITHDRAWN PHRASES IN LIVE TEXT\n')
        for path, n, phrase, why in hits:
            print('%s:%d\n  phrase : %s\n  why    : %s\n' % (path, n, phrase, why))
        print('To quote one legitimately, put <!-- %s --> on or beside the '
              'line.\n' % WITHDRAWN_OK)
    if stale:
        print('PLAN FRESHNESS\n')
        for label, msg in stale:
            print('  %-6s %s' % (label, msg))
        print('\nRe-read the plan against its section, fix what is stale, then '
              'set the marker to the section\'s current draft.\n')
    if bib_problems:
        print('BIBLIOGRAPHY PARSE\n')
        for label, msg in bib_problems:
            print('  %-6s %s' % (label, msg))
        print()
    if uncited:
        print('BIBLIOGRAPHY ENTRIES MISSING FROM AN INVENTORY\n')
        for label, where in uncited:
            print('  %-6s absent from %s' % (label, where))
        print('\nA reference nothing instructs a drafter to cite will not be '
              'cited.\n')
    return 1


if __name__ == '__main__':
    sys.exit(main())
