[CmdletBinding()]
param(
    [switch]$Stop,
    [switch]$SetupOnly,
    [switch]$NoInstall
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
$BackendLogDir = Join-Path $BackendDir "storage\logs"
$PidFile = Join-Path $BackendLogDir "dev.pids.json"

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message"
}

function Assert-Command {
    param(
        [string]$Name,
        [string]$InstallHint
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found. $InstallHint"
    }
}

function Stop-DevProcesses {
    $stopped = $false

    if (-not (Test-Path -LiteralPath $PidFile)) {
        Write-Host "No dev PID file found."
    } else {
        $pidData = Get-Content -LiteralPath $PidFile -Raw | ConvertFrom-Json
        foreach ($entry in @($pidData.backend, $pidData.frontend)) {
            if (-not $entry.pid) {
                continue
            }

            $process = Get-Process -Id $entry.pid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Step "Stopping $($entry.name) process tree (PID $($entry.pid))"
                taskkill.exe /PID $entry.pid /T /F | Out-Null
                $stopped = $true
            }
        }

        Remove-Item -LiteralPath $PidFile -Force
    }

    $portPids = @{}
    $netstatLines = netstat.exe -ano
    foreach ($line in $netstatLines) {
        if ($line -notmatch "^\s*TCP\s+\S+:(8000|5173)\s+\S+\s+LISTENING\s+(\d+)\s*$") {
            continue
        }

        $port = $Matches[1]
        $processId = $Matches[2]
        $portPids["$port/$processId"] = @{ port = $port; pid = $processId }
    }

    foreach ($item in $portPids.Values) {
        $process = Get-Process -Id $item.pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Step "Stopping process on port $($item.port) (PID $($item.pid))"
            taskkill.exe /PID $item.pid /T /F | Out-Null
            $stopped = $true
        }
    }

    if (-not $stopped) {
        Write-Host "No running dev processes found."
    }
}

if ($Stop) {
    Stop-DevProcesses
    exit 0
}

New-Item -ItemType Directory -Force -Path $BackendLogDir | Out-Null

Assert-Command "npm.cmd" "Install Node.js, then reopen PowerShell."

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Assert-Command "python3.cmd" "Install Python 3.11+ or add it to PATH."
    Write-Step "Creating backend virtual environment"
    Push-Location $BackendDir
    try {
        python3.cmd -m venv .venv
    } finally {
        Pop-Location
    }
}

if (-not $NoInstall) {
    Write-Step "Installing backend dependencies"
    Push-Location $BackendDir
    try {
        & $VenvPython -m pip install -e ".[dev]"
    } finally {
        Pop-Location
    }

    Write-Step "Installing frontend dependencies"
    Push-Location $FrontendDir
    try {
        npm.cmd install
    } finally {
        Pop-Location
    }
}

if ($SetupOnly) {
    Write-Step "Setup complete"
    exit 0
}

Stop-DevProcesses

$backendOut = Join-Path $BackendLogDir "backend.out.log"
$backendErr = Join-Path $BackendLogDir "backend.err.log"
$frontendOut = Join-Path $BackendLogDir "frontend.out.log"
$frontendErr = Join-Path $BackendLogDir "frontend.err.log"

Write-Step "Starting backend on http://127.0.0.1:8000"
$backend = Start-Process `
    -FilePath $VenvPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000") `
    -WorkingDirectory $BackendDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $backendOut `
    -RedirectStandardError $backendErr `
    -PassThru

Write-Step "Starting frontend on http://127.0.0.1:5173"
$frontend = Start-Process `
    -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev") `
    -WorkingDirectory $FrontendDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $frontendOut `
    -RedirectStandardError $frontendErr `
    -PassThru

@{
    backend = @{ name = "backend"; pid = $backend.Id; log = $backendOut; errorLog = $backendErr }
    frontend = @{ name = "frontend"; pid = $frontend.Id; log = $frontendOut; errorLog = $frontendErr }
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $PidFile -Encoding UTF8

Write-Step "Waiting for backend health check"
$healthy = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2 | Out-Null
        $healthy = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $healthy) {
    Write-Warning "Backend health check did not pass yet. Check $backendErr"
}

Write-Host ""
Write-Host "Paper RAG Assistant is starting."
Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "Logs:     $BackendLogDir"
Write-Host "Stop:     .\start.cmd -Stop"
