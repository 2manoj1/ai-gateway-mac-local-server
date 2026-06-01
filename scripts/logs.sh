#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE="${COMPOSE:-podman compose}"

cd "$ROOT_DIR/infra"
${COMPOSE} --env-file .env -f compose.yaml logs -f "$@"
