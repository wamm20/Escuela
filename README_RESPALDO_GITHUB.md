# Respaldo GitHub - ProjEscuela

Este documento define el flujo minimo y seguro para publicar un respaldo del proyecto en GitHub sin secretos ni librerias innecesarias.

## Objetivo

- Publicar codigo fuente y documentacion del proyecto.
- Excluir secretos (tokens, passwords, .env reales).
- Excluir dependencias instaladas y artefactos generados.

## Reglas de seguridad

1. Nunca subir `Backend/.env` ni otros `.env` con valores reales.
2. Mantener solo plantillas como `Backend/.env.example`.
3. Excluir `node_modules`, `.venv`, `dist`, logs y caches.
4. Antes de `git push`, revisar siempre con `git status` y `git diff --cached --name-only`.

## Alcance del respaldo basico

Incluye:
- Codigo fuente de `Backend` y `Frontend/src`.
- Scripts, configuraciones y documentacion.

Excluye:
- `.env` reales y llaves.
- Librerias instaladas (`node_modules`, `.venv`).
- Artefactos de build y runtime (`Frontend/dist`, `.angular`, logs, caches).

## Flujo operativo recomendado

Desde la raiz de `ProjEscuela`:

```bash
git init
git branch -M main
git add .
git status --short
git diff --cached --name-only
```

Validar que NO aparezcan archivos sensibles, por ejemplo:
- `Backend/.env`
- Cualquier `*.key`, `*.pem`, `*.p12`, `*.pfx`

Primer commit:

```bash
git commit -m "chore: respaldo basico seguro del proyecto Escuela"
```

Configurar remoto y publicar:

```bash
git remote add origin https://github.com/wamm20/Escuela.git
git push -u origin main
```

## Checklist previo al push

- [ ] `.gitignore` presente y correcto.
- [ ] `Backend/.env` excluido.
- [ ] Sin `node_modules`, `.venv`, `dist`, logs ni caches en staging.
- [ ] `git status` limpio despues del commit.

## Nota operativa

Si GitHub solicita autenticacion, usar credenciales del usuario o token personal (PAT) segun el metodo configurado en la maquina.
