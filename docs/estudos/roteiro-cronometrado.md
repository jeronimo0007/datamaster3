# Roteiro cronometrado — banca DataMaster

Ensaio compacto em **~45 min** (tour técnico + demo de negócio).  
**Apresentação completa 1h30:** [apresentacao-90min.md](apresentacao-90min.md) · `bash docs/estudos/ensaio-90min.sh`

Versão **rápida (~25 min)** no final.

Use com: [ensaio-banca.sh](ensaio-banca.sh) (passo a passo no terminal).

---

## Pré-sala (T−10 min) — não conta no tempo da apresentação

```bash
cd datamaster
cp .env.example .env          # DEEPSEEK_API_KEY, SMTP_* se quiser IA/e-mail real
bash scripts/run_demo.sh
bash scripts/status-stack.sh
docker compose ps
```

Fixe **10 abas** (ver [README.md](README.md)).  
Opcional: screenshot de `docker compose ps` para plano B.

**Frase de abertura (30 s):**

> *"Na mesa subo a stack completa no Docker — mesma lógica do VPS em Kubernetes e da Azure no Terraform. Passo componente a componente: o que é, onde abre, equivalente na nuvem. Depois faço o fluxo de fraude ao vivo."*

---

## Bloco A — Hub e produto (0:00 → 0:23) · 23 min

| Tempo | Acum. | Peça | Onde | O que fazer | Guia |
|-------|-------|------|------|-------------|------|
| 0:30 | 0:30 | **Abertura** | Terminal | `docker compose ps` ou slide mapa nuvem | — |
| 2:00 | 2:30 | **Portal** | :8880 | Tabela serviços, credenciais, links | [portal.md](portal.md) |
| 8:00 | 10:30 | **API** | :8080 Swagger | health, profile-stats, analyze normal + fraude, LGPD mask | [api.md](api.md) |
| 8:00 | 18:30 | **Dashboard** | :8501 | KPIs, fraudes, liberar caso, aba LGPD | [dashboard.md](dashboard.md) |
| 5:00 | 23:30 | **Console** | :3333 | Gerar JSON, enviar lote ou mencionar fluxo completo | [console.md](console.md) |

### Comandos cola — API (Bloco A)

```bash
curl -s http://localhost:8080/health | python3 -m json.tool
curl -s http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool

# Fraude explícita (T5–T6 checklist banca)
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":50000,"merchant_category":"Viagem","user_country":"BR","merchant_country":"US","payment_method":"CREDIT_CARD","hour":3,"is_weekend":1,"is_international":1,"user_id":"user_1001"}' \
  | python3 -m json.tool
```

**Checkpoint 23 min:** API respondeu, dashboard mostra fraude, console explicado.

---

## Bloco B — Dados e batch (0:23 → 0:45) · 22 min

| Tempo | Acum. | Peça | Onde | O que fazer | Guia |
|-------|-------|------|------|-------------|------|
| 5:00 | 28:30 | **MongoDB** | Terminal + API | profile-stats, mongosh 1 doc, analyze com/sem perfil | [mongodb.md](mongodb.md) |
| 3:00 | 31:30 | **PostgreSQL** | Terminal | `\dt`, SELECT transactions/alerts | [postgres.md](postgres.md) |
| 4:00 | 35:30 | **MinIO + lake** | :9001 + host | Console buckets, `ls data/lake/`, dq_latest.json | [minio.md](minio.md) |
| 5:00 | 40:30 | **Spark** | :18080 | Workers, job completed, correlacionar com lake | [spark.md](spark.md) |
| 5:00 | 45:30 | **Jupyter** | :8888 | `01_dataprep_dq.py` topo + spark-submit ou só UI Spark | [jupyter.md](jupyter.md) |

### Comandos cola — Dados (Bloco B)

```bash
curl -s http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool
docker exec postgres psql -U admin -d fraud_detection -c '\dt'
ls -la data/lake/bronze data/lake/silver data/lake/gold
cat data/lake/reports/dq_latest.json 2>/dev/null | head -15
```

**Frase Medallion (15 s):**

> *"Bronze landing, Silver limpo, Gold features — mesmo layout no ADLS em Azure."*

**Checkpoint 45 min:** lake com 3 camadas, Spark UI vista, perfis Mongo > 0.

---

## Bloco C — Mensageria (0:45 → 0:56) · 11 min

| Tempo | Acum. | Peça | Onde | O que fazer | Guia |
|-------|-------|------|------|-------------|------|
| 1:00 | 46:30 | **Zookeeper** | Terminal | `docker compose ps zookeeper kafka` — só narrativa | [zookeeper.md](zookeeper.md) |
| 4:00 | 50:30 | **Kafka** | Terminal | list topics, opcional producer/consumer | [kafka.md](kafka.md) |
| 4:00 | 54:30 | **RabbitMQ** | :15672 | fila `fraud.alert.email` após analyze fraude | [rabbitmq.md](rabbitmq.md) |
| 3:00 | 57:30 | **email-worker** | :8090 + logs | health + `docker logs fraud-email-worker --tail 30` | [email-worker.md](email-worker.md) |

### Comandos cola — Mensageria (Bloco C)

```bash
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
curl -s http://localhost:8090/actuator/health | python3 -m json.tool
docker logs fraud-email-worker --tail 30
```

**Frase Kafka vs Rabbit (20 s):**

> *"Kafka = stream de eventos do core, narrativa Event Hubs. Rabbit = fila de tarefa — alerta de e-mail sem bloquear o HTTP."*

---

## Bloco D — Observabilidade (0:56 → 1:05) · 9 min

| Tempo | Acum. | Peça | Onde | O que fazer | Guia |
|-------|-------|------|------|-------------|------|
| 2:00 | 59:30 | **Redis** | Terminal | `redis-cli PING` | [redis.md](redis.md) |
| 3:00 | 62:30 | **Prometheus** | :9090 | Targets → fraud-api UP, query `up{job="fraud-api"}` | [prometheus.md](prometheus.md) |
| 4:00 | 66:30 | **Grafana** | :3000 | pasta DataMaster → dashboard API Fraude | [grafana.md](grafana.md) |

Gerar tráfego antes do Grafana (se gráficos vazios):

```bash
for i in $(seq 1 15); do
  curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
    -H "Content-Type: application/json" \
    -d '{"amount":500,"merchant_category":"Alimentação","user_id":"user_1001","hour":12}' >/dev/null
done
```

---

## Bloco E — Demo de negócio fechada (1:05 → 1:20) · 15 min

Se já fez analyze no Bloco A, **reforce o arco narrativo**:

| Tempo | Ação |
|-------|------|
| 3 min | Console :3333 → **Iniciar loop** · dashboard auto-refresh |
| 3 min | Dashboard → selecionar fraude → **Liberar** falso positivo |
| 3 min | Aba **LGPD** → mascarar CPF/e-mail |
| 3 min | RabbitMQ UI → mensagem na fila (se fraude recente) |
| 3 min | Encerramento: mapa nuvem + *"não era só Jupyter — pipeline, governança e API com contrato"* |

**Frase de fechamento (30 s):**

> *"Local opero tudo ao vivo; no VPS e na Azure o mesmo desenho está provisionado. Batch alimenta perfil e lake; online a API decide em milissegundos; mensageria e observabilidade fecham a plataforma."*

---

## Versão rápida (~25 min) — se a banca apertar tempo

| Min | Peças | Pular ou encurtar |
|-----|-------|-------------------|
| 0–2 | Portal + `docker compose ps` | — |
| 2–10 | API + analyze fraude + Swagger | LGPD só via curl rápido |
| 10–15 | Dashboard fraudes + liberar 1 caso | Assistente IA, gráficos |
| 15–18 | Mongo profile-stats + `data/lake/` ls | mongosh, Postgres |
| 18–20 | Spark UI :18080 | Jupyter |
| 20–22 | Kafka list + RabbitMQ UI | producer/consumer |
| 22–25 | Grafana dashboard | Redis, Prometheus detalhado, email-worker logs |

Comando único de validação:

```bash
bash docs/estudos/ensaio-banca.sh --rapido
```

---

## Plano B (algo caiu)

1. **Só API:** `curl` health + analyze + narrar resto no draw.io  
2. **Sem Spark/Jupyter:** mostrar `data/lake/` no host se já existir  
3. **Sem Rabbit:** explicar arquitetura assíncrona verbalmente  
4. **Sem Grafana:** Prometheus targets UP como prova mínima  

Arquivo draw.io: `docs/arquitetura/datamaster-04-docker-compose.drawio`

---

## Checklist final (marque ao ensaiar)

- [ ] Ensaio completo 1× com cronômetro
- [ ] Ensaio versão rápida 1×
- [ ] Todas as abas abrem antes de entrar
- [ ] `profile-stats` > 0
- [ ] Pelo menos 1 fraude no dashboard
- [ ] RabbitMQ fila vista OU explicado plano B
- [ ] Grafana com tráfego OU Prometheus UP

---

## Referências

- [README.md](README.md) — índice de guias
- [fluxo-demo.md](fluxo-demo.md) — pipeline completo
- [ensaio-banca.sh](ensaio-banca.sh) — script interativo
- [../operacao/CHECKLIST_DEMO_BANCA.md](../operacao/CHECKLIST_DEMO_BANCA.md)
