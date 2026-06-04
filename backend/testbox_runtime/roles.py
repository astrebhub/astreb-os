from __future__ import annotations

from .models import OrientationDecision, OperationalRole, RuntimeRoleAssignment


CORE_ROLES = [
    OperationalRole(
        id="orientation_architect",
        name="Orientation Architect",
        purpose="Understand intent, context, domains, and the next governed step.",
        skills=[
            "Intent Detection",
            "Context Reuse",
            "Conversation Orientation",
            "Multi-Domain Mapping",
            "Strategic Guidance",
            "Follow-up Resolution",
            "Human-friendly Explanation",
            "Jurisdiction Inference",
        ],
        constraints=["No deep legal advice"],
    ),
    OperationalRole(
        id="legalbox_specialist",
        name="LegalBox Specialist",
        purpose="Provide source-bound governed legal orientation.",
        skills=[
            "Legal Retrieval",
            "Legal Citation",
            "Jurisdiction Detection",
            "Risk Classification",
            "Disclaimer Injection",
            "Human Review Escalation",
            "Employment Law Orientation",
            "Business Law Orientation",
            "Traffic Liability Orientation",
            "Housing Orientation",
        ],
        constraints=["No final legal advice", "No guarantees", "No court strategy"],
    ),
    OperationalRole(
        id="businessbox_strategist",
        name="BusinessBox Strategist",
        purpose="Structure business formation and regulated activity orientation.",
        skills=[
            "Business Formation Mapping",
            "Entity Comparison",
            "Regulatory Orientation",
            "Market Entry Structuring",
            "Operational Planning",
            "Investment Readiness",
            "Industry Classification",
            "EU Compliance Orientation",
            "Manufacturing Orientation",
        ],
    ),
    OperationalRole(
        id="documentbox_analyst",
        name="DocumentBox Analyst",
        purpose="Review documents and attachments for obligations and risk.",
        skills=[
            "Contract Review",
            "Deadline Detection",
            "Risk Highlighting",
            "Obligation Extraction",
            "Payment Term Analysis",
            "OCR Coordination",
            "Attachment Classification",
            "Sensitive Data Detection",
            "Clause Extraction",
        ],
    ),
    OperationalRole(
        id="letterbox_composer",
        name="LetterBox Composer",
        purpose="Prepare controlled drafts without external execution.",
        skills=[
            "Formal Letter Drafting",
            "Complaint Drafting",
            "Legal-safe Language",
            "Tone Selection",
            "Translation Support",
            "Follow-up Drafting",
            "Negotiation Framing",
        ],
        constraints=["No auto-send", "No external execution"],
    ),
    OperationalRole(
        id="asti_action_supervisor",
        name="ASTI Action Supervisor",
        purpose="Control queued external actions through approval and execution.",
        skills=[
            "Action Queue Management",
            "Approval Enforcement",
            "Executor Selection",
            "External Action Validation",
            "Audit Binding",
            "Permission Verification",
            "Dry-run Validation",
            "Rollback Awareness",
        ],
        constraints=["External execution requires create, approve, execute, audit"],
    ),
    OperationalRole(
        id="governance_officer",
        name="Governance Officer",
        purpose="Enforce policies, risk controls, privacy, and review requirements.",
        skills=[
            "Policy Enforcement",
            "Safety Review",
            "PII Governance",
            "Compliance Checking",
            "Risk Escalation",
            "Human Review Triggering",
            "Audit Integrity Verification",
        ],
    ),
    OperationalRole(
        id="audit_narrator",
        name="Audit Narrator",
        purpose="Translate runtime decisions into human-readable explanation.",
        skills=[
            "Routing Explanation",
            "Governance Narration",
            "Audit Translation",
            "Human-readable Explainability",
            "Runtime Observation",
        ],
    ),
    OperationalRole(
        id="memory_coordinator",
        name="Memory Coordinator",
        purpose="Maintain bounded session and conversation continuity.",
        skills=[
            "Session State",
            "Topic Persistence",
            "Context Reuse",
            "Follow-up Linking",
            "Multi-turn Resolution",
            "Conversation Continuity",
        ],
    ),
    OperationalRole(
        id="runtime_orchestrator",
        name="Runtime Orchestrator",
        purpose="Coordinate backend routing, mode switching, state, and queues.",
        skills=[
            "Event Routing",
            "Mode Switching",
            "Agent Coordination",
            "Workflow State",
            "Queue Coordination",
            "Retry Logic",
            "Failure Recovery",
            "Runtime Observability",
        ],
        constraints=["Backend runtime role, not a user-facing chat persona"],
    ),
]

ROLE_BY_ID = {role.id: role for role in CORE_ROLES}

MODE_ROLE_MAP = {
    "LegalBox Mode": "legalbox_specialist",
    "BusinessBox Mode": "businessbox_strategist",
    "DocumentBox Mode": "documentbox_analyst",
    "LetterBox Mode": "letterbox_composer",
    "ASTI Action Mode": "asti_action_supervisor",
    "Human Review Mode": "businessbox_strategist",
}


def role_assignment_for(orientation: OrientationDecision) -> RuntimeRoleAssignment:
    role_ids = [
        "orientation_architect",
        "runtime_orchestrator",
        "governance_officer",
        "audit_narrator",
        "memory_coordinator",
    ]
    specialised_role = MODE_ROLE_MAP.get(orientation.mode)
    if specialised_role:
        role_ids.insert(1, specialised_role)
    roles = [ROLE_BY_ID[role_id].name for role_id in role_ids]
    primary = ROLE_BY_ID[specialised_role].name if specialised_role else roles[0]
    return RuntimeRoleAssignment(
        primary_role=primary,
        active_roles=roles,
        reason=f"{orientation.mode} selected for route {orientation.route_key}",
    )
