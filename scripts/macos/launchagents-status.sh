#!/usr/bin/env zsh
set -euo pipefail

for label in \
  com.manoj.ai-gateway-stack \
  com.manoj.ai-gateway-tunnel \
  com.manoj.caffeinate
do
  echo "== $label =="
  launchctl print "gui/$(id -u)/$label" 2>/dev/null | sed -n "1,35p" || echo "not loaded"
  echo
done
