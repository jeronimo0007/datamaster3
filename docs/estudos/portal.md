# Portal — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Hub de navegação — links, credenciais e atalhos da demo |
| **Container** | `fraud-portal` |
| **Imagem** | nginx servindo `portal/` |
| **URL** | http://localhost:8880 |
| **Equivalente** | Portal interno / landing de ops (narrativa) |

Frase curta:

> *"Mapa da demo — um clique para cada serviço e credenciais."*

---

## Onde entra na arquitetura

```text
[Portal :8880] ──links──► API, Dashboard, Console, Grafana, MinIO, Jupyter…
```

Não processa dados — é **índice visual** para a banca.

---

## Demo prática (2 min)

### 1. Abrir

http://localhost:8880

### 2. Mostrar

- Tabela de serviços com portas e credenciais
- Links para Swagger, dashboard, console
- Botão **Executar fluxo completo** (dispara `run_demo.sh` via console interno ou link)
- Slides: `banca.html`, `roteiro.html` (se servidos pelo portal)

### 3. Prova rápida

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8880/
# 200
```

---

## Roteiro de fala (20 s)

> *"Começo pelo portal porque concentra tudo que sobe no Docker — mesma lógica do Kubernetes no VPS e da Azure no Terraform. Daqui abro cada componente na ordem do tour."*

---

## Checklist

- [ ] Portal abre :8880
- [ ] Mostrei tabela de serviços/credenciais
- [ ] Cliquei em pelo menos 2 links (Swagger, Dashboard)

---

## Referências

- `portal/index.html`, `portal/banca.html`, `portal/roteiro.html`
- `docker-compose.yaml` — serviço `portal`
