# Tópico 2 — Ingestão (slides 6 e 6b)

## 1. O que é
Colocar o dado **dentro** da plataforma: **streaming** (contínuo) e **batch** (janelas/histórico), com serving unificado (Lambda).

## 2. Problema que resolve
- Stream: decidir fraude em **segundos** e **propagar o fato** da análise sem travar o HTTP.  
- Batch: histórico, reprocessamento, features e **perfis**.  
- Fila de alerta: não travar a API esperando SMTP.

## 3. Componentes usados
| Componente | Papel |
|------------|--------|
| API Java :8080 | Speed layer — scoring HTTP síncrono |
| Kafka local | Após `/analyze`, publica `transaction-analyzed` **assíncrono** |
| `batch_dataprep_mongo.py` | Batch de perfis |
| Spark / `spark_local_pipeline.py` | Batch Medallion |
| RabbitMQ + email-worker | Alerta assíncrono de e-mail (tarefa, não log de negócio) |
| Mongo `analyzed_events` | Espelho consultável dos eventos (Jupyter/dashboard) |

**Caminho real da demo online:**
```text
Console/Dashboard → API → Mongo (perfil) → resposta HTTP
                         │
                         ├── (sempre) Kafka transaction-analyzed  [async]
                         └── (se fraude) RabbitMQ → email-worker
```

## 4. Por que cada um
- **HTTP `/analyze`:** canal precisa do score na hora (&lt;2s).  
- **Kafka após a decisão:** log de eventos com categoria, CPF e `card_last4` — Negócios/analytics consomem sem acoplar à latência.  
- **Batch dataprep:** materializa perfil histórico para o online.  
- **RabbitMQ:** work queue pontual (e-mail); Kafka seria overkill para “mande este e-mail”.  
- **Não retenho infinito no Kafka:** broker = replay/retenção curta; histórico definitivo = lake → Gold por categoria.

## 5. Onde entra
Depois da extração: a API decide; o evento alimenta stream/analytics; o batch alimenta perfis e lake.

## 6. Local
- Analyze: `POST /api/v1/transactions/analyze`  
- Eventos do dia: `GET /api/v1/events/analyzed?date=today`  
- Dashboard: aba **Kafka / eventos do dia**  
- Jupyter: `notebooks/02_kafka_consultas_dia.ipynb`  
- Broker: tópico `transaction-analyzed` (T8)

## 7. Azure / AWS
| Função | Azure | AWS | Local |
|--------|-------|-----|-------|
| Stream / fato | Event Hubs | Kinesis / MSK | Kafka |
| Capture → lake | Event Hubs Capture / Databricks | Firehose / Glue | consumer → Bronze (alvo) |
| Batch orquestrado | Data Factory | Glue / Step Functions | scripts + compose |
| Alerta | Service Bus | SQS + Lambda | RabbitMQ + worker |

## 8. Alternativa e trade-off
| Alternativa | Trade-off |
|-------------|-----------|
| Só batch diário | Simples; perde meta &lt;2s |
| Só stream (Kappa) | Unifica; reprocessamento histórico mais caro |
| Kafka também para e-mail | Possível; overkill — mistura fato e tarefa; Service Bus/SQS é o par natural |
| Só Rabbit para tudo | Resolve e-mail; fraco como log de negócio com replay → lake/Gold |
| Os dois (escolhido) | Kafka = fato; Rabbit = tarefa — alinhado a Event Hubs + Service Bus |
| Kafka como DW eterno | Possível (`retention=-1`); caro, ruim para BI e LGPD |
| Consumer → Bronze → Gold por categoria | Caminho certo para Negócios (taxa de fraude por categoria) |

## 9. Como demonstrar
1. `POST /analyze` (com ou sem fraude)  
2. Dashboard aba Kafka **ou** `GET /events/analyzed`  
3. Consumer:  
   `docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic transaction-analyzed --from-beginning --max-messages 3`  
4. Jupyter: abrir `02_kafka_consultas_dia.ipynb` (gráficos do dia)  
5. Se perguntarem histórico eterno: falar retenção + Gold no lake

## 10. Fala
> “Ingestão em dois modos: streaming e batch. O scoring é HTTP síncrono porque o canal precisa da decisão agora. Em paralelo, publico o fato `transaction-analyzed` no Kafka — com categoria, CPF e só o final do cartão — sem aumentar a latência da resposta. RabbitMQ fica para o e-mail. Kafka não é meu DW: retenho para replay; o histórico analítico para Negócios vai ao lake e vira Gold por categoria.”

## 10b. Defesa Kafka × Rabbit (cola / Q&A)
> “Eu poderia unificar num broker só. Separei porque Kafka registra o **fato** e Rabbit executa a **tarefa**. Só Kafka deixa o alerta mais pesado do que precisa; só Rabbit deixa fraco o log com replay para o lake. No cloud: Event Hubs + Service Bus — o porquê é o mesmo. Não usei os dois ‘para estudar’ — usei porque os problemas são diferentes.”

## 11. Perguntas
| Pergunta | Resposta |
|----------|----------|
| Kafka no analyze? | Sim, **depois** do score, assíncrono — HTTP não espera o broker |
| Histórico fica no Kafka pra sempre? | Não — retenção/replay; definitivo no lake/Gold |
| Por que categoria no evento? | Negócios mede fraude por categoria |
| Kafka vs Rabbit? | Fato (“aconteceu”) ≠ tarefa (“envie e-mail”). Poderia unificar; separei pelo problema. Só Kafka = alerta pesado; só Rabbit = fraco para replay/Gold. |
| Usei os dois só para estudar? | **Não diga isso.** Diga: problemas diferentes → ferramentas diferentes. |
| Lambda vs Kappa? | Lambda: speed + batch (meu desenho) |

## 12. Transição
> “O dado ingerido e o evento precisam **pousar e servir** — lake, warehouse e NoSQL. Próximo: armazenamento.”

**Próximo:** [topico-03-armazenamento.md](topico-03-armazenamento.md) · Detalhe Kafka: [kafka.md](kafka.md)
