#Requires -Version 5
<#
.SYNOPSIS
    Update version for a given package.
.DESCRIPTION
    This script is a wrapper of python script `packaging_tools.sdk_update_version`.
    It calls `python -m packaging_tools.sdk_update_version` to update version.
.PARAMETER packagePath
    Path to the package.
.PARAMETER releaseType
    Release type. Must be either "stable" or "beta".
.PARAMETER version
    Version string to set.
.PARAMETER releaseDate
    Release date in YYYY-MM-DD format.
#>
param(
    [Parameter(Mandatory=$true, HelpMessage="Path to the package")]
    [string]
    $packagePath,

    [Parameter(Mandatory=$false, HelpMessage="Release type (stable or beta)")]
    [ValidateSet("stable", "beta")]
    [string]
    $releaseType,

    [Parameter(Mandatory=$false, HelpMessage="Version string")]
    [string]
    $version,

    [Parameter(Mandatory=$false, HelpMessage="Release date in YYYY-MM-DD format")]
    [ValidatePattern('^\d{4}-\d{2}-\d{2}$')]
    [string]
    $releaseDate
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

# Build the command with required parameter
$command = "python -m packaging_tools.sdk_update_version --package-path $absolutePackagePath"

# Add optional parameters if provided
if ($releaseType) {
    $command += " --release-type $releaseType"
}

if ($version) {
    $command += " --version $version"
}

if ($releaseDate) {
    $command += " --release-date $releaseDate"
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
