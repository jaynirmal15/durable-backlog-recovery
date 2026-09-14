#!/usr/bin/env python3
"""Find reported numbers carrying more significant figures than the data supports.

Rules applied, from the W2 brief:
  utilisation ratios      two significant figures maximum
  delta/S percentages     9.26% and 1.85%, same precision
  four-decimal utilisation figures flagged wherever they appear

A "utilisation figure" is a decimal in [0.80, 1.05] with three or more decimal
places appearing in committed prose, a caption or a generated report. That band
covers every rho and effective-utilisation value the study reports and excludes
overheads, fractions of cap and p-values.

Reports only. Nothing is rewritten.

Usage: python3 scripts/precision_sweep.py
"""
import collections
import glob
import os
import re
import sys

TARGETS = sorted(glob.glob('results/*.md') + glob.glob('figures/*.md')
                 + ['PRE-REGISTRATION.md'] + glob.glob('scripts/*.py'))
NUM = re.compile(r'(?<![\d.])(0\.\d{3,}|1\.0\d{2,})(?![\d])')
PCT = re.compile(r'(?<![\d.])(\d{1,2}\.\d{1,3})\s*%')


def main():
    util = collections.defaultdict(list)
    pcts = collections.defaultdict(list)
    for path in TARGETS:
        if not os.path.exists(path) or 'REVIEWER-RESPONSE' in path:
            continue
        for i, line in enumerate(open(path, errors='ignore'), 1):
            for m in NUM.finditer(line):
                v = float(m.group(1))
                if 0.80 <= v <= 1.05:
                    dec = len(m.group(1).split('.')[1])
                    if dec >= 3:
                        util[path].append((i, m.group(1), dec, line.strip()[:96]))
            for m in PCT.finditer(line):
                if len(m.group(1).split('.')[1]) >= 2:
                    pcts[path].append((i, m.group(1) + '%', line.strip()[:96]))

    print('=== utilisation figures with 3+ decimal places (band 0.80-1.05) ===')
    print()
    tot = 0
    for path in sorted(util):
        vals = util[path]
        tot += len(vals)
        four = sum(1 for v in vals if v[2] >= 4)
        print('%-44s %3d occurrences (%d at four decimals)' % (path, len(vals), four))
    print()
    print('total: %d occurrences across %d files' % (tot, len(util)))

    print()
    print('=== the distinct values involved ===')
    distinct = collections.Counter()
    for vals in util.values():
        for _, s, dec, _ in vals:
            distinct[s] += 1
    print('%-10s %6s  %s' % ('value', 'count', 'two-sig-fig form'))
    for s, n in sorted(distinct.items(), key=lambda kv: -kv[1])[:24]:
        v = float(s)
        print('%-10s %6d  %s' % (s, n, '%.2g' % v))
    print('(%d distinct values in total)' % len(distinct))

    print()
    print('=== percentages with 2+ decimal places ===')
    for path in sorted(pcts):
        seen = collections.Counter(p[1] for p in pcts[path])
        print('%-44s %s' % (path, ', '.join('%s x%d' % (k, v)
                                            for k, v in seen.most_common(6))))

    print()
    print('=== delta/S percentages specifically ===')
    for path in sorted(set(TARGETS)):
        if not os.path.exists(path):
            continue
        for i, line in enumerate(open(path, errors='ignore'), 1):
            if re.search(r'9\.3%|9\.26%|1\.85%|1\.852%|9\.260%', line):
                print('  %s:%d  %s' % (path, i, line.strip()[:100]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
