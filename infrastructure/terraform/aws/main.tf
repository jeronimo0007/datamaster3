terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Stack minima AWS — lake S3 (paths Medallion).
# Kafka e MongoDB sobem iguais ao docker-compose (containers ECS/EKS), não DocumentDB/Dynamo/Kinesis.
resource "aws_s3_bucket" "datamaster_lake" {
  bucket = var.lake_bucket_name

  tags = {
    Project     = "datamaster"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "datamaster_lake" {
  bucket = aws_s3_bucket.datamaster_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}
