#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/autostart.log"
HOST="${AI_CABINET_HOST:-127.0.0.1}"
PORT="${AI_CABINET_PORT:-8000}"

mkdir -p "${LOG_DIR}"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "${LOG_FILE}"
}

find_python() {
  if [[ -x "${BACKEND_DIR}/.venv/bin/python" ]]; then
    printf '%s\n' "${BACKEND_DIR}/.venv/bin/python"
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
  log "Backend directory not found: ${BACKEND_DIR}"
  exit 1
fi

if [[ ! -f "${BACKEND_DIR}/.env" && -f "${BACKEND_DIR}/.env.example" ]]; then
  cp "${BACKEND_DIR}/.env.example" "${BACKEND_DIR}/.env"
  log "Created backend/.env from backend/.env.example"
fi

PYTHON_BIN="$(find_python || true)"
if [[ -z "${PYTHON_BIN}" ]]; then
  log "Python is not installed or not available in PATH. Install Python 3.11+ first."
  exit 1
fi

if [[ ! -d "${BACKEND_DIR}/.venv" ]]; then
  log "Creating virtual environment in backend/.venv"
  "${PYTHON_BIN}" -m venv "${BACKEND_DIR}/.venv"
  PYTHON_BIN="${BACKEND_DIR}/.venv/bin/python"
fi

if ! "${PYTHON_BIN}" -m pip show fastapi >/dev/null 2>&1; then
  log "Installing backend dependencies from backend/requirements.txt"
  "${PYTHON_BIN}" -m pip install --upgrade pip
  "${PYTHON_BIN}" -m pip install -r "${BACKEND_DIR}/requirements.txt"
fi

log "Starting AI Cabinet at http://${HOST}:${PORT}"
cd "${BACKEND_DIR}"
exec "${PYTHON_BIN}" -m uvicorn main:app --host "${HOST}" --port "${PORT}"
