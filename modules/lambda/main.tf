resource "aws_lambda_function" "gitlab_repos_collector" {
  function_name = "gitlab_repos_collector"
  role          = var.role_arn
  handler       = "collector.lambda_handler"
  runtime       = "python3.10"
  filename      = "build/gitlab_collector.zip"
  source_code_hash = filebase64sha256("build/gitlab_collector.zip")

  environment {
    variables = {
      GITLAB_SECRET_ARN = var.gitlab_secret_arn
      SNS_TOPIC_ARN     = var.sns_topic_arn
    }
  }

  tracing_config {
    mode = "Active"
  }

  timeout = 30
}

resource "aws_lambda_function" "gitlab_ci_configurator" {
  function_name = "gitlab_ci_configurator"
  role          = var.role_arn
  handler       = "configurator.lambda_handler"
  runtime       = "python3.10"
  filename      = "build/gitlab_configurator.zip"
  source_code_hash = filebase64sha256("build/gitlab_configurator.zip")

  environment {
    variables = {
      GITLAB_SECRET_ARN = var.gitlab_secret_arn
      SNS_TOPIC_ARN     = var.sns_topic_arn
    }
  }

  tracing_config {
    mode = "Active"
  }

  timeout = 30
}

output "collector_lambda_arn" {
  value = aws_lambda_function.gitlab_repos_collector.arn
}

output "configurator_lambda_arn" {
  value = aws_lambda_function.gitlab_ci_configurator.arn
}