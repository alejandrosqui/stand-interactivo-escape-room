#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

require_sprint_2
require_env
require_clean_tree

mkdir -p "$ROOT_DIR/.deploy"
new_tag="$(git -C "$ROOT_DIR" rev-parse --short=12 HEAD)"
if [[ -f "$ROOT_DIR/.deploy/current_tag" ]]; then
  cp "$ROOT_DIR/.deploy/current_tag" "$ROOT_DIR/.deploy/previous_tag"
fi

export APP_IMAGE_TAG="$new_tag"
"${COMPOSE[@]}" config --quiet
"${COMPOSE[@]}" build --pull
"${COMPOSE[@]}" up -d --remove-orphans --wait
printf '%s\n' "$new_tag" > "$ROOT_DIR/.deploy/current_tag"
"${COMPOSE[@]}" ps
echo "Despliegue listo en 127.0.0.1:${APP_PORT:-18080} (imagen $new_tag)."
