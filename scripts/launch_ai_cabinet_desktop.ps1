$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ServerScript = Join-Path $ProjectRoot "scripts\start_ai_cabinet.ps1"
$Url = "http://127.0.0.1:8000"

$Existing = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $Existing) {
    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $ServerScript
    ) -WorkingDirectory $ProjectRoot
    Start-Sleep -Seconds 4
}

Start-Process $Url
