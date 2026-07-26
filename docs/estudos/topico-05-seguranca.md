# Tópico 5 — Segurança (slide 9)

## 1. O que é
**Defesa em profundidade:** proteger dado em trânsito, em repouso, em segredo e por identidade/autorização.

## 2. Problema que resolve
Plataforma de fraude trata PII e decisões sensíveis. Credencial no código, bucket aberto ou API sem controle = incidente e LGPD.

## 3. Componentes (honestidade)
| Camada | Produção (desenho) | O que a mesa prova |
|--------|--------------------|--------------------|
| Transporte | TLS / Front Door | HTTP local (demo) |
| Repouso | CMK Key Vault / KMS | Volumes Docker / object storage |
| Secrets | Key Vault / Secrets Manager | `.env` (não commitado) |
| Identidade | Entra ID / IAM | Sem IdP na demo |
| Autorização | RBAC / Lake Formation | Papéis no desenho Terraform |
| Aplicação | API + DataMasker | **Sim — código e endpoint** |

## 4. Por que cada um
- **Secrets fora do código:** rotação, auditoria, menor blast radius.  
- **RBAC:** least privilege — Spark job ≠ analista BI ≠ operador de alerta.  
- **Criptografia:** obrigação regulatória e defesa se o storage vazar.  
- **Mascaramento na app:** última milha (detalho no tópico LGPD).

## 5. Onde entra
Transversal: ADF/Glue puxa secret; lake com ACL; API com identidade; exportações mascaradas.

## 6. Local — o que dizer sem overclaim
> “Na mesa demonstro a camada de aplicação: API e DataMasker. Key Vault, Entra e TLS terminado são o desenho de produção no Terraform e no mapa multicloud — não vou fingir que o compose é um banco certificado.”

## 7. Azure / AWS
| Função | Azure | AWS |
|--------|-------|-----|
| Secrets + chaves | Key Vault | Secrets Manager / SSM + KMS |
| Identidade | Entra ID | IAM + Identity Center |
| Auditoria | Azure Activity / Diagnostic | CloudTrail |
| Borda API | APIM | API Gateway |

## 8. Alternativa e trade-off
| Alternativa | Trade-off |
|-------------|-----------|
| Secrets no compose.yaml | Fácil no lab; inaceitável em produção |
| Só network isolation | Ajuda; não substitui identidade e crypto |
| mTLS em todos os hops | Forte; complexidade operacional alta |

## 8b. Defesa 360° — perguntas técnicas duras

> **Postura:** a superfície da demo é *conscientemente aberta* — laboratório em rede Docker isolada. Nunca dizer “é seguro”; dizer **“na mesa X, em produção Y, porque Z”**.

### TLS no Kafka?
Mesa = listener `PLAINTEXT` em `kafka:29092`, rede interna, sem exposição pública.

| Ambiente | Trânsito | AuthN | AuthZ |
|----------|----------|-------|-------|
| Mesa | PLAINTEXT | — | — |
| Kafka self-managed | SASL_SSL / mTLS | SCRAM ou cert | ACL por tópico |
| Event Hubs | TLS 1.2 obrigatório | Entra ID / SAS | RBAC Sender/Receiver |
| MSK | TLS in-transit + KMS | IAM auth / mTLS | Policy por tópico |

Ponto LGPD junto: o evento leva **CPF + só final do cartão**; em produção CPF **tokenizado**, retenção curta no tópico, histórico no lake governado.

### OAuth2 / JWT — quem chama a API?
- Mesa: perfil `local` com Spring Security em `permitAll` (deliberado, para a banca usar `curl`).
- No código já existe o hook: perfil `enterprise` com `oauth2ResourceServer(jwt)` — **esqueleto**, não IdP configurado (não inventar issuer).
- Produção: API é *resource server*; valida JWT RS256 contra o JWKS (Entra ID / Cognito): `iss`, `aud`, `exp`, assinatura, **scope**.

| Quem chama | Fluxo | Por quê |
|------------|-------|---------|
| Sistema → API | Client Credentials | M2M, identidade da aplicação |
| Front SPA / analista | Authorization Code + PKCE | Nunca segredo no browser |
| Parceiro externo | mTLS + client credentials | Dupla prova de identidade |

Scopes: `fraud.score:write` · `fraud.read` · `fraud.admin` · **`pii.read` separado e auditado**.

**Por que JWT e não API key?** Key é segredo estático: sem expiração, sem escopo, sem identidade. JWT expira, carrega claims, é revogável no IdP e dá auditoria de *quem* chamou.

### Como o front acessa a API?
- Mesa: portal `:8880` faz `fetch` do browser direto em `:8080` com `@CrossOrigin("*")`; Streamlit `:8501` chama **server-side** (`API_URL=http://api:8080`).
- Risco que eu mesmo aponto: CORS `*` sem token = qualquer origem chama. Lab sim, produção não.
- Produção: *Front → Front Door/WAF → API Gateway (valida JWT) → API core em rede privada*. CORS restrito à origem, token no header, **PII nunca em query string** (vai para log de acesso).

### O que um API Gateway implementa?
Ponto único de política — tira do código a preocupação transversal:

| Função | Por que na borda |
|--------|------------------|
| Terminação TLS + cert manager | Certificado num lugar, rotação automática |
| Validação JWT / OAuth2 | Token inválido morre antes de gastar a API |
| Rate limit e quota por cliente | Protege o motor de score de abuso |
| WAF + IP allowlist | OWASP Top 10 antes da aplicação |
| mTLS gateway → backend | API core só aceita o gateway |
| Log scrubbing | PII fora do log de acesso |
| Versionamento / canary | v1→v2 sem quebrar o core |

Equivalência: **APIM / Front Door** · **API Gateway + WAF**. Na mesa não existe — roadmap no diagrama online-gateway. Se cobrarem: *“gateway sem IdP é caixa vazia; preferi provar o motor e desenhar a borda a encenar segurança.”*

### Acesso a Bronze / Silver / Gold
Mesa: MinIO com credencial única (`minioadmin`), buckets criados no `minio-init`, **sem policy por camada** — assumo.

| Camada | Escreve | Lê | Controle |
|--------|---------|----|----------|
| Bronze | Só job de ingestão | Engenharia + auditoria | Imutável (versioning/WORM) · PII tokenizada · retenção |
| Silver | Job de transformação | Engenharia + DS | Sem PII em claro · schema enforced |
| Gold | Job de agregação | BI / Negócio | **Sem PII** — agregado |

Implementação: managed identity / IAM role **por job** → RBAC por container/prefixo → ACL POSIX (ADLS) ou bucket policy (S3) → **Lake Formation / Unity Catalog** para grão fino (coluna e linha) → **CMK** no Key Vault/KMS → **private endpoint**.

> *Frase de ouro:* “O Medallion não é só qualidade de dado — é **fronteira de segurança**. Quem lê a Gold não deveria conseguir ler a Bronze. Negócio não precisa de CPF; precisa de fraude por categoria.”

### Tem senha no repositório?
Sim, **credenciais de laboratório** (`admin123`, `minioadmin`, `datamaster`) — fixas de propósito e documentadas no portal para a stack ser reproduzível. **Segredo real não é versionado**: `.gitignore` bloqueia `.env`, `secrets/`, `*.pem`, `*.key`, `tfstate`. Tudo já é lido via `${VAR:-default}`, então o caminho para o cofre está aberto: troco o default pela referência ao Key Vault **sem mudar código**.

## 9. Como demonstrar
- Mostrar `docs/.env.example` e o `.gitignore` — segredo real não versionado  
- Avançar para slide LGPD e mascarar PII (prova prática)  
- Citar Terraform `apresentacao` (Key Vault) se a banca pedir infra

## 10. Fala
> “Segurança em camadas: criptografia, cofre de segredos, identidade e RBAC. Credencial não fica no código. Na demo mostro o controle na aplicação; o cofre e o IdP são o caminho de produção.”

## 11. Perguntas
| Pergunta | Resposta |
|----------|----------|
| Onde está o Key Vault na demo? | Desenho Azure/Terraform; local usa env vars |
| Como evita vazamento no dashboard? | Mascaramento LGPD + não expor PII desnecessário |
| RBAC no Mongo local? | Demo aberta; produção: identidade gerenciada + roles |
| TLS no Kafka? | Mesa PLAINTEXT em rede interna; prod SASL_SSL + ACL por tópico |
| Autentica a API como? | Resource server JWT (Entra/Cognito); mesa `permitAll` deliberado |
| API key resolveria? | Não: sem expiração, escopo nem identidade |
| Front chama a API direto? | Mesa sim (CORS `*`); prod via gateway com token |
| Gateway faz o quê? | TLS, JWT, rate limit, WAF, mTLS backend, scrubbing, versionamento |
| Quem lê a Bronze? | Só ingestão/auditoria; RBAC por camada, Gold sem PII |
| Como audita acesso a dado? | Activity Log/Diagnostic (Azure) · CloudTrail (AWS) |

## 12. Transição
> “Segurança técnica protege o ativo; a **LGPD** exige minimização e tratamento adequado de dado pessoal — próximo slide.”

**Próximo:** [topico-06-lgpd.md](topico-06-lgpd.md)
