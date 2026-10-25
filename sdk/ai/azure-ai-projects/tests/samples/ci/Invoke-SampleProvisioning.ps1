# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $PlanPath,
    [Parameter(Mandatory)] [string] $StatePath,
    [Parameter(Mandatory)] [string] $StandardTemplatePath,
    [switch] $ConfirmProvisioning
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'SampleCiHelpers.ps1')
if (-not $ConfirmProvisioning) { throw 'Provisioning is disabled by default. Use -ConfirmProvisioning only for an explicitly requested live run.' }
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json -AsHashtable
Assert-SampleRunPlan -Plan $plan
if (Test-Path -LiteralPath $StatePath) { throw 'Deployment state already exists. Do not adopt or overwrite a previous attempt.' }
if ($plan.provisionMcp) { Assert-SampleMcpPat }

$runnerIdentity = Set-SampleSubscriptionContext -Plan $plan
$subscription = Get-SampleSubscriptionId
$runnerPrincipalId = $runnerIdentity.principalId
$exists = Invoke-SampleAzure -Arguments @('group', 'exists', '--name', $plan.resourceGroup, '--subscription', $subscription)
if ($exists) { throw 'The generated resource group already exists. No existing group will be reused, retagged, or deleted.' }

$providers = @(Invoke-SampleAzure -Arguments @('provider', 'list', '--subscription', $subscription,
    '--query', '[].{namespace:namespace,state:registrationState}'))
foreach ($namespace in @('Microsoft.CognitiveServices', 'Microsoft.Storage', 'Microsoft.DocumentDB', 'Microsoft.Search')) {
    if (@($providers | Where-Object { $_.namespace -eq $namespace -and $_.state -eq 'Registered' }).Count -ne 1) {
        throw "Provider '$namespace' must already be registered by an administrator; nothing has been provisioned."
    }
}

$catalog = @(Invoke-SampleAzure -Arguments @('cognitiveservices', 'model', 'list', '--location', $plan.location, '--subscription', $subscription))
$sampleModel = Resolve-SampleModel -Catalog $catalog -Name $plan.sampleModel.name -Version $plan.sampleModel.version `
    -Sku $plan.sampleModel.sku -Capacity $plan.sampleModel.capacity
$usages = @(Invoke-SampleAzure -Arguments @('cognitiveservices', 'usage', 'list', '--location', $plan.location, '--subscription', $subscription))
Assert-SampleAccountQuota -Usages $usages -Location $plan.location
foreach ($model in @($sampleModel)) {
    $quota = @($usages | Where-Object { $_.name.value -eq $model.usageName })
    if ($quota.Count -ne 1 -or ($quota[0].limit - $quota[0].currentValue) -lt $model.capacity) {
        throw "Insufficient or unverifiable quota for '$($model.name)' ($($model.usageName)); no resources were created."
    }
    Write-Host ('Model preflight: {0} {1}, {2}, capacity {3}.' -f $model.name, $model.version, $model.sku, $model.capacity)
}

$groupDeploymentName = 'sample-ci-rg-' + $plan.ownerToken
$groupArguments = @('--name', $groupDeploymentName, '--location', $plan.location, '--subscription', $subscription,
    '--template-file', (Join-Path $PSScriptRoot 'infra/resource-group.bicep'), '--parameters',
    "location=$($plan.location)", "resourceGroupName=$($plan.resourceGroup)",
    ('runId={0}-{1}-{2}' -f $plan.definitionId, $plan.buildId, $plan.jobAttempt),
    "ownerToken=$($plan.ownerToken)", "expiresUtc=$($plan.expiresUtc)")
Write-Host 'Validating Bicep resource-group deployment before any resource changes.'
$null = Invoke-SampleAzure -Arguments (@('deployment', 'sub', 'validate') + $groupArguments)

$state = @{
    schemaVersion = 1
    plan = $plan
    subscriptionId = $subscription
    resourceGroupDeployment = $groupDeploymentName
    status = 'Provisioning'
    provisioningStep = 'ResourceGroup'
}
$stateDirectory = Split-Path -Parent $StatePath
$null = New-Item -ItemType Directory -Path $stateDirectory -Force
$state | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $StatePath -Encoding utf8
'[]' | Set-Content -LiteralPath (Join-Path $stateDirectory 'inventory-before.json') -Encoding utf8

try {
    $null = Invoke-SampleAzure -Arguments (@('deployment', 'sub', 'create') + $groupArguments)
    $group = Invoke-SampleAzure -Arguments @('group', 'show', '--name', $plan.resourceGroup, '--subscription', $subscription)
    Assert-SampleResourceGroupOwnership -Plan $plan -ResourceGroup $group -SubscriptionId $subscription

    # All resource creation is performed by Bicep, including the official Standard setup.
    $state['provisioningStep'] = 'StandardSetup'
    Write-Host 'Deploying official Standard setup Bicep (capability hosts can take 10-20 minutes).' 
    $standard = Invoke-SampleAzure -Arguments @('deployment', 'group', 'create', '--name', 'standard-setup',
        '--resource-group', $plan.resourceGroup, '--subscription', $subscription, '--template-file', $StandardTemplatePath,
        '--parameters', "location=$($plan.location)", "aiFoundryName=$($plan.accountPrefix)", 'foundryProjectName=project',
        'displayName=SDK sample CI', 'projectDescription=Temporary azure-ai-projects sample test project',
        "deploymentTimestamp=$($plan.deploymentTimestamp)", 'deployApplicationInsights=false')
    if ($standard.properties.provisioningState -ne 'Succeeded') { throw 'Standard setup Bicep deployment did not succeed.' }
    Save-SampleInventory -State $state -OutputPath (Join-Path $stateDirectory 'inventory-standard.json')
    Write-Host 'Official Standard setup Bicep completed successfully.'

    $accounts = @(Invoke-SampleAzure -Arguments @('resource', 'list', '--resource-group', $plan.resourceGroup,
        '--subscription', $subscription, '--resource-type', 'Microsoft.CognitiveServices/accounts', '--query', '[].{name:name,id:id}'))
    if ($accounts.Count -ne 1 -or -not $accounts[0].name.StartsWith($plan.accountPrefix, [StringComparison]::Ordinal)) {
        throw 'Cannot identify the single Foundry account created by Standard setup.'
    }
    $projects = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--url',
        ('https://management.azure.com{0}/projects?api-version=2025-10-01-preview' -f $accounts[0].id))
    if (@($projects.value).Count -ne 1) { throw 'Cannot identify the single Foundry project created by Standard setup.' }
    $projectResourceId = [string] $projects.value[0]['id']
    if (-not $projectResourceId.StartsWith($accounts[0].id + '/projects/', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'The returned project is outside the run-owned Foundry account.'
    }
    $projectName = $projectResourceId.Split('/')[-1]

    $parameterEnvironment = @{
        SAMPLE_CI_ACCOUNT_NAME = [string] $accounts[0].name
        SAMPLE_CI_PROJECT_NAME = $projectName
        SAMPLE_CI_RUNNER_PRINCIPAL_ID = $runnerPrincipalId
        SAMPLE_CI_AGENT_NAME = [string] $plan.agentName
        SAMPLE_CI_MODEL_NAME = [string] $sampleModel.name
        SAMPLE_CI_MODEL_VERSION = [string] $sampleModel.version
        SAMPLE_CI_MODEL_SKU = [string] $sampleModel.sku
        SAMPLE_CI_MODEL_CAPACITY = [string] $sampleModel.capacity
        SAMPLE_CI_PROVISION_MCP = ([string] $plan.provisionMcp).ToLowerInvariant()
    }
    $originalEnvironment = @{}
    try {
        foreach ($entry in $parameterEnvironment.GetEnumerator()) {
            if ([string]::IsNullOrWhiteSpace([string] $entry.Value)) {
                throw "Missing live Bicep binding '$($entry.Key)'; placeholder parameter values must never be deployed."
            }
            $originalEnvironment[$entry.Key] = [Environment]::GetEnvironmentVariable($entry.Key)
            [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value)
        }
        if (-not $plan.provisionMcp) {
            $originalEnvironment['MCP_GITHUB_PAT'] = $env:MCP_GITHUB_PAT
            $env:MCP_GITHUB_PAT = ''
        }
        # readEnvironmentVariable supplies the secret to @secure() without putting it on a command line or in a file.
        $state['provisioningStep'] = 'SampleResources'
        Write-Host 'Deploying the sample model, runner roles and MCP connection; secret-bearing deployment output is suppressed.'
        $sampleResources = Invoke-SampleAzure -Arguments @('deployment', 'group', 'create', '--name', 'sample-resources',
            '--resource-group', $plan.resourceGroup, '--subscription', $subscription,
            '--parameters', (Join-Path $PSScriptRoot 'infra/sample-resources.bicepparam')) -Sensitive
    } finally {
        foreach ($entry in $originalEnvironment.GetEnumerator()) {
            [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value)
        }
    }
    if ($sampleResources.properties.provisioningState -ne 'Succeeded') { throw 'Sample resources Bicep deployment did not succeed.' }
    $state['environment'] = $sampleResources.properties.outputs.environment.value
    $state.environment['AZURE_SUBSCRIPTION_ID'] = $subscription
    $state.environment['AZURE_RESOURCE_GROUP'] = $plan.resourceGroup
    $state['status'] = 'Ready'
    $state['provisioningStep'] = 'Complete'
} catch {
    $failure = $_
    Write-Host ('Provisioning failed during step: {0}.' -f $state.provisioningStep)
    try {
        Save-SampleDeploymentDiagnostics -State $state -OutputPath (Join-Path $stateDirectory 'deployment-diagnostics.json')
    } catch {
        Write-Warning 'ARM error-code diagnostics could not be captured. Raw deployment errors remain suppressed to protect secrets.'
    }
    throw $failure
} finally {
    $state | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $StatePath -Encoding utf8
    try {
        Save-SampleInventory -State $state -OutputPath (Join-Path $stateDirectory 'inventory-after.json')
    } catch {
        Write-Warning 'Resource inventory could not be captured; cleanup must still verify the exact ownership tags.'
    }
}
Write-Host 'Bicep provisioning completed. Only non-secret endpoints and resource IDs were saved for the test step.'
