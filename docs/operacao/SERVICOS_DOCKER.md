# Serviços Docker — engenharia de dados

**Hub:** http://localhost:8880 · **Airflow:** http://localhost:8085 (`admin`/`admin`)

## Núcleo

| Serviço | Porta | Papel |
|---------|-------|-------|
| airflow-webserver | 8085 | Orquestra Bronze→DQ→Silver→Gold |
| airflow-scheduler | — | Executa DAGs |
| spark-master/worker + spark-job | 18080 | Processamento batch |
| kafka + zookeeper | 9092 | Streaming |
| mongodb | 27017 | Perfis (serving) |
| minio | 9000/9001 | Object storage do lake |
| jupyter | 8888 | Exploração (token `datamaster`) |

## Serving (secundário)

| Serviço | Porta |
|---------|-------|
| portal | 8880 |
| api | 8080 |
| dashboard | 8501 |
| data-console | 3333 |
| prometheus / grafana | 9090 / 3000 |

**Removidos da arquitetura:** Postgres, Redis, RabbitMQ, email-worker, VPS/k3s.

Na Azure/AWS sobem os **mesmos** Kafka, MongoDB, Airflow e Spark (não Cosmos, não Event Hubs, não DocumentDB).
