# Documentación del Proyecto — ProjEscuela

Última actualización: 10 de diciembre de 2025

Propósito
- Documentar todo lo creado y modificado durante la integración del login (frontend + backend) y los cambios realizados en la base de datos `escuela.usuarios`.
- Servir como referencia técnica para revisión, auditoría y difusión.

Resumen ejecutivo
- Se implementó un backend en Flask con un endpoint de autenticación `POST /api/login` que valida usuarios contra la tabla `escuela.usuarios` en PostgreSQL y devuelve un JWT (`access_token`).
- Se creó un frontend en Angular con una pantalla de login (captura usuario y contraseña) y un componente `Home` para usuarios autenticados.
- Se migraron contraseñas existentes a bcrypt y se añadieron columnas/respaldos en la tabla `escuela.usuarios` para soportar la transición.
- Se añadió lógica de compatibilidad en el backend para detectar dinámicamente las columnas de contraseñas (evitar errores si alguna columna fue eliminada manualmente).

Estructura del repositorio (resumen de la estructura final)

- Backend/
  - `domain/` — Acceso a la base de datos y utilidades del dominio:
    - `domain/Configuration/database.py` — helper de conexión (`get_db_connection`).
    - `domain/create_escuela_user.py`, `domain/create_user.py`, `domain/get_plain_pw.py`, `domain/cleanup_plain_passwords.py` — utilidades y scripts que tocan directamente la tabla `escuela.usuarios`.
  - `applications/` — Reglas de negocio y procesos de migración:
    - `applications/migrate_to_bcrypt.py` — migrador a bcrypt.
  - `infrastructure/` — Controladores y adaptadores de entrada/salida:
    - `infrastructure/app.py` — Flask app (blueprints registrados).
    - `infrastructure/routes/auth.py` — endpoint `POST /api/login`.
  - `app.py` — entrypoint que delega en `infrastructure.app` (mantiene compatibilidad con comandos previos).
  - `requirements.txt` — dependencias: `Flask`, `python-dotenv`, `psycopg2-binary`, `bcrypt`, `PyJWT`.
  - `tests/` — pruebas unitarias e integración (ejecutadas con pytest).

- Frontend/
  - Angular app (skeleton) con rutas mínimas:
    - `LoginComponent` (`src/app/login/*`) — formulario de login con validación básica, botón de mostrar/ocultar contraseña.
    - `HomeComponent` (`src/app/home/*`) — pantalla simple que muestra nombre de usuario decodificado desde el JWT.
    - `AuthService` (`src/app/services/auth.service.ts`) — responsable de `login()`, `setToken()`, `getToken()` y parseo del JWT.
  - `proxy.conf.json` — proxy de dev server para redirigir `/api` al backend (`http://localhost:5000`) y evitar CORS durante desarrollo.
  - Ajustes en `tsconfig.json` y `angular.json` para compatibilidad con la versión del builder y el entorno de desarrollo local.

Cambios a la Base de Datos
- Tabla objetivo: `escuela.usuarios`.

Cambios aplicados por la migración (scripts en `Backend/domain` y `Backend/applications`):
1. Columnas añadidas (si no existían):
   - `pwr_usuario_hash` (text): contiene la contraseña bcrypt (ej. `$2b$12$...`).
   - `pwr_usuario_plain` (text, temporal): copia de la contraseña en claro durante la migración (opcional, se recomienda limpiar después).

2. Tabla de respaldo creada por `cleanup_plain_passwords.py` (si se ejecutó):
   - `escuela.usuarios_pwr_plain_backup` — copia de filas con `pwr_usuario_plain` antes de ser NULLed.

3. Comportamiento del migrador (`migrate_to_bcrypt.py`):
   - Detecta usuarios con contraseña en claro (según la columna antigua o `pwr_usuario_plain`) y genera bcrypt con `bcrypt.hashpw(..., bcrypt.gensalt())` guardándolo en `pwr_usuario_hash`.
   - Tiene `--dry-run` para revisar qué cambios se harían sin escribir.

4. Estado actual observado en la DB (ejemplo):
   - Se confirmó que `pwr_usuario` fue eliminada manualmente por el usuario. No hay problema: la migración creó `pwr_usuario_hash`.
   - Para el usuario `wamm20@gmail.com` `pwr_usuario_hash` existe y comienza con `$2b$12$...`.
   - `pwr_usuario_plain` estaba vacía (o fue limpiada) después de migración/backup.

SQL útiles para inspección (ejecutar con `psql` o desde una herramienta SQL):
- Listar columnas:
  SELECT column_name
  FROM information_schema.columns
  WHERE table_schema='escuela' AND table_name='usuarios'
  ORDER BY column_name;

- Ver hash y plain para un usuario:
  SELECT usuario, pwr_usuario_hash, pwr_usuario_plain
  FROM escuela.usuarios
  WHERE usuario = 'wamm20@gmail.com';

- Ver contenido de la tabla backup (si existe):
  SELECT * FROM escuela.usuarios_pwr_plain_backup LIMIT 100;

Endpoint de autenticación (backend)
- Ruta: `POST /api/login`
- Payload JSON esperado: `{ "username": "<usuario o email>", "password": "<clave>" }`
- Respuesta (éxito): `200` con JSON `{ "access_token": "<JWT>" }`
- Respuesta (error credenciales): `401` o `200` con campo vacío según la implementación de frontend (actualmente backend responde `200` con token en éxito y `401`/error genérico en fallo). Recomendación: estandarizar a `401` para credenciales inválidas.

Lógica de verificación implementada
1. El backend detecta qué columnas de contraseña existen consultando `information_schema.columns`.
2. Si existe `pwr_usuario_hash`, se usa bcrypt para comparar la contraseña enviada.
3. Si no existe hash pero existe `pwr_usuario_plain` o `pwr_usuario` (columna antigua), hay una verificación en texto plano como fallback durante migración.
4. Si la contraseña valida, se devuelve un JWT con `sub` = id_usuario y un `username` en el payload. El secreto y tiempo de expiración vienen de variables de entorno (`JWT_SECRET`, `JWT_EXPIRE_MINUTES`).

- Ejecución y pruebas (comandos reproducibles)
- Preparar entorno backend (virtualenv):
```bash
cd /ruta/al/proyecto/ProjEscuela
python -m venv .venv
source .venv/bin/activate
pip install -r Backend/requirements.txt
cp Backend/.env.example Backend/.env   # editar valores DB y JWT
```
- Iniciar backend (desarrollo):
```bash
source .venv/bin/activate
# Recomendado: usar el entrypoint principal (mantiene compatibilidad)
python Backend/app.py
# o en background (logs se guardan en `logs/`)
nohup python Backend/app.py > logs/backend.log 2>&1 &
```
- Inspeccionar logs:
```bash
tail -f logs/backend.log
```
- Ejecutar migración (dry-run):
```bash
# El migrador ahora está en la capa de aplicaciones
python Backend/applications/migrate_to_bcrypt.py --dry-run
```
- Ejecutar migración real (verificar antes):
```bash
python Backend/applications/migrate_to_bcrypt.py
```
- Ejecutar cleanup de contraseñas plain (recomendado solo tras respaldo):
```bash
python Backend/domain/cleanup_plain_passwords.py --no-run  # dry-run
python Backend/domain/cleanup_plain_passwords.py            # aplicar
```
- Probar endpoint login (curl):
```bash
curl -v -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wamm20@gmail.com","password":"W1ll14m#$"}'
```
- Iniciar frontend (dev server con proxy):
```bash
cd Frontend
npm install
npm run start
# abre: http://localhost:4200
```

Consideraciones de seguridad y recomendaciones
- JWT secret: Asegúrate de que `JWT_SECRET` sea fuerte y no esté en control de versiones. Rota si el secreto pudo haber sido expuesto.
- Contraseñas en texto plano: El objetivo final debe ser eliminar `pwr_usuario_plain`. El script `cleanup_plain_passwords.py` crea una tabla de respaldo antes de `NULL`ear`pwr_usuario_plain`. Recomendación: conservar respaldo fuera de la BD de producción y luego eliminarlo definitivamente.
- Producción: No usar el servidor de desarrollo Flask en producción. Implementar Gunicorn/uWSGI + reverse proxy (Nginx) y activar HTTPS.
- Hardening DB: restringir accesos al rol `postgres` y usar cuentas con permisos mínimos desde la app.

Notas sobre decisiones técnicas
- Se eligió bcrypt para hashing por su resistencia y soporte en Python (`bcrypt` library).
- Se devolvió JWT sencillo por simplicidad; para un sistema real considere:
  - refresh tokens, expiración corta de access tokens y revocación.
  - firmar con HS256 (actual) o RS256 (clave pública/privada) según necesidades.
- El frontend usa un proxy dev para evitar CORS en desarrollo y guarda token en `localStorage` (para producción considere `httpOnly` cookies o gestión más segura).

Archivos clave y su ubicación
- Backend/
  - `domain/Configuration/database.py`
  - `domain/create_escuela_user.py`
  - `domain/create_user.py`
  - `domain/get_plain_pw.py`
  - `domain/cleanup_plain_passwords.py`
  - `applications/migrate_to_bcrypt.py`
  - `infrastructure/app.py`
  - `infrastructure/routes/auth.py`
  - `app.py` (entrypoint que delega en `infrastructure.app`)
  - `requirements.txt`
  - `.env.example`
- Frontend/
  - `src/app/login/login.component.{ts,html,css}`
  - `src/app/home/*`
  - `src/app/services/auth.service.ts`
  - `proxy.conf.json`
  - `package.json`, `angular.json`, `tsconfig.json`

Pruebas realizadas y resultados
- Migración dry-run: mostró usuarios a procesar.
- Migración real: generó `pwr_usuario_hash` para el usuario de prueba.
- Backend arrancó correctamente y `POST /api/login` devolvió `access_token` para credenciales correctas.
- Frontend (`ng serve`) cargó la aplicación y el login funcionó tanto con petición directa al backend como vía proxy (http://localhost:4200 -> /api/login).
- Se actualizó la UI para mostrar/ocultar contraseña con icono SVG (ojo cerrado por defecto).

Pasos siguientes recomendados
- Revisar y aprobar limpieza de `pwr_usuario_plain` (ejecutar `cleanup_plain_passwords.py --apply` tras respaldo).
- Cambiar almacenamiento de token en frontend a mecanismo más seguro si la app va a producción.
- Añadir controles de acceso (route-guards) en Angular para proteger rutas.
- Añadir tests automatizados para el endpoint de login (pytest + requests o pruebas integradas) y tests E2E para el flujo de login con Playwright o Cypress.

Profesores (nueva funcionalidad)
--------------------------------

- Tabla: `escuela.profesores` ahora incluye los campos relevantes:
  - `id_profesor` (PK)
  - `nombre`, `apellido` (varchar)
  - `cedula_prof` (numeric o integer, hasta 8 dígitos)
  - `especialidad`, `email`
  - `anu_prof` (char(1)) — indica anulado cuando contiene 'X', activo cuando NULL

- Endpoints implementados (backend Flask, prefijo `/api`):
  - `GET /api/profesores` — lista todos los profesores (incluye `cedula_prof` y `anu_prof`).
  - `GET /api/profesores/<id>` — obtiene un profesor por `id_profesor`.
  - `POST /api/profesores` — crea profesor. Payload JSON: `{ nombre, apellido, cedula_prof, especialidad, email }`.
  - `PUT /api/profesores/<id>` — actualiza campos proporcionados (uso de `COALESCE` para no sobrescribir valores no enviados).
  - `DELETE /api/profesores/<id>` — *anula* al profesor (no borra). Esto actualiza `anu_prof = 'X'` y devuelve `id_profesor`.
  - `POST /api/profesores/<id>/activar` — endpoint protegido que restablece `anu_prof = NULL`. Requiere token JWT con `user_level == 1` (admin).

- Comportamiento y validaciones importantes:
  - `cedula_prof` acepta números o strings de dígitos; máximo 8 dígitos. Se valida en backend y frontend.
  - Al anular un profesor el campo `anu_prof` pasa a `'X'`. En la UI los botones `Editar` y `Anular` quedan deshabilitados para registros anulados y aparece un botón `Activar` (visible solo para nivel 1).
  - Al activar, `anu_prof` se establece a `NULL`.

- Frontend (Angular) cambios clave:
  - Servicio: `src/app/services/profesor.service.ts` — métodos: `getProfesores()`, `getProfesor(id)`, `createProfesor()`, `updateProfesor()`, `anularProfesor()`, `activateProfesor()`.
  - Componente: `src/app/profesores/profesores.component.ts/html/css` — listado, formulario (campo `cedula_prof` agregado justo después de `apellido`), validaciones de longitud, modal para crear/editar, mecanismos de anular/activar y deshabilitado de botones según `anu_prof`.
  - Ruta registrada en `src/app/app-routing.module.ts` como `/profesores` y menú actualizado en `src/app/sidebar/sidebar.component.html`.

- Nota sobre dependencias CommonJS en Angular:
  - Durante compilación puede aparecer una advertencia sobre `sweetalert2` (CommonJS). Para silenciar la advertencia y permitir optimizaciones, agregar en `angular.json` dentro de `projects.<tu-app>.architect.build.options`:

```json
"allowedCommonJsDependencies": ["sweetalert2"]
```

- Migración/SQL (si la columna no existe en tu DB):
  - Para añadir `cedula_prof` y `anu_prof` si no existen:

```sql
ALTER TABLE escuela.profesores ADD COLUMN IF NOT EXISTS cedula_prof numeric(8,0);
ALTER TABLE escuela.profesores ADD COLUMN IF NOT EXISTS anu_prof character(1);
```

  - Verificar índices/constraints según la política de la base de datos.

Pruebas sugeridas para `profesores`
- Crear un profesor con `cedula_prof` de 8 dígitos y revisar respuesta 201 y que aparezca en `GET /api/profesores`.
- Anularlo con `DELETE /api/profesores/<id>` y verificar `anu_prof = 'X'` en la respuesta y en la UI.
- Intentar editar mientras está anulado: botones deben estar deshabilitados y la UI no debe permitir cambios.
- Activar con `POST /api/profesores/<id>/activar` usando un token admin y verificar `anu_prof` = NULL.

Archivos añadidos/actualizados para `profesores`:
- Backend:
  - `Backend/domain/profesores.py` — validación, CRUD, anular/activar.
  - `Backend/infrastructure/routes/profesores.py` — endpoints REST y protección para `activar`.
  - `Backend/infrastructure/app.py` — registro del blueprint `profesores_bp`.
- Frontend:
  - `Frontend/src/app/services/profesor.service.ts`
  - `Frontend/src/app/profesores/profesores.component.ts`
  - `Frontend/src/app/profesores/profesores.component.html`
  - `Frontend/src/app/profesores/profesores.component.css`
  - `Frontend/src/app/app-routing.module.ts` (ruta)
  - `Frontend/src/app/sidebar/sidebar.component.html` (menú)

Notas operativas
- El patrón de anular/activar sigue exactamente la misma lógica utilizada en `alumnos`, por lo que la interacción y permisos son consistentes entre módulos.


Corrección reciente (28 de enero de 2026)
------------------------------------

- **Resumen:** Se detectó un fallo que hacía que la interfaz mostrara "Sesión expirada" al intentar listar usuarios. Causa: tokens JWT generados con el claim `sub` como entero provocaban que PyJWT lanzara `InvalidSubjectError` en el backend; la excepción era tratada como token inválido/expirado y devolvía 401, provocando la UX observada.
- **Qué se corrigió:**
  - En el backend se comenzó a emitir `sub` como *string* y al decodificar se convierte a entero cuando se necesita (`int(payload.get('sub'))`). Esto evita la excepción de PyJWT por tipo incorrecto en `sub`.
  - En el frontend se añadió una comprobación proactiva de expiración de token (`AuthService.isTokenExpired()`) y se propagó el guardado en componentes clave (`AppComponent`, `HomeComponent`, `WelcomeComponent`, `UsuariosComponent`) para evitar llamadas a la API cuando el token ya expiró.
  - Se eliminaron logs temporales que volcaban el header `Authorization` para evitar registrar datos sensibles.
- **Archivos modificados (resumen):**
  - [Backend/infrastructure/routes/auth.py](Backend/infrastructure/routes/auth.py)
  - [Frontend/src/app/services/auth.service.ts](Frontend/src/app/services/auth.service.ts)
  - [Frontend/src/app/app.component.ts](Frontend/src/app/app.component.ts)
  - [Frontend/src/app/home/home.component.ts](Frontend/src/app/home/home.component.ts)
  - [Frontend/src/app/welcome/welcome.component.ts](Frontend/src/app/welcome/welcome.component.ts)
  - [Frontend/src/app/usuarios/usuarios.component.ts](Frontend/src/app/usuarios/usuarios.component.ts)
- **Pasos de verificación rápidos:**
  1. Reiniciar backend y frontend:

```bash
# Backend (desde la raíz del proyecto)
source .venv/bin/activate
python Backend/app.py

# Frontend
cd Frontend
npm run start
```

  2. Hacer login válido y obtener `access_token` (la UI lo hace automáticamente). Comprobar `GET /api/users` con curl (ejemplo):

```bash
curl -v -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:5000/api/users
```

  3. Generar o usar un token expirado y comprobar que la aplicación redirige al login sin hacer la petición a `/api/users`.
- **Recomendaciones:**
  - Añadir `JWT_EXPIRE_MINUTES` a `Backend/.env` para controlar expiración desde entorno.
  - No loggear headers `Authorization` en entornos productivos.
  - Considerar refresco de tokens (refresh tokens) y/o uso de cookies `HttpOnly` para mayor seguridad.


Contacto y notas finales
- Archivo de configuración de DB: `Backend/Configuration/database.py` (usa `.env`).
- Registro de cambios y scripts de migración están en `Backend/`.

Si quieres, puedo:
- Generar un README más corto orientado a operaciones (runbook) con comandos mínimos para despliegue y rollback.
- Crear scripts de unit/integration tests para el endpoint de login.
- Ejecutar la limpieza de `pwr_usuario_plain` bajo tu autorización.

---
Documento generado automáticamente por la herramienta de soporte de desarrollo del proyecto.
