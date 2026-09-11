# deploy/ — the E-series boundary runner

One fixed-performance EC2 box. The boundary campaign moved here before E1; the
2026-08-18 corpus was measured on a laptop, and the two are **not comparable**.
See the dated entry in `NOTES.md`.

## Why this shape

**`c6i.2xlarge`, never a t-series.** Burstable instances earn and spend CPU
credits. Once the balance runs out the vCPUs are throttled, which changes the
downstream's effective service rate partway through a drain — silently, and in
the middle of the measurement. A `validation` block in `variables.tf` rejects any
`t*` type outright.

8 vCPU matches the laptop's core count so the concurrency arms mean the same
thing; 16 GiB is double the laptop, which removes memory pressure as a variable
at 1024 consumer workers.

**Default VPC.** A dedicated VPC needs a NAT gateway at about $32/month and buys
nothing: the box needs outbound package access and inbound SSH from one address.
The experiment is entirely local to the instance.

**No Elastic IP.** An EIP bills while the instance is stopped. The public
address changes across stop/start; the Makefile resolves it each time.

**IMDSv2 required.** The runner reads its instance type through it and records
it per run.

## Cost

| State | Cost |
|---|---|
| Running | about **$0.34/hr** |
| Stopped | the 50 GB gp3 volume only, about **$4/month** |
| Whole E1 campaign | roughly 12 hours, about **$4** |

**The instance stays stopped when runs are not executing.** `make stop`.

A monthly budget alarm is set at **$50**, notifying at 50% actual and 100%
forecast. Its purpose is catching a box left running, not policing normal use.

## Use

```
make key                       # one-time SSH keypair
make up EMAIL=you@example.com  # create instance + budget alarm
make start                     # before a campaign
make sync                      # push tracked files (never local results/)
make ssh
make stop                      # WHEN THE CAMPAIGN PAUSES
make fetch                     # pull results back
make destroy EMAIL=you@example.com
```

SSH is opened only to the address `make up` saw at apply time. Re-run `make up`
from a new network.

## Pinned versions

`user_data.sh` pins Go and nats-server rather than taking latest. A toolchain
that moves between boundaries puts two different builds in one dataset. Every
run record carries the Go and Docker versions so that is detectable if it
happens anyway.
