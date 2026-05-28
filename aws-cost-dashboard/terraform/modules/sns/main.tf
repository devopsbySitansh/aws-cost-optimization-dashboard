# ==============================================================
# Module: SNS Alert Topics & Subscriptions
# ==============================================================

resource "aws_sns_topic" "alerts" {
  name         = "${var.project_name}-cost-alerts-${var.environment}"
  display_name = "AWS Cost Dashboard Alerts"

  tags = {
    Name        = "${var.project_name}-alerts"
    Environment = var.environment
  }
}

# Email subscription for cost alerts
resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Optional: Slack webhook via HTTPS (uncomment if needed)
# resource "aws_sns_topic_subscription" "slack_alert" {
#   topic_arn = aws_sns_topic.alerts.arn
#   protocol  = "https"
#   endpoint  = var.slack_webhook_url
# }

# SNS Topic Policy — allow CloudWatch to publish
resource "aws_sns_topic_policy" "cloudwatch_publish" {
  arn = aws_sns_topic.alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudWatchPublish"
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}

output "alert_topic_arn" {
  description = "ARN of the SNS alert topic"
  value       = aws_sns_topic.alerts.arn
}
