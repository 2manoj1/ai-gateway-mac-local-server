#!/usr/bin/env zsh
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

OLLAMA_RELEASE_VERSION="${OLLAMA_RELEASE_VERSION:-v0.30.6}"
OLLAMA_INSTALL_DIR="${OLLAMA_INSTALL_DIR:-$HOME/.local/ollama/$OLLAMA_RELEASE_VERSION}"
ARCHIVE_NAME="ollama-darwin.tgz"
RELEASE_BASE_URL="https://github.com/ollama/ollama/releases/download/$OLLAMA_RELEASE_VERSION"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

cd "$TMP_DIR"
curl -fsSLO "$RELEASE_BASE_URL/$ARCHIVE_NAME"
curl -fsSLO "$RELEASE_BASE_URL/sha256sum.txt"

expected_sha="$(
  awk -v name="$ARCHIVE_NAME" '
    {
      path = $2
      sub(/^\.\//, "", path)
      if (path == name) {
        print $1
      }
    }
  ' sha256sum.txt
)"
actual_sha="$(shasum -a 256 "$ARCHIVE_NAME" | awk '{print $1}')"

if [[ -z "$expected_sha" || "$expected_sha" != "$actual_sha" ]]; then
  echo "Checksum verification failed for $ARCHIVE_NAME" >&2
  exit 1
fi

mkdir -p "$OLLAMA_INSTALL_DIR"
tar -xzf "$ARCHIVE_NAME" -C "$OLLAMA_INSTALL_DIR"
chmod +x "$OLLAMA_INSTALL_DIR/ollama" \
  "$OLLAMA_INSTALL_DIR/llama-server" \
  "$OLLAMA_INSTALL_DIR/llama-quantize"

echo "Installed official Ollama $OLLAMA_RELEASE_VERSION to $OLLAMA_INSTALL_DIR"
echo "Binary: $OLLAMA_INSTALL_DIR/ollama"
