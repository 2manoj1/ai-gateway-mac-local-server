#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR/infra"

if [[ ! -f .env.dev ]]; then
  cp .env.dev.example .env.dev
fi

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

"${COMPOSE[@]}" -p ai-gateway-dev -f compose.dev.yaml --env-file .env.dev up -d --build
