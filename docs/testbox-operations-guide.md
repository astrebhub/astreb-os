# ASTREB TESTBOX Operations Guide

Status: TESTBOX v0.1 local MVP

```text
TESTBOX v0.1 = passed local functional smoke test.
Ready for backend integration phase.
```

## 1. What TESTBOX Is

TESTBOX is a dynamic AI governance and demonstration environment for ASTREB OS.

It is not a chatbot and not a normal dashboard. It is an AI operations cockpit
that shows how governed AI processes move through routing, policy checks,
approval gates, audit, memory, quality validation, and operator explanation.

Core distinction:

```text
AI Cabinet = static governance architecture
TESTBOX = dynamic operations and demonstration environment
```

TESTBOX v0.1 demonstrates three layers:

```text
Static Layer:
roles / routes / skills / settings

Dynamic Layer:
scenarios / actions / audit / memory

Observation Layer:
cockpit / routing / audit / demo pages
```

## 2. Route Structure

The MVP exposes one TESTBOX shell with route-based operating modes:

```text
/testbox
/testbox/cockpit
/testbox/orchestration
/testbox/user
/testbox/legal
/testbox/legal-demo
/testbox/audit
/testbox/routing
/testbox/memory
/testbox/settings
/testbox/training
/testbox/hackathon
```

Recommended entry points:

```text
/testbox
/testbox/legal-demo
/testbox/user
/testbox/routing
/testbox/audit
```

### 5.11 User Interaction

Open:

```text
/testbox/user
```

This mode provides a governed user intake surface:

- text input
- voice command fallback
- image attachment metadata and preview
- document attachment metadata
- governed Administrator response
- risk analysis
- route selection
- policy trigger visibility
- audit logging

v0.1 does not upload files to a backend. Attachments are handled locally in the
browser as metadata and previews. v0.2 should add a secure backend upload and
document/image processing pipeline.

## 3. Installation

### 3.1 Requirements

Minimal local runtime:

- Python 3.11+ for FastAPI mode, or
- Node.js for local static preview mode.

Python dependencies are listed in:

```text
backend/requirements.txt
```

### 3.2 Install Python Dependencies

From the repository root:

```bash
cd backend
python -m pip install -r requirements.txt
```

If your system uses the Windows Python launcher:

```bash
cd backend
py -m pip install -r requirements.txt
```

## 4. Running TESTBOX

### 4.1 FastAPI Mode

From the repository root:

```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/testbox
http://127.0.0.1:8000/testbox/legal-demo
http://127.0.0.1:8000/testbox/routing
http://127.0.0.1:8000/testbox/audit
```

### 4.2 Local Node Preview Mode

From the repository root:

```bash
node scripts/local_jazekker_server.mjs
```

Open:

```text
http://127.0.0.1:8000/testbox
```

The Codex in-app preview used during validation also ran the page at:

```text
http://127.0.0.1:8123/testbox
```

That preview URL is development-session specific. For normal use, prefer the
FastAPI route or the local Node preview route.

## 5. Operating the Cockpit

### 5.1 Main Cockpit

Open:

```text
/testbox
```

Use this view to demonstrate the full AI operations environment:

- active role
- active scenario
- system status
- static setup
- dynamic execution
- routing decisions
- audit stream
- quality and governance
- TESTBOX Administrator narration
- voice meeting mode

### 5.2 Roles

Available roles:

- Operator
- Instructor
- Legal Assistant
- Governance Officer
- Project Architect
- Demo Presenter
- Hackathon Mentor
- CRM Dispatcher

Operational use:

- Use **Operator** for normal command-center operation.
- Use **Legal Assistant** for the legal demo.
- Use **Governance Officer** for policy and approval explanations.
- Use **Instructor** for training sessions.
- Use **Demo Presenter** for investor, partner, or stakeholder walkthroughs.
- Use **Hackathon Mentor** for guided team scenarios.
- Use **CRM Dispatcher** when explaining future CRM/API routing.

### 5.3 Skills

Skills are separate from roles. This is intentional.

Available skills:

- Self Presentation
- Workflow Explanation
- Legal Citation
- Audit Narration
- Risk Analysis
- Quality Review
- Routing Explanation
- Policy Explanation
- Demo Narration
- Voice Meeting Mode
- CRM Routing
- Memory Explanation

Operational use:

- Activate skills to show how capabilities can be composed independently from
  role identity.
- Use this to explain why role behavior, skill behavior, policies, and runtime
  workflows must not be mixed.

### 5.4 Static Setup

Static setup blocks are clickable and perform local self-tests:

- Gateway
- Policy Engine
- Router Config
- Role System
- Skill System
- Memory
- Audit
- Quality Rules
- CRM Connectors
- Legal Sources
- LLM Connectors
- UI Configuration

Operational use:

- Click a block to show whether it is online, local, mocked, or stored in
  local state.
- Use this section to explain that AI Cabinet is the static governance substrate.

### 5.5 Dynamic Execution

The execution lane shows the runtime flow:

```text
Request
Intent Detection
Jurisdiction Detection
PII Detection
PII Masking
Legal Source Retrieval
Policy Evaluation
Routing
LLM Drafting
Citation Validation
Quality Check
Human Approval
PII Rehydration
Audit Logging
```

Operational use:

- Click **Run Legal Demo** to execute the flow.
- Click **Replay** to run the demo again.
- Click **Emergency Stop** to pause runtime behavior.

### 5.6 Routing Monitor

Open:

```text
/testbox/routing
```

Routes:

- Local AI
- Legal DB
- CRM/API
- Cloud LLM
- Human Approval

Routing philosophy:

```text
LLM only when needed.
```

Operational use:

- Click each route to let Administrator explain why it is selected or skipped.
- Use this scenario to show that sensitive data stays local, legal retrieval uses
  legal sources, and cloud LLM access is only allowed after masking.

### 5.7 Legal Demo

Open:

```text
/testbox/legal-demo
```

Recommended demo flow:

1. Review the legal question in the input area.
2. Click **Mask PII**.
3. Inspect placeholder replacement.
4. Inspect retrieved local legal sources.
5. Click **Run Legal Demo**.
6. Watch dynamic execution move through the governance pipeline.
7. Click **Approve** at the approval gate.
8. Click **Rehydrate Locally**.
9. Review audit stream and Administrator narration.

What it demonstrates:

- voice/text input readiness
- PII detection and masking
- legal source retrieval
- route selection
- approval gate
- QMS scoring
- local rehydration
- audit trail
- governed response behavior

### 5.8 Audit

Open:

```text
/testbox/audit
```

Operational use:

- Use this route after running a demo.
- Confirm that audit events accumulate.
- Use it as the replay and governance evidence surface.

v0.1 stores audit in browser local state. v0.2 should replace this with backend
persistent audit storage.

### 5.9 Memory

Open:

```text
/testbox/memory
```

Operational use:

- Show that TESTBOX can write workflow memories locally.
- Explain that raw PII should not be stored in memory.
- Use this view to demonstrate the memory governance principle:

```text
Store workflow metadata, not raw sensitive content.
```

### 5.10 Voice Meeting Mode

Voice controls:

- Start Voice
- Stop Voice
- Send Command
- Speak Administrator

Operational use:

- Use **Send Command** for safe fallback testing.
- Use **Speak Administrator** to test browser text-to-speech where supported.
- Use **Start Voice** only during an explicit microphone permission test.

Recommended fallback commands:

```text
explain routing
explain policy
run demo
mask PII
stop
```

Important:

```text
Start Voice may trigger a browser microphone permission prompt.
Do not run this test silently or during unattended validation.
```

## 6. Recommended Scenarios

### Scenario A: Executive Governance Demo

Purpose:

Show that TESTBOX is an AI operations environment, not a chatbot.

Flow:

1. Open `/testbox`.
2. Explain Static / Dynamic / Observation layers.
3. Click Static Setup blocks.
4. Switch role to Governance Officer.
5. Click Explain Policies.
6. Run Legal Demo.
7. Show audit stream and QMS.

Best audience:

- founders
- enterprise partners
- governance stakeholders
- investors

### Scenario B: Legal AI Governance Demo

Purpose:

Demonstrate governed legal AI flow with PII masking and approval.

Flow:

1. Open `/testbox/legal-demo`.
2. Switch role to Legal Assistant.
3. Click Mask PII.
4. Inspect legal sources.
5. Click Run Legal Demo.
6. Click Approve.
7. Click Rehydrate Locally.
8. Open `/testbox/audit`.

Best audience:

- legal teams
- compliance teams
- public-sector stakeholders
- privacy officers

### Scenario C: Routing Philosophy Demo

Purpose:

Explain "LLM only when needed."

Flow:

1. Open `/testbox/routing`.
2. Switch role to Project Architect or Governance Officer.
3. Click Local AI.
4. Click Legal DB.
5. Click CRM/API.
6. Click Cloud LLM.
7. Click Human Approval.
8. Explain why routing is governed by data sensitivity, factual need, legal
   retrieval, reasoning need, and risk level.

Best audience:

- architects
- AI platform teams
- security teams
- technical reviewers

### Scenario D: Operator Training

Purpose:

Train operators to understand runtime decisions.

Flow:

1. Open `/testbox/training`.
2. Switch role to Instructor.
3. Activate Workflow Explanation, Audit Narration, Risk Analysis, and Policy
   Explanation.
4. Run Legal Demo.
5. Pause workflow.
6. Override Routing.
7. Reject.
8. Replay.

Best audience:

- operators
- implementation teams
- support teams
- hackathon participants

### Scenario E: Hackathon Mentor Mode

Purpose:

Use TESTBOX as a guided challenge environment.

Flow:

1. Open `/testbox/hackathon`.
2. Switch role to Hackathon Mentor.
3. Activate Demo Narration and Routing Explanation.
4. Run the legal demo.
5. Ask teams to identify which blocks are static, dynamic, and observational.
6. Ask teams to propose a v0.2 backend integration.

Best audience:

- hackathon teams
- students
- builders
- demo workshop participants

## 7. Operational Checklist

Before a demo:

- Start the local server.
- Open `/testbox`.
- Confirm the page loads.
- Confirm there are no console errors.
- Run **Mask PII** once.
- Run **Run Legal Demo** once.
- Confirm audit events increase.
- Keep voice microphone testing disabled unless planned.

During a demo:

- Start from the cockpit, not from a technical explanation.
- Use Administrator narration buttons.
- Show routing before showing final output.
- Show audit and QMS before claiming governance.
- Keep the message clear: TESTBOX controls AI processes; it does not pretend
  that AI is autonomous.

After a demo:

- Open `/testbox/audit`.
- Capture audit count and final state.
- Note any browser permission issues.
- Reset local state only if a clean demo is needed.

## 8. v0.2 Backend Integration Targets

Priority backlog:

1. Voice permission test as a separate operator-controlled test.
2. Real backend events instead of mock/local state.
3. Persistent audit storage.
4. Real PII masking pipeline.
5. Legal source retrieval integration.
6. Real approval workflow.
7. Exportable demo report.

Recommended v0.2 backend services:

```text
FastAPI event API
PostgreSQL audit storage
Redis runtime event queue
PII masking service
Legal retrieval service
Approval workflow service
Report export service
```

## 9. Current Limitations

TESTBOX v0.1 is a local MVP. It proves operating model viability, not production
readiness.

Current limitations:

- Audit and memory are local browser state.
- Legal sources are local demo sources.
- LLM drafting is simulated.
- QMS is deterministic local scoring.
- Voice depends on browser STT/TTS support.
- No real CRM/API connection yet.
- No persistent backend workflow engine yet.

## 10. Acceptance Reference

See:

```text
docs/testbox-v0.1-acceptance-report.md
```
