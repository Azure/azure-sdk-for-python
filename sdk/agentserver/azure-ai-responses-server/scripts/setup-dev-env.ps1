#!/usr/bin/env pwsh
# Sets up (or refreshes) the development virtual environment.
# Usage: ./scripts/setup-dev-env.ps1 [-PythonPath <path>] [-Force]
[CmdletBinding()]
param(
    [string]$PythonPath,
    [switch]$Force,
    [switch]$Help
)
$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Host "Usage: ./scripts/setup-dev-env.ps1 [-PythonPath <path>] [-Force]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -PythonPath <path>  Path to a specific Python interpreter (default: 'python')"
    Write-Host "  -Force              Recreate the virtual environment even if it already exists"
    Write-Host "  -Help               Show this help message"
    exit 0
}

$projectRoot = Split-Path $PSScriptRoot -Parent
$venvDir = Join-Path $projectRoot '.venv'

# Resolve Python interpreter
if (-not $PythonPath) {
    $PythonPath = if (Get-Command python3 -ErrorAction SilentlyContinue) { 'python3' } else { 'python' }
}

# Verify Python is available and meets minimum version
try {
    $versionOutput = & $PythonPath -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Python command failed" }
    $parts = $versionOutput -split '\.'
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        Write-Error "Python 3.10+ is required (found $versionOutput). Use -PythonPath to specify a compatible interpreter."
        exit 1
    }
    Write-Host "[setup] Using Python $versionOutput ($PythonPath)"
} catch {
    Write-Error "Could not find a Python interpreter. Install Python 3.10+ or pass -PythonPath."
    exit 1
}

# Create or recreate virtual environment
if ((Test-Path $venvDir) -and $Force) {
    Write-Host "[setup] Removing existing virtual environment..."
    Remove-Item -Recurse -Force $venvDir
}

if (-not (Test-Path $venvDir)) {
    Write-Host "[setup] Creating virtual environment at .venv ..."
    & $PythonPath -m venv $venvDir
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create virtual environment"; exit 1 }
} else {
    Write-Host "[setup] Virtual environment already exists at .venv (use -Force to recreate)"
}

# Determine pip path inside venv
$pipPath = if ($IsWindows -or $env:OS -match 'Windows') {
    Join-Path $venvDir 'Scripts\pip'
} else {
    Join-Path $venvDir 'bin/pip'
}

# Upgrade pip
Write-Host "[setup] Upgrading pip..."
& $pipPath install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to upgrade pip"; exit 1 }

# Install the package in editable mode with dev dependencies
Write-Host "[setup] Installing package in editable mode with dev dependencies..."
& $pipPath install -e "$projectRoot[dev]" --quiet
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install package"; exit 1 }

# Determine python path inside venv for display
$venvPython = if ($IsWindows -or $env:OS -match 'Windows') {
    Join-Path $venvDir 'Scripts\python'
} else {
    Join-Path $venvDir 'bin/python'
}

Write-Host ""
Write-Host "[setup] Development environment ready."
Write-Host ""
Write-Host "Activate the environment:"
if ($IsWindows -or $env:OS -match 'Windows') {
    Write-Host "  .venv\Scripts\Activate.ps1"
} else {
    Write-Host "  source .venv/bin/activate"
}
Write-Host ""
Write-Host "Verify installation:"
Write-Host "  python -m pytest --version"
Write-Host "  ruff --version"
Write-Host "  mypy --version"
