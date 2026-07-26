# Fluxo completo da demo — guia de estudo

Material pessoal de estudo. Orquestra **todas as peças** em sequência — use como aquecimento antes da banca.

---

## O que é

O script `bash scripts/run_demo.sh` (alias `demo_full_stack.sh`) executa o **pipeline end-to-end**:

1. Sobe a stack Docker completa
2. Gera `data/transactions.json` (500 transações)
3. Roda `batch_dataprep_mongo.py` → perfis em MongoDB
4. Roda `spark_local_pipeline.py` → lake Bronze/Silver/Gold
5. Valida `profile-stats` na API

---

## Demo prática (5 min)

### 1. Executar

```bash
cd datamaster
bash scripts/run_demo.sh
```

Aguarde até ver `=== Stack pronta (fluxo completo) ===`.

### 2. Validar cada etapa

```bash
# API viva
curl -s http://localhost:8080/health | python3 -m json.tool

# Perfis Mongo (via API)
curl -s http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool

# Lake Medallion
ls -la data/lake/bronze data/lake/silver data/lake/gold
cat data/lake/reports/dq_latest.json 2>/dev/null | head -20

# Status geral
bash scripts/status-stack.sh
```

### 3. Mostrar no navegador

1. Portal :8880 — links de tudo
2. Dashboard :8501 — KPI “Perfis MongoDB” > 0
3. Spark UI :18080 — job do pipeline (se ainda visível)

---

## O que dizer (1 min)

> *"Este comando sobe a plataforma inteira e materializa o desenho batch + online: histórico vira perfil no Mongo para o scoring em tempo real, e o mesmo JSON passa pelo Spark nas camadas Bronze, Silver e Gold do lake. É o Lambda architecture na prática — batch layer alimentando a speed layer."*

---

## Alternativa via UI

- Portal :8880 → **Executar fluxo completo**
- Console :3333 → mesma ação (usa Docker socket)

---

## Se algo falhar

| Sintoma | Ação |
|---------|------|
| API não sobe | Aguardar ~60s no 1º build; `docker logs fraud-api --tail 40` |
| Mongo vazio | `docker compose --profile batch run --rm batch-prep` |
| Lake vazio | `docker compose --profile spark-run run --rm spark-job` |
| Spark UI down | `docker compose up -d spark-master spark-worker` |

---

## Checklist

- [ ] `run_demo.sh` terminou sem erro
- [ ] `profileCount` > 0
- [ ] 3 camadas em `data/lake/`
- [ ] `status-stack.sh` com OK nos principais serviços
