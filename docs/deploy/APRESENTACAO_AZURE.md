# Deploy Azure — mesma stack do Docker

Terraform: `infrastructure/terraform/apresentacao`

Sobe:
- ADLS (`landing` / `bronze` / `silver` / `gold`)
- **MongoDB** (ACI `mongo:6.0`) — senha via `mongo_admin_password` no tfvars
- **Kafka** (ACI)
- ACR + Container Apps (API)
- Key Vault + Monitor

Não sobe Event Hubs, Cosmos nem PostgreSQL.

```bash
cd infrastructure/terraform/apresentacao
cp terraform.tfvars.example terraform.tfvars
# edite mongo_admin_password em terraform.tfvars
terraform init && terraform apply
```

## GitHub Actions (branch `azure`)

- Secret obrigatório: `TF_VAR_mongo_admin_password` (senha do MongoDB na Azure).
- Secrets de identidade: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` (OIDC).
- A stack analítica (`Databricks/Synapse/ML`) fica desligada por padrão (`enable_analytics_stack = false`).

Tabela multiplataforma: [readme.md](../../readme.md).
