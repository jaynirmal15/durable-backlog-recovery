# OPERATIONS — the EC2 boundary runner

Recovery information for the campaign box, committed **because Terraform state
is local and gitignored**. If that laptop is lost, everything needed to find and
stop this instance is here.

## The instance

| | |
|---|---|
| Instance ID | **`i-099dca965768db94a`** |
| Region | **`us-east-1`** |
| Type | `c6i.2xlarge` — 8 vCPU, 16 GiB |
| AMI | Ubuntu 24.04 LTS |
| Account | `296641054943` |
| AWS CLI profile | `medialab` (IAM user `lab-admin`) |
| Name tag | `rhc-runner` |
| SSH key | `~/.ssh/rhc-ec2`, user `ubuntu` |

The public IP **changes on every stop/start** — no Elastic IP is attached, since
one bills while the instance is stopped. Resolve it when you need it:

```bash
aws ec2 describe-instances --profile medialab --region us-east-1 \
  --instance-ids i-099dca965768db94a \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
```

## Cost, and the thing that actually costs money

| State | Cost |
|---|---|
| Running | about **$0.34/hr** |
| Stopped | the 50 GB gp3 volume only, about **$4/month** |
| One full E1 campaign | roughly 12 hours, about **$4** |

The expensive failure is not a runaway experiment. It is **a box left running
after a campaign ends or aborts**, which from the billing side looks identical
to one that is working. Three independent guards exist, in order of how quickly
they act:

1. **CloudWatch alarm `rhc-runner-idle-stop`** — stops the instance after 60
   minutes below 5% CPU (`Maximum` statistic over 12 × 5-minute periods, so a
   single busy minute keeps it alive). Also notifies the `rhc-ops` SNS topic.
2. **AWS Budget `rhc-monthly`** — $50/month, notifying at 50% actual and 100%
   forecast.
3. **You**, with the commands below.

## Stop it

```bash
aws ec2 stop-instances --profile medialab --region us-east-1 \
  --instance-ids i-099dca965768db94a
```

Or, with the Terraform state present: `cd deploy && make stop`

Stopping **preserves the root volume and everything on it**, including results
not yet fetched. Fetch before destroying.

## Start it again

```bash
aws ec2 start-instances --profile medialab --region us-east-1 \
  --instance-ids i-099dca965768db94a
```

## Fetch results before tearing anything down

```bash
IP=$(aws ec2 describe-instances --profile medialab --region us-east-1 \
      --instance-ids i-099dca965768db94a \
      --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
rsync -az -e "ssh -i ~/.ssh/rhc-ec2" ubuntu@$IP:rhc/results/ ./results/
```

## Destroy everything

With Terraform state: `cd deploy && make destroy EMAIL=...`

Without it — the four resources, by hand. **Terminating destroys the volume and
every unfetched result.**

```bash
aws ec2 terminate-instances --profile medialab --region us-east-1 \
  --instance-ids i-099dca965768db94a
aws ec2 delete-security-group --profile medialab --region us-east-1 \
  --group-name rhc-runner          # after the instance is terminated
aws ec2 delete-key-pair --profile medialab --region us-east-1 --key-name rhc-runner
aws cloudwatch delete-alarms --profile medialab --region us-east-1 \
  --alarm-names rhc-runner-idle-stop
aws budgets delete-budget --profile medialab \
  --account-id 296641054943 --budget-name rhc-monthly
aws sns delete-topic --profile medialab --region us-east-1 \
  --topic-arn arn:aws:sns:us-east-1:296641054943:rhc-ops
```

## Finding it if this file is all you have

```bash
aws ec2 describe-instances --profile medialab --region us-east-1 \
  --filters "Name=tag:Project,Values=durable-backlog-recovery" \
  --query 'Reservations[].Instances[].{id:InstanceId,state:State.Name,type:InstanceType}' \
  --output table
```

Every resource carries `Project=durable-backlog-recovery` and
`Purpose=paper2-E-series-boundary-campaign` through Terraform default tags.

## Running a campaign

The campaign script lives at `~/campaign.sh` on the instance and logs to
`~/campaign.log`. It writes `~/.done-<arm>-<REGIME>` as each boundary finishes
and `~/.done-ALL` at the end; a watcher on the laptop fetches and pushes on
those markers. **Git credentials are deliberately not on the instance.**

Check progress:

```bash
ssh -i ~/.ssh/rhc-ec2 ubuntu@$IP 'tail -20 ~/campaign.log; ls ~/.done-*'
```
