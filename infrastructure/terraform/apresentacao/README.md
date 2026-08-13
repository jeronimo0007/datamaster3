# Terraform Azure — mesma stack do Docker Compose

| Local | Azure (este módulo) |
|-------|---------------------|
| Kafka | **Kafka** (ACI `bitnami/kafka`) |
| MongoDB | **MongoDB** (ACI `mongo:6.0`) |
| MinIO / lake | **ADLS Gen2** (`landing`/`bronze`/`silver`/`gold`) |
| api-java | Container Apps + ACR |
| Airflow / Spark | mesmos containers (expandir ACI/AKS se precisar na demo) |

**Não provisiona:** Event Hubs, Cosmos DB, PostgreSQL, DocumentDB.

```bash
cd infrastructure/terraform/apresentacao
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform plan && terraform apply
```
