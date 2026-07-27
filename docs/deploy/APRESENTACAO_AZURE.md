# Roteiro Azure — apresentação / banca

## Objetivo

Um único **Run workflow** na branch `azure` sobe (ou atualiza) a stack completa e publica a API Java, com URLs no resumo do job.

## Pré-requisitos (uma vez)

Repository secrets:

| Secret | Uso |
|--------|-----|
| `AZURE_CLIENT_ID` | App registration (OIDC) |
| `AZURE_TENANT_ID` | Tenant |
| `AZURE_SUBSCRIPTION_ID` | Subscription paga |
| `TF_VAR_db_admin_password` | Senha Postgres |

App registration com **Contributor** ou **Owner** na subscription + credencial federada na branch **`azure`**.

## Na hora da apresentação

1. GitHub → **Actions** → **Deploy → Azure**
2. **Run workflow**
   - branch: `azure`
   - action: **apply**
   - enable_analytics_stack: **true** (stack completa)
   - name_suffix: **banca** (padrão)
3. Espere o job (pode levar **30–60+ min** na primeira vez)
4. Abra o **Summary** do job — ali estão API, health e links

Teste rápido:

```bash
curl https://<fqdn-do-summary>/health
```

## Apagar e subir de novo (demo “do zero”)

1. Actions → Deploy → Azure → Run workflow → action: **destroy**
2. Espere terminar (Cosmos/Synapse podem demorar)
3. Confira limpeza:

```bash
az group list --query "[?contains(name,'rg-fraud-apresentacao')].name" -o tsv
```

4. Run workflow de novo com action: **apply**

Se der conflito de nome global após delete recente, use `name_suffix=banca2`.

## O que o workflow faz

1. Login OIDC + registro de providers (só se faltar)
2. Bootstrap do **state remoto** (`rg-datamaster3-tfstate` / `datamaster3tfstate`)
3. `terraform apply` (nomes estáveis com suffix `banca`)
4. Build/push da API Java no ACR
5. Update do Container App + wait em `/health`
6. Resumo com URLs no GitHub Actions

## Não usar na banca

- Rodar apply com o RG antigo ainda existindo **e** sem state → cria duplicata. Com o state remoto isso não acontece.
- Confiar só no `/actuator/health` — use **`/health`**.

Local e k3s **não** mudam com este fluxo.
