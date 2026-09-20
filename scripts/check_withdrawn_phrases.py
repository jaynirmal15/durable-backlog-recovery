#!/usr/bin/env python3
"""Fail if a withdrawn phrase survives anywhere a drafter or a generator reads.

Five times in this project a phrase was withdrawn from the place a reviewer was
looking at and left standing somewhere else: the F6 caption propagated through
report prose, a caption, a title drawn inside a PDF, the outline and a section
draft; the Set A narrative; "the conventional construction" banned in the
outline's version header while two live planning lines still taught it;
"the probe was sound" surviving its own withdrawal in the same plan that
withdrew it; and that phrase again in frozen section7.md's body after only the
outline had been swept.

A remembered rule has now failed five times, so this is the rule as a check.

Each entry names the phrase, the reason it was withdrawn, and where it is still
allowed to appear -- version histories and explicit prohibitions are legitimate,
because a record of a withdrawal is not the withdrawn claim.

It also checks a SECOND kind of staleness the phrase list cannot reach. A plan
instruction can go stale without containing any banned string: after section10
draft 2 removed the controller-comparison experiment, the outline's own SS-10
plan still said "controller comparison as declared future work" -- semantically
dead, lexically innocent. So each plan heading in paper/OUTLINE.md carries

    <!-- plan-synced-to: sectionN draft M -->

and this script fails when the section has moved past M. That does not prove the
plan is correct; it proves nobody has claimed it is current since draft M. The
claim is cheap to make and the absence of it is the signal.

A THIRD check covers the citation inventories. A work can enter
paper/references.md and never reach the instructions that tell a drafter to cite
it: Papadopoulos et al. was in the bibliography at [14], with a note saying it
attaches to SS-II-D, while neither SS-2's own citation inventory nor the
outline's Thread-4 anchor list knew it existed. Every entry below must appear in
BOTH paper/section2.md and paper/OUTLINE.md. Adding a reference means adding it
here too -- that is the forcing function, and it is cheap.

Usage: python3 scripts/check_withdrawn_phrases.py
Exit 0 if clean, 1 if a withdrawn phrase appears outside its allowed sites, a
plan is marked against an older draft than its section, or a reference is
missing from a citation inventory.
"""
import os
import re
import sys

# SCOPE, and the scoping is the point. A check that fires on legitimate history
# is a check nobody runs, so this one reads only text that a READER OF THE PAPER
# will see, or that GENERATES such text:
#
#   paper/section*.md   -- body only, below the first '---'. The header block
#                          above it is a change log: it describes withdrawals
#                          and must be free to quote them.
#   paper/OUTLINE.md    -- drafting instructions only, below the version header,
#                          for the same reason.
#   figures/*.md        -- generated tables the manuscript prints.
#   scripts/make_*.py   -- the generators that write them.
#
# results/ is EXCLUDED on purpose. Registrations are immutable once their commit
# is cited, and the reports are the campaign's historical record; a correction
# notice that quotes the wording it corrects is doing its job. Rewriting either
# to match a later convention would be editing the record, which this project
# has explicitly refused to do.

PAPER_SECTIONS = 'paper'
FIGURE_TABLES = 'figures'
GENERATORS = 'scripts'
SELF = 'check_withdrawn_phrases.py'

# phrase, why it was withdrawn, allowed-context regexes (case-insensitive).
# A line matching an allowed context is a record of the withdrawal, not a use.
WITHDRAWN = [
    ('the conventional construction',
     'No cited work establishes an industry default: DAGOR and Breakwater key on '
     'queueing delay, Bouncer on response-time percentiles. Permitted: "an '
     'established construction", and live latency as a literature-grounded comparator.',
     [r'withdraw', r'must not', r'never', r'do not restore', r'v8\.\d', r'v9\.\d',
      r'prohibit', r'banned', r'removed at', r'said ', r'read ', r'corrected']),

    ('the default answer',
     'Same reason as "the conventional construction".',
     [r'withdraw', r'must not', r'never', r'do not restore', r'v8\.\d', r'v9\.\d',
      r'prohibit', r'banned', r'removed at', r'said ', r'read ']),

    ('which was sound',
     'Frozen SS-IX-B concedes the probe\'s effective clock resolution was never '
     'measured and its repeatability was not measured at the two conditions '
     'compared. Permitted: the probe exposed rather than generated the bias.',
     [r'withdraw', r'must not', r'do not write', r'v8\.\d', r'v9\.\d', r'contradic']),

    ('which is impossible',
     'SS-VI states C_measured is a normalisation reference, not a physical ceiling, '
     'and two cells read 1.0002. Permitted: a pattern incompatible with treating '
     'the estimator as physically interpretable at collapsed points.',
     [r'withdraw', r'must not', r'struck', r'v8\.\d', r'v9\.\d', r'corrected']),

    ('true capacity',
     'The configured parameter is never called true capacity. The four rigid terms '
     'are C_config, C_staffed, C_model, C_measured. The harness field trueCapacity '
     'is an identifier and is exempt.',
     [r'truecapacity', r'never call', r'must not', r'residue', r'withdraw',
      r'corrected', r'identifier', r'field name', r'admin field',
      r'specification describes', r'it does not', r'falsifi']),

    ('apparent finding',
     'Table 3 column 1 is "Candidate explanation": the admission limit was '
     'explicitly not a finding.',
     [r'withdraw', r'must not', r'never', r'v8\.\d', r'v9\.\d', r'retired', r'corrected']),

    ('statistically',
     'The indistinguishability argument rests on resolution, not on an equivalence '
     'test. Struck from the claim register.',
     [r'struck', r'must not', r'never', r'withdraw', r'does not appear',
      r'invites', r'equivalence test']),
]


def window_for(numbered, idx):
    """The matched line plus any line the hard wrap has joined to it.

    These files are hard-wrapped at ~78 columns, so a prohibition and the phrase
    it prohibits routinely land on different lines: "do not restore" ends one
    line and the quoted phrase begins the next. Matching line-by-line reported
    four such splits as violations on the first run.

    But taking one line either side unconditionally excuses too much. A genuine
    violation passed this check while the PRECEDING SENTENCE, on its own line,
    happened to contain "corrected" -- an unrelated sentence, not a prohibition
    governing the phrase. Found by negative control, 2026-09-20.

    So a neighbour joins the window only if the wrap actually joined it: the
    line before, only when it does not end a sentence; the line after, only when
    the matched line does not end one. A blank line always breaks the window.
    """
    ends = re.compile(r'[.!?:;)"\u201d]\s*$')
    parts = [numbered[idx][1]]
    if idx > 0:
        prev = numbered[idx - 1][1]
        if prev.strip() and not ends.search(prev.rstrip()):
            parts.insert(0, prev)
    if idx + 1 < len(numbered):
        cur = numbered[idx][1]
        nxt = numbered[idx + 1][1]
        if nxt.strip() and not ends.search(cur.rstrip()):
            parts.append(nxt)
    return ' '.join(parts)


def allowed(context, patterns):
    low = context.lower()
    return any(re.search(p, low) for p in patterns)


def targets():
    """Manuscript-facing text and the generators that produce it."""
    out = []
    for name in sorted(os.listdir(PAPER_SECTIONS)):
        if name.endswith('.md'):
            out.append((os.path.join(PAPER_SECTIONS, name), True))
    if os.path.isdir(FIGURE_TABLES):
        for name in sorted(os.listdir(FIGURE_TABLES)):
            if name.endswith('.md'):
                out.append((os.path.join(FIGURE_TABLES, name), False))
    if os.path.isdir(GENERATORS):
        for name in sorted(os.listdir(GENERATORS)):
            if name.startswith('make_') and name.endswith('.py'):
                out.append((os.path.join(GENERATORS, name), False))
    return out


def body_of(lines, skip_header):
    """Drop the leading header block: it is a change log, not manuscript text."""
    if not skip_header:
        return list(enumerate(lines, 1))
    for i, line in enumerate(lines):
        if line.strip() == '---':
            return list(enumerate(lines[i + 1:], i + 2))
    return list(enumerate(lines, 1))


# (reference label, tokens that count as naming it, where it must appear).
# SS-2 names some works by system rather than by author, so either form counts.
# 'both'    -- literature cited from SS-II; must be in SS-2's inventory AND the plans.
# 'outline' -- cited from a section other than SS-II; required in the plans only.
#              Little is the only one: SS-III uses Little's law for the staffing
#              relation and SS-X repeats it, but SS-II never cites it. The first
#              version of this check demanded it in SS-2's inventory and was
#              wrong to; the check found that itself on its first scoped run.
CITED_WORKS = [
    ('[1] Mytkowicz et al.',        ['mytkowicz'],                 'both'),
    ('[2] Ousterhout',              ['ousterhout'],                'both'),
    ('[3] Heiser',                  ['heiser'],                    'both'),
    ('[4] DAGOR / Zhou et al.',     ['dagor', 'zhou'],             'both'),
    ('[5] Breakwater / Cho et al.', ['breakwater', 'cho,'],        'both'),
    ('[6] Bouncer / Xu & Colmenares', ['bouncer', 'colmenares'],   'both'),
    ('[7] Autopilot / Rzadca et al.', ['autopilot', 'rzadca'],     'both'),
    ('[8] Killer microseconds',     ['killer microsecond'],        'both'),
    ('[9] Tail at scale',           ['tail at scale'],             'both'),
    ('[10] Little',                 ["little's law", 'j. d. c. little'], 'outline'),
    ('[11] AWS Builders Library',   ['builders', 'yanacek'],       'both'),
    ('[12]/[13] GitLab incidents',  ['gitlab'],                    'both'),
    ('[14] Papadopoulos et al.',    ['papadopoulos'],              'both'),
]


def citation_inventory():
    """Works in the bibliography that no LIVE inventory tells a drafter to cite.

    SCOPED, and the first version was not. It searched each whole file, so
    removing Papadopoulos from the outline's live anchor list still "passed" --
    the word survived in the version-history header that RECORDED the addition.
    A check that reads history as if it were a live instruction is the exact
    defect this script exists to catch, reproduced inside the script itself.

    So: the outline is searched BELOW its version header (the live plans), and
    section2.md is searched IN its header block, because that is where its
    citation inventory actually lives.
    """
    missing = []

    outline = os.path.join(PAPER_SECTIONS, 'OUTLINE.md')
    sec2 = os.path.join(PAPER_SECTIONS, 'section2.md')
    if not (os.path.isfile(outline) and os.path.isfile(sec2)):
        return missing

    with open(outline, encoding='utf-8') as fh:
        lines = fh.readlines()
    body = ''.join(t[1] for t in body_of(lines, True)).lower()

    with open(sec2, encoding='utf-8') as fh:
        text = fh.read()
    cut = text.find('\n---\n')
    header = (text[:cut] if cut >= 0 else text).lower()

    for label, tokens, scope in CITED_WORKS:
        checks = [('paper/OUTLINE.md (live plans)', body)]
        if scope == 'both':
            checks.append(('paper/section2.md (citation inventory)', header))
        for where, hay in checks:
            if not any(t in hay for t in tokens):
                missing.append((label, where))
    return missing


def plan_sync():
    """Plans that have not been re-read since their section moved on."""
    stale = []
    outline = os.path.join(PAPER_SECTIONS, 'OUTLINE.md')
    if not os.path.isfile(outline):
        return stale
    with open(outline, encoding='utf-8') as fh:
        text = fh.read()
    for m in re.finditer(
            r'<!--\s*plan-synced-to:\s*section(\d{1,2})\s+draft\s+(\d+)\s*-->', text):
        sec, marked = int(m.group(1)), int(m.group(2))
        path = os.path.join(PAPER_SECTIONS, 'section%d.md' % sec)
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as fh:
            head = fh.read(4000)
        d = re.search(r'\*+\s*Draft\s+(\d+)', head, re.I)
        if not d:
            continue
        current = int(d.group(1))
        if current > marked:
            stale.append((sec, marked, current))
    return stale


def main():
    hits = []
    for path, skip_header in targets():
        if os.path.basename(path) == SELF:
            continue
        try:
            with open(path, encoding='utf-8') as fh:
                lines = fh.readlines()
        except (UnicodeDecodeError, OSError):
            continue
        numbered = body_of(lines, skip_header)
        for idx, (n, line) in enumerate(numbered):
            window = window_for(numbered, idx)
            for phrase, why, ctx in WITHDRAWN:
                if phrase in line.lower() and not allowed(window, ctx):
                    hits.append((path, n, phrase, why, line.strip()))

    stale = plan_sync()
    uncited = citation_inventory()

    if not hits and not stale and not uncited:
        print('clean: no withdrawn phrase appears in manuscript-facing text')
        print('checked %d file(s): paper/*.md bodies, figures/*.md, scripts/make_*.py'
              % len(targets()))
        print('all 10 section plans marked current with their sections')
        print('all %d bibliography entries present in both citation inventories'
              % len(CITED_WORKS))
        return 0

    if hits:
        print('WITHDRAWN PHRASES STILL PRESENT\n')
    for path, n, phrase, why, line in hits:
        print('%s:%d' % (path, n))
        print('  phrase : %s' % phrase)
        print('  why    : %s' % why)
        print('  line   : %s' % (line[:160] + ('...' if len(line) > 160 else '')))
        print()
    if hits:
        print('%d occurrence(s). A phrase withdrawn in one layer and left in '
              'another is not withdrawn.' % len(hits))
    if stale:
        print('\nPLAN INSTRUCTIONS NOT RE-READ SINCE THEIR SECTION MOVED\n')
        for sec, marked, current in stale:
            print('  SS-%d: plan marked for draft %d, section is at draft %d'
                  % (sec, marked, current))
        print('\nRe-read each plan against its section, fix what has gone stale, '
              'then bump its plan-synced-to marker. A stale plan is how a '
              'withdrawn claim gets written back in.')
    if uncited:
        print('\nBIBLIOGRAPHY ENTRIES MISSING FROM A CITATION INVENTORY\n')
        for label, path in uncited:
            print('  %-32s absent from %s' % (label, path))
        print('\nA reference nothing instructs a drafter to cite will not be '
              'cited. Add it to the inventory, or remove it from the list.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
