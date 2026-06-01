#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../infra"

if [[ ! -f .env.dev ]]; then
  cp .env.dev.example .env.dev
fi

podman compose -p ai-gateway-dev -f compose.dev.yaml --env-file .env.dev down
