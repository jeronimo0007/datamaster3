# Tópico 8 — Escalabilidade (slide 12)

## 1. O que é
Capacidade de **crescer throughput e carga** sem quebrar latência/SLO — cada camada com alavanca própria.

## 2. Problema que resolve
Meta de **10M+ tx/dia** e picos. Só “subir máquina” sem partição/consumer/réplica certa **não** resolve.

## 3. Componentes / alavancas
| Camada | Alavanca |
|--------|----------|
| Streaming | Partições Event Hubs / shards Kinesis / partições Kafka |
| Batch | Workers Databricks / EMR |
| Serving NoSQL | RU/s Cosmos / WCU DynamoDB / índices Mongo |
| API | Réplicas AKS / Container Apps / ECS |
| Cache | Redis (sessão/hot keys) |
| Lake | Particionamento por data/canal |

## 4. Por que assim
- **Particionar stream:** paralelismo real de consumidores.  
- **Escalar API horizontalmente:** stateless + load balancer (produção).  
- **Separar batch:** jobs pesados não competem com path &lt;2s.  
- **FinOps:** capacidade com custo por 1M tx — escala sem controle quebra o negócio.

## 5. Onde entra
Fecha o edital: a arquitetura não é só “bonita” — é **operável sob carga**.

## 6. Local — honestidade
Na mesa mostro **padrão** (batch na API, vários containers), **não** um teste de 10M tx.  
Frase segura: *“A meta 10M é capacidade-alvo do desenho; a demo prova o caminho e os pontos de escala.”*

## 7. Azure / AWS
Autoscaling nativo: Event Hubs TU, Databricks clusters, Cosmos RU, AKS HPA · na AWS: Kinesis shards, EMR, DynamoDB on-demand, EKS HPA.

## 8. Alternativa e trade-off
| Alternativa | Trade-off |
|-------------|-----------|
| Vertical scaling só | Limite rápido; ponto único |
| Mais partições sem chave boa | Hot partition (ex.: um `user_id` quente) |
| Cache sem invalidação | Latência boa; risco de perfil stale |

## 9. Como demonstrar (T7)
```bash
curl -s -X POST http://localhost:8080/api/v1/transactions/batch ...
curl -s http://localhost:8080/api/v1/model/metrics | python3 -m json.tool
docker compose ps   # cite serviços escaláveis em orquestrador
```

## 10. Fala
> “Escalo por camada: partições no stream, workers no Spark, RU no serving, réplicas na API. A meta de dez milhões por dia é do desenho — na mesa mostro o caminho e onde eu puxaria a alavanca. Sem particionamento certo, réplica a mais não resolve.”

## 11. Perguntas
| Pergunta | Resposta |
|----------|----------|
| Provou 10M? | Não na mesa; meta de arquitetura + pontos de escala |
| Redis está no scoring? | Na stack para cache; path crítico demo = API + Mongo |
| Gargalo típico? | Hot key no perfil; consumer lag; I/O do lake mal particionado |

## 12. Transição
> “Teoria fechada. Agora **opero** a plataforma — slide 13, trilha T0–T12.”

Volta ao índice: [plano-estudo-8-topicos.md](plano-estudo-8-topicos.md)
