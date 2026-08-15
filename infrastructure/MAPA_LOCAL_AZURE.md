# Mapa multiplataforma — mesma stack, não “equivalentes”

Princípio: **o que roda no Docker local sobe igual na nuvem**.

| Componente | Docker local | Azure | AWS |
|------------|--------------|-------|-----|
| Orquestração | **Apache Airflow** | **Apache Airflow** (Container Apps + Job init) | **Apache Airflow** (ECS Fargate + task init + EFS) |
| Processamento | **Spark / pandas** | **Spark / pandas** (mesmo job por camada) | **Spark / pandas** (mesmo job) |
| Streaming | **Kafka** | **Kafka** (ACI) | **Kafka** (ECS) |
| Perfis / NoSQL | **MongoDB** | **MongoDB** (ACI) | **MongoDB** (ECS) |
| Object storage (lake) | **MinIO** (`landing/bronze/silver/gold`) | **ADLS Gen2** (filesystem `lake`) | **S3** (mesmos paths) |
| Serving API | api-java | api-java (Container Apps) | api-java (ECS + ALB) |
| IaC | `docker-compose.yaml` | `infrastructure/terraform/apresentacao` | `infrastructure/terraform/aws` |

**Não usamos:** Event Hubs/MSK no lugar de Kafka, Cosmos/DocumentDB no lugar de Mongo, Postgres/Redis na arquitetura de dados, VPS/k3s.

## Fluxo (igual em todo ambiente)

```text
Fontes → landing (JSON/CSV/Parquet/XML)
  → Airflow: Bronze → DQ gate → Silver → Gold
  → Kafka (eventos) + MongoDB (perfis) + API (serving)
```

## Comandos

```bash
docker compose up -d --build
# Airflow http://localhost:8085 — DAG datamaster_e2e
python3 scripts/ingest_landing.py
python3 scripts/medallion_job.py all
```

## Pipeline na Azure (mesma stack)

```bash
# 1) Deploy da infra via CI (branch azure) ou CLI:
cd infrastructure/terraform/apresentacao && terraform apply

# 2) No GitHub Actions, a imagem custom do Airflow é buildada/sobe pro ACR,
#    o Job de init roda e os DAGs são disparados via API:
#    ingest_multi_source → landing (JSON/CSV/Parquet/XML) no ADLS lake/landing
#    medallion_pipeline → Bronze → DQ → Silver → Gold no ADLS lake/{camada}

# O scheduler usa Managed Identity (Storage Blob Data Contributor) p/ acessar o ADLS.
```

## Pipeline na AWS (mesma stack)

```bash
# 1) Deploy da infra via CI (branch aws) ou CLI:
cd infrastructure/terraform/aws && terraform apply

# 2) No GitHub Actions, a imagem custom do Airflow é buildada/sobe pro ECR,
#    a task de init roda e os DAGs são disparados via API:
#    ingest_multi_source → landing no S3 bucket/landing
#    medallion_pipeline → Bronze → DQ → Silver → Gold no S3 bucket/{camada}

# O scheduler usa IAM task role com leitura/escrita no bucket S3 (s3fs/fsspec).
```
