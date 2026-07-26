# RabbitMQ — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Fila **assíncrona** de alertas de fraude (desacopla API do e-mail) |
| **Container** | `fraud-rabbitmq` |
| **Portas** | **5672** (AMQP), **15672** (Management UI) |
| **Fila** | `fraud.alert.email` |
| **Credenciais UI** | `datamaster` / `datamaster` |
| **Equivalente Azure** | Service Bus |

Frase curta:

> *"Quando a API detecta fraude, publica na fila — o HTTP não espera o SMTP."*

---

## Onde entra na arquitetura

```text
POST /analyze  ──►  API :8080
                       │ is_fraud (score ≥ 0,74)
                       ▼
                  [RabbitMQ]
              fraud.alert.email
                       │
                       ▼
                 email-worker :8090  ──►  SMTP
```

**Kafka vs RabbitMQ:** Kafka = stream de eventos; RabbitMQ = **tarefa pontual** (enviar alerta).

---

## Demo prática (4 min)

### 1. Abrir UI

http://localhost:15672  
Login: `datamaster` / `datamaster`

Mostre aba **Queues** — fila `fraud.alert.email`.

### 2. Disparar fraude (1 min)

```bash
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":50000,"merchant_category":"Viagem","user_country":"BR","merchant_country":"US","payment_method":"CREDIT_CARD","hour":3,"is_weekend":1,"is_international":1,"user_id":"user_1001"}' \
  | python3 -m json.tool | grep is_fraud
```

### 3. Ver fila (1 min)

Na UI RabbitMQ:

- **Queues** → `fraud.alert.email`
- Observe **Ready** / **Message rates** (mensagem consumida rapidamente se worker ativo)

### 4. Logs do worker (1 min)

```bash
docker logs fraud-email-worker --tail 30
```

Com `SMTP_HOST` no `.env`: e-mail real. Sem SMTP: worker loga aviso mas processa fila.

### 5. Health worker

```bash
curl -s http://localhost:8090/actuator/health | python3 -m json.tool
```

---

## Configuração (`.env`)

| Variável | Descrição |
|----------|-----------|
| `FRAUD_EMAIL_ENABLED` | `true` para publicar/consumir |
| `RABBITMQ_USER` / `RABBITMQ_PASSWORD` | Broker |
| `SMTP_*`, `FRAUD_ALERT_TO` | E-mail real (opcional) |

---

## Roteiro de fala (30 s)

> *"RabbitMQ implementa o padrão fire-and-forget: a API responde rápido ao cliente e delega o e-mail ao worker. É fila de trabalho, não log de streaming — por isso Rabbit e não Kafka neste fluxo."*

---

## Por que RabbitMQ (e não Kafka para e-mail)

| Motivo | Detalhe |
|--------|---------|
| Problema | Enviar alerta sem aumentar latência do `/analyze` |
| Escolha | Fila de trabalho AMQP (`fraud.alert.email`) + worker |
| Trade-off vs Kafka | Kafka = log de eventos / replay; Rabbit = tarefa pontual com ack |
| Cloud | Service Bus (Azure) · SQS + Lambda (AWS) |

Pergunta: *"Por que dois brokers?"* → *"Papéis diferentes: ingestão de eventos vs desacoplar SMTP."*

## Checklist

- [ ] UI :15672 abre
- [ ] Fila `fraud.alert.email` visível
- [ ] Analyze com fraude executado
- [ ] Logs do email-worker conferidos
- [ ] Contrastei com Kafka

---

## Referências

- `docs/online/FRAUD_EMAIL_RABBITMQ.md`
- `api-java/.../messaging/`
- [email-worker.md](email-worker.md)
