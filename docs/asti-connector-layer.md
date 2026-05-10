# ASTI Connector Layer

AI Cabinet implements ASTI agent capabilities through governed connectors, not direct model access.

ASTI means **Agentic Secure Tool Interface** in AI Cabinet. It is the safe connector layer between untrusted AI models and real-world systems such as email, calendar, files, browser, GitHub, Microsoft 365, Telegram, WhatsApp, Notion, and local computer operations.

## Principle

```text
Model proposes.
Microkernel checks.
Connector manifest restricts.
Approval center authorizes.
Audit records.
Only then can an executor run.
```

In the current MVP, connectors are **draft/report only** unless their manifest contains a signed connector block and the requested action is approved.

## Compatibility

ASTI is the AI Cabinet-native connector layer used by:

- `AI CABINET Control Center`
- `agent-action-scenario-*.json`
- `agent-action-test-scenario.md`
- `asti-connector-layer.md`

This keeps the system independent from third-party agent branding while preserving the original goal: controlled AI actions behind microkernel governance.

## Connector States

- `unsigned`: manifest exists, real-world execution disabled.
- `signed`: connector has signer and signature metadata.
- `approved`: action has a human approval record.
- `executed`: executor completed and wrote an audit record.

## Current Connectors

- `email_plugin`
- `calendar_plugin`
- `telegram_plugin`
- `whatsapp_plugin`
- `browser_plugin`
- `files_plugin`
- `paperclip_plugin`
- `notion_plugin`
- `github_connector`
- `microsoft_365_connector`
- `computer_control_plugin`

## Runtime Endpoints

```http
GET /connectors/status
GET /connectors/{connector_name}
POST /connectors/{connector_name}/dry-run?action=send_email&data_class=public&access_level=2
```

The dry-run endpoint never executes the action. It only explains whether the connector policy would allow the action.

## Safety Guarantees

- Unsigned connectors cannot perform external actions.
- Sensitive data is governed by PII masking and policy rules before routing.
- Action modes enter the approval queue.
- Browser, file, computer, email, calendar, Teams, WhatsApp, and GitHub operations remain blocked until signed executors are added.
- Local report artifacts are allowed as evidence of controlled execution.

## Next Step

To enable a real connector, add:

```yaml
signed_connector:
  status: signed
  signer: owner
  signature: <signature-or-certificate-reference>
```

Then implement a dedicated executor that:

1. checks the manifest,
2. checks approval,
3. checks data class,
4. performs one narrowly scoped action,
5. writes audit and rollback metadata.
