#!/usr/bin/env zsh
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO_DIR="${AI_GATEWAY_REPO_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$HOME/Library/Logs/ai-gateway"
APP_SUPPORT_DIR="$HOME/Library/Application Support/ai-gateway"
TUNNEL_ID="${CLOUDFLARED_TUNNEL_ID:-}"

mkdir -p "$LAUNCH_AGENTS_DIR" "$LOG_DIR" "$APP_SUPPORT_DIR"
install -m 0755 "$REPO_DIR/scripts/macos/start-ai-gateway-stack.sh" "$APP_SUPPORT_DIR/start-ai-gateway-stack.sh"

if [[ -z "$TUNNEL_ID" ]]; then
  EXISTING_TUNNEL_PLIST="$LAUNCH_AGENTS_DIR/com.manoj.ai-gateway-tunnel.plist"
  if [[ -f "$EXISTING_TUNNEL_PLIST" ]]; then
    TUNNEL_ID="$(/usr/libexec/PlistBuddy -c "Print :ProgramArguments:3" "$EXISTING_TUNNEL_PLIST" 2>/dev/null || true)"
  fi
fi

cat >"$LAUNCH_AGENTS_DIR/com.manoj.ai-gateway-stack.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.manoj.ai-gateway-stack</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>${APP_SUPPORT_DIR}/start-ai-gateway-stack.sh</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>300</integer>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/ai-gateway-stack.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/ai-gateway-stack.err.log</string>
</dict>
</plist>
PLIST

cat >"$LAUNCH_AGENTS_DIR/com.manoj.caffeinate.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.manoj.caffeinate</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/caffeinate</string>
    <string>-dimsu</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/caffeinate.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/caffeinate.err.log</string>
</dict>
</plist>
PLIST

if [[ -n "$TUNNEL_ID" ]]; then
  cat >"$LAUNCH_AGENTS_DIR/com.manoj.ai-gateway-tunnel.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.manoj.ai-gateway-tunnel</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/bin/cloudflared</string>
    <string>tunnel</string>
    <string>run</string>
    <string>${TUNNEL_ID}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key>
    <false/>
  </dict>
  <key>ThrottleInterval</key>
  <integer>5</integer>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/cloudflared.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/cloudflared.err.log</string>
</dict>
</plist>
PLIST
else
  echo "Skipping com.manoj.ai-gateway-tunnel: set CLOUDFLARED_TUNNEL_ID or keep an existing tunnel plist." >&2
fi

load_agent() {
  local label="$1"
  local plist="$2"

  launchctl bootout "gui/$(id -u)" "$plist" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "$plist"
  launchctl enable "gui/$(id -u)/$label"
  launchctl kickstart -k "gui/$(id -u)/$label" >/dev/null 2>&1 || true
}

load_agent "com.manoj.ai-gateway-stack" "$LAUNCH_AGENTS_DIR/com.manoj.ai-gateway-stack.plist"
load_agent "com.manoj.caffeinate" "$LAUNCH_AGENTS_DIR/com.manoj.caffeinate.plist"

if [[ -n "$TUNNEL_ID" ]]; then
  load_agent "com.manoj.ai-gateway-tunnel" "$LAUNCH_AGENTS_DIR/com.manoj.ai-gateway-tunnel.plist"
fi

echo "Installed LaunchAgents in $LAUNCH_AGENTS_DIR"
echo "Logs are written to $LOG_DIR"
