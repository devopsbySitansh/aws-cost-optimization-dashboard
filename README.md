# ☁️ AWS Cost Optimization Dashboard

> **Identify overprovisioned AWS resources and reduce infrastructure costs — automatically.**

[![AWS](https://img.shields.io/badge/AWS-CloudWatch%20%7C%20EC2%20%7C%20RDS-FF9900?style=flat&logo=amazonaws&logoColor=white)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?style=flat&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Python](https://img.shields.io/badge/Python-Flask%20API-3776AB?style=flat&logo=python&logoColor=white)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-Dashboard%20UI-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📸 Dashboard Preview

![Dashboard Overview](docs/screenshots/dashboard-preview.png)

> *Real-time cost visibility across EC2 and RDS — with actionable optimization recommendations.*

---

## 🎯 Problem Statement

AWS bills can spiral out of control when:
- EC2 instances run at **<20% CPU** for weeks (overprovisioned)
- RDS instances are sized for peak loads that never occur
- Idle resources accumulate silently across regions
- Teams lack a **centralized view** of utilization vs. cost

This dashboard solves that by aggregating CloudWatch metrics, flagging underutilized resources, and generating **right-sizing recommendations** — all in one place.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **EC2 Monitoring** | CPU, Memory, Network utilization across all instances |
| 🗄️ **RDS Monitoring** | CPU, connections, storage utilization per DB instance |
| 💡 **Cost Recommendations** | AI-driven right-sizing suggestions with estimated savings |
| 📈 **Utilization Graphs** | 7-day / 30-day trend charts via CloudWatch metrics |
| 🔔 **SNS Alert Integration** | Threshold-based alerts to email/Slack/PagerDuty |
| 🏗️ **Infrastructure Overview** | Resource inventory across regions |
| 💰 **Cost Breakdown** | Per-service and per-instance cost attribution |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cloud                                 │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────────┐  │
│  │  EC2     │───▶│          │    │   CloudWatch Dashboards   │  │
│  │Instances │    │CloudWatch│───▶│   (Metrics & Alarms)     │  │
│  └──────────┘    │ Metrics  │    └──────────────────────────┘  │
│                  │          │              │                     │
│  ┌──────────┐    │          │              ▼                     │
│  │  RDS     │───▶│          │    ┌──────────────────────────┐  │
│  │Instances │    └──────────┘    │     SNS Topics           │  │
│  └──────────┘          │         │  (Email/Slack Alerts)    │  │
│                         │         └──────────────────────────┘  │
│                         ▼                                        │
│                ┌──────────────────┐                             │
│                │  Lambda Function  │  (optional serverless      │
│                │  OR EC2 Backend  │   or self-hosted)           │
│                └────────┬─────────┘                             │
└─────────────────────────│───────────────────────────────────────┘
                           │  REST API
                           ▼
               ┌───────────────────────┐
               │   Flask Backend API   │
               │   (Python 3.11)       │
               │   /api/ec2/metrics    │
               │   /api/rds/metrics    │
               │   /api/recommendations│
               └───────────┬───────────┘
                            │  JSON
                            ▼
               ┌───────────────────────┐
               │   React Dashboard     │
               │   (Tailwind CSS)      │
               │   Recharts / Chart.js │
               └───────────────────────┘
```

### AWS Services Used

| Service | Purpose |
|---|---|
| **EC2** | Compute instances being monitored |
| **RDS** | Managed database instances |
| **CloudWatch** | Metrics collection, alarms, dashboards |
| **SNS** | Push alerts to email/Slack/PagerDuty |
| **IAM** | Least-privilege roles for metric access |
| **Terraform** | Infrastructure provisioning as code |

---

## 📁 Project Structure

```
aws-cost-optimization-dashboard/
│
├── 📄 README.md                    # You are here
├── 📄 .gitignore
│
├── 🎨 frontend/                    # React dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── components/
│   │       ├── Dashboard.jsx       # Main layout
│   │       ├── EC2Monitor.jsx      # EC2 utilization panel
│   │       ├── RDSMonitor.jsx      # RDS monitoring panel
│   │       ├── CostRecommendations.jsx
│   │       ├── AlertsPanel.jsx
│   │       └── charts/
│   │           ├── UtilizationChart.jsx
│   │           └── CostTrendChart.jsx
│   ├── package.json
│   └── tailwind.config.js
│
├── 🐍 backend/                     # Flask REST API
│   ├── app.py                      # Main Flask app
│   ├── config.py                   # AWS / app config
│   ├── requirements.txt
│   └── routes/
│       ├── ec2_routes.py
│       ├── rds_routes.py
│       └── recommendations.py
│
├── 🏗️ terraform/                   # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars.example
│   └── modules/
│       ├── cloudwatch/             # CloudWatch alarms & dashboards
│       │   ├── main.tf
│       │   └── variables.tf
│       ├── sns/                    # SNS topics & subscriptions
│       │   ├── main.tf
│       │   └── variables.tf
│       └── ec2_monitoring/         # EC2 IAM + monitoring setup
│           ├── main.tf
│           └── variables.tf
│
├── 📚 docs/
│   ├── architecture.md
│   ├── deployment-guide.md
│   └── screenshots/
│       └── dashboard-preview.png
│
└── 🔧 scripts/
    ├── setup.sh                    # Dev environment setup
    └── generate_sample_data.py     # Local demo data generator
```

---

## 🚀 Quick Start

### Prerequisites

- AWS Account with CloudWatch access
- Python 3.11+
- Node.js 18+
- Terraform 1.5+
- AWS CLI configured (`aws configure`)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/aws-cost-optimization-dashboard.git
cd aws-cost-optimization-dashboard
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure AWS credentials
cp config.py.example config.py
# Edit config.py with your AWS region and settings

python app.py
# API running at http://localhost:5000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

### 4. Deploy Infrastructure (Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Fill in your values

terraform init
terraform plan
terraform apply
```

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/ec2/metrics` | GET | EC2 utilization metrics |
| `/api/rds/metrics` | GET | RDS utilization metrics |
| `/api/recommendations` | GET | Cost optimization suggestions |
| `/api/cost/summary` | GET | Monthly cost breakdown |
| `/api/alerts` | GET | Active CloudWatch alarms |

### Sample Response — `/api/recommendations`

```json
{
  "recommendations": [
    {
      "resource_id": "i-0abc123def456",
      "resource_type": "EC2",
      "instance_type": "t3.xlarge",
      "avg_cpu_7d": 8.3,
      "recommendation": "Downsize to t3.small",
      "estimated_monthly_saving": 67.20,
      "confidence": "HIGH"
    }
  ],
  "total_potential_savings": 412.80,
  "currency": "USD"
}
```

---

## 🔧 Configuration

### Environment Variables

```bash
# backend/.env
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_key          # Use IAM role in production
AWS_SECRET_ACCESS_KEY=your_secret
CLOUDWATCH_PERIOD=3600              # Metrics interval in seconds
ALERT_THRESHOLD_CPU=20              # % CPU below which = underutilized
FLASK_ENV=development
```

### Terraform Variables (`terraform.tfvars`)

```hcl
aws_region        = "ap-south-1"
project_name      = "cost-dashboard"
alert_email       = "you@example.com"
cpu_alarm_threshold = 20
environment       = "production"
```

---

## 💡 Cost Optimization Logic

The recommendation engine uses these rules:

```
EC2 Recommendations:
  - avg_cpu_7d < 10%  → "Strongly consider downsizing or stopping"
  - avg_cpu_7d < 20%  → "Consider right-sizing to smaller instance"
  - avg_cpu_7d > 85%  → "Consider upsizing — risk of performance issues"

RDS Recommendations:
  - avg_cpu_7d < 10%  → "Consider smaller DB instance class"
  - connections < 5   → "Check if DB is actively used"
  - storage_used < 20%→ "Allocated storage may be over-provisioned"
```

---

## 🔔 Alert Integration

SNS topics created by Terraform automatically send alerts when:
- Any EC2 instance CPU drops below threshold for 24+ hours
- RDS instance approaches storage limit (>80% used)
- Estimated monthly spend exceeds budget threshold

Configure alert destinations in `terraform/modules/sns/main.tf`.

---

## 🚧 Future Enhancements

- [ ] **S3 Cost Analysis** — Identify large/unused S3 buckets
- [ ] **Lambda Monitoring** — Function invocation and duration costs
- [ ] **Multi-Account Support** — AWS Organizations integration
- [ ] **Scheduled Reports** — Weekly PDF cost reports via SES
- [ ] **Anomaly Detection** — ML-based spend spike alerts
- [ ] **Savings Plans Analyzer** — On-demand vs Reserved vs Spot comparison
- [ ] **Terraform Drift Detection** — Alert on manual infrastructure changes
- [ ] **Slack Bot Integration** — Query recommendations from Slack
- [ ] **Cost Allocation Tags** — Break down costs by team/project

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/s3-monitoring`
3. Commit your changes: `git commit -m 'Add S3 bucket cost monitoring'`
4. Push and open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

Built as a portfolio project demonstrating AWS cost management, Infrastructure as Code, and full-stack development skills.

**Connect:** [LinkedIn](https://linkedin.com) | [GitHub](https://github.com)

---

> ⭐ If this project helped you, consider giving it a star!
