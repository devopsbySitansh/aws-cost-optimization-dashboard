# ==============================================================
# Outputs — AWS Cost Optimization Dashboard
# ==============================================================

output "sns_topic_arn" {
  description = "ARN of the SNS alert topic"
  value       = module.sns.alert_topic_arn
}

output "cloudwatch_dashboard_url" {
  description = "URL to the CloudWatch dashboard"
  value       = "https://${data.aws_region.current.name}.console.aws.amazon.com/cloudwatch/home#dashboards:name=${var.project_name}-${var.environment}"
}

output "dashboard_iam_policy_arn" {
  description = "ARN of the read-only IAM policy for the dashboard backend"
  value       = aws_iam_policy.dashboard_readonly.arn
}

output "account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "Deployed AWS region"
  value       = data.aws_region.current.name
}
