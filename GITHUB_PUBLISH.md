# Publish AI Cabinet To GitHub

The canonical public branch for the full AI Cabinet project is:

```text
ai-cabinet-full
```

Use `main` only after the repository default branch has been cleaned or merged
intentionally.

## GitHub Manager Governance

The project includes `github_manager_agent` for governed repository work. It may
prepare issues, pull request plans, review summaries, CI diagnostics, branch
plans, and release notes. It must queue approval before any external GitHub
action such as push, merge, branch deletion, release publication, issue closure,
repository setting changes, or secret handling.

## Git CLI Publish

```powershell
cd C:\Users\Viacheslav\OneDrive\Документы\ai_cabinet_mvp
git add .
git commit -m "Harden AI Cabinet public release"
git push origin HEAD:ai-cabinet-full
```

## Release Hygiene

- Do not publish `backend/.env`, `backend/*.db`, logs, model weights, ZIP
  bundles, or generated transfer bundles.
- Set `ADMIN_API_TOKEN` before sharing the Control Center beyond localhost.
- Keep GitHub Manager actions approval-gated.
- Run tests and CI before tagging releases.

## Autostart

Autostart is supported through:

- `scripts/start_ai_cabinet.ps1`
- `scripts/install_autostart.ps1`
- `scripts/install_startup_folder_autostart.ps1`
- `scripts/uninstall_autostart.ps1`
- `scripts/uninstall_startup_folder_autostart.ps1`
- `scripts/start_ai_cabinet.sh`
- `scripts/install_ubuntu_autostart.sh`
- `scripts/install_macos_autostart.sh`
