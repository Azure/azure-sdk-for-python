<#!
.SYNOPSIS
Creates a virtual environment for a CI machine.

.DESCRIPTION
If the virtual environment directory already exists, it will skip creation but still update pip. The location of the virtual environment will be stored in a variable
named <VenvName>_LOCATION. The location will be RepoRoot + VenvName.

.PARAMETER VenvName
The name of the virtual environment which will be created.

.PARAMETER RepoRoot
The root of the repository.
#>
param(
    [Parameter(Mandatory = $true)]
    [string] $VenvName,
    # The root of the repository should be $(Build.SourcesDirectory) passed in from template
    [Parameter(Mandatory = $true)]
    [string] $RepoRoot,
    [bool] $UseUv = $true
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$venvPath = Join-Path $RepoRoot $VenvName
$bootstrap = "$RepoRoot/eng/tools/azure-sdk-tools/ci_tools/bootstrap.py"

if ($UseUv) {
    python $bootstrap --uv
}
else {
    python $bootstrap
}

if (!(Test-Path $venvPath)) {
    $invokingPython = (Get-Command "python").Source

    if ($UseUv) {
        Write-Host "Creating virtual environment '$VenvName' using uv."
        python -m uv venv --python $invokingPython $venvPath --verbose
    }
    else {
        Write-Host "Creating virtual environment '$VenvName' using virtualenv and python located at '$invokingPython'."
        python -m pip install virtualenv==20.25.1
        python -m virtualenv "$venvPath"
    }
    $pythonVersion = python --version
    Write-Host "Virtual environment '$VenvName' created at directory path '$venvPath' utilizing python version $pythonVersion."
}
else {
    Write-Host "Virtual environment '$VenvName' already exists. Skipping creation."
}

$venvPython = if ($IsWindows) {
    Join-Path $venvPath "Scripts/python.exe"
} else {
    Join-Path $venvPath "bin/python"
}
python $bootstrap --python $venvPython
Write-Host "##vso[task.setvariable variable=$($VenvName)_LOCATION]$venvPath"
