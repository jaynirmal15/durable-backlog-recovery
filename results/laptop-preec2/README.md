# Laptop runs, superseded before E1 began

Three runs at the C0 / 10-server anchor (rl=840, n=3) and one aborted run at
rl=925, measured on the laptop (MacBookPro15,2, 8 cores, 8 GiB) on 2026-09-11
before the campaign moved to EC2.

All three anchor runs classified SAFE (vSLO 0.0000 / 0.0000 / 0.0000, achieved
rho 0.9124, tDrain 148 s). They are retained because runs are never deleted,
and they are kept out of `results/` proper for one reason:

**They are not E1 data and must not be compared with E1 results.** E1 runs on
EC2. Mixing measurements across platforms would reintroduce exactly the kind of
uncontrolled variable this project keeps having to withdraw findings over. No
cross-platform claim is made from these runs, here or anywhere else.

They also predate continuous host-load sampling, so they carry a start-only
load reading, which cannot detect load climbing during a run.
