# ==============================================================
# Variables — AWS Cost Optimization Dashboard
# ==============================================================

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "cost-dashboard"
}

variable "environment" {
  description = "Deployment environment (dev / staging / production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "alert_email" {
  description = "Email address to receive CloudWatch alarm notifications"
  type        = string
}

variable "cpu_alarm_threshold" {
  description = "CPU utilization % below which an EC2 instance is flagged as underutilized"
  type        = number
  default     = 20

  validation {
    condition     = var.cpu_alarm_threshold > 0 && var.cpu_alarm_threshold <= 100
    error_message = "CPU threshold must be between 1 and 100."
  }
}

variable "ec2_instance_ids" {
  description = "List of EC2 instance IDs to monitor"
  type        = list(string)
  default     = []
}

variable "rds_instance_ids" {
  description = "List of RDS instance identifiers to monitor"
  type        = list(string)
  default     = []
}

variable "alarm_evaluation_periods" {
  description = "Number of periods CloudWatch evaluates before triggering alarm"
  type        = number
  default     = 3
}

variable "alarm_period_seconds" {
  description = "Period in seconds for each CloudWatch alarm evaluation"
  type        = number
  default     = 86400  # 24 hours
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
