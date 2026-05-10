# Agent Action Scenario Test

This scenario verifies that AI Cabinet can run an agent through a controlled action lifecycle without real-world side effects.

## Purpose

Prove that an agent can:

- receive a governed task;
- generate an action proposal;
- enter the approval queue;
- be approved by the owner/admin;
- execute a local sandbox report artifact;
- produce an auditable report.

The scenario intentionally does **not** push, publish, send, delete, or call a network connector.
It does create a real local report file under `runtime/reports/`.

## Scenario

```text
Agent: GitHub Manager
Dialogue mode: GitHub Manager
Mode: GitHub operations
Access level: Level 3
Provider: Ollama local
Action type: prepare_github_action
Execution: local sandbox report artifact
```

## Run

From the project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_agent_action_scenario.ps1
```

Optional:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_agent_action_scenario.ps1 `
  -BaseUrl "http://127.0.0.1:8000" `
  -AdminToken "change-me-before-public-demo" `
  -Provider "ollama"
```

## Expected Result

The report verdict should be:

```json
"verdict": "passed"
```

Expected lifecycle:

```text
/submit
  -> action_id created
  -> action status: pending_approval
  -> approve action
  -> execute local report artifact
  -> action status: executed
  -> artifact_path exists
  -> audit row exists
  -> state timeline exists
```

## Report Location

By default, reports are written to:

```text
logs/agent-action-scenario-YYYYMMDD-HHMMSS.json
```

## What This Demonstrates

This is a controlled execution test, not a chatbot test. It demonstrates:

- policy-controlled action generation;
- human approval workflow;
- action queue lifecycle;
- auditability;
- provider/model traceability;
- a real local execution artifact with no external network side effects.
