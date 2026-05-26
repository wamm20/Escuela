#!/usr/bin/env bash
set -euo pipefail
# Script que arranca el backend y luego el frontend (desde la raíz del repo)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

VENV_ACTIVATE=""
for candidate in \
  "$ROOT_DIR/.venv/bin/activate" \
  "$ROOT_DIR/.venv-backend/bin/activate" \
  "$ROOT_DIR/../.venv/bin/activate"; do
  if [ -f "$candidate" ]; then
    VENV_ACTIVATE="$candidate"
    break
  fi
done

if [ -z "$VENV_ACTIVATE" ]; then
  echo "Error: no se encontro un virtualenv valido. Rutas probadas: .venv, .venv-backend y ../.venv" >&2
  exit 2
fi

echo "Activando virtualenv..."
# shellcheck disable=SC1091
source "$VENV_ACTIVATE"

if ! command -v python >/dev/null 2>&1; then
  echo "Error: el virtualenv seleccionado no expone el comando python." >&2
  exit 6
fi

if ! python -c "import flask, dotenv, psycopg2, bcrypt, jwt" >/dev/null 2>&1; then
  echo "Dependencias del backend no disponibles en el virtualenv. Instalando Backend/requirements.txt..."
  python -m pip install -r Backend/requirements.txt
fi

mkdir -p logs

if [ -f "$ROOT_DIR/bin/status-backend.sh" ] && bash "$ROOT_DIR/bin/status-backend.sh" >/dev/null 2>&1; then
  echo "Se detecto un backend previo en ejecucion. Deteniendolo antes de iniciar uno nuevo..."
  bash "$ROOT_DIR/bin/stop-backend.sh"
fi

BACKEND_PID=""

cleanup() {
  if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    echo
    echo "Deteniendo backend (PID=$BACKEND_PID)..."
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "Arrancando backend (logs -> logs/backend.log)"
python Backend/app.py > logs/backend.log 2>&1 &
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

FRONTEND_PORT="${FRONTEND_PORT:-4200}"

port_is_busy() {
  local port="$1"
  (echo > /dev/tcp/127.0.0.1/"$port") >/dev/null 2>&1
}

resolve_frontend_port() {
  local requested_port="$1"
  local candidate="$requested_port"
  local attempts=0

  while port_is_busy "$candidate"; do
    candidate=$((candidate+1))
    attempts=$((attempts+1))
    if [ "$attempts" -ge 20 ]; then
      echo "Error: no se encontro un puerto libre para el frontend partiendo de ${requested_port}." >&2
      exit 7
    fi
  done

  echo "$candidate"
}

RESOLVED_FRONTEND_PORT="$(resolve_frontend_port "$FRONTEND_PORT")"
if [ "$RESOLVED_FRONTEND_PORT" != "$FRONTEND_PORT" ]; then
  echo "Puerto ${FRONTEND_PORT} ocupado para el frontend. Usando ${RESOLVED_FRONTEND_PORT}."
fi

echo "Instalando dependencias del frontend (npm install)"
cd Frontend
npm install

echo "Arrancando frontend en el puerto ${RESOLVED_FRONTEND_PORT} (npm run start -- --port ${RESOLVED_FRONTEND_PORT})"
# Ejecuta en foreground para ver la salida del dev server
npm run start -- --port "$RESOLVED_FRONTEND_PORT"
