# Prometheus — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Coleta **métricas** (pull) da API e do próprio Prometheus |
| **Container** | `prometheus` |
| **Porta** | **9090** |
| **Config** | `config/prometheus.yml` |
| **Equivalente Azure** | Azure Monitor / métricas |

Frase curta:

> *"Pilar métricas — latência, throughput, JVM da API."*

---

## Onde entra na arquitetura

```text
[API :8080] ── /actuator/prometheus ──► [Prometheus :9090] ──► [Grafana :3000]
```

Job configurado: `fraud-api` → target `api:8080`.

---

## Demo prática (3 min)

### 1. Abrir UI

http://localhost:9090

### 2. Verificar targets

**Status → Targets** → job `fraud-api` deve estar **UP**.

Se DOWN: API ainda subindo ou rede Docker — aguarde e refresh.

### 3. Gerar tráfego

```bash
for i in $(seq 1 10); do
  curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
    -H "Content-Type: application/json" \
    -d '{"amount":500,"merchant_category":"Alimentação","user_id":"user_1001","hour":12}' >/dev/null
done
```

### 4. Query de exemplo

Na aba **Graph**, teste:

```promql
up{job="fraud-api"}
```

Ou métricas HTTP Spring (se expostas):

```promql
http_server_requests_seconds_count
```

Execute → **Graph** ou **Table**.

---

## Roteiro de fala (20 s)

> *"Prometheus faz scrape periódico da API — modelo pull. Em produção alimenta alertas SRE e dashboards Grafana; na Azure seria Monitor ou Prometheus gerenciado."*

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Target DOWN | `curl localhost:8080/actuator/prometheus` · reiniciar api |
| Mount error | `config/prometheus.yml` virou pasta — ver QUICK_START |

---

## Por que Prometheus (+ Grafana)

| Motivo | Detalhe |
|--------|---------|
| Problema | Medir latência/disponibilidade sem depender só de log |
| Escolha | Pull Prometheus + Actuator; Grafana só visualiza |
| Trade-off | Só logs = debug ok, SLO ruim; APM SaaS = rico e caro |
| Cloud | Monitor / CloudWatch (mesmo desenho de métricas) |

## Checklist

- [ ] :9090 abre
- [ ] Target `fraud-api` UP
- [ ] Executei queries após tráfego
- [ ] Mencionei ligação com Grafana

---

## Referências

- `config/prometheus.yml`
- `docs/operacao/QUICK_START.md` — Grafana/Prometheus
