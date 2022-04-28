#Requires -Version 7.0

Param(
    [string] $serviceDirectory
)

$repoRoot = Resolve-Path "$PSScriptRoot/../../"

Push-Location $repoRoot

# create a smoketests directory
$smoketestsDir = Join-Path $repoRoot eng scripts smoketest 
Write-Host "Creating a new directory for smoketests at $smoketestsDir"
New-Item -Path $smoketestsDir -ItemType Directory

# Run smoketests python script to create requirements.txt
Write-Host "Creating requirements.txt in the smoketest folder"
# virtualenv env
# env/Scripts/activate
$fileName = Join-Path $repoRoot scripts devops_tasks  get_track2_packages.py
python $fileName release
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}
Pop-Location

# Run pip install -r requirements-release.txt.
# Followed by import lib command
#If these succeed the smoke tests pass
Push-Location $smoketestsDir
Write-Host "Printing content of requirements-release.txt file:"
Get-Content requirements-release.txt
Write-Host "Installing the packages in the file recursively"
pip install -r requirements-release.txt
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}

Write-Host "The following packages are installed"
Write-Host pip list
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}
Pop-Location

# Clean-up the directory created
# Remove-Item -Path $smoketestsDir -Recurse -Force