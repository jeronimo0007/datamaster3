#!/usr/bin/env bash
# Ensaio interativo da banca — passo a passo com pausas.
# Uso:
#   bash docs/estudos/ensaio-banca.sh           # tour completo
#   bash docs/estudos/ensaio-banca.sh --rapido    # versão ~25 min
#   bash docs/estudos/ensaio-banca.sh --so-check  # só validações, sem pausas
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

MODO="${1:-completo}"
RAPIDO=false
SO_CHECK=false

case "$MODO" in
  --rapido|-r) RAPIDO=true ;;
  --so-check|-c) SO_CHECK=true ;;
  --help|-h)
    echo "Uso: bash docs/estudos/ensaio-banca.sh [--rapido|--so-check|--help]"
    exit 0
    ;;
esac

# cores (desliga se terminal não suporta)
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
  CYN=$(tput setaf 6 2>/dev/null || true)
  GRN=$(tput setaf 2 2>/dev/null || true)
  YEL=$(tput setaf 3 2>/dev/null || true)
  BLD=$(tput bold 2>/dev/null || true)
  RST=$(tput sgr0 2>/dev/null || true)
else
  CYN="" GRN="" YEL="" BLD="" RST=""
fi

step() {
  local n="$1" titulo="$2" fala="$3" acao="$4"
  echo ""
  echo "${BLD}${CYN}════════════════════════════════════════════════════════════${RST}"
  echo "${BLD}Passo ${n} — ${titulo}${RST}"
  echo "${BLD}${CYN}════════════════════════════════════════════════════════════${RST}"
  echo ""
  echo "${YEL}O que dizer:${RST}"
  echo "  ${fala}"
  echo ""
  echo "${YEL}Ação:${RST}"
  echo "  ${acao}"
  echo ""
  if [[ "$SO_CHECK" == true ]]; then
    return 0
  fi
  read -r -p "Enter para continuar (Ctrl+C para sair)… " _
}

run() {
  echo "${GRN}\$ $*${RST}"
  eval "$@"
}

echo "${BLD}DataMaster — ensaio de banca${RST}"
echo "Modo: $([[ "$RAPIDO" == true ]] && echo 'RÁPIDO (~25 min)' || [[ "$SO_CHECK" == true ]] && echo 'SÓ CHECK' || echo 'COMPLETO (~45–65 min)')"
echo "Raiz: $ROOT"
echo ""
echo "Guia cronometrado: docs/estudos/roteiro-cronometrado.md"
echo ""

# ── Pré-voo ──────────────────────────────────────────────────────────────────
step "0" "Pré-voo" \
  "Antes da sala: stack no ar, dados populados, abas fixas no navegador." \
  "bash scripts/run_demo.sh  ·  bash scripts/status-stack.sh"

if [[ "$SO_CHECK" == true ]]; then
  run "bash scripts/status-stack.sh" || true
else
  echo "  (Execute run_demo.sh agora se ainda não rodou.)"
  read -r -p "Stack pronta? Enter… " _
  run "bash scripts/status-stack.sh" || true
fi

# ── A: Produto ───────────────────────────────────────────────────────────────
step "1" "Portal :8880" \
  "Mapa da demo — links e credenciais de todos os serviços." \
  "Abrir http://localhost:8880 — mostrar tabela de serviços."

step "2" "API :8080" \
  "Motor de scoring Spring Boot. Heurística + boost contra perfil Mongo. Limiar fraude: score ≥ 0,74." \
  "Swagger http://localhost:8080/swagger-ui.html"

run "curl -sf http://localhost:8080/health | python3 -m json.tool" || echo "  !! API indisponível"
run "curl -sf http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool" || echo "  !! profile-stats falhou — rode run_demo.sh"

echo ""
echo "${YEL}Analyze — fraude explícita:${RST}"
run "curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H 'Content-Type: application/json' \
  -d '{\"amount\":50000,\"merchant_category\":\"Viagem\",\"user_country\":\"BR\",\"merchant_country\":\"US\",\"payment_method\":\"CREDIT_CARD\",\"hour\":3,\"is_weekend\":1,\"is_international\":1,\"user_id\":\"user_1001\"}' \
  | python3 -m json.tool | head -40"

if [[ "$RAPIDO" == false ]]; then
  step "2b" "API — LGPD" \
    "Mascaramento de PII — CPF, e-mail, telefone." \
    "curl POST /api/v1/lgpd/mask ou Swagger"
  run "curl -s -X POST http://localhost:8080/api/v1/lgpd/mask \
    -H 'Content-Type: application/json' \
    -d '{\"cpf\":\"12345678901\",\"email\":\"joao@banco.com\"}' | python3 -m json.tool"
fi

step "3" "Dashboard :8501" \
  "Operação — fraudes, liberar falso positivo, LGPD, assistente IA." \
  "Abrir http://localhost:8501 — KPIs, aba Transações, liberar 1 caso."

if [[ "$RAPIDO" == false ]]; then
  step "3b" "Dashboard — LGPD" \
    "Aba LGPD / mascaramento — aplicar máscara na UI." \
    "Preencher CPF fictício e aplicar."
fi

step "4" "Console :3333" \
  "Simula o core banking — gera JSON e envia lote à API." \
  "Abrir http://localhost:3333 — Gerar JSON ou Enviar lote."

# ── B: Dados ─────────────────────────────────────────────────────────────────
step "5" "MongoDB — perfis batch" \
  "Perfis user_profiles alimentam o /analyze. Batch layer → serving online." \
  "profile-stats + opcional mongosh"

run "curl -sf http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool"

if [[ "$RAPIDO" == false ]]; then
  step "6" "PostgreSQL OLTP" \
    "Schema relacional de referência — transactions, fraud_alerts, audit. API local não grava aqui." \
    "docker exec postgres psql …"
  run "docker exec postgres psql -U admin -d fraud_detection -c '\\dt'" || echo "  !! Postgres"
fi

step "7" "MinIO + lake Medallion" \
  "Object storage S3/ADLS. Camadas Bronze, Silver, Gold em data/lake/." \
  "MinIO :9001 + ls data/lake/"

run "ls -la data/lake/ 2>/dev/null | head -10 || echo '  !! Rode run_demo.sh para popular lake'"
if [[ -f data/lake/reports/dq_latest.json ]]; then
  run "head -15 data/lake/reports/dq_latest.json"
fi
echo "  Abrir http://localhost:9001 (minioadmin/minioadmin)"

step "8" "Spark :18080" \
  "Batch distribuído — master + worker. Job Medallion no cluster." \
  "Abrir http://localhost:18080 — Workers + Completed Applications"

if [[ "$RAPIDO" == false ]]; then
  step "9" "Jupyter :8888" \
    "Engenharia interativa — notebook DQ, PySpark no cluster." \
    "http://localhost:8888/?token=datamaster — work/notebooks/01_dataprep_dq.py"
fi

# ── C: Mensageria ────────────────────────────────────────────────────────────
if [[ "$RAPIDO" == false ]]; then
  step "10" "Zookeeper" \
    "Infra interna do Kafka — em produção seria gerenciado." \
    "docker compose ps zookeeper kafka"
  run "docker compose ps zookeeper kafka 2>/dev/null | tail -n +1" || true
fi

step "11" "Kafka :9092" \
  "Streaming — narrativa Event Hubs. Caminho crítico da demo NÃO passa pelo Kafka." \
  "docker exec kafka kafka-topics --list"

run "docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null" \
  && echo "  OK Kafka" || echo "  !! Kafka indisponível"

step "12" "RabbitMQ :15672" \
  "Fila fraud.alert.email — API publica alerta, HTTP não espera SMTP." \
  "UI http://localhost:15672 (datamaster/datamaster) — aba Queues"

if [[ "$RAPIDO" == false ]]; then
  step "13" "email-worker :8090" \
    "Consumidor assíncrono — JavaMail. Sem SMTP no .env só loga aviso." \
    "health + logs"
  run "curl -sf http://localhost:8090/actuator/health | python3 -m json.tool" || echo "  !! email-worker"
  run "docker logs fraud-email-worker --tail 20 2>/dev/null" || true
fi

# ── D: Observabilidade ───────────────────────────────────────────────────────
if [[ "$RAPIDO" == false ]]; then
  step "14" "Redis" \
    "Cache transversal — infra pronta; demo scoring não depende dele." \
    "redis-cli PING"
  run "docker exec redis redis-cli PING 2>/dev/null" || echo "  !! Redis"
fi

if [[ "$RAPIDO" == false ]]; then
  step "15" "Prometheus :9090" \
    "Métricas pull da API — target fraud-api UP." \
    "http://localhost:9090/targets"
else
  echo ""
  echo "${YEL}Prometheus (encurtado):${RST} http://localhost:9090/targets — fraud-api UP"
fi

step "16" "Grafana :3000" \
  "Dashboards SRE — pasta DataMaster, painel API Fraude." \
  "http://localhost:3000 (admin/admin)"

echo ""
echo "${YEL}Gerando tráfego para Grafana…${RST}"
run "for i in \$(seq 1 10); do curl -sf -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H 'Content-Type: application/json' \
  -d '{\"amount\":500,\"merchant_category\":\"Alimentação\",\"user_id\":\"user_1001\",\"hour\":12}' >/dev/null; done" \
  || true

# ── Fechamento ───────────────────────────────────────────────────────────────
step "17" "Demo de negócio + fechamento" \
  "Console loop + dashboard + mapa nuvem. Não era só Jupyter — pipeline, governança e API com contrato." \
  "Console Iniciar loop · Dashboard liberar fraude · portal/banca.html se quiser slides"

echo ""
echo "${GRN}${BLD}=== Ensaio concluído ===${RST}"
echo ""
run "bash scripts/status-stack.sh" || true
echo ""
echo "Checklist: docs/estudos/roteiro-cronometrado.md (final)"
echo "Índice guias: docs/estudos/README.md"
