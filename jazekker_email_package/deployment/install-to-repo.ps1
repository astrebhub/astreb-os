param(
  [Parameter(Mandatory = $true)]
  [string]$TargetRepo
)

$ErrorActionPreference = "Stop"

$packageRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$target = Resolve-Path -LiteralPath $TargetRepo
$destination = Join-Path $target "docs\strategy\jazekker"

Write-Host "JAZEKKER package root: $packageRoot"
Write-Host "Target repository: $target"
Write-Host "Destination: $destination"

New-Item -ItemType Directory -Force -Path $destination | Out-Null

Copy-Item -LiteralPath (Join-Path $packageRoot "README.md") -Destination $destination -Force
Copy-Item -LiteralPath (Join-Path $packageRoot "00-email-cover-note.md") -Destination $destination -Force
Copy-Item -LiteralPath (Join-Path $packageRoot "01-project-charter.md") -Destination $destination -Force
Copy-Item -LiteralPath (Join-Path $packageRoot "02-agentic-media-operating-system.md") -Destination $destination -Force
Copy-Item -LiteralPath (Join-Path $packageRoot "03-orientation-experience-ux.md") -Destination $destination -Force
Copy-Item -LiteralPath (Join-Path $packageRoot "04-execution-backlog.md") -Destination $destination -Force
Copy-Item -LiteralPath (Join-Path $packageRoot "05-placement-instructions.md") -Destination $destination -Force

$assetSource = Join-Path $packageRoot "assets"
if (Test-Path -LiteralPath $assetSource) {
  Copy-Item -LiteralPath $assetSource -Destination $destination -Recurse -Force
}

$deploymentSource = Join-Path $packageRoot "deployment"
if (Test-Path -LiteralPath $deploymentSource) {
  Copy-Item -LiteralPath $deploymentSource -Destination $destination -Recurse -Force
}

Write-Host "Package copied successfully."
Write-Host "Review files before commit. No publishing action was performed."

