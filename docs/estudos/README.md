# DataMaster — estudos por componente

Material pessoal (pasta **não versionada**).

**Princípio da apresentação:** o mais importante **não é o quê — é o porquê**.  
Listar tools = decorar. Explicar *problema → escolha → trade-off* = engenharia de dados.

---

## Comece aqui (nota 10)

| Ordem | Arquivo | Uso |
|------:|---------|-----|
| 1 | **[plano-estudo-8-topicos.md](plano-estudo-8-topicos.md)** | Índice dos 8 tópicos + frases de ouro |
| 1b | **[agente-estudo-banca-chatgpt.md](agente-estudo-banca-chatgpt.md)** | **Colar no ChatGPT** — system + 8 tópicos + defesas + simulado |
| 2 | **[topico-01 … topico-08](plano-estudo-8-topicos.md)** | 12 pontos por tópico (estude **um por vez**) |
| 3 | **[apresentacao-90min.md](apresentacao-90min.md)** | Roteiro de fala no projetor |
| 4 | **[cola-1-pagina.md](cola-1-pagina.md)** | Imprimir — slide ↔ tempo ↔ comando ↔ porquê |
| 5 | `bash docs/estudos/ensaio-90min.sh` | Ensaio cronometrado |

Slides: [banca.html](http://localhost:8880/banca.html)

```bash
bash docs/estudos/ensaio-90min.sh
bash docs/estudos/ensaio-90min.sh --so-check
```

---

## Os 8 tópicos (edital)

| # | Guia | Slide |
|---|------|-------|
| 1 | [topico-01-extracao.md](topico-01-extracao.md) | 5 |
| 2 | [topico-02-ingestao.md](topico-02-ingestao.md) | 6 + 6b |
| 3 | [topico-03-armazenamento.md](topico-03-armazenamento.md) | 7 + 7c + 7b |
| 4 | [topico-04-observabilidade.md](topico-04-observabilidade.md) | 8 |
| 5 | [topico-05-seguranca.md](topico-05-seguranca.md) | 9 |
| 6 | [topico-06-lgpd.md](topico-06-lgpd.md) | 10 |
| 7 | [topico-07-arquitetura.md](topico-07-arquitetura.md) | 11 |
| 8 | [topico-08-escalabilidade.md](topico-08-escalabilidade.md) | 12 |

---

## Antes de qualquer demo

```bash
cp .env.example .env   # opcional: DEEPSEEK_API_KEY, SMTP_*
bash scripts/run_demo.sh
bash scripts/status-stack.sh
```

| # | Componente | URL |
|---|------------|-----|
| 1 | Portal | http://localhost:8880 |
| 2 | Swagger | http://localhost:8080/swagger-ui.html |
| 3 | Dashboard | http://localhost:8501 |
| 4 | Console | http://localhost:3333 |
| 5 | RabbitMQ | http://localhost:15672 |
| 6 | Grafana | http://localhost:3000 |
| 7 | Prometheus | http://localhost:9090 |
| 8 | Spark UI | http://localhost:18080 |
| 9 | Jupyter | http://localhost:8888/?token=datamaster |
| 10 | MinIO | http://localhost:9001 |

---

## Guias por componente (tour / demo)

Use **depois** de dominar o tópico do edital — aprofundam o “como mostro”.

### Produto (online)

| Arquivo | Componente |
|---------|------------|
| [portal.md](portal.md) | Portal :8880 |
| [api.md](api.md) | API Java :8080 |
| [dashboard.md](dashboard.md) | Dashboard Streamlit :8501 |
| [console.md](console.md) | Console Node :3333 |

### Dados e batch

| Arquivo | Componente |
|---------|------------|
| [mongodb.md](mongodb.md) | MongoDB + batch prep |
| [postgres.md](postgres.md) | PostgreSQL OLTP |
| [minio.md](minio.md) | MinIO (lake objeto) |
| [spark.md](spark.md) | Spark master/worker |
| [jupyter.md](jupyter.md) | Jupyter PySpark |

### Mensageria

| Arquivo | Componente |
|---------|------------|
| [zookeeper.md](zookeeper.md) | Zookeeper (suporte Kafka) |
| [kafka.md](kafka.md) | Kafka streaming |
| [rabbitmq.md](rabbitmq.md) | RabbitMQ filas |
| [email-worker.md](email-worker.md) | Worker SMTP |

### Infra transversal

| Arquivo | Componente |
|---------|------------|
| [redis.md](redis.md) | Redis cache |
| [prometheus.md](prometheus.md) | Prometheus métricas |
| [grafana.md](grafana.md) | Grafana dashboards |
| [fluxo-demo.md](fluxo-demo.md) | Pipeline `run_demo.sh` |

Outros ensaios: [roteiro-cronometrado.md](roteiro-cronometrado.md) (~45 min) · `ensaio-banca.sh`

---

## Mapa mental (fale apontando)

```text
[Console/Dashboard] → API :8080 → Mongo (perfil)
                         │ is_fraud
                         └── RabbitMQ → email-worker

[Kafka] ← streaming (Event Hubs)     [Spark/Jupyter] → lake (MinIO + data/lake/)
[Postgres] ← OLTP ref.               [Redis] ← cache

[Prometheus] → [Grafana]             [Portal :8880] = índice
```

---

## Checklist “mostrei tudo”

- [ ] Portal :8880
- [ ] API :8080 + Swagger + `analyze`
- [ ] Dashboard :8501 (transações, LGPD, IA)
- [ ] Console :3333 (gerar JSON, fluxo completo)
- [ ] Mongo (`profile-stats` > 0)
- [ ] Postgres (`\dt`) — deixar claro: não é scoring
- [ ] MinIO :9001
- [ ] Spark :18080
- [ ] Jupyter :8888
- [ ] Kafka (list topics) — deixar claro: não está no analyze
- [ ] RabbitMQ :15672
- [ ] email-worker :8090/health
- [ ] Redis PING
- [ ] Prometheus :9090 (target UP)
- [ ] Grafana :3000 (dashboard DataMaster)

---

## Referências oficiais no repo

- [docs/operacao/ROTEIRO_TOUR_COMPONENTES.md](../operacao/ROTEIRO_TOUR_COMPONENTES.md)
- [docs/operacao/CHECKLIST_DEMO_BANCA.md](../operacao/CHECKLIST_DEMO_BANCA.md)
- [docs/operacao/SERVICOS_DOCKER.md](../operacao/SERVICOS_DOCKER.md)
