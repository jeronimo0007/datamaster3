# Roteiro de fala — 90 minutos alinhado a `banca.html`

**URL dos slides:** http://localhost:8880/banca.html

**Como usar os dois materiais:**

| Material | Função |
|----------|--------|
| **`banca.html`** | Slides no **Meet** (tela compartilhada) — teoria e porquês, **sem** “Demo ao vivo” |
| **`cola.html`** | Cola do apresentador (tela **privada**) — demos, comandos, falas |
| **`apresentacao-90min.md`** | Roteiro de fala completo |
| **`plano-estudo-8-topicos.md`** | Estudo profundo (12 pontos × 8 tópicos) |

**Meet:** compartilhe só `http://localhost:8880/banca.html`. Mantenha `http://localhost:8880/cola.html` na outra tela.

Detalhes técnicos (draw.io, tabelas longas, plano B) ficam **só neste roteiro**, não no deck.

Use **← →** no `banca.html` e consulte este arquivo ao lado do monitor.

---

## Princípio nº 1 — o **porquê** manda, o **quê** só ilustra

Na banca, quem lista ferramentas parece decorou o deck. Quem explica **decisão** parece engenheiro de dados.

| Prioridade | O que falar | Tempo mental |
|------------|-------------|--------------|
| **1º** | **Por quê** esse componente (problema + trade-off) | ~70% |
| **2º** | **Onde** entra no fluxo DataMaster | ~20% |
| **3º** | **O que** é / qual comando / qual URL | ~10% |

**Fórmula em todo slide de tópico:**  
`Problema → Escolhi X porque… → Alternativa Y custaria… → Na mesa mostro…`

Se a frase começar só com o nome da tech (“temos Kafka, Spark, Mongo…”), **pare e reformule com o porquê**.

---

## Como este roteiro se relaciona com o deck

| Parte | Slides `banca.html` | Tempo | O que acontece |
|-------|---------------------|-------|----------------|
| **Abertura** | 0 → 1 → 1b → 2 | ~10 min | Quem sou, capa, três ambientes, agenda dos 8 tópicos |
| **Teoria** | 3 → 4 → 5 → 6 → 6b → 7 → 7c → 7b | ~25 min | Contexto, arquitetura, extração, ingestão, online, Medallion, Mongo |
| **Tópicos 4–8** | 8 → 9 → 10 → 11 → 12 | ~18 min | Observabilidade, segurança, LGPD, modelo analítico, escala |
| **Demo ao vivo** | **13** (T0–T12) | ~30 min | Stack, API, dashboard, batch, Kafka, Grafana… |
| **Fechamento** | 14 → 15 | ~4 min | Mapa multicloud, agradecimento, perguntas |

**Total ≈ 90 min**

---

## Antes de abrir o slide 0 (T−30 min)

```bash
bash scripts/run_demo.sh
bash scripts/status-stack.sh
```

Abas: Portal · **banca.html** · Swagger · Dashboard · Console · RabbitMQ · Grafana · Prometheus · Spark · Jupyter · MinIO.

---

# SLIDE 0 — Apresentador · ~3 min

**[Slide ativo: `data-slide="0"`]**

Banca, bom dia / boa tarde. Sou **Jerônimo Alves Cardoso**.

Atuo como engenheiro de dados e software, expert em **riscos e motores de crédito**, com formação em sistemas de informação, pós em Arquitetura de Dados, Arquitetura de Software, Data Science e Cyber Security, MIB em IA para Negócios — mais de vinte anos em TI, a maior parte no setor financeiro. Já passei por modernização Java, saída de mainframe, APIs de canal e plataformas.

Hoje venho mostrar uma **plataforma de dados** aplicada a antifraude. O fio condutor **não é o inventário de ferramentas** — é o **porquê** de cada escolha: qual problema resolve, o que eu rejeitei e qual o trade-off.

**[Próximo → slide 1]**

---

# SLIDE 1 — Capa · ~2 min

**[Slide 1 — pipeline animado na capa]**

O tema é **sistema de detecção de fraudes bancárias**.

Três frentes que a banca vai ver citadas ao longo da apresentação:

1. **Demo ao vivo** — Docker local, stack inteira na mesa  
2. **VPS homelab** — Kubernetes, mesmo desenho  
3. **Azure** — Terraform `apresentacao`, mesmo desenho  

**AWS** entra como **mapa multicloud** — equivalências, sem deploy.

A animação na capa resume o fluxo: **fonte → barramento → processamento → lake → serving → alerta → monitoramento**.

**[Próximo → slide 1b]**

---

# SLIDE 1b — Um desenho · três lugares · ~2 min

**[Slide 1b]**

Reforço: **um desenho, três lugares**.

- **Mesa:** `docker compose`, portal :8880, trilha **T1–T12** no slide de demo  
- **VPS:** `kubectl get pods -n datamaster`, mesmos manifests  
- **Azure:** resource group do Terraform, ADLS, Event Hubs, Container App  

AWS: só o slide de **mapa multicloud** — provo que o desenho não é preso a um vendor.

**[Próximo → slide 2]**

---

# SLIDE 2 — Agenda · 8 tópicos · ~3 min

**[Slide 2 — SVG dos 8 nós em movimento]**

Banca, a ordem dos **oito tópicos** do edital é esta. Em cada um o mais importante **não é o nome da tecnologia** — é **por que ela está aí**: problema, escolha e trade-off. O “o quê” só comprova.

1. **Extração** — fontes e contrato  
2. **Ingestão** — stream e batch  
3. **Armazenamento** — lake, DW, NoSQL  
4. **Observabilidade** — SLI, métricas, trilhas  
5. **Segurança** — cripto, vault, RBAC  
6. **LGPD** — mascaramento e conformidade  
7. **Arquitetura** — Medallion, Kimball, features  
8. **Escalabilidade** — partições, autoscale  

Depois desses blocos, abro o **slide 13** e faço a **demo ao vivo** com o checklist **T0–T12**.

**[Próximo → slide 3]**

---

# SLIDE 3 — Contexto · ~4 min

**[Slide 3 — números de fraude]**

Contexto de negócio:

- Fraudes digitais na casa dos **bilhões**  
- Crescimento forte de tentativas  
- **Cartão** e CNP em alta  
- Meta de decisão: **menos de 2 segundos**

Requisitos que guiam a arquitetura:

| Requisito | Meta |
|-----------|------|
| Latência | < 2 s |
| Precisão | Recall alto + controle de falso positivo |
| Escala | 10M+ transações/dia |
| SLA | 99,9% na camada crítica |
| Conformidade | LGPD ponta a ponta |

Minha tese: entregar **plataforma confiável** — rastreio, segurança e custo previsível — não só um modelo. O modelo sem engenharia de dados não sobrevive a auditoria nem a pico.

**[Próximo → slide 4]**

---

# SLIDE 4 — Arquitetura alvo Azure · ~5 min

**[Slide 4 — imagem `datamaster-00-visao-geral.png` + 8 bullets em duas colunas]**

Este slide mostra a **visão geral batch + online** — mesma lógica Lambda do edital.

Percorro os oito blocos numerados na tela — cada um existe por um motivo:

1. Ingestão — Event Hubs + Data Factory (mesa: Kafka + console) → **latência + histórico**  
2. Lake — ADLS Medallion (mesa: `data/lake/` + MinIO) → **reprocessamento barato**  
3. Processamento — Databricks (mesa: Spark + Jupyter) → **volume distribuído**  
4. Serving — API + Cosmos perfis (mesa: :8080 + MongoDB) → **decisão &lt;2s**  
5. Consumo — Power BI (mesa: Streamlit :8501) → **humano no loop**  
6. Alertas — Service Bus (mesa: RabbitMQ + email-worker) → **não bloquear HTTP**  
7. Governança — Purview + Key Vault (mesa: DQ + `governanca.yaml`) → **qualidade e segredo**  
8. Observabilidade — Monitor (mesa: Prometheus + Grafana) → **SLO visível**  

A imagem é **PNG estática** — funciona sem internet.

Se a banca pedir **zoom técnico** (porta a porta, containers), uso o **Apêndice draw.io** deste roteiro — não é slide no projetor.

**[Próximo → slide 5]**

---

# SLIDE 5 — Extração · ~3 min · Tópico 1

**[Slide 5]**

**Extração:** de onde vêm os dados — e como viram **contrato**.

**Problema:** fontes heterogêneas (core, API, arquivo, parceiro) quebram o modelo se eu acoplar o schema de cada uma.

**O que uso e por quê:**

- **`data-generator-console` + `generate_data.py`** — simulam o core na mesa com volume controlado (não tenho mainframe na sala).  
- **Contrato JSON** — campos mínimos alinhados ao modelo (`amount`, `hour`, flags, categoria, `payment_method`).  
- **`transaction_adapters.py`** — normaliza simulador / fila / CSV para o dicionário canônico. **Por quê:** muda a fonte, não reescrevo o scoring.

**Cloud:** na Azure, producer Event Hubs + ADF Copy para landing; na AWS, Kinesis + Glue. O padrão é o mesmo: **extrair → adaptar → pousar**.

**Fala:**
> “Extração aqui é contrato. Eu simulo o core e o adapter garante que o modelo e o lake não dependem do formato de quem enviou.”

**Se perguntarem:** *Por que não ligar o ML direto no core?* — Acoplamento; qualquer mudança no core quebra a plataforma.

**[Próximo → slide 6]**

---

# SLIDE 6 — Streaming, batch e Lambda · ~4 min · Tópico 2

**[Slide 6]**

**Ingestão** em dois modos — porque os problemas são diferentes:

| Modo | Resolve | Por que esse componente |
|------|---------|-------------------------|
| **Streaming** (Kafka → Event Hubs / Kinesis) | Propagar o **fato** da análise sem travar o HTTP | Log particionado, replay; categoria para Negócios |
| **Batch** (Spark + `batch_dataprep_mongo.py`) | Histórico, reprocessamento, **perfis** | Janela completa; agregação por `user_id` |

**Lambda:** speed = API (score) + evento Kafka; batch = lake + perfis.

**Fluxo real (obrigatório):**
> Canal chama a API por HTTP (score síncrono). Em paralelo, publico `transaction-analyzed` no Kafka (assíncrono) com categoria, CPF e `card_last4`. RabbitMQ fica só para e-mail se fraude.

**Kafka ≠ DW eterno:** retenção/replay no broker; histórico analítico → lake → Gold por categoria.

**Por que não só batch?** Perco a meta &lt;2s. **Por que não só stream (Kappa)?** Features históricas ficam mais caras — Lambda me dá os dois braços.

**[Próximo → slide 6b]**

---

# SLIDE 6b — Microserviços · caminho da demo · ~3 min

**[Slide 6b — diagrama online]**

Arquitetura de microserviços de referência: LB e API Gateway **não implementados** — estão apagados no desenho. Em produção são críticos (contrato, quota, segurança na borda).

**Caminho real da demo:**

```text
Console/Dashboard → API :8080 → Mongo (perfil) → resposta HTTP
                         │
                         ├── Kafka transaction-analyzed (sempre, async)
                         └── se fraude → RabbitMQ → email-worker
```

**Por quê cada hop:**

- **API Java** — contrato OpenAPI, Actuator/Prometheus, AMQP + Kafka, stack comum em banco.  
- **Mongo** — perfil por `user_id` em leitura rápida (não full scan no lake).  
- **Kafka** — após o score, fato assíncrono `transaction-analyzed` (categoria / analytics).  
- **RabbitMQ** — alerta de e-mail: o HTTP **não espera** SMTP. (Kafka = log de negócio; Rabbit = tarefa pontual.)

Mostro no slide 13: T5–T6 analyze · T8 Kafka/consumer · dashboard aba Kafka · Jupyter `02_kafka_consultas_dia`.

**[Próximo → slide 7]**

---

# SLIDE 7 — Lake Medallion · ~4 min · Tópico 3 (parte 1)

**[Slide 7 — imagem batch Medallion]**

**Armazenamento** — padrão Medallion:

- **Bronze** — landing (não destruo a origem)  
- **Silver** — limpo e enriquecido (DQ)  
- **Gold** — features para ML / consumo  

**Por que Medallion:** qualidade **progressiva** + reprocessamento a partir do Bronze sem perder auditoria.

Pipeline local: `scripts/spark_local_pipeline.py` → `data/lake/`.

**Por que Spark:** motor distribuído para volume; na Azure vira Databricks; na AWS, EMR/Glue.

Lambda: este slide é a camada **batch**; streaming + API é a **speed** (slide 6).

**[Próximo → slide 7c]**

---

# SLIDE 7c — Camadas lake, DW, operacional · ~3 min

**[Slide 7c]**

**Por que três stores** (não um banco só):

| Camada | Tecnologia | Por quê |
|--------|------------|---------|
| **Lake** | parquet/Delta + MinIO/`data/lake/` | Histórico barato, schema-on-read, ML |
| **Warehouse** | Synapse / Redshift (narrativa) · Postgres OLTP ref. | SQL dimensional / Kimball para BI |
| **Operacional** | Mongo `user_profiles` | Serving online do `/analyze` |

Na mesa: Postgres tem schema demo; **scoring usa Mongo** + memória na API `local` — diga isso sem hesitar.

**Trade-off:** tudo no Postgres seria simples no POC e fraco em lake/ML; tudo no Mongo seria ruim para BI dimensional.

**[Próximo → slide 7b]**

---

# SLIDE 7b — Dataprep → MongoDB → API · ~3 min

**[Slide 7b — fluxo batch→Mongo→analyze]**

Elo entre batch e online:

```text
transactions.json → batch_dataprep_mongo.py → user_profiles → POST /analyze
```

**Por quê:** a API **não retreina** a cada request — consulta o perfil e aplica **anomaly_score_boost**. Histórico materializado = latência previsível.

Spark Medallion (paralelo) alimenta **treino/analítico**; dataprep Mongo alimenta **serving**. Dois destinos, um histórico.

Mostro no **T5–T6** do slide 13.

**[Próximo → slide 8]**

---

# SLIDE 8 — Observabilidade · ~3 min · Tópico 4

**[Slide 8]**

**Problema:** sem métricas, não cumpro SLO de latência nem detecto regressão.

**Separação que eu defendo:**

| Pilar | Ferramenta local | Cloud |
|-------|------------------|-------|
| Coleta de métricas | Prometheus | Monitor / CloudWatch |
| Visualização | Grafana | Workbooks / dashboards |
| APM / traces | (narrativa) | App Insights / X-Ray |
| Logs | `docker logs` | Log Analytics / Logs Insights |

**Por que Prometheus + Grafana:** padrão pull + PromQL; Actuator já expõe; em produção o desenho se mapeia 1:1.

Demo no **T11**: targets UP, dashboard **DataMaster — API Fraude**.

**[Próximo → slide 9]**

---

# SLIDE 9 — Segurança · ~3 min · Tópico 5

**[Slide 9]**

**Defesa em profundidade** — e honestidade sobre o que a mesa prova:

| Controle | Por quê | Mesa vs produção |
|----------|---------|------------------|
| TLS / crypto em repouso | Dado sensível em trânsito e disco | Desenho cloud |
| **Key Vault / KMS** | Secrets **fora do código**, rotação | `.env` local; Vault no Terraform |
| **Entra ID / IAM + RBAC** | Least privilege por workload | Narrativa; papéis no desenho |
| Mascaramento na app | Última milha (próximo slide) | **Código real** |

**Fala:**
> “Credencial não fica no repositório. Na demo mostro a camada de aplicação; cofre e identidade são o caminho de produção.”

**[Próximo → slide 10]**

---

# SLIDE 10 — LGPD · ~3 min · Tópico 6

**[Slide 10]**

**Problema:** antifraude precisa de sinal; **não** precisa expor PII em claro.

**O que uso:** `DataMasker` · `POST /api/v1/lgpd/mask` · aba LGPD no dashboard.

**Três conceitos (se perguntarem, nota 10):**

| | Mascaramento | Anonimização | Criptografia |
|---|--------------|--------------|--------------|
| Reversível? | Parcial | Não (ideal) | Sim (com chave) |
| Uso | UI / suporte | Analytics | Repouso / trânsito |

**Demo ao vivo (T4b):** dashboard :8501 → aba **LGPD / mascaramento**.

```bash
curl -s -X POST http://localhost:8080/api/v1/lgpd/mask \
  -H "Content-Type: application/json" \
  -d '{"cpf":"123.456.789-00","email":"joao.silva@banco.com.br","phone":"(11) 98765-4321","name":"Joao Silva","card_number":"1234 5678 9012 3456"}' \
  | python3 -m json.tool
```

**[Próximo → slide 11]**

---

# SLIDE 11 — Modelo analítico e features · ~3 min · Tópico 7

**[Slide 11]**

**Arquitetura analítica — por quê cada peça:**

- **Medallion** — engenharia: qualidade progressiva e replay.  
- **Kimball** — consumo: fato transações + dimensões (Synapse/Redshift). **Não substitui** Medallion.  
- **Features / perfis** — Cosmos narrativa, **Mongo local** `user_profiles` para `/analyze`.  
- **Gold** alimenta retreino; **perfis** alimentam decisão online.  
- **`governanca.yaml` + DQ report** — qualidade como contrato.

```bash
curl -s http://localhost:8080/api/v1/data-quality/report | python3 -m json.tool
```

Menciono notebook `01_dataprep_dq.py`.

**[Próximo → slide 12]**

---

# SLIDE 12 — Escalabilidade · ~3 min · Tópico 8

**[Slide 12]**

**Problema:** 10M+ tx/dia e picos. **Réplica sem partição certa não resolve.**

| Camada | Alavanca | Por quê |
|--------|----------|---------|
| Stream | Partições / shards | Paralelismo de consumidores |
| Batch | Workers Spark/Databricks | Throughput de histórico |
| Serving | RU/s Cosmos / escala Mongo | Leitura de perfil |
| API | Réplicas horizontais | Stateless + LB (produção) |
| Cache | Redis | Hot keys (stack pronta) |

**Honestidade:**
> “Dez milhões é **meta do desenho**. Na mesa mostro o caminho e onde puxo a alavanca — batch na API no T7 — não um load test de produção.”

**FinOps:** escalar com custo por 1M tx na conversa — capacidade sem custo previsível quebra o negócio.

**[Próximo → slide 13 — DEMO AO VIVO]**

---

# SLIDE 13 — Trilha T0–T12 · ~30 min · DEMO AO VIVO

**[Slide 13 — checklist na tela; alterno slide ↔ terminal ↔ browser]**

Banca, agora **opero a plataforma**. Em cada passo amarro ao tópico do edital.

## T0 — Stack no ar (~2 min)

```bash
docker compose ps --format "table {{.Name}}\t{{.Status}}"
bash scripts/status-stack.sh
```

*"Tudo que estava nos slides anteriores está aqui rodando."*

## T1 — Health (~1 min) · Obs / API

```bash
curl -s http://localhost:8080/health | python3 -m json.tool
```

## T2 — Swagger (~2 min) · Contrato

http://localhost:8080/swagger-ui.html — *"Contrato OpenAPI — a borda da plataforma."*

## T3 — Batch → Mongo (~3 min) · Armazenamento / Lambda

```bash
curl -s http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool
```

Se `profileCount` = 0: `bash scripts/run_demo.sh`

*"Perfis materializados pelo batch — prontos para o analyze. Slide 7b."*

## T4 — Dashboard (~5 min) · Consumo

http://localhost:8501 — fraudes, liberar caso, KPIs, opinião IA (se `DEEPSEEK_API_KEY`).

## T4b — LGPD (~2 min) · Tópico 6

Aba **LGPD / mascaramento** — *"Mascaramento na borda — não é anonimização."*

## T5–T6 — Analyze (~5 min) · Online + perfil

```bash
# Com perfil (T5)
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":150,"merchant_category":"Alimentação","user_country":"BR","merchant_country":"BR","payment_method":"CREDIT_CARD","hour":14,"user_id":"user_1001"}' \
  | python3 -m json.tool

# Suspeita + anomaly_reasons (T6)
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":50000,"merchant_category":"Viagem","user_country":"BR","merchant_country":"US","payment_method":"CREDIT_CARD","hour":3,"is_weekend":1,"is_international":1,"user_id":"user_1001"}' \
  | python3 -m json.tool
```

Aponto `anomaly_reasons` e limiar **0,74**. *"Batch alimenta online sem retreinar a cada request."*

## T7 — Batch na API (~2 min) · Escala (amostra)

Console :3333 → **Enviar lote**, ou:

```bash
curl -s -X POST http://localhost:8080/api/v1/transactions/batch \
  -H "Content-Type: application/json" \
  -d '[{"amount":150,"merchant_category":"Alimentacao","user_country":"BR","merchant_country":"BR","payment_method":"CREDIT_CARD","hour":14,"is_weekend":0,"is_international":0}]' \
  | python3 -m json.tool
```

## T4c — RabbitMQ + e-mail (~3 min) · Ingestão de alerta

Após fraude: http://localhost:15672 — fila `fraud.alert.email`

```bash
curl -s http://localhost:8090/actuator/health | python3 -m json.tool
docker logs fraud-email-worker --tail 25
```

*"HTTP não espera SMTP — por isso fila, não chamada síncrona."*

## T8 — Kafka (~3 min) · fato após o analyze

```bash
# Tópico alimentado pela API (após cada /analyze)
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092   --topic transaction-analyzed --from-beginning --max-messages 3
```

Consulta visual: dashboard aba **Kafka / eventos do dia** · Jupyter `02_kafka_consultas_dia.ipynb` · `curl …/api/v1/events/analyzed?date=today`

*"Score é HTTP síncrono; o evento vai ao Kafka assíncrono. Kafka não é DW eterno — Negócios lê Gold no lake por categoria."*

## T9 — Jupyter + Spark Medallion (~4 min) · Armazenamento

http://localhost:8888/?token=datamaster — topo do `01_dataprep_dq.py`  
http://localhost:18080 — Spark UI  
`ls data/lake/bronze data/lake/silver data/lake/gold`

*"Bronze intacto; Silver limpo; Gold para ML."*

## T10 — batch_dataprep_mongo (~1 min)

Menciono o script — já rodou no T3.

## T11 — Prometheus + Grafana (~3 min) · Observabilidade

:9090 targets · :3000 dashboard DataMaster. *"Coleta separada de visualização."*

## T12 — Fluxo completo (~2 min)

```bash
bash scripts/run_demo.sh   # se ainda não rodou
```

Valido lake + perfis. Se perguntarem containers → **Apêndice draw.io**.

**[Próximo → slide 14]**

---

# SLIDE 14 — Mapa multicloud · ~3 min

**[Slide 14 — tabela Azure / AWS]**

Fecho serviço a serviço — mesma tabela do slide.

**Fala:**
> “Não escolhi vendor; escolhi **padrões**. Local opero ao vivo; VPS e Azure têm o mesmo desenho provisionado; AWS prova portabilidade.”

**[Próximo → slide 15]**

---

# SLIDE 15 — Encerramento · ~2 min + perguntas

**[Slide 15 — agradecimento]**

Banca, para encerrar:

Não era uma lista de ferramentas. Em cada camada expliquei o **porquê** — Medallion, perfis, API, fila, LGPD, observabilidade, mapa multicloud — e mostrei a plataforma rodando. Engenharia de dados é **decisão justificada**, não catálogo.

Obrigado. Fico à disposição para perguntas.

---

# APÊNDICE — Diagramas draw.io (só roteiro · não é slide)

**Quando usar:** se perguntarem “cadê o desenho do Docker?” ou “qual serviço na Azure?” — abro no laptop, **sem sair do fluxo dos slides**.

Abrir em https://app.diagrams.net → **File → Open from Device** → `docs/arquitetura/`

| Arquivo | Quando abrir | Conteúdo |
|---------|--------------|----------|
| `datamaster-04-docker-compose.drawio` | Tour de containers / T0 | Cada serviço do compose e quem chama quem |
| `datamaster-03-mapa.drawio` / `.png` | Pergunta nuvem | Equivalência local ↔ Azure ↔ AWS |
| `datamaster-01-batch-medallion.drawio` | Junto ao slide 7 | Ingest · Store · Process · Serve |
| `datamaster-02-online-gateway.drawio` | Junto ao slide 6b | LB/Gateway apagados · caminho demo |
| `datamaster-02-online.drawio` | Demo T4–T7 | Console → API → Mongo |
| `datamaster-01-batch.drawio` | Demo T3 / T9 | JSON → dataprep → lake |
| `datamaster-azure-aws-local.drawio` | Encerramento | Abas Azure, AWS, mesa local |
| `datamaster-00-visao-geral.drawio` | Reforço slide 4 | Batch + online Lambda |

**O que digo:** *“Os diagramas estão versionados no repositório; abro o draw.io se quiserem ver container por container.”*

Regenerar: `python3 scripts/generate_architecture_drawio.py` · Índice: `docs/arquitetura/README.md`

---

## Se a banca perguntar… (cola de defesa)

| Pergunta | Resposta (com slide) |
|----------|----------------------|
| Por que esse componente? | Problema → escolha → trade-off (guias `topico-0N-*.md`) |
| Onde está o lake? | Slide 7/7c · `data/lake/` + MinIO :9001 (T9) |
| API usa Postgres? | Slide 7c · scoring: Mongo; Postgres = OLTP referência |
| Kafka no analyze? | Score HTTP síncrono; publish Kafka **assíncrono** depois (slide 6 / T8) |
| Histórico eterno no Kafka? | Não — retenção/replay; definitivo no lake/Gold por categoria |
| Por que Java na API? | Contrato OpenAPI, Actuator, AMQP, Kafka, stack bancária |
| Por que Mongo e não só Postgres? | Documento de perfil flexível + leitura por user_id |
| Por que Kafka e Rabbit? | Fato ≠ tarefa. Poderia unificar; só Kafka = alerta pesado; só Rabbit = fraco para replay/Gold. Cloud: Event Hubs + Service Bus |
| Retreino online? | Slide 11 · perfis batch; `/model/metrics` é referência |
| E-mail saiu? | Slide 6b · T4c · Rabbit + worker |
| Provou 10M tx? | Meta do desenho; mesa prova caminho e alavancas |
| Key Vault na demo? | Terraform/Azure; local `.env` — não overclaim |
| Mascaramento = anônimo? | Não — ver tabela slide 10 |
| Por que não Prom/Grafana na Azure? | Podem (managed). PaaS métrica = Monitor. Equivalência = capacidade; híbrido ok |
| Dynatrace / Kibana? | APM ≈ App Insights; Kibana = logs ≠ Prometheus SLO |

---

## Plano B

| Falha | Ação |
|-------|------|
| Demo cai no slide 13 | Narrar com **Apêndice draw.io** + um `curl` analyze |
| Sem tempo | Encurtar T8–T10; manter T1–T7 + slide 14 |
| Grafana vazio | T11 só Prometheus target UP |

---

## Ensaio alinhado

```bash
bash docs/estudos/ensaio-90min.sh
```

Estudo por tópico: [plano-estudo-8-topicos.md](plano-estudo-8-topicos.md)

## Referências

- **Cola 1 página (imprimir):** [cola-1-pagina.md](cola-1-pagina.md)
- Slides: `portal/banca.html`
- Checklist: `docs/operacao/CHECKLIST_DEMO_BANCA.md`
- Tour componentes: `docs/operacao/ROTEIRO_TOUR_COMPONENTES.md`
