#!/usr/bin/env python3
"""Count manuscript words under ONE stated convention, because no one had.

The outline's section budgets and each section's self-reported count have never
reconciled -- SS-4 reads 2,400 (budget) / 2,930 (its own header) / 5,167 (raw)
-- for the simple reason that nobody ever wrote down what a "word" counts.
Three different conventions were in use at once. This script picks one, applies
it uniformly, and prints the alternatives beside it so the choice stays visible.

THE CONVENTION, and what it excludes and why:

  counted    body prose below the first '---', including headings, since a
             reader reads them.

  excluded   the draft header block above the first '---'. It is a change log
             addressed to this project, not to a reader, and it is stripped
             before submission.

  excluded   HTML comments. These are the source comments that cite an artefact
             at point of use; the outline says they strip in W6.

  excluded   fenced code blocks. The arithmetic displays in SS-5 are set as
             blocks, and a reader does not read them as prose; they consume
             column inches, which is a LAYOUT cost, not a prose cost.

  excluded   markdown table rows. A table is typeset as a float, not as running
             text. SS-4's Table 1 alone is the difference between 2,930 and 5,167.

"prose" is what the budgets should be read against. "with tables and code" is
the raw figure, reported because it is what drives page count, and page count
is the thing IEEE Access actually cares about.

Usage: python3 scripts/section_wordcount.py [--budgets]
"""
import os
import re
import sys

PAPER = 'paper'

# budget, from paper/OUTLINE.md's structure table
# Re-budgeted at outline v9.6 from the 2026-09-20 measurement, after the ruling
# that the manuscript's length is controlled by the scientific record rather
# than by a planning estimate that was never measured under a defined
# convention. Baseline 18,308 prose words, ~22-23 pages accepted; 20 pages is a
# readability target. These are not targets to write toward -- they record what
# the frozen sections contain.
BUDGETS = {1: 1600, 2: 1400, 3: 1700, 4: 4750, 5: 2750,
           6: 1550, 7: 1350, 8: 1070, 9: 1650, 10: 460}


def split_body(text):
    """Everything below the first '---' line: the header block is a change log."""
    for m in re.finditer(r'^---\s*$', text, re.M):
        return text[m.end():]
    return text


def counts(text):
    body = split_body(text)
    body = re.sub(r'<!--.*?-->', ' ', body, flags=re.S)

    raw = len(body.split())

    without_code = re.sub(r'^```.*?^```', ' ', body, flags=re.S | re.M)
    prose_lines = [ln for ln in without_code.split('\n')
                   if not ln.lstrip().startswith('|')]
    prose = len(' '.join(prose_lines).split())

    return prose, raw


def main():
    rows = []
    for n in range(1, 11):
        path = os.path.join(PAPER, 'section%d.md' % n)
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as fh:
            prose, raw = counts(fh.read())
        rows.append((n, prose, raw, BUDGETS.get(n)))

    print('%-4s %8s %8s %8s %9s   %s' %
          ('sec', 'prose', 'budget', 'delta', 'w/tables', 'status'))
    tp = tr = tb = 0
    for n, prose, raw, budget in rows:
        tp += prose
        tr += raw
        tb += budget or 0
        delta = prose - budget if budget else 0
        flag = ''
        if budget:
            if delta > budget * 0.15:
                flag = 'OVER by %d%%' % round(100.0 * delta / budget)
            elif delta < -budget * 0.25:
                flag = 'under by %d%%' % round(100.0 * -delta / budget)
            else:
                flag = 'within 15%'
        print('%-4d %8d %8s %8s %9d   %s' %
              (n, prose, budget or '-', ('%+d' % delta) if budget else '-',
               raw, flag))
    print('%-4s %8d %8d %8s %9d' % ('all', tp, tb, '%+d' % (tp - tb), tr))
    print()
    print('prose = the budget convention: body below the header, no source')
    print('comments, no code blocks, no table rows.')
    print('w/tables = the same body with tables and code back in; this is what')
    print('drives page count, and page count is what IEEE Access cares about.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
