# Tópico 3 — Armazenamento (slides 7, 7c, 7b)

## 1. O que é
Onde o dado **fica** e **como é servido**: lake (histórico), DW (analítico), NoSQL (online), OLTP (relacional).

## 2. Problema que resolve
Um único banco não atende: histórico barato + reprocessamento **e** leitura de perfil em milissegundos **e** modelo relacional de auditoria.

## 3. Componentes usados
| Store | Uso no DataMaster |
|-------|-------------------|
| `data/lake/` + MinIO | Medallion Bronze/Silver/Gold |
| Spark | Processa e materializa o lake |
| MongoDB `user_profiles` | Serving online do `/analyze` |
| PostgreSQL | OLTP de referência (schema demo) |
| Narrativa Synapse/Redshift | DW dimensional (Kimball) |

## 4. Por que cada um
- **Lake + Spark:** histórico, schema-on-read, reprocessamento, features para ML.  
- **MinIO:** object storage S3-compatível na mesa (= ADLS/S3).  
- **Mongo:** documento por `user_id`, flexível, leitura rápida no scoring.  
- **Postgres:** mostra fronteira OLTP (transação/alerta/auditoria) — **não** é o banco do scoring na demo.  
- **Dois braços batch:** Spark → lake analítico; `batch_dataprep_mongo` → perfis online.

## 5. Onde entra
Centro da plataforma: ingestão grava; processamento refina; API lê perfil; BI lê Gold/DW.

## 6. Local
```text
transactions.json → spark_local_pipeline.py → data/lake/{bronze,silver,gold}
transactions.json → batch_dataprep_mongo.py → Mongo user_profiles → POST /analyze
Postgres: schema seed (mostrar \dt) — API local não grava scoring nele
```

## 7. Azure / AWS
| Local | Azure | AWS |
|-------|-------|-----|
| data/lake + MinIO | ADLS Gen2 | S3 |
| Spark | Databricks | EMR / Glue Spark |
| Mongo | Cosmos (API Mongo / SQL) | DocumentDB / DynamoDB |
| Postgres | Flexible Server | RDS Aurora |
| DW narrativa | Synapse / Fabric | Redshift / Athena |

## 8. Alternativa e trade-off
| Alternativa | Trade-off |
|-------------|-----------|
| Tudo no Postgres | Simples; não escala lake/ML nem features flexíveis |
| Tudo no Mongo | Bom serving; fraco para SQL analítico/Kimball |
| Só lake sem serving store | Bom para treino; `/analyze` ficaria lento (scan) |
| Feature store dedicada | Ideal em produção; Mongo cobre o POC com clareza |

## 9. Como demonstrar
- T9: `ls data/lake/bronze silver gold` + Spark UI + Jupyter  
- T3: `profile-stats` > 0  
- T5–T6: analyze com/sem perfil  
- Opcional: `psql` e `\dt` — “OLTP de referência”

## 10. Fala
> “Separei armazenamento por carga: lake para histórico e reprocessamento, Mongo para perfil na decisão online, Postgres para o desenho OLTP. O scoring usa Mongo — não o Postgres.”

## 11. Perguntas
| Pergunta | Resposta |
|----------|----------|
| API usa Postgres? | Não no perfil local; scoring = Mongo + heurística |
| Por que Medallion? | Qualidade progressiva; Bronze intacto para reprocessar |
| MinIO vs pasta local? | Pasta prova o pipeline; MinIO prova object storage cloud |

## 12. Transição
> “Com dados fluindo e armazenados, preciso **provar saúde** — métricas, dashboards, SLO. Observabilidade.”

**Próximo:** [topico-04-observabilidade.md](topico-04-observabilidade.md)
