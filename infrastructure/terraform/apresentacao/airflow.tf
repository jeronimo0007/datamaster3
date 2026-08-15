# --- Airflow na Azure (mesma stack do Docker local) ---
#
# Orquestra o MESMO pipeline de dados:
#   ingestão multi-formato (JSON/CSV/Parquet/XML) -> landing
#   Medallion Bronze -> DQ gate -> Silver (harmonização) -> Gold
# Escrevendo no ADLS Gen2 (filesystem "lake") via adlfs/fsspec.
#
# Componentes:
# - Container App Job de init (migra o SQLite + cria usuário admin)
# - Container App webserver (UI em :8080)
# - Container App scheduler (executa os DAGs)
# - Managed Identity + role "Storage Blob Data Contributor" no lake

locals {
  airflow_dns = substr("${local.alnum}airflow${local.suffix}", 0, 32)
}

# Compartilhamento Azure Files para metadados do Airflow (SQLite)
resource "azurerm_container_app_environment_storage" "airflow" {
  name                         = "airflowstorage"
  container_app_environment_id = azurerm_container_app_environment.main.id
  account_name                 = azurerm_storage_account.datalake.name
  access_key                   = azurerm_storage_account.datalake.primary_access_key
  access_mode                  = "ReadWrite"
  share_name                   = azurerm_storage_share.airflow.name
}

# Job de init: migra o banco e cria o usuário admin (uma única execução)
resource "azurerm_container_app_job" "airflow_init" {
  name                         = "${var.project_name}-airflow-init-${local.suffix}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location

  identity {
    type = "SystemAssigned"
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }

  manual_trigger_config {
    parallelism              = 1
    replica_completion_count = 1
  }

  template {
    container {
      name    = "airflow-init"
      image   = local.airflow_image
      cpu     = "0.5"
      memory  = "1Gi"
      command = ["/bin/bash", "-c"]
      args = [
        <<-EOT
        set -euo pipefail
        mkdir -p /opt/airflow/data
        airflow db migrate
        airflow users create \
          --username admin --password "${var.airflow_admin_password}" \
          --firstname Data --lastname Master --role Admin \
          --email admin@datamaster.local || true
        EOT
      ]
      volume_mounts {
        name = "airflow-data"
        path = "/opt/airflow/data"
      }
    }

    volume {
      name         = "airflow-data"
      storage_type = "AzureFile"
      storage_name = azurerm_container_app_environment_storage.airflow.name
    }
  }

  replica_timeout_in_seconds = 300
  replica_retry_limit        = 1
}

# Permite o job de init ler do ACR (mesma identidade)
resource "azurerm_role_assignment" "airflow_init_acr" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_container_app_job.airflow_init.identity[0].principal_id
}

# Webserver (UI) — sem acesso ao storage (só agendamento/visual)
resource "azurerm_container_app" "airflow_webserver" {
  name                         = "${var.project_name}-airflow-web-${local.suffix}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "airflow-webserver"
      image  = local.airflow_image
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"
        value = "sqlite:////opt/airflow/data/airflow.db"
      }
      env {
        name  = "AIRFLOW__CORE__EXECUTOR"
        value = "SequentialExecutor"
      }
      env {
        name  = "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION"
        value = "false"
      }
      env {
        name  = "AIRFLOW__API__AUTH_BACKENDS"
        value = "airflow.api.auth.backend.basic_auth"
      }
      env {
        name  = "PYTHONPATH"
        value = "/opt/airflow/project"
      }

      volume_mounts {
        name = "airflow-data"
        path = "/opt/airflow/data"
      }
    }

    volume {
      name         = "airflow-data"
      storage_type = "AzureFile"
      storage_name = azurerm_container_app_environment_storage.airflow.name
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    transport        = "http"
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

# Scheduler — executa os DAGs; precisa de acesso ao lake (ADLS) + ACR
resource "azurerm_container_app" "airflow_scheduler" {
  name                         = "${var.project_name}-airflow-scheduler-${local.suffix}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "airflow-scheduler"
      image  = local.airflow_image
      cpu    = 0.5
      memory = "2Gi"

      env {
        name  = "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"
        value = "sqlite:////opt/airflow/data/airflow.db"
      }
      env {
        name  = "AIRFLOW__CORE__EXECUTOR"
        value = "SequentialExecutor"
      }
      env {
        name  = "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION"
        value = "false"
      }
      env {
        name  = "AIRFLOW__API__AUTH_BACKENDS"
        value = "airflow.api.auth.backend.basic_auth"
      }
      # Serving: espelho batch das transações no MongoDB (mesma stack)
      env {
        name  = "MONGODB_URI"
        value = local.mongodb_uri
      }
      env {
        name  = "KAFKA_BOOTSTRAP_SERVERS"
        value = local.kafka_bootstrap
      }
      # Pipeline escreve no ADLS
      env {
        name  = "LAKE_BASE_URI"
        value = local.lake_uri
      }
      env {
        name  = "LANDING_BASE_URI"
        value = "${local.lake_uri}/landing"
      }
      env {
        name  = "PROJECT_ROOT"
        value = "/opt/airflow/project"
      }
      env {
        name  = "PYTHONPATH"
        value = "/opt/airflow/project"
      }

      volume_mounts {
        name = "airflow-data"
        path = "/opt/airflow/data"
      }
    }

    volume {
      name         = "airflow-data"
      storage_type = "AzureFile"
      storage_name = azurerm_container_app_environment_storage.airflow.name
    }
  }

  tags = azurerm_resource_group.main.tags

  lifecycle {
    ignore_changes = [template[0].container[0].image]
  }
}

# Acesso do scheduler ao ADLS (escreve bronze/silver/gold + reports)
resource "azurerm_role_assignment" "airflow_scheduler_storage" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_container_app.airflow_scheduler.identity[0].principal_id
}
