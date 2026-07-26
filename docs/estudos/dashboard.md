# Dashboard Streamlit — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Operação — fraudes, liberação, LGPD, gráficos, assistente IA |
| **Container** | `fraud-dashboard` |
| **Stack** | Python Streamlit — `src/dashboard/app.py` |
| **Porta** | **8501** |
| **Equivalente** | Power BI / Fabric (narrativa) |

Frase curta:

> *"Painel operacional — o analista vê fraudes, libera casos e aplica LGPD."*

---

## Onde entra na arquitetura

```text
[Dashboard :8501] ──HTTP──► API :8080 ──► Mongo / memória
        │
        └── DeepSeek (opcional, DEEPSEEK_API_KEY)
```

Toda ação passa pela API — o dashboard **não** acessa banco direto.

---

## Seções da UI

| Seção | Função |
|-------|--------|
| **Transações** | Fraudes abertas, gráficos, liberar caso, pesos do modelo |
| **Batch / perfil** | Status perfis Mongo, stats batch |
| **LGPD / mascaramento** | Máscara CPF, e-mail, telefone, cartão |
| **Assistente IA** | Chat contextual sobre fraudes (DeepSeek) |
| **Gráficos** | Evolução temporal, distribuições |

Sidebar: enviar transação de teste, auto-refresh, contagem perfis Mongo.

---

## Demo prática (8 min)

### Pré-requisito

```bash
bash scripts/run_demo.sh
# Gerar ao menos 1 fraude via API ou console antes
```

### 1. Abrir e KPIs (1 min)

http://localhost:8501

Mostre a barra de KPIs: transações, fraudes abertas, perfis MongoDB, taxa fraude.

### 2. Aba Transações (3 min)

1. Gráfico de fraudes por categoria
2. Selecione uma fraude na tabela
3. **Liberar transação** (falso positivo) — chama `POST .../release`
4. Mostre pesos de feature-importance (referência do modelo)

### 3. Aba Batch / perfil (1 min)

Confirme perfis MongoDB carregados e stats do batch.

### 4. Aba LGPD (2 min)

1. Preencha CPF, e-mail, telefone fictícios
2. **Aplicar mascaramento**
3. Mostre campos mascarados na resposta

### 5. Aba Assistente IA (1 min, opcional)

Requer `DEEPSEEK_API_KEY` no `.env`. Pergunte: *"Por que esta transação foi marcada como fraude?"*

### 6. Sidebar — transação teste (1 min)

Formulário lateral → enviar amount alto → ver score na sidebar.

---

## Roteiro de fala (30 s)

> *"O dashboard é a camada de consumo para o time de operações. Ele consome o mesmo contrato REST da API — em produção seria Power BI ou um portal interno. Aqui mostro o ciclo completo: detectar, revisar, liberar falso positivo e mascarar PII."*

---

## Checklist

- [ ] Dashboard :8501 abre com KPIs
- [ ] Mostrei fraudes na aba Transações
- [ ] Liberei um caso (ou simulei)
- [ ] LGPD mascaramento aplicado
- [ ] Mencionei dependência da API (sidebar URL)

---

## Referências

- `src/dashboard/app.py`
- `docs/operacao/CHECKLIST_DEMO_BANCA.md` — T4, T4b
