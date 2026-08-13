# Domínio: Observabilidade

Métricas, health checks e dashboards.

## Documentos

| Documento | Conteúdo |
|-----------|----------|
| [../operacao/SERVICOS_DOCKER.md](../operacao/SERVICOS_DOCKER.md) | Prometheus + Grafana |
| [../arquitetura/README.md](../arquitetura/README.md) | Diagramas de arquitetura |

## Configuração

| Caminho | Função |
|---------|--------|
| `config/prometheus.yml` | Scrape da API |
| `config/grafana/dashboards/datamaster-api.json` | Dashboard DataMaster |

## URLs locais

| Serviço | URL |
|---------|-----|
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (`admin` / `admin`) |
| Health API | http://localhost:8080/health |

Apresentação: slide observabilidade em `portal/banca.html` · **T11**.

[← Índice geral](../README.md)
