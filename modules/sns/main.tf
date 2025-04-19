resource "aws_kms_key" "sns" {
  description            = "CMK for SNS Topic encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

resource "aws_sns_topic" "gitlab_notify" {
  name              = "gitlab-change-notifications"
  kms_master_key_id = aws_kms_key.sns.arn
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.gitlab_notify.arn
  protocol  = "email"
  endpoint  = var.email_notification
}

output "topic_arn" {
  value = aws_sns_topic.gitlab_notify.arn
}