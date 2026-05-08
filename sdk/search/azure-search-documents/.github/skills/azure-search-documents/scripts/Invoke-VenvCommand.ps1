<#
.SYNOPSIS
    Runs any command inside the package .venv. Self-contained — no shell
    activation state required. Aborts if the .venv is missing.

.EXAMPLE
    .\.github\skills\azure-search-documents\scripts\Invoke-VenvCommand.ps1 azpysdk pylint .
    .\.github\skills\azure-search-documents\scripts\Invoke-VenvCommand.ps1 python -m pytest tests\
    .\.github\skills\azure-search-documents\scripts\Invoke-VenvCommand.ps1 pip list
#>

if ($args.Count -eq 0) {
    Write-Error "Usage: Invoke-VenvCommand.ps1 <command> [args...]"
    exit 2
}

$pkgRoot     = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$venvScripts = Join-Path $pkgRoot ".venv\Scripts"

if (-not (Test-Path (Join-Path $venvScripts "python.exe"))) {
    Write-Error @"
FATAL: .venv missing at $pkgRoot\.venv.
Bootstrap it with:
    cd $pkgRoot
    python -m venv .venv
    .\.venv\Scripts\python -m pip install -r dev_requirements.txt
    .\.venv\Scripts\python -m pip install -e .
Then retry.
"@
    exit 1
}

$env:VIRTUAL_ENV = Join-Path $pkgRoot ".venv"
$env:PATH = "$venvScripts;$env:PATH"

Push-Location $pkgRoot
try {
    if ($args.Count -eq 1) {
        & $args[0]
    } else {
        & $args[0] @($args[1..($args.Count - 1)])
    }
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
