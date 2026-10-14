#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

require_env
backup_dir="${BACKUP_DIR:-$ROOT_DIR/backups}"
mkdir -p "$backup_dir"
umask 077
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="$backup_dir/stand_interactivo_${stamp}.sql.gz"

"${COMPOSE[@]}" exec -T db sh -c 'pg_dump --clean --if-exists --no-owner --no-privileges -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip -9 > "$target"
gzip -t "$target"
echo "Backup verificado: $target"
