# Architecture & Deployment Guide

## How It Works — Data Flow

```
AWS Resources (EC2, RDS)
        │  emit metrics every 1 minute
        ▼
   AWS CloudWatch
        │  GetMetricStatistics API
        ▼
   Flask Backend (app.py)
        │  aggregates, calculates recommendations
        ▼
   React Frontend
        │  renders charts, tables, recommendations
        ▼
   User Browser
```

## IAM Permissions Required

The backend needs an IAM role or user with these minimum permissions:

- `cloudwatch:GetMetricData`
- `cloudwatch:GetMetricStatistics`
- `cloudwatch:ListMetrics`
- `cloudwatch:DescribeAlarms`
- `ec2:DescribeInstances`
- `rds:DescribeDBInstances`
- `ce:GetCostAndUsage` (Cost Explorer — optional)

**Best practice:** Use an IAM role attached to your EC2 backend instance, not access keys.

## Deployment Options

### Option A — Local Development (Demo)
1. Run `python scripts/generate_sample_data.py`
2. Set `DEMO_MODE = true` in `frontend/src/App.jsx`
3. `cd frontend && npm run dev`
4. Dashboard runs fully offline with realistic data

### Option B — Real AWS (Production)
1. Deploy Flask backend on EC2 with IAM role attached
2. Set env vars: `AWS_REGION`, `ALERT_THRESHOLD_CPU`
3. Build frontend: `npm run build` → serve `dist/` via Nginx or S3+CloudFront
4. Run Terraform to create CloudWatch alarms and SNS topics

### Option C — Serverless (Advanced)
Replace Flask with AWS Lambda + API Gateway for a fully serverless backend.
Each route in `app.py` becomes a Lambda handler.

## CloudWatch Metric Reference

| Metric | Namespace | Dimension |
|---|---|---|
| EC2 CPU | AWS/EC2 | InstanceId |
| EC2 Network In | AWS/EC2 | InstanceId |
| EC2 Disk Read | AWS/EC2 | InstanceId |
| RDS CPU | AWS/RDS | DBInstanceIdentifier |
| RDS Connections | AWS/RDS | DBInstanceIdentifier |
| RDS Free Storage | AWS/RDS | DBInstanceIdentifier |

## Cost of Running This Dashboard

Estimated AWS costs to operate this dashboard itself:

| Component | Monthly Cost |
|---|---|
| CloudWatch GetMetricStatistics (1000 calls/day) | ~$0.30 |
| SNS notifications (100/month) | ~$0.01 |
| EC2 t3.micro (if self-hosted backend) | ~$8.50 |
| **Total** | **~$9/month** |

Much less than the savings it identifies!
