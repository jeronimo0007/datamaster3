#!/usr/bin/env bash
# Exporta SVG + PNG 2x dos diagramas usados em portal/banca.html
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARCH="$ROOT/docs/arquitetura"
PORTAL="$ROOT/portal"

DRAWIO="${DRAWIO_APP:-/Applications/draw.io.app/Contents/MacOS/draw.io}"
if [[ ! -x "$DRAWIO" ]]; then
  echo "draw.io não encontrado. Instale ou defina DRAWIO_APP." >&2
  exit 1
fi

for f in datamaster-00-visao-geral datamaster-01-batch-medallion datamaster-02-online-gateway; do
  "$DRAWIO" --export --format svg --output "$PORTAL/${f}.svg" "$ARCH/${f}.drawio"
  "$DRAWIO" --export --format png --scale 2 --output "$PORTAL/${f}.png" "$ARCH/${f}.drawio"
  cp "$PORTAL/${f}.png" "$ARCH/${f}.png"
  echo "✓ $f → portal/ (+ docs/arquitetura PNG 2x)"
done

echo "Reconstrua o portal: docker compose up -d --build portal"
