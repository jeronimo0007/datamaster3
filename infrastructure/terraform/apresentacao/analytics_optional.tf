# Databricks, Synapse, Azure ML — ativo por padrão (enable_analytics_stack = true)
# Nomes usam o mesmo name_suffix estável da stack (ex.: banca).

resource "random_password" "synapse_sql" {
  count   = var.enable_analytics_stack ? 1 : 0
  length  = 24
  special = true
}

resource "azurerm_synapse_workspace" "main" {
  count = var.enable_analytics_stack ? 1 : 0

  name                                 = substr("${local.alnum}syn${local.suffix}", 0, 50)
  resource_group_name                  = azurerm_resource_group.main.name
  location                             = azurerm_resource_group.main.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.gold.id
  sql_administrator_login              = var.synapse_sql_admin_login
  sql_administrator_login_password     = random_password.synapse_sql[0].result

  identity {
    type = "SystemAssigned"
  }

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_role_assignment" "synapse_storage" {
  count = var.enable_analytics_stack ? 1 : 0

  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_synapse_workspace.main[0].identity[0].principal_id
}

resource "azurerm_databricks_workspace" "main" {
  count = var.enable_analytics_stack ? 1 : 0

  name                = substr("${local.alnum}dbw${local.suffix}", 0, 30)
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.databricks_sku

  tags = azurerm_resource_group.main.tags
}

# Azure ML nao aceita storage com HNS (ADLS). Conta dedicada sem hierarchical namespace.
resource "azurerm_storage_account" "aml" {
  count = var.enable_analytics_stack ? 1 : 0

  name                     = substr("${local.alnum}aml${local.suffix}", 0, 24)
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = false

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_machine_learning_workspace" "main" {
  count = var.enable_analytics_stack ? 1 : 0

  name                    = substr("${local.alnum}mlw${local.suffix}", 0, 33)
  location                = azurerm_resource_group.main.location
  resource_group_name     = azurerm_resource_group.main.name
  application_insights_id = azurerm_application_insights.main.id
  key_vault_id            = azurerm_key_vault.main.id
  storage_account_id      = azurerm_storage_account.aml[0].id

  identity {
    type = "SystemAssigned"
  }

  tags = azurerm_resource_group.main.tags
}
