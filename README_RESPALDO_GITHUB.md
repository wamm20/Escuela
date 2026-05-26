# Respaldo GitHub - ProjEscuela

Este documento define el flujo minimo y seguro para publicar respaldos del proyecto en GitHub sin secretos ni librerias innecesarias.

## Estado actual (2026-05-26)

- Repositorio remoto activo: `https://github.com/wamm20/Escuela.git`
- Rama publicada: `main`
- Commit base de respaldo limpio: `000ab456`
- Tag publicado: `v1.1.0-calificaciones-20260526`

## Ultimo hito publicado

- Modulo de calificaciones publicado en backend y frontend.
- Ajustes operativos en `run-project.sh`.
- Carga de configuracion de BD preparada para leer desde `.venv/.env` fuera del respaldo.

## Objetivo

- Publicar codigo fuente y documentacion del proyecto.
- Excluir secretos (tokens, passwords, `.env` reales).
- Excluir dependencias instaladas y artefactos generados.
- Mantener una base versionada y trazable para proximos respaldos.

## Reglas de seguridad

1. Nunca subir `Backend/.env` ni otros `.env` con valores reales.
2. Mantener solo plantillas como `Backend/.env.example`.
3. Excluir `node_modules`, `.venv`, `.venv-backend`, `dist`, logs y caches.
4. Antes de `git push`, revisar siempre con `git status` y `git diff --cached --name-only`.
5. Versionar cada hito con tag anotado (`git tag -a ...`).

## Alcance del respaldo basico

Incluye:
- Codigo fuente de `Backend` y `Frontend/src`.
- Scripts, configuraciones y documentacion.

Excluye:
- `.env` reales y llaves.
- Librerias instaladas (`node_modules`, `.venv`, `.venv-backend`).
- Artefactos de build y runtime (`Frontend/dist`, `Frontend/.angular`, logs, caches).

## Flujo operativo para proximos respaldos

Desde la raiz de `ProjEscuela`:

```bash
git checkout main
git pull --ff-only origin main
git status --short
```

Preparar cambios:

```bash
git add .
git diff --cached --name-only
```

Validar que NO aparezcan archivos sensibles, por ejemplo:
- `Backend/.env`
- Cualquier `*.key`, `*.pem`, `*.p12`, `*.pfx`
- Rutas de dependencias/artefactos (`node_modules`, `.venv`, `.venv-backend`, `Frontend/dist`, `Frontend/.angular`, `logs`)

Commit y push:

```bash
git commit -m "chore: respaldo <descripcion-corta>"
git push origin main
```

Crear tag de version:

```bash
TAG="vX.Y.Z-o-nombre-hito"
git tag -a "$TAG" -m "Descripcion del hito"
git push origin "$TAG"
```

## Flujo de primer arranque (si no existe repo local git)

```bash
git init
git branch -M main
git add .
git commit -m "chore: respaldo basico seguro del proyecto Escuela"
git remote add origin https://github.com/wamm20/Escuela.git
git push -u origin main
```

## Si el remoto ya trae historial distinto

Si `git push` falla con `fetch first` y hay conflictos grandes al fusionar, usar esta estrategia segura:

1. Publicar respaldo en rama nueva (ejemplo: `backup-basico-seguro-YYYYMMDD`).
2. Resolver en PR contra `main` o crear repo nuevo limpio (cuando aplique).
3. Evitar `force-push` a `main` salvo aprobacion explicita.

## Checklist rapido previo al push

- [ ] `.gitignore` presente y correcto.
- [ ] `Backend/.env` excluido.
- [ ] Sin `node_modules`, `.venv`, `.venv-backend`, `dist`, logs ni caches en staging.
- [ ] `git status` limpio despues del commit.
- [ ] Tag del hito creado y publicado (si aplica).

## Nota operativa

Si GitHub solicita autenticacion, usar credenciales del usuario o token personal (PAT) segun el metodo configurado en la maquina.
