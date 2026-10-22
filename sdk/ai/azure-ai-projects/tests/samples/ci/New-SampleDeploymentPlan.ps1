# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $SelectionManifest,
    [Parameter(Mandatory)] [string] $OutputDirectory,
    [ValidatePattern('^[a-z0-9]+$')] [string] $Location = 'eastus2',
    [ValidatePattern('^[A-Za-z0-9._-]+$')] [string] $ModelName = 'gpt-4.1',
    [ValidatePattern('^[A-Za-z0-9._-]+$')] [string] $ModelVersion = 'auto',
    [ValidateSet('GlobalStandard', 'Standard')] [string] $ModelSku = 'GlobalStandard',
    [ValidateRange(1, 1000)] [int] $ModelCapacity = 10,
    [ValidatePattern('^[A-Za-z0-9._-]+$')] [string] $ValidationModelVersion = 'auto',
    [ValidateRange(1, 1000)] [int] $ValidationModelCapacity = 10,
    [ValidatePattern('^\d+$')] [string] $DefinitionId = $env:SYSTEM_DEFINITIONID,
    [ValidatePattern('^\d+$')] [string] $BuildId = $env:BUILD_BUILDID,
    [ValidatePattern('^\d+$')] [string] $JobAttempt = $env:SYSTEM_JOBATTEMPT,
    [string] $PackageRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'SampleCiHelpers.ps1')
$manifest = Read-SampleManifest -Path $SelectionManifest -PackageRoot $PackageRoot
$scanner = Join-Path $PackageRoot '.github/skills/azure-ai-projects-record-sample/scripts/GetSampleRequiredEnvironmentVariables.ps1'
$samplePaths = @($manifest.tests | ForEach-Object { $_.sample_path } | Sort-Object -Unique)
$required = @(& $scanner -SamplePath $samplePaths -PackageRoot $PackageRoot)
$provided = @('FOUNDRY_PROJECT_ENDPOINT', 'FOUNDRY_MODEL_NAME', 'FOUNDRY_AGENT_NAME', 'MCP_PROJECT_CONNECTION_ID',
    'LLM_VALIDATION_PROJECT_ENDPOINT', 'AZURE_SUBSCRIPTION_ID', 'AZURE_RESOURCE_GROUP')
$unsupported = @($required | Where-Object { $_ -notin $provided })
if ($unsupported.Count -gt 0) {
    throw "Selected samples require additional provisioners or inputs: $($unsupported -join ', '). No Azure changes were made."
}

$ownerToken = [guid]::NewGuid().ToString('N')
$plan = @{
    schemaVersion = 1
    definitionId = $DefinitionId
    buildId = $BuildId
    jobAttempt = $JobAttempt
    ownerToken = $ownerToken
    resourceGroup = 'azsdk-samples-{0}-{1}-{2}-{3}' -f $DefinitionId, $BuildId, $JobAttempt, $ownerToken.Substring(0, 8)
    location = $Location
    accountPrefix = 'sdk' + $ownerToken.Substring(0, 6)
    agentName = 'sample-' + $ownerToken.Substring(0, 12)
    deploymentTimestamp = [DateTime]::UtcNow.ToString('yyyyMMddHHmmss')
    expiresUtc = [DateTime]::UtcNow.AddDays(1).ToString('o')
    sampleModel = @{ name = $ModelName; version = $ModelVersion; sku = $ModelSku; capacity = $ModelCapacity }
    validationModel = @{ name = 'gpt-5.2'; version = $ValidationModelVersion; sku = 'GlobalStandard'; capacity = $ValidationModelCapacity }
    provisionMcp = ($required -contains 'MCP_PROJECT_CONNECTION_ID')
    requiredEnvironment = $required
    selectedTests = @($manifest.tests)
}
Assert-SampleRunPlan -Plan $plan
$null = New-Item -ItemType Directory -Path $OutputDirectory -Force
$plan | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'deployment-plan.json') -Encoding utf8

Write-Host 'DRY RUN: no Azure resources, role assignments, or project connections were changed.'
Write-Host ('New resource group: {0}; region: {1}' -f $plan.resourceGroup, $Location)
Write-Host 'Bicep Standard setup: Foundry account/project, Storage, Cosmos DB, AI Search, capability hosts and RBAC.'
Write-Host ('Models: {0} ({1}), gpt-5.2 ({2}) for harness output validation.' -f $ModelName, $ModelVersion, $ValidationModelVersion)
Write-Host ('GitHub MCP connection: {0}; the PAT is never stored in this plan.' -f $plan.provisionMcp)
Write-Host 'Public networking. Resources incur charges until cleanup completes.'
Write-Host 'This offline preview is not ARM what-if. A live run checks identity, providers, model availability and quota before provisioning.'
