resource "aws_iam_role" "lambda_exec" {
  name = "lambda-gitlab-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_permissions" {
  name = "lambda-gitlab-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "secretsmanager:GetSecretValue",
        Resource = var.gitlab_secret_arn
      },
      {
        Action = [
          "ssm:PutParameter",
          "ssm:GetParameter",
          "ssm:GetParametersByPath"
        ],
        Resource = "arn:aws:ssm:*:*:parameter/gitlab.com/*",
        Effect = "Allow"
      },
      {
        Action = "sns:Publish",
        Resource = "*",
        Effect = "Allow"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_permissions.arn
}

output "role_arn" {
  value = aws_iam_role.lambda_exec.arn
}