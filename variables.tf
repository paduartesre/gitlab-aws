variable "region" {
  description = "AWS region"
  type        = string
}

variable "gitlab_secret_arn" {
  type        = string
  description = "ARN of the GitLab secret"
}

variable "email_notification" {
  description = "E-mail para receber notificações"
  type        = string
}

variable "role_arn" {
  description = "ARN do papel IAM para as funções Lambda"
  type        = string
}
