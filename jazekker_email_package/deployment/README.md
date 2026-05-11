# JAZEKKER Deployment Layer

This folder contains safe deployment and activation templates for the JAZEKKER project package.

It does not auto-run from email. That would be insecure and is usually blocked by operating systems and mail clients.

Available templates:

- `install-to-repo.ps1` - copy the package into a target repository.
- `create-project-structure.ps1` - create recommended repository folders.
- `nightly-orientation-task.example.ps1` - example Windows scheduled task runner.
- `github-actions-nightly-orientation.yml` - GitHub Actions template for future automation.
- `DEPLOYMENT_PLAN.md` - placement and rollout instructions.

## Recommended Flow

1. Review the package in this repository.
2. Run deployment scripts manually only after confirming the target path.
3. Review copied files before committing.
4. Add automation only after governance and publishing rules are confirmed.

No publishing action is performed by these templates.
