# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $SelectionManifest,
    [Parameter(Mandatory)] [string] $OutputDirectory,
    [Parameter(Mandatory)] [ValidateSet('q1', 'q2', 'q3', 'q4')] [string] $QueueName,
    [ValidateSet('westus3')] [string] $Location = 'westus3',
    [ValidatePattern('^[A-Za-z0-9._-]+$')] [string] $ModelName = 'gpt-5.2',
    [ValidatePattern('^[A-Za-z0-9._-]+$')] [string] $ModelVersion = '2025-12-11',
    [ValidateSet('GlobalStandard', 'Standard')] [string] $ModelSku = 'GlobalStandard',
    [ValidateRange(1, 1000)] [int] $ModelCapacity = 10,
    [ValidatePattern('^\d+$')] [string] $DefinitionId = $env:SYSTEM_DEFINITIONID,
    [ValidatePattern('^\d+$')] [string] $BuildId = $env:BUILD_BUILDID,
    [ValidatePattern('^\d+$')] [string] $JobAttempt = $env:SYSTEM_JOBATTEMPT,
    [string] $PackageRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'SampleCiHelpers.ps1')
$subscription = Get-SampleSubscriptionId
$tenant = Get-SampleTenantId
$manifest = Read-SampleManifest -Path $SelectionManifest -PackageRoot $PackageRoot
$scanner = Join-Path $PackageRoot '.github/skills/azure-ai-projects-record-sample/scripts/GetSampleRequiredEnvironmentVariables.ps1'
$samplePaths = @($manifest.tests | ForEach-Object { $_.sample_path } | Sort-Object -Unique)
$required = @(& $scanner -SamplePath $samplePaths -PackageRoot $PackageRoot)
$provided = @('FOUNDRY_PROJECT_ENDPOINT', 'FOUNDRY_MODEL_NAME', 'FOUNDRY_AGENT_NAME', 'MCP_PROJECT_CONNECTION_ID',
    'LLM_VALIDATION_PROJECT_ENDPOINT', 'AZURE_SUBSCRIPTION_ID', 'AZURE_TENANT_ID', 'AZURE_RESOURCE_GROUP')
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
    queueName = $QueueName
    ownerToken = $ownerToken
    subscriptionId = $subscription
    tenantId = $tenant
    resourceGroup = 'azsdk-samples-{0}-{1}-{2}-{3}-{4}' -f $DefinitionId, $BuildId, $QueueName, $JobAttempt, $ownerToken.Substring(0, 8)
    sharedIdentities = Get-SampleSharedIdentityIds -SubscriptionId $subscription
    location = $Location
    accountPrefix = 'sdk' + $ownerToken.Substring(0, 6)
    agentName = 'sample-' + $ownerToken.Substring(0, 12)
    deploymentTimestamp = [DateTime]::UtcNow.ToString('yyyyMMddHHmmss')
    expiresUtc = [DateTime]::UtcNow.AddDays(1).ToString('o')
    sampleModel = @{ name = $ModelName; version = $ModelVersion; sku = $ModelSku; capacity = $ModelCapacity }
    provisionMcp = ($required -contains 'MCP_PROJECT_CONNECTION_ID')
    requiredEnvironment = $required
    selectedTests = @($manifest.tests)
}
Assert-SampleRunPlan -Plan $plan -QueueName $QueueName
$null = New-Item -ItemType Directory -Path $OutputDirectory -Force
$plan | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'deployment-plan.json') -Encoding utf8

Write-Host 'DRY RUN: no Azure resources, role assignments, or project connections were changed.'
Write-Host ('Target subscription from AZURE_SUBSCRIPTION_ID: {0}.' -f $subscription)
Write-Host ('Target tenant from AZURE_TENANT_ID: {0}.' -f $tenant)
Write-Host ('New resource group: {0}; region: {1}' -f $plan.resourceGroup, $Location)
Write-Host ('Test queue: {0}. Local shared-identity Standard variant: new account/project, Storage, Cosmos DB, Search and capability hosts.' -f $QueueName)
Write-Host 'Shared UAMIs and Azure service-role grants must already exist. Only native Cosmos data roles are created per run.'
Write-Host ('Sample model: {0} ({1}).' -f $ModelName, $ModelVersion)
Write-Host 'Output validation uses an existing project supplied by the LLM_VALIDATION_PROJECT_ENDPOINT environment variable; no validator is provisioned.'
Write-Host ('GitHub MCP connection: {0}; the PAT is never stored in this plan.' -f $plan.provisionMcp)
Write-Host 'Public networking. Resources incur charges until cleanup completes.'
Write-Host 'This offline preview is not ARM what-if. A live run checks identity, providers, regional dependency eligibility and model/account quota before provisioning.'
