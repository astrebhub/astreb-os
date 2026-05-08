# Publish AI Cabinet To GitHub

Local `git` and `gh` are not installed on this machine, so this project is prepared for publishing but cannot be pushed from the local CLI yet.

## Option A: GitHub Web Upload

1. Create a new GitHub repository, for example `ai-cabinet`.
2. Upload the contents of this folder, excluding ignored files:
   - `backend/.env`
   - `backend/*.db`
   - `logs/`
   - `.venv/`
3. Commit as `Initial AI Cabinet microkernel runtime`.

## Option B: Git CLI

After installing Git:

```powershell
cd C:\Users\Viacheslav\OneDrive\Документы\ai_cabinet_mvp
git init
git add .
git commit -m "Initial AI Cabinet microkernel runtime"
git branch -M main
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

## Option C: GitHub CLI

After installing GitHub CLI:

```powershell
cd C:\Users\Viacheslav\OneDrive\Документы\ai_cabinet_mvp
gh repo create ai-cabinet --private --source . --remote origin --push
```

## Autostart

Autostart is already supported through:

- `scripts/start_ai_cabinet.ps1`
- `scripts/install_autostart.ps1`
- `scripts/install_startup_folder_autostart.ps1`
- `scripts/uninstall_autostart.ps1`
- `scripts/uninstall_startup_folder_autostart.ps1`
