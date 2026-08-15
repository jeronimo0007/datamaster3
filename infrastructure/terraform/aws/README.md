# Terraform AWS — mesma stack do Docker / Azure

Princípio: **não trocar componentes**. Kafka = Kafka, Mongo = Mongo, Airflow = Airflow.

| Componente | AWS (este módulo) |
|------------|-------------------|
| Kafka | Kafka KRaft (`bitnami/kafka:3.6` no ECS Fargate) |
| MongoDB | MongoDB (`mongo:6.0` no ECS Fargate) |
| Data Lake | **S3** — prefixes `landing/bronze/silver/gold/reports` |
| Airflow | ECS Fargate (webserver + scheduler) + task de init + EFS (SQLite) |
| api-java | ECS Fargate + ALB (`/api/*`, `/health`) |
| Registry | ECR (`datamaster-airflow`, `datamaster-api`) |

**Não provisiona:** MSK “no lugar de” Kafka, DocumentDB, DynamoDB, Kinesis, RDS/Postgres.

## O que o pipeline faz na AWS

Após o `terraform apply`, o GitHub Actions (`deploy-aws.yml`):

1. Builda e sobe para o ECR a **imagem custom do Airflow** (`airflow/Dockerfile`),
   com DAGs + código + `s3fs`/`boto3`.
2. Atualiza task definitions / services do webserver e scheduler.
3. Executa a **task de init** (migra o SQLite no EFS + cria usuário `admin`).
4. Dispara os DAGs via API:
   - `ingest_multi_source` → landing em `s3://bucket/landing/run=*/`
   - `medallion_pipeline` → Bronze → DQ → Silver → Gold em `s3://bucket/{camada}/`
5. O scheduler usa a **task role IAM** com permissão de leitura/escrita no bucket S3
   (espelho da Managed Identity na Azure).

## Deploy local (CLI)

```bash
cd infrastructure/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# edite lake_bucket_name, mongo_admin_password, airflow_admin_password
terraform init && terraform plan && terraform apply
```

## GitHub Actions (branch `aws`)

Secrets obrigatórios:

| Secret | Uso |
|--------|-----|
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Credenciais AWS |
| `AWS_LAKE_BUCKET_NAME` | Nome único do bucket S3 |
| `TF_VAR_mongo_admin_password` | Senha root do MongoDB |
| `TF_VAR_airflow_admin_password` | Senha admin do Airflow |

## Credenciais da UI do Airflow

- URL: output `airflow_webserver_url`
- Usuário: `admin` · Senha: `TF_VAR_airflow_admin_password`

Tabela multiplataforma: [readme.md](../../../readme.md) · mapa: [MAPA_LOCAL_AZURE.md](../../MAPA_LOCAL_AZURE.md)
