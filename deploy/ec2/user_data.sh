#!/bin/bash
# Bootstrap for the E-series boundary runner.
#
# Pinned rather than "latest" wherever a version can move underneath a campaign:
# a Go or Docker upgrade between boundaries would put two different toolchains in
# one dataset, and every run record carries these versions precisely so that is
# detectable.
set -euxo pipefail

GO_VERSION=1.25.3
NATS_VERSION=2.10.22

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  git curl ca-certificates build-essential jq python3 unzip \
  docker.io

systemctl enable --now docker
usermod -aG docker ubuntu

# Go from upstream: the repo needs go 1.25.3 and Ubuntu 24.04 ships older.
curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -o /tmp/go.tgz
rm -rf /usr/local/go
tar -C /usr/local -xzf /tmp/go.tgz
rm /tmp/go.tgz
echo 'export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH' > /etc/profile.d/go.sh
chmod 0644 /etc/profile.d/go.sh

# nats-server binary, so the harness does not depend on pulling a container
# image mid-campaign.
curl -fsSL "https://github.com/nats-io/nats-server/releases/download/v${NATS_VERSION}/nats-server-v${NATS_VERSION}-linux-amd64.tar.gz" -o /tmp/nats.tgz
tar -C /tmp -xzf /tmp/nats.tgz
install -m 0755 "/tmp/nats-server-v${NATS_VERSION}-linux-amd64/nats-server" /usr/local/bin/nats-server
rm -rf /tmp/nats.tgz "/tmp/nats-server-v${NATS_VERSION}-linux-amd64"

# Keep the box from sleeping or throttling anything on a timer.
systemctl disable --now unattended-upgrades  || true
systemctl disable --now apt-daily.timer      || true
systemctl disable --now apt-daily-upgrade.timer || true

mkdir -p /home/ubuntu/rhc
chown -R ubuntu:ubuntu /home/ubuntu/rhc

# Marker the Makefile waits on, so a run never starts against a half-built box.
touch /var/lib/cloud/rhc-bootstrap-complete
