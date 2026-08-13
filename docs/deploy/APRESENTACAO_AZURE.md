# Deploy Azure — mesma stack do Docker

Terraform: `infrastructure/terraform/apresentacao`

Sobe:
- ADLS (`landing` / `bronze` / `silver` / `gold`)
- **MongoDB** (ACI `mongo:6.0`)
- **Kafka** (ACI)
- ACR + Container Apps (API)
- Key Vault + Monitor

Não sobe Event Hubs, Cosmos nem PostgreSQL.

```bash
cd infrastructure/terraform/apresentacao
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform apply
```

Tabela multiplataforma: [readme.md](../../readme.md).
