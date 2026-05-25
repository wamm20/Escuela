#!/usr/bin/env bash
set -euo pipefail
# Muestra el estado del backend y las últimas líneas de logs si está corriendo.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PIDS1="$(pgrep -f "python Backend/app.py" || true)"
PIDS2="$(pgrep -f "infrastructure.app" || true)"
PIDS="$(echo $PIDS1 $PIDS2 | xargs)"

if [ -z "$PIDS" ]; then
  echo "Backend: NO EN EJECUCIÓN"
  exit 1
fi

echo "Backend: EN EJECUCIÓN (PID: $PIDS)"
echo "Comandos de proceso:"
ps -fp $PIDS || true

if [ -f "logs/backend.log" ]; then
  echo
  echo "Últimas 60 líneas de logs/backend.log:"
  tail -n 60 logs/backend.log || true
fi

exit 0
