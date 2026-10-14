# Despliegue de producción — Ubuntu Server 24.04

Esta guía prepara `stand.patagoniasoftware.com.ar` sin modificar otros servicios del
servidor. Los comandos deben ejecutarse manualmente luego de revisar rutas, puertos y
la configuración Nginx existente. Esta entrega no ejecuta cambios en producción.

## Arquitectura

- El Nginx existente del host termina HTTP/HTTPS y reenvía al puerto exclusivo
  `127.0.0.1:18080`.
- El contenedor `web` sirve el build estático React/Vite y reenvía `/api` a FastAPI.
- FastAPI y PostgreSQL sólo están en la red interna de Compose; no publican puertos.
- PostgreSQL persiste en el volumen Docker `stand_interactivo_postgres_data`.
- `/admin` y toda API no pública requieren Basic Auth. `/api/publico/*`, las rutas de
  participantes y `/api/salud` permanecen públicas.

La aplicación admite ingreso manual de códigos QR. **ESC03 (escaneo mediante cámara)
continúa pendiente y no está implementada.**

## 1. Prerrequisitos y DNS

1. Crear un registro DNS `A` para `stand.patagoniasoftware.com.ar` con la IPv4 pública
   del servidor. Crear `AAAA` sólo si el servidor tiene IPv6 correctamente publicado.
2. Esperar propagación y verificar desde otra red:

   ```bash
   dig +short stand.patagoniasoftware.com.ar A
   ```

3. Confirmar Ubuntu 24.04, Docker Engine, el plugin Docker Compose, Git, Nginx y
   Certbot. No cambiar firewall ni configuraciones globales como parte de este proyecto.
4. Confirmar que `127.0.0.1:18080` esté libre:

   ```bash
   sudo ss -ltnp | grep ':18080' || true
   ```

Si está ocupado, elegir otro puerto sólo para este proyecto en `.env` y reflejarlo en
el `proxy_pass` del sitio Nginx.

## 2. Preparar el checkout

Estos comandos presuponen que los cambios de esta preparación ya fueron revisados,
confirmados y publicados en la rama remota `sprint-2`. Esta tarea no hace `push`.

Ejemplo de ruta aislada; puede adaptarse a la convención del servidor:

```bash
sudo install -d -o "$USER" -g "$USER" /opt/stand-interactivo
git clone --branch sprint-2 --single-branch \
  https://github.com/alejandrosqui/stand-interactivo-escape-room.git \
  /opt/stand-interactivo
cd /opt/stand-interactivo
test "$(git branch --show-current)" = sprint-2
cp .env.production.example .env
chmod 600 .env
```

Editar `.env` y reemplazar ambos valores `REEMPLAZAR_...`. Generar secretos distintos,
por ejemplo con `openssl rand -hex 32`. No confirmar `.env` en Git. El formato
hexadecimal evita caracteres que necesitarían codificación especial dentro de
`DATABASE_URL`.

## 3. Validar y levantar los contenedores

Antes del primer despliegue:

```bash
cd /opt/stand-interactivo
docker compose --env-file .env -f compose.prod.yml config --quiet
chmod +x scripts/*.sh
./scripts/deploy.sh
curl --fail http://127.0.0.1:18080/healthz
curl --fail http://127.0.0.1:18080/api/salud
curl -I http://127.0.0.1:18080/admin
```

La última llamada debe devolver `401` sin credenciales. Probar luego con
`curl -u 'usuario:clave' -I http://127.0.0.1:18080/admin` y esperar `200`.

## 4. Integrar con el Nginx existente

El archivo `deploy/nginx/stand.patagoniasoftware.com.ar.conf` es un sitio independiente.
Revisarlo primero; no reemplaza `nginx.conf` ni otros bloques `server`.

```bash
sudo cp deploy/nginx/stand.patagoniasoftware.com.ar.conf \
  /etc/nginx/sites-available/stand.patagoniasoftware.com.ar
sudo ln -s /etc/nginx/sites-available/stand.patagoniasoftware.com.ar \
  /etc/nginx/sites-enabled/stand.patagoniasoftware.com.ar
sudo nginx -t
sudo systemctl reload nginx
```

Si el servidor no usa `sites-available/sites-enabled`, adaptar únicamente la inclusión
del nuevo bloque según su estructura. No editar bloques de otros dominios.

## 5. HTTPS

Cuando el DNS ya resuelva al servidor y HTTP funcione:

```bash
sudo certbot --nginx -d stand.patagoniasoftware.com.ar
sudo nginx -t
sudo systemctl reload nginx
sudo certbot renew --dry-run
```

Certbot puede agregar la redirección HTTP→HTTPS al sitio. Revisar el diff del archivo
del sitio antes de recargar. La variable `CORS_ORIGINS` ya usa el origen HTTPS exacto;
las solicitudes normales son same-origin porque el frontend consume `/api`.

## Operación

### Actualizar desde `sprint-2`

```bash
cd /opt/stand-interactivo
./scripts/backup.sh
./scripts/update.sh
```

`update.sh` rechaza otra rama, exige un árbol limpio, sólo acepta avance fast-forward,
construye imágenes con el SHA del commit y espera health checks antes de finalizar.

### Backup

```bash
cd /opt/stand-interactivo
BACKUP_DIR=/var/backups/stand-interactivo ./scripts/backup.sh
```

El resultado es un `pg_dump` comprimido y verificado. Proteger esa carpeta con permisos
del operador y copiarla a almacenamiento externo siguiendo la política del servidor.
Probar restauraciones periódicamente en un entorno separado.

Restauración manual (destructiva, sólo después de confirmar archivo y destino):

```bash
gunzip -c /var/backups/stand-interactivo/ARCHIVO.sql.gz | \
  docker compose --env-file .env -f compose.prod.yml exec -T db \
  sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" "$POSTGRES_DB"'
```

### Rollback de aplicación

```bash
cd /opt/stand-interactivo
./scripts/rollback.sh
```

Esto vuelve a las imágenes del despliegue anterior y no modifica PostgreSQL. Si una
versión futura introduce migraciones incompatibles, el rollback de datos debe evaluarse
por separado y nunca automatizarse sin revisar el backup.

### Diagnóstico

```bash
docker compose --env-file .env -f compose.prod.yml ps
docker compose --env-file .env -f compose.prod.yml logs --tail=200 web backend db
curl --fail https://stand.patagoniasoftware.com.ar/api/salud
```

No usar `docker compose down -v`: `-v` elimina el volumen persistente de PostgreSQL.

## Verificación funcional posterior (manual)

1. Abrir la portada y una experiencia activa sin autenticación.
2. Iniciar y completar una partida, pedir una pista y comprobar el temporizador.
3. Confirmar que `/admin` pide credenciales y que credenciales incorrectas fallan.
4. Con credenciales válidas, crear/editar una experiencia y su secuencia.
5. Confirmar que el QR apunta a `https://stand.patagoniasoftware.com.ar/experiencia/...`.
6. Confirmar que la interfaz ofrece ingreso manual para desafíos QR; no registrar ESC03
   como aprobado porque el escaneo con cámara sigue pendiente.
