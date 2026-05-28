"""
generate_sample_data.py
========================
Generates realistic mock AWS metrics for local development
and portfolio demo purposes. Run this instead of connecting
to a real AWS account during demos.

Usage:
    python scripts/generate_sample_data.py
    # Outputs sample_data.json — used by frontend in demo mode
"""

import json
import random
from datetime import datetime, timedelta

random.seed(42)

INSTANCE_TYPES = ["t3.micro", "t3.small", "t3.medium", "t3.large", "t3.xlarge",
                  "m5.large", "m5.xlarge", "m5.2xlarge"]
DB_CLASSES = ["db.t3.micro", "db.t3.small", "db.t3.medium", "db.m5.large"]
NAMES = ["web-server-prod", "api-server-01", "worker-node-1", "batch-processor",
         "ml-training-gpu", "bastion-host", "monitoring-server", "legacy-app"]
DB_NAMES = ["users-db-prod", "analytics-db", "cache-db", "reporting-db"]
ENGINES = ["mysql", "postgres", "aurora-mysql"]

def random_cpu(bias="low"):
    if bias == "low":
        return round(random.uniform(2, 18), 1)
    elif bias == "high":
        return round(random.uniform(70, 95), 1)
    return round(random.uniform(5, 80), 1)

def gen_ec2_instances(n=8):
    instances = []
    for i in range(n):
        cpu = random_cpu("low" if i < 5 else "normal")
        itype = INSTANCE_TYPES[i % len(INSTANCE_TYPES)]
        instances.append({
            "instance_id": f"i-0{random.randint(100000000000, 999999999999):012x}"[:14],
            "instance_type": itype,
            "state": "running",
            "name": NAMES[i % len(NAMES)],
            "launch_time": (datetime.utcnow() - timedelta(days=random.randint(10, 180))).isoformat(),
            "avg_cpu_7d": cpu,
            "avg_network_in_7d_mb": round(random.uniform(50, 5000), 1),
            "status": (
                "CRITICALLY_UNDERUTILIZED" if cpu < 10 else
                "UNDERUTILIZED" if cpu < 20 else
                "HIGH" if cpu > 85 else "NORMAL"
            )
        })
    return instances

def gen_rds_instances(n=4):
    instances = []
    for i in range(n):
        cpu = random_cpu("low" if i < 3 else "normal")
        alloc = random.choice([20, 50, 100, 200, 500])
        free = round(random.uniform(0.1, 0.8) * alloc, 1)
        instances.append({
            "db_instance_id": DB_NAMES[i % len(DB_NAMES)],
            "db_class": DB_CLASSES[i % len(DB_CLASSES)],
            "engine": ENGINES[i % len(ENGINES)],
            "engine_version": "8.0.35",
            "status": "available",
            "allocated_storage_gb": alloc,
            "free_storage_gb": free,
            "avg_cpu_7d": cpu,
            "avg_connections_7d": round(random.uniform(0, 45), 1),
            "multi_az": random.choice([True, False]),
            "utilization_status": (
                "CRITICALLY_UNDERUTILIZED" if cpu < 10 else
                "UNDERUTILIZED" if cpu < 20 else "NORMAL"
            )
        })
    return instances

def gen_recommendations(ec2, rds):
    recs = []
    downsize_map = {
        "t3.xlarge": ("t3.large", 67.20), "t3.large": ("t3.medium", 33.60),
        "t3.medium": ("t3.small", 16.80), "m5.xlarge": ("m5.large", 70.08),
        "m5.2xlarge": ("m5.xlarge", 70.08),
    }
    for inst in ec2:
        if inst["avg_cpu_7d"] < 20:
            target, saving = downsize_map.get(inst["instance_type"], (None, 10.0))
            if target:
                recs.append({
                    "resource_id": inst["instance_id"],
                    "resource_type": "EC2",
                    "name": inst["name"],
                    "current_type": inst["instance_type"],
                    "avg_cpu_7d": inst["avg_cpu_7d"],
                    "recommendation": f"Downsize to {target}",
                    "estimated_monthly_saving": saving,
                    "confidence": "HIGH" if inst["avg_cpu_7d"] < 10 else "MEDIUM",
                    "priority": "HIGH" if saving > 50 else "MEDIUM",
                })
    recs.sort(key=lambda x: x["estimated_monthly_saving"], reverse=True)
    return recs

def gen_cost_summary():
    services = [
        ("Amazon EC2", 312.40), ("Amazon RDS", 198.20),
        ("Amazon S3", 45.80), ("AWS Lambda", 12.30),
        ("Amazon CloudFront", 28.50), ("Amazon Route 53", 5.00),
        ("AWS CloudWatch", 8.40), ("Amazon SNS", 1.20),
    ]
    return {
        "period_start": datetime.utcnow().replace(day=1).strftime("%Y-%m-%d"),
        "period_end": datetime.utcnow().strftime("%Y-%m-%d"),
        "total_cost_usd": sum(s[1] for s in services),
        "breakdown": [{"service": s[0], "cost_usd": s[1]} for s in services]
    }

def gen_cpu_trend(days=7):
    """7-day hourly CPU trend for charts."""
    trend = []
    base = datetime.utcnow() - timedelta(days=days)
    for h in range(days * 24):
        trend.append({
            "timestamp": (base + timedelta(hours=h)).strftime("%Y-%m-%dT%H:00:00"),
            "ec2_avg_cpu": round(random.uniform(5, 35), 1),
            "rds_avg_cpu": round(random.uniform(3, 22), 1),
        })
    return trend

if __name__ == "__main__":
    ec2 = gen_ec2_instances(8)
    rds = gen_rds_instances(4)
    recs = gen_recommendations(ec2, rds)

    data = {
        "ec2": {"instances": ec2, "count": len(ec2)},
        "rds": {"instances": rds, "count": len(rds)},
        "recommendations": {
            "recommendations": recs,
            "count": len(recs),
            "total_potential_savings": sum(r["estimated_monthly_saving"] for r in recs),
            "currency": "USD"
        },
        "cost_summary": gen_cost_summary(),
        "cpu_trend": gen_cpu_trend(7),
        "alerts": {
            "alarms": [
                {
                    "name": "cost-dashboard-ec2-low-cpu-i-0abc123",
                    "description": "EC2 CPU below 20% threshold",
                    "state": "ALARM",
                    "reason": "Threshold Crossed: 3 datapoints were less than 20%",
                    "updated": datetime.utcnow().isoformat(),
                    "metric": "CPUUtilization",
                    "namespace": "AWS/EC2",
                }
            ],
            "count": 1
        }
    }

    with open("scripts/sample_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Generated sample_data.json")
    print(f"   EC2 instances:     {len(ec2)}")
    print(f"   RDS instances:     {len(rds)}")
    print(f"   Recommendations:   {len(recs)}")
    print(f"   Total savings:     ${data['recommendations']['total_potential_savings']:.2f}/mo")
    print(f"   Monthly cost:      ${data['cost_summary']['total_cost_usd']:.2f}")
