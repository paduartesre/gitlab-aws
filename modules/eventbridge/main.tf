resource "aws_scheduler_schedule" "daily_collector_schedule" {
  name = "daily-gitlab-collector"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 10 * * ? *)"

  target {
    arn      = var.lambda_collector_arn
    role_arn = var.role_arn
  }
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_collector_arn
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.daily_collector_schedule.arn
}

resource "aws_scheduler_schedule" "daily_configurator_schedule" {
  name = "daily-gitlab-configurator"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(5 10 * * ? *)"

  target {
    arn      = var.lambda_configurator_arn
    role_arn = var.role_arn
  }
}

resource "aws_lambda_permission" "allow_eventbridge_cfg" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_configurator_arn
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.daily_configurator_schedule.arn
}