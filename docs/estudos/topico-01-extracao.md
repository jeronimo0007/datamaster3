# Tópico 1 — Extração (slide 5)

## 1. O que é
Trazer dados de **fontes heterogêneas** (core, API, arquivo, parceiro) para um **contrato canônico** que o restante da plataforma entende.

## 2. Problema que resolve
Sem contrato e adapters, cada fonte quebra o modelo, o lake e a API. Extração mal feita = dívida eterna de schema.

## 3. Componentes usados
| Componente | Papel |
|------------|--------|
| `data-generator-console` (:3333) | Simula canal/core na mesa |
| `scripts/generate_data.py` | Gera histórico JSON (landing) |
| `transaction_adapters.py` | Normaliza formatos → dict do modelo |
| Contrato JSON | Campos mínimos: amount, hour, flags, categoria, payment_method |

## 4. Por que cada um
- **Simulador:** não tenho core banking na banca; preciso de volume controlado e reprodutível.  
- **`generate_data.py`:** gera lote histórico para Bronze + dataprep de perfis.  
- **Adapters:** desacoplam fonte do modelo — muda o core, não reescrevo o scoring.  
- **Contrato JSON:** schema explícito para API, Spark e treino falarem a mesma língua.

## 5. Onde entra no DataMaster
Primeiro elo: **fonte → contrato →** (depois) ingestão stream/batch.

## 6. Local
Console gera JSON / chama API. Adapter: `from_simulator_record` / `normalize_for_model`. Landing: `data/transactions.json`.

## 7. Azure / AWS
| Local | Azure | AWS |
|-------|-------|-----|
| Console + scripts | Event Hubs producer + ADF Copy | Kinesis producer + Glue/Step Functions |
| JSON em disco | Landing ADLS Raw/Bronze | Landing S3 Raw/Bronze |
| Adapters Python | Mesmo padrão em Function/Databricks job | Mesmo padrão em Lambda/Glue |

## 8. Alternativa e trade-off
| Alternativa | Trade-off |
|-------------|-----------|
| Ligar o modelo direto no schema do core | Acoplamento; qualquer mudança no core quebra ML |
| Só CSV fixo sem adapter | Rápido no POC; não escala a multi-fonte |
| Schema Registry (Avro/Protobuf) | Mais governança; overhead para demo local |

## 9. Como demonstrar
1. Abrir console :3333 → Gerar JSON  
2. Mostrar `data/transactions.json`  
3. Abrir `src/data_ingestion/transaction_adapters.py`  
4. Citar `event_hub_producer.py` como narrativa de publicação

## 10. Fala (1ª pessoa)
> “Extração aqui é contrato. Eu simulo o core com o console e o `generate_data.py`, e o `transaction_adapters` normaliza qualquer fonte para o dicionário do modelo. Assim o scoring e o lake não dependem do formato de quem enviou.”

## 11. Perguntas da banca
| Pergunta | Resposta |
|----------|----------|
| Por que não usar o banco do core direto? | Isolamento e contrato; core muda; plataforma precisa de canônico |
| O adapter está em produção? | Padrão implementado no repo; na mesa o simulador já cai no formato da API |
| E Data Factory? | Orquestra cópia/validação na nuvem; na mesa o script + console fazem o papel de landing |

## 12. Transição
> “Com o contrato definido, preciso **ingerir** — em stream para tempo real e em batch para histórico. Isso é o próximo slide.”

**Próximo:** [topico-02-ingestao.md](topico-02-ingestao.md)
