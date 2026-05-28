# ==============================================================
# AWS Cost Optimization Dashboard — Terraform Root Config
# ==============================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment for remote state (recommended for production)
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "cost-dashboard/terraform.tfstate"
  #   region = "ap-south-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ==============================================================
# Data Sources
# ==============================================================

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# ==============================================================
# Module: CloudWatch Alarms & Dashboards
# ==============================================================

module "cloudwatch" {
  source = "./modules/cloudwatch"

  project_name        = var.project_name
  environment         = var.environment
  cpu_alarm_threshold = var.cpu_alarm_threshold
  sns_topic_arn       = module.sns.alert_topic_arn

  ec2_instance_ids = var.ec2_instance_ids
  rds_instance_ids = var.rds_instance_ids
}

# ==============================================================
# Module: SNS Alerts
# ==============================================================

module "sns" {
  source = "./modules/sns"

  project_name  = var.project_name
  environment   = var.environment
  alert_email   = var.alert_email
}

# ==============================================================
# Module: EC2 Monitoring IAM Role
# ==============================================================

module "ec2_monitoring" {
  source = "./modules/ec2_monitoring"

  project_name = var.project_name
  environment  = var.environment
  account_id   = data.aws_caller_identity.current.account_id
}

# ==============================================================
# IAM Policy — Read-Only CloudWatch Access for Dashboard
# ==============================================================

resource "aws_iam_policy" "dashboard_readonly" {
  name        = "${var.project_name}-dashboard-readonly-${var.environment}"
  description = "Read-only access for cost dashboard to CloudWatch and Cost Explorer"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CloudWatchReadOnly"
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:DescribeAlarms",
          "cloudwatch:DescribeAlarmsForMetric"
        ]
        Resource = "*"
      },
      {
        Sid    = "EC2ReadOnly"
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus",
          "ec2:DescribeInstanceTypes"
        ]
        Resource = "*"
      },
      {
        Sid    = "RDSReadOnly"
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:ListTagsForResource"
        ]
        Resource = "*"
      },
      {
        Sid    = "CostExplorerReadOnly"
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetRightsizingRecommendation",
          "ce:GetCostForecast"
        ]
        Resource = "*"
      }
    ]
  })
}
