# Airflow no ECS Fargate — mesma stack do Docker / Azure Container Apps.
#
# Orquestra:
#   ingestão multi-formato → landing (S3)
#   Medallion Bronze → DQ → Silver (harmonização) → Gold (S3)
#
# Metadados SQLite em EFS (espelho do Azure Files Share).
# Task role com acesso S3 (espelho da Managed Identity na Azure).

resource "aws_efs_file_system" "airflow" {
  creation_token = "${local.name_prefix}-airflow-${local.suffix}"
  encrypted      = true

  tags = { Name = "${local.name_prefix}-airflow-efs" }
}

resource "aws_security_group" "efs" {
  name_prefix = "${local.name_prefix}-efs-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_efs_mount_target" "airflow" {
  count           = 2
  file_system_id  = aws_efs_file_system.airflow.id
  subnet_id       = aws_subnet.public[count.index].id
  security_groups = [aws_security_group.efs.id]
}

resource "aws_efs_access_point" "airflow" {
  file_system_id = aws_efs_file_system.airflow.id

  posix_user {
    gid = 0
    uid = 50000
  }

  root_directory {
    path = "/airflow-data"
    creation_info {
      owner_gid   = 0
      owner_uid   = 50000
      permissions = "775"
    }
  }
}

# ALB → Airflow webserver
resource "aws_lb" "airflow" {
  name               = substr("${local.name_prefix}-af-${local.suffix}", 0, 32)
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "airflow" {
  name        = substr("${local.name_prefix}-af-tg-${local.suffix}", 0, 32)
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 5
    timeout             = 10
    interval            = 30
    matcher             = "200"
  }
}

resource "aws_lb_listener" "airflow" {
  load_balancer_arn = aws_lb.airflow.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.airflow.arn
  }
}

locals {
  airflow_common_env = [
    { name = "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN", value = "sqlite:////opt/airflow/data/airflow.db" },
    { name = "AIRFLOW__CORE__EXECUTOR", value = "SequentialExecutor" },
    { name = "AIRFLOW__CORE__LOAD_EXAMPLES", value = "False" },
    { name = "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION", value = "False" },
    { name = "AIRFLOW__API__AUTH_BACKENDS", value = "airflow.api.auth.backend.basic_auth" },
    { name = "AIRFLOW__WEBSERVER__EXPOSE_CONFIG", value = "False" },
    { name = "PYTHONPATH", value = "/opt/airflow/project" },
    { name = "PROJECT_ROOT", value = "/opt/airflow/project" },
    { name = "LAKE_BASE_URI", value = local.lake_uri },
    { name = "LANDING_BASE_URI", value = local.landing_uri },
    { name = "MONGODB_URI", value = local.mongodb_uri },
    { name = "KAFKA_BOOTSTRAP_SERVERS", value = local.kafka_bootstrap },
    { name = "AWS_DEFAULT_REGION", value = var.aws_region },
  ]
}

resource "aws_iam_role_policy" "ecs_task_efs" {
  name = "efs-airflow-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "elasticfilesystem:ClientMount",
          "elasticfilesystem:ClientWrite",
          "elasticfilesystem:ClientRootAccess"
        ]
        Resource = [aws_efs_file_system.airflow.arn]
      }
    ]
  })
}

# Task de init (executada pelo workflow via `aws ecs run-task`)
resource "aws_ecs_task_definition" "airflow_init" {
  family                   = "${local.name_prefix}-airflow-init"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  volume {
    name = "airflow-data"
    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.airflow.id
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.airflow.id
        iam             = "ENABLED"
      }
    }
  }

  container_definitions = jsonencode([
    {
      name      = "airflow-init"
      image     = local.airflow_image
      essential = true
      command = [
        "bash", "-c",
        "set -euo pipefail; mkdir -p /opt/airflow/data; airflow db migrate; airflow users create --username admin --password \"$AIRFLOW_ADMIN_PASSWORD\" --firstname Data --lastname Master --role Admin --email admin@datamaster.local || true"
      ]
      environment = concat(local.airflow_common_env, [
        { name = "AIRFLOW_ADMIN_PASSWORD", value = var.airflow_admin_password }
      ])
      mountPoints = [
        { sourceVolume = "airflow-data", containerPath = "/opt/airflow/data" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "airflow-init"
        }
      }
    }
  ])

  depends_on = [aws_efs_mount_target.airflow]
}

resource "aws_ecs_task_definition" "airflow_webserver" {
  family                   = "${local.name_prefix}-airflow-web"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  volume {
    name = "airflow-data"
    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.airflow.id
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.airflow.id
        iam             = "ENABLED"
      }
    }
  }

  container_definitions = jsonencode([
    {
      name      = "airflow-webserver"
      image     = local.airflow_image
      essential = true
      command   = ["airflow", "webserver"]
      portMappings = [
        { containerPort = 8080, protocol = "tcp" }
      ]
      environment = local.airflow_common_env
      mountPoints = [
        { sourceVolume = "airflow-data", containerPath = "/opt/airflow/data" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "airflow-web"
        }
      }
    }
  ])

  depends_on = [aws_efs_mount_target.airflow]
}

resource "aws_ecs_service" "airflow_webserver" {
  name            = "${local.name_prefix}-airflow-web"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.airflow_webserver.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.airflow.arn
    container_name   = "airflow-webserver"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.airflow]

  lifecycle {
    ignore_changes = [task_definition]
  }
}

resource "aws_ecs_task_definition" "airflow_scheduler" {
  family                   = "${local.name_prefix}-airflow-scheduler"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  volume {
    name = "airflow-data"
    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.airflow.id
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.airflow.id
        iam             = "ENABLED"
      }
    }
  }

  container_definitions = jsonencode([
    {
      name        = "airflow-scheduler"
      image       = local.airflow_image
      essential   = true
      command     = ["airflow", "scheduler"]
      environment = local.airflow_common_env
      mountPoints = [
        { sourceVolume = "airflow-data", containerPath = "/opt/airflow/data" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "airflow-scheduler"
        }
      }
    }
  ])

  depends_on = [aws_efs_mount_target.airflow]
}

resource "aws_ecs_service" "airflow_scheduler" {
  name            = "${local.name_prefix}-airflow-scheduler"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.airflow_scheduler.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}

# API Java (serving) — mesma imagem do Docker / Azure
resource "aws_ecs_task_definition" "api" {
  family                   = "${local.name_prefix}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = local.api_image
      essential = true
      portMappings = [
        { containerPort = 8080, protocol = "tcp" }
      ]
      environment = [
        { name = "MONGODB_URI", value = local.mongodb_uri },
        { name = "KAFKA_BOOTSTRAP_SERVERS", value = local.kafka_bootstrap },
        { name = "SPRING_PROFILES_ACTIVE", value = "local" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "api"
        }
      }
    }
  ])
}

resource "aws_lb_target_group" "api" {
  name        = substr("${local.name_prefix}-api-tg-${local.suffix}", 0, 32)
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 5
    timeout             = 10
    interval            = 30
    matcher             = "200"
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.airflow.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/health"]
    }
  }
}

resource "aws_ecs_service" "api" {
  name            = "${local.name_prefix}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  # Sobe apos o CI fazer push da imagem no ECR (desired_count atualizado no workflow)
  desired_count = var.api_container_image != null ? 1 : 0
  launch_type   = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener_rule.api]

  lifecycle {
    ignore_changes = [task_definition, desired_count]
  }
}
