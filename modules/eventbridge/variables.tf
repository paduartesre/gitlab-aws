variable "role_arn" {
  description = "ARN do papel IAM para as funções Lambda"
  type        = string
}

variable "lambda_collector_arn" {
  description = "ARN da função Lambda gitlab_repos_collector"
  type        = string
}

variable "lambda_configurator_arn" {
  description = "ARN da função Lambda gitlab_ci_configurator"
  type        = string
}
