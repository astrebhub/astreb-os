# Security Policy

AI Cabinet is a governed AI control-plane MVP. Treat it as a local-first
runtime unless you have explicitly configured authentication, network
boundaries, managed secrets, and deployment hardening.

## Supported Security Posture

- Public cloud model calls must receive masked input only.
- Personal and confidential data are routed local-only by policy.
- Real-world actions are drafts or approval-queue records in the MVP.
- Administrative endpoints require `X-AI-Cabinet-Admin-Token` when
  `ADMIN_API_TOKEN` is configured.

## Reporting A Vulnerability

Open a private security advisory on GitHub if available, or contact the
repository owner directly. Do not publish exploit details before maintainers
have had a reasonable chance to respond.

## Known MVP Limitations

- The development secrets store is not a production KMS. Replace it with a
  managed key-management backend before production use.
- SQLite is used for local development storage.
- Plugin sandboxing validates manifests but does not yet execute plugins in
  hardened process/container isolation.
