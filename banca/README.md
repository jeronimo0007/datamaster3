# Banca — estudo e apresentação (somente local)

Esta pasta **não vai para o Git** (ver `banca/` no `.gitignore`).

Use para roteiros, planos de estudo, rascunhos e colas — separado da documentação técnica em `docs/`.

## Estrutura sugerida

```
banca/
├── apresentacao/     # Roteiro 90 min, guia de comandos, slides HTML (cópia)
├── estudo/           # Planos de estudo, perguntas/respostas, base_estudo
└── README.md         # Este arquivo
```

## Demo ao vivo (versionado no repositório)

Slides e cola servidos pelo Docker continuam em:

- `portal/banca.html` — projetor
- `portal/roteiro.html` — fala
- http://localhost:8880 — após `docker compose up -d portal`

## Documentação técnica (Git)

Avaliação do código e arquitetura: [readme.md](../readme.md) e [docs/README.md](../docs/README.md).
