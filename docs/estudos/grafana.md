# Grafana — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | **Visualização** de métricas — dashboards SRE |
| **Container** | `grafana` |
| **Porta** | **3000** |
| **Login** | `admin` / `admin` |
| **Dashboard** | **DataMaster — API Fraude** (pasta DataMaster) |
| **Datasource** | Prometheus (provisionado automaticamente) |
| **Equivalente Azure** | Dashboards no Monitor / Grafana Cloud |

Frase curta:

> *"Camada de visualização — Prometheus coleta, Grafana exibe."*

---

## Onde entra na arquitetura

```text
[Prometheus] ──query──► [Grafana :3000] ──► analista SRE / ops
```

Provisioning em `config/grafana/` — sobe pronto após `docker compose up`.

---

## Demo prática (4 min)

### 1. Login

http://localhost:3000  
`admin` / `admin` (pode pedir troca de senha — pode pular na demo)

### 2. Abrir dashboard

**Dashboards** → browse → pasta **DataMaster** → **DataMaster — API Fraude**

### 3. Gerar tráfego para animar gráficos

```bash
# Loop de analyze
for i in $(seq 1 20); do
  curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
    -H "Content-Type: application/json" \
    -d "{\"amount\":$((100 + i * 50)),\"merchant_category\":\"Alimentação\",\"user_id\":\"user_1001\",\"hour\":12}" >/dev/null
  sleep 0.5
done
```

Ou use **Iniciar loop** no console :3333.

### 4. Mostrar painéis

- Requisições HTTP / latência
- Métricas JVM (heap, threads)
- Refresh automático (canto superior direito — 5s ou 10s)

### 5. Validar datasource

**Connections → Data sources → Prometheus** → **Save & test** → success.

---

## Arquivos de provisioning

| Arquivo | Função |
|---------|--------|
| `config/grafana/provisioning/datasources/prometheus.yml` | Datasource |
| `config/grafana/dashboards/datamaster-api.json` | Dashboard API |

Após editar:

```bash
docker compose up -d grafana
```

---

## Roteiro de fala (30 s)

> *"Grafana fecha o pilar observabilidade: métricas da API em tempo quase real. Já vem provisionado — não monto na hora. Em produção seria o mesmo padrão com Monitor ou Grafana Cloud."*

---

## Por que Grafana (separado do Prometheus)

| Motivo | Detalhe |
|--------|---------|
| Problema | Operação precisa de painel, não de PromQL cru na hora da crise |
| Escolha | Grafana consome Prometheus — coleta ≠ visualização |
| Trade-off | Embutir UI no Prometheus limita dashboards e alertas ricos |

## Checklist

- [ ] Login :3000 OK
- [ ] Dashboard **DataMaster — API Fraude** aberto
- [ ] Gráficos reagiram ao tráfego
- [ ] Prometheus datasource healthy
- [ ] Mencionei par com Prometheus :9090

---

## Referências

- `config/grafana/`
- `docs/operacao/QUICK_START.md` — seção 12
- `docs/operacao/CHECKLIST_DEMO_BANCA.md` — T11
- [prometheus.md](prometheus.md)
