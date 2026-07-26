# Tópico 7 — Arquitetura de dados (slide 11)

## 1. O que é
Como o dado é **organizado e modelado** ao longo do ciclo: Medallion (engenharia), Kimball (consumo analítico), features/perfis (serving).

## 2. Problema que resolve
Sem arquitetura, vira “pasta de CSV”: sem qualidade, sem reprocessamento confiável, sem estrela para BI, sem feature pronta para o online.

## 3. Componentes usados
| Peça | Papel |
|------|--------|
| Medallion Bronze→Silver→Gold | Qualidade progressiva no lake |
| `medallion.py` / `medallion.yaml` | Paths e contratos |
| Notebook `01_dataprep_dq.py` | Limpeza, enrich, expectativas DQ |
| Kimball (narrativa) | Fato transações + dimensões |
| `user_profiles` (Mongo) | Feature store leve para `/analyze` |
| `governanca.yaml` + `/data-quality/report` | Governança e qualidade |

## 4. Por que cada um
- **Medallion:** Bronze intacto (auditoria/replay); Silver confiável; Gold pronto para ML/BI.  
- **Kimball:** BI e negócios pensam em fatos/dimensões — Synapse/Redshift.  
- **Perfis/features no Mongo:** o online não faz full scan no lake a cada transação.  
- **Contratos DQ:** qualidade é regra, não “esperança no job”.

## 5. Onde entra
Depois de armazenar: define **como** o dado evolui e **quem** consome (treino, API, BI).

## 6. Local
```bash
curl -s http://localhost:8080/api/v1/data-quality/report | python3 -m json.tool
ls data/lake/bronze data/lake/silver data/lake/gold
# Abrir governanca.yaml e notebooks/01_dataprep_dq.py
```

## 7. Azure / AWS
| Conceito | Azure | AWS |
|----------|-------|-----|
| Lake + Delta | ADLS + Databricks | S3 + EMR/Glue + Delta |
| DW Kimball | Synapse / Fabric | Redshift |
| Catálogo | Purview | Glue Catalog + Lake Formation |
| Features online | Cosmos | DynamoDB / Feature Store |

## 8. Alternativa e trade-off
| Alternativa | Trade-off |
|-------------|-----------|
| Só Data Vault | Auditoria forte; mais complexo para BI ad hoc |
| Só Wide table única | Rápido no POC; vira caos de qualidade |
| Feature store Feast/Tecton | Produção ML madura; overkill se Mongo resolve o caso |

## 8b. Mapa de arquiteturas (não misture)

| Pergunta | Família | DataMaster |
|----------|---------|------------|
| Como entra/processa no tempo? | **Lambda** / Kappa | Lambda (speed + batch) |
| Como ganha qualidade no lake? | **Medallion** | B→S→G |
| Como BI modela consulta? | **Kimball** / Data Vault | Narrativa DW |
| Como online serve feature? | Feature store / perfil | Mongo |

**Lambda/streaming são arquitetura?** Sim — de *pipeline*. Medallion = lake. Kimball = modelo analítico. **Se complementam**, não se substituem.

**Por que Medallion:** landing imutável + DQ progressivo + Gold pronta p/ ML/BI. Wide table = caos. Data Vault = overkill p/ BI. Só Kimball = não resolve landing/online. Kappa = features históricas caras.

## 9. Como demonstrar
- Curl DQ report  
- Pastas Medallion  
- Relacionar Gold (treino) × Mongo (serving) — **dois destinos, um histórico**

## 10. Fala
> “Arquitetura de dados em três ideias: Medallion organiza qualidade no lake; Kimball organiza o consumo analítico; e o perfil no Mongo é a feature de serving. Gold alimenta retreino; `user_profiles` alimenta o `/analyze`.”

## 11. Perguntas
| Pergunta | Resposta |
|----------|----------|
| Medallion substitui Kimball? | Não — um é pipeline/lake; outro é modelo dimensional |
| Onde está o fato/dimensão no código? | Narrativa DW; local mostro Gold + schema Postgres de referência |
| O que é anomaly_score_boost? | Desvio vs perfil histórico materializado no batch |

## 12. Transição
> “Com o modelo definido, a pergunta é: **isso cresce?** Escalabilidade.”

**Próximo:** [topico-08-escalabilidade.md](topico-08-escalabilidade.md)
