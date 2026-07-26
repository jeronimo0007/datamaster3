# Cola 1 página — apresentador (tela privada no Meet)

**Tela 1 (Meet):** http://localhost:8880/banca.html — só a banca vê  
**Tela 2 (você):** http://localhost:8880/cola.html — demos, falas, comandos  

**Não compartilhe a cola no Meet.**

**Pré-voo:** `bash scripts/run_demo.sh` · `bash scripts/status-stack.sh`

**Mantra:** o **porquê** manda; o **quê** só ilustra.  
Fórmula: problema → escolhi X porque… → alternativa Y → na mesa mostro…

> Os blocos **“Demo ao vivo”** saíram do `banca.html` (slides limpos) e estão em `cola.html` + abaixo.

---

## Porquês em 1 linha (comece a frase por “porque / escolhi”)

| Tópico | Frase |
|--------|-------|
| Extração | Escolhi adapter porque o modelo não pode depender do schema do core |
| Ingestão | Stream porque latência + fato async; batch porque histórico e perfis |
| Online | Score sync; Kafka = fato; Rabbit = tarefa e-mail (não “para estudar”) |
| Lake | Medallion porque reprocesso sem perder a landing |
| Mongo | Documento por user_id porque online precisa de ms, não scan no lake |
| Obs | Prometheus coleta e Grafana mostra — papéis separados de propósito |
| Segurança | Secrets fora do código porque rotação e blast radius |
| LGPD | Mascaro na borda porque preciso de sinal, não de PII em claro |
| Arquitetura | Medallion = engenharia; Kimball = BI; perfil = serving |
| Escala | Particiono porque réplica sem chave certa não remove gargalo |

---


## Defesa rápida — Kafka × Rabbit (slide 6b)

**Não diga:** usei os dois para estudar.  
**Diga:** Kafka = fato (“análise aconteceu”); Rabbit = tarefa (“envie o e-mail”).

| Só Kafka? | Viável para alerta; overkill + mistura fato/tarefa; cloud natural = Service Bus/SQS |
| Só Rabbit? | Resolve e-mail; fraco como log com replay → lake/Gold |
| Os dois | Event Hubs/Kinesis (fato) + Service Bus/SQS (tarefa) — mesmo porquê |

**Fala:** “Eu poderia unificar. Separei porque problemas diferentes. Só Kafka deixa o alerta pesado; só Rabbit deixa fraco o barramento analítico.”

---

## Defesa — por que não Kafka na Azure/AWS? (tópico 2)

| Lugar | Produto | Por quê |
|-------|---------|---------|
| Mesa / k3s | Kafka | Broker que opero localmente |
| Azure | Event Hubs | PaaS nativo; Capture → ADLS; mesmo papel |
| AWS | Kinesis ou MSK | Stream gerenciado / Kafka gerenciado |

**Fala:** “Kafka é o padrão. Na mesa uso Kafka; na Azure o equivalente é Event Hubs. Eu poderia subir Kafka na nuvem; preferiria o PaaS nativo. Um desenho, três lugares — o produto muda, o papel não.”

---

## Defesa — armazenamento (tópico 3)

**Só Postgres?** Não — fraco para lake/ML e perfil em ms.  
**API usa Postgres?** **Não** no score. Score = Mongo. Postgres = OLTP referência.  
**Mongo vs lake no /analyze?** Lake = batch/reprocessar; score precisa lookup em ms → perfil materializado no Mongo.  
**Medallion:** Bronze bruto · Silver DQ · Gold ML/BI.  
**Gold vs Kafka:** Negócios lê Gold; Kafka = fato com retenção/replay.

**Fala:** “Separei por carga. Scoring é Mongo, não Postgres. Lake não serve o online.”

---

## Defesa — Observabilidade (tópico 4 / slide 8)

**Pilares:** métricas ≠ logs ≠ traces ≠ visualização.

| Mesa | Azure | AWS |
|------|-------|-----|
| Prometheus + Grafana | Monitor + App Insights | CloudWatch + X-Ray |

**Por que equivalência?** Capacidade, não proibição. Prom/Grafana *podem* na nuvem (managed). Métrica de PaaS (Event Hubs, Cosmos…) só no Monitor/CW. Produção: híbrido (Prom app + nativo PaaS + Grafana).

**SLIs (decore):** latência `/analyze` (&lt;2s) · disponibilidade `/health` · taxa de erro. SLO = meta; SLI = indicador.

**Tracing na mesa?** **NÃO** — mesa = métricas; tracing = App Insights/X-Ray (nuvem).

**Classes:** Dynatrace = APM (≈ App Insights) · Kibana = logs (≈ Log Analytics) · Prometheus = métricas · Grafana = visualização. Não são rivais diretos.

**Só Grafana?** Não coleta sozinho.

**Fala:** “Na mesa Prometheus prova métricas. Na nuvem o papel é o mesmo; PaaS usa o nativo. SLI: latência do /analyze, health, erro.”

---
## Tópico 1 — Extração (treino consolidado)

**Problema:** fontes heterogêneas → sem contrato, core quebra modelo/lake/API.  
**Por quê adapter:** desacopla / normaliza; muda a fonte, não o scoring.  
**Por quê simulador:** não tenho core na sala.  

**Fala slide 5:**  
“Extração é contrato. Simulo o core e uso adapters. Scoring não depende do schema de quem enviou. Azure: Event Hubs/ADF→ADLS; AWS: Kinesis/Glue→S3 — o porquê é o mesmo.”

**Trade-off:** rejeitei ligar ML no schema do core (dívida).  

**Demo (só cola):** console :3333 → Gerar JSON → `data/transactions.json` → `transaction_adapters.py` (`from_simulator_record`).

---

| Slide | Tempo | Acum. | Na banca.html (Meet) | Na cola (você) |
|:-----:|:-----:|:-----:|----------------------|----------------|
| **0** | 3 min | 0:03 | Card apresentador | Só fala |
| **1** | 2 min | 0:05 | Capa | Três frentes |
| **1b** | 2 min | 0:07 | Três lugares | — |
| **2** | 3 min | 0:10 | Agenda 8 tópicos | Lembrar: porquê > quê |
| **3** | 4 min | 0:14 | Contexto | Meta &lt;2s · 10M · LGPD |
| **4** | 5 min | 0:19 | Visão geral | Por quê de cada bloco |
| **5** | 3 min | 0:22 | Extração (teoria) | **Demo** console + adapters |
| **6** | 4 min | 0:26 | Ingestão Lambda | **Demo** analyze → Kafka async · eventos do dia |
| **6b** | 3 min | 0:29 | Online gateway | API→Mongo→resposta; Kafka async; Rabbit se fraude |
| **7** | 4 min | 0:33 | Medallion | **Demo** `data/lake/` T9 |
| **7c** | 3 min | 0:36 | Lake+DW+ops | Postgres ≠ scoring |
| **7b** | 3 min | 0:39 | Batch→Mongo | **Demo** profile-stats + analyze |
| **8** | 3 min | 0:42 | Observabilidade | **Demo** T11 Prom/Grafana |
| **9** | 3 min | 0:45 | Segurança | Honestidade Vault |
| **10** | 3 min | 0:48 | LGPD | **Demo** aba LGPD / curl mask |
| **11** | 3 min | 0:51 | Arquitetura | **Demo** DQ report |
| **12** | 3 min | 0:54 | Escala | Batch API T7 · 10M = meta |
| **13** | **30 min** | **1:24** | Trilha T0–T12 | Comandos abaixo |
| **14** | 3 min | 1:27 | Mapa multicloud | Padrões ≠ vendor |
| **15** | +Q&A | — | Encerramento | “Decisão justificada” |

---

## Demos ao vivo por slide (resumo)

| Slide | O que fazer na tela 2 / terminal |
|------:|----------------------------------|
| 5 | :3333 Gerar JSON · `transaction_adapters.py` |
| 6 | Analyze → consumer `transaction-analyzed` · dashboard Kafka · Jupyter |
| 6b | Caminho: score sync + Kafka async + Rabbit e-mail |
| 7/7c | `ls data/lake/*` · Spark :18080 |
| 7b | `profile-stats` · analyze com `user_id` |
| 8 | :9090 targets · :3000 |
| 9 | Citar `.env` / Vault desenho |
| 10 | :8501 aba LGPD · ou curl mask |
| 11 | `curl …/data-quality/report` |
| 12 | POST batch · `/model/metrics` |
| 13 | Trilha T0–T12 completa |

---

## Slide 13 — T0–T12

| Step | Comando / URL |
|:----:|---------------|
| T0 | `docker compose ps` · `bash scripts/status-stack.sh` |
| T1 | `curl -s localhost:8080/health \| python3 -m json.tool` |
| T2 | http://localhost:8080/swagger-ui.html |
| T3 | `curl -s localhost:8080/api/v1/batch/profile-stats \| python3 -m json.tool` |
| T4 | http://localhost:8501 |
| T4b | Aba LGPD |
| T5–T6 | Analyze ↓ |
| T7 | :3333 lote ou POST batch |
| T4c | :15672 · `docker logs fraud-email-worker --tail 25` |
| T8 | Consumer `transaction-analyzed` · dashboard/Jupyter do dia |
| T9 | :8888 · :18080 · `ls data/lake/*` |
| T11 | :9090 · :3000 |

---

## Comandos copiar-colar

```bash
curl -s http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool

curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":150,"merchant_category":"Alimentação","user_country":"BR","merchant_country":"BR","payment_method":"CREDIT_CARD","hour":14,"user_id":"user_1001"}' | python3 -m json.tool

curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":50000,"merchant_category":"Viagem","user_country":"BR","merchant_country":"US","payment_method":"CREDIT_CARD","hour":3,"is_weekend":1,"is_international":1,"user_id":"user_1001"}' | python3 -m json.tool

curl -s -X POST http://localhost:8080/api/v1/lgpd/mask \
  -H "Content-Type: application/json" \
  -d '{"cpf":"123.456.789-00","email":"joao@banco.com.br","phone":"(11) 98765-4321"}' | python3 -m json.tool
```

---

Plano B: API cai → 1 curl analyze · Sem tempo → cortar T8–T10.

Cola web: http://localhost:8880/cola.html · Roteiro: [apresentacao-90min.md](apresentacao-90min.md)

## Segurança 360° (respostas duras)

| Perguntaram | Diga |
|---|---|
| TLS no Kafka? | Mesa PLAINTEXT em rede interna; prod SASL_SSL + ACL por tópico (Event Hubs/MSK já TLS) |
| OAuth2/JWT? | Resource server valida JWT do Entra/Cognito; client credentials M2M, PKCE p/ humano |
| API key serve? | Não: sem expiração, sem escopo, sem identidade |
| Front → API | Mesa CORS aberto (lab); prod gateway + token, core em rede privada |
| Gateway faz o quê? | TLS, JWT, rate limit, WAF, mTLS backend, scrubbing de PII, versionamento |
| Bronze/Silver/Gold | Identidade por job + RBAC por camada; Gold sem PII; CMK + private endpoint |
| Senha no repo? | Credencial de **lab** documentada; segredo real no `.gitignore`; tudo via env var → cofre |
| Auditoria | Activity Log/Diagnostic · CloudTrail |
| PII no evento Kafka | CPF + só final do cartão; prod = CPF tokenizado, PAN nunca |

**Postura:** nunca "é seguro" — sempre "na mesa X, em produção Y, porque Z".

## LGPD (tópico 6 / slide 10)

**Não misture:** Segurança = canal/cofre/quem acessa · LGPD = o dado pessoal (minimizar/mascarar).

| Técnica | Reversível? | Uso |
|---------|-------------|-----|
| Mascaramento | Parcial | UI / DataMasker |
| Anonimização | Não | Analytics / Gold agregada |
| Criptografia | Sim (chave) | Repouso/trânsito — **não** substitui máscara |

**Armadilhas:** mascarei ≠ anonimizei · crypto no disco ≠ LGPD na tela · **SHA ≠ crypto** (hash é mão única; AES/TLS recuperam com chave).

| Perguntaram | Diga |
|---|---|
| Anônimo? | Não — mascaramento |
| Só crypto? | Não — operador vê PII na API |
| Por que na API? | Front mente (DevTools); um contrato na borda |
| Kafka | CPF + só final do cartão; prod tokeniza |
| Gold tem CPF? | Não deve |

**Fala:** “Antifraude precisa de sinal, não de CPF em claro. Máscara na borda. Três controles diferentes.”


**Conceitos p/ engenheiro:** minimização · finalidade · PII · máscara ≠ pseudo ≠ anônimo · crypto ≠ máscara · retenção · esquecimento · Bronze restrita / Gold sem PII.

**Kafka × Gold:** Kafka = CPF/token + last4 (curto) · Gold = sem PII agregado · Bronze = bruto governado.

---


## Arquitetura (tópico 7) — mapa rápido

| Pergunta | Família | Aqui |
|----------|---------|------|
| Tempo / pipeline | Lambda (não Kappa) | API+Kafka + batch Spark |
| Qualidade no lake | Medallion | B→S→G |
| Modelo BI | Kimball | Narrativa DW |
| Serving online | Perfil | Mongo |

**Por quê Medallion:** landing intacta + DQ progressivo + Gold p/ ML/BI.  
Lambda/streaming = arquitetura de *pipeline*; Medallion = *lake*; Kimball = *consumo* — se complementam.

