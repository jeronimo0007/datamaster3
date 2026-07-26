# Email Worker — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | **Consumidor** da fila RabbitMQ — envia alerta SMTP |
| **Container** | `fraud-email-worker` |
| **Stack** | Java Spring Boot — `email-worker/` |
| **Porta** | **8090** (Actuator health) |
| **Fila** | `fraud.alert.email` |
| **Equivalente Azure** | Service Bus + Azure Function / Container App worker |

Frase curta:

> *"Worker assíncrono — consome alerta de fraude e envia e-mail sem bloquear a API."*

---

## Onde entra na arquitetura

```text
API (produtor)  ──►  RabbitMQ  ──►  email-worker (consumidor)  ──►  SMTP
```

Health independente da API: http://localhost:8090/actuator/health

---

## Demo prática (3 min)

### 1. Health check

```bash
curl -s http://localhost:8090/actuator/health | python3 -m json.tool
```

Esperado: `"status": "UP"`.

### 2. Fluxo completo (com RabbitMQ)

1. Dispare fraude via API (ver [rabbitmq.md](rabbitmq.md))
2. Acompanhe logs:

```bash
docker logs fraud-email-worker --tail 40 -f
```

### 3. Com SMTP configurado (opcional)

No `.env`:

```env
SMTP_HOST=smtp.exemplo.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=alertas@datamaster.local
FRAUD_ALERT_TO=seu@email.com
FRAUD_EMAIL_ENABLED=true
```

Reinicie:

```bash
docker compose up -d --build email-worker api
```

Repita analyze com fraude → confira caixa de entrada.

### 4. Sem SMTP (demo mínima)

Worker **sobe normalmente** e loga que SMTP não está configurado — ainda assim mostra consumo da fila nos logs.

---

## Roteiro de fala (20 s)

> *"Microserviço dedicado ao canal de notificação. Se o SMTP cair, a API continua scoring. Em nuvem seria Function ou worker em Container App ouvindo Service Bus."*

---

## Por que email-worker separado

| Motivo | Detalhe |
|--------|---------|
| Problema | SMTP lento/instável não pode travar a decisão de fraude |
| Escolha | Consumer da fila + Actuator health |
| Cloud | Azure Function / Container App · Lambda |
| Trade-off | Síncrono na API = simples e arrisca latência/timeout |

## Checklist

- [ ] `:8090/actuator/health` UP
- [ ] Logs após fraude na API
- [ ] Expliquei desacoplamento API ↔ e-mail
- [ ] (Opcional) SMTP real configurado

---

## Referências

- `email-worker/`
- `docs/online/FRAUD_EMAIL_RABBITMQ.md`
- `docs/operacao/CHECKLIST_DEMO_BANCA.md` — T4c
