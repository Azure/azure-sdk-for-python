
# Prerequisites (installed from PyPI in virtual environment):
#   build            - builds the wheel
#   twine            - uploads the wheel to the feed
#   keyring          - credential storage backend
#   artifacts-keyring - Azure AD authentication for Azure DevOps feeds
#
# Feed permission:
#   You must have the Contributor role on the foundry feed to upload.
#   Ask the feed owner to add you at:
#   https://msdata.visualstudio.com/Vienna/_artifacts/feed/foundry@Local -> Settings -> Permissions
#
# Usage:
#   .\publish_private_wheel.ps1               # default: dev1
#   .\publish_private_wheel.ps1 -DevNumber 2  # re-upload same base version (bump dev number to avoid 409)

[CmdletBinding()]
param(
    [int] $DevNumber = 1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$LABEL = "foundry.prpr"

$PACKAGE_NAME    = "azure-ai-projects"
$FEED_UPLOAD_URL = "https://pkgs.dev.azure.com/msdata/Vienna/_packaging/foundry/pypi/upload/"
$FEED_BROWSE_URL = "https://msdata.visualstudio.com/Vienna/_artifacts/feed/foundry@Local"

$PackageRoot = $PSScriptRoot
$VersionFile = Join-Path $PackageRoot "azure\ai\projects\_version.py"
$DistDir     = Join-Path $PackageRoot "dist"

# Read and compute private version
$versionContent = Get-Content $VersionFile -Raw
if ($versionContent -notmatch "VERSION\s*=\s*`"([^`"]+)`"") {
    Write-Error "Could not parse VERSION in $VersionFile"
    exit 1
}
$baseVersion    = ($Matches[1] -split "\+")[0] -replace "\.dev\d+$", ""
$privateVersion = if ($DevNumber -gt 0) { "${baseVersion}.dev${DevNumber}+${LABEL}" } else { "${baseVersion}+${LABEL}" }

Write-Host "  $PACKAGE_NAME  $baseVersion  ->  $privateVersion" -ForegroundColor Cyan

# Build wheel (patch _version.py temporarily, always restore)
$originalContent = Get-Content $VersionFile -Raw
[System.IO.File]::WriteAllText($VersionFile, ($originalContent -replace "VERSION\s*=\s*`"[^`"]+`"", "VERSION = `"$privateVersion`""))

try {
    if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
    Push-Location $PackageRoot
    try {
        $env:PIP_CONFIG_FILE = "NUL"   # prevent pip.ini from redirecting setuptools/wheel to the private feed
        python -m build --wheel --outdir $DistDir
        if ($LASTEXITCODE -ne 0) { Write-Error "Build failed."; exit 1 }
    } finally {
        Remove-Item Env:\PIP_CONFIG_FILE -ErrorAction SilentlyContinue
        Pop-Location
    }
} finally {
    [System.IO.File]::WriteAllText($VersionFile, $originalContent)
}

$wheel = (Get-ChildItem $DistDir -Filter "*.whl" -ErrorAction SilentlyContinue)[0]
if (-not $wheel) { Write-Error "No .whl found in $DistDir."; exit 1 }
Write-Host "  Built: $($wheel.Name)" -ForegroundColor Green

# Upload via Azure AD (browser on first use, silent after via cached MSAL token)
twine upload --repository-url $FEED_UPLOAD_URL $wheel.FullName

if ($LASTEXITCODE -ne 0) {
    Write-Host "  403 = missing Contributor role: $FEED_BROWSE_URL -> Settings -> Permissions" -ForegroundColor Red
    Write-Host "  409 = version exists, re-run with -DevNumber $($DevNumber + 1)" -ForegroundColor Red
    exit 1
}

Remove-Item $DistDir -Recurse -Force

Write-Host "  Uploaded : $PACKAGE_NAME==$privateVersion" -ForegroundColor Green
Write-Host "  Feed     : $FEED_BROWSE_URL" -ForegroundColor White
Write-Host "  Install  : pip install `"$PACKAGE_NAME==$privateVersion`"" -ForegroundColor White

# ---
# To install this package from the private feed (one-time setup per machine):
#   1. pip install keyring artifacts-keyring --index-url https://pypi.org/simple/
#   2. Create %APPDATA%\pip\pip.ini with:
#        [global]
#        index-url = https://pypi.org/simple/
#        extra-index-url = https://pkgs.dev.azure.com/msdata/Vienna/_packaging/foundry/pypi/simple/
#      NOTE: Keep PyPI as index-url (primary). Foundry must be extra-index-url so that
#            build tools (setuptools, wheel) resolve from PyPI without auth issues.
#   3. pip install "azure-ai-projects==2.0.2.dev1+foundry.prpr"
# ---