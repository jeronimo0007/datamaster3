# Tópico 6 — LGPD (slide 10)

## 1. O que é
Conformidade com proteção de dados pessoais: **minimização**, finalidade, segurança e transparência no tratamento.

## 2. Problema que resolve
Antifraude precisa de sinal; **não** precisa expor CPF/e-mail/cartão em claro em tela, log ou exportação.

## 3. Componentes usados
| Componente | Papel |
|------------|--------|
| `DataMasker` (`src/utils/data_masker.py`) | Máscaras por campo |
| `POST /api/v1/lgpd/mask` | Contrato demonstrável |
| Dashboard aba LGPD | Antes × depois visual |
| Hash com salt (no código) | Narrativa de anonimização analítica |

## 4. Por que cada um
- **Mascaramento na API:** um lugar só — painel e jobs reutilizam.  
- **Endpoint dedicado:** prova para a banca sem depender de UI.  
- **Campos cobertos:** CPF, e-mail, telefone, nome, cartão — PII típica de canal.

## 5. Três conceitos (decore)
| Técnica | Reversível? | Uso |
|---------|-------------|-----|
| **Mascaramento** | Parcialmente (ainda há formato) | UI, suporte, demos |
| **Anonimização** | Não (idealmente) | Analytics sem vínculo |
| **Criptografia** | Sim (com chave) | Repouso/trânsito — não é “esconder na tela” |


## 5b. Hash ≠ criptografia (armadilha de banca)

| Família | Reversível? | Exemplos | Uso |
|---------|-------------|----------|-----|
| **Criptografia** | **Sim** (com chave) | AES, TLS, RSA | Proteger e *recuperar* depois |
| **Hash** | **Não** (por desenho) | SHA-256, bcrypt | Integridade, senha, anonimização analítica |
| **Hash + salt** | Não (melhor) | sha256(cpf+salt) | Dificulta rainbow table |

SHA-1/SHA-256 **não** são “criptografia irreversível” — são **hash**. Se a banca usar esse termo, corrija com educação: “na engenharia isso se chama função de hash; criptografia implica chave e reversão autorizada.”

## 6. Local
Dashboard :8501 → **LGPD / mascaramento** · ou curl do slide 10.

## 7. Azure / AWS
Políticas de classificação + Purview/Lake Formation; Dynamic Data Masking em SQL; encryption com Key Vault/KMS. O **padrão de app** (máscara na borda) permanece.

## 8. Alternativa e trade-off
| Alternativa | Trade-off |
|-------------|-----------|
| Só crypto no disco | Protege storage; operador ainda vê PII na API |
| Tokenização de cartão | Mais forte (PCI); mais infra |
| Apagar PII do lake | Bom para minimização; dificulta investigação forense |

## 8b. Defesa — perguntas duras

> **Não misture com Segurança:** Segurança = quem acessa / canal / cofre. LGPD = o *dado pessoal* — minimizar, mascarar, finalidade.

| Pergunta | Resposta |
|----------|----------|
| Isso torna anônimo? | **Não** — é mascaramento. Anonimização exige irreversibilidade |
| Só crypto no disco resolve? | Não — operador ainda vê PII na API |
| Base legal antifraude? | Legítimo interesse / obrigação de segurança (narrativa jurídica); engenharia foca minimização e proteção |
| Onde mais aplica? | Logs, exportações, ambientes não produtivos, e-mail de alerta, evento Kafka |
| PII no Kafka? | CPF + só final do cartão; prod = CPF tokenizado, PAN nunca, retenção curta |
| Gold tem CPF? | **Não deve** — Gold agregada; PII na Bronze governada |
| Tokenização de cartão? | Mais forte (PCI); mesa = last4; prod = vault/tokenização |
| Direito ao esquecimento? | Retenção + job de purge no lake/perfil — não basta apagar no Mongo |
| Por que máscara na API e não só no front? | Front mente: DevTools vê JSON bruto; um contrato só na borda |

## 8c. Conceitos LGPD para engenheiro de dados (decore)

| Conceito | Frase de banca | No DataMaster |
|----------|----------------|---------------|
| **Minimização** | Só o necessário para a finalidade | Score sem CPF na tela; Gold sem PII |
| **Finalidade** | Trato para antifraude — não reuso livre | Pipeline ≠ dump genérico |
| **Base legal** | Legítimo interesse / segurança (narrativa) | Engenheiro foca proteção + minimização |
| **PII** | Identifica ou pode identificar | CPF, e-mail, telefone, nome, cartão |
| **Mascaramento** | Esconde na UI; **ainda é dado pessoal** | DataMasker / `/lgpd/mask` |
| **Pseudonimização** | ID no lugar do PII; com chave ainda reidentifica | `user_id`; token no Kafka (prod) |
| **Anonimização** | Irreversível | Hash+salt / agregado Gold |
| **Criptografia** | Canal/storage — **não** substitui máscara | TLS / CMK (desenho) |
| **Retenção** | Quanto tempo o dado vive | Kafka curto · lake com política |
| **Esquecimento** | Apagar/anonimizar sob demanda | Purge lake + perfil (não só Mongo) |
| **Governança por camada** | Quem lê o quê | Bronze restrita · Gold sem PII |

**Kafka × Gold:** Kafka = identificador mínimo (CPF/token + last4), retenção curta, PAN nunca. Gold = **sem PII**, agregado. Bronze = bruto governado.

## 9. Como demonstrar (T4b)
1. Abrir aba LGPD  
2. Aplicar máscara — mostrar tabela  
3. Opcional: curl `/lgpd/mask`

## 10. Fala
> “LGPD na prática: minimizo o que aparece. O DataMasker mascara CPF, e-mail, telefone, nome e cartão. Mascaramento não é anonimização nem criptografia — são controles diferentes, e eu aplico o mascaramento na borda da API e no painel.”

## 11. Perguntas
| Pergunta | Resposta |
|----------|----------|
| Isso torna o dado anônimo? | Não — é mascaramento; anonimização exige irreversibilidade |
| Base legal antifraude? | Legítimo interesse / obrigação de segurança — narrativa jurídica; engenharia foca minimização e proteção |
| Onde mais aplica? | Logs, exportações, ambientes não produtivos, Kafka, e-mail |
| Só crypto resolve LGPD? | Não — crypto ≠ máscara na tela |
| Por que máscara na API? | Um lugar; front sozinho vaza PII no JSON |
| Gold tem CPF? | Não deve — agregada sem PII |

## 12. Transição
> “Com conformidade na borda, fecho o **modelo de dados**: Medallion, Kimball e features.”

**Próximo:** [topico-07-arquitetura.md](topico-07-arquitetura.md)
