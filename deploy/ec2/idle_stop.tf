# Stop the instance when it has been idle for an hour.
#
# The campaign is long and unattended, and the failure mode that actually costs
# money is not a runaway experiment -- it is a box left running after one
# finishes or aborts. An aborted campaign looks exactly like a finished one from
# the billing side.
#
# 5% CPU over 60 minutes is well clear of a real run: even between probes the
# harness is settling, and a boundary run drives 8 vCPU hard. An idle Ubuntu box
# sits near 0%.
resource "aws_cloudwatch_metric_alarm" "idle_stop" {
  alarm_name        = "rhc-runner-idle-stop"
  alarm_description = "Stop rhc-runner after 60 minutes below 5% CPU. Guards against a box left running after a campaign ends or aborts."

  namespace   = "AWS/EC2"
  metric_name = "CPUUtilization"
  statistic   = "Maximum" # Maximum, not Average: a single busy minute in the
  # hour means the box is working and must not be stopped.

  period              = 300 # 5-minute samples...
  evaluation_periods  = 12  # ...12 of them = 60 minutes
  datapoints_to_alarm = 12  # every one must be idle
  threshold           = 5
  comparison_operator = "LessThanThreshold"

  # Without this, a stopped instance reports no data, the alarm goes INSUFFICIENT
  # and then re-alarms on the next start. notBreaching keeps it quiet.
  treat_missing_data = "notBreaching"

  dimensions = { InstanceId = aws_instance.runner.id }

  alarm_actions = [
    "arn:aws:automate:${var.region}:ec2:stop",
    aws_sns_topic.ops.arn,
  ]

  tags = { Name = "rhc-runner-idle-stop" }
}

resource "aws_sns_topic" "ops" {
  name = "rhc-ops"
}

resource "aws_sns_topic_subscription" "ops_email" {
  topic_arn = aws_sns_topic.ops.arn
  protocol  = "email"
  endpoint  = var.budget_notify_email
}
