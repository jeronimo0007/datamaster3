# Spark — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Processamento **batch distribuído** — pipeline Medallion |
| **Containers** | `spark-master`, `spark-worker` |
| **UI** | http://localhost:18080 (master mapeia 8080→18080) |
| **Master RPC** | `spark://spark-master:7077` |
| **Imagem** | `bitnamilegacy/spark:3.5.5` |
| **Job** | `scripts/spark_local_pipeline.py` (serviço `spark-job`) |
| **Equivalente Azure** | Databricks / Synapse Spark |

Frase curta:

> *"Batch distribuído — histórico vira lake Bronze, Silver, Gold."*

---

## Onde entra na arquitetura

```text
data/transactions.json
        │
        ▼
spark_local_pipeline.py  (spark-job / Jupyter / spark-submit)
        │
        ├── Bronze  (landing)
        ├── Silver  (limpo)
        └── Gold    (features ML)
        │
        ▼
   data/lake/ + relatório DQ
```

Paralelo: `batch_dataprep_mongo.py` alimenta Mongo (perfis), Spark alimenta lake (features).

---

## Demo prática (5 min)

### 1. Spark UI (1 min)

http://localhost:18080

Mostre:

- **Workers** — 1 worker conectado
- **Running / Completed Applications** — jobs recentes

### 2. Rodar pipeline (2 min)

```bash
# Pré-requisito: data/transactions.json
python3 scripts/generate_data.py -n 500 -o data/transactions.json 2>/dev/null || true

docker compose --profile spark-run run --rm spark-job
```

Ou via fluxo completo:

```bash
bash scripts/run_demo.sh
```

### 3. Validar saídas (1 min)

```bash
ls -R data/lake/bronze data/lake/silver data/lake/gold | head -30
cat data/lake/reports/dq_latest.json | python3 -m json.tool | head -20
```

### 4. Correlacionar UI + arquivos (1 min)

Volte ao Spark UI → abra application concluída → Stages/Duration.

---

## Comandos úteis

```bash
docker compose ps spark-master spark-worker
docker compose logs spark-master --tail 20
curl -s http://localhost:18080 | head -5
```

---

## Roteiro de fala (30 s)

> *"Spark é a batch layer — processa o histórico em escala. Master coordena, worker executa. O job local replica o que rodaria no Databricks: ingestão, limpeza, enriquecimento e camada Gold para ML. A UI prova que foi distribuído."*

---

## Perguntas frequentes

| Pergunta | Resposta |
|----------|----------|
| Spark vs Jupyter? | Mesmo cluster; Jupyter = interativo, spark-job = automatizado |
| Worker não aparece? | `docker compose up -d spark-master spark-worker` |

---

## Por que Spark

| Motivo | Detalhe |
|--------|---------|
| Problema | Processar histórico e materializar Bronze→Silver→Gold em volume |
| Escolha | Spark distribuído (Databricks/EMR na nuvem) |
| Alternativa | Pandas só | Trade-off: simples no notebook, não escala nem espelha produção |
| Alternativa | Só SQL no DW | Trade-off: bom para BI; fraco para pipeline de features no lake |

Pergunta: *"Por que não só o notebook?"* → *"Jupyter explora; `spark_local_pipeline.py` / job automatiza o Medallion."*

## Checklist

- [ ] Spark UI :18080 abre com worker
- [ ] Executei `spark-job` ou `run_demo.sh`
- [ ] 3 camadas em `data/lake/`
- [ ] Mostrei job na UI

---

## Referências

- `scripts/spark_local_pipeline.py`
- `docker/spark-job-entrypoint.sh`
- `docs/dados/LOCAL_SPARK.md`
- `docs/estudos/jupyter.md` — execução interativa
