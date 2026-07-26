# Kafka no DataMaster — guia de estudo e demo

Material pessoal de estudo (pasta não versionada). Orientação prática para explicar o componente na banca.

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Ingestão **streaming** de eventos — narrativa de arquitetura (speed layer) |
| **Container** | `kafka` (+ `zookeeper` como coordenação) |
| **Imagem** | `confluentinc/cp-kafka:7.5.0` + `confluentinc/cp-zookeeper:7.5.0` |
| **Porta (host)** | **9092** (`localhost:9092`) |
| **Porta (rede Docker)** | **29092** (`kafka:29092` — outros containers) |
| **Equivalente em produção** | Azure Event Hubs · AWS Kinesis / MSK |

Frase curta para a banca:

> *"Ingestão streaming — narrativa Event Hubs / Kinesis. Após cada `/analyze`, a API publica o evento `transaction-analyzed` no Kafka de forma **assíncrona** (CPF + card_last4). O scoring HTTP continua síncrono."*

Consulta do dia: `GET /api/v1/events/analyzed?date=today` · Jupyter `notebooks/02_kafka_consultas_dia.ipynb` · Dashboard aba **Kafka / eventos do dia**.

---

## Onde o Kafka entra na arquitetura

### Ponto crítico (seja honesto na banca)

O **score** continua HTTP síncrono. Depois da decisão, a API publica o fato no Kafka **de forma assíncrona** (o HTTP não espera o broker).

```text
CAMINHO REAL DA DEMO (online)
─────────────────────────────
Console :3333  ──POST /analyze──►  API :8080  ──►  MongoDB (perfil)
Dashboard :8501 ──GET/POST──────►       │
                                        ├──►  resposta HTTP (score)
                                        ├──►  Kafka topic transaction-analyzed  [async]
                                        └──►  se is_fraud: RabbitMQ ──► email-worker

CONSULTA / ANALYTICS
────────────────────
GET /api/v1/events/analyzed  ·  dashboard aba Kafka  ·  Jupyter 02_kafka_consultas_dia
(espelho Mongo analyzed_events)

PRODUÇÃO (alvo)
───────────────
Kafka/Event Hubs (retenção/replay) → consumer → Bronze → Gold por categoria (Negócios)
Kafka NÃO é DW eterno.
```

### Padrão Lambda (como falar)

- **Speed layer** (tempo real): API de scoring + evento Kafka/Event Hubs
- **Batch layer** (histórico): Spark + lake Medallion (`data/lake/`) + Gold para BI

O notebook `notebooks/01_dataprep_dq.py` menciona esse padrão nos comentários iniciais.

### Mapa mental (tour de componentes)

```text
[Console/Dashboard] → API :8080 → Mongo (perfil)
                         │ is_fraud
                         └── RabbitMQ → email-worker

[Kafka] ← streaming (Event Hubs)     [Spark/Jupyter] → lake (MinIO + data/lake/)
[Postgres] ← OLTP                    [Redis] ← cache
```

Kafka e **RabbitMQ** são mensagerias **diferentes** neste projeto:

| | Kafka | RabbitMQ |
|---|-------|----------|
| **Uso aqui** | Streaming / ingestão contínua | Fila de alerta de fraude (`fraud.alert.email`) |
| **Demo ativa?** | Sim — após cada `/analyze` (tópico `transaction-analyzed`) | Sim — após `analyze` com fraude |
| **Equivalente Azure** | Event Hubs | Service Bus |

---

## Configuração no Docker Compose

Serviços em `docker-compose.yaml`:

- **zookeeper** — porta 2181 (interna), coordena o broker
- **kafka** — depende do Zookeeper, `KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"`

Listeners:

- `PLAINTEXT://kafka:29092` — comunicação entre containers
- `PLAINTEXT_HOST://localhost:9092` — acesso do host (Mac/Windows)

---

## Pré-requisito: stack no ar

```bash
bash scripts/run_demo.sh
# ou
docker compose up -d --build
```

Confirme Kafka + Zookeeper:

```bash
docker compose ps kafka zookeeper
# State: Up
```

---

## Demo prática — passo a passo (≈ 3–5 min)

### 1. Contextualizar (1 min)

**O que dizer antes de abrir terminal:**

*"O Kafka está na stack para mostrar o desenho de ingestão em tempo real — como Event Hubs na Azure. Na mesa, o console manda transação direto para a API REST; em produção, o core banking publicaria eventos no tópico e consumidores fariam scoring ou enriquecimento."*

### 2. Prova rápida — broker vivo (30 s)

```bash
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

Se vazio, está ok — o broker respondeu. Com auto-create, tópicos aparecem ao primeiro publish.

Ou use o script de status:

```bash
bash scripts/status-stack.sh
```

### 3. Criar tópico de exemplo (opcional, 30 s)

```bash
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --create --topic fraud-transactions --if-not-exists \
  --partitions 1 --replication-factor 1

docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

**O que dizer:**

*"Tópico `fraud-transactions` — onde entrariam eventos de transação do canal em produção."*

### 4. Publicar e consumir mensagem (2 min) — demo “ao vivo”

**Terminal 1 — producer (simula core banking):**

```bash
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic fraud-transactions
```

Cole uma linha JSON (mesmo layout do simulador) e Enter:

```json
{"transaction_id":"demo-kafka-001","user_id":"user_42","amount":1500.0,"merchant_category":"Eletrônicos","timestamp":"2025-06-02T14:30:00","user_country":"BR","merchant_country":"US","payment_method":"CREDIT_CARD"}
```

Ctrl+C para sair.

**Terminal 2 — consumer (simula worker de ingestão):**

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic fraud-transactions \
  --from-beginning
```

**O que dizer:**

*"O produtor publica evento imutável no log; o consumidor lê com offset. Em produção, um serviço normalizaria isso via `from_event_or_queue_message` em `src/data_ingestion/transaction_adapters.py` e chamaria scoring ou persistiria no lake."*

### 5. Contrastar com RabbitMQ (1 min)

Mostre que **alertas de fraude** usam **RabbitMQ**, não Kafka:

- RabbitMQ UI: http://localhost:15672 (`datamaster` / `datamaster`)
- Fila: `fraud.alert.email`
- Disparo: `POST /api/v1/transactions/analyze` com score ≥ 0,74

**O que dizer:**

*"Kafka = stream de eventos de negócio (alto volume, replay). RabbitMQ = fila de tarefa pontual (enviar e-mail sem bloquear a API)."*

---

## Roteiro de fala (30 segundos)

> *"O Kafka é o barramento de fatos após a análise — equivalente ao Event Hubs. O score é HTTP síncrono; em paralelo publico `transaction-analyzed` com categoria, CPF e card_last4. Kafka não é DW eterno: retenção/replay; Negócios lê Gold no lake. E-mail de fraude vai pelo RabbitMQ."*

---

## Perguntas que podem surgir (e respostas)

| Pergunta | Resposta |
|----------|----------|
| Por que Kafka se o score é HTTP? | Score precisa ser síncrono; o fato `transaction-analyzed` vai ao Kafka **depois**, async. |
| Kafka vs RabbitMQ? | Kafka = log de eventos / streaming; RabbitMQ = fila de trabalho (e-mail de alerta). |
| Por que Zookeeper? | Modo clássico Confluent 7.5; em produção gerenciado (MSK/Event Hubs) isso é abstraído. |
| Qual tópico usar? | Exemplo: `fraud-transactions`; auto-create habilitado no compose. |
| Equivalente AWS? | Kinesis ou Amazon MSK. |
| E se Kafka não subir? | Erro `KAFKA_PROCESS_ROLES` = imagem errada; projeto usa `cp-kafka:7.5.0`. Ver `docs/operacao/QUICK_START.md`. |
| Consome RAM? | Sim — stack completa (API + Kafka + Spark + Jupyter) pede ~8 GB no Docker Desktop. |

---

## Troubleshooting rápido

**Kafka não sobe (`KAFKA_PROCESS_ROLES is not set`):**

```bash
docker compose down
docker compose up -d --build
docker compose ps kafka zookeeper
```

**Subir só o essencial (sem Kafka):**

```bash
docker compose up -d api dashboard data-console spark-master spark-worker
```

---

## Checklist “mostrei o Kafka”

- [ ] Expliquei: Kafka = streaming / Event Hubs; **não** é o caminho do `analyze` na demo
- [ ] `docker exec kafka kafka-topics --list` retornou sem erro
- [ ] (Opcional) Criei tópico `fraud-transactions`
- [ ] (Opcional) Producer + consumer com JSON de transação
- [ ] Contrastei com RabbitMQ (:15672) para alertas de fraude
- [ ] Mencionei equivalente Azure (Event Hubs) e AWS (Kinesis/MSK)

---

## Ordem sugerida nos estudos

1. Jupyter
2. Spark
3. MinIO + lake
4. MongoDB + batch prep
5. **Kafka** ← você está aqui (mensageria streaming)
6. **RabbitMQ + email-worker** (mensageria de alerta — par natural do Kafka na banca)
7. API Java
8. Dashboard / Console

---

## Referências no repositório

- `docker-compose.yaml` — serviços `zookeeper` e `kafka`
- `docs/arquitetura/README.md` — fluxo online (Kafka opcional na demo)
- `docs/operacao/SERVICOS_DOCKER.md` — bloco mensageria
- `docs/operacao/ROTEIRO_TOUR_COMPONENTES.md` — bloco 3 (streaming + alertas)
- `docs/operacao/QUICK_START.md` — troubleshooting Kafka
- `src/data_ingestion/transaction_adapters.py` — `from_event_or_queue_message()` (Event Hubs/Kafka)
- `config/medallion.yaml` — speed layer Event Hubs / Kafka / Kinesis
