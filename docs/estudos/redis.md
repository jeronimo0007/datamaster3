# Redis — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Cache em memória — sessão, rate limit, cache de scores (narrativa) |
| **Container** | `redis` |
| **Porta** | **6379** |
| **Imagem** | `redis:7-alpine` |
| **Equivalente Azure** | Azure Cache for Redis |

Frase curta:

> *"Cache de baixa latência — infra pronta para escala; na demo local a API usa perfil `local` leve."*

---

## Onde entra na arquitetura

```text
[API / serviços] ──► Redis :6379  (cache / sessão — roadmap produção)
```

**Seja honesto:** no perfil demo atual, a API **não depende** do Redis para o fluxo principal. O serviço sobe no Compose como **infra de plataforma completa**.

---

## Demo prática (2 min)

### 1. PING

```bash
docker exec redis redis-cli PING
```

Esperado: `PONG`.

### 2. Comandos básicos (opcional)

```bash
docker exec -it redis redis-cli
```

No shell Redis:

```
SET datamaster:demo "ok"
GET datamaster:demo
KEYS *
exit
```

### 3. Status script

```bash
bash scripts/status-stack.sh
# linha: OK  Redis PING
```

---

## Roteiro de fala (20 s)

> *"Redis está na stack como cache transversal — scores recentes, sessões, rate limiting. Na mesa a demo prioriza API + Mongo; Redis mostra o desenho completo de produção."*

---

## Por que Redis na stack

| Motivo | Detalhe |
|--------|---------|
| Problema | Hot keys / cache para reduzir carga no serving sob pico |
| Escolha | Redis (Azure Cache / ElastiCache na nuvem) |
| Honestidade | Path crítico da demo de scoring = API + Mongo; Redis é alavanca de escala |
| Trade-off | Cache sem invalidação → perfil stale |

## Checklist

- [ ] `redis-cli PING` → PONG
- [ ] Expliquei papel vs uso real na demo local

---

## Referências

- `docker-compose.yaml` — serviço `redis`
- `docs/operacao/SERVICOS_DOCKER.md`
