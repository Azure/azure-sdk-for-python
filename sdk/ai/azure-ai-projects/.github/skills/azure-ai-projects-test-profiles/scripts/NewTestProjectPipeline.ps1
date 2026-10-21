# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$FoundryProjectEndpoint,
    [Parameter(Mandatory = $true)]
    [string]$ProjectVariableGroup,
    [string]$RegistryVariableGroup = 'azure-ai-projects-test-profiles',
    [string[]]$ValueVariable = @(),
    [string]$PackageRoot,
    [switch]$Run,
    [switch]$ConfirmWrite,
    [switch]$Replace
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'TestProfileHelpers.ps1')
$endpointHash = Get-TestProjectEndpointHash $FoundryProjectEndpoint
foreach ($group in @($ProjectVariableGroup, $RegistryVariableGroup)) {
    if ($group -notmatch '^[a-zA-Z0-9][a-zA-Z0-9 _.-]{0,99}$') { throw 'Use a plain ADO variable-group name without macros or YAML characters.' }
}
if ($ProjectVariableGroup -eq $RegistryVariableGroup) { throw 'Project values and the metadata-only profile registry require separate variable groups.' }
$names = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($name in $ValueVariable) {
    if ($name -cnotmatch '^[A-Z][A-Z0-9_]*$' -or -not $names.Add($name) -or
        $name -in @('FOUNDRY_PROJECT_ENDPOINT', 'SYSTEM_ACCESSTOKEN', 'SAMPLE_TEST_PROFILE_IDS', 'SAMPLE_TEST_PROFILES_JSON')) {
        throw 'ValueVariable must contain unique uppercase ordinary value references, not reserved pipeline/endpoint variables.'
    }
}
if (-not $PackageRoot) { $PackageRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path }
$outputPath = Join-Path $PackageRoot "pipelines/projects/foundry-$endpointHash.yml"
$lines = @(
    '# Generated wrapper: endpoint values remain in ADO Library, never in this YAML.'
    'trigger: none'
    'pr: none'
    ''
    'extends:'
    '  template: /eng/pipelines/templates/stages/1es-redirect.yml'
    '  parameters:'
    '    stages:'
    '      - template: /sdk/ai/azure-ai-projects/pipelines/test-profile-project.yml'
    '        parameters:'
    "          ExpectedEndpointHash: '$endpointHash'"
    "          RegistryVariableGroup: '$RegistryVariableGroup'"
    "          ProjectVariableGroup: '$ProjectVariableGroup'"
)
if ($ValueVariable.Count -eq 0) { $lines += '          ValueVariables: []' }
else {
    $lines += '          ValueVariables:'
    foreach ($name in @($ValueVariable | Sort-Object)) { $lines += "            - $name" }
}
$yaml = ($lines -join "`n") + "`n"
$plan = [pscustomobject]@{
    Applied = $false; OutputPath = $outputPath; EndpointHash = $endpointHash
    RegistryVariableGroup = $RegistryVariableGroup; ProjectVariableGroup = $ProjectVariableGroup
    ValueVariables = @($ValueVariable | Sort-Object); PipelineCreated = $false
}
if (-not $Run) { return $plan }
if (-not $ConfirmWrite) { throw 'Preview before writing, then use -Run -ConfirmWrite after approval.' }
if ((Test-Path -LiteralPath $outputPath) -and -not $Replace) { throw 'This endpoint already has a wrapper. Use -Replace only after reviewing the replacement.' }
$directory = Split-Path -Parent $outputPath
$null = New-Item -ItemType Directory -Path $directory -Force
[IO.File]::WriteAllText($outputPath, $yaml, [Text.UTF8Encoding]::new($false))
$plan.Applied = $true
$plan