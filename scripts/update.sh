#!/usr/bin/env bash
set -Eeuo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/lib.sh"

require_sprint_2
require_env
require_clean_tree
git -C "$ROOT_DIR" fetch origin sprint-2
git -C "$ROOT_DIR" merge --ff-only origin/sprint-2
exec "$script_dir/deploy.sh"
