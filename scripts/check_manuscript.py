#!/usr/bin/env python3
"""Six invariants over the manuscript's live text. Renamed from
check_withdrawn_phrases.py, which understated what it does.

Check 6 was added 2026-09-23 after a review found "Table 8" still standing in
SS-VI-C, a number no float has had since the cut pass moved the audit trail
into the supplement. Check 5 validated keyed references and was silent about
literals, so the one reference that could go stale was the one nothing looked
at.

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
# The marker only counts inside a real HTML comment. A bare substring search
# meant PROSE THAT NAMES THE MARKER granted the exemption: OUTLINE.md's own
# changelog says "four `withdrawn-quote-ok` markers at the legitimate sites",
# and any withdrawn phrase landing within one line of that sentence became
# exempt. Same defect as delimited() matching its tag named in prose -- a
# mechanism defeated by the text describing it. (Control, 2026-09-20.)
WITHDRAWN_OK_RE = re.compile(r'<!--[^>]*' + re.escape(WITHDRAWN_OK) + r'[^>]*-->')
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
    # RESTORED after review. The rewrite dropped these two silently while
    # fixing four other bugs -- a coverage regression introduced by a repair,
    # with no note, which is the same failure class this list exists for. Both
    # prohibitions are live: METHOD-AUDIT item 33 for the first, the claim
    # register for the second.
    ('true capacity',
     'The configured parameter is NEVER called true capacity. The four rigid '
     'terms are C_config, C_staffed, C_model, C_measured. The harness field '
     'trueCapacity is an identifier and is exempt; SS-III quoting the '
     'specification as a primary source is exempt by marker.'),
    # B1, 2026-09-23. Both adversarial reviews found this independently. SS-VI-B
    # states the policy -- "no range spanning the seven is quoted: they do not
    # share a precision, and a range would assert one they do not have" -- and
    # four places asserted exactly such a range anyway. Retiring the four
    # manifestations alone would let regeneration restore them, so the phrases
    # are retired here and the claim register's headline was rewritten.
    ('within 1%',
     'Retired as a seven-cell formulation: it asserts a precision the seven '
     'cells do not share, which SS-VI-B expressly refuses. Say "at or near '
     'measured capacity, indistinguishable from it at each cell\'s '
     'experimental resolution".'),
    ('within 0.7%',
     'Same: a shared percentage range across cells of different resolution. '
     'The Fig. 2 caption now reports the 0.0071 spread against E2b\'s 0.0127 '
     'resolution instead.'),
    ('statistically',
     'Struck from the claim register: the indistinguishability argument rests '
     'on resolution -- bisection step, interval width, replicate spread -- not '
     'on an equivalence test. It invites "which test, which null, which '
     'margin", a fight SS-IV does not equip the paper for.'),
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


class ScopeError(Exception):
    """A slice whose end bound could not be found. Never a fallback."""


def body_of(lines, skip_header, name='(unnamed)'):
    """Drop the leading header block: it is a change log, not manuscript text.

    A MISSING END BOUND RAISES when a header was expected. Falling back to the
    whole file meant a paper/ file without its `---` would have had its entire
    drafting header scanned as live manuscript text -- and, in the build's
    copy of this function, typeset. Files that legitimately have no header
    still pass skip_header=False and are returned whole, which is a stated
    choice rather than a fallback.
    """
    if not skip_header:
        return list(enumerate(lines, 1))
    for i, line in enumerate(lines):
        if line.strip() == '---':
            return list(enumerate(lines[i + 1:], i + 2))
    raise ScopeError('%s has no own-line `---`, so where its header ends is '
                     'unknown' % name)


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
    numbered = body_of(lines, skip_header, path)
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
                if WITHDRAWN_OK_RE.search(window):
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
    #
    # A PLAN ENDS AT THE NEXT "## " OF ANY KIND, not at the next plan heading.
    # Ending the last plan at len(text) gave §10 a 9,566-character slice that
    # ran to end of file and swallowed two unrelated "## " sections. It passed
    # only because exactly one plan-synced-to marker happened to fall inside
    # it; a stray marker anywhere below the last plan would have been credited
    # to §10 silently. Bounded, that slice is 1,489 characters.
    plans = {}
    heads = list(re.finditer(r'^## §(\d{1,2}) [^\n]*$', text, re.M))
    allheads = [m.start() for m in re.finditer(r'^## ', text, re.M)]
    for k, m in enumerate(heads):
        after = [s for s in allheads if s > m.start()]
        if not after:
            raise ScopeError(
                'OUTLINE.md: the plan for §%s is the last "## " heading in the '
                'file, so where it ends is unknown. A plan that runs to end of '
                'file adopts every marker below it.' % m.group(1))
        plans.setdefault(int(m.group(1)), text[m.start():after[0]])

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


def reference_blocks():
    """references.md's entries, each bounded at its own end. ONE parser.

    There were two, and that was the second defect behind the first. Both read
    this file, both sliced from `**[n]**` to the next entry, and they used
    DIFFERENT separators to do it -- `\n\n**[` in one and `\n**[` in the other --
    so the same file had two notions of where an entry began. Both then fell
    back to len(text) for the LAST entry, which swallowed every drafting note
    below the bibliography: 4,719 characters against a 1,020-character
    maximum for the others.

    An entry ends at the next entry or at the first own-line `---` or `## `
    after it, whichever comes first. THE LAST ENTRY MUST HAVE ONE: if nothing
    closes it, that is a missing end bound and this raises rather than reading
    to end of file.
    """
    path = os.path.join(PAPER, 'references.md')
    if not os.path.isfile(path):
        return None, [('references.md', 'missing')]
    with open(path, encoding='utf-8') as fh:
        text = fh.read()
    starts = list(re.finditer(r'^\*\*\[(\d+)\]\*\*', text, re.M))
    stops = [m.start() for m in re.finditer(r'^(?:---|## )', text, re.M)]
    out = []
    for j, m in enumerate(starts):
        after = [s for s in stops if s > m.start()]
        if j + 1 < len(starts):
            end = min(starts[j + 1].start(), after[0] if after else len(text))
        elif after:
            end = after[0]
        else:
            raise ScopeError(
                'references.md entry [%s] is the last one and nothing closes '
                'it -- no own-line `---` or `## ` follows. Where it ends is '
                'unknown, and reading to end of file is how 726 words of '
                'drafting notes were typeset inside reference [14].'
                % m.group(1))
        out.append((int(m.group(1)), text[m.start():end]))
    return out, []


def bibliography():
    """Cite keys, from the one shared parser."""
    blocks, problems = reference_blocks()
    if blocks is None:
        return [], problems
    entries = []
    for num, block in blocks:
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


def citation_markers():
    """Every [@key] resolves to exactly one entry; every entry is cited once.

    Added 2026-09-20 with the citation pass. The bibliography is the single
    source of truth: each entry carries a marker-key comment, and the sections
    carry [@key]. A key with no entry is a citation to nothing; a key matching
    two entries is an ambiguous number; an entry nobody cites is a reference the
    manuscript does not use, which IEEE numbering by first appearance cannot
    assign a number to at all.

    Keys are read from an HTML comment, never as a bare substring -- item 37.
    """
    problems = []
    blocks, probs = reference_blocks()
    if blocks is None:
        return probs, {}, {}
    problems += probs
    entries = {}
    for num, block in blocks:
        k = re.search(r'<!--\s*marker-key:\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*-->', block)
        if not k:
            problems.append(('[%d]' % num, 'no <!-- marker-key: ... --> comment'))
            continue
        entries.setdefault(k.group(1), []).append(num)

    cited = {}
    for sec in range(1, 11):
        sp = os.path.join(PAPER, 'section%d.md' % sec)
        if not os.path.isfile(sp):
            continue
        with open(sp, encoding='utf-8') as fh:
            lines = fh.readlines()
        for n, line in body_of(lines, True, sp):
            for m in re.finditer(r'\[@([A-Za-z0-9][A-Za-z0-9._-]*)\]', line):
                cited.setdefault(m.group(1), []).append((sp, n))

    for key, where in sorted(cited.items()):
        hits = entries.get(key, [])
        if not hits:
            problems.append(('[@%s]' % key,
                             'cited at %s:%d but no entry carries that marker-key'
                             % (where[0][0], where[0][1])))
        elif len(hits) > 1:
            problems.append(('[@%s]' % key,
                             'ambiguous: entries %s both carry it'
                             % ', '.join('[%d]' % h for h in hits)))
    for key, nums in sorted(entries.items()):
        if key not in cited:
            problems.append(('[%d]' % nums[0],
                             'marker-key %r is never cited by any section' % key))
    return problems, entries, cited


FLOAT_FIGURES = 5
FLOAT_TABLES = 7
S1_FILE = 'supplement-S1.md'
# The census is a RULING, not a measurement. ASSEMBLY-SPEC.md Draft 2 ruling A
# fixed it at six figures and eight tables; CUT-PLAN.md Draft 4 moved Fig. 2
# and the amendment table to Supplement S1, leaving the ARTICLE at five and
# seven. S1's own counts are reported rather than asserted, because no ruling
# has fixed them. Hard-coding it means
# losing a float fails here instead of silently shortening the article. Adding
# one is a deliberate edit to this line, which is the point.


def own_line_tags(text, pattern):
    """Every own-line HTML-comment marker matching `pattern`, with its line.

    Own-line only, for the reason delimited() is: a marker named in prose is
    prose. OUTLINE.md and the spec both describe these markers in sentences
    (item 37), and a bare substring search would count those descriptions as
    the markers they describe.
    """
    out = []
    for m in re.finditer(r'^[ \t]*<!--[ \t]*(' + pattern + r')[ \t]*-->[ \t]*$',
                         text, re.M):
        # group(1) is the whole marker; group(2) is the key. Every pattern
        # passed here supplies that inner group. re.lastindex is NOT usable to
        # detect it -- with the outer group wrapping the pattern it reports 1
        # even when groups 2 and 3 matched, which silently made every key None.
        out.append((m.group(2), m.start(),
                    text.count('\n', 0, m.start()) + 1, m))
    return out


XREF_OK = 'xref-ok'
XREF_OK_RE = re.compile(r'<!--[^>]*' + re.escape(XREF_OK) + r'[^>]*-->')
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

# A literal float number, anywhere in live text. "Table~8" is included because
# the build emits that form and a source could too.
LITERAL_FLOAT = re.compile(
    r'(?<![\w:])(Tables?|Figs?\.|Figures?)[ ~]+(S?\d+)')
SECTION_REF = re.compile(r'§[ ~]*([IVX]+)(?:-([A-Z]))?')


def section_inventory(root='.'):
    """The article's sections and subsections, read from the sources.

    Both documents' section references point at ARTICLE sections: the
    supplement's own divisions are S1-A, S1-B and so on, and it refers to the
    article by number throughout. So one inventory serves both.
    """
    inv = {}
    for n in range(1, 11):
        path = os.path.join(root, PAPER, 'section%d.md' % n)
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as fh:
            lines = fh.readlines()
        letters = set()
        for _, line in body_of(lines, True, path):
            m = re.match(r'###\s+([A-Z])\.\s', line)
            if m:
                letters.add(m.group(1))
        inv[ROMAN[n - 1]] = letters
    return inv


def shipped_only(numbered):
    """In figures/*.md, only delimited captions and pipe tables are typeset.

    The rest of the file is apparatus -- and the apparatus legitimately says
    "Fig. 2" and "Table 1" while explaining why the body may not. Scanning it
    would have made the check unusable and taught the project to exempt its
    way out of a real rule, which is how a check stops meaning anything.
    """
    out, inside = [], False
    for n, line in numbered:
        s = line.strip()
        if re.match(r'<!--\s*caption:[^>]*:start\s*-->', s):
            inside = True
            continue
        if re.match(r'<!--\s*caption:[^>]*:end\s*-->', s):
            inside = False
            continue
        if inside or s.startswith('|'):
            out.append((n, line))
    return out


def cross_references(root='.'):
    """Check 6: every cross-reference resolves, in the document that makes it.

    WHY THIS EXISTS. The cut pass moved the audit trail into Supplement S1 and
    renumbered everything after it, and SS-VI-C went on saying "Table 8" -- a
    number no float in the article has had since. Nothing caught it: check 5
    validates KEYED references and says nothing about literals, so a literal
    was invisible in exactly the way an unkeyed reference goes stale. Three
    more had gone stale the same way in Supplement S1's headings, pointing at
    an article Fig. 2, an article Table 2, a SS-V-G and a SS-VII-D that the cut
    had moved, renumbered or removed.

    Two rules, and the second is the one the cut broke:

      FLOAT REFERENCES MUST BE KEYED. A literal "Table 8" or "Fig. 2" in live
      text is an error wherever it appears, because a literal cannot be
      checked against the float that would carry that number and cannot
      survive renumbering. This also enforces the scope rule -- a literal is
      the only way one document could name the other's float, since check 5
      already rejects a keyed cross-document reference.

      SECTION REFERENCES MUST RESOLVE. Every SS-X and SS-X-Y, in either
      document, must name a section and subsection the article actually has.

    Historical text quotes a retired number legitimately; mark it with
    <!-- xref-ok: why --> on or beside the line, the same explicit-marker
    mechanism the withdrawn list uses, and for the same reason: a contextual
    guess at what counts as historical is not auditable.
    """
    problems = []
    inv = section_inventory(root)
    if not inv:
        return [('inventory', 'no article sections found; nothing was checked')]
    paper = os.path.join(root, PAPER)
    figures = os.path.join(root, FIGURES)
    sources = [(os.path.join(paper, 'section%d.md' % n), True)
               for n in range(1, 11)]
    sources.append((os.path.join(paper, S1_FILE), True))
    sources.append((os.path.join(paper, 'frontmatter.md'), True))
    if os.path.isdir(figures):
        sources += [(os.path.join(figures, n), False)
                    for n in sorted(os.listdir(figures)) if n.endswith('.md')]
    for path, skip in sources:
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as fh:
            lines = fh.readlines()
        numbered = body_of(lines, skip, path)
        if not skip:
            numbered = shipped_only(numbered)
        for n, line in numbered:
            window = ' '.join(l for m, l in numbered if n - 1 <= m <= n + 1)
            exempt = XREF_OK_RE.search(window)
            for m in LITERAL_FLOAT.finditer(line):
                if exempt:
                    continue
                problems.append(('%s:%d' % (path, n),
                                 'literal float reference %r -- float '
                                 'references must be keyed, as [@tab:key] or '
                                 '[@fig:key], so they cannot go stale when '
                                 'floats are renumbered' % m.group(0)))
            for m in SECTION_REF.finditer(line):
                sec, sub = m.group(1), m.group(2)
                if sec not in inv:
                    if exempt:
                        continue
                    problems.append(('%s:%d' % (path, n),
                                     'section reference %r -- the article has '
                                     'no section %s' % (m.group(0), sec)))
                elif sub and sub not in inv[sec]:
                    if exempt:
                        continue
                    have = ''.join(sorted(inv[sec])) or 'none'
                    problems.append(('%s:%d' % (path, n),
                                     'section reference %r -- article section '
                                     '%s has subsections %s'
                                     % (m.group(0), sec, have)))
    return problems


def float_keys(root='.'):
    """Check 5: keyed figure and table references resolve, both ways, PER SCOPE.

    WHY THIS EXISTS. citation_markers() matches [@key] as
    [A-Za-z0-9][A-Za-z0-9._-]* , which excludes the colon, so every
    [@fig:harness] and [@tab:resolution] in the sources fell through it
    WITHOUT A WORD -- not reported as unresolved, not reported at all. The
    keyed float pass was therefore unvalidated from the moment it was written:
    a typo'd key, a caption with no float, or a figure nobody cites would all
    have reached the build. A check that silently ignores what it was not told
    about is worse than no check, because the clean line implies coverage.

    SCOPES, added with the cut pass. A float belongs to the article or to
    Supplement S1, declared by a trailing ':s1' on its placement marker. The
    caption library is SHARED and looked up by key, because a caption follows
    its float between documents unchanged. References are scoped by the file
    they sit in: the ten sections are the article, supplement-S1.md is S1.

    Five relations, each failing separately:
      key -> caption   exactly one delimited caption block per key
      key -> float     exactly one artefact: a figure FILE that exists, or a
                       table marker followed by a pipe table
      float -> prose   every float referenced at least once, IN ITS OWN SCOPE
      scope agreement  a document may not reference the other's float
      census           the article's counts equal the ruling
    """
    problems = []
    paper = os.path.join(root, PAPER)
    figures = os.path.join(root, FIGURES)
    sections = [os.path.join(paper, 'section%d.md' % n) for n in range(1, 11)]
    s1_path = os.path.join(paper, S1_FILE)
    others = []
    if os.path.isdir(figures):
        others = [os.path.join(figures, n) for n in sorted(os.listdir(figures))
                  if n.endswith('.md')]
    ref_sources = [(p, 'article') for p in sections]
    if os.path.isfile(s1_path):
        ref_sources.append((s1_path, 's1'))
    marker_sources = [p for p, _ in ref_sources] + others

    # --- references in prose, in order of first appearance, per scope --------
    refs = {}
    order = {'article': [], 's1': []}
    for sp, scope in ref_sources:
        if not os.path.isfile(sp):
            continue
        with open(sp, encoding='utf-8') as fh:
            lines = fh.readlines()
        for n, line in body_of(lines, True, sp):
            for m in re.finditer(r'\[@((?:fig|tab):[A-Za-z0-9][A-Za-z0-9._-]*)\]',
                                 line):
                k = m.group(1)
                # FIRST APPEARANCE IS PER SCOPE. Keying this off `refs`, which
                # is global, meant a key referenced from BOTH documents landed
                # only in the first scope's order -- so an S1 reference to an
                # article float was never examined and the cross-scope check
                # passed on it. The bug hid the very case the check exists for.
                if k not in order[scope]:
                    order[scope].append(k)
                refs.setdefault(k, []).append((sp, n, scope))

    # --- caption blocks: one shared library, found by key -------------------
    captions = {}
    for path in marker_sources:
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
        for key, _pos, line, _m in own_line_tags(
                text, r'caption:((?:fig|tab):[A-Za-z0-9][A-Za-z0-9._-]*):start'):
            captions.setdefault(key, []).append((path, line))
            if delimited(text, 'caption:%s:start' % key,
                         'caption:%s:end' % key) is None:
                problems.append(('caption:%s' % key,
                                 '%s:%d opens a caption that never properly '
                                 'closes (no own-line :end after it)'
                                 % (path, line)))

    # --- floats, each carrying the scope its marker declares ----------------
    floats = {}
    for path in marker_sources:
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
        lines = text.split('\n')
        for key, _pos, line, m in own_line_tags(
                text,
                r'figure:(fig:[A-Za-z0-9][A-Za-z0-9._-]*):'
                r'([^: \t>]+):(s1)|figure:(fig:[A-Za-z0-9][A-Za-z0-9._-]*):'
                r'([^: \t>]+)'):
            gs = m.groups()
            key = gs[1] or gs[4]
            fn = gs[2] or gs[5]
            scope = 's1' if gs[3] else 'article'
            floats.setdefault(key, []).append((path, line, scope))
            if not os.path.isfile(os.path.join(figures, fn)):
                problems.append(('figure:%s' % key,
                                 '%s:%d binds it to %s, which is not in %s/'
                                 % (path, line, fn, FIGURES)))
        for key, _pos, line, m in own_line_tags(
                text, r'table:(tab:[A-Za-z0-9][A-Za-z0-9._-]*)(?::(s1))?'):
            scope = 's1' if m.group(3) else 'article'
            floats.setdefault(key, []).append((path, line, scope))
            nxt = ''
            for cand in lines[line:]:
                if cand.strip():
                    nxt = cand
                    break
            if not nxt.startswith('|'):
                problems.append(('table:%s' % key,
                                 '%s:%d is not followed by a pipe table; the '
                                 'build would set the wrong block' % (path, line)))

    # --- the five relations --------------------------------------------------
    for scope in ('article', 's1'):
        for key in order[scope]:
            where = refs[key][0]
            if key not in captions:
                problems.append(('[@%s]' % key,
                                 'referenced at %s:%d but no caption block '
                                 'carries that key' % (where[0], where[1])))
            elif len(captions[key]) > 1:
                problems.append(('[@%s]' % key, 'has %d caption blocks: %s'
                                 % (len(captions[key]),
                                    ', '.join('%s:%d' % w
                                              for w in captions[key]))))
            if key not in floats:
                problems.append(('[@%s]' % key,
                                 'referenced at %s:%d but no float carries that '
                                 'key (a figure: binding or a table: marker)'
                                 % (where[0], where[1])))
            elif len(floats[key]) > 1:
                problems.append(('[@%s]' % key, 'has %d floats: %s'
                                 % (len(floats[key]),
                                    ', '.join('%s:%d' % (w[0], w[1])
                                              for w in floats[key]))))
            elif floats[key][0][2] != scope:
                problems.append(('[@%s]' % key,
                                 'referenced from %s but its float is declared '
                                 '%s -- a document cannot number the other\'s '
                                 'float' % (scope, floats[key][0][2])))

    for key, where in sorted(captions.items()):
        if key not in refs:
            problems.append(('caption:%s' % key,
                             'written at %s:%d but nothing references [@%s]'
                             % (where[0][0], where[0][1], key)))
    for key, where in sorted(floats.items()):
        if key not in refs:
            problems.append(('float:%s' % key,
                             'set at %s:%d but nothing references [@%s] -- '
                             'an unreferenced float has no number to print'
                             % (where[0][0], where[0][1], key)))

    counts = {}
    for scope in ('article', 's1'):
        keys = [k for k, v in floats.items() if v and v[0][2] == scope]
        counts[scope] = (sum(1 for k in keys if k.startswith('fig:')),
                         sum(1 for k in keys if k.startswith('tab:')))
    nfig, ntab = counts['article']
    if nfig != FLOAT_FIGURES:
        problems.append(('census', 'the article has %d figures, the ruling '
                         'says %d' % (nfig, FLOAT_FIGURES)))
    if ntab != FLOAT_TABLES:
        problems.append(('census', 'the article has %d tables, the ruling '
                         'says %d' % (ntab, FLOAT_TABLES)))
    return problems, order, floats, counts


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
    cite_problems, cite_entries, cited = citation_markers()
    entries, bib_problems = bibliography()
    uncited = citation_inventory(entries) if entries else []
    float_problems, float_order, floats, float_counts = float_keys()
    xref_problems = cross_references()

    ok = not (hits or stale or bib_problems or uncited or cite_problems
              or float_problems or xref_problems)
    if ok:
        print('clean.')
        print('  withdrawn phrases : none in live manuscript-facing text '
              '(%d files, matched across line breaks)' % len(targets()))
        print('  plan freshness    : 10/10 sections have exactly one marker, '
              'correctly placed, equal to the section draft')
        print('  citations         : %d bibliography entries, all present in '
              'their delimited inventories' % len(entries))
        print('  citation markers  : %d keys cited, each resolving to exactly one '
              'entry; every entry cited' % len(cited))
        inv = section_inventory()
        nsub = sum(len(v) for v in inv.values())
        print('  cross-references  : every float reference keyed; every section '
              'reference resolves (%d sections, %d subsections)'
              % (len(inv), nsub))
        af, at = float_counts['article']
        sf, st = float_counts['s1']
        print('  float keys        : article %d figures + %d tables (ruled); '
              'S1 %d + %d (reported)' % (af, at, sf, st))
        for scope, label in (('article', 'article'), ('s1', 'Supplement S1')):
            if not float_order[scope]:
                continue
            print('                      %s, by first appearance:' % label)
            pre = 'S' if scope == 's1' else ''
            fign = tabn = 0
            for key in float_order[scope]:
                if key.startswith('fig:'):
                    fign += 1
                    print('                        Fig. %s%-3d %s'
                          % (pre, fign, key))
                else:
                    tabn += 1
                    print('                        Table %s%-3d %s'
                          % (pre, tabn, key))
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
    if cite_problems:
        print('CITATION MARKERS\n')
        for label, msg in cite_problems:
            print('  %-18s %s' % (label, msg))
        print('\nEvery [@key] must resolve to exactly one entry, and every entry '
              'must be cited at least once.\n')
    if xref_problems:
        print('CROSS-REFERENCES\n')
        for label, msg in xref_problems:
            print('  %-28s %s' % (label, msg))
        print('\nFloat references must be keyed; section references must name a '
              'section the article has. To keep a retired number in historical '
              'text, put <!-- %s: why --> on or beside the line.\n' % XREF_OK)
    if float_problems:
        print('FIGURE AND TABLE KEYS\n')
        for label, msg in float_problems:
            print('  %-24s %s' % (label, msg))
        print('\nEvery [@fig:...] / [@tab:...] must have exactly one caption '
              'block and one float, and every float must be referenced.\n')
    if uncited:
        print('BIBLIOGRAPHY ENTRIES MISSING FROM AN INVENTORY\n')
        for label, where in uncited:
            print('  %-6s absent from %s' % (label, where))
        print('\nA reference nothing instructs a drafter to cite will not be '
              'cited.\n')
    return 1


if __name__ == '__main__':
    sys.exit(main())
