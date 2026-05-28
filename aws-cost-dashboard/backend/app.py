"""
AWS Cost Optimization Dashboard — Flask Backend API
====================================================
Connects to AWS CloudWatch, EC2, and RDS to surface
utilization metrics and generate cost recommendations.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import boto3
import os
from datetime import datetime, timedelta
from config import Config

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# AWS clients (uses env vars or IAM role in production)
session = boto3.Session(region_name=Config.AWS_REGION)
cloudwatch = session.client("cloudwatch")
ec2_client = session.client("ec2")
rds_client = session.client("rds")


# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


# ─────────────────────────────────────────────────────────────────────────────
# EC2 Metrics
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/ec2/metrics")
def ec2_metrics():
    """Return CPU utilization and metadata for all running EC2 instances."""
    try:
        instances = _get_ec2_instances()
        result = []

        for inst in instances:
            instance_id = inst["InstanceId"]
            cpu_avg = _get_metric_average(
                namespace="AWS/EC2",
                metric_name="CPUUtilization",
                dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                days=7
            )
            network_in = _get_metric_average(
                namespace="AWS/EC2",
                metric_name="NetworkIn",
                dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                days=7
            )
            result.append({
                "instance_id": instance_id,
                "instance_type": inst.get("InstanceType"),
                "state": inst["State"]["Name"],
                "name": _get_tag(inst.get("Tags", []), "Name"),
                "launch_time": inst["LaunchTime"].isoformat() if inst.get("LaunchTime") else None,
                "avg_cpu_7d": round(cpu_avg, 2),
                "avg_network_in_7d_mb": round(network_in / 1024 / 1024, 2),
                "status": _utilization_status(cpu_avg),
            })

        return jsonify({"instances": result, "count": len(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# RDS Metrics
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/rds/metrics")
def rds_metrics():
    """Return CPU, connections, and storage metrics for all RDS instances."""
    try:
        response = rds_client.describe_db_instances()
        db_instances = response["DBInstances"]
        result = []

        for db in db_instances:
            db_id = db["DBInstanceIdentifier"]
            dims = [{"Name": "DBInstanceIdentifier", "Value": db_id}]

            cpu_avg = _get_metric_average("AWS/RDS", "CPUUtilization", dims, days=7)
            connections = _get_metric_average("AWS/RDS", "DatabaseConnections", dims, days=7)
            free_storage = _get_metric_average("AWS/RDS", "FreeStorageSpace", dims, days=1)

            result.append({
                "db_instance_id": db_id,
                "db_class": db.get("DBInstanceClass"),
                "engine": db.get("Engine"),
                "engine_version": db.get("EngineVersion"),
                "status": db.get("DBInstanceStatus"),
                "allocated_storage_gb": db.get("AllocatedStorage"),
                "free_storage_gb": round(free_storage / 1024 / 1024 / 1024, 2),
                "avg_cpu_7d": round(cpu_avg, 2),
                "avg_connections_7d": round(connections, 1),
                "multi_az": db.get("MultiAZ"),
                "utilization_status": _utilization_status(cpu_avg),
            })

        return jsonify({"instances": result, "count": len(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Cost Recommendations
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/recommendations")
def recommendations():
    """Generate right-sizing recommendations based on utilization metrics."""
    try:
        ec2_instances = _get_ec2_instances()
        recs = []
        total_savings = 0.0

        for inst in ec2_instances:
            instance_id = inst["InstanceId"]
            instance_type = inst.get("InstanceType", "")
            cpu_avg = _get_metric_average(
                "AWS/EC2", "CPUUtilization",
                [{"Name": "InstanceId", "Value": instance_id}],
                days=7
            )

            recommendation, saving, confidence = _ec2_recommendation(instance_type, cpu_avg)
            if recommendation:
                total_savings += saving
                recs.append({
                    "resource_id": instance_id,
                    "resource_type": "EC2",
                    "name": _get_tag(inst.get("Tags", []), "Name"),
                    "current_type": instance_type,
                    "avg_cpu_7d": round(cpu_avg, 2),
                    "recommendation": recommendation,
                    "estimated_monthly_saving": round(saving, 2),
                    "confidence": confidence,
                    "priority": "HIGH" if saving > 50 else "MEDIUM",
                })

        # Sort by highest potential saving first
        recs.sort(key=lambda x: x["estimated_monthly_saving"], reverse=True)

        return jsonify({
            "recommendations": recs,
            "count": len(recs),
            "total_potential_savings": round(total_savings, 2),
            "currency": "USD",
            "generated_at": datetime.utcnow().isoformat(),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Cost Summary
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/cost/summary")
def cost_summary():
    """Return current month cost summary (requires Cost Explorer access)."""
    try:
        ce = session.client("ce", region_name="us-east-1")  # CE only in us-east-1
        now = datetime.utcnow()
        start = now.replace(day=1).strftime("%Y-%m-%d")
        end = now.strftime("%Y-%m-%d")

        response = ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
        )

        groups = response["ResultsByTime"][0]["Groups"] if response["ResultsByTime"] else []
        breakdown = [
            {
                "service": g["Keys"][0],
                "cost_usd": round(float(g["Metrics"]["UnblendedCost"]["Amount"]), 2)
            }
            for g in groups
        ]
        breakdown.sort(key=lambda x: x["cost_usd"], reverse=True)
        total = sum(b["cost_usd"] for b in breakdown)

        return jsonify({
            "period_start": start,
            "period_end": end,
            "total_cost_usd": round(total, 2),
            "breakdown": breakdown[:10],  # Top 10 services
        })

    except Exception as e:
        return jsonify({"error": str(e), "note": "Cost Explorer may not be enabled"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Active CloudWatch Alarms
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/alerts")
def alerts():
    """Return currently firing CloudWatch alarms."""
    try:
        response = cloudwatch.describe_alarms(StateValue="ALARM")
        alarms = [
            {
                "name": a["AlarmName"],
                "description": a.get("AlarmDescription", ""),
                "state": a["StateValue"],
                "reason": a.get("StateReason", ""),
                "updated": a["StateUpdatedTimestamp"].isoformat(),
                "metric": a.get("MetricName"),
                "namespace": a.get("Namespace"),
            }
            for a in response["MetricAlarms"]
        ]
        return jsonify({"alarms": alarms, "count": len(alarms)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def _get_ec2_instances():
    """Fetch all running EC2 instances."""
    response = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}]
    )
    instances = []
    for reservation in response["Reservations"]:
        instances.extend(reservation["Instances"])
    return instances


def _get_metric_average(namespace, metric_name, dimensions, days=7):
    """Fetch the average of a CloudWatch metric over the specified number of days."""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Average"]
    )

    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return 0.0
    return sum(d["Average"] for d in datapoints) / len(datapoints)


def _utilization_status(cpu_avg):
    if cpu_avg < 10:
        return "CRITICALLY_UNDERUTILIZED"
    elif cpu_avg < 20:
        return "UNDERUTILIZED"
    elif cpu_avg > 85:
        return "HIGH"
    else:
        return "NORMAL"


# Simplified savings estimation (replace with AWS Pricing API for production)
EC2_HOURLY_COSTS = {
    "t3.nano": 0.0052, "t3.micro": 0.0104, "t3.small": 0.0208,
    "t3.medium": 0.0416, "t3.large": 0.0832, "t3.xlarge": 0.1664,
    "t3.2xlarge": 0.3328, "m5.large": 0.096, "m5.xlarge": 0.192,
    "m5.2xlarge": 0.384, "m5.4xlarge": 0.768, "c5.large": 0.085,
}

DOWNSIZE_MAP = {
    "t3.xlarge": "t3.large", "t3.large": "t3.medium",
    "t3.medium": "t3.small", "m5.xlarge": "m5.large",
    "m5.2xlarge": "m5.xlarge", "m5.4xlarge": "m5.2xlarge",
}


def _ec2_recommendation(instance_type, cpu_avg):
    if cpu_avg > 20:
        return None, 0.0, None  # No recommendation needed

    target = DOWNSIZE_MAP.get(instance_type)
    if not target:
        return f"Review instance — avg CPU {cpu_avg:.1f}%", 10.0, "LOW"

    current_cost = EC2_HOURLY_COSTS.get(instance_type, 0)
    target_cost = EC2_HOURLY_COSTS.get(target, 0)
    monthly_saving = (current_cost - target_cost) * 730

    confidence = "HIGH" if cpu_avg < 10 else "MEDIUM"
    return f"Downsize to {target}", monthly_saving, confidence


def _get_tag(tags, key):
    for tag in tags:
        if tag["Key"] == key:
            return tag["Value"]
    return ""


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
