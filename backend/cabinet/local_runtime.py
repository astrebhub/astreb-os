import os
from dataclasses import dataclass
from typing import Any, Dict, List

import httpx

from . import config


LOCAL_MODEL_FAMILIES = ["llama3", "mistral", "deepseek", "phi", "qwen-coder"]


@dataclass
class LocalModelStatus:
    provider: str
    model_name: str
    family: str
    device: str
    quantization: str
    loaded: bool
    available: bool


class LocalRuntimeManager:
    def __init__(self):
        self.ollama_base_url = config.OLLAMA_BASE_URL

    async def status(self) -> Dict[str, Any]:
        models = await self.list_ollama_models()
        return {
            "offline_capable": True,
            "local_only_mode": config.LOCAL_ONLY_MODE,
            "ollama_base_url": self.ollama_base_url,
            "supported_families": LOCAL_MODEL_FAMILIES,
            "runtime_targets": ["ollama", "gguf", "cpu", "gpu", "local_embeddings", "vector_search"],
            "ollama_models": models,
        }

    async def list_ollama_models(self) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code >= 400:
                return []
            return response.json().get("models", [])
        except Exception:
            return []

    async def load_model(self, model_name: str) -> Dict[str, Any]:
        return {
            "model": model_name,
            "status": "load_requested",
            "note": "Ollama loads models lazily on first generation; GGUF loader is reserved for native runtime.",
        }

    async def unload_model(self, model_name: str) -> Dict[str, Any]:
        return {
            "model": model_name,
            "status": "unload_requested",
            "note": "No destructive model process control is performed by the MVP runtime.",
        }

    def choose_local_model(self, task_type: str) -> str:
        if task_type == "code":
            return os.getenv("LOCAL_CODER_MODEL", "qwen2.5-coder:latest")
        if task_type in ["strategy", "legal_draft"]:
            return os.getenv("LOCAL_REASONING_MODEL", "deepseek-r1:latest")
        return os.getenv("LOCAL_GENERAL_MODEL", "llama3:latest")
