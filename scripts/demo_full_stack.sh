#!/usr/bin/env bash
# Demo focada em engenharia de dados: ingestão → Medallion → (opcional) Spark + serving.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Garantindo stack..."
docker compose up -d --build

echo "==> Ingestão multi-formato (landing)..."
# Tenta com fontes públicas (CSV + JSON OpenML); sem rede, cai para sintético
python3 scripts/ingest_landing.py || python3 scripts/ingest_landing.py -n 300 --skip-public

echo "==> Medallion Bronze → DQ → Silver → Gold..."
python3 scripts/medallion_job.py all --backend pandas

if docker compose ps --status running 2>/dev/null | grep -q mongodb; then
  echo "==> Perfis Mongo (serving API)..."
  python3 scripts/batch_dataprep_mongo.py -i data/transactions.json || true
fi

echo "==> Spark job (opcional)..."
docker compose run --rm -e MEDALLION_LAYER=all spark-job || echo "(Spark job pulado)"

echo ""
echo "OK. Airflow UI: http://localhost:8085 (admin/admin) — DAG datamaster_e2e"
echo "Portal:         http://localhost:8880"
echo "Lake:           data/lake/{bronze,silver,gold}"
echo "Landing:        data/landing/"
