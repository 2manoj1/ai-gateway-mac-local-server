#!/usr/bin/env zsh
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO_DIR="${AI_GATEWAY_REPO_DIR:-/Users/apple/Documents/projects/ai-home-lab/ai-gateway}"
LOG_DIR="${AI_GATEWAY_LOG_DIR:-$HOME/Library/Logs/ai-gateway}"
COMPOSE_COMMAND="${AI_GATEWAY_COMPOSE_COMMAND:-}"

mkdir -p "$LOG_DIR"

if [[ -z "$COMPOSE_COMMAND" ]]; then
  if command -v podman >/dev/null 2>&1; then
    COMPOSE_COMMAND="podman compose"
  elif command -v docker >/dev/null 2>&1; then
    COMPOSE_COMMAND="docker compose"
  else
    echo "ERROR: Neither podman nor docker was found. Install one or set AI_GATEWAY_COMPOSE_COMMAND." >&2
    exit 1
  fi
fi

if command -v podman >/dev/null 2>&1; then
  if podman machine list --format "{{.Running}}" 2>/dev/null | grep -q "false"; then
    podman machine start
  fi
fi

cd "$REPO_DIR/infra"

${=COMPOSE_COMMAND} up -d --build --force-recreate
