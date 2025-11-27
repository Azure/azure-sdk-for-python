#Requires -Version 5
<#
.SYNOPSIS
    Update version for a given package.
.DESCRIPTION
    This script is a wrapper of python script `packaging_tools.sdk_update_version`.
    It calls `python -m packaging_tools.sdk_update_version` to update version.
.PARAMETER PackagePath
    Path to the package.
.PARAMETER ReleaseType
    Release type. Must be either "stable" or "beta".
.PARAMETER Version
    Version string to set.
.PARAMETER ReleaseDate
    Release date in YYYY-MM-DD format.
#>
param(
    [Parameter(Mandatory=$true, HelpMessage="Path to the package")]
    [string]
    $PackagePath,

    [Parameter(Mandatory=$false, HelpMessage="Release type (stable or beta)")]
    [ValidateSet("stable", "beta")]
    [string]
    $ReleaseType,

    [Parameter(Mandatory=$false, HelpMessage="Version string")]
    [string]
    $Version,

    [Parameter(Mandatory=$false, HelpMessage="Release date in YYYY-MM-DD format")]
    [ValidatePattern('^\d{4}-\d{2}-\d{2}$')]
    [string]
    $ReleaseDate
)

$scriptPath = $MyInvocation.MyCommand.Path
$scriptParent = Split-Path $scriptPath -Parent
$repoRoot = (Get-Location).Path

if (-not (Test-Path $PackagePath)) {
    Write-Error "PackagePath: $PackagePath does not exist"
    exit 1
}

$absolutePackagePath = Resolve-Path -Path $PackagePath
Write-Host "absolutePackagePath: $absolutePackagePath"

# Build the command with required parameter
$command = "python -m packaging_tools.sdk_update_version --package-path $absolutePackagePath"

# Add optional parameters if provided
if ($ReleaseType) {
    $command += " --release-type $ReleaseType"
}

if ($Version) {
    $command += " --version $Version"
}

if ($ReleaseDate) {
    $command += " --release-date $ReleaseDate"
}

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
