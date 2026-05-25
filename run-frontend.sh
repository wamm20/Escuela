#!/usr/bin/env bash
set -euo pipefail
# Script de conveniencia para instalar y arrancar el frontend (debe ejecutarse desde la raíz del repo)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

FRONTEND_DIR="$ROOT_DIR/Frontend"
if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Error: no se encontró el directorio Frontend en $ROOT_DIR" >&2
  exit 2
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm no está disponible. Instala Node.js y npm o usa nvm." >&2
  exit 3
fi

echo "Entrando en $FRONTEND_DIR"
cd "$FRONTEND_DIR"

echo "Ejecutando: npm install"
npm install

echo "Ejecutando: npm run start"
npm run start
