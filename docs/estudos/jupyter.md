# Jupyter no DataMaster — guia de estudo e demo

Material pessoal de estudo (pasta não versionada). Orientação prática para explicar o componente na banca.

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Explorar dados, rodar PySpark no cluster, validar DQ (data quality) |
| **Container** | `fraud-jupyter` |
| **Imagem** | `jupyter/pyspark-notebook:spark-3.5.0` |
| **URL** | http://localhost:8888/?token=datamaster |
| **Arquivo principal** | `notebooks/01_dataprep_dq.py` (formato Databricks, não `.ipynb`) |
| **Equivalente em produção** | Databricks / Synapse (Azure) ou EMR (AWS) |

Frase curta para a banca (do roteiro do projeto):

> *"Engenharia interativa — notebook de data prep e data quality no lake Medallion."*

---

## Onde o Jupyter entra na arquitetura

```text
[data/transactions.json]
        │
        ├── batch_dataprep_mongo.py  →  MongoDB (perfis online)
        │
        └── Spark (batch)  →  data/lake/  (Bronze → Silver → Gold)
                 ▲
                 │
            [Jupyter]  ← você explora e roda isso de forma interativa
```

- **API Java (:8080)** = scoring em tempo real (online)
- **Spark + Jupyter** = batch e lakehouse (offline)
- O README deixa claro: a plataforma **não é só um notebook de ML** — o Jupyter é uma **peça de engenharia**, não o artefato final.

---

## Pré-requisito: stack no ar

Se ainda não subiu:

```bash
bash scripts/run_demo.sh
# ou
docker compose up -d --build
```

Confirme que o Jupyter está healthy:

```bash
docker compose ps | grep jupyter
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8888/?token=datamaster"
# esperado: 200 ou 302
```

---

## Demo prática — passo a passo (≈ 5–8 min)

### 1. Abrir e contextualizar (30 s)

1. Abra http://localhost:8888/?token=datamaster
2. Mostre a pasta **`work/`** — é o repositório montado dentro do container (`.:/home/jovyan/work` no `docker-compose.yaml`).

**O que dizer:**

*"O notebook roda dentro do Docker, mas enxerga o código e os dados do host. O Spark usa o cluster `spark-master:7077`, não roda só na máquina local."*

### 2. Mostrar o notebook de DQ (2 min)

Navegue até: **`work/notebooks/01_dataprep_dq.py`**

Abra e comente **só o topo** (não precisa executar tudo):

- Comentários sobre **Medallion**: Bronze → Silver → Gold
- Classe `AzureDataPrep` com paths `abfss://` (Azure Data Lake)
- Great Expectations para validação de qualidade

**O que dizer:**

*"Este arquivo foi escrito para Databricks. Mostra o desenho alvo em nuvem. Localmente usamos o script adaptado `scripts/spark_local_pipeline.py`."*

Isso conecta **notebook (experimentação)** com **job batch (produção/demo)**.

### 3. Rodar o pipeline local pelo Jupyter (3 min) — o “wow”

Abra um **novo notebook** (File → New → Notebook) e execute célula a célula:

**Célula 1 — conectar ao cluster Spark:**

```python
import os
os.environ["SPARK_MASTER_URL"] = "spark://spark-master:7077"
os.environ["PROJECT_ROOT"] = "/home/jovyan/work"

from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .appName("demo-jupyter") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

print("Spark version:", spark.version)
print("Master:", spark.sparkContext.master)
```

**Célula 2 — disparar o pipeline (terminal do notebook):**

```python
!cd /home/jovyan/work && spark-submit --master spark://spark-master:7077 \
  scripts/spark_local_pipeline.py --input data/transactions.json
```

**Célula 3 — inspecionar o lake:**

```python
from pathlib import Path
for layer in ["bronze", "silver", "gold"]:
    p = Path("/home/jovyan/work/data/lake") / layer
    print(layer, "→", list(p.rglob("*"))[:5])
```

**Célula 4 — ler Silver com Spark (opcional):**

```python
silver = spark.read.parquet("/home/jovyan/work/data/lake/silver/transactions")
silver.printSchema()
silver.show(5, truncate=False)
silver.count()
```

### 4. Provar que foi distribuído (1 min)

Abra em outra aba: **Spark UI** http://localhost:18080

Mostre o job que acabou de rodar (Workers, Stages, Duration).

**O que dizer:**

*"O Jupyter é a interface; o trabalho pesado roda no cluster Spark. Em Azure seria Databricks conectado ao ADLS."*

### 5. Cruzar com MinIO (opcional, +1 min)

Se quiser reforçar o lake em object storage:

- MinIO Console: http://localhost:9001 (`minioadmin` / `minioadmin`)
- Buckets `bronze`, `silver`, `gold` (se já populados)

---

## Roteiro de fala (30 segundos)

> *"O Jupyter é onde o engenheiro de dados explora transações, valida qualidade e materializa as camadas Bronze, Silver e Gold. O notebook `01_dataprep_dq.py` espelha o desenho Databricks; na demo local rodamos o mesmo fluxo via `spark_local_pipeline.py`. O scoring online fica na API Java — o Jupyter alimenta o lake e as features, não substitui a API."*

---

## Perguntas que podem surgir (e respostas)

| Pergunta | Resposta |
|----------|----------|
| Por que `.py` e não `.ipynb`? | Formato Databricks; localmente o pipeline “de verdade” é o script em `scripts/`. |
| Por que não roda o `01_dataprep_dq.py` direto? | Usa `abfss://` e `dbutils` — dependências de nuvem. Ver `docs/dados/LOCAL_SPARK.md`. |
| Jupyter vs `spark-job` no compose? | Mesmo pipeline; Jupyter = interativo, `spark-job` = batch automatizado na demo. |
| Equivalente Azure? | Databricks notebook + ADLS Gen2 (Bronze/Silver/Gold). |
| Precisa de 8 GB RAM? | Sim, se subir stack completa com Kafka + Jupyter. |

---

## Checklist “mostrei o Jupyter”

- [ ] Abri :8888 com token `datamaster`
- [ ] Mostrei `work/notebooks/01_dataprep_dq.py` (Medallion + DQ)
- [ ] Executei `spark_local_pipeline.py` a partir do notebook
- [ ] Mostrei `data/lake/` ou parquet no Silver
- [ ] Abri Spark UI :18080 com o job visível
- [ ] Expliquei: Jupyter = batch/experimentação; API = online

---

## Ordem sugerida nos estudos

1. **Jupyter** ← você está aqui
2. **Spark** (master/worker + `spark_local_pipeline.py`)
3. **MinIO + `data/lake/`** (Medallion físico)
4. **MongoDB + `batch_dataprep_mongo.py`** (perfis para a API)
5. **API Java** (`POST /analyze`)
6. **Dashboard / Console**

---

## Referências no repositório

- `docker-compose.yaml` — serviço `jupyter`
- `docs/dados/LOCAL_SPARK.md` — opções A (job batch) e B (Jupyter)
- `docs/operacao/ROTEIRO_TOUR_COMPONENTES.md` — bloco 2 (dados/batch)
- `docs/operacao/SERVICOS_DOCKER.md` — ordem na apresentação
