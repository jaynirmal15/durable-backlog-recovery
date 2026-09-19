"""Formatting helpers that report a value at its own cell's resolution.

W2 rule, applied 2026-09-13. The bisection resolves the boundary to 5 rps, so a
utilisation figure is only meaningful to 5/C_measured:

    cells at C >= 1400   resolution 0.0025 to 0.0039   -> three decimals
    E2b, C = 400         resolution 0.0127             -> two decimals

Four decimals are never warranted for a utilisation figure anywhere.

REGISTERED VALUES ARE NEVER PASSED THROUGH HERE. A registration records what was
predicted before the data existed, and re-rounding it after the fact falsifies
the record. Where a report quotes a registered value beside a measured one, the
registered value keeps its original digits and only the measured one is rounded.

vSLO is not a utilisation ratio and is not covered: it is a fraction of violating
seconds, with its own resolution of roughly 1/T_full.
"""


def u(v, coarse=False):
    """A MEASURED utilisation, at its cell's resolution."""
    if v is None:
        return '-'
    return ('%.2f' if coarse else '%.3f') % v


def ud(v, coarse=False):
    """A MEASURED difference of utilisations, signed."""
    if v is None:
        return '-'
    return ('%+.2f' if coarse else '%+.3f') % v


def is_coarse(cell_label):
    """True for cells whose bisection step exceeds 0.01 in utilisation."""
    return 'E2b' in (cell_label or '') or 'C=400' in (cell_label or '')
