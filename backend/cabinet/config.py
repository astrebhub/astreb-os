import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT_DIR / "config"
FRONTEND_DIR = ROOT_DIR / "frontend"
DB_PATH = str(BACKEND_DIR / "ai_cabinet.db")


def getenv_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def getenv_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


APP_NAME = os.getenv("APP_NAME", "AI CABINET v0.2")
TOKEN_LIMIT_PER_REQUEST = getenv_int("TOKEN_LIMIT_PER_REQUEST", 8000)
DAILY_COST_LIMIT = getenv_float("DAILY_COST_LIMIT", 5.0)
DAILY_TOKEN_LIMIT_PER_USER = getenv_int("DAILY_TOKEN_LIMIT_PER_USER", 50000)
SESSION_COST_LIMIT = getenv_float("SESSION_COST_LIMIT", 1.0)
MONTHLY_COST_LIMIT = getenv_float("MONTHLY_COST_LIMIT", 100.0)
EMERGENCY_STOP = os.getenv("EMERGENCY_STOP", "false").lower() == "true"
LOCAL_ONLY_MODE = os.getenv("LOCAL_ONLY_MODE", "false").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")


def load_yaml(name: str) -> Dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
