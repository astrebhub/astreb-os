$ErrorActionPreference = "Stop"

$TaskName = "AI Cabinet Autostart"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$StartScript = Join-Path $ProjectRoot "scripts\start_ai_cabinet.ps1"
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

$PowerShellPath = (Get-Command powershell.exe).Source
$Action = New-ScheduledTaskAction `
    -Execute $PowerShellPath `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StartScript`"" `
    -WorkingDirectory $ProjectRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Starts AI Cabinet FastAPI runtime at user logon." `
    -Force | Out-Null

Write-InstallLog "Installed scheduled task '$TaskName' for project '$ProjectRoot'."
Write-Host "Installed '$TaskName'. AI Cabinet will start at next Windows logon."
