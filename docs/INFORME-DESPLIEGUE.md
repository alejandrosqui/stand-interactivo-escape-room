# Informe de preparación de despliegue

Fecha: 2026-10-14

Repositorio: `alejandrosqui/stand-interactivo-escape-room`

Rama: `sprint-2`
Commit base inspeccionado: `16c7b2f`

## Resultado

Se preparó una configuración de producción para Ubuntu Server 24.04 sin ejecutar
ningún cambio sobre el servidor. El diseño publica solamente
`127.0.0.1:18080`, conserva FastAPI y PostgreSQL en una red Docker privada y usa
el Nginx existente del host como entrada para
`stand.patagoniasoftware.com.ar`.

El frontend consume la API same-origin mediante `/api`. Las rutas de participantes
y `/api/publico/*` continúan abiertas. `/admin` y los endpoints administrativos
quedan protegidos con Basic Auth en el Nginx del contenedor. El backend no publica un
puerto que permita evitar esa restricción.

PostgreSQL usa el volumen persistente
`stand_interactivo_postgres_data`. Los tres servicios tienen política
`restart: unless-stopped` y health checks.

**ESC03 continúa pendiente:** se conserva el ingreso manual de códigos; no se agregó
ni se declara implementado el escaneo mediante cámara.

## Archivos modificados

- `.gitignore`: excluye secretos, backups, cachés y estado local de despliegue.
- `README.md`: enlaza la guía de producción y explicita el estado de ESC03.
- `backend/.env.example`: documenta el origen CORS.
- `backend/app/main.py`: acepta una lista exacta de orígenes mediante
  `CORS_ORIGINS`, preservando el regex local de desarrollo.
- `frontend/.env.example`: usa `/api`.
- `frontend/src/api.ts`: usa `/api` como valor predeterminado same-origin.

## Archivos agregados

- `.dockerignore` y `backend/.dockerignore`.
- `.env.production.example`.
- `compose.prod.yml`.
- `backend/Dockerfile.prod`: backend no-root.
- `frontend/Dockerfile.prod`: build multietapa y runtime Nginx.
- `frontend/nginx/default.conf`: SPA, proxy de API, health y Basic Auth selectivo.
- `frontend/docker-entrypoint.d/40-admin-auth.sh`: genera el archivo htpasswd desde
  secretos de entorno.
- `deploy/nginx/stand.patagoniasoftware.com.ar.conf`: sitio aislado para el Nginx
  existente del host.
- `scripts/lib.sh`, `deploy.sh`, `update.sh`, `backup.sh` y `rollback.sh`.
- `docs/DESPLIEGUE-PRODUCCION.md`: DNS, despliegue, HTTPS, operación y verificación.

## Pruebas y verificaciones ejecutadas

- Backend: `python -m pytest -q tests` → **14 aprobadas en 9,80 s**.
- Frontend: `npm run lint` → **aprobado** (TypeScript sin errores).
- Frontend: `npm run build` → el typecheck terminó, pero Vite no pudo iniciar
  `esbuild` por `spawn EPERM` del entorno Windows. No informó errores del código.
- `git diff --check` → **sin errores**.
- `python -m compileall -q backend/app` → **sin errores**.
- Docker/Compose/Nginx: no ejecutables en este entorno; deben validarse en Ubuntu antes
  de habilitar el sitio.

`npm install` informó 3 vulnerabilidades del árbol de herramientas (1 moderada y 2
altas). El runtime de producción del frontend es Nginx y no incluye Node ni esas
dependencias, pero conviene planificar su actualización en una tarea separada para no
alterar Sprint 2 durante esta entrega.

## Comandos exactos de despliegue

No ejecutarlos hasta revisar la guía y los valores del servidor. Presuponen que estos
cambios ya fueron revisados, confirmados y publicados en la rama remota `sprint-2`;
esta preparación no hizo `push`:

```bash
sudo install -d -o "$USER" -g "$USER" /opt/stand-interactivo
git clone --branch sprint-2 --single-branch \
  https://github.com/alejandrosqui/stand-interactivo-escape-room.git \
  /opt/stand-interactivo
cd /opt/stand-interactivo
test "$(git branch --show-current)" = sprint-2
cp .env.production.example .env
chmod 600 .env
# Editar .env y reemplazar los secretos; usar, por ejemplo: openssl rand -hex 32

docker compose --env-file .env -f compose.prod.yml config --quiet
chmod +x scripts/*.sh
./scripts/deploy.sh
curl --fail http://127.0.0.1:18080/healthz
curl --fail http://127.0.0.1:18080/api/salud
curl -I http://127.0.0.1:18080/admin
```

La última llamada debe devolver `401`. Luego:

```bash
curl -u 'USUARIO:CLAVE' -I http://127.0.0.1:18080/admin
sudo cp deploy/nginx/stand.patagoniasoftware.com.ar.conf \
  /etc/nginx/sites-available/stand.patagoniasoftware.com.ar
sudo ln -s /etc/nginx/sites-available/stand.patagoniasoftware.com.ar \
  /etc/nginx/sites-enabled/stand.patagoniasoftware.com.ar
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d stand.patagoniasoftware.com.ar
sudo nginx -t
sudo systemctl reload nginx
sudo certbot renew --dry-run
```

Operación posterior:

```bash
cd /opt/stand-interactivo
BACKUP_DIR=/var/backups/stand-interactivo ./scripts/backup.sh
./scripts/update.sh
./scripts/rollback.sh
```

La guía completa incluye comprobación de DNS, puerto disponible, restauración,
diagnóstico y checklist funcional posterior.
