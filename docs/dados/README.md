# Domínio: Dados

Engenharia de dados e lake Medallion. A referência principal é o [README raiz](../../readme.md).

## Documentos

| Documento | Conteúdo |
|-----------|----------|
| [../operacao/SERVICOS_DOCKER.md](../operacao/SERVICOS_DOCKER.md) | Spark, Jupyter, Mongo, MinIO |
| [../arquitetura/README.md](../arquitetura/README.md) | Diagramas de arquitetura |

## Scripts e artefatos

| Caminho | Função |
|---------|--------|
| `scripts/ingest_landing.py` | Landing multi-formato (JSON/CSV/Parquet/XML) |
| `scripts/medallion_job.py` | Medallion Bronze → DQ → Silver → Gold |
| `scripts/batch_dataprep_mongo.py` | Agregação por `user_id` → `user_profiles` |
| `notebooks/01_dataprep_dq.py` | DQ (versão cloud) |

## Diagramas

[../arquitetura/README.md](../arquitetura/README.md)

[← Índice geral](../README.md)
