terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.67"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

locals {
  suffix = var.name_suffix
  alnum  = replace(var.project_name, "-", "")

  storage_account_name = coalesce(
    var.storage_account_name,
    substr("${local.alnum}st${local.suffix}", 0, 24)
  )
  key_vault_name = coalesce(
    var.key_vault_name,
    substr("${local.alnum}kv${local.suffix}", 0, 24)
  )
  acr_name = substr("${local.alnum}acr${local.suffix}", 0, 50)
  api_image = coalesce(
    var.api_container_image,
    "mcr.microsoft.com/k8se/quickstart:latest"
  )
  # MongoDB real (ACI) — mesma imagem do docker-compose, não Cosmos
  mongodb_uri = "mongodb://admin:${var.mongo_admin_password}@${azurerm_container_group.mongo.fqdn}:27017/fraud_detection?authSource=admin"
  # Kafka real (ACI) — mesmo broker Kafka do local, não Event Hubs
  kafka_dns       = substr("${local.alnum}kafka${local.suffix}", 0, 63)
  mongo_dns       = substr("${local.alnum}mongo${local.suffix}", 0, 63)
  kafka_bootstrap = "${azurerm_container_group.kafka.fqdn}:9092"
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "main" {
  name     = "${var.resource_group_name}-${local.suffix}"
  location = var.location
  tags = {
    Environment = "apresentacao"
    Project     = "fraud-detection"
  }
}

# --- Data Lake Gen2 (Medallion: bronze / silver / gold) ---
resource "azurerm_storage_account" "datalake" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "bronze" {
  name               = "bronze"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "silver" {
  name               = "silver"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "gold" {
  name               = "gold"
  storage_account_id = azurerm_storage_account.datalake.id
}

# Legado (compatível com scripts antigos raw/processed/curated)
resource "azurerm_storage_data_lake_gen2_filesystem" "raw" {
  name               = "raw"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "processed" {
  name               = "processed"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "curated" {
  name               = "curated"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "landing" {
  name               = "landing"
  storage_account_id = azurerm_storage_account.datalake.id
}

# --- MongoDB (mesma imagem do compose — NÃO Cosmos/DocumentDB) ---
resource "azurerm_container_group" "mongo" {
  name                = "${var.project_name}-mongo-${local.suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  ip_address_type     = "Public"
  dns_name_label      = local.mongo_dns
  restart_policy      = "Always"

  container {
    name   = "mongodb"
    image  = "mongo:6.0"
    cpu    = "1"
    memory = "1.5"

    ports {
      port     = 27017
      protocol = "TCP"
    }

    environment_variables = {
      MONGO_INITDB_ROOT_USERNAME = "admin"
      MONGO_INITDB_ROOT_PASSWORD = var.mongo_admin_password
    }
  }

  tags = azurerm_resource_group.main.tags
}

# --- Kafka KRaft (mesma tecnologia do compose — NÃO Event Hubs) ---
resource "azurerm_container_group" "kafka" {
  name                = "${var.project_name}-kafka-${local.suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  ip_address_type     = "Public"
  dns_name_label      = local.kafka_dns
  restart_policy      = "Always"

  container {
    name   = "kafka"
    image  = "bitnami/kafka:3.6"
    cpu    = "1"
    memory = "2"

    ports {
      port     = 9092
      protocol = "TCP"
    }

    environment_variables = {
      KAFKA_CFG_NODE_ID                        = "0"
      KAFKA_CFG_PROCESS_ROLES                  = "controller,broker"
      KAFKA_CFG_LISTENERS                      = "PLAINTEXT://:9092,CONTROLLER://:9093"
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP = "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT"
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS       = "0@127.0.0.1:9093"
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES      = "CONTROLLER"
      KAFKA_CFG_ADVERTISED_LISTENERS           = "PLAINTEXT://${local.kafka_dns}.${var.location}.azurecontainer.io:9092"
      ALLOW_PLAINTEXT_LISTENER                 = "yes"
    }
  }

  tags = azurerm_resource_group.main.tags
}

# --- Key Vault ---
resource "azurerm_key_vault" "main" {
  name                       = local.key_vault_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  tags = azurerm_resource_group.main.tags

  timeouts {
    create = "30m"
    read   = "10m"
    update = "30m"
    delete = "30m"
  }
}


# --- Observabilidade (sempre — par do slide Monitor / App Insights) ---
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.project_name}-logs-${local.suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_application_insights" "main" {
  name                = "${var.project_name}-appi-${local.suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"

  tags = azurerm_resource_group.main.tags
}

# --- Container Apps + ACR (API Java — mesmo papel do slide) ---
resource "azurerm_container_registry" "main" {
  name                = local.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_container_app_environment" "main" {
  name                       = "${var.project_name}-cae-${local.suffix}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_container_app" "api" {
  name                         = "${var.project_name}-api-${local.suffix}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }

  secret {
    name  = "mongodb-uri"
    value = local.mongodb_uri
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }

  template {
    min_replicas = 1
    max_replicas = 3

    container {
      name   = "api"
      image  = local.api_image
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "SPRING_PROFILES_ACTIVE"
        value = "local"
      }
      env {
        name        = "MONGODB_URI"
        secret_name = "mongodb-uri"
      }
      env {
        name  = "KAFKA_BOOTSTRAP_SERVERS"
        value = local.kafka_bootstrap
      }
      env {
        name  = "FRAUD_KAFKA_ENABLED"
        value = "true"
      }
      env {
        name  = "FRAUD_KAFKA_TOPIC"
        value = "transaction-analyzed"
      }
      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = azurerm_application_insights.main.connection_string
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    transport        = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  tags = azurerm_resource_group.main.tags

  lifecycle {
    ignore_changes = [template[0].container[0].image]
  }
}
