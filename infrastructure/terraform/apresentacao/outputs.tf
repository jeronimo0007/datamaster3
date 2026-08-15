output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "storage_account_name" {
  value = azurerm_storage_account.datalake.name
}

output "lake_uri" {
  value = local.lake_uri
}

output "airflow_webserver_url" {
  value = "https://${azurerm_container_app.airflow_webserver.ingress[0].fqdn}"
}

output "airflow_webserver_name" {
  value = azurerm_container_app.airflow_webserver.name
}

output "airflow_scheduler_name" {
  value = azurerm_container_app.airflow_scheduler.name
}

output "airflow_init_job_name" {
  value = azurerm_container_app_job.airflow_init.name
}

output "datalake_containers" {
  value = ["lake"]
}

output "mongodb_fqdn" {
  value = azurerm_container_group.mongo.fqdn
}

output "mongodb_uri" {
  value     = local.mongodb_uri
  sensitive = true
}

output "kafka_bootstrap" {
  value = local.kafka_bootstrap
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.main.id
}

output "application_insights_connection_string" {
  value     = azurerm_application_insights.main.connection_string
  sensitive = true
}

output "container_registry_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "container_app_api_fqdn" {
  value = try(azurerm_container_app.api.ingress[0].fqdn, try(azurerm_container_app.api.latest_revision_fqdn, ""))
}

output "container_app_api_name" {
  value = azurerm_container_app.api.name
}

output "container_app_api_url" {
  value = "https://${try(azurerm_container_app.api.ingress[0].fqdn, azurerm_container_app.api.latest_revision_fqdn)}"
}

output "name_suffix" {
  value = var.name_suffix
}

output "enable_analytics_stack" {
  value = var.enable_analytics_stack
}

output "databricks_workspace_url" {
  value = var.enable_analytics_stack ? "https://${azurerm_databricks_workspace.main[0].workspace_url}" : null
}

output "synapse_workspace_name" {
  value = var.enable_analytics_stack ? azurerm_synapse_workspace.main[0].name : null
}

output "machine_learning_workspace_name" {
  value = var.enable_analytics_stack ? azurerm_machine_learning_workspace.main[0].name : null
}
