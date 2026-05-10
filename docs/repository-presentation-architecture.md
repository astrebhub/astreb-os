# AI Cabinet Repository Presentation Architecture

## Product Narrative

AI Cabinet is a governed hybrid AI control plane for controlled AI execution
across local intelligence, cloud intelligence, agents, and signed connector
workflows.

It is not positioned as a chatbot, prompt interface, automation script, or thin
model wrapper. It is a runtime governance layer: a microkernel architecture that
turns AI work into classified, routed, policy-bound, auditable, approval-aware
execution.

The repository should present AI Cabinet as an executable control system for
teams that need AI capability without losing operational authority.

## Primary Definition

AI Cabinet is a governed AI execution microkernel.

It coordinates:

- input normalization,
- risk and data classification,
- PII and secret handling,
- policy enforcement,
- token and cost governance,
- model and tool routing,
- local/cloud execution decisions,
- approval gates,
- audit records,
- governed memory,
- agent boundaries,
- plugin and connector control,
- ASTI governed connector manifests,
- free/local-first model routing.

## One-Line Description

Governed hybrid AI control plane for policy-bound, auditable, local-first AI
execution with controlled agents and ASTI connector governance.

## Short Description

AI Cabinet routes AI tasks through classification, privacy controls, YAML
policy, budget governance, model routing, approval queues, audit logs,
governed memory, agent roles, and ASTI connector manifests before action. It is
designed for teams building AI infrastructure where control, privacy,
traceability, and human authority matter.

## Repository Story

The repository should tell the story in five layers:

1. What problem AI Cabinet solves.
2. What architectural model it uses.
3. How the execution pipeline works.
4. What governance guarantees it provides.
5. How developers can run, extend, and integrate it.

## Core Architecture

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
  -> ASTI CONNECTOR GATE
  -> OUTPUT GUARD
  -> ACTION QUEUE
  -> APPROVAL CENTER
  -> AUDIT LOG
  -> MEMORY PROPOSAL
  -> HUMAN APPROVAL IF REQUIRED
```

## Governance Promise

AI Cabinet does not treat autonomy as a default.

Agents may draft, analyze, classify, route, and propose. They may not publish,
delete, send, merge, release, alter durable memory, change policy, or execute
external actions without an approval record.

## ASTI Positioning

ASTI stands for **Agentic Secure Tool Interface**.

ASTI is the AI Cabinet-native connector layer. It turns agent capabilities into
signed, manifest-based, approval-gated connector workflows. It is designed for
email, calendar, files, browser, GitHub, Microsoft 365, Telegram, WhatsApp,
Notion, local computer operations, and future enterprise tools.

The current public MVP exposes connector status and dry-run evaluation while
keeping real-world execution disabled until a connector is signed and approved.

## Local-First Security Position

AI Cabinet supports hybrid intelligence, but sensitive work is local-first.

Public and low-risk tasks may be routed to cloud models when policy permits.
Personal, confidential, secret-bearing, or high-risk work is masked, blocked, or
routed to local/manual execution depending on policy.

## Extension Model

- Add agents through the agent registry.
- Add policies through YAML configuration.
- Add providers through provider adapters.
- Add tools through sandboxed plugin manifests and ASTI connector manifests.
- Add workflows through mode classification and action queue integration.
- Add memory behavior through governed proposal and approval flows.

## Current Public Demonstration Layers

- AI Control Center browser UI.
- Governed Microsoft 365 agent for Outlook, Calendar, Teams, Planner, OneDrive, and SharePoint proposals.
- GitHub Manager agent for repository planning and release proposals.
- Computer Control agent for safe local operation plans and report artifacts.
- Free/local model stack: Ollama local, OpenRouter free routing, Gemini slot, and local-safe fallback.
- ASTI connector status API for signed connector governance.

## Success Standard

The repository presentation succeeds when a technical reader can understand,
within three minutes:

- what AI Cabinet is,
- why it exists,
- how the execution pipeline works,
- what governance guarantees it provides,
- how to run it,
- how to extend it,
- why it is different from a chatbot or model wrapper.

The target impression is:

> This is not another AI demo. This is an operating layer for controlled AI
> execution.
