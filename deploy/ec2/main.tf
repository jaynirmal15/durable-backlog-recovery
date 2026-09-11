# Single fixed-performance box for the E-series boundary campaign.
#
# It lives in the default VPC on purpose. A dedicated VPC would add a NAT
# gateway at roughly $32/month for no experimental benefit: this instance needs
# outbound access to fetch packages and inbound SSH from one address, nothing
# more. The experiment itself is entirely local to the box.

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Canonical's published Ubuntu 24.04 LTS, resolved at apply time rather than
# pinned to an AMI id, which is region-specific and goes stale.
data "aws_ssm_parameter" "ubuntu" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

resource "aws_key_pair" "runner" {
  key_name   = "rhc-runner"
  public_key = file(pathexpand(var.public_key_path))
}

resource "aws_security_group" "runner" {
  name        = "rhc-runner"
  description = "SSH from one address; all egress. No experiment port is exposed."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from the operator only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    description = "Package and toolchain downloads"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "rhc-runner" }
}

resource "aws_instance" "runner" {
  ami                    = data.aws_ssm_parameter.ubuntu.value
  instance_type          = var.instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.runner.id]
  key_name               = aws_key_pair.runner.key_name

  # Credit specification is meaningless on c6i and would error on a non-burstable
  # type, so it is deliberately absent. The variable validation keeps t-series out.

  root_block_device {
    volume_size           = var.volume_gb
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }

  metadata_options {
    http_tokens   = "required" # IMDSv2 only; the runner records instance type through it
    http_endpoint = "enabled"
  }

  user_data                   = file("${path.module}/user_data.sh")
  user_data_replace_on_change = false # changing bootstrap must not silently rebuild a box mid-campaign

  tags = { Name = "rhc-runner" }

  lifecycle {
    # The instance is stopped and started around runs. Terraform must not treat
    # a stopped box as drift and recreate it, which would destroy its results.
    ignore_changes = [ami]
  }
}

# Account-wide monthly cost alarm. The campaign is roughly 12 hours of
# c6i.2xlarge (about $4) plus the volume, so $50 is a wide margin whose purpose
# is catching a box left running, not normal use.
resource "aws_budgets_budget" "monthly" {
  name         = "rhc-monthly"
  budget_type  = "COST"
  limit_amount = tostring(var.budget_limit_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_notify_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.budget_notify_email]
  }
}
