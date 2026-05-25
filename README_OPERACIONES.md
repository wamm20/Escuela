# README de Operaciones — ProjEscuela

Este documento contiene los comandos mínimos para operar, migrar y limpiar contraseñas, además de iniciar frontend y backend en entorno de desarrollo.

Prerequisitos
- Python 3.10+ (se ha trabajado con 3.12 localmente)
- Node.js + npm (o nvm)
- PostgreSQL accesible con las credenciales en `Backend/.env`

Pasos rápidos

1) Preparar entorno Python (backend)
```bash
cd /ruta/al/proyecto/ProjEscuela
python -m venv .venv
source .venv/bin/activate
pip install -r Backend/requirements.txt
# opcional: pip install pytest requests
```

2) Configurar variables de entorno
```bash
cp Backend/.env.example Backend/.env
# Edita Backend/.env con los valores reales (DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT, JWT_SECRET)
```

3) Iniciar backend (desarrollo)
```bash
source .venv/bin/activate
# Ahora la app principal está delegada a la capa de infraestructura.
# El entrypoint sigue siendo `Backend/app.py` y este delega en `infrastructure/app.py`.
python Backend/app.py
# o en background
nohup python Backend/app.py > Backend/backend.log 2>&1 &
```
Alternativa (script):
```bash
# Usa el script para arrancar el backend de forma consistente
./bin/start-backend.sh
```

4) Ejecutar migración a bcrypt (recomendado: dry-run primero)
```bash
# Dry-run para revisar (este script delega en la capa de aplicaciones)
python Backend/migrate_to_bcrypt.py --dry-run
# Si todo ok, ejecutar real
python Backend/migrate_to_bcrypt.py
```

5) Limpiar contraseñas plain (solo después de respaldar)
```bash
python Backend/cleanup_plain_passwords.py --apply
```

6) Iniciar frontend (desarrollo)
```bash
cd Frontend
npm install
npm run start
# abre: http://localhost:4200
```

7) Probar endpoint de login (curl)
```bash
curl -v -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wamm20@gmail.com","password":"W1ll14m#$"}'
```

Profesores — endpoints y operaciones rápidas
-------------------------------------------

La nueva funcionalidad `profesores` está disponible en el backend con prefijo `/api`.

- Crear profesor (POST):
```bash
curl -v -X POST http://127.0.0.1:5000/api/profesores \
  -H "Content-Type: application/json" \
  -d '{"nombre":"JUAN","apellido":"PEREZ","cedula_prof":"12345678","especialidad":"MATEMATICAS","email":"juan.perez@example.com"}'
```

- Listar profesores (GET):
```bash
curl -v http://127.0.0.1:5000/api/profesores
```

- Obtener uno (GET):
```bash
curl -v http://127.0.0.1:5000/api/profesores/1
```

- Actualizar (PUT):
```bash
curl -v -X PUT http://127.0.0.1:5000/api/profesores/1 \
  -H "Content-Type: application/json" \
  -d '{"especialidad":"FISICA"}'
```

- Anular (DELETE) — NO borra, marca `anu_prof = 'X'`:
```bash
curl -v -X DELETE http://127.0.0.1:5000/api/profesores/1
```

- Activar (POST) — requiere token admin en header `Authorization: Bearer <TOKEN>`:
```bash
curl -v -X POST http://127.0.0.1:5000/api/profesores/1/activar \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

SQL: añadir columnas si no existen
```sql
ALTER TABLE escuela.profesores ADD COLUMN IF NOT EXISTS cedula_prof numeric(8,0);
ALTER TABLE escuela.profesores ADD COLUMN IF NOT EXISTS anu_prof character(1);
```

Frontend — notas rápidas
- La UI incluye `cedula_prof` en el formulario (campo después de `apellido`).
- Botones `Editar` y `Anular` se deshabilitan si `anu_prof = 'X'`.
- Aparece botón `Activar` cuando `anu_prof = 'X'` (visible solo para `user_level === 1`).


Logs
- Backend: `Backend/backend.log` (si lo ejecutaste en background con nohup)

8) Ejecutar todo (backend + frontend) — script conveniente
```bash
# Desde la raíz del repositorio
./run-project.sh
```

Qué hace el script:
- Activa el virtualenv `.venv` (debe existir y contener las dependencias).
- Arranca el backend en background (logs -> `logs/backend.log`).
- Espera a que el backend responda en `127.0.0.1:5000` y, si está disponible, arranca el frontend (`npm run start`) en foreground.

Comandos útiles luego de usar `./run-project.sh`:
```bash
# Ver estado del backend
./bin/status-backend.sh

# Parar backend
./bin/stop-backend.sh
# alternativa rápida:
pkill -f "python Backend/app.py"
```

Rollback básicos
- Si la migración generó `pwr_usuario_hash` y quieres revertir (solo en entorno de prueba): restaura desde un respaldo de la BD antes de ejecutar `migrate_to_bcrypt.py`.

Notas de seguridad
- No guardes `.env` con secretos en control de versiones.
- Eliminar `pwr_usuario_plain` es obligatorio antes de mover a producción; usa `cleanup_plain_passwords.py`.

Contacto
- Para más automatizaciones (CI, tests E2E), pedir ayuda para integrarlo en pipelines.
