<#
.SYNOPSIS
Creates a virtual environment while seeding with specific versions of setuptools, wheel, and pip.

.DESCRIPTION
Creates a virtual environment with three specifically targeted wheel versions. When used in conjunction with the environment variable 
VIRTUALENV_OVERRIDE_APP_DATA, further virtualenv creations will leverage these targeted wheels specifically.

.PARAMETER Pip
The targeted pip version.

.PARAMETER SetupTools
The targeted setuptools version.

.PARAMETER Wheel
The targeted wheel version.

.PARAMETER SeedDirectory
The location of the virtualenv that will be created.
#>
param (
  $Pip,
  $SetupTools,
  $Wheel,
  $SeedDirectory
)

$attempts = 0

# ensure these can be pulled down from pypi.
$env:PIP_EXTRA_INDEX_URL="https://pypi.python.org/simple"

while ($attempts -lt 3) {
  virtualenv --download --reset-app-data `
    --pip="$Pip" `
    --setuptools="$SetupTools" `
    --wheel="$Wheel" `
    "$SeedDirectory"
  if ($LASTEXITCODE -eq 0) {
    break
  }

  $attempts += 1
}

if ($LASTEXITCODE -ne 0) {
  Write-Error "Unable to successfully populate an app data directory."
  exit $LASTEXITCODE
}
