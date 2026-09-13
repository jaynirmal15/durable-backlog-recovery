# E2b, first attempt — stopped by the cost guard, excluded from the cell

These seven runs are **not part of the reported E2b cell** and must not be
pooled into any statistic. They are kept because deleting the record of an
interrupted attempt would make the campaign look cleaner than it was.

The CloudWatch idle-stop alarm stopped the instance at 04:06 UTC on 2026-09-13,
53 minutes into the attempt, part-way through the third rep at rl=190. Its
threshold was 5% CPU, calibrated against the C=2000 campaigns; E2b draws 3.1-4.1%
at C=400, so a working campaign read as idle. See `../E2B-PLAN.md`.

The search was restarted from the anchor. The reported cell is entirely from the
restarted campaign in `../e2b/`.

| rl | reps here | class |
|---:|---:|---|
| 180 | 3 | SAFE |
| 190 | 1 | SAFE (the point was incomplete when the box stopped) |
| 200 | 3 | UNSAFE |

Where the attempts overlap they agree: rl=180 returned as-measured rho of 0.9442
and 0.9444 on reps 1 and 2 in both. That is a check on the restart, not data.

The eighth run, `e2b-c50-c0-rl190-r2`, was killed mid-flight. It produced no
record, only a partial uncompressed trace, which was left on the instance and
never fetched -- a plain trace beside a complete gzip has silently shadowed a
good one in this project before.
