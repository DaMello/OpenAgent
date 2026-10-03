param(
    [switch]$SkipBrowser
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host ""
Write-Host "OpenAgent bootstrap" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ was not found in PATH."
}

$Version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "Python $Version"

if (-not (Test-Path ".venv")) {
    Write-Host "Creating .venv..." -ForegroundColor Cyan
    python -m venv .venv
}

$Py = Join-Path $PWD ".venv\Scripts\python.exe"

Write-Host "Installing OpenAgent..." -ForegroundColor Cyan
& $Py -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }

& $Py -m pip install -e .
if ($LASTEXITCODE -ne 0) { throw "OpenAgent install failed" }

if (-not $SkipBrowser) {
    Write-Host "Installing local Chromium for Playwright..." -ForegroundColor Cyan
    & $Py -m playwright install chromium
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Browser install failed; the core agent is still installed." -ForegroundColor Yellow
    }
}

Write-Host "Creating runtime..." -ForegroundColor Cyan
& $Py -m openagent bootstrap
if ($LASTEXITCODE -ne 0) { throw "runtime bootstrap failed" }

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "Next:" -ForegroundColor White
Write-Host "  .\.venv\Scripts\python.exe -m openagent doctor"
Write-Host "  .\.venv\Scripts\python.exe -m openagent chat --mode high"
