<#! 
.SYNOPSIS
Creates a virtual environment for a CI machine.

.PARAMETER VenvName
The name of the virtual environment to activate.

.PARAMETER RepoRoot
The root of the repository.
#>
param(
    [Parameter(Mandatory = $true)]
    [string] $VenvName,
    # The root of the repository should be $(Build.SourcesDirectory) passed in from template
    [Parameter(Mandatory = $true)]
    [string] $RepoRoot
)

$venvPath = Join-Path $RepoRoot $VenvName
if (!(Test-Path $venvPath)) {
    Write-Host "Creating virtual environment '$VenvName'."
    python -m venv "$venvPath"
    Write-Host "Virtual environment '$VenvName' created."
    Write-Host "##vso[task.setvariable variable=$($VenvName)_LOCATION]$venvPath"
}
else {
    Write-Host "Virtual environment '$VenvName' already exists. Skipping creation."
}
