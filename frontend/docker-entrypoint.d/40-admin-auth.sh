#!/bin/sh
set -eu

if [ -z "${ADMIN_USER:-}" ] || [ -z "${ADMIN_PASSWORD:-}" ]; then
  echo "ADMIN_USER y ADMIN_PASSWORD son obligatorios" >&2
  exit 1
fi

htpasswd -bc /etc/nginx/.htpasswd "$ADMIN_USER" "$ADMIN_PASSWORD"
chmod 600 /etc/nginx/.htpasswd
