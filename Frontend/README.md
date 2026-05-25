# Frontend (Angular) - Proyecto Escuela

Instrucciones rápidas para arrancar el frontend Angular minimal creado en `Frontend/`.

1. Instalar dependencias:
```bash
cd Frontend
npm install
```

2. Ejecutar con proxy hacia el backend (usa `Backend` corriendo en http://localhost:5000):
```bash
npx ng serve --proxy-config proxy.conf.json --open
```

3. URL de desarrollo: `http://localhost:4200`

Notas:
- El proyecto es un scaffold minimal: si prefieres puedo generar el proyecto usando `ng new` y más configuraciones.
- El proxy `proxy.conf.json` redirige `/api` al backend para evitar problemas de CORS durante desarrollo.
