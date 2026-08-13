# Arquitetura DataMaster (visão engenharia de dados)

```mermaid
flowchart TB
  subgraph fontes [Fontes]
    Pub[API_publica_fraude]
    Syn[Sintetico]
    Fmt[JSON_CSV_Parquet_XML]
  end
  subgraph orch [Airflow]
    Ing[ingest_multi_source]
    Br[bronze]
    Dq[dq_gate]
    Si[silver]
    Go[gold]
  end
  subgraph lake [Lake]
    LB[(bronze)]
    LS[(silver)]
    LG[(gold)]
  end
  subgraph serve [Serving]
    Kf[Kafka]
    Api[API_Java]
  end
  Pub --> Ing
  Syn --> Ing
  Fmt --> Ing
  Ing --> Br --> LB --> Dq --> Si --> LS --> Go --> LG
  LG -.-> Api
  Kf --> Api
```

- Paths: `src/data_architecture/medallion.py`
- Transformações: `src/data_processing/`
- DAGs: `airflow/dags/`
- Cloud: Azure (ADLS + Kafka + MongoDB + Airflow/Spark)

Removido do discurso: Lambda architecture, RabbitMQ, comparação AWS.
