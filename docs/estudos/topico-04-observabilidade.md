# Tópico 4 — Observabilidade (slide 8)

## 1. O que é
Capacidade de **ver, medir e alertar** o comportamento da plataforma: métricas, logs, traces (pilares).

## 2. Problema que resolve
Sem observabilidade, fraude “funciona até quebrar”. Não sei latência do `/analyze`, se o target caiu, nem se o SLO de &lt;2s está sendo cumprido.

## 3. Componentes usados
| Componente | Papel |
|------------|--------|
| Prometheus :9090 | Coleta (pull) de métricas |
| Grafana :3000 | Visualização / dashboard |
| Spring Actuator `/actuator/prometheus` | Expõe métricas da API |
| Narrativa | Azure Monitor + App Insights · AWS CloudWatch + X-Ray |

## 4. Por que cada um
- **Prometheus:** padrão de métricas pull, labels, PromQL — portável (AMP, Azure Managed Prometheus).  
- **Grafana:** UI de operação; separa **coleta** de **visualização**.  
- **Actuator:** instrumentação nativa Spring sem reinventar.  
- **Não misturo:** métricas ≠ logs ≠ traces — cada um responde pergunta diferente.

## 5. Onde entra
Camada transversal: observa API, (em produção) consumers, filas, lake jobs.

## 6. Local
Targets UP em :9090 · dashboard **DataMaster — API Fraude** em :3000 · health em `/health`.

## 7. Azure / AWS
| Pilar | Azure | AWS | Local |
|-------|-------|-----|-------|
| Métricas | Monitor | CloudWatch | Prometheus |
| APM / traces | App Insights | X-Ray / OTel | (narrativa; mesa = métricas) |
| Logs | Log Analytics | Logs Insights | `docker logs` |

## 8. Alternativa e trade-off
| Alternativa | Trade-off |
|-------------|-----------|
| Só logs | Debug útil; ruim para SLO e tendência |
| Datadog/New Relic | Ricos; custo e vendor lock |
| Push metrics só | Ok em serverless; Prometheus pull é o padrão da stack Java |

## 9. Como demonstrar (T11)
1. :9090 → Status → Targets → `fraud-api` **UP**  
2. :3000 → pasta DataMaster  
3. Disparar analyze e mostrar série (se painel tiver request rate)

## 10. Fala
> “Observabilidade para mim é separar coleta, visualização e alerta. Na mesa, Prometheus raspa a API e o Grafana mostra. Em Azure seria Monitor e App Insights; o desenho é o mesmo.”

## 11. Perguntas
| Pergunta | Resposta |
|----------|----------|
| Por que não só Grafana? | Grafana não coleta sozinho — precisa de fonte (Prometheus) |
| Tem tracing na mesa? | Métricas sim; tracing distribuído é narrativa cloud (App Insights/X-Ray) |
| Qual SLI? | Latência do `/analyze`, disponibilidade `/health`, taxa de erro |
| Por que equivalência Monitor e não Prom na Azure? | Prom *pode* (managed). Métrica de PaaS só no Monitor. Equivalência = capacidade. Híbrido em produção. |
| Dynatrace / Kibana? | Dynatrace = APM (≈ App Insights). Kibana = logs/busca (≠ Prometheus SLO). |

## 12. Transição
> “Ver o sistema não basta — preciso **proteger** o dado. Segurança.”

**Próximo:** [topico-05-seguranca.md](topico-05-seguranca.md)
