# Deploy

Ambientes: **Docker local**, **Azure**, **AWS**. Sem VPS/k3s.

| Documento | Conteúdo |
|-----------|----------|
| [APRESENTACAO_AZURE.md](APRESENTACAO_AZURE.md) | Terraform Azure + Actions (pipeline completo) |
| [APRESENTACAO_AWS.md](APRESENTACAO_AWS.md) | Terraform AWS + Actions (pipeline completo) |
| [../../infrastructure/terraform/aws/README.md](../../infrastructure/terraform/aws/README.md) | Detalhe do módulo AWS |
| [../../infrastructure/MAPA_LOCAL_AZURE.md](../../infrastructure/MAPA_LOCAL_AZURE.md) | Tabela Local \| Azure \| AWS |

**CI na `main`:** `.github/workflows/deploy-main.yml` sobe **Azure e AWS em paralelo**
(submódulos `deploy-azure.yml` ∥ `deploy-aws.yml`). Branches `azure` / `aws` disparam só a cloud respectiva.

Stack obrigatória em todos: **Kafka, MongoDB, Airflow, Spark, object storage (MinIO/ADLS/S3)**.

[← Índice](../README.md)
