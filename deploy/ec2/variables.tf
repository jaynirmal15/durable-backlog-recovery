variable "region" {
  description = "AWS region. us-east-1 matches the existing lab account."
  type        = string
  default     = "us-east-1"
}

variable "profile" {
  description = "AWS CLI profile. medialab maps to the lab-admin IAM user."
  type        = string
  default     = "medialab"
}

variable "instance_type" {
  description = <<-EOT
    Fixed-performance instance. NOT a t-series: burstable CPU credits throttle
    once the balance is exhausted, which would silently change service rate
    partway through a drain and corrupt exactly the timing this campaign
    measures. c6i.2xlarge is 8 vCPU / 16 GiB, matching the laptop's core count
    while giving twice its memory.
  EOT
  type        = string
  default     = "c6i.2xlarge"

  validation {
    condition     = !startswith(var.instance_type, "t")
    error_message = "Burstable t-series instances corrupt timing measurements. Use a fixed-performance type."
  }
}

variable "volume_gb" {
  description = "Root volume size. Traces are 35-85 MB per run and a full disk truncates them silently."
  type        = number
  default     = 50
}

variable "allowed_ssh_cidr" {
  description = "CIDR permitted to reach SSH. Defaults to nothing; set it to your own address."
  type        = string
}

variable "public_key_path" {
  description = "Path to the SSH public key placed on the instance."
  type        = string
  default     = "~/.ssh/rhc-ec2.pub"
}

variable "budget_limit_usd" {
  description = "Monthly budget for the account. The campaign itself is about 12 hours of c6i.2xlarge."
  type        = number
  default     = 50
}

variable "budget_notify_email" {
  description = "Where budget alarms go. Required: an alarm with no subscriber is not an alarm."
  type        = string
}
