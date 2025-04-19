variable "role_arn" {
  description = "ARN do papel IAM para as funções Lambda"
  type        = string
}

variable "gitlab_secret_arn" {
  description = "ARN do secret contendo o token do GitLab"
  type        = string
}

variable "sns_topic_arn" {
  description = "ARN do tópico SNS"
  type        = string
}