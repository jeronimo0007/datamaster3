# Zookeeper — guia de estudo e demo

---

## O que é, neste projeto

| Aspecto | Detalhe |
|---------|---------|
| **Papel** | Coordenação do **Kafka** (modo Zookeeper) |
| **Container** | `zookeeper` |
| **Porta** | **2181** (interna, rede Docker) |
| **Imagem** | `confluentinc/cp-zookeeper:7.5.0` |
| **UI pública** | Nenhuma — infraestrutura interna |

Frase curta:

> *"Suporte ao broker Kafka — em produção seria serviço gerenciado (MSK/Event Hubs)."*

---

## Onde entra na arquitetura

```text
[zookeeper :2181] ◄── coordena ──► [kafka :9092]
```

Não participa do fluxo HTTP da demo. Só **habilita o Kafka** a subir.

---

## Demo prática (1 min)

### 1. Verificar que está Up

```bash
docker compose ps zookeeper kafka
```

Ambos `Up`.

### 2. Provar Kafka funcional (indireto)

```bash
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

Se Kafka responde, Zookeeper cumpriu o papel.

### 3. O que dizer (não abrir UI — não existe)

> *"Zookeeper é infra de suporte — não demonstro tela. Em Azure Event Hubs ou MSK gerenciado isso desaparece para o time de dados."*

---

## Checklist

- [ ] `docker compose ps` — zookeeper Up
- [ ] Kafka list topics OK
- [ ] Expliquei que é suporte interno, não produto

---

## Referências

- `docker-compose.yaml` — `zookeeper`, `kafka`
- [kafka.md](kafka.md)
