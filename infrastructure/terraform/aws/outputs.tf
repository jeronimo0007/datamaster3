output "lake_bucket_name" {
  description = "Bucket S3 do data lake"
  value       = aws_s3_bucket.datamaster_lake.bucket
}

output "lake_bucket_arn" {
  description = "ARN do bucket"
  value       = aws_s3_bucket.datamaster_lake.arn
}

output "lake_uri" {
  description = "URI base do lake (LAKE_BASE_URI)"
  value       = local.lake_uri
}

output "landing_uri" {
  description = "URI da landing (LANDING_BASE_URI)"
  value       = local.landing_uri
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "ecr_airflow_url" {
  value = aws_ecr_repository.airflow.repository_url
}

output "ecr_api_url" {
  value = aws_ecr_repository.api.repository_url
}

output "airflow_webserver_url" {
  description = "URL da UI do Airflow (ALB)"
  value       = "http://${aws_lb.airflow.dns_name}"
}

output "airflow_webserver_service" {
  value = aws_ecs_service.airflow_webserver.name
}

output "airflow_scheduler_service" {
  value = aws_ecs_service.airflow_scheduler.name
}

output "airflow_init_task_family" {
  value = aws_ecs_task_definition.airflow_init.family
}

output "airflow_web_task_family" {
  value = aws_ecs_task_definition.airflow_webserver.family
}

output "airflow_scheduler_task_family" {
  value = aws_ecs_task_definition.airflow_scheduler.family
}

output "api_service" {
  value = aws_ecs_service.api.name
}

output "api_url" {
  description = "URL da API via ALB (/api/*, /health)"
  value       = "http://${aws_lb.airflow.dns_name}"
}

output "api_task_family" {
  value = aws_ecs_task_definition.api.family
}

output "mongodb_host" {
  value = local.mongo_host
}

output "kafka_bootstrap" {
  value = local.kafka_bootstrap
}

output "mongodb_uri" {
  value     = local.mongodb_uri
  sensitive = true
}

output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "ecs_security_group_id" {
  value = aws_security_group.ecs.id
}
