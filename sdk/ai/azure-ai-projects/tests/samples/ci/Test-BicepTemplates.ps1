# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.0

[CmdletBinding()]
param([Parameter(Mandatory)] [string] $StandardTemplatePath)

$ErrorActionPreference = 'Stop'
foreach ($path in @((Join-Path $PSScriptRoot 'infra/resource-group.bicep'),
    (Join-Path $PSScriptRoot 'infra/sample-resources.bicep'), $StandardTemplatePath)) {
    $compiled = @(& az bicep build --file $path --stdout --only-show-errors) -join [Environment]::NewLine
    if ($LASTEXITCODE -ne 0) { throw "Bicep compilation failed: $path" }
    $template = $compiled | ConvertFrom-Json -AsHashtable
    if ($path -eq (Join-Path $PSScriptRoot 'infra/sample-resources.bicep')) {
        if ($template.parameters.mcpPat.type -ne 'secureString') {
            throw 'The MCP PAT must compile to an ARM secureString parameter.'
        }
        # Typed parameters emit ARM languageVersion 2.0 with symbolic resource keys.
        if ($template.resources -isnot [System.Collections.IDictionary] -or
            $template.resources['sampleDeployment']['type'] -ne 'Microsoft.CognitiveServices/accounts/deployments') {
            throw 'Cannot verify the compiled ARM sample model resource.'
        }
        $models = @($template.resources.Values | Where-Object { $_['type'] -eq 'Microsoft.CognitiveServices/accounts/deployments' })
        if ($models.Count -ne 1 -or $template.parameters.ContainsKey('validationModel') -or
            $template.outputs.environment.value.ContainsKey('LLM_VALIDATION_PROJECT_ENDPOINT')) {
            throw 'Bicep must provision only the sample model and must not emit the external validation endpoint.'
        }
        Write-Host 'Compiled ARM verified: one sample model, no validation deployment or secret endpoint output.'
    }
    Write-Host ('Bicep compiled: {0}' -f (Split-Path -Leaf $path))
}

# Only fictional bindings are used to validate the dynamic .bicepparam file.
$bindings = @{
    SAMPLE_CI_ACCOUNT_NAME = 'example-account'
    SAMPLE_CI_PROJECT_NAME = 'example-project'
    SAMPLE_CI_RUNNER_PRINCIPAL_ID = '00000000-0000-0000-0000-000000000000'
    SAMPLE_CI_AGENT_NAME = 'sample-preview'
    SAMPLE_CI_MODEL_NAME = 'gpt-4.1'
    SAMPLE_CI_MODEL_VERSION = '2025-04-14'
    SAMPLE_CI_MODEL_SKU = 'GlobalStandard'
    SAMPLE_CI_MODEL_CAPACITY = '10'
    SAMPLE_CI_PROVISION_MCP = 'false'
    MCP_GITHUB_PAT = ''
}
$original = @{}
try {
    foreach ($entry in $bindings.GetEnumerator()) {
        $original[$entry.Key] = [Environment]::GetEnvironmentVariable($entry.Key)
        [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value)
    }
    $compiledParameters = @(& az bicep build-params --file (Join-Path $PSScriptRoot 'infra/sample-resources.bicepparam') --stdout --only-show-errors)
    if ($LASTEXITCODE -ne 0) { throw 'Bicep parameter-file compilation failed.' }
    $null = ($compiledParameters -join [Environment]::NewLine) | ConvertFrom-Json
} finally {
    foreach ($entry in $original.GetEnumerator()) { [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value) }
}
Write-Host 'Bicep parameter file compiled with fictional values; no secret values were logged or saved.'
