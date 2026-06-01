#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR/infra"

if [[ -z "${COMPOSE:-}" ]]; then
  if command -v podman >/dev/null 2>&1; then
    COMPOSE=(podman compose)
  elif command -v docker >/dev/null 2>&1; then
    COMPOSE=(docker compose)
  else
    echo "ERROR: Neither podman nor docker was found. Install one or set COMPOSE." >&2
    exit 1
  fi
else
  IFS=' ' read -r -a COMPOSE <<< "$COMPOSE"
fi

"${COMPOSE[@]}" up -d --build --force-recreate
