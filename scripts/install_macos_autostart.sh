#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLIST_DIR="${HOME}/Library/LaunchAgents"
PLIST_FILE="${PLIST_DIR}/nl.jazekker.ai-cabinet.plist"
START_SCRIPT="${PROJECT_DIR}/scripts/start_ai_cabinet.sh"
LOG_DIR="${PROJECT_DIR}/logs"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS launchd." >&2
  exit 1
fi

mkdir -p "${PLIST_DIR}" "${LOG_DIR}"
chmod +x "${START_SCRIPT}"

cat > "${PLIST_FILE}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>nl.jazekker.ai-cabinet</string>
  <key>ProgramArguments</key>
  <array>
    <string>${START_SCRIPT}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${PROJECT_DIR}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>AI_CABINET_HOST</key>
    <string>127.0.0.1</string>
    <key>AI_CABINET_PORT</key>
    <string>8000</string>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/launchd.err.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "${PLIST_FILE}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "${PLIST_FILE}"
launchctl enable "gui/$(id -u)/nl.jazekker.ai-cabinet"
launchctl kickstart -k "gui/$(id -u)/nl.jazekker.ai-cabinet"

echo "AI Cabinet macOS LaunchAgent installed and started."
echo "Status:"
echo "  launchctl print gui/$(id -u)/nl.jazekker.ai-cabinet"
echo "Logs:"
echo "  tail -f ${LOG_DIR}/launchd.out.log ${LOG_DIR}/launchd.err.log"
