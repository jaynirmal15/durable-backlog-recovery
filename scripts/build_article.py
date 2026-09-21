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
EXPECT_FIGURES = 6                  # ASSEMBLY-SPEC.md Draft 2, review ruling A
EXPECT_TABLES = 8
EXPECT_EQUATIONS = 8

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
    'c / S': r'c \,/\, S',
    '50 · S': r'50 \cdot S',
    'c/(S+δ)': r'c/(S + \delta)',
    'c / (S + δ)': r'c \,/\, (S + \delta)',
    '50 · (S + δ)': r'50 \cdot (S + \delta)',
    'C_config · S': r'C_{\mathrm{config}} \cdot S',
    'δ = 0.463': r'\delta = 0.463',
    '[ρ_safe, 1]': r'[\rho_{\mathrm{safe}},\, 1]',
    'C_staffed = C_config': r'C_{\mathrm{staffed}} = C_{\mathrm{config}}',
    'C_measured / C_config': r'C_{\mathrm{measured}} \,/\, C_{\mathrm{config}}',
    'ceil(C_config · S)': r'\lceil C_{\mathrm{config}} \cdot S \rceil',
    'c = ceil(C·S)': r'c = \lceil C \cdot S \rceil',
    '[R_lastSAFE, R_firstNonSAFE]':
        r'[R_{\mathrm{lastSAFE}},\, R_{\mathrm{firstNonSAFE}}]',
    'ρ_eff,safe = R_ach,lastSAFE / C_measured':
        r'\rho_{\mathrm{eff,safe}} = R_{\mathrm{ach,lastSAFE}} \,/\,'
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
    '-0.006': r'-0.006',
    'h = (ρ*_E2b − ρ10) / D':
        r'h = (\rho^{*}_{\mathrm{E2b}} - \rho_{10}) \,/\, D',
    'h = (0.98 − 0.9137) / 0.0689 = +0.980':
        r'h = (0.98 - 0.9137) \,/\, 0.0689 = +0.980',
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

def code_span(span):
    """A backtick span, by explicit map. Neither class -> stop."""
    if span in MATH:
        return '$' + MATH[span] + '$'
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
                      lambda m: park(r'\textbf{'
                                     + inline(m.group(1), True, eqs, shelf)
                                     + '}'),
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
    return re.sub('\x00(\\d+)\x00', lambda m: shelf[int(m.group(1))], text)


# --------------------------------------------------------------------------
# Block conversion
# --------------------------------------------------------------------------

def table(lines, key, caption, wide=True):
    """A markdown pipe table -> table* with its caption ABOVE, per IEEE style."""
    rows = [l for l in lines if l.strip().startswith('|')]
    if len(rows) < 2:
        raise BuildError('table %s has no separator row' % key)

    def cells(row):
        return [c.strip() for c in row.strip().strip('|').split('|')]

    header, sep, data = cells(rows[0]), cells(rows[1]), [cells(r) for r in rows[2:]]
    align = ''
    for s in sep:
        if not re.fullmatch(r':?-{2,}:?', s):
            raise BuildError('table %s separator cell %r is not an alignment'
                             % (key, s))
        align += 'r' if s.endswith(':') and not s.startswith(':') else 'l'
    env = 'table*' if wide else 'table'
    out = [r'\begin{%s}[!t]' % env, r'\caption{%s}' % inline(caption),
           r'\label{%s}' % key, r'\centering',
           r'\begin{tabular}{%s}' % align, r'\hline']
    out.append(' & '.join(r'\textbf{%s}' % inline(h, True) for h in header)
               + r' \\ \hline')
    for row in data:
        if len(row) != len(header):
            raise BuildError('table %s: a row has %d cells, the header has %d'
                             % (key, len(row), len(header)))
        out.append(' & '.join(inline(c, keep_bold=True) for c in row) + r' \\')
    out += [r'\hline', r'\end{tabular}', r'\end{%s}' % env]
    return out


def figure(key, filename, caption):
    return [r'\begin{figure*}[!t]', r'\centering',
            r'\includegraphics[width=\textwidth]{%s}' % filename,
            r'\caption{%s}' % inline(caption), r'\label{%s}' % key,
            r'\end{figure*}']


# --------------------------------------------------------------------------
# The build
# --------------------------------------------------------------------------

class Build(object):

    def __init__(self):
        self.tex = []
        self.equations = []
        self.conversions = []
        self.emitted_floats = []
        self.captions = {}
        self.fig_files = {}
        self.file_tables = {}
        self.pending = {}

    # -- inputs -----------------------------------------------------------
    def load_floats(self):
        caps = read(os.path.join(FIGURES, 'CAPTIONS.md'))
        self.captions.update(article_blocks(caps, 'caption'))
        for m in re.finditer(
                r'^[ \t]*<!--[ \t]*figure:(fig:[A-Za-z0-9._-]+):([^ \t>]+)'
                r'[ \t]*-->[ \t]*$', caps, re.M):
            path = os.path.join(FIGURES, m.group(2))
            if not os.path.isfile(path):
                raise BuildError('figure %s binds to %s, which is missing'
                                 % (m.group(1), m.group(2)))
            self.fig_files[m.group(1)] = m.group(2)

        for name in sorted(os.listdir(FIGURES)):
            if not name.startswith('T') or not name.endswith('.md'):
                continue
            text = read(os.path.join(FIGURES, name))
            lines = text.split('\n')
            for m in re.finditer(
                    r'^[ \t]*<!--[ \t]*table:(tab:[A-Za-z0-9._-]+)[ \t]*-->'
                    r'[ \t]*$', text, re.M):
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
                self.file_tables[key] = block

        for sec in range(1, 11):
            name = 'section%d.md' % sec
            text = read(os.path.join(PAPER, name))
            self.captions.update(article_blocks(text, 'caption'))
            # Section tables are collected here, NOT emitted where their
            # marker sits. LaTeX numbers floats by position in the source, so
            # emitting a table at its marker printed Table 1 for the
            # resolution table: tab:amendments is first REFERENCED at
            # section4.md:85 but its markup sits at line 460, after the
            # reference to tab:resolution. Every float is now placed at its
            # first reference, which is what makes the printed numbers equal
            # the ruling's order of first appearance.
            lines = text.split('\n')
            for m in re.finditer(
                    r'^[ \t]*<!--[ \t]*table:(tab:[A-Za-z0-9._-]+)[ \t]*-->'
                    r'[ \t]*$', text, re.M):
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
                if key in self.file_tables:
                    raise BuildError('table %s is marked in two places' % key)
                self.file_tables[key] = block

    # -- front matter -----------------------------------------------------
    def front_matter(self):
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
    def sections(self):
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
                self.tex += [r'{\footnotesize\begin{alltt}'] + \
                            [''.join(UNICODE.get(ch, ch) if ord(ch) > 127
                                     else ch for ch in ln) for ln in block] + \
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
        m = re.match(r'<!--\s*(table:tab:[A-Za-z0-9._-]+)\s*-->', comment)
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

        want('<!--' not in tex, 'no HTML comment survives into the .tex')
        want('[@' not in tex, 'no [@ marker survives into the .tex')
        want(nfig == EXPECT_FIGURES,
             'figures: %d, the ruling says %d' % (nfig, EXPECT_FIGURES))
        want(ntab == EXPECT_TABLES,
             'tables: %d, the ruling says %d' % (ntab, EXPECT_TABLES))
        want(len(self.equations) == EXPECT_EQUATIONS,
             'equations: %d, the source has %d'
             % (len(self.equations), EXPECT_EQUATIONS))
        want(sorted(self.equations) == list(range(1, EXPECT_EQUATIONS + 1)),
             'equation numbers are 1..%d with none missing' % EXPECT_EQUATIONS)
        for key in self.emitted_floats:
            want(tex.count(r'\ref{%s}' % key) >= 1,
                 'float %s is referenced in the prose' % key)
            want(tex.count(r'\label{%s}' % key) == 1,
                 'float %s has exactly one label' % key)
        unref = sorted(n for n in self.equations if n not in EQ_REFERENCED)
        want(not unref,
             'every numbered equation is referenced in the prose'
             + ('' if not unref else
                ' -- (%s) %s not'
                % (', '.join(str(n) for n in unref),
                   'is' if len(unref) == 1 else 'are')))

        # The % parity check the spec asks for by name: an unescaped percent
        # silently deletes the rest of its line, with no error anywhere.
        src = ''
        for sec in range(1, 11):
            src += COMMENT_RE.sub('', body_of(
                read(os.path.join(PAPER, 'section%d.md' % sec))))
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
        path = os.path.join(OUT, 'article.tex')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(self.tex))
        return path


def page_count(pdf):
    """Pages without poppler: the log line is authoritative, the page-tree
    count is the check on it."""
    data = open(pdf, 'rb').read()
    return len(re.findall(rb'/Type\s*/Page[^s]', data))


def compile_pdf(latexmk):
    log = os.path.join(OUT, 'build.log')
    cmd = (['latexmk', '-pdf', '-interaction=nonstopmode', 'article.tex']
           if latexmk else
           ['pdflatex', '-interaction=nonstopmode', 'article.tex'])
    runs = 1 if latexmk else 3      # 3 passes resolve refs, labels and floats
    with open(log, 'w') as fh:
        for _ in range(runs):
            p = subprocess.run(cmd, cwd=OUT, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
            fh.write(p.stdout.decode('utf-8', 'replace'))
    return log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compile', action='store_true',
                    help='run pdflatex after generating (needs TeX)')
    ap.add_argument('--latexmk', action='store_true',
                    help='use latexmk instead of three pdflatex passes')
    args = ap.parse_args()

    b = Build()
    try:
        b.load_floats()
        b.front_matter()
        b.sections()
        entries = b.bibliography()
    except BuildError as e:
        print('BUILD STOPPED\n\n  %s\n' % e)
        return 1

    path = b.write()
    results = b.checks(entries)
    failed = [m for s, m in results if s == 'FAIL']

    print('generated %s (%d lines, %d bytes)'
          % (os.path.relpath(path, ROOT), len(b.tex), os.path.getsize(path)))
    print('floats, in the order the .tex places them:')
    fign = tabn = 0
    for key in b.emitted_floats:
        if key.startswith('fig:'):
            fign += 1
            print('   Fig. %-2d %-22s %s' % (fign, key, b.fig_files[key]))
        else:
            tabn += 1
            print('   Table %-2d %-22s' % (tabn, key))
    print('checks:')
    for status, msg in results:
        print('  %-4s %s' % (status, msg))

    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print('bundle: %d files, %.1f MB (limit %d MB per file)'
          % (len(os.listdir(OUT)), size / 1e6, MAX_BYTES // 1024 // 1024))

    if failed:
        print('\n%d CHECK(S) FAILED.\n' % len(failed))
        return 1

    if args.compile:
        if not shutil.which('latexmk' if args.latexmk else 'pdflatex'):
            print('\nno TeX on this machine; generation only. '
                  'Compile where a toolchain exists.')
            return 0
        log = compile_pdf(args.latexmk)
        pdf = os.path.join(OUT, 'article.pdf')
        if not os.path.isfile(pdf):
            print('\ncompile produced no PDF; see %s'
                  % os.path.relpath(log, ROOT))
            return 1
        text = open(log, encoding='utf-8', errors='replace').read()
        m = re.findall(r'Output written on .*?\((\d+) pages', text)
        over = re.findall(r'^(Overfull \\[hv]box.*)$', text, re.M)
        print('\nPDF: %s pages (page tree: %d), %.2f MB'
              % (m[-1] if m else '?', page_count(pdf),
                 os.path.getsize(pdf) / 1e6))
        print('overfull boxes: %d' % len(over))
        for line in over[:20]:
            print('   ' + line.strip())
    return 0


if __name__ == '__main__':
    sys.exit(main())
