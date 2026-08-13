variable "resource_group_name" {
  type    = string
  default = "rg-fraud-apresentacao"
}

variable "location" {
  type    = string
  default = "brazilsouth"
}

variable "project_name" {
  type    = string
  default = "fraud-apresentacao"
}

variable "name_suffix" {
  type        = string
  default     = "banca"
  description = "Sufixo estável dos recursos (apresentação)."
}

variable "storage_account_name" {
  type        = string
  description = "Único globalmente na Azure (3-24 chars, só minúsculas e números)"
  default     = null
}

variable "key_vault_name" {
  type    = string
  default = null
}

variable "mongo_admin_password" {
  type        = string
  sensitive   = true
  description = "Senha do MongoDB (mesma stack do docker-compose)."
  default     = "admin123ChangeMe"
}

variable "enable_analytics_stack" {
  description = "Databricks + Synapse + Azure ML (opcional)."
  type        = bool
  default     = false
}

variable "analytics_high_cost_acknowledged" {
  type    = bool
  default = false
}

variable "synapse_sql_admin_login" {
  type    = string
  default = "sqladmin"
}

variable "databricks_sku" {
  type    = string
  default = "premium"
}

variable "api_container_image" {
  description = "Imagem da API Java no ACR. null = quickstart até o build."
  type        = string
  default     = null
}
