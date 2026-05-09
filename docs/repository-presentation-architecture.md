# Astreb OS Repository Presentation Architecture

## Product-Grade Technical Narrative

Astreb OS is a governed hybrid AI operating system for controlled AI execution across local and cloud intelligence.

It is not positioned as a chatbot, prompt interface, automation script, or model wrapper. It is a runtime governance layer: a microkernel architecture that turns AI work into classified, routed, policy-bound, auditable, approval-aware execution.

The repository should present Astreb OS as an executable control system for organizations that need AI capability without losing operational authority.

## Repository Positioning

### Primary Definition

Astreb OS is a governed AI execution microkernel.

It coordinates:

- input normalization,
- risk and data classification,
- policy enforcement,
- model and tool routing,
- local/cloud execution decisions,
- approval gates,
- audit records,
- governed memory,
- agent boundaries,
- plugin and connector control.

### One-Line Repository Description

Governed hybrid AI operating system for policy-bound, auditable, local-first AI execution.

### Short Repository Description

Astreb OS routes AI tasks through classification, policy, model routing, approval queues, audit logs, and governed memory before execution. It is designed for teams building AI infrastructure where control, privacy, traceability, and human authority matter.

## Presentation Architecture

The repository should tell the story in five layers:

1. What problem Astreb OS solves.
2. What architectural model it uses.
3. How the execution pipeline works.
4. What governance guarantees it provides.
5. How developers can run, extend, and integrate it.

This creates a product-grade technical narrative instead of a feature list.

## Recommended README Structure

### 1. Product Identity

Open with a precise product statement:

```md
# Astreb OS

Astreb OS is a governed hybrid AI operating system for controlled AI execution across local and cloud intelligence.

It routes every task through policy, privacy, risk classification, model routing, approval queues, audit logs, and governed memory before execution.
```

Avoid describing the project first as "an app", "a chatbot", or "a demo". Those frames undersell the architecture.

### 2. Strategic Problem

Explain why this platform exists:

```md
Modern AI systems can generate, automate, and act faster than most organizations can govern them.

Astreb OS addresses the missing layer between AI capability and organizational control: a runtime system that makes AI execution policy-bound, observable, budgeted, and approval-aware.
```

### 3. Core Architecture

Show the microkernel model:

```text
INPUT
  -> MULTIMODAL NORMALIZER
  -> STATE ENGINE
  -> PII DETECTOR
  -> DATA CLASSIFIER
  -> POLICY ENGINE
  -> TOKEN / COST GOVERNOR
  -> MODEL / TOOL ROUTER
  -> LOCAL OR CLOUD RUNTIME
  -> PLUGIN SANDBOX
  -> OUTPUT GUARD
  -> ACTION QUEUE
  -> APPROVAL CENTER
  -> AUDIT LOG
  -> MEMORY PROPOSAL
  -> HUMAN APPROVAL IF REQUIRED
```

This diagram should be near the top of the README because it communicates the product's architecture faster than a paragraph can.

### 4. Platform Capabilities

Present features as platform subsystems:

| Subsystem | Purpose |
| --- | --- |
| Gateway | Accepts text, voice, image, file, browser, email, calendar, and plugin tasks. |
| Classifier | Determines data class, risk level, task type, and routing implications. |
| Policy Engine | Enforces YAML governance before generation or execution. |
| Model Router | Routes work across local, cloud, manual, and enterprise providers. |
| PII Layer | Detects and masks personal or confidential data. |
| Budget Governor | Controls cost, token use, quotas, and emergency stop behavior. |
| Action Queue | Converts external actions into approval-controlled records. |
| Approval Center | Separates proposal from execution authority. |
| Audit Layer | Records decisions, routes, risks, costs, and action states. |
| Memory Layer | Stores only governed operational memory and approved learning proposals. |
| Plugin Sandbox | Validates connector boundaries before tool use. |
| Agent Registry | Defines controlled agent roles, tools, budgets, and permissions. |

### 5. Governance Promise

State the contract clearly:

```md
Astreb OS does not treat AI autonomy as a default.

Agents may draft, analyze, classify, route, and propose. They may not publish, delete, send, merge, release, alter durable memory, change policy, or execute external actions without an approval record.
```

### 6. Local-First Security Position

Explain the local/cloud model:

```md
Astreb OS supports hybrid intelligence, but sensitive work is local-first.

Public and low-risk tasks may be routed to cloud models when policy permits. Personal, confidential, secret-bearing, or high-risk work is masked, blocked, or routed to local/manual execution depending on policy.
```

### 7. Developer Quickstart

Keep setup direct and operational:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --port 8000
```

Then:

```text
http://127.0.0.1:8000
```

### 8. API Surface

Group endpoints by subsystem instead of listing them randomly:

| Area | Endpoints |
| --- | --- |
| Runtime | `POST /submit`, `GET /health`, `GET /state/{request_id}` |
| Governance | `GET /config/policy`, `GET /approvals`, `GET /actions` |
| Audit | `GET /audit`, `GET /observability/events` |
| Memory | `GET /memory/layers`, `POST /memory/proposals/{id}/approve`, `POST /vector-memory/search` |
| Agents | `GET /agents`, `POST /agents` |
| Local Runtime | `GET /local-runtime/status`, `POST /local-runtime/models/{model}/load` |
| Forecasting | `POST /forecasts`, `GET /forecasts`, `GET /forecasts/calibration-profile` |

### 9. Extension Model

Present extension points:

- new agents through `agent_registry`,
- new policies through YAML configuration,
- new providers through provider adapters,
- new tools through sandboxed plugin manifests,
- new workflows through mode classification and action queue integration,
- new memory layers through governed proposal and approval flows.

### 10. Roadmap

Frame the roadmap as maturity layers:

| Layer | Direction |
| --- | --- |
| Runtime | Replace local mock execution with managed local model workers. |
| Data | Add PostgreSQL, pgvector, and append-only audit storage. |
| Governance | Add policy tests, signed policies, and dual-control approvals. |
| Connectors | Add signed connector workers for GitHub, email, calendar, CRM, and team platforms. |
| Observability | Add OpenTelemetry, SIEM export, and compliance retention profiles. |
| Enterprise | Add SSO, RBAC, tenant isolation, key vault integration, and model risk management. |

## Product Narrative

Astreb OS exists because organizations do not only need AI that can answer. They need AI that can operate inside rules.

The first generation of AI tools optimized for conversation. The second generation optimized for automation. Astreb OS targets the next phase: governed execution.

In governed execution, intelligence is not a free-floating assistant. It is a controlled runtime capability. Every request is classified. Every sensitive input is handled under policy. Every model call is routed with cost and risk awareness. Every external action is separated from approval. Every important decision is logged. Every memory update becomes a proposal before it becomes institutional knowledge.

This makes Astreb OS a practical foundation for AI systems that need to function inside real organizations: editorial teams, operations teams, product groups, research desks, compliance-sensitive workflows, and local-first AI deployments.

The platform turns AI from a response generator into an accountable execution layer.

## Technical Narrative

Astreb OS follows a microkernel architecture. The kernel does not try to solve every task directly. Instead, it coordinates the control path that every task must pass through.

The runtime accepts multimodal and tool-oriented input. It normalizes the request, detects personal or confidential information, classifies the task, applies YAML policy, estimates token and cost impact, chooses an execution route, calls the selected provider, scans the output, queues external actions when needed, records audit data, and proposes memory updates only through governed flows.

This architecture separates capability from authority:

- models provide intelligence,
- agents provide specialization,
- policies provide boundaries,
- routers provide execution choice,
- approvals provide authority,
- audit provides accountability,
- memory provides continuity.

The result is a platform where adding more AI capability does not automatically increase uncontrolled risk.

## Repository Landing Page Copy

```md
Astreb OS is a governed hybrid AI operating system: a microkernel control layer for policy-bound, auditable, local-first AI execution.

It routes tasks through classification, privacy controls, YAML policy, budget governance, model routing, approval queues, audit logs, and governed memory before action. It is designed for teams that need AI as infrastructure, not as an uncontrolled chatbot.
```

## Investor / Partner Description

Astreb OS is an AI governance runtime that enables organizations to deploy AI agents and model workflows under policy, privacy, audit, and approval control. It provides the missing operational layer between raw AI capability and trustworthy organizational execution.

## Developer Description

Astreb OS is a FastAPI-based governed AI microkernel with policy enforcement, data classification, local/cloud model routing, action queues, approval records, audit logging, agent registry, plugin sandboxing, and governed memory proposals.

## Enterprise Description

Astreb OS is a local-first AI control layer for regulated or operationally sensitive environments. It supports hybrid model routing, approval-gated external actions, auditability, policy-driven execution, and structured agent governance.

## What This Repository Should Signal

The repository should signal:

- architectural seriousness,
- governance-first execution,
- local-first security,
- practical developer usability,
- extensibility,
- auditability,
- enterprise trajectory,
- agent control instead of agent hype.

It should not signal:

- chatbot-first positioning,
- prompt library positioning,
- vague AI assistant branding,
- uncontrolled autonomy,
- generic automation,
- speculative AGI language,
- feature volume over system coherence.

## Recommended Top-Level Repository Files

```text
README.md
architecture.md
agents.md
workflows.md
policies.yaml
GITHUB_PUBLISH.md
docs/
  repository-presentation-architecture.md
  operating-manifesto.md
  platform-narrative.md
  technical-architecture.md
  governance-model.md
```

## Success Standard

The repository presentation succeeds when a technical reader can understand, within three minutes:

- what Astreb OS is,
- why it exists,
- how the execution pipeline works,
- what governance guarantees it provides,
- how to run it,
- how to extend it,
- why it is different from a chatbot or model wrapper.

The target impression is:

> This is not another AI demo. This is an operating layer for controlled AI execution.
