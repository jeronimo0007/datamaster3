# Checklist — demo banca

Núcleo: Airflow + landing + Medallion + Kafka + Mongo.  
Sem Postgres, sem VPS, sem “equivalentes” de cloud.

## 1. Stack

```bash
docker compose up -d --build
```

| URL | OK? |
|-----|-----|
| http://localhost:8880 | ☐ |
| http://localhost:8085 | ☐ |
| http://localhost:8080/health | ☐ |

## 2. Dados

| # | Ação | OK? |
|---|------|-----|
| D1 | Trigger `datamaster_e2e` ou `ingest_landing.py` + `medallion_job.py all` | ☐ |
| D2 | `data/landing/run=*/` com JSON, CSV, Parquet, XML | ☐ |
| D3 | `dq_latest.json` com success true | ☐ |
| D4 | `data/lake/{bronze,silver,gold}` | ☐ |
| D5 | Mostrar `src/data_processing/` | ☐ |

## 3. Serving (opcional)

```bash
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":50000,"merchant_category":"Viagem","user_country":"BR","merchant_country":"US","payment_method":"CREDIT_CARD","hour":3,"is_weekend":1,"is_international":1,"user_id":"user_1001"}'
```

## 4. Multiplataforma (fala)

Tabela única do README: Local | Azure | AWS — **Kafka e Mongo iguais** em todos.
