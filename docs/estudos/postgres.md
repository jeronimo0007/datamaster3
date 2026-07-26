# PostgreSQL — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Banco **OLTP relacional** — schema demo de transações, alertas, auditoria |
| **Container** | `postgres` |
| **Porta** | **5432** |
| **Database** | `fraud_detection` |
| **Credenciais** | `admin` / `admin123` |
| **Equivalente Azure** | PostgreSQL Flexible Server |

Frase curta:

> *"Desenho OLTP de referência — transações, alertas e auditoria LGPD."*

---

## Onde entra na arquitetura

```text
[API local demo] ──► memória + Mongo (scoring ativo)
[PostgreSQL]     ──► schema + seed (mostrar persistência relacional)
```

**Seja honesto:** no perfil `local`, a API **não grava** no Postgres. Os dados servem para **mostrar o modelo relacional** na banca.

---

## Tabelas principais

| Tabela | Conteúdo |
|--------|----------|
| `transactions` | Transações OLTP |
| `fraud_alerts` | Alertas com severity/status |
| `audit_events` | Trilha de auditoria (governança) |

Schema: `sql/schema.sql` · Seed: `sql/seed_demo.sql` (na 1ª subida do volume).

---

## Demo prática (3 min)

### 1. Listar tabelas

```bash
docker exec -it postgres psql -U admin -d fraud_detection -c '\dt'
```

### 2. Ver transações seed

```bash
docker exec -it postgres psql -U admin -d fraud_detection -c \
  "SELECT transaction_id, user_id, amount, fraud_score, is_fraud FROM transactions LIMIT 5;"
```

### 3. Ver alertas

```bash
docker exec -it postgres psql -U admin -d fraud_detection -c \
  "SELECT transaction_id, severity, status FROM fraud_alerts LIMIT 5;"
```

### 4. Se volume antigo sem tabelas

```bash
bash scripts/seed_postgres.sh
```

---

## Roteiro de fala (30 s)

> *"Postgres representa o OLTP transacional — onde ficariam transações persistidas, alertas e eventos de auditoria. Na demo ao vivo o scoring usa Mongo para perfil e memória para transações recentes; Postgres mostra que a plataforma contempla o modelo relacional completo."*

---

## Por que PostgreSQL se o scoring usa Mongo

| Motivo | Detalhe |
|--------|---------|
| Problema | Mostrar fronteira OLTP (transação, alerta, auditoria LGPD) |
| Escolha | Postgres como **referência relacional** na mesa |
| Honestidade | Perfil `local` da API **não grava** scoring no Postgres |
| Cloud | Flexible Server / RDS Aurora |

Pergunta: *"API usa Postgres?"* → *"Não no scoring da demo — Mongo. Postgres prova o modelo OLTP."*

## Checklist

- [ ] `\dt` mostra 3 tabelas
- [ ] SELECT em `transactions` e `fraud_alerts`
- [ ] Expliquei diferença vs Mongo (perfil) e vs API em memória

---

## Referências

- `sql/schema.sql`, `sql/seed_demo.sql`
- `scripts/seed_postgres.sh`
- `docs/operacao/QUICK_START.md` — seção PostgreSQL
