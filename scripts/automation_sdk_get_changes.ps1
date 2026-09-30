#Requires -Version 5
<#
.SYNOPSIS
    Detect SDK changes for a given package and write the result to a JSON file.
.DESCRIPTION
    This script is a wrapper of python script `packaging_tools.sdk_changelog`.
    It calls `python -m packaging_tools.sdk_changelog --output-json` to run the SDK
    change detector. The detector compares the package against the latest release and
    writes a JSON file with the shape:
        { "changes": "<changelog markdown>", "hasBreakingChange": true/false }
    It does NOT modify CHANGELOG.md.
.PARAMETER PackagePath
    Path to the package.
.PARAMETER OutputJsonFile
    Path to the JSON output file to write the SDK change detection result to.
.PARAMETER SdkRepoPath
    Absolute path string where SDK code is. Optional.
#>
param(
    [Parameter(Mandatory = $true, HelpMessage = "Path to the package")]
    [string]
    $PackagePath,

    [Parameter(Mandatory = $true, HelpMessage = "Path to the JSON output file")]
    [string]
    $OutputJsonFile,

    [Parameter(Mandatory = $false, HelpMessage = "Absolute path string where SDK code is")]
    [string]
    $SdkRepoPath
)

$scriptPath = $MyInvocation.MyCommand.Path
$scriptParent = Split-Path $scriptPath -Parent
$repoRoot = (Get-Location).Path

# Change to SDK repo path if provided
if ($SdkRepoPath) {
    if (-not (Test-Path $SdkRepoPath)) {
        Write-Error "SdkRepoPath: $SdkRepoPath does not exist"
        exit 1
    }
    Write-Host "Changing directory to: $SdkRepoPath"
    Set-Location -Path $SdkRepoPath
}

if (-not (Test-Path $PackagePath)) {
    Write-Error "PackagePath: $PackagePath does not exist"
    exit 1
}

$absolutePackagePath = Resolve-Path -Path $PackagePath
Write-Host "absolutePackagePath: $absolutePackagePath"

# Resolve the output JSON path to an absolute path (the file may not exist yet)
if ([System.IO.Path]::IsPathRooted($OutputJsonFile)) {
    $absoluteOutputJsonFile = $OutputJsonFile
}
else {
    $absoluteOutputJsonFile = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $OutputJsonFile))
}
Write-Host "absoluteOutputJsonFile: $absoluteOutputJsonFile"

# Determine the correct Python path based on OS
if ($IsWindows -or ($PSVersionTable.PSEdition -eq 'Desktop')) {
    $pythonPath = ".venv\Scripts\python.exe"
}
else {
    $pythonPath = ".venv/bin/python"
}

# Validate virtual environment Python, fall back to global python if not found
if (-not (Test-Path $pythonPath)) {
    Write-Host "Virtual environment Python not found at '$pythonPath'. Falling back to 'python' on PATH."
    $pythonPath = "python"
}
$command = "$pythonPath -m packaging_tools.sdk_changelog --package-path $absolutePackagePath --output-json $absoluteOutputJsonFile"
Write-Host "running command: $command"

# Capture output first
$output = Invoke-Expression $command 2>&1

# Display the output
$output | ForEach-Object { Write-Host $_ }

# Convert to string and check for [ERROR]
$outputString = $output | Out-String

if ($outputString -match "\[ERROR\]") {
    exit 1
}
else {
    exit 0
}
