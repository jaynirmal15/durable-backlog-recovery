output "instance_id" {
  description = "Used by the start/stop targets in deploy/Makefile."
  value       = aws_instance.runner.id
}

output "public_ip" {
  description = "Changes on every stop/start, since no Elastic IP is attached (one would bill while stopped)."
  value       = aws_instance.runner.public_ip
}

output "ssh" {
  description = "Ready-made SSH command."
  value       = "ssh -i ~/.ssh/rhc-ec2 ubuntu@${aws_instance.runner.public_ip}"
}

output "hourly_cost_note" {
  value = "c6i.2xlarge on-demand us-east-1 is about $0.34/hr while RUNNING. Stopped, only the ${var.volume_gb} GB gp3 volume bills (about $4/month)."
}
