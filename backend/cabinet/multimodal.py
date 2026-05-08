from dataclasses import dataclass
from typing import Any, Dict, List

from .schemas import SubmitRequest


@dataclass
class NormalizedTask:
    input_type: str
    text: str
    artifacts: List[Dict[str, Any]]
    modality_risk: str


class MultimodalNormalizer:
    def normalize(self, req: SubmitRequest) -> NormalizedTask:
        artifacts = []
        text = req.task.strip()
        modality_risk = "low"

        if req.input_type == "voice":
            text = f"[VOICE_TRANSCRIPT]\n{text}"
            modality_risk = "medium"
        elif req.input_type == "image":
            text = f"[IMAGE_TASK]\n{text}\nImage artifacts: {len(req.files)}"
            artifacts = req.files
            modality_risk = "medium"
        elif req.input_type == "file":
            text = f"[FILE_TASK]\n{text}\nFile artifacts: {len(req.files)}"
            artifacts = req.files
            modality_risk = "medium"
        elif req.input_type in ["browser_action", "plugin_action", "email", "calendar"]:
            text = f"[ACTION_INTENT:{req.input_type}]\n{text}"
            artifacts = req.files
            modality_risk = "high"

        return NormalizedTask(
            input_type=req.input_type,
            text=text,
            artifacts=artifacts,
            modality_risk=modality_risk,
        )
