terraform {
  backend "s3" {
    bucket = "your-bucket-name"
    key    = "terraform/aws-gitlab-automation/terraform.tfstate"
    region = "us-east-1"

    dynamodb_table = "terraform-lock-table"
  }
}