# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

[CmdletBinding(DefaultParameterSetName = 'Provision')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Provision')] [string] $PlanPath,
    [Parameter(Mandatory, ParameterSetName = 'Provision')] [string] $StatePath,
    [Parameter(Mandatory, ParameterSetName = 'Provision')] [ValidateSet('q1', 'q2', 'q3', 'q4')] [string] $QueueName,
    [Parameter(ParameterSetName = 'Provision')] [switch] $ConfirmProvisioning,
    [Parameter(Mandatory, ParameterSetName = 'Admission')] [string] $BatchPlanDirectory,
    [Parameter(ParameterSetName = 'Admission')] [string] $ResolvedPlanDirectory
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'SampleCiHelpers.ps1')
if ($PSCmdlet.ParameterSetName -eq 'Admission') {
    $files = @(Get-ChildItem -LiteralPath $BatchPlanDirectory -Filter 'deployment-plan.json' -Recurse -File)
    if ($files.Count -lt 1 -or $files.Count -gt 4) { throw 'Expected one to four fresh queue plans.' }
    $plans = @(foreach ($file in $files) {
        $queue = Split-Path -Leaf (Split-Path -Parent $file.FullName)
        $item = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json -AsHashtable
        Assert-SampleRunPlan -Plan $item -QueueName $queue
        $item
    })
    $runner = Set-SampleSubscriptionContext -Plan $plans[0]
    # Resolve each immutable offline name intent before any capacity check/write.
    # No unresolved artifact is ever used by provisioning workers.
    $resolvedPlans = @()
    foreach ($item in $plans) {
        $resolvedPlans += $(if ($item.ContainsKey('identityResolution') -and $item.identityResolution -ceq 'Pending') {
            Resolve-SampleIdentitySelection -Plan $item
        } else { $item })
    }
    $plans = $resolvedPlans
    $identities = Get-SampleSharedIdentities -Plan $plans[0]
    Assert-SampleSharedIdentityGrants -Plan $plans[0] -Identities $identities -RunnerPrincipalId $runner.principalId
    Assert-SampleBatchCapacity -Plans $plans
    if ($ResolvedPlanDirectory) {
        if (Test-Path -LiteralPath $ResolvedPlanDirectory) { throw 'Resolved plan output already exists; refusing to overwrite an earlier admission.' }
        foreach ($item in $plans) {
            $directory = Join-Path $ResolvedPlanDirectory $item.queueName
            $null = New-Item -ItemType Directory -Path $directory -Force
            $item | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $directory 'deployment-plan.json') -Encoding utf8
        }
    }
    return
}
if (-not $ConfirmProvisioning) { throw 'Provisioning is disabled by default. Use -ConfirmProvisioning only for an explicitly requested live run.' }
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json -AsHashtable
Assert-SampleRunPlan -Plan $plan -QueueName $QueueName
if ($plan.ContainsKey('identityResolution') -and $plan.identityResolution -cne 'Resolved') { throw 'Only an admitted, resolved identity plan may provision resources.' }
if (Test-Path -LiteralPath $StatePath) { throw 'Deployment state already exists. Do not adopt or overwrite a previous attempt.' }
if ($plan.provisionMcp) { Assert-SampleMcpPat }

$runnerIdentity = Set-SampleSubscriptionContext -Plan $plan
$subscription = Get-SampleSubscriptionId
$exists = Invoke-SampleAzure -Arguments @('group', 'exists', '--name', $plan.resourceGroup, '--subscription', $subscription)
if ($exists) { throw 'The generated resource group already exists. No existing group will be reused, retagged, or deleted.' }

$providers = @(Invoke-SampleAzure -Arguments @('provider', 'list', '--subscription', $subscription,
    '--query', '[].{namespace:namespace,state:registrationState}'))
foreach ($namespace in @('Microsoft.CognitiveServices', 'Microsoft.Storage', 'Microsoft.DocumentDB', 'Microsoft.Search')) {
    if (@($providers | Where-Object { $_.namespace -eq $namespace -and $_.state -eq 'Registered' }).Count -ne 1) {
        throw "Provider '$namespace' must already be registered by an administrator; nothing has been provisioned."
    }
}
Assert-SampleRegionAvailability -SubscriptionId $subscription -Location $plan.location
$identities = Get-SampleSharedIdentities -Plan $plan
Assert-SampleSharedIdentityGrants -Plan $plan -Identities $identities -RunnerPrincipalId $runnerIdentity.principalId

$catalog = @(Invoke-SampleAzure -Arguments @('cognitiveservices', 'model', 'list', '--location', $plan.location, '--subscription', $subscription))
$sampleModel = Resolve-SampleModel -Catalog $catalog -Name $plan.sampleModel.name -Version $plan.sampleModel.version `
    -Sku $plan.sampleModel.sku -Capacity $plan.sampleModel.capacity
$usages = @(Invoke-SampleAzure -Arguments @('cognitiveservices', 'usage', 'list', '--location', $plan.location, '--subscription', $subscription))
Assert-SampleAccountQuota -Usages $usages -Location $plan.location
$null = Get-SampleQuotaAvailable -Usages $usages -UsageName $sampleModel.usageName -RequiredCapacity $sampleModel.capacity `
    -Description "model deployment quota for '$($sampleModel.name)'"
Write-Host ('Model preflight: {0} {1}, {2}, capacity {3}.' -f $sampleModel.name, $sampleModel.version, $sampleModel.sku, $sampleModel.capacity)

$groupDeploymentName = 'sample-ci-rg-' + $plan.ownerToken
$groupArguments = @('--name', $groupDeploymentName, '--location', $plan.location, '--subscription', $subscription,
    '--template-file', (Join-Path $PSScriptRoot 'infra/resource-group.bicep'), '--parameters',
    "location=$($plan.location)", "resourceGroupName=$($plan.resourceGroup)",
    ('runId={0}-{1}-{2}-{3}' -f $plan.definitionId, $plan.buildId, $plan.queueName, $plan.jobAttempt),
    "queueName=$($plan.queueName)",
    "ownerToken=$($plan.ownerToken)", "expiresUtc=$($plan.expiresUtc)")
Write-Host 'Validating Bicep resource-group deployment before any resource changes.'
$null = Invoke-SampleAzure -Arguments (@('deployment', 'sub', 'validate') + $groupArguments)

$standardTemplatePath = Join-Path $PSScriptRoot 'infra/standard-shared-identities.bicep'
$state = @{
    schemaVersion = 1
    plan = $plan
    subscriptionId = $subscription
    tenantId = $runnerIdentity.tenantId
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

    # Reviewed local Standard variant: no worker ARM IAM writes or per-run identities.
    $state['provisioningStep'] = 'StandardSetup'
    Write-Host 'Deploying the shared-UAMI Standard variant (capability hosts can take 10-20 minutes).'
    $standard = Invoke-SampleAzure -Arguments @('deployment', 'group', 'create', '--name', 'standard-setup',
        '--resource-group', $plan.resourceGroup, '--subscription', $subscription, '--template-file', $standardTemplatePath,
        '--parameters', "location=$($plan.location)", "accountPrefix=$($plan.accountPrefix)", 'projectPrefix=project',
        "deploymentTimestamp=$($plan.deploymentTimestamp)",
        "sharedProjectIdentityResourceId=$($identities.project.resourceId)",
        "sharedAccountIdentityResourceId=$($identities.account.resourceId)",
        "sharedSearchIdentityResourceId=$($identities.search.resourceId)",
        "sharedProjectPrincipalId=$($identities.project.principalId)")
    if ($standard.properties.provisioningState -ne 'Succeeded') { throw 'Standard setup Bicep deployment did not succeed.' }
    Save-SampleInventory -State $state -OutputPath (Join-Path $stateDirectory 'inventory-standard.json')
    Write-Host 'Shared-UAMI Standard setup completed successfully; bootstrap identities and grants were not changed.'

    $accounts = @(Invoke-SampleAzure -Arguments @('resource', 'list', '--resource-group', $plan.resourceGroup,
        '--subscription', $subscription, '--resource-type', 'Microsoft.CognitiveServices/accounts', '--query', '[].{name:name,id:id}'))
    if ($accounts.Count -ne 1 -or -not $accounts[0].name.StartsWith($plan.accountPrefix, [StringComparison]::Ordinal)) {
        throw 'Cannot identify the single Foundry account created by Standard setup.'
    }
    $projects = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url',
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
        Write-Host 'Deploying the sample model and MCP connection; Azure IAM roles are preconfigured and secret-bearing output is suppressed.'
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
    $state.environment['AZURE_TENANT_ID'] = $runnerIdentity.tenantId
    $state.environment['AZURE_RESOURCE_GROUP'] = $plan.resourceGroup
    $state['status'] = 'Ready'
    $state['provisioningStep'] = 'Complete'
} catch {
    $state['status'] = 'Failed'
    Write-Host ('Provisioning failed during step: {0}.' -f $state.provisioningStep)
    throw
} finally {
    $state | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $StatePath -Encoding utf8
    try {
        Save-SampleInventory -State $state -OutputPath (Join-Path $stateDirectory 'inventory-after.json')
    } catch {
        Write-Warning 'Resource inventory could not be captured; cleanup must still verify the exact ownership tags.'
    }
}
Write-Host 'Bicep provisioning completed. Only non-secret endpoints and resource IDs were saved for the test step.'
