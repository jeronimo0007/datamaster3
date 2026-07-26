# Plano de estudo — 8 tópicos do edital (nota 10)

## Princípio: o porquê > o quê

Na apresentação, **o mais importante não é o que você usou — é por que usou**.

- Listar Kafka, Spark, Mongo = decorar.  
- Explicar o **problema**, a **escolha** e o **trade-off** = nota de engenharia de dados.

Use **um tópico por sessão**. Não avance até responder, em voz alta e sem olhar o texto:

> **“Por que você escolheu esse componente e qual problema ele resolve aqui?”**

Se a resposta começar com “é um…” e não com “escolhi porque…”, ainda não está pronto.

---

## Ordem mental ao estudar (e ao falar)

| Ordem | Ponto | Peso |
|------:|-------|------|
| 1 | **Problema** que resolve | crítico |
| 2 | **Por que** cada componente | crítico |
| 3 | **Alternativa** e trade-off | crítico |
| 4 | Onde entra no DataMaster | alto |
| 5 | Local vs Azure/AWS (mesmo porquê) | alto |
| 6 | O que é (definição curta) | apoio |
| 7 | Como demonstrar + o que falar | apoio |
| 8 | Perguntas da banca | apoio |
| 9 | Transição | apoio |

Os 12 pontos completos estão em cada `topico-0N-*.md` — mas **estude 1→2→3 primeiro**.

Roteiro de fala: [apresentacao-90min.md](apresentacao-90min.md) · Slides: `portal/banca.html`

---

## Mapa rápido: tópico → slide → demo

| # | Tópico | Slide | Demo | Guia |
|---|--------|-------|------|------|
| 1 | Extração | 5 | Console :3333 · `generate_data.py` · adapters | [topico-01-extracao.md](topico-01-extracao.md) |
| 2 | Ingestão | 6 + 6b | Kafka T8 · caminho online T4–T7 · Rabbit T4c | [topico-02-ingestao.md](topico-02-ingestao.md) |
| 3 | Armazenamento | 7 + 7c + 7b | Lake T9 · Mongo T3 · Postgres | [topico-03-armazenamento.md](topico-03-armazenamento.md) |
| 4 | Observabilidade | 8 | Prometheus + Grafana T11 | [topico-04-observabilidade.md](topico-04-observabilidade.md) |
| 5 | Segurança | 9 | Narrativa + o que a mesa prova | [topico-05-seguranca.md](topico-05-seguranca.md) |
| 6 | LGPD | 10 | Dashboard LGPD T4b · curl mask | [topico-06-lgpd.md](topico-06-lgpd.md) |
| 7 | Arquitetura de dados | 11 | DQ report · Medallion · Kimball | [topico-07-arquitetura.md](topico-07-arquitetura.md) |
| 8 | Escalabilidade | 12 | Batch API T7 · mapa de escala | [topico-08-escalabilidade.md](topico-08-escalabilidade.md) |

---

## Frases de ouro (sempre começam pelo porquê)

1. **Extração:** *“Escolhi adapters porque o modelo não pode depender do schema do core.”*  
2. **Ingestão:** *“Stream porque preciso de latência e do fato assíncrono; batch porque preciso de histórico e perfis.”*  
3. **Online:** *“Score é HTTP síncrono; Kafka publica depois, assíncrono; Rabbit é só o e-mail.”*  
4. **Lake:** *“Medallion porque quero reprocessar sem perder a landing.”*  
5. **Mongo:** *“Documento por user_id porque o online precisa de ms, não de scan no lake.”*  
6. **Obs:** *“Prometheus coleta e Grafana mostra — misturar os dois papéis atrapalha operação.”*  
7. **Segurança:** *“Secrets fora do código porque rotação e blast radius importam.”*  
8. **LGPD:** *“Mascaro na borda porque antifraude precisa de sinal, não de PII em claro.”*  
9. **Arquitetura:** *“Medallion para engenharia; Kimball para BI; perfil no Mongo para serving.”*  
10. **Escala:** *“Particiono porque réplica sem chave certa não remove o gargalo.”*

---

## Regra de ouro na banca

- **Afirme só o que roda.** LB, Vault, 10M tx = desenho; diga o **porquê do desenho**, sem fingir prova ao vivo.  
- Template seguro: *“Escolhi X porque Y; na mesa represento com Z; em Azure seria W — o problema resolvido é o mesmo.”*

---

## Ordem de estudo (≈ 8 sessões)

1. Ler só as seções **Problema / Por que / Trade-off** do guia  
2. Falar em voz alta **sem** abrir o slide  
3. Só então abrir `banca.html` + `apresentacao-90min.md`  
4. Fazer a demo (o “quê” comprova o “porquê”)  
5. Avançar

Ensaio: `bash docs/estudos/ensaio-90min.sh`
