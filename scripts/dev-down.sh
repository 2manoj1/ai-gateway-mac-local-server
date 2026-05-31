#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../infra"

podman compose -f compose.dev.yaml --env-file .env.dev down
