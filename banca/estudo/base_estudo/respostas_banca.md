## Batch → MongoDB → API (tratamento de dados na banca)

**Pergunta provável:** “Como você mostra engenharia de dados além do scoring online?”

**Resposta curta:**  
Histórico em JSON (Bronze) → dataprep agregado por `user_id` → MongoDB `user_profiles` → na análise em tempo real a API consulta o documento e soma `anomaly_reasons` ao score. O painel filtra fraudes, libera falsos positivos e o assistente DeepSeek explica o contexto.

**Comandos demo:**
```bash
docker compose up -d --build
docker compose --profile batch run --rm batch-prep
# ou pelo portal :8880 → Executar batch dataprep
curl -s http://localhost:8080/api/v1/batch/profile-stats
```

**Par Azure:** Data Factory + Databricks (agregação) → Cosmos DB (perfil) → Container Apps API.

---

## 1. Escalabilidade
- **Horizontal**: Auto-scaling configurado em todos os serviços
- **Partitioning**: Dados particionados por data/user_id
- **Throughput**: Event Hubs escala para 1MB/s por TU
- **Processamento**: Databricks cluster auto-scaling
- **Perfis batch**: Cosmos/Mongo com partition key `user_id`

## 2. Custos
- **Dev**: ~R$ 500/mês
- **Prod (10M/dia)**: ~R$ 3.000/mês
- **Enterprise**: ~R$ 15.000/mês
- **Otimização**: Reservas, spot instances, auto-pause

## 3. Latência
- **Streaming**: < 2 segundos (95th percentile)
- **Batch**: Processamento horário/diário (perfis); consulta Mongo na API < 50 ms
- **ML Inference**: < 100ms por transação
- **API Response**: < 50ms

## 4. ML Pipeline
- **Retreinamento**: Automático semanal
- **A/B Testing**: Canary deployment
- **Model Registry**: MLflow para versionamento
- **Monitoring**: Data drift detection
- **Features online**: perfil histórico + score heurístico/ML na demo Java

## 5. Segurança e LGPD
- **Mascaramento**: Dados sensíveis ofuscados
- **Criptografia**: AES-256 em trânsito e repouso
- **Audit Logs**: Todos os acessos registrados
- **Data Retention**: Políticas automáticas de exclusão

## 6. Disaster Recovery
- **Backup**: Automático para Data Lake
- **Replication**: Cross-region para dados críticos
- **RTO**: 4 horas para recuperação completa
- **RPO**: 15 minutos de perda de dados

## 7. Monitoramento
- **Alertas**: Proativos baseados em métricas
- **Dashboards**: Tempo real para métricas chave (Streamlit + Grafana)
- **Logging**: Centralizado no Log Analytics
- **Tracing**: End-to-end com Application Insights

## 8. Manutenção
- **IaC**: Terraform para consistência
- **CI/CD**: Deploys automatizados
- **Documentação**: Completa e atualizada
- **Automation**: Scripts para operações comuns (`batch_dataprep_mongo.py`, `demo_full_stack.sh`)
