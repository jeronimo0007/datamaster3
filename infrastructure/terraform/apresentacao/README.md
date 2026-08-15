# Terraform Azure — mesma stack do Docker Compose

| Local | Azure (este módulo) |
|-------|---------------------|
| Kafka | **Kafka** (ACI `bitnami/kafka`) |
| MongoDB | **MongoDB** (ACI `mongo:6.0`) |
| MinIO / lake | **ADLS Gen2** (filesystem `lake`: `landing`/`bronze`/`silver`/`gold`) |
| api-java | Container Apps + ACR |
| Airflow (webserver/scheduler) | Container Apps + Job de init (mesma imagem) |

**Não provisiona:** Event Hubs, Cosmos DB, PostgreSQL, DocumentDB.

O Airflow roda o MESMO pipeline do Docker local: ingestão multi-formato
(JSON/CSV/Parquet/XML) + Medallion (Bronze → DQ → Silver → Gold) no ADLS,
usando Managed Identity + `Storage Blob Data Contributor`.

```bash
cd infrastructure/terraform/apresentacao
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform plan && terraform apply
```

Dependências (no Worker/job de dados):
- `fsspec` + `adlfs` (leitura/escrita `abfss://`)
- `pandas` + `pyarrow` (backends Bronze/Silver/Gold)

Pipeline via CI: `.github/workflows/deploy-azure.yml`.
