variable "aws_region" {
  description = "Regiao AWS"
  type        = string
  default     = "sa-east-1"
}

variable "environment" {
  description = "Ambiente (dev, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Prefixo dos recursos"
  type        = string
  default     = "datamaster"
}

variable "lake_bucket_name" {
  description = "Nome globalmente unico do bucket S3 (lake Medallion)"
  type        = string
}

variable "mongo_admin_password" {
  description = "Senha root do MongoDB (mesma stack do Docker)"
  type        = string
  sensitive   = true
}

variable "airflow_admin_password" {
  description = "Senha do usuario admin do Airflow"
  type        = string
  sensitive   = true
}

variable "airflow_container_image" {
  description = "Imagem do Airflow (ECR). Null = usa ECR :latest apos o push do CI"
  type        = string
  default     = null
}

variable "api_container_image" {
  description = "Imagem da API Java (ECR). Null = usa ECR :latest apos o push do CI"
  type        = string
  default     = null
}
