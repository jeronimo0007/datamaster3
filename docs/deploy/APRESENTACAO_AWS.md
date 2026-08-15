# Deploy AWS — mesma stack do Docker (pipeline completo)

Terraform: `infrastructure/terraform/aws`

A AWS sobe a **mesma stack** do Docker local e da Azure — sem serviços equivalentes:

| Componente | AWS (este módulo) |
|------------|-------------------|
| Kafka | Kafka KRaft (ECS Fargate `bitnami/kafka:3.6`) |
| MongoDB | MongoDB (ECS Fargate `mongo:6.0`) |
| Data Lake | **S3** — prefixes `landing/bronze/silver/gold` |
| Airflow | ECS Fargate (webserver + scheduler) + task de init + EFS |
| api-java | ECS Fargate + ALB + ECR |
| Service discovery | Cloud Map (`*.datamaster.local`) |

**Não provisiona:** MSK, DocumentDB, DynamoDB, Kinesis, RDS/Postgres.

## O que o pipeline faz na AWS

Após o `terraform apply`, o GitHub Actions (`deploy-aws.yml`):

1. Builda e sobe para o ECR a **imagem custom do Airflow** (`airflow/Dockerfile`),
   que contém os DAGs + o código do pipeline (src/scripts/config) + `s3fs`.
2. Atualiza webserver e scheduler para essa imagem.
3. Executa a **task de init** (migra o SQLite no EFS + cria usuário `admin`).
4. Dispara os DAGs via API:
   - `ingest_multi_source` → dados públicos (CSV/JSON OpenML) + sintético
     em **4 formatos** (JSON, CSV, Parquet, XML) no S3 `landing/run=*/`.
   - `medallion_pipeline` → **Bronze → DQ gate → Silver (harmonização) → Gold**,
     gravando Parquet no S3 `{bronze,silver,gold}/`.
5. O scheduler usa **IAM task role** com acesso de leitura/escrita ao bucket do lake
   (mesmo papel da Managed Identity na Azure).

## Deploy local (CLI)

```bash
cd infrastructure/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# edite lake_bucket_name, mongo_admin_password e airflow_admin_password
terraform init && terraform apply
```

## GitHub Actions (branch `aws` ou merge em `main`)

- Branch `aws` → só AWS (`deploy-aws.yml`)
- Merge/push em `main` → **Azure ∥ AWS em paralelo** (`deploy-main.yml`)

Secrets obrigatórios:

- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
- `AWS_LAKE_BUCKET_NAME` (nome globalmente único do bucket)
- `TF_VAR_mongo_admin_password`
- `TF_VAR_airflow_admin_password`

## Credenciais da UI do Airflow

- URL: output `airflow_webserver_url` (via `terraform output`)
- Usuário: `admin` · Senha: `TF_VAR_airflow_admin_password`

Tabela multiplataforma: [readme.md](../../readme.md).
