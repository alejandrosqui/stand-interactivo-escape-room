#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE=(docker compose --project-directory "$ROOT_DIR" --env-file "$ROOT_DIR/.env" -f "$ROOT_DIR/compose.prod.yml")

require_sprint_2() {
  local branch
  branch="$(git -C "$ROOT_DIR" branch --show-current)"
  if [[ "$branch" != "sprint-2" ]]; then
    echo "Rama incorrecta: '$branch'. Se requiere sprint-2." >&2
    exit 1
  fi
}

require_env() {
  if [[ ! -f "$ROOT_DIR/.env" ]]; then
    echo "Falta $ROOT_DIR/.env. Copie .env.production.example y complete sus secretos." >&2
    exit 1
  fi
}

require_clean_tree() {
  if [[ -n "$(git -C "$ROOT_DIR" status --porcelain)" ]]; then
    echo "El árbol de trabajo tiene cambios sin confirmar; se cancela el despliegue." >&2
    exit 1
  fi
}
