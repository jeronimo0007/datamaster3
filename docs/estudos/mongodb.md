# MongoDB — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Armazena **perfis históricos** (`user_profiles`) para o `/analyze` |
| **Container** | `mongodb` |
| **Porta** | **27017** |
| **Database** | `fraud_detection` |
| **Credenciais** | `admin` / `admin123` (authSource `admin`) |
| **Equivalente Azure** | Cosmos DB (narrativa; TF usa SQL API) |

Frase curta:

> *"Perfis batch por usuário — a API compara transação ao vivo com o comportamento histórico."*

---

## Onde entra na arquitetura

```text
data/transactions.json
        │
        ▼
batch_dataprep_mongo.py  ──►  MongoDB.user_profiles
                                      │
                                      ▼
                              POST /analyze (API)
                              (anomaly_score_boost)
```

Script: `scripts/batch_dataprep_mongo.py`  
Serviço Docker: `batch-prep` (profile `batch`)

---

## Estrutura do perfil (resumo)

Campos agregados por `user_id`:

- `tx_count`, `avg_amount`, `std_amount`, `p95_amount`
- `typical_categories`, `typical_payment_methods`
- `pct_international`, `avg_hour`, `historical_fraud_rate`

---

## Demo prática (5 min)

### 1. Via API (mais fácil na banca)

```bash
curl -s http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool
```

Esperado: `profileCount` > 0, `sampleUserIds`.

### 2. Via mongosh (1 min)

```bash
docker exec -it mongodb mongosh -u admin -p admin123 --authenticationDatabase admin
```

No shell:

```javascript
use fraud_detection
db.user_profiles.countDocuments()
db.user_profiles.findOne()
db.user_profiles.find({}, {user_id:1, tx_count:1, avg_amount:1}).limit(5)
```

### 3. Rodar batch manualmente (1 min)

```bash
docker compose --profile batch run --rm batch-prep
curl -s http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool
```

### 4. Provar impacto no scoring (2 min)

Analyze com `user_id` que existe no perfil vs usuário inexistente:

```bash
# Com perfil (user do sampleUserIds)
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":8000,"merchant_category":"Eletrônicos","user_id":"user_1001","hour":14}' \
  | python3 -m json.tool | grep -E "anomaly|fraud_score|is_fraud"

# Sem perfil
curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"amount":8000,"merchant_category":"Eletrônicos","user_id":"user_sem_historico","hour":14}' \
  | python3 -m json.tool | grep -E "anomaly|fraud_score|is_fraud"
```

Mostre diferença em `user_profile.anomaly_reasons` e `anomaly_score_boost`.

---

## Roteiro de fala (30 s)

> *"O Mongo guarda o serving layer dos perfis — resultado do batch sobre histórico. Quando chega uma transação, a API não retreina; ela consulta o perfil e calcula desvio. Em Azure seria Cosmos ou cache de features."*

---

## Perguntas frequentes

| Pergunta | Resposta |
|----------|----------|
| Por que Mongo e não Postgres? | Documentos flexíveis para perfil agregado; Postgres mostra OLTP relacional |
| Onde roda o batch? | `batch_dataprep_mongo.py` ou serviço `batch-prep` |

---

## Checklist

- [ ] `profile-stats` > 0
- [ ] Mostrei um documento `user_profiles`
- [ ] Comparei analyze com/sem perfil
- [ ] Mencionei script `batch_dataprep_mongo.py`

---

## Referências

- `scripts/batch_dataprep_mongo.py`
- `scripts/init_mongo.js`
- Dashboard sidebar — contagem perfis
