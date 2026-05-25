#!/usr/bin/env bash
set -euo pipefail
# Detiene procesos del backend (intenta apagar limpiamente, fuerza si es necesario).

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Buscando procesos del backend..."
PIDS="$(pgrep -f "python Backend/app.py" || true) $(pgrep -f "infrastructure.app" || true)"
PIDS="$(echo $PIDS | xargs)"

if [ -z "$PIDS" ]; then
  echo "No se encontraron procesos del backend.";
  exit 0
fi

echo "PID(s) a detener: $PIDS"
echo "Enviando SIGTERM..."
kill $PIDS || true
sleep 2

# Verificar si siguen vivos
STILL_ALIVE="$(pgrep -f "python Backend/app.py" || true) $(pgrep -f "infrastructure.app" || true)"
STILL_ALIVE="$(echo $STILL_ALIVE | xargs)"
if [ -n "$STILL_ALIVE" ]; then
  echo "Procesos todavía activos: $STILL_ALIVE. Enviando SIGKILL..."
  kill -9 $STILL_ALIVE || true
  sleep 1
fi

echo "Backend detenido." 
