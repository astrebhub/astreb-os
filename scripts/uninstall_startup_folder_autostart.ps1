$ErrorActionPreference = "Stop"

$StartupDir = [Environment]::GetFolderPath("Startup")
$CmdPath = Join-Path $StartupDir "AI Cabinet Autostart.cmd"

if (Test-Path $CmdPath) {
    Remove-Item -LiteralPath $CmdPath -Force
    Write-Host "Removed Startup folder autostart: $CmdPath"
}
else {
    Write-Host "Startup folder autostart was not installed."
}
