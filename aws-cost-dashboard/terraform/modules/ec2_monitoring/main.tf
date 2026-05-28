# ==============================================================
# Module: EC2 Monitoring — IAM Role & Instance Profile
# ==============================================================

# IAM Role for EC2 instances to push custom CloudWatch metrics
resource "aws_iam_role" "ec2_monitoring" {
  name = "${var.project_name}-ec2-monitoring-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "${var.project_name}-ec2-monitoring"
    Environment = var.environment
  }
}

# Attach CloudWatch Agent policy
resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {
  role       = aws_iam_role.ec2_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# Attach SSM policy (for CloudWatch agent config distribution)
resource "aws_iam_role_policy_attachment" "ssm_policy" {
  role       = aws_iam_role.ec2_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Instance profile to attach role to EC2 instances
resource "aws_iam_instance_profile" "ec2_monitoring" {
  name = "${var.project_name}-ec2-monitoring-profile-${var.environment}"
  role = aws_iam_role.ec2_monitoring.name
}

output "instance_profile_name" {
  value = aws_iam_instance_profile.ec2_monitoring.name
}

output "role_arn" {
  value = aws_iam_role.ec2_monitoring.arn
}
