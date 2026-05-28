# ==============================================================
# Module: CloudWatch Alarms & Dashboard
# ==============================================================

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "EC2 CPU Utilization (All Monitored Instances)"
          period = 3600
          stat   = "Average"
          view   = "timeSeries"
          metrics = [
            for id in var.ec2_instance_ids : ["AWS/EC2", "CPUUtilization", "InstanceId", id]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "RDS CPU Utilization"
          period = 3600
          stat   = "Average"
          view   = "timeSeries"
          metrics = [
            for id in var.rds_instance_ids : ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", id]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "EC2 Network In/Out"
          period = 3600
          stat   = "Sum"
          view   = "timeSeries"
          metrics = flatten([
            for id in var.ec2_instance_ids : [
              ["AWS/EC2", "NetworkIn", "InstanceId", id],
              ["AWS/EC2", "NetworkOut", "InstanceId", id]
            ]
          ])
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "RDS Database Connections"
          period = 3600
          stat   = "Average"
          view   = "timeSeries"
          metrics = [
            for id in var.rds_instance_ids : ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", id]
          ]
        }
      }
    ]
  })
}

# ==============================================================
# EC2 Low CPU Alarms (one per instance)
# ==============================================================

resource "aws_cloudwatch_metric_alarm" "ec2_low_cpu" {
  for_each = toset(var.ec2_instance_ids)

  alarm_name          = "${var.project_name}-ec2-low-cpu-${each.key}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.alarm_evaluation_periods
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = var.alarm_period_seconds
  statistic           = "Average"
  threshold           = var.cpu_alarm_threshold

  dimensions = {
    InstanceId = each.key
  }

  alarm_description = "EC2 instance ${each.key} CPU below ${var.cpu_alarm_threshold}% — possible overprovisioning"
  alarm_actions     = [var.sns_topic_arn]
  ok_actions        = [var.sns_topic_arn]

  tags = {
    Name        = "${var.project_name}-ec2-low-cpu-${each.key}"
    Environment = var.environment
  }
}

# ==============================================================
# RDS Low CPU Alarms
# ==============================================================

resource "aws_cloudwatch_metric_alarm" "rds_low_cpu" {
  for_each = toset(var.rds_instance_ids)

  alarm_name          = "${var.project_name}-rds-low-cpu-${each.key}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.alarm_evaluation_periods
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = var.alarm_period_seconds
  statistic           = "Average"
  threshold           = var.cpu_alarm_threshold

  dimensions = {
    DBInstanceIdentifier = each.key
  }

  alarm_description = "RDS instance ${each.key} CPU below ${var.cpu_alarm_threshold}% — consider downsizing"
  alarm_actions     = [var.sns_topic_arn]

  tags = {
    Name        = "${var.project_name}-rds-low-cpu-${each.key}"
    Environment = var.environment
  }
}

# ==============================================================
# RDS High Storage Alarm
# ==============================================================

resource "aws_cloudwatch_metric_alarm" "rds_low_storage" {
  for_each = toset(var.rds_instance_ids)

  alarm_name          = "${var.project_name}-rds-low-storage-${each.key}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 86400
  statistic           = "Minimum"
  threshold           = 5368709120  # 5 GB in bytes

  dimensions = {
    DBInstanceIdentifier = each.key
  }

  alarm_description = "RDS instance ${each.key} free storage below 5GB"
  alarm_actions     = [var.sns_topic_arn]
}
