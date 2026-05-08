import time
import uuid
from dataclasses import dataclass
from typing import Dict, Optional

from .database import Database


MEMORY_LAYERS = [
    "constitution",
    "role_instruction",
    "policy",
    "project",
    "operational",
    "learning",
    "audit",
]

IMMUTABLE_LAYERS = {"constitution", "role_instruction", "policy", "audit"}


@dataclass
class MemoryProposal:
    id: str
    layer: str
    status: str


class MemoryEngine:
    def __init__(self, database: Database):
        self.database = database

    def propose_learning_update(
        self,
        request_id: str,
        classification: Dict[str, str],
        route_reason: str,
        output_status: str,
    ) -> Optional[MemoryProposal]:
        if output_status not in ["completed", "blocked_output_scanner"]:
            return None

        observation = (
            f"Task classified as {classification['data_class']} / {classification['risk_level']} "
            f"and routed because {route_reason}."
        )
        hypothesis = "Routing and policy behavior can be improved by tracking repeated classifications."
        proposal = (
            "Learning observation: preserve this routing/policy outcome as optimization evidence. "
            "This does not change policy, role instructions, or constitution memory."
        )
        proposal_id = str(uuid.uuid4())
        self.database.insert_memory_proposal(
            {
                "id": proposal_id,
                "created_at": int(time.time()),
                "request_id": request_id,
                "layer": "learning",
                "observation": observation,
                "hypothesis": hypothesis,
                "proposal": proposal,
                "status": "pending_approval",
                "approval_note": "Learning flow requires human approval.",
            }
        )
        return MemoryProposal(id=proposal_id, layer="learning", status="pending_approval")

    def approve_proposal(self, proposal_id: str) -> Optional[Dict[str, str]]:
        row = self.database.update_memory_proposal_status(
            proposal_id,
            "approved",
            "Approved by owner and written to governed learning memory.",
        )
        if not row:
            return None
        return {"id": proposal_id, "status": "approved"}

    def reject_proposal(self, proposal_id: str) -> Optional[Dict[str, str]]:
        row = self.database.update_memory_proposal_status(proposal_id, "rejected", "Rejected by owner.")
        if not row:
            return None
        return {"id": proposal_id, "status": "rejected"}
