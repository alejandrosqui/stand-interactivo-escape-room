#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

require_env
if [[ ! -s "$ROOT_DIR/.deploy/previous_tag" ]]; then
  echo "No hay una imagen anterior registrada para rollback." >&2
  exit 1
fi

previous_tag="$(<"$ROOT_DIR/.deploy/previous_tag")"
current_tag="$(<"$ROOT_DIR/.deploy/current_tag")"
export APP_IMAGE_TAG="$previous_tag"
"${COMPOSE[@]}" config --quiet
"${COMPOSE[@]}" up -d --no-build --remove-orphans --wait
printf '%s\n' "$previous_tag" > "$ROOT_DIR/.deploy/current_tag"
printf '%s\n' "$current_tag" > "$ROOT_DIR/.deploy/previous_tag"
"${COMPOSE[@]}" ps
echo "Rollback de aplicación completado: $previous_tag. La base de datos no fue alterada."
