# AI Cabinet Architecture

AI Cabinet is a governed AI execution microkernel. Models are treated as
replaceable execution engines. AI Cabinet remains the trusted layer for policy,
permissions, routing, memory, cost, audit, approvals, and plugin control.

## Control Boundary

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
  -> PROVIDER ADAPTER
  -> OUTPUT GUARD
  -> ACTION QUEUE
  -> APPROVAL CENTER
  -> AUDIT LOG
  -> MEMORY UPDATE PROPOSAL
```

## Runtime Domains

```text
/kernel              trusted control boundary
/router              model and workload routing
/security            PII, secrets, redaction, output guard
/policies            YAML governance rules
/providers           model provider adapters
/local_runtime       Ollama and local execution targets
/plugins             permission-manifest plugins
/memory              governed layered memory
/audit               execution evidence trail
/runtime             pipeline orchestration
/ui                  AI Control Center
/budget              cost, quota, kill-switch governance
/voice               voice pipeline readiness
/connectors          external integration targets
/vector_memory       vector store abstraction
/action_queue        approval-controlled action lifecycle
```

## Governance Model

Agents may draft, analyze, classify, route, and propose. They may not publish,
delete, send, merge, release, alter durable policy, or execute external actions
without an approval record.

## Hybrid Intelligence

Routing considers data sensitivity, policy, risk, estimated cost, task type,
latency intent, and local availability.

- Personal or confidential data: local-only or manual path.
- Public low-risk content: cloud allowed when policy permits.
- External actions: draft or approval queue only.
- Offline mode: local safe fallback or configured Ollama runtime.

## Memory

Memory is separated into constitution, role instruction, policy, project,
operational, learning, and audit layers. Runtime learning follows:

```text
Observation -> Hypothesis -> Proposal -> Approval -> Memory Update -> Audit
```

Constitution, role instruction, policy, and audit layers are not autonomously
rewritten by agents.

## Production Hardening Roadmap

- Managed AuthN/AuthZ and tenant isolation.
- KMS-backed secrets.
- PostgreSQL and append-only audit storage.
- Signed plugin registry and connector isolation.
- Policy-as-code review workflow.
- Model evaluation and red-team gates.
- OpenTelemetry and SIEM export.
