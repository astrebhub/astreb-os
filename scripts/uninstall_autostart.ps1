$ErrorActionPreference = "Stop"

$TaskName = "AI Cabinet Autostart"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed '$TaskName'."
}
else {
    Write-Host "'$TaskName' was not installed."
}
