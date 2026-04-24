# Setup script for Azure AI Content Understanding SDK users (PowerShell)
# Mirrors scripts/setup_user_env.sh for Windows / cross-platform PowerShell.

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

# Determine script directory and package root
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = (Resolve-Path (Join-Path $ScriptDir '..\..\..\..')).Path

Write-Host "=== Azure AI Content Understanding - User Environment Setup ==="
Write-Host "Package root: $PackageRoot"
Write-Host ""

Set-Location $PackageRoot

# Resolve a usable Python interpreter.
# IMPORTANT: On Windows, plain `python`/`python3` may be a Microsoft Store stub
# that exits silently (failing `python -m venv`). Prefer the `py` launcher, and
# reject stubs located under WindowsApps.
function Resolve-Python {
    $candidates = @()
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { $candidates += @(@{ Exe = $py.Source; Args = @('-3') }) }
    foreach ($name in 'python3', 'python') {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { $candidates += @(@{ Exe = $cmd.Source; Args = @() }) }
    }
    foreach ($c in $candidates) {
        if ($c.Exe -match 'WindowsApps') { continue }
        try {
            $ver = & $c.Exe @($c.Args + '--version') 2>&1
            if ($LASTEXITCODE -eq 0 -and $ver -match 'Python 3') {
                return $c
            }
        } catch {}
    }
    return $null
}

# Step 0: Prerequisites check (Python 3.9+ with venv + pip)
Write-Host "Step 0: Checking Python prerequisites..."
$py = Resolve-Python
if (-not $py) {
    Write-Host "  [FAIL] Python 3 not found (or only Windows Store stub available)."
    Write-Host "         Install real Python and retry:"
    Write-Host "         winget install Python.Python.3.12"
    exit 1
}
$verOut = & $py.Exe @($py.Args + '-c' + 'import sys; print("%d.%d" % sys.version_info[:2])') 2>$null
if ($LASTEXITCODE -ne 0 -or -not $verOut) {
    Write-Host "  [FAIL] Could not determine Python version via '$($py.Exe) $($py.Args -join ' ')'."
    exit 1
}
$parts = $verOut.Trim().Split('.')
$major = [int]$parts[0]; $minor = [int]$parts[1]
if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
    Write-Host "  [FAIL] Found Python $verOut, need 3.9+. Install: winget install Python.Python.3.12"
    exit 1
}
& $py.Exe @($py.Args + '-c' + 'import venv') 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] 'import venv' failed. Reinstall Python with the standard installer."
    exit 1
}
& $py.Exe @($py.Args + '-m' + 'pip' + '--version') 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] pip not available. Run: $($py.Exe) $($py.Args -join ' ') -m ensurepip --upgrade"
    exit 1
}
Write-Host "  [OK] Python $verOut via '$($py.Exe) $($py.Args -join ' ')' (venv + pip OK)"
Write-Host ""

# Step 1: Check and create virtual environment
Write-Host "Step 1: Checking virtual environment..."
if (Test-Path '.venv') {
    Write-Host "  [OK] Virtual environment already exists at .venv"
} else {
    Write-Host "  Creating virtual environment..."
    $py = Resolve-Python
    if (-not $py) {
        Write-Host "  [ERROR] No usable Python 3 interpreter found." -ForegroundColor Red
        Write-Host "          Install Python 3 from https://www.python.org/downloads/ and re-run." -ForegroundColor Red
        Write-Host "          (The Microsoft Store stub at WindowsApps is not supported.)" -ForegroundColor Red
        exit 1
    }
    & $py.Exe @($py.Args + @('-m', 'venv', '.venv'))
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path '.venv')) {
        Write-Host "  [ERROR] Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] Virtual environment created at .venv"
}
Write-Host ""

# Step 2: Activate virtual environment
Write-Host "Step 2: Activating virtual environment..."
if ($IsWindows -or $PSVersionTable.PSEdition -eq 'Desktop') {
    $activate = Join-Path $PackageRoot '.venv\Scripts\Activate.ps1'
    $venvPython = Join-Path $PackageRoot '.venv\Scripts\python.exe'
} else {
    $activate = Join-Path $PackageRoot '.venv/bin/Activate.ps1'
    $venvPython = Join-Path $PackageRoot '.venv/bin/python'
}
if (-not (Test-Path $activate)) {
    Write-Host "  [ERROR] Activation script not found at $activate" -ForegroundColor Red
    exit 1
}
. $activate
Write-Host "  [OK] Virtual environment activated"
Write-Host "  Python: $venvPython"
Write-Host ""

# Step 3: Install SDK and dependencies
Write-Host "Step 3: Installing SDK and dependencies..."
Write-Host "  Installing azure-ai-contentunderstanding..."
& $venvPython -m pip install azure-ai-contentunderstanding --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "  [ERROR] pip install failed." -ForegroundColor Red; exit 1 }
Write-Host "  Installing sample dependencies..."
& $venvPython -m pip install -r dev_requirements.txt --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "  [ERROR] pip install -r dev_requirements.txt failed." -ForegroundColor Red; exit 1 }
Write-Host "  [OK] Dependencies installed"
Write-Host ""

# Step 4: Configure environment file
Write-Host "Step 4: Configuring environment file..."
if (Test-Path '.env') {
    Write-Host "  [WARN] .env file already exists - NOT overwriting"
    Write-Host "  If you want to start fresh, delete .env manually: Remove-Item .env"
} else {
    if (Test-Path 'env.sample') {
        Copy-Item 'env.sample' '.env'
        Write-Host "  [OK] Created .env from env.sample"
    } else {
        Write-Host "  [WARN] env.sample not found, skipping .env creation"
    }
}
Write-Host ""

function Set-EnvValue {
    param([string]$Key, [string]$Value)
    if (-not (Test-Path '.env')) { return }
    $content = Get-Content -Raw -Path '.env'
    $pattern = "(?m)^$([regex]::Escape($Key))=.*$"
    $replacement = "$Key=$Value"
    if ([regex]::IsMatch($content, $pattern)) {
        $content = [regex]::Replace($content, $pattern, $replacement)
    } else {
        if ($content -and -not $content.EndsWith("`n")) { $content += "`n" }
        $content += "$replacement`n"
    }
    Set-Content -Path '.env' -Value $content -NoNewline
}

# Step 5: Check and prompt for required configuration
Write-Host "Step 5: Environment variable configuration..."
Write-Host ""
Write-Host "  Required variables for running samples:"
Write-Host "  +-----------------------------------------------------------------+"
Write-Host "  | CONTENTUNDERSTANDING_ENDPOINT - Your Microsoft Foundry endpoint |"
Write-Host "  |   Example: https://my-resource.services.ai.azure.com/           |"
Write-Host "  |                                                                 |"
Write-Host "  | CONTENTUNDERSTANDING_KEY - API key (optional)                   |"
Write-Host "  |   If not set, DefaultAzureCredential is used (run 'az login')   |"
Write-Host "  +-----------------------------------------------------------------+"
Write-Host ""
Write-Host "  Required for sample_update_defaults.py (one-time model config):"
Write-Host "  +-----------------------------------------------------------------+"
Write-Host "  | GPT_4_1_DEPLOYMENT              - Your GPT-4.1 deployment name  |"
Write-Host "  | GPT_4_1_MINI_DEPLOYMENT         - Your GPT-4.1-mini deployment  |"
Write-Host "  | TEXT_EMBEDDING_3_LARGE_DEPLOYMENT - Your embedding deployment   |"
Write-Host "  +-----------------------------------------------------------------+"
Write-Host ""

$configureNow = Read-Host "Would you like to configure required variables now? (y/N)"
if ($configureNow -match '^[Yy]$') {
    Write-Host ""

    # CONTENTUNDERSTANDING_ENDPOINT
    $endpoint = Read-Host "Enter CONTENTUNDERSTANDING_ENDPOINT (e.g., https://my-resource.services.ai.azure.com/)"
    if ($endpoint) {
        Set-EnvValue 'CONTENTUNDERSTANDING_ENDPOINT' $endpoint
        Write-Host "  [OK] Set CONTENTUNDERSTANDING_ENDPOINT"
    } else {
        Write-Host "  [WARN] Skipped CONTENTUNDERSTANDING_ENDPOINT (required - please set manually)"
    }

    # CONTENTUNDERSTANDING_KEY
    $apiKey = Read-Host "Enter CONTENTUNDERSTANDING_KEY (press Enter to use DefaultAzureCredential)"
    if ($apiKey) {
        Set-EnvValue 'CONTENTUNDERSTANDING_KEY' $apiKey
        Write-Host "  [OK] Set CONTENTUNDERSTANDING_KEY"
    } else {
        Write-Host "  [INFO] Using DefaultAzureCredential - make sure to run 'az login'"
    }

    # Probe existing model defaults on the Foundry resource before prompting.
    # Exit codes:
    #   0  ALL_SET   - all 3 deployments already mapped
    #   10 PARTIAL   - some mapped, some missing
    #   2  NONE      - no defaults configured
    #   3  AUTH      - 401/403 authentication error
    #   1  OTHER     - any other error
    $gpt41 = ''
    $gpt41mini = ''
    $embedding = ''
    $skipUpdateDefaults = $false
    $probeRc = 1
    $probeOut = ''
    if ($endpoint) {
        Write-Host ""
        Write-Host "  Probing existing model defaults on the Foundry resource..."
        $probeScript = @'
import os, sys
try:
    from azure.ai.contentunderstanding import ContentUnderstandingClient
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
except Exception:
    sys.exit(1)
ep = os.environ.get("CONTENTUNDERSTANDING_ENDPOINT", "")
key = os.environ.get("CONTENTUNDERSTANDING_KEY") or None
if not ep:
    sys.exit(1)
cred = AzureKeyCredential(key) if key else DefaultAzureCredential()
try:
    d = ContentUnderstandingClient(ep, cred).get_defaults().model_deployments or {}
except ClientAuthenticationError:
    sys.exit(3)
except HttpResponseError as e:
    sys.exit(3 if e.status_code in (401, 403) else 1)
except Exception:
    sys.exit(1)
keys = ["gpt-4.1", "gpt-4.1-mini", "text-embedding-3-large"]
vals = [d.get(k, "") for k in keys]
print(";".join(f"{k}={v}" for k, v in zip(keys, vals)))
sys.exit(0 if all(vals) else (2 if not any(vals) else 10))
'@
        $env:CONTENTUNDERSTANDING_ENDPOINT = $endpoint
        $env:CONTENTUNDERSTANDING_KEY = $apiKey
        try {
            $probeOut = & $venvPython -c $probeScript 2>$null
            $probeRc = $LASTEXITCODE
        } catch {
            $probeRc = 1
        }

        if ($probeRc -eq 0 -or $probeRc -eq 10) {
            foreach ($pair in ($probeOut -split ';')) {
                $kv = $pair -split '=', 2
                if ($kv.Count -eq 2) {
                    switch ($kv[0]) {
                        'gpt-4.1'                { $gpt41     = $kv[1] }
                        'gpt-4.1-mini'           { $gpt41mini = $kv[1] }
                        'text-embedding-3-large' { $embedding = $kv[1] }
                    }
                }
            }
        }

        switch ($probeRc) {
            0 {
                Write-Host "  [OK] Detected existing defaults:"
                Write-Host "      gpt-4.1                = $gpt41"
                Write-Host "      gpt-4.1-mini           = $gpt41mini"
                Write-Host "      text-embedding-3-large = $embedding"
                $useDetected = Read-Host "  Use these detected values? (Y/n)"
                if ($useDetected -notmatch '^[Nn]$') {
                    $skipUpdateDefaults = $true
                } else {
                    $gpt41 = ''; $gpt41mini = ''; $embedding = ''
                }
            }
            10 {
                Write-Host "  [INFO] Partial defaults detected; missing entries will be prompted below."
            }
            2 {
                Write-Host "  [INFO] No existing defaults detected; continuing with manual entry."
            }
            3 {
                Write-Host "  [WARN] Probe unavailable (authentication failed)."
                Write-Host "         If you're using DefaultAzureCredential, run 'az login' and ensure"
                Write-Host "         the Cognitive Services User role is assigned. Continuing with manual entry."
            }
            default {
                Write-Host "  [WARN] Probe failed (exit=$probeRc); continuing with manual entry."
            }
        }
    }

    Write-Host ""
    Write-Host "  Model deployment configuration (for sample_update_defaults.py):"

    if (-not $gpt41) {
        $gpt41 = Read-Host "Enter GPT_4_1_DEPLOYMENT (default: gpt-4.1)"
        if (-not $gpt41) { $gpt41 = 'gpt-4.1' }
    } else {
        Write-Host "  [OK] Using detected GPT_4_1_DEPLOYMENT=$gpt41"
    }
    Set-EnvValue 'GPT_4_1_DEPLOYMENT' $gpt41

    if (-not $gpt41mini) {
        $gpt41mini = Read-Host "Enter GPT_4_1_MINI_DEPLOYMENT (default: gpt-4.1-mini)"
        if (-not $gpt41mini) { $gpt41mini = 'gpt-4.1-mini' }
    } else {
        Write-Host "  [OK] Using detected GPT_4_1_MINI_DEPLOYMENT=$gpt41mini"
    }
    Set-EnvValue 'GPT_4_1_MINI_DEPLOYMENT' $gpt41mini

    if (-not $embedding) {
        $embedding = Read-Host "Enter TEXT_EMBEDDING_3_LARGE_DEPLOYMENT (default: text-embedding-3-large)"
        if (-not $embedding) { $embedding = 'text-embedding-3-large' }
    } else {
        Write-Host "  [OK] Using detected TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=$embedding"
    }
    Set-EnvValue 'TEXT_EMBEDDING_3_LARGE_DEPLOYMENT' $embedding

    Write-Host ""
    Write-Host "  [OK] Environment variables configured"
} else {
    Write-Host ""
    Write-Host "  Please edit .env manually with your configuration:"
    Write-Host "    notepad .env"
    Write-Host "  or"
    Write-Host "    code .env"
}
Write-Host ""

# Summary
Write-Host "=== Setup Complete ==="
Write-Host ""
Write-Host "Next steps:"
Write-Host ""
Write-Host "  1. Activate virtual environment (in new terminals):"
Write-Host "     cd $PackageRoot"
if ($IsWindows -or $PSVersionTable.PSEdition -eq 'Desktop') {
    Write-Host "     .venv\Scripts\Activate.ps1"
} else {
    Write-Host "     . .venv/bin/Activate.ps1"
}
Write-Host ""
if ($skipUpdateDefaults) {
    Write-Host "  2. Model defaults already configured on your Foundry resource; skip sample_update_defaults.py."
} else {
    Write-Host "  2. Configure model defaults (one-time per Foundry resource):"
    Write-Host "     cd samples"
    Write-Host "     python sample_update_defaults.py"
}
Write-Host ""
Write-Host "  3. Run samples:"
Write-Host "     python sample_analyze_url.py"
Write-Host "     python sample_analyze_binary.py"
Write-Host ""
