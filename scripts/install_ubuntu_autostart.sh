#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICE_DIR="${HOME}/.config/systemd/user"
SERVICE_FILE="${SERVICE_DIR}/ai-cabinet.service"
START_SCRIPT="${PROJECT_DIR}/scripts/start_ai_cabinet.sh"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl was not found. This installer is for Ubuntu/Linux with systemd." >&2
  exit 1
fi

mkdir -p "${SERVICE_DIR}"
chmod +x "${START_SCRIPT}"

cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=AI Cabinet Secure Microkernel Runtime
After=network-online.target

[Service]
Type=simple
WorkingDirectory=${PROJECT_DIR}
ExecStart=${START_SCRIPT}
Restart=always
RestartSec=5
Environment=AI_CABINET_HOST=127.0.0.1
Environment=AI_CABINET_PORT=8000

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable ai-cabinet.service
systemctl --user restart ai-cabinet.service

if command -v loginctl >/dev/null 2>&1; then
  loginctl enable-linger "${USER}" >/dev/null 2>&1 || true
fi

echo "AI Cabinet user service installed and started."
echo "Status:"
echo "  systemctl --user status ai-cabinet.service"
echo "Logs:"
echo "  journalctl --user -u ai-cabinet.service -f"
