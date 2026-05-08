$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$StartScript = Join-Path $ProjectRoot "scripts\start_ai_cabinet.ps1"
$StartupDir = [Environment]::GetFolderPath("Startup")
$CmdPath = Join-Path $StartupDir "AI Cabinet Autostart.cmd"
$LogDir = Join-Path $ProjectRoot "logs"
$TaskLog = Join-Path $LogDir "autostart_install.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-InstallLog {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $TaskLog -Value "[$Timestamp] $Message"
}

if (-not (Test-Path $StartScript)) {
    throw "Start script not found: $StartScript"
}

$Cmd = @"
@echo off
start "AI Cabinet" /min powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "$StartScript"
"@

Set-Content -Path $CmdPath -Value $Cmd -Encoding ASCII
Write-InstallLog "Installed Startup folder autostart: $CmdPath"
Write-Host "Installed Startup folder autostart: $CmdPath"
