# Terraform AWS — stack preparada (mesma do Docker)

Princípio do projeto: **não trocar componentes**.

| Local | AWS |
|-------|-----|
| Kafka | **Kafka** (ECS/EKS / EC2 — não MSK como “substituto narrativo”; se usar MSK, é Kafka) |
| MongoDB | **MongoDB** (Atlas ou container — **não** DocumentDB/Dynamo) |
| MinIO / lake | **S3** (mesmo layout `landing/bronze/silver/gold`) |
| Airflow | **Airflow** |
| Spark | **Spark** |
| api-java | ECS / EKS |

Este módulo provisiona o **lake em S3** (ponto de partida). Expandir com containers Kafka + Mongo iguais ao `docker-compose.yaml`.

```bash
cd infrastructure/terraform/aws
cp terraform.tfvars.example terraform.tfvars   # ajuste lake_bucket_name (globalmente único)
terraform init && terraform plan && terraform apply
```

CI: branch `aws` → `.github/workflows/deploy-aws.yml`.

Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_LAKE_BUCKET_NAME`.
