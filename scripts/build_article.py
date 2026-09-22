#!/usr/bin/env python3
"""Generate the IEEE Access submission from the frozen markdown.

ASSEMBLY-SPEC.md is the specification; this is its implementation. The build
GENERATES and never edits `paper/` -- a fix applied to article.tex is lost on
the next run and, worse, makes the source and the submission disagree.

WHAT IT REFUSES TO GUESS. Every construct the article uses is listed in an
explicit map here: the eight equations, the sixty-three backtick spans, the
seventeen non-ASCII characters. Anything not in a map STOPS THE BUILD. That is
the spec's rule and it is the whole value of the script: silent passthrough of
unrecognised markup is how a drafting note reaches a reviewer, and a heuristic
that "mostly works" on a paper this dense will be wrong somewhere nobody looks.

COMPILING IS SEPARATE. This machine has no TeX. Generation and every check
that does not need TeX run here; the compile happens where a toolchain exists.
`--compile` runs pdflatex (or latexmk with --latexmk) so the same invocation
works unchanged once TeX is installed here.

  python3 scripts/build_article.py             generate and check, no compile
  python3 scripts/build_article.py --compile   also run pdflatex twice
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, 'paper')
FIGURES = os.path.join(ROOT, 'figures')
TEMPLATE = os.path.join(ROOT, 'build', 'template',
                        'ACCESS_latex_template_20260513')
OUT = os.path.join(ROOT, 'build', 'access')

MAX_BYTES = 40 * 1024 * 1024        # IEEE Access: source and PDF each under 40 MB
# CUT-PLAN.md Draft 4 moved Fig. 2 and the amendment table to Supplement S1,
# so the ARTICLE's ruled census is five and seven. S1's own census was
# reported rather than asserted while the count was open -- the instruction
# named one S1 table and ruling 2 sent a second one there. It was ruled
# 2026-09-21 at one figure and two tables, so it is asserted now: a reported
# number nobody checks is the state this project keeps writing checks about.
EXPECT_FIGURES = 5
EXPECT_TABLES = 7
EXPECT_S1_FIGURES = 1
EXPECT_S1_TABLES = 2
EXPECT_EQUATIONS = 8
S1_SOURCE = 'supplement-S1.md'
S1_TITLE_RE = re.compile(r'^##\s+(S1-[A-Z]\.\s+.+?)\s*$')
# S1-H acquired numbered sub-headings when §VII-C and §VII-D moved into it.
# "S1-H.1" is the label a reader follows, so like the section labels it is set
# with a starred form and never renumbered by the class.
S1_SUBTITLE_RE = re.compile(r'^###\s+(S1-[A-Z]\.\d+\s+.+?)\s*$')
MAX_NESTING = 12                    # bold in a cell, code in bold, italic in code

# Template files the generated article actually needs. The class is used AS
# SHIPPED -- never edited, because a reviewer's build must match ours.
TEMPLATE_FILES = ['ieeeaccess.cls', 'IEEEtran.cls', 'IEEEtran.bst',
                  'spotcolor.sty', 'logo.png', 'notaglinelogo.png',
                  'bullet.png']
TEMPLATE_GLOBS = ('.pfb', '.tfm', '.map', '.fd')


class BuildError(Exception):
    """Something the build will not guess about. Always fatal, always named."""


WHERE = ['']


def fail(msg):
    """Every refusal names the source line it is refusing. A build that stops
    without saying where is a build a person cannot act on."""
    raise BuildError(('%s\n  at %s' % (msg, WHERE[0])) if WHERE[0] else msg)


# --------------------------------------------------------------------------
# Explicit maps. Every one of these is the spec's "fails rather than guesses".
# --------------------------------------------------------------------------

# The census from the source review, and nothing else. A character outside it
# stops the build instead of being dropped -- under pdflatex a stray non-ASCII
# byte is an error or, worse, silently absent from the PDF.
UNICODE = {
    '\u2014': '---',            # em dash
    '\u2013': '--',             # en dash
    # \S{} not \S: the prose writes "SSVI" as a section cross-reference, and
    # a bare \S swallows the following letters into \SVI -- an undefined
    # control sequence, and one that only shows up when TeX runs.
    '\u00a7': r'\S{}',
    '\u00b7': r'$\cdot$',
    '\u2212': r'$-$',           # true minus, not hyphen
    '\u00d7': r'$\times$',
    '\u2264': r'$\leq$',
    '\u2265': r'$\geq$',
    '\u00b1': r'$\pm$',
    '\u2192': r'$\rightarrow$',
    '\u0394': r'$\Delta$',    # Table 2's "Resolution the-normalised-step"
    '\u2308': r'$\lceil$',
    '\u2309': r'$\rceil$',
    '\u03c1': r'$\rho$',
    '\u03b4': r'$\delta$',
    '\u03bb': r'$\lambda$',
    '\u03c3': r'$\sigma$',
    '\u00b5': r'$\mu$',
    '\u2026': r'\ldots{}',
    '\u2019': "'",
    '\u2018': "`",
    '\u201c': "``",
    '\u201d': "''",
    # From references.md, which the first census did not cover: the author of
    # [11] is P. Tuma with a ring. Dropping the accent would misspell a cited
    # author's name in a published bibliography.
    '\u016f': r'\r{u}',
}

# The eight numbered equations, written out rather than translated by rule.
# They are the paper's formal content; a regex that got one subscript wrong
# would be a mathematical error printed in a journal.
EQUATIONS = {
    1: r'c = \lceil C_{\mathrm{config}} \cdot S \rceil',
    2: r'C_{\mathrm{staffed}} = c \,/\, S',
    3: r'\mathrm{queueCap} = 50 \cdot c',
    4: r'S_{\mathrm{actual}} = S + \delta',
    5: r'C_{\mathrm{model}} = c \,/\, (S + \delta)',
    6: r'C_{\mathrm{staffed}} \,/\, C_{\mathrm{model}} = 1 + \delta \,/\, S',
    7: r'\rho_{\mathrm{config}} = ( \lambda_{\mathrm{L,ach}} + R_{\mathrm{ach}} )'
       r' \,/\, C_{\mathrm{config}}',
    8: r'\rho_{\mathrm{eff}} = ( \lambda_{\mathrm{L,ach}} + R_{\mathrm{ach}} )'
       r' \,/\, C_{\mathrm{measured}}',
}

# Backtick spans, split into the spec's two classes by an explicit map.
# VARIABLES are set in math, which is IEEE style for a quantity; IDENTIFIERS
# -- commit hashes, field names, paths -- are set in \texttt. A span in
# neither map stops the build.
MATH = {
    'δ': r'\delta',
    'S': r'S',
    'c': r'c',
    'h': r'h',
    'ρ': r'\rho',
    'ρ*': r'\rho^{*}',
    'rl': r'r_{l}',
    'r_l': r'r_{l}',
    'spread': r'\mathrm{spread}',
    'vSLO': r'\mathrm{vSLO}',
    'vSLO_raw': r'\mathrm{vSLO}_{\mathrm{raw}}',
    'vSLO_latency': r'\mathrm{vSLO}_{\mathrm{latency}}',
    'vSLO_error': r'\mathrm{vSLO}_{\mathrm{error}}',
    'vSLO_both': r'\mathrm{vSLO}_{\mathrm{both}}',
    'vSLO ≤ 0.01': r'\mathrm{vSLO} \leq 0.01',
    'vSLO > 0.05': r'\mathrm{vSLO} > 0.05',
    'C_config': r'C_{\mathrm{config}}',
    'C_staffed': r'C_{\mathrm{staffed}}',
    'C_model': r'C_{\mathrm{model}}',
    'C_measured': r'C_{\mathrm{measured}}',
    'ρ_config': r'\rho_{\mathrm{config}}',
    'ρ_eff': r'\rho_{\mathrm{eff}}',
    'ρ_eff,safe': r'\rho_{\mathrm{eff,safe}}',
    'S = 5': r'S = 5',
    'S = 25': r'S = 25',
    '2 · c': r'2 \cdot c',
    'c / S': r'c \mathbin{/} S',
    '50 · S': r'50 \cdot S',
    'c/(S+δ)': r'c/(S + \delta)',
    'c / (S + δ)': r'c \mathbin{/} (S + \delta)',
    '50 · (S + δ)': r'50 \cdot (S + \delta)',
    'C_config · S': r'C_{\mathrm{config}} \cdot S',
    'δ = 0.463': r'\delta = 0.463',
    '[ρ_safe, 1]': r'[\rho_{\mathrm{safe}},\, 1]',
    'C_staffed = C_config': r'C_{\mathrm{staffed}} = C_{\mathrm{config}}',
    'C_measured / C_config': r'C_{\mathrm{measured}} \mathbin{/} C_{\mathrm{config}}',
    'ceil(C_config · S)': r'\lceil C_{\mathrm{config}} \cdot S \rceil',
    'c = ceil(C·S)': r'c = \lceil C \cdot S \rceil',
    '[R_lastSAFE, R_firstNonSAFE]':
        r'[R_{\mathrm{lastSAFE}},\, R_{\mathrm{firstNonSAFE}}]',
    'ρ_eff,safe = R_ach,lastSAFE / C_measured':
        r'\rho_{\mathrm{eff,safe}} = R_{\mathrm{ach,lastSAFE}} \mathbin{/}'
        r' C_{\mathrm{measured}}',
    'δ = S(C_config/plateau − 1)':
        r'\delta = S(C_{\mathrm{config}}/\mathrm{plateau} - 1)',
    'excess(25 ms) − excess(5 ms) = 0':
        r'\mathrm{excess}(25\,\mathrm{ms}) - \mathrm{excess}(5\,\mathrm{ms}) = 0',
    'D = m50 - m10 = 0.0689': r'D = m_{50} - m_{10} = 0.0689',
    'f ≤ 0.25': r'f \leq 0.25',
    'f ≥ 0.75': r'f \geq 0.75',
    'h ≥ 0.75': r'h \geq 0.75',
    'h ≤ 0.25': r'h \leq 0.25',
    'D': r'D',
    'f': r'f',
    'C = 400': r'C = 400',
    'f = +0.000': r'f = +0.000',
    'σ = 0.15': r'\sigma = 0.15',
    'queueCap = 50 · c': r'\mathrm{queueCap} = 50 \cdot c',
    '-0.006': r'-0.006',
    'h = (ρ*_E2b − ρ10) / D':
        r'h = (\rho^{*}_{\mathrm{E2b}} - \rho_{10}) \mathbin{/} D',
    'h = (0.98 − 0.9137) / 0.0689 = +0.980':
        r'h = (0.98 - 0.9137) \mathbin{/} 0.0689 = +0.980',
}

TEXTTT = {
    'trueCapacity', 'startedAt', 'results/E1B-PLAN.md', '"unknown"',
    '10.5281/zenodo.22761131', 'CAP-DRIVEN',
}
# Only spans the converted text actually uses are listed. Entries kept "just
# in case" rot: they assert a rendering nobody checks, and they hide which
# spans the article really contains. If one is needed again the build stops
# and says so, which is the whole mechanism.

# Commit hashes are identifiers too, and there are too many to list: seven
# lowercase hex characters is the project's own convention for one and is not
# a heuristic about prose, it is a format.
HASH_RE = re.compile(r'^[0-9a-f]{7}$')

SECTION_RE = re.compile(r'^##\s+([IVXLC]+|\d{1,2})\.\s+(.+?)\s*$')
SUBSECTION_RE = re.compile(r'^###\s+([A-Z])\.\s+(.+?)\s*$')
EQ_LINE_RE = re.compile(r'^ {2,}(\S.*?)\s{2,}\((\d)\)\s*$')
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)


# --------------------------------------------------------------------------
# Source reading
# --------------------------------------------------------------------------

def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def body_of(text):
    """Everything below the first own-line `---`: the header block is a change
    log, not article text."""
    m = re.search(r'^---\s*$', text, re.M)
    return text[m.end():] if m else text


def article_blocks(text, kind):
    """Delimited blocks, `kind:NAME:start` .. `kind:NAME:end`, own-line only.

    Own-line matters for the reason it matters in check_manuscript.py: these
    files describe their own delimiters in prose, and a substring search would
    treat the description as the thing described (METHOD-AUDIT item 37).
    """
    out = {}
    pat = re.compile(
        r'^[ \t]*<!--[ \t]*' + kind + r':([A-Za-z0-9:._-]+?):start[ \t]*-->[ \t]*$'
        r'(.*?)'
        r'^[ \t]*<!--[ \t]*' + kind + r':\1:end[ \t]*-->[ \t]*$',
        re.M | re.S)
    for m in pat.finditer(text):
        name = m.group(1)
        if name in out:
            raise BuildError('duplicate %s block %r' % (kind, name))
        out[name] = m.group(2).strip()
    # An unclosed or mismatched delimiter must fail, not silently vanish.
    opens = re.findall(r'^[ \t]*<!--[ \t]*' + kind +
                       r':([A-Za-z0-9:._-]+?):start[ \t]*-->[ \t]*$', text, re.M)
    for name in opens:
        if name not in out:
            raise BuildError('%s block %r opens but never properly closes'
                             % (kind, name))
    return out


# --------------------------------------------------------------------------
# Inline conversion
# --------------------------------------------------------------------------

# \mathbin{/}, not \,/\, : a slash is a mathord, and TeX may not break a line
# at one. Declaring it a binary operator makes the break legal, which is what
# was left of the 44pt overfull box in section IV-E after the formula was
# split at its "=" -- the right-hand side alone, R_ach,lastSAFE / C_measured,
# is still 53 characters of otherwise unbreakable math. The spacing is
# medmuskip either side rather than two thin spaces, which is the correct
# spacing for a binary operator anyway. Display equations are deliberately not
# changed: they are the paper's formal content and none of them overflows.
MATH_SPLIT_CHARS = 50   # longer than this and the formula gets a break point
MATH_SPLIT_MIN = 12     # ... but only if BOTH halves are worth a box


def math_span(latex):
    """One inline formula, split at its top-level "=" when it is long.

    Inline math is one unbreakable box, so a formula wider than what remains
    of a line pushes past the column: rho_eff,safe = R_ach,lastSAFE /
    C_measured ran 45pt over in section IV-E. The slash is a mathord, not a
    binary operator, so TeX may not break there, and this class gives no
    usable break at the relation either. Closing the group after "=" and
    reopening it makes an ordinary interword break point, with every glyph
    unchanged and the spacing around "=" preserved by keeping it inside the
    first group.
    """
    if len(latex) <= MATH_SPLIT_CHARS:
        return '$' + latex + '$'
    depth = 0
    for i, ch in enumerate(latex):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch == '=' and depth == 0 and 0 < i < len(latex) - 1:
            head, tail = latex[:i + 1].rstrip(), latex[i + 1:].lstrip()
            # Both halves must be substantial. Splitting on the first "="
            # regardless put "excess(25 ms) - excess(5 ms) =" in one box and a
            # bare "0" in the next, which buys nothing and invites a line
            # break that leaves the "= 0" stranded from what it evaluates.
            if len(head) < MATH_SPLIT_MIN or len(tail) < MATH_SPLIT_MIN:
                continue
            return '$' + head + '$ $' + tail + '$'
    return '$' + latex + '$'


def code_span(span):
    """A backtick span, by explicit map. Neither class -> stop."""
    if span in MATH:
        return math_span(MATH[span])
    if span in TEXTTT or HASH_RE.match(span):
        return r'\texttt{' + span.replace('_', r'\_').replace('"', "''") + '}'
    raise BuildError(
        'backtick span %r is in neither the variable map nor the identifier '
        'map. Add it to MATH (set in math, for a quantity) or TEXTTT (set in '
        '\\texttt, for a name) in this file -- do not edit the markdown.'
        % span)


def escape(text):
    """TeX specials, then the Unicode allowlist. Order matters: escaping first
    would leave the mapped Unicode's own backslashes mangled."""
    for ch in '\\{}':
        if ch in text:
            fail('raw %r in article text; the source census had none, so this '
                 'is new and needs a rule. Text: %r' % (ch, text[:160]))
    for ch in '%&#$^~_':
        text = text.replace(ch, '\\' + ch)
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        elif ch in UNICODE:
            out.append(UNICODE[ch])
        else:
            fail('character %r (U+%04X) is not in the Unicode map. The '
                 'census is the allowlist: add it with an explicit LaTeX '
                 'spelling. Text: %r' % (ch, ord(ch), text[:160]))
    return ''.join(out)


EQ_REFERENCED = set()


# NOT \textbf. ieeeaccess.cls:199 defines \textbf#1{{\bf #1}} and line 1092
# redefines \bf to TAKE AN ARGUMENT:
#   \long\def\bf#1{\ifmmode\mathbf{#1}...\else...\selectfont{#1}\fi}
# so \bf grabs one token, not the rest of the group. \textbf{$\rho$\_eff,safe}
# hands \bf the bare "$", which opens math that never closes -- "Extra }, or
# forgotten $". The quieter half is worse: \textbf{predicted at $S$ = 5} bolds
# only "predicted" and compiles CLEANLY, so the defect ships. \bfseries is a
# declaration, is not redefined by either class, and takes no argument.
BOLD_OPEN = '{\\bfseries '
BOLD_CLOSE = '}'


ALLTT_COLS = 52         # what fits one column at \footnotesize in this class


def alltt_wrap(line):
    """Break a fenced-display line that is wider than one column.

    The section-V arithmetic is 78 characters wide and ran 131pt past the
    column. alltt cannot break a line itself, and the display cannot become a
    float without becoming a numbered one, so the build breaks it: at the
    arrow, which is where the calculation turns from the sum to the rate, and
    the continuation is indented to sit under the expression rather than under
    the label. No character is added or removed -- only the line breaks are
    the build's.
    """
    if len(line) <= ALLTT_COLS:
        return [line]
    indent = len(line) - len(line.lstrip())
    cut = line.rfind('→', 0, ALLTT_COLS + 1)
    if cut < 0:
        cut = line.rfind(' ', indent + 1, ALLTT_COLS + 1)
    if cut < 0:
        fail('fenced display line is %d characters and offers no break point '
             'before column %d: %r' % (len(line), ALLTT_COLS, line))
    head = line[:cut].rstrip()
    tail = line[cut:].strip()
    pad = ' ' * (indent + 9)
    return [head] + alltt_wrap(pad + tail)


def alltt_char(ch):
    """A Unicode character inside alltt.

    alltt leaves $ with catcode "other", so it does NOT start math: the $ was
    typeset as a literal dollar and \rightarrow was then a math-only command
    in text mode -- "Missing $ inserted", four times. \ensuremath supplies the
    math mode itself and is correct in both modes.
    """
    if ord(ch) < 128:
        return ch
    if ch not in UNICODE:
        fail('character %r (U+%04X) in a fenced block is not in the Unicode '
             'map' % (ch, ord(ch)))
    latex = UNICODE[ch]
    m = re.fullmatch(r'\$(.+)\$', latex)
    return r'\ensuremath{%s}' % m.group(1) if m else latex


def eq_ref(n):
    EQ_REFERENCED.add(int(n))
    return r'\eqref{eq:%s}' % n


def range_ref(lo, hi):
    """"(4)-(6)" prints as a range and a reader takes it to name (5) as well,
    so the reference check counts every equation the range spans. Only the
    endpoints get an \\eqref, because that is what the printed text shows."""
    for n in range(int(lo), int(hi) + 1):
        EQ_REFERENCED.add(n)
    return r'\eqref{eq:%s}--\eqref{eq:%s}' % (lo, hi)


def inline(text, keep_bold=False, eqs=None, _shelf=None):
    """Markdown inline -> LaTeX, with code and float keys protected.

    Bold: ruling B. Body prose and captions set it PLAIN -- the words do not
    change, so the claim register's verbatim statements are untouched. Table
    cells keep it, because there it marks the registered choice and the
    measured value.
    """
    # ONE shelf for the whole recursion. Giving the nested call its own shelf
    # handed it the outer shelf's placeholders and none of their contents, so
    # it either crashed on an index or -- far worse -- resolved \x00 3 \x00 to
    # whatever happened to sit at index 3 in the inner shelf, silently swapping
    # one parked fragment for another.
    top = _shelf is None
    shelf = [] if top else _shelf

    def park(latex):
        shelf.append(latex)
        return '\x00%d\x00' % (len(shelf) - 1)

    text = re.sub(r'`([^`\n]+)`', lambda m: park(code_span(m.group(1))), text)
    text = re.sub(r'\[@(fig:[A-Za-z0-9._-]+)\]',
                  lambda m: park(r'Fig.~\ref{%s}' % m.group(1)), text)
    text = re.sub(r'\[@(tab:[A-Za-z0-9._-]+)\]',
                  lambda m: park(r'Table~\ref{%s}' % m.group(1)), text)
    text = re.sub(r'\[@([A-Za-z0-9][A-Za-z0-9._-]*)\]',
                  lambda m: park(r'\cite{%s}' % m.group(1)), text)

    if eqs:
        # A range first, so "(4)-(6)" does not become two separate refs with a
        # literal dash the class cannot renumber.
        text = re.sub(r'\((\d)\)\s*[\u2013-]\s*\((\d)\)',
                      lambda m: park(range_ref(m.group(1), m.group(2)))
                      if int(m.group(1)) in eqs and int(m.group(2)) in eqs
                      else m.group(0), text)
        text = re.sub(r'\((\d)\)',
                      lambda m: park(eq_ref(m.group(1)))
                      if int(m.group(1)) in eqs else m.group(0), text)

    # Bold and italic are PARKED, not spliced in as text. Splicing them fed
    # the build's own \textbf{...} back through escape(), which then reported
    # a raw backslash "in article text" that no source file contained -- the
    # generator accusing its own output. Recursing on the inner fragment keeps
    # nesting (bold inside a cell, code inside bold) correct.
    if keep_bold:
        text = re.sub(r'\*\*(.+?)\*\*',
                      lambda m: park(BOLD_OPEN
                                     + inline(m.group(1), True, eqs, shelf)
                                     + BOLD_CLOSE),
                      text, flags=re.S)
    else:
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text, flags=re.S)
    text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)',
                  lambda m: park(r'\textit{'
                                 + inline(m.group(1), keep_bold, eqs, shelf)
                                 + '}'),
                  text)

    text = escape(text)
    if not top:
        return text          # the outermost call owns resolution
    # Placeholders survive escaping because \x00 is not a TeX special.
    #
    # RESOLVE UNTIL STABLE. A single re.sub() pass does not rescan what it
    # substitutes, so a placeholder INSIDE a parked fragment survived into the
    # .tex: "**`h >= 0.75` reads S GOVERNS**" parked the code span, then parked
    # the whole \textbf{...} around it, and only the outer one was replaced.
    # pdflatex then saw a literal NUL and the span's text was simply gone from
    # the article. Nested parking is normal here -- bold around code, italic
    # around bold -- so one pass was never enough.
    for _ in range(MAX_NESTING):
        after = re.sub('\x00(\\d+)\x00',
                       lambda m: shelf[int(m.group(1))], text)
        if after == text:
            return text
        text = after
    fail('placeholder resolution did not settle after %d passes; a parked '
         'fragment probably refers to itself' % MAX_NESTING)


# --------------------------------------------------------------------------
# Block conversion
# --------------------------------------------------------------------------

PROSE_WIDTH = 40        # a column whose widest cell exceeds this is prose
# Width estimation, so a table that cannot fit is caught here rather than as
# an overfull box a person has to read a log to find. These are estimates:
# \textwidth in this class is about 516pt, and a character of the class's 7pt
# table font averages near 3.1pt. The compile is the authority; this only
# decides how many columns to let wrap.
TEXTWIDTH_PT = 516.0
CHAR_PT = 3.1
COLSEP_PT = 12.0        # \tabcolsep is 6pt, applied on both sides
X_MIN_CHARS = 10        # an X column can wrap down to roughly this


def short_caption(raw):
    """The entry for the list of figures: a moving argument, so it must be one
    short line with no \\par in it.

    Fig. 4's caption is four paragraphs. LaTeX writes \\caption's argument into
    the .lof, where a \\par ends the paragraph mid-\\addcontentsline --
    "Paragraph ended before \\addcontentsline was complete". Giving \\caption an
    OPTIONAL argument makes that short text the moving one and leaves the long
    text free to hold \\par.
    """
    first = raw.strip().split('\n\n')[0].strip()
    m = re.match(r'\*\*(.+?)\*\*', first, re.S)
    text = m.group(1) if m else first
    text = ' '.join(text.split())
    if not m:
        cut = re.match(r'(.+?[.!?])(\s|$)', text)
        if cut:
            text = cut.group(1)
    return text


def caption_tex(raw):
    """\\caption[short]{long}, paragraphs joined with \\par."""
    paras = [p.strip() for p in raw.strip().split('\n\n') if p.strip()]
    long_text = r' \par '.join(inline(' '.join(p.split())) for p in paras)
    return r'\caption[%s]{%s}' % (inline(short_caption(raw)), long_text)


def table(lines, key, caption, wide=True):
    """A markdown pipe table -> table* with its caption ABOVE, per IEEE style."""
    rows = [l for l in lines if l.strip().startswith('|')]
    if len(rows) < 2:
        raise BuildError('table %s has no separator row' % key)

    def cells(row):
        return [c.strip() for c in row.strip().strip('|').split('|')]

    header, sep, data = cells(rows[0]), cells(rows[1]), [cells(r) for r in rows[2:]]
    for s in sep:
        if not re.fullmatch(r':?-{2,}:?', s):
            raise BuildError('table %s separator cell %r is not an alignment'
                             % (key, s))
    right = [s.endswith(':') and not s.startswith(':') for s in sep]

    # WHY tabularx. An l column is as wide as its widest cell, so a table
    # whose cells are sentences becomes a single unbreakable line: T7's
    # candidate-explanation cells overran the page by 3,416pt. Any column
    # whose widest cell is prose becomes an X column, which wraps and shares
    # the remaining width; short numeric columns keep l/r so the numbers stay
    # aligned and do not get stretched.
    widest = [max(len(r[i]) for r in [header] + data) for i in range(len(sep))]
    prose = [w > PROSE_WIDTH for w in widest]

    # A table of short numeric columns can still overrun the page simply by
    # having many of them: the eleven-column resolution table was 141pt too
    # wide with no cell over 24 characters, so the prose test alone missed it.
    # Widen-to-wrap the broadest remaining column until the estimate fits.
    def estimate():
        total = COLSEP_PT * len(sep)
        for i, w in enumerate(widest):
            total += CHAR_PT * (X_MIN_CHARS if prose[i] else w)
        return total

    while estimate() > TEXTWIDTH_PT:
        candidates = [i for i in range(len(sep)) if not prose[i]]
        if not candidates:
            break
        prose[max(candidates, key=lambda i: widest[i])] = True
    if any(prose):
        align = ''.join(
            r'>{\raggedright\arraybackslash}X' if prose[i]
            else ('r' if right[i] else 'l')
            for i in range(len(sep)))
        open_tab = r'\begin{tabularx}{\textwidth}{%s}' % align
        close_tab = r'\end{tabularx}'
    else:
        align = ''.join('r' if right[i] else 'l' for i in range(len(sep)))
        open_tab = r'\begin{tabular}{%s}' % align
        close_tab = r'\end{tabular}'

    env = 'table*' if wide else 'table'
    out = [r'\begin{%s}[!t]' % env, caption_tex(caption),
           r'\label{%s}' % key, r'\centering', r'\footnotesize',
           open_tab, r'\hline']
    out.append(' & '.join(BOLD_OPEN + inline(h, True) + BOLD_CLOSE
                          for h in header) + r' \\ \hline')
    for row in data:
        if len(row) != len(header):
            raise BuildError('table %s: a row has %d cells, the header has %d'
                             % (key, len(row), len(header)))
        out.append(' & '.join(inline(c, keep_bold=True) for c in row) + r' \\')
    out += [r'\hline', close_tab, r'\end{%s}' % env]
    return out


# HOW EACH FIGURE IS PLACED AND SIZED. Adopted 2026-09-21 after measuring
# every figure's intrinsic width, its type sizes at each candidate scale, and
# its ink bounding box, then reading each candidate rendered at its printed
# size. Nothing here touches a generator: data, axis limits, ticks, labels and
# annotations are exactly as committed, and the figure PDFs are byte-unchanged.
#
# THE FINDING THAT DROVE IT: the generators produce TWO design widths, and the
# build was applying one placement rule to both. F4 and F6 are drawn 244.8pt
# wide -- column width -- and width=\textwidth was enlarging them 2.04x, so
# their type printed at 13-16pt against 9pt body text and each cost over half
# a page. Setting them single-column is their native size, not a compromise.
#
# 'crop' trims the figure's own whitespace via \includegraphics trim/clip.
# Cropping is preferred to reducing scale because it takes the margin instead
# of the data region: it cuts height AND makes the type larger, since the
# remaining ink is scaled up to the same printed width.
#
# The third field is a fraction of the span's width. It exists because
# CROPPING CHANGES THE TYPE SIZE: trimming Fig. 1's margins and holding the
# printed width at \textwidth scaled its remaining ink up 1.17x, so its labels
# printed at 7.6-9.3pt -- above body text and above every other figure in the
# paper, which print at 6.3-7.9pt. Setting it at 0.85 of the span puts the
# same cropped figure at 6.4-7.9pt, in the band the others occupy, and takes
# another 0.04 page with it. The lever for type size is HERE, not in the
# generator: make_figures.py authors every figure at 8pt and the printed size
# is authored size x (printed width / source width).
FIGURE_LAYOUT = {
    # key                  span      trim (l, b, r, t)         width fraction
    'fig:harness':        ('full',   (62.9, 27.9, 12.5, 24.0), 0.85),
    'fig:collapse':       ('full',   None,                     1.0),
    'fig:plateau':        ('column', None,                     1.0),
    'fig:overhead':       ('full',   None,                     1.0),
    'fig:signals':        ('column', None,                     1.0),
    # Fig. S1, re-measured after the notation fix regenerated it. 0.90 puts
    # its type at 7.9 / 7.4 / 6.9pt, which is F3's band exactly.
    'fig:capacity-model': ('full',   (58.3, 11.2, 0.0, 21.5),  0.90),
}


def figure(key, filename, caption):
    if key not in FIGURE_LAYOUT:
        fail('figure %s has no entry in FIGURE_LAYOUT; placement and size are '
             'decided explicitly, never by default' % key)
    span, trim, frac = FIGURE_LAYOUT[key]
    env = 'figure*' if span == 'full' else 'figure'
    width = r'\textwidth' if span == 'full' else r'\columnwidth'
    opts = 'width=%s' % width if frac == 1.0 else 'width=%.3g%s' % (frac, width)
    if trim:
        opts = 'trim=%.1f %.1f %.1f %.1f, clip, %s' % (trim + (opts,))
    return [r'\begin{%s}[!t]' % env, r'\centering',
            r'\includegraphics[%s]{%s}' % (opts, filename),
            caption_tex(caption), r'\label{%s}' % key,
            r'\end{%s}' % env]


# --------------------------------------------------------------------------
# The build
# --------------------------------------------------------------------------

class Build(object):

    def __init__(self, target='article'):
        self.target = target
        self.tex = []
        self.equations = []
        self.conversions = []
        self.emitted_floats = []
        self.captions = {}
        self.fig_files = {}
        self.file_tables = {}
        self.pending = {}

    # -- inputs -----------------------------------------------------------
    @staticmethod
    def scope_of(suffix):
        """':s1' on a placement marker puts the float in the supplement."""
        return 's1' if suffix else 'article'

    def load_floats(self):
        """Captions from every source; floats only from this target's scope.

        The caption library is SHARED and looked up by key, because a caption
        follows its float between documents unchanged -- Fig. 2's caption is
        still in CAPTIONS.md now that its figure is declared ':s1'. Placement
        markers are scoped, so the same run of this method serves either
        target and a float cannot appear in both documents.
        """
        sources = [os.path.join(FIGURES, 'CAPTIONS.md')]
        sources += [os.path.join(FIGURES, n)
                    for n in sorted(os.listdir(FIGURES))
                    if n.startswith('T') and n.endswith('.md')]
        sources += [os.path.join(PAPER, 'section%d.md' % s) for s in range(1, 11)]
        s1 = os.path.join(PAPER, S1_SOURCE)
        if os.path.isfile(s1):
            sources.append(s1)

        for path in sources:
            text = read(path)
            name = os.path.basename(path)
            self.captions.update(article_blocks(text, 'caption'))
            lines = text.split('\n')

            for m in re.finditer(
                    r'^[ \t]*<!--[ \t]*figure:(fig:[A-Za-z0-9._-]+):'
                    r'([^: \t>]+?)(?::(s1))?[ \t]*-->[ \t]*$', text, re.M):
                key, fn = m.group(1), m.group(2)
                if not os.path.isfile(os.path.join(FIGURES, fn)):
                    raise BuildError('figure %s binds to %s, which is missing'
                                     % (key, fn))
                if self.scope_of(m.group(3)) != self.target:
                    continue
                if key in self.fig_files:
                    raise BuildError('figure %s is bound twice' % key)
                self.fig_files[key] = fn

            # Tables are COLLECTED here, not emitted where their marker sits.
            # LaTeX numbers floats by position in the source, so emitting a
            # table at its marker printed the resolution table as Table 1:
            # tab:amendments was first REFERENCED early in §IV while its
            # markup sat hundreds of lines later. Every float is placed at its
            # first reference instead, which is what makes the printed numbers
            # equal the ruling's order of first appearance.
            for m in re.finditer(
                    r'^[ \t]*<!--[ \t]*table:(tab:[A-Za-z0-9._-]+)'
                    r'(?::(s1))?[ \t]*-->[ \t]*$', text, re.M):
                key = m.group(1)
                start = text.count('\n', 0, m.start()) + 1
                block = []
                for line in lines[start:]:
                    if line.strip().startswith('|'):
                        block.append(line)
                    elif block:
                        break
                if not block:
                    raise BuildError('%s: marker %s is not followed by a table'
                                     % (name, key))
                if self.scope_of(m.group(2)) != self.target:
                    continue
                if key in self.file_tables:
                    raise BuildError('table %s is marked in two places' % key)
                self.file_tables[key] = block

    # -- front matter -----------------------------------------------------
    def front_matter(self):
        if self.target == 's1':
            return self.s1_front_matter()
        fm = article_blocks(read(os.path.join(PAPER, 'frontmatter.md')),
                            'article')
        need = ['title', 'short-title', 'author', 'address', 'corresp',
                'abstract', 'index-terms', 'biography']
        for k in need:
            if k not in fm:
                raise BuildError('frontmatter.md has no article:%s block' % k)
        self.fm = fm
        t = self.tex
        t += [r'\documentclass{ieeeaccess}',
              r'\usepackage{cite}',
              r'\usepackage{amsmath,amssymb,amsfonts}',
              r'\usepackage{graphicx}',
              r'\usepackage{textcomp}',
              r'\usepackage{alltt}',
              r'\usepackage{array}',
              r'\usepackage{tabularx}',
              # algorithmic.sty is NOT loaded: the sample preamble loads it,
              # this TeX installation may not have it, and the article has no
              # algorithm environment. Recorded in ASSEMBLY-SPEC.md 0.
              r'\begin{document}',
              r'\history{Date of publication xxxx 00, 0000, date of current '
              r'version xxxx 00, 0000.}',
              r'\doi{10.1109/ACCESS.2026.0429000}',
              r'\title{%s}' % inline(fm['title']),
              r'\author{\uppercase{%s}\authorrefmark{1}}' % inline(fm['author']),
              r'\address[1]{%s}' % inline(fm['address']),
              r'\markboth{%s}{%s}' % (inline(fm['short-title']),
                                      inline(fm['short-title'])),
              r'\corresp{%s}' % inline(fm['corresp']),
              '',
              r'\begin{abstract}',
              inline(' '.join(fm['abstract'].split())),
              r'\end{abstract}',
              '',
              r'\begin{IEEEkeywords}',
              inline(' '.join(fm['index-terms'].split())),
              r'\end{IEEEkeywords}',
              '',
              r'\titlepgskip=-15pt',
              r'\maketitle', '']

    # -- sections ---------------------------------------------------------
    def s1_front_matter(self):
        """The supplement is set with the same class and the same maps, so a
        reader gets one typeface and one set of conventions across both files.

        It is NOT an article: no abstract, no index terms, no bibliography and
        no biography. Its floats are lettered S1, S2 ... by redefining
        \\thetable and \\thefigure, because the class would otherwise number
        them 1, 2 and collide with the article a reader has open beside it.
        """
        text = read(os.path.join(PAPER, S1_SOURCE))
        m = re.match(r'#\s+(.+?)\s*$', text, re.M)
        if not m:
            raise BuildError('%s has no `# ` title line' % S1_SOURCE)
        head = text[:text.index('\n---\n')] if '\n---\n' in text else ''
        note = re.search(r'^\*(.+?)\*$', COMMENT_RE.sub('', head),
                         re.M | re.S)
        self.tex += [r'\documentclass{ieeeaccess}',
                     r'\usepackage{cite}',
                     r'\usepackage{amsmath,amssymb,amsfonts}',
                     r'\usepackage{graphicx}',
                     r'\usepackage{textcomp}',
                     r'\usepackage{alltt}',
                     r'\usepackage{array}',
                     r'\usepackage{tabularx}',
                     r'\renewcommand{\thetable}{S\arabic{table}}',
                     r'\renewcommand{\thefigure}{S\arabic{figure}}',
                     r'\begin{document}',
                     r'\history{Supplementary material.}',
                     r'\doi{10.1109/ACCESS.2026.0429000}',
                     r'\title{%s}' % inline(m.group(1)),
                     r'\author{\uppercase{Jay Suresh Nirmal}\authorrefmark{1}}',
                     r'\address[1]{Independent Researcher, Boston, MA, USA}',
                     r'\markboth{Nirmal: Supplement S1}{Nirmal: Supplement S1}',
                     '']
        if note:
            self.tex += [r'\begin{abstract}',
                         inline(' '.join(note.group(1).split())),
                         r'\end{abstract}', '']
        self.tex += [r'\titlepgskip=-15pt', r'\maketitle', '']

    def sections(self):
        if self.target == 's1':
            self.section(os.path.join(PAPER, S1_SOURCE), 0)
            return
        for sec in range(1, 11):
            self.section(os.path.join(PAPER, 'section%d.md' % sec), sec)

    def section(self, path, num):
        text = COMMENT_RE.sub(lambda m: self.keep_marker(m.group(0)),
                              body_of(read(path)))
        lines = text.split('\n')
        i, para = 0, []
        while i < len(lines):
            line = lines[i]
            WHERE[0] = '%s:%d' % (os.path.basename(path), i + 1)

            if line.startswith('\x01'):                 # a preserved marker
                key = line[1:].strip()
                self.flush(para)
                para = []
                if key.startswith('table:'):
                    # Content already collected in load_floats(); skip past it
                    # so the raw pipe rows do not fall through as prose.
                    _, i = self.take_table(lines, i + 1)
                    continue
                i += 1
                continue

            if line.startswith('```'):
                if line.strip() != '```':
                    raise BuildError(
                        '%s:%d fenced block carries a language tag (%r), which '
                        'the spec reads as drafting code, not article content'
                        % (os.path.basename(path), i + 1, line.strip()))
                self.flush(para)
                para = []
                block, i = [], i + 1
                while i < len(lines) and lines[i].strip() != '```':
                    block.append(lines[i])
                    i += 1
                # alltt, not verbatim. The block is a worked arithmetic
                # display and contains a real arrow; verbatim would hand
                # pdflatex a raw U+2192 it cannot set, and the spacing that
                # makes the display readable rules out an ordinary paragraph.
                # In alltt only \ { } keep their meaning, so the Unicode map
                # applies and every space and line break survives.
                for ln in block:
                    for ch in '\\{}':
                        if ch in ln:
                            fail('fenced block contains %r, which alltt reads '
                                 'as markup: %r' % (ch, ln))
                wrapped = []
                for ln in block:
                    wrapped += alltt_wrap(ln)
                self.tex += [r'{\footnotesize\begin{alltt}'] + \
                            [''.join(alltt_char(ch) for ch in ln)
                             for ln in wrapped] + \
                            [r'\end{alltt}}', '']
                i += 1
                continue

            m = EQ_LINE_RE.match(line)
            if m:
                self.flush(para)
                para = []
                n = int(m.group(2))
                if n not in EQUATIONS:
                    raise BuildError('%s:%d equation (%d) has no entry in the '
                                     'EQUATIONS map' % (path, i + 1, n))
                if n in self.equations:
                    raise BuildError('equation (%d) is defined twice' % n)
                self.equations.append(n)
                self.tex += [r'\begin{equation}', EQUATIONS[n],
                             r'\label{eq:%d}' % n, r'\end{equation}', '']
                i += 1
                continue

            m = S1_SUBTITLE_RE.match(line) if self.target == 's1' else None
            if m:
                self.flush(para)
                para = []
                self.tex += [r'\subsection*{%s}' % inline(m.group(1)), '']
                i += 1
                continue

            m = S1_TITLE_RE.match(line) if self.target == 's1' else None
            if m:
                self.flush(para)
                para = []
                # \section*, not \section: the label "S1-A" is the identity a
                # reader follows from the article, so the class must not
                # renumber it to "I".
                self.tex += [r'\section*{%s}' % inline(m.group(1)), '']
                i += 1
                continue

            m = SECTION_RE.match(line)
            if m:
                self.flush(para)
                para = []
                # The numeral is discarded: the class numbers sections, and a
                # hard-coded numeral is exactly what the keyed design removes.
                self.tex += [r'\section{%s}' % inline(m.group(2)), '']
                i += 1
                continue

            m = SUBSECTION_RE.match(line)
            if m:
                self.flush(para)
                para = []
                self.tex += [r'\subsection{%s}' % inline(m.group(2)), '']
                i += 1
                continue

            if line.startswith('#'):
                raise BuildError('%s:%d heading %r is neither "## N. TITLE" nor '
                                 '"### X. Title"'
                                 % (os.path.basename(path), i + 1, line[:60]))

            if line.strip().startswith('|'):
                raise BuildError('%s:%d a table with no table: marker above it'
                                 % (os.path.basename(path), i + 1))

            if re.match(r'^[-*] ', line):
                self.flush(para)
                para = []
                items, i = [], i
                while i < len(lines) and re.match(r'^[-*] ', lines[i]):
                    items.append(lines[i][2:])
                    i += 1
                self.tex += [r'\begin{itemize}'] + \
                            [r'\item ' + inline(x, eqs=EQUATIONS) for x in items] + \
                            [r'\end{itemize}', '']
                continue

            if line.strip():
                para.append(line)
            else:
                self.flush(para)
                para = []
            i += 1
        self.flush(para)

    def keep_marker(self, comment):
        """Comments vanish, except the two that place a float."""
        # The optional :s1 must be matched here too. Without it the marker
        # for an S1 table was not recognised as a marker at all, the comment
        # was dropped with every other comment, and the table's rows fell
        # through into the prose stream -- which the build then reported as a
        # table with no marker above it, one line off from the real cause.
        m = re.match(r'<!--\s*(table:tab:[A-Za-z0-9._-]+)(?::s1)?\s*-->',
                     comment)
        if m:
            return '\n\x01' + m.group(1) + '\n'
        return ''

    def take_table(self, lines, i):
        block = []
        while i < len(lines):
            if lines[i].strip().startswith('|'):
                block.append(lines[i])
            elif block:
                break
            i += 1
        return block, i

    def flush(self, para):
        if not para:
            return
        text = ' '.join(l.strip() for l in para).strip()
        if not text:
            return
        self.tex += [inline(text, eqs=EQUATIONS), '']
        # A float is emitted after the paragraph that first refers to it, so
        # LaTeX's source order IS order of first appearance and the printed
        # numbers come out as the ruling derives them.
        for key in re.findall(r'\\ref\{((?:fig|tab):[A-Za-z0-9._-]+)\}',
                              self.tex[-2]):
            if key in self.emitted_floats:
                continue
            if key in self.fig_files:
                self.emit_figure(key)
            elif key in self.file_tables:
                self.emit_table(key, self.file_tables[key])

    def emit_table(self, key, block):
        if key in self.emitted_floats:
            raise BuildError('table %s emitted twice' % key)
        if key not in self.captions:
            raise BuildError('table %s has no caption block' % key)
        self.emitted_floats.append(key)
        self.tex += table(block, key, self.captions[key]) + ['']

    def emit_figure(self, key):
        if key in self.emitted_floats:
            raise BuildError('figure %s emitted twice' % key)
        if key not in self.captions:
            raise BuildError('figure %s has no caption block' % key)
        self.emitted_floats.append(key)
        self.tex += figure(key, self.fig_files[key], self.captions[key]) + ['']

    # -- back matter ------------------------------------------------------
    def bibliography(self):
        if self.target == 's1':
            self.tex += ['', r'\EOD', r'\end{document}', '']
            return []
        WHERE[0] = 'references.md'
        text = read(os.path.join(PAPER, 'references.md'))
        starts = list(re.finditer(r'^\*\*\[(\d+)\]\*\*', text, re.M))
        if not starts:
            raise BuildError('references.md has no numbered entries')
        entries = []
        for j, m in enumerate(starts):
            end = starts[j + 1].start() if j + 1 < len(starts) else len(text)
            block = text[m.start():end]
            k = re.search(r'<!--\s*marker-key:\s*([A-Za-z0-9._-]+)\s*-->', block)
            if not k:
                raise BuildError('reference [%s] has no marker-key' % m.group(1))
            body = COMMENT_RE.sub('', block)
            body = re.sub(r'^\*\*\[\d+\]\*\*\s*', '', body).strip()
            body = ' '.join(body.split())
            entries.append((int(m.group(1)), k.group(1), body))

        # The committed file is authoritative, and the build FAILS if the
        # markers disagree with it. Recomputing and silently reordering would
        # let the printed article and the committed file diverge with nothing
        # to catch it.
        order, seen = [], set()
        for sec in range(1, 11):
            b = body_of(read(os.path.join(PAPER, 'section%d.md' % sec)))
            for m in re.finditer(r'\[@([A-Za-z0-9][A-Za-z0-9._-]*)\]', b):
                if m.group(1) not in seen:
                    seen.add(m.group(1))
                    order.append(m.group(1))
        committed = [k for _, k, _ in entries]
        if order != committed:
            raise BuildError(
                'references.md order disagrees with first appearance.\n'
                '  committed: %s\n  markers  : %s' % (committed, order))

        self.tex += ['', r'\begin{thebibliography}{%d}' % len(entries)]
        for _, key, body in entries:
            self.tex.append(r'\bibitem{%s} %s' % (key, inline(body)))
        self.tex += [r'\end{thebibliography}', '']

        bio = ' '.join(self.fm['biography'].split())
        name = re.match(r'\*\*([^*]+)\*\*', bio)
        if not name:
            raise BuildError('the biography does not open with a bold name')
        rest = bio[name.end():].strip()
        self.tex += [r'\begin{IEEEbiographynophoto}{%s}'
                     % inline(name.group(1).title()),
                     inline(rest), r'\end{IEEEbiographynophoto}', '',
                     r'\EOD', r'\end{document}', '']
        return entries

    # -- checks -----------------------------------------------------------
    def checks(self, entries):
        out, tex = [], '\n'.join(self.tex)
        nfig = sum(1 for k in self.emitted_floats if k.startswith('fig:'))
        ntab = sum(1 for k in self.emitted_floats if k.startswith('tab:'))

        def want(ok, msg):
            out.append(('PASS' if ok else 'FAIL', msg))

        ctrl = sorted({c for c in tex if ord(c) < 32 and c != '\n'})
        want(not ctrl,
             'no control character in the .tex'
             + ('' if not ctrl else
                ' -- found %s' % ', '.join('U+%04X' % ord(c) for c in ctrl)))
        want(all(ord(c) < 128 for c in tex),
             'the .tex is pure ASCII')
        want('<!--' not in tex, 'no HTML comment survives into the .tex')
        want('[@' not in tex, 'no [@ marker survives into the .tex')
        if self.target == 'article':
            want(nfig == EXPECT_FIGURES,
                 'figures: %d, the ruling says %d' % (nfig, EXPECT_FIGURES))
            want(ntab == EXPECT_TABLES,
                 'tables: %d, the ruling says %d' % (ntab, EXPECT_TABLES))
            want(len(self.equations) == EXPECT_EQUATIONS,
                 'equations: %d, the source has %d'
                 % (len(self.equations), EXPECT_EQUATIONS))
            want(sorted(self.equations) == list(range(1, EXPECT_EQUATIONS + 1)),
                 'equation numbers are 1..%d with none missing'
                 % EXPECT_EQUATIONS)
        else:
            want(nfig == EXPECT_S1_FIGURES,
                 'S1 figures: %d, the ruling says %d'
                 % (nfig, EXPECT_S1_FIGURES))
            want(ntab == EXPECT_S1_TABLES,
                 'S1 tables: %d, the ruling says %d'
                 % (ntab, EXPECT_S1_TABLES))
        for key in self.emitted_floats:
            want(tex.count(r'\ref{%s}' % key) >= 1,
                 'float %s is referenced in the prose' % key)
            want(tex.count(r'\label{%s}' % key) == 1,
                 'float %s has exactly one label' % key)
        # REPORT, not a check: the author ruled 2026-09-20 that a numbered
        # equation need not be referenced. The list is still printed, because
        # an equation that loses its last reference is worth seeing once.
        unref = sorted(n for n in self.equations if n not in EQ_REFERENCED)
        out.append(('note', 'equations not referenced in the prose: %s'
                    % (', '.join('(%d)' % n for n in unref) if unref
                       else 'none')))

        # The % parity check the spec asks for by name: an unescaped percent
        # silently deletes the rest of its line, with no error anywhere.
        src = ''
        if self.target == 'article':
            for sec in range(1, 11):
                src += COMMENT_RE.sub('', body_of(
                    read(os.path.join(PAPER, 'section%d.md' % sec))))
        else:
            src = COMMENT_RE.sub('', body_of(
                read(os.path.join(PAPER, S1_SOURCE))))
        want(len(re.findall(r'(?<!\\)%', tex)) == 0,
             'every %% in the .tex is escaped (%d source, %d escaped)'
             % (src.count('%'), len(re.findall(r'\\%', tex))))
        want(src.count('%') <= len(re.findall(r'\\%', tex)),
             'no source %% was lost in translation')
        want(len(entries) == len(set(k for _, k, _ in entries)),
             'bibliography keys are unique')
        return out

    # -- output -----------------------------------------------------------
    def write(self):
        if not os.path.isdir(OUT):
            os.makedirs(OUT)
        for name in os.listdir(TEMPLATE):
            if name in TEMPLATE_FILES or name.endswith(TEMPLATE_GLOBS):
                shutil.copy2(os.path.join(TEMPLATE, name),
                             os.path.join(OUT, name))
        for key, fn in self.fig_files.items():
            shutil.copy2(os.path.join(FIGURES, fn), os.path.join(OUT, fn))
        path = os.path.join(
            OUT, 'article.tex' if self.target == 'article'
            else 'supplement-S1.tex')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(self.tex))
        return path


def page_count(pdf):
    """Pages without poppler: the log line is authoritative, the page-tree
    count is the check on it."""
    data = open(pdf, 'rb').read()
    return len(re.findall(rb'/Type\s*/Page[^s]', data))


def compile_pdf(latexmk, stem='article'):
    log = os.path.join(OUT, stem + '-build.log')
    tex = stem + '.tex'
    cmd = (['latexmk', '-pdf', '-interaction=nonstopmode', tex]
           if latexmk else
           ['pdflatex', '-interaction=nonstopmode', tex])
    runs = 1 if latexmk else 3      # 3 passes resolve refs, labels and floats
    with open(log, 'w') as fh:
        for _ in range(runs):
            p = subprocess.run(cmd, cwd=OUT, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
            fh.write(p.stdout.decode('utf-8', 'replace'))
    return log


def build_one(target, args):
    """Generate one document and report on it. Returns (ok, tex path)."""
    b = Build(target)
    label = 'article' if target == 'article' else 'Supplement S1'
    try:
        b.load_floats()
        b.front_matter()
        b.sections()
        entries = b.bibliography()
    except BuildError as e:
        print('BUILD STOPPED (%s)\n\n  %s\n' % (label, e))
        return False, None

    path = b.write()
    results = b.checks(entries)
    failed = [m for s, m in results if s == 'FAIL']

    print('--- %s ---' % label)
    print('generated %s (%d lines, %d bytes)'
          % (os.path.relpath(path, ROOT), len(b.tex), os.path.getsize(path)))
    print('floats, in the order the .tex places them:')
    pre = '' if target == 'article' else 'S'
    fign = tabn = 0
    for key in b.emitted_floats:
        if key.startswith('fig:'):
            fign += 1
            print('   Fig. %s%-3d %-22s %s' % (pre, fign, key, b.fig_files[key]))
        else:
            tabn += 1
            print('   Table %s%-3d %-22s' % (pre, tabn, key))
    for status, msg in results:
        print('  %-4s %s' % (status, msg))
    if failed:
        print('  %d CHECK(S) FAILED.' % len(failed))
    return not failed, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compile', action='store_true',
                    help='run pdflatex after generating (needs TeX)')
    ap.add_argument('--latexmk', action='store_true',
                    help='use latexmk instead of three pdflatex passes')
    ap.add_argument('--only', choices=('article', 's1'),
                    help='build just one of the two documents')
    args = ap.parse_args()

    targets = [args.only] if args.only else ['article', 's1']
    ok = True
    paths = []
    for target in targets:
        good, path = build_one(target, args)
        ok = ok and good
        if path:
            paths.append((target, path))
        print()
    if not paths:
        return 1

    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print('bundle: %d files, %.1f MB (limit %d MB per file)'
          % (len(os.listdir(OUT)), size / 1e6, MAX_BYTES // 1024 // 1024))
    if not ok:
        return 1

    if args.compile:
        tool = 'latexmk' if args.latexmk else 'pdflatex'
        if not shutil.which(tool):
            print('\nno TeX on this machine; generation only. Compile where a '
                  'toolchain exists:')
            for _, path in paths:
                print('  %s -interaction=nonstopmode %s   (three passes)'
                      % (tool, os.path.basename(path)))
            return 0
        for target, path in paths:
            stem = os.path.splitext(os.path.basename(path))[0]
            log = compile_pdf(args.latexmk, stem)
            pdf = os.path.join(OUT, stem + '.pdf')
            if not os.path.isfile(pdf):
                print('\n%s produced no PDF; see %s'
                      % (stem, os.path.relpath(log, ROOT)))
                return 1
            text = open(log, encoding='utf-8', errors='replace').read()
            pages = re.findall(r'Output written on .*?\((\d+) pages', text)
            over = re.findall(r'^(Overfull \\[hv]box.*)$', text, re.M)
            big = [x for x in over
                   if float(re.search(r'\(([\d.]+)pt', x).group(1)) > 10.0]
            print('\n%s: %s pages (page tree: %d), %.2f MB'
                  % (stem, pages[-1] if pages else '?', page_count(pdf),
                     os.path.getsize(pdf) / 1e6))
            print('overfull boxes over 10pt: %d of %d' % (len(big), len(over)))
            for line in big[:20]:
                print('   ' + line.strip())
    return 0


if __name__ == '__main__':
    sys.exit(main())
