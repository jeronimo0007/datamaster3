# Mapa multiplataforma — mesma stack, não “equivalentes”

Princípio: **o que roda no Docker local sobe igual na nuvem**.

| Componente | Docker local | Azure | AWS (preparado) |
|------------|--------------|-------|-----------------|
| Orquestração | **Apache Airflow** | **Apache Airflow** (Container Apps / AKS) | **Apache Airflow** (ECS / EKS) |
| Processamento | **Spark** | **Spark** | **Spark** |
| Streaming | **Kafka** | **Kafka** | **Kafka** |
| Perfis / NoSQL | **MongoDB** | **MongoDB** | **MongoDB** |
| Object storage (lake) | **MinIO** (`landing/bronze/silver/gold`) | **ADLS Gen2** (mesmos paths) | **S3** (mesmos paths) |
| Serving API | api-java | api-java (Container Apps) | api-java (ECS/EKS) |
| IaC | `docker-compose.yaml` | `infrastructure/terraform/apresentacao` | `infrastructure/terraform/aws` |

**Não usamos:** Event Hubs no lugar de Kafka, Cosmos/DocumentDB no lugar de Mongo, Postgres/Redis na arquitetura de dados, VPS/k3s.

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
