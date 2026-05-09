# Publishing AI Cabinet

The full public project is published from the `ai-cabinet-full` branch.

## Git CLI

```bash
git add .
git commit -m "Prepare AI Cabinet public release"
git push origin HEAD:ai-cabinet-full
```

## Release Hygiene

- Do not publish `.env` files, local databases, logs, ZIP bundles, generated
  transfer bundles, model weights, private screenshots, or local machine paths.
- Set `ADMIN_API_TOKEN` before sharing the Control Center outside a local demo.
- Keep GitHub Manager actions approval-gated.
- Run tests and CI before tagging releases.

## GitHub Manager Governance

`github_manager_agent` may draft issues, pull request plans, review summaries,
CI diagnostics, branch plans, and release notes. It must queue approval before
any external GitHub action such as push, merge, branch deletion, release
publication, issue closure, repository setting changes, or secret handling.
