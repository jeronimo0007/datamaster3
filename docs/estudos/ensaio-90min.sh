#!/usr/bin/env bash
# Ensaio 90 min — alinhado a portal/banca.html (slides 0–15 + T0–T12).
# Uso:
#   bash docs/estudos/ensaio-90min.sh
#   bash docs/estudos/ensaio-90min.sh --so-check
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

SO_CHECK=false
[[ "${1:-}" == "--so-check" || "${1:-}" == "-c" ]] && SO_CHECK=true
[[ "${1:-}" == "--help" || "${1:-}" == "-h" ]] && {
  echo "Uso: bash docs/estudos/ensaio-90min.sh [--so-check|--help]"
  echo "Slides: http://localhost:8880/banca.html"
  echo "Guia:   docs/estudos/apresentacao-90min.md"
  exit 0
}

if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
  GRN=$(tput setaf 2 2>/dev/null || true)
  YEL=$(tput setaf 3 2>/dev/null || true)
  MAG=$(tput setaf 5 2>/dev/null || true)
  CYN=$(tput setaf 6 2>/dev/null || true)
  BLD=$(tput bold 2>/dev/null || true)
  RST=$(tput sgr0 2>/dev/null || true)
else
  GRN="" YEL="" MAG="" CYN="" BLD="" RST=""
fi

slide() {
  local num="$1" tempo="$2" titulo="$3" fala="$4" acao="$5"
  echo ""
  echo "${BLD}${MAG}━━━ SLIDE ${num} · ${tempo} · ${titulo} ━━━${RST}"
  echo "${CYN}Abrir em banca.html: slide ${num}${RST}"
  echo ""
  echo "${YEL}Eu digo à banca:${RST}"
  echo "  ${fala}"
  echo ""
  echo "${YEL}Eu mostro:${RST}"
  echo "  ${acao}"
  echo ""
  [[ "$SO_CHECK" == true ]] && return 0
  read -r -p "Enter (→ próximo slide no banca.html)… " _
}

tstep() {
  local id="$1" titulo="$2" acao="$3"
  echo ""
  echo "${BLD}${GRN}  ▶ ${id} — ${titulo}${RST}"
  echo "    ${acao}"
  [[ "$SO_CHECK" == true ]] && return 0
  read -r -p "    Enter… " _
}

run() {
  echo "${GRN}    \$ $*${RST}"
  eval "$@" || echo "    (falhou — plano B no guia)"
}

echo "${BLD}Ensaio 90 min — alinhado a banca.html${RST}"
echo "Abra: http://localhost:8880/banca.html"
echo "Guia: docs/estudos/apresentacao-90min.md"
echo ""

BLOCO="${BLD}PRÉ-VOO (fora dos 90 min)${RST}"
echo "$BLOCO"
if [[ "$SO_CHECK" == true ]]; then
  run "bash scripts/status-stack.sh"
else
  read -r -p "Stack pronta (run_demo.sh)? Enter… " _
  run "bash scripts/status-stack.sh"
fi

# ── Teoria: slides 0–12 (~46 min) ───────────────────────────────────────────
slide "0" "~3 min" "Apresentador" \
  "Me apresento: riscos, motores de crédito, trajetória em TI financeira." \
  "Ler card do slide; não abrir terminal."

slide "1" "~2 min" "Capa" \
  "Tema: detecção de fraudes. Três frentes: Docker local, VPS K8s, Azure TF. AWS = mapa." \
  "Pipeline animado na capa — fonte ao alerta."

slide "1b" "~2 min" "Três lugares" \
  "Um desenho, três runtimes: compose, k3s, Terraform." \
  "Portal :8880 · citar trilha T1–T12."

slide "2" "~3 min" "Agenda 8 tópicos" \
  "Extração → Ingestão → Armazenamento → Observabilidade → Segurança → LGPD → Arquitetura → Escala." \
  "SVG dos 8 nós; lista com ✅."

slide "3" "~4 min" "Contexto" \
  "Números de fraude, meta <2s, 10M tx/dia, LGPD. Plataforma, não só modelo." \
  "Grid de stats + tabela de requisitos."

slide "4" "~5 min" "Arquitetura Azure" \
  "PNG visão geral + 8 blocos Azure↔local. draw.io só no roteiro (apêndice)." \
  "Imagem datamaster-00-visao-geral.png no slide."

slide "5" "~3 min" "Extração · Tópico 1" \
  "Fontes, contrato JSON, console simula core." \
  "transaction_adapters.py"

slide "6" "~4 min" "Ingestão · Tópico 2" \
  "Lambda: Kafka=stream, batch=Spark+Mongo. Analyze não passa pelo Kafka." \
  "Preparar narrativa para T8."

slide "6b" "~3 min" "Online / gateway" \
  "LB/Gateway apagados. Caminho demo: Console→API→Mongo→Rabbit." \
  "Diagrama verde no slide."

slide "7" "~4 min" "Medallion · Tópico 3" \
  "Bronze/Silver/Gold. spark_local_pipeline.py." \
  "Imagem batch Medallion."

slide "7c" "~3 min" "Lake + DW + ops" \
  "Lake, warehouse narrativo, Mongo operacional." \
  "Três camadas na fala."

slide "7b" "~3 min" "Batch→Mongo→API" \
  "batch_dataprep_mongo → user_profiles → /analyze." \
  "Diagrama do slide; demo vem no T3/T5."

slide "8" "~3 min" "Observabilidade · Tópico 4" \
  "Monitor/App Insights na nuvem; Prometheus/Grafana na mesa." \
  "Demo no T11."

slide "9" "~3 min" "Segurança · Tópico 5" \
  "Key Vault, Entra, RBAC; mascaramento na app." \
  "Só teoria — demo LGPD no slide 10/T4b."

slide "10" "~3 min" "LGPD · Tópico 6" \
  "DataMasker, campos PII, POST /lgpd/mask." \
  "Dashboard aba LGPD ou curl (T4b)."

slide "11" "~3 min" "Arquitetura analítica · Tópico 7" \
  "Kimball, features, governanca.yaml, DQ report." \
  "curl /api/v1/data-quality/report"

slide "12" "~3 min" "Escalabilidade · Tópico 8" \
  "10M+ tx/dia, autoscale, partições." \
  "Batch API e metrics no T7."

echo ""
echo "${BLD}${MAG}━━━ SLIDE 13 · ~30 min · DEMO T0–T12 ━━━${RST}"
echo "${CYN}Manter slide 13 visível ou alternar com browser/terminal${RST}"
[[ "$SO_CHECK" != true ]] && read -r -p "Enter para iniciar demo ao vivo… " _

tstep "T0" "Stack" "docker compose ps · status-stack.sh"
run "docker compose ps --format 'table {{.Name}}\t{{.Status}}' 2>/dev/null | head -20"

tstep "T1" "Health" "curl /health"
run "curl -sf http://localhost:8080/health | python3 -m json.tool"

tstep "T2" "Swagger" "http://localhost:8080/swagger-ui.html"
tstep "T3" "Batch Mongo" "profile-stats > 0"
run "curl -sf http://localhost:8080/api/v1/batch/profile-stats | python3 -m json.tool"

tstep "T4" "Dashboard" "http://localhost:8501 — fraudes, liberar"
tstep "T4b" "LGPD" "Aba LGPD no dashboard (slide 10)"
tstep "T5–T6" "Analyze" "normal + fraude com anomaly_reasons"
run "curl -s -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H 'Content-Type: application/json' \
  -d '{\"amount\":50000,\"merchant_category\":\"Viagem\",\"user_country\":\"BR\",\"merchant_country\":\"US\",\"payment_method\":\"CREDIT_CARD\",\"hour\":3,\"is_weekend\":1,\"is_international\":1,\"user_id\":\"user_1001\"}' \
  | python3 -m json.tool | head -35"

tstep "T7" "Batch API" "Console :3333 ou POST /transactions/batch"
tstep "T4c" "RabbitMQ" ":15672 fila fraud.alert.email · logs worker"
run "curl -sf http://localhost:8090/actuator/health | python3 -m json.tool" || true

tstep "T8" "Kafka" "kafka-topics --list (slide 6)"
run "docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null" || true

tstep "T9" "Jupyter + Spark + lake" ":8888 · :18080 · data/lake/"
run "ls data/lake/bronze data/lake/silver data/lake/gold 2>/dev/null | head -12" || true

tstep "T10" "batch_dataprep" "Mencionar script (já no T3)"
tstep "T11" "Prometheus + Grafana" ":9090 · :3000 (slide 8)"
run "docker exec redis redis-cli PING 2>/dev/null" || true

tstep "T12" "run_demo" "bash scripts/run_demo.sh se necessário · draw.io = apêndice do roteiro"

slide "14" "~3 min" "Mapa multicloud" \
  "Tabela Azure/AWS do slide — fecho equivalências." \
  "Ler tabela na tela."

slide "15" "~2 min" "Encerramento" \
  "Não era só Jupyter — é plataforma. Obrigado, perguntas." \
  "Animação de agradecimento."

echo ""
echo "${GRN}${BLD}=== Ensaio concluído (banca.html 0→15 + T0–T12) ===${RST}"
run "bash scripts/status-stack.sh" || true
