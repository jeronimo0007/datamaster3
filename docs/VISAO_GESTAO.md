# DataMaster — Visão para gestão

Documento curto para gestor / sponsor. Sem tutorial técnico.

## O que é

Plataforma de **engenharia de dados** para antifraude: camadas Medallion, qualidade antes de promover dados, Airflow orquestrando o lake, **Kafka** e **MongoDB** iguais no local e na nuvem.

## Valor

- Bronze fiel à origem; Silver só sobe com DQ; Gold pronto para consumo.
- **Mesma stack** em Docker, Azure e AWS (preparado) — sem trocar Kafka por outro produto, nem Mongo por outro banco.
- Demo local prova o pipeline; Terraform sobe o mesmo desenho.

## Papéis

- **Arquiteto de solução:** desenho multiplataforma com componentes idênticos.
- **Engenheiro de dados:** ingestão multi-formato, Airflow, transformações por camada.

## Escopo

| É | Não é |
|---|--------|
| Pipeline de dados + orquestração | Comparar “serviços equivalentes” de cada cloud |
| Kafka + Mongo + Spark + Airflow | Postgres / Redis / filas de e-mail no núcleo |
| Azure (demo cloud) + AWS preparado | VPS / k3s |

## Riscos e controles

| Risco | Controle |
|-------|----------|
| Dado sujo no modelo | DQ gate Bronze → Silver |
| Reprocesso caro | Jobs por camada, idempotentes |
| Drift local vs nuvem | Mesmos componentes (Kafka, Mongo) em todos os ambientes |
