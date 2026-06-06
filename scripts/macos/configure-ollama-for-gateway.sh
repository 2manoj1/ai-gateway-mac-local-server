#!/usr/bin/env zsh
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO_DIR="${AI_GATEWAY_REPO_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
INFRA_ENV_FILE="${AI_GATEWAY_INFRA_ENV:-$REPO_DIR/infra/.env}"
PLIST="$HOME/Library/LaunchAgents/homebrew.mxcl.ollama.plist"
USER_DOMAIN="gui/$(id -u)"
OLLAMA_RELEASE_VERSION="${OLLAMA_RELEASE_VERSION:-v0.30.6}"
OLLAMA_INSTALL_DIR="${OLLAMA_INSTALL_DIR:-$HOME/.local/ollama/$OLLAMA_RELEASE_VERSION}"
OLLAMA_BIN="${OLLAMA_BIN:-$OLLAMA_INSTALL_DIR/ollama}"

read_env_value() {
  local key="$1"
  local file="$2"

  if [[ -f "$file" ]]; then
    awk -F= -v key="$key" '$1 == key {print $2}' "$file" | tail -n 1
  fi
}

MODEL="${OLLAMA_MODEL:-$(read_env_value DEFAULT_MODEL "$INFRA_ENV_FILE")}"
MODEL="${MODEL:-qwen3.5:9b}"

OLLAMA_KEEP_ALIVE_VALUE="${OLLAMA_KEEP_ALIVE:--1}"
OLLAMA_NUM_PARALLEL_VALUE="${OLLAMA_NUM_PARALLEL:-10}"
OLLAMA_MAX_QUEUE_VALUE="${OLLAMA_MAX_QUEUE:-10}"
OLLAMA_MAX_LOADED_MODELS_VALUE="${OLLAMA_MAX_LOADED_MODELS:-1}"
OLLAMA_CONTEXT_LENGTH_VALUE="${OLLAMA_CONTEXT_LENGTH:-4096}"
OLLAMA_FLASH_ATTENTION_VALUE="${OLLAMA_FLASH_ATTENTION:-1}"
OLLAMA_KV_CACHE_TYPE_VALUE="${OLLAMA_KV_CACHE_TYPE:-q8_0}"
OLLAMA_KEEP_ALIVE_JSON="\"$OLLAMA_KEEP_ALIVE_VALUE\""

if [[ "$OLLAMA_KEEP_ALIVE_VALUE" =~ '^-?[0-9]+$' ]]; then
  OLLAMA_KEEP_ALIVE_JSON="$OLLAMA_KEEP_ALIVE_VALUE"
fi

if [[ ! -x "$OLLAMA_BIN" ]]; then
  OLLAMA_BIN="$(command -v ollama || true)"
fi

if [[ -z "$OLLAMA_BIN" || ! -x "$OLLAMA_BIN" ]]; then
  echo "ollama is not installed or is not on PATH" >&2
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required because this machine runs Ollama as a brew service" >&2
  exit 1
fi

if [[ ! -f "$PLIST" ]]; then
  brew services start ollama >/dev/null
fi

if [[ ! -f "$PLIST" ]]; then
  echo "Could not find $PLIST after starting the Homebrew Ollama service" >&2
  exit 1
fi

set_plist_env() {
  local key="$1"
  local value="$2"

  /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables dict" "$PLIST" \
    >/dev/null 2>&1 || true

  if /usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:$key" "$PLIST" \
    >/dev/null 2>&1; then
    /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:$key $value" "$PLIST"
  else
    /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables:$key string $value" \
      "$PLIST"
  fi
}

set_plist_env OLLAMA_KEEP_ALIVE "$OLLAMA_KEEP_ALIVE_VALUE"
set_plist_env OLLAMA_NUM_PARALLEL "$OLLAMA_NUM_PARALLEL_VALUE"
set_plist_env OLLAMA_MAX_QUEUE "$OLLAMA_MAX_QUEUE_VALUE"
set_plist_env OLLAMA_MAX_LOADED_MODELS "$OLLAMA_MAX_LOADED_MODELS_VALUE"
set_plist_env OLLAMA_CONTEXT_LENGTH "$OLLAMA_CONTEXT_LENGTH_VALUE"
set_plist_env OLLAMA_FLASH_ATTENTION "$OLLAMA_FLASH_ATTENTION_VALUE"
set_plist_env OLLAMA_KV_CACHE_TYPE "$OLLAMA_KV_CACHE_TYPE_VALUE"

/usr/libexec/PlistBuddy -c "Set :ProgramArguments:0 $OLLAMA_BIN" "$PLIST"
if /usr/libexec/PlistBuddy -c "Print :ProgramArguments:1" "$PLIST" \
  >/dev/null 2>&1; then
  /usr/libexec/PlistBuddy -c "Set :ProgramArguments:1 serve" "$PLIST"
else
  /usr/libexec/PlistBuddy -c "Add :ProgramArguments:1 string serve" "$PLIST"
fi

launchctl bootout "$USER_DOMAIN" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "$USER_DOMAIN" "$PLIST"
launchctl enable "$USER_DOMAIN/homebrew.mxcl.ollama"
launchctl kickstart -k "$USER_DOMAIN/homebrew.mxcl.ollama" >/dev/null 2>&1 || true

for _ in {1..30}; do
  if curl -fsS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

curl -fsS http://127.0.0.1:11434/api/version >/dev/null
"$OLLAMA_BIN" pull "$MODEL"
curl -fsS http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"keep_alive\":$OLLAMA_KEEP_ALIVE_JSON}" \
  >/dev/null

echo "Ollama configured for gateway chat concurrency."
echo "Binary: $OLLAMA_BIN"
echo "Model: $MODEL"
"$OLLAMA_BIN" ps
