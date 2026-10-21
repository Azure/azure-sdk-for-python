# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding(DefaultParameterSetName = 'Local')]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProfileFile,
    [Parameter(Mandatory = $true, ParameterSetName = 'Local')]
    [string]$RegistryFile,
    [Parameter(Mandatory = $true, ParameterSetName = 'Ado')]
    [ValidateRange(1, 2147483647)]
    [int]$RegistryGroupId,
    [string]$Organization = 'azure-sdk',
    [string]$Project = 'internal',
    [string]$BearerToken = $env:AZURE_DEVOPS_BEARER_TOKEN,
    [switch]$Update,
    [switch]$Run,
    [switch]$ConfirmSave,
    [string]$ExpectedDigest,
    [scriptblock]$RequestInvoker
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'TestProfileHelpers.ps1')
if ($Run -and (-not $ConfirmSave -or $ExpectedDigest -notmatch '^[0-9a-f]{64}$')) {
    throw 'Preview first; saving requires -Run -ConfirmSave and the preview ExpectedDigest.'
}
try { $testProfile = Get-Content -LiteralPath $ProfileFile -Raw | ConvertFrom-Json -ErrorAction Stop }
catch { throw 'ProfileFile must contain one valid non-secret JSON profile.' }
Assert-TestProfile $testProfile
if ($PSCmdlet.ParameterSetName -eq 'Local') {
    $registryJson = if (Test-Path -LiteralPath $RegistryFile) { [IO.File]::ReadAllText($RegistryFile) } else { '{"Version":1,"Profiles":[]}' }
    $digest = Get-TestProfileDigest $registryJson
} else {
    if ($Organization -notmatch '^[a-zA-Z0-9][a-zA-Z0-9-]*$' -or [string]::IsNullOrWhiteSpace($Project)) { throw 'Invalid ADO organization/project.' }
    $readUri = "https://dev.azure.com/$Organization/$([Uri]::EscapeDataString($Project))/_apis/distributedtask/variablegroups/$RegistryGroupId`?api-version=7.1"
    $request = @{ BearerToken = $BearerToken; RequestInvoker = $RequestInvoker }
    $group = Invoke-TestProfileRequest -Method Get -Uri $readUri @request
    $groupState = Get-TestProfileRegistryGroup $group $RegistryGroupId
    $registryJson = $groupState.Json
    $digest = $groupState.Digest
}
$profileJson = ConvertTo-Json -InputObject $testProfile -Depth 10 -Compress
$reviewDigest = Get-TestProfileDigest ("$digest`n$profileJson`n$([bool]$Update)`n$($PSCmdlet.ParameterSetName)`n$RegistryFile`n$RegistryGroupId")
if ($Run -and $ExpectedDigest -cne $reviewDigest) { throw 'The profile, action, or registry changed since preview. Preview again before saving.' }
$registry = ConvertFrom-TestProfileRegistry $registryJson
$existing = @($registry.Profiles | Where-Object { $_.TestId -ceq $testProfile.TestId })
if ($existing.Count -gt 0 -and -not $Update) { throw 'This TestId already has a profile; use -Update explicitly.' }
if ($existing.Count -eq 0 -and $Update) { throw 'This TestId is not registered; omit -Update to add it.' }
$profiles = @(@($registry.Profiles | Where-Object { $_.TestId -cne $testProfile.TestId }) + @($testProfile) | Sort-Object TestId)
$newJson = ConvertTo-Json -InputObject ([ordered]@{ Version = 1; Profiles = $profiles }) -Depth 10
$null = ConvertFrom-TestProfileRegistry $newJson
$plan = [pscustomobject]@{
    Applied = $false
    Action = if ($Update) { 'Update' } else { 'Add' }
    TestId = $testProfile.TestId
    SamplePath = $testProfile.SamplePath
    EnvironmentNames = @($testProfile.Environment.Name)
    ExpectedDigest = $reviewDigest
    Execution = 'Not run (configuration only)'
}
if (-not $Run) { return $plan }
if ($PSCmdlet.ParameterSetName -eq 'Local') {
    $directory = Split-Path -Parent ([IO.Path]::GetFullPath($RegistryFile))
    if (-not (Test-Path -LiteralPath $directory)) { $null = New-Item -ItemType Directory -Path $directory -Force }
    [IO.File]::WriteAllText([IO.Path]::GetFullPath($RegistryFile), $newJson + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
} else {
    # Variable groups have no supported revision/CAS field: serialize administration. Recheck
    # immediately before PUT to detect edits since review, but do not claim atomic concurrency.
    $fresh = Invoke-TestProfileRequest -Method Get -Uri $readUri @request
    if ((Get-TestProfileRegistryGroup $fresh $RegistryGroupId).Digest -cne $digest) {
        throw 'The registry changed during registration; preview again. No update was sent.'
    }
    $group.variables.SAMPLE_TEST_PROFILES_JSON.value = $newJson
    $body = @{
        name = $group.name; description = $group.description; type = $group.type; variables = $group.variables
        variableGroupProjectReferences = $group.variableGroupProjectReferences
    }
    $uri = "https://dev.azure.com/$Organization/_apis/distributedtask/variablegroups/$RegistryGroupId`?api-version=7.1"
    $saved = Invoke-TestProfileRequest -Method Put -Uri $uri -Body $body @request
    if ((Get-TestProfileRegistryGroup $saved $RegistryGroupId).Json -cne $newJson) {
        throw 'ADO did not confirm the profile update. Inspect Library before retrying.'
    }
}
$plan.Applied = $true
$plan