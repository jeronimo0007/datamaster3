# Deploy Azure — mesma stack do Docker (pipeline completo)

Terraform: `infrastructure/terraform/apresentacao`

A Azure sobe a **mesma stack** do Docker local — sem serviços equivalentes:

| Componente | Azure (este módulo) |
|------------|---------------------|
| Kafka | Kafka KRaft (ACI `bitnami/kafka:3.6`) |
| MongoDB | MongoDB (ACI `mongo:6.0`) |
| Data Lake | **ADLS Gen2** — filesystem `lake` com `landing/bronze/silver/gold` |
| Airflow | Container Apps (webserver + scheduler) + Job de init |
| api-java | Container Apps + ACR |
| Observabilidade | Log Analytics + Application Insights |

**Não provisiona:** Event Hubs, Cosmos DB, PostgreSQL, DocumentDB, Kinesis.

## O que o pipeline faz na Azure

Após o `terraform apply`, o GitHub Actions (`deploy-azure.yml`):

1. Builda e sobe para o ACR a **imagem custom do Airflow** (`airflow/Dockerfile`),
   que contém os DAGs + o código do pipeline (src/scripts/config).
2. Atualiza webserver e scheduler para essa imagem.
3. Executa o **Job de init** (migra o SQLite + cria usuário `admin`).
4. Dispara os DAGs via API:
   - `ingest_multi_source` → baixa dados públicos (CSV/JSON OpenML) + sintético
     e escreve **4 formatos** (JSON, CSV, Parquet, XML) no ADLS `lake/landing/run=*/`.
   - `medallion_pipeline` → **Bronze → DQ gate → Silver (harmonização) → Gold**,
     gravando Parquet no ADLS `lake/{bronze,silver,gold}/`.
5. O scheduler usa **Managed Identity** com role
   `Storage Blob Data Contributor` no storage account para ler/escrever no lake.

## Deploy local (CLI)

```bash
cd infrastructure/terraform/apresentacao
cp terraform.tfvars.example terraform.tfvars
# edite mongo_admin_password e airflow_admin_password
terraform init && terraform apply
```

## GitHub Actions (branch `azure` ou merge em `main`)

- Branch `azure` → só Azure (`deploy-azure.yml`)
- Merge/push em `main` → **Azure ∥ AWS em paralelo** (`deploy-main.yml` chama os dois submódulos)
- Secrets obrigatórios:
  - `TF_VAR_mongo_admin_password` (senha do MongoDB)
  - `TF_VAR_airflow_admin_password` (senha admin do Airflow na Azure)
- Secrets de identidade: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` (OIDC).
- A stack analítica (`Databricks/Synapse/ML`) fica desligada por padrão
  (`enable_analytics_stack = false`).

## Credenciais da UI do Airflow

- URL: output `airflow_webserver_url` (via `terraform output`)
- Usuário: `admin` · Senha: `TF_VAR_airflow_admin_password`

Tabela multiplataforma: [readme.md](../../readme.md).
