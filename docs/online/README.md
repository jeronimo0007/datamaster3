# Domínio: Online (serving)

A API e o Kafka são a **camada de serving** da demo — o núcleo do projeto é o pipeline Medallion + Airflow (ver [README](../../readme.md)).

## Serviços

| Serviço | Porta | Papel |
|---------|-------|--------|
| api | 8080 | Scoring online, consulta perfis Mongo |
| dashboard | 8501 | Streamlit |
| data-console | 3333 | Simulador |
| kafka | 9092 | Eventos `transaction-analyzed` (mesmo Kafka na Azure) |

## Documentos

| Documento | Conteúdo |
|-----------|----------|
| [../operacao/SERVICOS_DOCKER.md](../operacao/SERVICOS_DOCKER.md) | Stack completa |
| [../../src/data_ingestion/kafka_client.py](../../src/data_ingestion/kafka_client.py) | Cliente Kafka unificado local/Azure |

[← Índice](../README.md)
