# Diagnostic branch only: execute the real completion script using built azure-template metadata and a no-network CLI stub.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ReleasePlanId,
    [Parameter(Mandatory = $true)][string]$PackageInfoFilePath
)

Set-StrictMode -Version 4
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$completion = Join-Path $repoRoot 'eng/common/scripts/Mark-ReleasePlanCompletion.ps1'
$stub = Join-Path $PSScriptRoot 'ReleasePlan-ArgvStub.ps1'
$package = Get-Content -LiteralPath $PackageInfoFilePath -Raw | ConvertFrom-Json -AsHashtable
if ($package.Name -ne 'azure-template') { throw 'Wrong built package metadata.' }
$originalCapture = $env:RELEASE_PLAN_TEST_CAPTURE
$capture = Join-Path ([IO.Path]::GetTempPath()) ('release-plan-test-' + [guid]::NewGuid().ToString('N') + '.jsonl')
$env:RELEASE_PLAN_TEST_CAPTURE = $capture

function Assert-Argument([string[]]$Arguments, [string]$Name, [string]$Expected) {
    $index = [Array]::IndexOf($Arguments, $Name)
    if ($index -lt 0 -or $index + 1 -ge $Arguments.Count -or $Arguments[$index + 1] -ne $Expected) {
        throw "Argument '$Name' did not match '$Expected'."
    }
    return
}

try {
    & $completion -PackageInfoFilePath $PackageInfoFilePath -AzsdkExePath $stub -ReleasePlanId $ReleasePlanId
    if (-not (Test-Path -LiteralPath $capture)) { throw 'Manual ID did not reach the CLI boundary.' }
    $lines = @(Get-Content -LiteralPath $capture)
    if ($lines.Count -ne 1) { throw 'Expected exactly one manual completion call.' }
    [string[]]$arguments = $lines[0] | ConvertFrom-Json
    Assert-Argument $arguments '--release-plan-id' $ReleasePlanId
    Assert-Argument $arguments '--package-name' 'azure-template'
    Assert-Argument $arguments '--language' 'Python'
    Assert-Argument $arguments '--package-version' ([string]$package.Version)
    Assert-Argument $arguments '--status' 'Released'
    Write-Host "PASS: pipeline parameter ReleasePlanId=$ReleasePlanId reached the real completion script for built azure-template $($package.Version)."

    & $completion -PackageInfoFilePath $PackageInfoFilePath -AzsdkExePath $stub
    if (@(Get-Content -LiteralPath $capture).Count -ne 1) { throw 'Omitted ID unexpectedly updated a plan.' }
    Write-Host 'PASS: omitted ID made no completion call.'

    $sdkPr = 'https://github.com/Azure/azure-sdk-for-python/pull/123'
    & $completion -PackageInfoFilePath $PackageInfoFilePath -AzsdkExePath $stub -SdkPullRequest $sdkPr
    $lines = @(Get-Content -LiteralPath $capture)
    if ($lines.Count -ne 2) { throw 'Expected one automatic completion call.' }
    [string[]]$automaticArguments = $lines[1] | ConvertFrom-Json
    Assert-Argument $automaticArguments '--sdk-pull-request' $sdkPr
    if ('--release-plan-id' -in $automaticArguments) { throw 'Automatic completion inherited a manual ID.' }
    Write-Host 'PASS: automatic completion used the exact triggering SDK PR.'
    Write-Host 'All handoff calls used a local argv stub. No package was published and no live release plan was updated.'
}
finally {
    $env:RELEASE_PLAN_TEST_CAPTURE = $originalCapture
    Remove-Item -LiteralPath $capture -ErrorAction SilentlyContinue
}
