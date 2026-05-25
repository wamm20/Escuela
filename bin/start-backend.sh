#!/usr/bin/env bash
set -euo pipefail
# Script para iniciar el backend en desarrollo desde el repositorio
# - activa el virtualenv
# - arranca la app y redirige logs a logs/backend.log

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  echo "Virtualenv .venv no encontrado. Crealo o ajusta el script." >&2
  exit 1
fi

mkdir -p logs
echo "Activando venv y arrancando backend (logs -> logs/backend.log)"
source .venv/bin/activate

nohup python Backend/app.py > logs/backend.log 2>&1 &
PID=$!
echo "Backend iniciado (PID=$PID). Ver logs: logs/backend.log"
