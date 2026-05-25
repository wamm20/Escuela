#!/usr/bin/env bash
set -euo pipefail
# Script que arranca el backend y luego el frontend (desde la raíz del repo)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  echo "Error: virtualenv .venv no encontrado. Crea el entorno: python -m venv .venv" >&2
  exit 2
fi

echo "Activando virtualenv..."
# shellcheck disable=SC1091
source .venv/bin/activate

mkdir -p logs

echo "Arrancando backend (logs -> logs/backend.log)"
nohup python Backend/app.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend iniciado (PID=$BACKEND_PID)"

# Esperar hasta que el puerto 5000 esté aceptando conexiones (timeout configurable)
HOST=127.0.0.1
PORT=5000
TIMEOUT=30
echo "Esperando backend en ${HOST}:${PORT} (timeout ${TIMEOUT}s) ..."
count=0
while ! (echo > /dev/tcp/${HOST}/${PORT}) 2>/dev/null; do
  sleep 1
  count=$((count+1))
  if [ "$count" -ge "$TIMEOUT" ]; then
    echo "Error: timeout esperando al backend. Revisa logs/backend.log" >&2
    exit 3
  fi
done
echo "Backend disponible en ${HOST}:${PORT}"

if [ ! -d "Frontend" ]; then
  echo "Error: directorio Frontend no encontrado en $ROOT_DIR" >&2
  exit 4
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm no está instalado o no está en PATH." >&2
  exit 5
fi

echo "Instalando dependencias del frontend (npm install)"
cd Frontend
npm install

echo "Arrancando frontend (npm run start)"
# Ejecuta en foreground para ver la salida del dev server
npm run start
