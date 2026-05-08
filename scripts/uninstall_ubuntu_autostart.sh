#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE_FILE="${HOME}/.config/systemd/user/ai-cabinet.service"

systemctl --user stop ai-cabinet.service >/dev/null 2>&1 || true
systemctl --user disable ai-cabinet.service >/dev/null 2>&1 || true
rm -f "${SERVICE_FILE}"
systemctl --user daemon-reload >/dev/null 2>&1 || true

echo "AI Cabinet Ubuntu autostart removed."
