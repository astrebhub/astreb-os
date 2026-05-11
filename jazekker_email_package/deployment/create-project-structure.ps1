param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"

$rootPath = Resolve-Path -LiteralPath $Root

$folders = @(
  "content\orientation",
  "content\briefings",
  "content\articles",
  "content\explainers",
  "content\governance-notes",
  "content\future-signals",
  "ai-cabinet\prompts",
  "ai-cabinet\workflows",
  "ai-cabinet\schemas",
  "ai-cabinet\audit",
  "ai-cabinet\memory",
  "distribution\linkedin",
  "distribution\telegram",
  "distribution\newsletter",
  "distribution\rss",
  "governance\policies",
  "governance\approvals",
  "governance\source-register"
)

foreach ($folder in $folders) {
  $path = Join-Path $rootPath $folder
  New-Item -ItemType Directory -Force -Path $path | Out-Null
  $keep = Join-Path $path ".gitkeep"
  if (-not (Test-Path -LiteralPath $keep)) {
    New-Item -ItemType File -Path $keep | Out-Null
  }
}

Write-Host "JAZEKKER project structure created at $rootPath"
Write-Host "No files were overwritten except missing .gitkeep placeholders."

