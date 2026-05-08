import json
import time
import uuid

from fastapi import HTTPException

from . import config
from .actions import ActionQueue
from .approval_center import ApprovalCenter
from .budget_governor import BudgetGovernor
from .classifier import DataClassifier
from .database import Database
from .evidence import EvidenceLayer
from .identity import IdentityAccessLayer
from .multimodal import MultimodalNormalizer
from .observability import ObservabilityLayer
from .output_guard import OutputGuard
from .pii import PiiDetector
from .plugin_sandbox import PluginSandbox
from .policy import PolicyEngine
from .providers import ProviderAdapter, build_provider_prompt
from .router import ModelRouter
from .schemas import SubmitRequest, SubmitResponse
from .state_engine import StateEngine
from .tokens import TokenCostEstimator
from .memory_engine import MemoryEngine


class CabinetPipeline:
    """Mandatory runtime order:
    INPUT -> MULTIMODAL NORMALIZER -> STATE ENGINE -> PII DETECTOR ->
    DATA CLASSIFIER -> POLICY ENGINE -> TOKEN / COST GOVERNOR ->
    MODEL / VOICE / TOOL ROUTER -> LOCAL OR CLOUD RUNTIME ->
    PLUGIN SANDBOX -> OUTPUT GUARD -> ACTION QUEUE -> APPROVAL CENTER ->
    AUDIT LOG -> MEMORY UPDATE PROPOSAL -> HUMAN APPROVAL IF REQUIRED
    """

    def __init__(
        self,
        database: Database,
        state: StateEngine,
        normalizer: MultimodalNormalizer,
        identity: IdentityAccessLayer,
        pii: PiiDetector,
        classifier: DataClassifier,
        policy: PolicyEngine,
        estimator: TokenCostEstimator,
        budget: BudgetGovernor,
        router: ModelRouter,
        provider: ProviderAdapter,
        plugin_sandbox: PluginSandbox,
        output_guard: OutputGuard,
        actions: ActionQueue,
        approvals: ApprovalCenter,
        evidence: EvidenceLayer,
        observability: ObservabilityLayer,
        memory_engine: MemoryEngine,
    ):
        self.database = database
        self.state = state
        self.normalizer = normalizer
        self.identity = identity
        self.pii = pii
        self.classifier = classifier
        self.policy = policy
        self.estimator = estimator
        self.budget = budget
        self.router = router
        self.provider = provider
        self.plugin_sandbox = plugin_sandbox
        self.output_guard = output_guard
        self.actions = actions
        self.approvals = approvals
        self.evidence = evidence
        self.observability = observability
        self.memory_engine = memory_engine

    async def run(self, req: SubmitRequest) -> SubmitResponse:
        request_id = str(uuid.uuid4())
        now = int(time.time())
        audit_base = {
            "id": str(uuid.uuid4()),
            "created_at": now,
            "request_id": request_id,
            "user_id": req.user_id,
            "status": "started",
        }
        started_at = time.time()

        try:
            self.state.transition(request_id, "received", {"input_type": req.input_type, "mode": req.mode})
            identity = self.identity.ensure_user(req.user_id, req.access_level)
            if not identity["allowed"]:
                raise HTTPException(status_code=403, detail="access_level_exceeds_role")

            normalized = self.normalizer.normalize(req)
            self.state.transition(
                request_id,
                "normalized",
                {"input_type": normalized.input_type, "modality_risk": normalized.modality_risk},
            )
            self.evidence.record_sources(request_id, req.sources)

            pii_result = self.pii.detect_and_mask(normalized.text)
            classification = self.classifier.classify(normalized.text, req.mode, pii_result)
            if normalized.modality_risk == "high":
                classification["risk_level"] = "high"
            self.state.transition(request_id, "classified", classification)
            policy = self.policy.evaluate(
                classification,
                pii_result.has_pii,
                req.access_level,
                req.local_only or config.LOCAL_ONLY_MODE,
            )
            if policy.blocked:
                raise HTTPException(status_code=403, detail=policy.reason)
            self.state.transition(request_id, "policy_checked", {"policy": policy.name})

            provider_input = pii_result.masked_text if policy.mask else normalized.text
            self.state.transition(request_id, "masked", {"masked": policy.mask, "pii": pii_result.counts})
            preliminary_route = self.router.route(
                req.provider,
                req.mode,
                classification["risk_level"],
                0.0,
                policy,
            )
            prompt = build_provider_prompt(provider_input, req.mode, policy.name, classification)
            estimate = self.estimator.evaluate(req.user_id, prompt, preliminary_route.model)
            if estimate.blocked:
                raise HTTPException(status_code=429, detail=estimate.reason)
            budget_decision = self.budget.evaluate(req.user_id, "default_agent", request_id, estimate.cost_estimated)
            if not budget_decision.allowed:
                raise HTTPException(status_code=429, detail=budget_decision.reason)
            self.state.transition(
                request_id,
                "budget_checked",
                {"tokens_estimated": estimate.tokens_estimated, "cost_estimated": estimate.cost_estimated},
            )

            route = self.router.route(
                req.provider,
                req.mode,
                classification["risk_level"],
                estimate.cost_estimated,
                policy,
            )
            local_cloud_decision = "local" if route.provider in ["local", "ollama", "manual"] else "cloud"
            self.state.transition(
                request_id,
                "routed",
                {"provider": route.provider, "model": route.model, "decision": local_cloud_decision},
            )
            provider_result = await self.provider.call(route.provider, route.model, prompt)
            self.state.transition(request_id, "executed", {"provider": route.provider, "model": provider_result.model})
            sandbox_manifests = self.plugin_sandbox.manifests()
            self.observability.event(
                "plugin_sandbox_checked",
                request_id,
                "info",
                {"manifests": len(sandbox_manifests), "mode": req.mode},
            )
            output_scan = self.output_guard.scan(provider_result.text, pii_result)
            self.state.transition(request_id, "scanned", output_scan)

            final_output = provider_result.text
            status = "completed"
            if not output_scan["passed"]:
                final_output = "[BLOCKED_OUTPUT_LEAKAGE] Output scanner detected possible sensitive data leakage."
                status = "blocked_output_scanner"

            action_state = self.actions.maybe_enqueue(
                request_id,
                req,
                classification["risk_level"],
                policy,
                final_output,
            )
            action_id = action_state["action_id"] if action_state else None
            if action_id:
                self.state.transition(request_id, "queued", {"action_id": action_id, "status": action_state["action_status"]})
                if policy.require_approval:
                    self.approvals.request(
                        "action",
                        action_id,
                        req.user_id,
                        "Action requires owner approval under current policy.",
                        {"policy": policy.name, "risk_level": classification["risk_level"]},
                    )

            self.database.insert_memory("user_masked", provider_input, {"id": str(uuid.uuid4()), "request_id": request_id})
            self.database.insert_memory("assistant", final_output, {"id": str(uuid.uuid4()), "request_id": request_id})
            self.database.insert_audit(
                {
                    **audit_base,
                    "risk_level": classification["risk_level"],
                    "data_class": classification["data_class"],
                    "policy": policy.name,
                    "tokens_estimated": estimate.tokens_estimated,
                    "tokens_used": provider_result.tokens_used,
                    "cost_estimated": estimate.cost_estimated,
                    "cost_real": provider_result.cost_real,
                    "provider": route.provider,
                    "model": provider_result.model,
                    "status": status,
                    "error": "",
                    "pii_summary": json.dumps(pii_result.counts),
                    "action_id": action_id,
                }
            )
            self.state.transition(request_id, "audited", {"status": status})
            memory_proposal = self.memory_engine.propose_learning_update(
                request_id,
                classification,
                route.reason,
                status,
            )
            if memory_proposal:
                self.state.transition(request_id, "memory_proposed", {"proposal_id": memory_proposal.id})
                self.approvals.request(
                    "memory_proposal",
                    memory_proposal.id,
                    req.user_id,
                    "Learning memory update requires human approval.",
                    {"layer": memory_proposal.layer},
                )
            self.budget.record(
                req.user_id,
                "default_agent",
                request_id,
                estimate.tokens_estimated,
                provider_result.tokens_used,
                estimate.cost_estimated,
                provider_result.cost_real,
                route.provider,
                provider_result.model,
                status,
            )
            self.state.transition(request_id, "completed", {"status": status})
            self.observability.event(
                "pipeline_completed",
                request_id,
                "info",
                {"provider": route.provider, "policy": policy.name, "budget_alert": budget_decision.alert},
                started_at,
            )

            return SubmitResponse(
                request_id=request_id,
                result=final_output,
                provider=route.provider,
                model=provider_result.model,
                risk_level=classification["risk_level"],
                data_class=classification["data_class"],
                policy_applied=policy.name,
                tokens_estimated=estimate.tokens_estimated,
                tokens_used=provider_result.tokens_used,
                cost_estimated=estimate.cost_estimated,
                cost_real=provider_result.cost_real,
                action_id=action_id,
                action_status=action_state["action_status"] if action_state else None,
                memory_proposal_id=memory_proposal.id if memory_proposal else None,
                route_reason=route.reason,
                local_cloud_decision=local_cloud_decision,
                pii_detected=pii_result.counts,
                output_scan=output_scan,
                state="completed",
                normalized_input_type=normalized.input_type,
            )
        except HTTPException as exc:
            self.state.transition(request_id, "failed", {"error": str(exc.detail)})
            self.observability.event("pipeline_blocked", request_id, "warning", {"error": str(exc.detail)}, started_at)
            self.database.insert_audit(
                {
                    **audit_base,
                    "risk_level": "",
                    "data_class": "",
                    "policy": "",
                    "tokens_estimated": 0,
                    "tokens_used": 0,
                    "cost_estimated": 0.0,
                    "cost_real": 0.0,
                    "provider": "",
                    "model": "",
                    "status": "blocked",
                    "error": str(exc.detail),
                    "pii_summary": "{}",
                    "action_id": None,
                }
            )
            raise
        except Exception as exc:
            self.state.transition(request_id, "failed", {"error": str(exc)})
            self.observability.event("pipeline_error", request_id, "error", {"error": str(exc)}, started_at)
            self.database.insert_audit(
                {
                    **audit_base,
                    "risk_level": "",
                    "data_class": "",
                    "policy": "",
                    "tokens_estimated": 0,
                    "tokens_used": 0,
                    "cost_estimated": 0.0,
                    "cost_real": 0.0,
                    "provider": "",
                    "model": "",
                    "status": "error",
                    "error": str(exc),
                    "pii_summary": "{}",
                    "action_id": None,
                }
            )
            raise HTTPException(status_code=500, detail="AI Cabinet runtime error")
