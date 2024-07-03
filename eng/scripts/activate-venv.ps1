<#! 
.SYNOPSIS
Activates a virtual environment for a CI machine. Any further usages of "python" will utilize this virtual environment.

.DESCRIPTION
When activating a virtual environment, only a few things are actually functionally changed on the machine.

# 1. PATH = path to the bin directory of the virtual env. "Scripts" on windows machines
# 2. VIRTUAL_ENV = path to root of the virtual env
# 3. VIRTUAL_ENV_PROMPT = the prompt that is displayed next to the CLI cursor when the virtual env is active
# within a CI machine, we only need the PATH and VIRTUAL_ENV variables to be set.
# 4. (optional and inconsistently) _OLD_VIRTUAL_PATH = the PATH before the virtual env was activated. This is not set in this script. 

.PARAMETER VenvName
The name of the virtual environment to activate.

.PARAMETER RepoRoot
The root of the repository.
#>
param (
    [Parameter(Mandatory=$true)]
    [string]$VenvName,
    [Parameter(Mandatory=$true)]
    [string]$RepoRoot # mandatory here, but $(Build.SourcesDirectory) will be passed in the template yaml
)

Set-StrictMode -Version 4
$ErrorActionPreference = "Stop"

$venvPath = Join-Path $RepoRoot $VenvName
$venvBinPath = Join-Path $venvPath "bin"
$env:VIRTUAL_ENV = $venvPath

if (-not (Test-Path $venvPath)) {
    Write-Error "Virtual environment '$venvPath' does not exist at $venvPath"
    exit 1
}

if ($IsWindows) {
    $venvBinPath = Join-Path $venvPath "Scripts"
    $env:PATH = "$venvBinPath;$($env:PATH)"
}
else {
    $env:PATH = "$venvBinPath`:$($env:PATH)"
}

Write-Host "Activating virtual environment '$VenvName' at $venvPath via AzDO to the value '$($env:PATH)'"
Write-Host "##vso[task.setvariable variable=VIRTUAL_ENV]$($env:VIRTUAL_ENV)"
Write-Host "##vso[task.prependpath]$($env:PATH)"