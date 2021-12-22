#Requires -Version 7.0

Param(
    [string] $serviceDirectory
)

$repoRoot = Resolve-Path "$PSScriptRoot/../../"

Push-Location $repoRoot/eng/tools/smoketests

# create a smoketests directory
$smoketestsDir = Join-Path $repoRoot sdk smoketests
Write-Host "Creating a new directory for smoketests at $smoketestsDir"
New-Item -Path $smoketestsDir -ItemType Directory

# Run smoketests script
Write-Host "Running 'go run . -serviceDirectory $serviceDirectory'"
go run . -serviceDirectory $serviceDirectory
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}

Pop-Location

# Run pip install -r requirements-nightly.txt.
# Followed by import lib command
#If these succeed the smoke tests pass
Push-Location $smoketestsDir
python get_track2_packages.py
Write-Host "Printing content of requirements-nightly.txt file:"
Get-Content requirements-nightly.txt
Write-Host "Installing the packages in the file recursively"
pip install -r requirements-nightly.txt


Pop-Location

# Clean-up the directory created
Remove-Item -Path $smoketestsDir -Recurse -Force