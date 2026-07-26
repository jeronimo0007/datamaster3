# Console de dados (Node) — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Simula o core banking — gera JSON, dispara batch, loop de carga |
| **Container** | `fraud-data-console` |
| **Stack** | Node.js — `data-generator-console/` |
| **Porta** | **3333** |
| **Acesso Docker** | Monta `docker.sock` para rodar jobs Spark/batch |

Frase curta:

> *"Simulador do canal — gera transações e alimenta a API como se viesse do core."*

---

## Onde entra na arquitetura

```text
[Console :3333]
    ├── generate_data.py  → data/transactions.json
    ├── batch_dataprep    → MongoDB
    ├── spark-job         → data/lake/
    ├── POST /batch       → API :8080
    └── demo_loop         → analyze contínuo
```

**Importante:** na demo, o console chama a **API direto** (HTTP) — não passa pelo Kafka.

---

## Funcionalidades na UI

| Ação | O que faz |
|------|-----------|
| **Gerar JSON** | Cria `data/transactions.json` com N linhas |
| **Executar fluxo completo** | batch-prep + spark + validação |
| **Enviar lote** | `POST /api/v1/transactions/batch` |
| **Iniciar loop** | Transações contínuas para demo ao vivo |
| **Batch prep** | Roda `batch_dataprep_mongo.py` |

---

## Demo prática (5 min)

### 1. Abrir

http://localhost:3333

### 2. Gerar dados (1 min)

- Quantidade: **500**
- Taxa fraude: **8%**
- Clique **Gerar JSON**
- Mostre log de sucesso

### 3. Fluxo completo (2 min)

Clique **Executar fluxo completo** (ou rode `bash scripts/run_demo.sh` no terminal).

Acompanhe logs na UI — batch Mongo + Spark.

### 4. Enviar lote à API (1 min)

- **Enviar lote** com slice 20
- Abra dashboard :8501 — transações aparecem

### 5. Loop ao vivo (1 min, opcional)

**Iniciar loop** — dashboard atualiza com auto-refresh.

Terminal alternativo:

```bash
docker compose logs -f data-console
```

---

## Prova via API

```bash
curl -s http://localhost:3333/api/health 2>/dev/null || curl -s http://localhost:3333/ | head -5
```

---

## Roteiro de fala (30 s)

> *"Este console substitui o core banking na mesa. Gera histórico para batch, dispara o pipeline Spark e manda transações em tempo real para a API — o mesmo caminho que em produção viria de filas ou APIs internas."*

---

## Por que o console (simulador)

| Motivo | Detalhe |
|--------|---------|
| Problema | Não há core banking na sala da banca |
| Escolha | Console Node gera JSON, dispara batch/Spark e chama a API |
| Honestidade | Chama API **direto** (HTTP) — não passa pelo Kafka |
| Trade-off | Simulador controlado vs conector real (ADF/Glue em produção) |

## Checklist

- [ ] Console :3333 abre
- [ ] Gerei JSON
- [ ] Executei fluxo completo ou enviei lote
- [ ] Dashboard refletiu novas transações
- [ ] Expliquei: HTTP direto à API, Kafka é narrativa separada

---

## Referências

- `data-generator-console/server.js`
- `data-generator-console/public/index.html`
- `docker-compose.yaml` — `data-console` (volume docker.sock)
