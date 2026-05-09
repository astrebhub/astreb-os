from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


ProviderName = Literal["auto", "openai", "gemini", "claude", "ollama", "deepseek", "mistral", "local", "manual"]
ModeName = Literal[
    "chat",
    "strategy",
    "content",
    "code",
    "legal_draft",
    "image_analysis",
    "file_review",
    "browser_action",
    "calendar_action",
    "github_ops",
    "voice_turn",
    "paperclip_task",
    "telegram_draft",
    "email_draft",
]
InputKind = Literal["text", "voice", "image", "file", "browser_action", "email", "calendar", "plugin_action"]
ActionStatus = Literal["draft", "pending_approval", "approved", "executed", "rejected", "rollback", "expired"]


class SubmitRequest(BaseModel):
    user_id: str = "owner"
    session_id: str = "default_session"
    agent_id: str = "default_agent"
    provider: ProviderName = "auto"
    mode: ModeName = "chat"
    input_type: InputKind = "text"
    task: str = Field(..., min_length=1)
    files: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    access_level: int = Field(default=3, ge=0, le=5)
    local_only: bool = False


class SubmitResponse(BaseModel):
    request_id: str
    result: str
    provider: str
    model: str
    risk_level: str
    data_class: str
    policy_applied: str
    tokens_estimated: int
    tokens_used: int
    cost_estimated: float
    cost_real: float
    action_id: Optional[str] = None
    action_status: Optional[str] = None
    memory_proposal_id: Optional[str] = None
    route_reason: str
    local_cloud_decision: str
    pii_detected: Dict[str, int]
    output_scan: Dict[str, Any]
    state: str
    normalized_input_type: str
