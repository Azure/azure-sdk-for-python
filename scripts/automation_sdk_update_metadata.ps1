#Requires -Version 5
<#
.SYNOPSIS
    Update metadata for a given package.
.DESCRIPTION
    This script is a wrapper of python script `packaging_tools.sdk_update_metadata`.
    It calls `python -m packaging_tools.sdk_update_metadata` to update metadata.
.PARAMETER packagePath
    Path to the package.
#>
param(
    [Parameter(Mandatory=$true, HelpMessage="Path to the package")]
    [string]
    $packagePath
)

$scriptPath = $MyInvocation.MyCommand.Path
$scriptParent = Split-Path $scriptPath -Parent
$repoRoot = (Get-Location).Path

if (-not (Test-Path $packagePath)) {
    Write-Error "packagePath: $packagePath does not exist"
    exit 1
}

$absolutePackagePath = Resolve-Path -Path $packagePath
Write-Host "absolutePackagePath: $absolutePackagePath"

$command = "python -m packaging_tools.sdk_update_metadata --package-path $absolutePackagePath"
Write-Host "running command: $command"

# Capture output first
$output = Invoke-Expression $command 2>&1

# Display the output
$output | ForEach-Object { Write-Host $_ }

# Convert to string and check for [ERROR]
$outputString = $output | Out-String

if ($outputString -match "\[ERROR\]") {
    exit 1
} else {
    exit 0
}

