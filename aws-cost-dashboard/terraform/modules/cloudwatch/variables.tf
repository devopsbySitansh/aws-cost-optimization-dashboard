variable "project_name"           { type = string }
variable "environment"            { type = string }
variable "cpu_alarm_threshold"    { type = number }
variable "sns_topic_arn"          { type = string }
variable "ec2_instance_ids"       { type = list(string) }
variable "rds_instance_ids"       { type = list(string) }
variable "alarm_evaluation_periods" {
  type    = number
  default = 3
}
variable "alarm_period_seconds" {
  type    = number
  default = 86400
}
