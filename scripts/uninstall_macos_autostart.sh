#!/usr/bin/env bash
set -Eeuo pipefail

PLIST_FILE="${HOME}/Library/LaunchAgents/nl.jazekker.ai-cabinet.plist"

launchctl bootout "gui/$(id -u)" "${PLIST_FILE}" >/dev/null 2>&1 || true
rm -f "${PLIST_FILE}"

echo "AI Cabinet macOS autostart removed."
