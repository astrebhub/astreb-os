$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendDir = Join-Path $ProjectRoot "backend"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "autostart.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Set-Location $BackendDir

function Write-StartupLog {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "[$Timestamp] $Message"
}

function Resolve-PythonCommand {
    $VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
    if (Test-Path $VenvPython) {
        return @($VenvPython)
    }

    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($Python) {
        return @($Python.Source)
    }

    $PyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($PyLauncher) {
        return @($PyLauncher.Source, "-3")
    }

    return $null
}

try {
    Write-StartupLog "Starting AI Cabinet autostart."

    if (-not (Test-Path (Join-Path $BackendDir ".env")) -and (Test-Path (Join-Path $BackendDir ".env.example"))) {
        Copy-Item -Path (Join-Path $BackendDir ".env.example") -Destination (Join-Path $BackendDir ".env")
        Write-StartupLog "Created backend\.env from .env.example."
    }

    $PythonCommand = Resolve-PythonCommand
    if (-not $PythonCommand) {
        Write-StartupLog "Python was not found. Install Python or create backend\.venv, then run scripts\install_autostart.ps1 again."
        exit 1
    }

    $PythonExe = $PythonCommand[0]
    $PythonArgs = @()
    if ($PythonCommand.Count -gt 1) {
        $PythonArgs += $PythonCommand[1..($PythonCommand.Count - 1)]
    }

    $UvicornCheck = & $PythonExe @PythonArgs -m uvicorn --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-StartupLog "uvicorn is not installed for this Python. Run: cd backend; pip install -r requirements.txt"
        exit 1
    }

    Write-StartupLog "Launching http://127.0.0.1:8000"
    & $PythonExe @PythonArgs -m uvicorn main:app --host 127.0.0.1 --port 8000
}
catch {
    Write-StartupLog "Startup failed: $($_.Exception.Message)"
    exit 1
}
