# MinIO — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Object storage **S3-compatível** — lake Bronze/Silver/Gold |
| **Container** | `minio` |
| **Portas** | **9000** (API S3), **9001** (Console UI) |
| **Credenciais** | `minioadmin` / `minioadmin` |
| **Equivalente Azure** | ADLS Gen2 |
| **Equivalente AWS** | S3 |

Frase curta:

> *"Data lake em object storage — camadas Medallion como buckets."*

---

## Onde entra na arquitetura

```text
Spark / pipeline batch  ──►  data/lake/ (volume host)
                         └──►  MinIO buckets bronze / silver / gold (narrativa S3)
```

Na demo local, os arquivos ficam em **`data/lake/`** no host. MinIO representa o **destino em nuvem** (ADLS/S3).

---

## Demo prática (4 min)

### 1. Console web

http://localhost:9001  
Login: `minioadmin` / `minioadmin`

Mostre buckets (se existirem): `bronze`, `silver`, `gold`.

### 2. Lake no host (principal na demo)

```bash
ls -la data/lake/
ls -la data/lake/bronze data/lake/silver data/lake/gold
cat data/lake/reports/dq_latest.json 2>/dev/null | python3 -m json.tool | head -30
```

### 3. Após pipeline Spark

```bash
bash scripts/run_demo.sh
# ou
docker compose --profile spark-run run --rm spark-job
```

Confirme parquet/arquivos nas 3 camadas.

### 4. Prova rápida (compose tour)

```bash
docker exec minio mc ls local/ 2>/dev/null || echo "Use console :9001 ou data/lake/ no host"
```

---

## Camadas Medallion

| Camada | Conteúdo |
|--------|----------|
| **Bronze** | Landing bruto (JSON/parquet raw) |
| **Silver** | Limpo, deduplicado, enriquecido |
| **Gold** | Features para ML (`transactions_ml`) |

Script: `scripts/spark_local_pipeline.py`

---

## Roteiro de fala (30 s)

> *"MinIO simula ADLS ou S3 na mesa. O pipeline Spark materializa Bronze, Silver e Gold — o padrão Medallion. Localmente vemos em `data/lake/`; em Azure seria `abfss://` no Databricks."*

---

## Por que MinIO (+ data/lake/)

| Motivo | Detalhe |
|--------|---------|
| Problema | Lake precisa de object storage (padrão cloud) |
| Escolha | MinIO S3-compatível = ADLS/S3 na mesa; arquivos também em `data/lake/` |
| Trade-off | Só pasta local prova pipeline, não o protocolo S3 |

## Checklist

- [ ] Console MinIO :9001 abre
- [ ] Mostrei `data/lake/` com 3 camadas após Spark
- [ ] Mencionei relatório DQ em `reports/dq_latest.json`
- [ ] Equivalência ADLS/S3

---

## Referências

- `scripts/spark_local_pipeline.py`
- `config/medallion.yaml`
- `docs/dados/LOCAL_SPARK.md`
