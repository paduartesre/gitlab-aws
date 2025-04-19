variable "region" {
  type        = string
  description = "AWS region"
}

module "iam" {
  source = "./modules/iam"
  gitlab_secret_arn = var.gitlab_secret_arn
}

module "lambda" {
  source            = "./modules/lambda"
  gitlab_secret_arn = var.gitlab_secret_arn
  sns_topic_arn     = module.sns.topic_arn
  role_arn          = var.role_arn
}

module "sns" {
  source = "./modules/sns"
  email_notification = var.email_notification
}

module "eventbridge" {
  source = "./modules/eventbridge"
  lambda_collector_arn = module.lambda.collector_lambda_arn
  lambda_configurator_arn = module.lambda.configurator_lambda_arn
  role_arn = var.role_arn
}