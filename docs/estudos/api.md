# API Java — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Motor de scoring, batch, LGPD, alertas, métricas |
| **Container** | `fraud-api` |
| **Stack** | Java 17, Spring Boot — `api-java/` |
| **Porta** | **8080** |
| **Perfil demo** | `SPRING_PROFILES_ACTIVE=local` |
| **Equivalente Azure** | Container Apps + ACR |

Frase curta:

> *"Contrato REST que decide risco em tempo aceitável — heurística + boost de anomalia contra perfil MongoDB."*

---

## Onde entra na arquitetura

```text
[Console/Dashboard/curl] ──HTTP──► API :8080
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
              MongoDB            RabbitMQ          memória
           (user_profiles)    (se is_fraud)     (transações demo)
```

**Limiar de fraude na demo:** score ≥ **0,74** → `is_fraud: true`

---

## Endpoints principais

| Método | Rota | Função |
|--------|------|--------|
| GET | `/health` | Health check |
| POST | `/api/v1/transactions/analyze` | Scoring + perfil |
| POST | `/api/v1/transactions/batch` | Lote de transações |
| GET | `/api/v1/transactions` | Listagem (`all`, `fraud`, `released`) |
| POST | `/api/v1/transactions/{id}/release` | Liberar falso positivo |
| GET | `/api/v1/batch/profile-stats` | Contagem perfis Mongo |
| POST | `/api/v1/lgpd/mask` | Mascaramento PII |
| POST | `/api/v1/assistant/chat` | Assistente IA (DeepSeek) |
| GET | `/api/v1/dashboard/summary` | KPIs dashboard |
| GET | `/api/v1/model/metrics` | Métricas de referência |
| GET | `/actuator/prometheus` | Métricas Prometheus |

Swagger: http://localhost:8080/swagger-ui.html

---

## Demo prática (8 min)

### 1. Health (30 s)

```bash
curl -s http://localhost:8080/health | python3 -m json.tool
```

### 2. Perfis batch (30 s)

```bash
curl -s http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool
```

Esperado: `profileCount` > 0 após `run_demo.sh`.

### 3. Analyze — transação normal (1 min)

```bash
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":150,"merchant_category":"Alimentação","user_country":"BR","merchant_country":"BR","payment_method":"CREDIT_CARD","hour":14,"user_id":"user_1001"}' \
  | python3 -m json.tool
```

Mostre: `fraud_score`, `is_fraud: false`, bloco `user_profile` com `anomaly_reasons`.

### 4. Analyze — fraude explícita (2 min)

```bash
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":50000,"merchant_category":"Viagem","user_country":"BR","merchant_country":"US","payment_method":"CREDIT_CARD","hour":3,"is_weekend":1,"is_international":1,"user_id":"user_1001"}' \
  | python3 -m json.tool
```

Mostre: `is_fraud: true`, score alto, razões de anomalia vs perfil.

### 5. LGPD (1 min)

```bash
curl -s -X POST http://localhost:8080/api/v1/lgpd/mask \
  -H "Content-Type: application/json" \
  -d '{"cpf":"12345678901","email":"joao@banco.com","phone":"11999998888"}' \
  | python3 -m json.tool
```

### 6. Swagger ao vivo (2 min)

Abra Swagger → expanda `POST /api/v1/transactions/analyze` → **Try it out** → Execute.

### 7. Listar fraudes (1 min)

```bash
curl -s "http://localhost:8080/api/v1/transactions?filter=fraud&limit=10" | python3 -m json.tool
```

---

## Roteiro de fala (30 s)

> *"A API é o artefato de produção — não o notebook. Ela combina regras interpretáveis com desvio do perfil histórico no MongoDB. Quando detecta fraude, publica na fila RabbitMQ sem bloquear o HTTP. Métricas expostas para Prometheus."*

---

## Perguntas frequentes

| Pergunta | Resposta |
|----------|----------|
| Por que Java? | OpenAPI, Actuator/Prometheus, AMQP — stack comum em banco |
| Usa Postgres? | Scoring usa Mongo; Postgres é OLTP de referência |
| Onde está o ML? | Heurística Java na demo; Spark/Python alimenta lake e treino |
| Por que não retreinar online? | Perfil batch + boost — latência previsível |

---

## Por que Java (e não FastAPI)

| Motivo | Detalhe |
|--------|---------|
| Problema | Motor de decisão com contrato estável, métricas e fila |
| Escolha | Spring Boot — OpenAPI, Actuator/Prometheus, AMQP |
| Trade-off | Python seria mais rápido para prototipar ML; Java encaixa melhor em banco/enterprise |

Pergunta da banca: *"Por que Java?"* → *"Contrato, observabilidade nativa e integração AMQP madura — o scoring demo é heurística Java; o lake/treino fica no Spark/Python."*

## Checklist

- [ ] `/health` OK
- [ ] Swagger aberto
- [ ] `analyze` normal e fraude executados
- [ ] `profile-stats` > 0
- [ ] LGPD mask demonstrado
- [ ] Mencionei limiar 0,74 e RabbitMQ pós-fraude

---

## Referências

- `api-java/src/main/java/com/fraud/local/LocalDemoApiController.java`
- `docs/operacao/QUICK_START.md` — analyze T5–T6
