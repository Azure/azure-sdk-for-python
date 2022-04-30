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
virtualenv envnightly
envnightly/bin/activate
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}
Write-Host "Creating requirements.txt in the smoketest folder"
$fileName = Join-Path $repoRoot scripts devops_tasks  get_track2_packages.py
python $fileName nightly
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}
Pop-Location

# Run pip install -r requirements-nightly.txt.
# Followed by import lib command
#If these succeed the smoke tests pass
Push-Location $smoketestsDir
Write-Host "Printing content of requirements-nightly.txt file:"
Get-Content requirements-nightly.txt
Write-Host "Installing the packages in the file recursively"
pip install -r requirements-nightly.txt
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}

Write-Host "The following packages are installed"
pip list
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}
Pop-Location

Write-Host "Importing __all__ from all the installed modules"
$fileName = Join-Path $repoRoot scripts devops_tasks smoke_tests.py
python $fileName
if ($LASTEXITCODE) {
    exit $LASTEXITCODE
}

# Clean-up the directory created
Remove-Item -Path $smoketestsDir -Recurse -Force