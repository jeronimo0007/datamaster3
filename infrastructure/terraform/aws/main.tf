terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Stack AWS = mesma do Docker local / Azure:
#   Kafka + MongoDB + Airflow + S3 (lake Medallion) + api-java
# Sem trocas: não usa MSK "no lugar de" Kafka, DocumentDB, Kinesis, etc.

resource "random_id" "suffix" {
  byte_length = 2
}

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  suffix      = lower(random_id.suffix.hex)
  name_prefix = "${var.project_name}-${var.environment}"
  azs         = slice(data.aws_availability_zones.available.names, 0, 2)

  lake_uri    = "s3://${aws_s3_bucket.datamaster_lake.bucket}"
  landing_uri = "${local.lake_uri}/landing"

  discovery_ns = "${var.project_name}.local"
  kafka_host   = "kafka.${local.discovery_ns}"
  mongo_host   = "mongodb.${local.discovery_ns}"

  kafka_bootstrap = "${local.kafka_host}:9092"
  mongodb_uri     = "mongodb://admin:${var.mongo_admin_password}@${local.mongo_host}:27017/fraud_detection?authSource=admin"

  # Bootstrap com imagem publica; o CI sobe a custom no ECR e atualiza os services.
  airflow_image = coalesce(
    var.airflow_container_image,
    "apache/airflow:2.9.3-python3.11"
  )
  api_image = coalesce(
    var.api_container_image,
    "${aws_ecr_repository.api.repository_url}:latest"
  )
}

# --- Rede (subnets públicas; Fargate com IP público — sem NAT) ---

resource "aws_vpc" "main" {
  cidr_block           = "10.40.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "${local.name_prefix}-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${local.name_prefix}-igw" }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true

  tags = { Name = "${local.name_prefix}-public-${count.index}" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = { Name = "${local.name_prefix}-public-rt" }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_service_discovery_private_dns_namespace" "main" {
  name = local.discovery_ns
  vpc  = aws_vpc.main.id
}

# --- Lake S3 (mesmos paths landing/bronze/silver/gold) ---

resource "aws_s3_bucket" "datamaster_lake" {
  bucket = var.lake_bucket_name
}

resource "aws_s3_bucket_versioning" "datamaster_lake" {
  bucket = aws_s3_bucket.datamaster_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "datamaster_lake" {
  bucket                  = aws_s3_bucket.datamaster_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "lake_prefixes" {
  for_each = toset(["landing/", "bronze/", "silver/", "gold/", "reports/"])
  bucket   = aws_s3_bucket.datamaster_lake.id
  key      = each.value
}

# --- ECR ---

resource "aws_ecr_repository" "airflow" {
  name                 = "${var.project_name}-airflow"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "api" {
  name                 = "${var.project_name}-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

# --- ECS cluster + logs ---

resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name_prefix}"
  retention_in_days = 7
}

# --- Security groups ---

resource "aws_security_group" "alb" {
  name_prefix = "${local.name_prefix}-alb-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name_prefix = "${local.name_prefix}-ecs-"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Airflow UI from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description = "Kafka interno"
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    self        = true
  }

  ingress {
    description = "MongoDB interno"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    self        = true
  }

  ingress {
    description = "API"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- IAM (execução ECS + task com acesso S3) ---

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${local.name_prefix}-ecs-exec-${local.suffix}"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name               = "${local.name_prefix}-ecs-task-${local.suffix}"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "s3-lake-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [aws_s3_bucket.datamaster_lake.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:AbortMultipartUpload",
          "s3:ListMultipartUploadParts"
        ]
        Resource = ["${aws_s3_bucket.datamaster_lake.arn}/*"]
      }
    ]
  })
}
