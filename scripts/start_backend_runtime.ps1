$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$SitePackages = Join-Path $Backend ".venv_runtime\Lib\site-packages"
$Python = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\python.exe"

$env:PYTHONPATH = "$SitePackages;$Backend"
Set-Location $Backend
& $Python -m uvicorn main:app --host 127.0.0.1 --port 8000
