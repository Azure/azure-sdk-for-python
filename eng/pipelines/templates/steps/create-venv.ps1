param(
    [Parameter(Mandatory = $true)]
    [string] $VenvName,
    # The root of the repository should be $(BUild.SourcesDirectory) passed in from template
    [Parameter(Mandatory = $true)]
    [string] $RepoRoot
)

$venvPath = Join-Path $RepoRoot $VenvName
if (!(Test-Path $venvPath)) {
    Write-Host "Creating virtual environment $VenvName"
    python -m venv "$venvPath"
    Write-Host "Virtual environment $VenvName created."
}
else {
    Write-Host "Virtual environment $VenvName already exists. Skipping creation."
}

Write-Host "##vso[task.setvariable variable=$($VenvName)_LOCATION;]$venvPath"