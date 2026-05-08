#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
PYTHON_BIN="${PYTHON_BIN:-}"

find_python() {
  if [[ -n "${PYTHON_BIN}" ]]; then
    printf '%s\n' "${PYTHON_BIN}"
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi

  return 1
}

if [[ ! -d "${BACKEND_DIR}" ]]; then
  echo "Backend directory not found: ${BACKEND_DIR}" >&2
  exit 1
fi

PYTHON_BIN="$(find_python || true)"
if [[ -z "${PYTHON_BIN}" ]]; then
  echo "Python is not installed. Install Python 3.11+ and rerun this script." >&2
  exit 1
fi

cd "${BACKEND_DIR}"

if [[ ! -d ".venv" ]]; then
  "${PYTHON_BIN}" -m venv .venv
fi

VENV_PYTHON="${BACKEND_DIR}/.venv/bin/python"
"${VENV_PYTHON}" -m pip install --upgrade pip
"${VENV_PYTHON}" -m pip install -r requirements.txt

if [[ ! -f ".env" && -f ".env.example" ]]; then
  cp ".env.example" ".env"
fi

mkdir -p "${PROJECT_DIR}/logs"
chmod +x "${PROJECT_DIR}/scripts/start_ai_cabinet.sh"

echo "AI Cabinet deployment is ready."
echo "Start manually:"
echo "  ${PROJECT_DIR}/scripts/start_ai_cabinet.sh"
echo "Open:"
echo "  http://127.0.0.1:8000"
