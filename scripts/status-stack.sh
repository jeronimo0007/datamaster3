#!/usr/bin/env bash
# Status rápido da stack Docker para a banca (todos os componentes).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== DataMaster — status da stack ==="
echo ""
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || docker compose ps
echo ""

check_url() {
  local name="$1" url="$2"
  if curl -sf --max-time 3 "$url" >/dev/null 2>&1; then
    echo "  OK  $name — $url"
  else
    echo "  --  $name — $url (indisponível ou sem HTTP)"
  fi
}

echo "=== HTTP / health ==="
check_url "Portal" "http://localhost:8880/"
check_url "API health" "http://localhost:8080/health"
check_url "Swagger" "http://localhost:8080/swagger-ui.html"
check_url "Dashboard" "http://localhost:8501/"
check_url "Console" "http://localhost:3333/"
check_url "Airflow" "http://localhost:8085/"
check_url "Prometheus" "http://localhost:9090/"
check_url "Grafana" "http://localhost:3000/login"
check_url "Spark UI" "http://localhost:18080/"
check_url "Jupyter" "http://localhost:8888/?token=datamaster"
check_url "MinIO console" "http://localhost:9001/"
echo ""

echo "=== CLI ==="
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null | head -5 && echo "  OK  Kafka topics" || echo "  --  Kafka"
docker exec mongodb mongosh --quiet --eval 'db.runCommand({ping:1})' 2>/dev/null >/dev/null && echo "  OK  MongoDB" || echo "  --  MongoDB"
curl -sf http://localhost:8080/api/v1/batch/profile-stats 2>/dev/null | head -c 120 && echo "" && echo "  OK  Mongo via API profile-stats" || echo "  --  profile-stats"
echo ""
