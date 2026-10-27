# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

[CmdletBinding()]
param([ValidateNotNullOrEmpty()] [string] $StandardTemplatePath)

$ErrorActionPreference = 'Stop'
$infra = Join-Path $PSScriptRoot '../infra'
$identitySkill = Join-Path $PSScriptRoot '../../../../.github/skills/azure-ai-projects-provision-identities'

function Invoke-BicepCompilation {
    param([Parameter(Mandatory)] [string] $Path, [switch] $Parameters)

    # Compile only: no deployment, authentication, downloader, or service calls.
    # Capture BOTH streams; never print compiled templates, parameter JSON, or raw diagnostics.
    $PSNativeCommandUseErrorActionPreference = $false
    $arguments = @('bicep', $(if ($Parameters) { 'build-params' } else { 'build' }),
        '--file', $Path, '--stdout', '--only-show-errors')
    $captured = $null
    $text = $null
    try {
        try {
            $captured = @(& az @arguments 2>&1)
            $exitCode = $LASTEXITCODE
        } catch {
            throw 'Local Bicep compiler invocation failed; output suppressed.'
        }
        if ($exitCode -ne 0) { throw 'Local Bicep compilation failed; output suppressed.' }
        $text = $captured -join [Environment]::NewLine
        try {
            $parsed = $text | ConvertFrom-Json -AsHashtable -ErrorAction Stop
        } catch {
            throw 'Local Bicep compiler returned invalid protected JSON; output suppressed.'
        }
        if ($parsed -isnot [System.Collections.IDictionary]) {
            throw 'Local Bicep compiler did not return a JSON object; output suppressed.'
        }
        return $parsed
    } finally {
        $captured = $null
        $text = $null
    }
}

function Get-ArmResources {
    param([Parameter(Mandatory)] [System.Collections.IDictionary] $Template, [string] $ParentType = '')

    $resources = $Template['resources']
    if ($null -eq $resources) { return }
    # Support both ordinary ARM resource arrays and languageVersion 2.0 symbolic dictionaries.
    if ($resources -is [System.Collections.IDictionary]) {
        $entries = @($resources.Values)
    } elseif ($resources -is [System.Collections.IList]) {
        $entries = @($resources)
    } else {
        throw 'Cannot inspect the compiled ARM resource collection.'
    }
    foreach ($resource in $entries) {
        if ($resource -isnot [System.Collections.IDictionary] -or [string]::IsNullOrWhiteSpace($resource['type'])) {
            throw 'Cannot inspect a compiled ARM resource.'
        }
        $type = [string] $resource['type']
        if ($ParentType -and $type -notmatch '^[^/]+\.[^/]+/') { $type = $ParentType + '/' + $type }
        [pscustomobject]@{ Type = $type; Definition = $resource }
        if ($resource.Contains('resources')) { Get-ArmResources -Template $resource -ParentType $type }
        if ($type -ieq 'Microsoft.Resources/deployments') {
            if ($resource['properties']['template'] -isnot [System.Collections.IDictionary] -or
                $resource['properties'].Contains('templateLink')) {
                throw 'Worker templates must inline nested deployments so all IAM resources can be inspected.'
            }
            Get-ArmResources -Template $resource['properties']['template']
        }
    }
}

function Assert-NoArmRoleAssignments {
    param([Parameter(Mandatory)] [object[]] $Resources)

    if (@($Resources | Where-Object { $_.Type -imatch '(^|/)Microsoft\.Authorization/roleAssignments$' }).Count -ne 0) {
        throw 'Worker templates must contain zero Microsoft.Authorization/roleAssignments, including nested deployments.'
    }
}

function Assert-SharedIdentity {
    param([Parameter(Mandatory)] [System.Collections.IDictionary] $Resource,
        [Parameter(Mandatory)] [string] $ParameterName)

    $identity = $Resource['identity']
    if ($identity -isnot [System.Collections.IDictionary] -or $identity['type'] -cne 'UserAssigned' -or
        $identity['userAssignedIdentities'] -isnot [System.Collections.IDictionary]) {
        throw 'Foundry account, project, and Search must use only their existing shared UAMIs.'
    }
    $keys = @($identity['userAssignedIdentities'].Keys)
    $expectedKey = '[parameters(''{0}'')]' -f $ParameterName
    $interpolatedKey = "[format('{0}', parameters('$ParameterName'))]"
    if ($keys.Count -ne 1 -or $keys[0] -cnotin @($expectedKey, $interpolatedKey)) {
        throw 'Each service must attach exactly its designated shared identity resource-ID parameter.'
    }
}

# Compile the three worker templates and the single bootstrap owner's two assets.
# Bootstrap IAM is intentional; only the worker graphs must contain zero ARM IAM.
$standard = Invoke-BicepCompilation -Path (Join-Path $infra 'standard-shared-identities.bicep')
$sample = Invoke-BicepCompilation -Path (Join-Path $infra 'sample-resources.bicep')
$group = Invoke-BicepCompilation -Path (Join-Path $infra 'resource-group.bicep')
foreach ($name in @('bootstrap.bicep', 'identities.bicep')) {
    $null = Invoke-BicepCompilation -Path (Join-Path $identitySkill "assets/$name")
}
# Bootstrap intentionally owns six project service grants plus an optional pipeline grant.
# Never apply the worker zero-IAM assertion to either bootstrap template or the official reference.
$standardResources = @(Get-ArmResources -Template $standard)
$sampleResources = @(Get-ArmResources -Template $sample)
Assert-NoArmRoleAssignments -Resources $standardResources
Assert-NoArmRoleAssignments -Resources $sampleResources
Assert-NoArmRoleAssignments -Resources @(Get-ArmResources -Template $group)
if ($standard['parameters']['location'].Contains('defaultValue') -or $standard['parameters']['location'].Contains('allowedValues')) {
    throw 'The worker region must be supplied by the selected MI set, never a Bicep default or fixed region allowlist.'
}
$storageResources = @($standardResources | Where-Object { $_.Type -ieq 'Microsoft.Storage/storageAccounts' })
if ($storageResources.Count -ne 1 -or $storageResources[0].Definition['sku']['name'] -cne 'Standard_ZRS') {
    throw 'The deployed StorageV2 SKU must match the Standard_ZRS regional preflight contract.'
}

foreach ($binding in @(
    @{ Type = 'Microsoft.CognitiveServices/accounts'; Parameter = 'sharedAccountIdentityResourceId' },
    @{ Type = 'Microsoft.CognitiveServices/accounts/projects'; Parameter = 'sharedProjectIdentityResourceId' },
    @{ Type = 'Microsoft.Search/searchServices'; Parameter = 'sharedSearchIdentityResourceId' }
)) {
    $serviceResources = @($standardResources | Where-Object { $_.Type -ieq $binding.Type })
    if ($serviceResources.Count -ne 1) { throw 'The Standard template must create one account, one project, and one Search service.' }
    Assert-SharedIdentity -Resource $serviceResources[0].Definition -ParameterName $binding.Parameter
}
if (@($standardResources | Where-Object { $_.Type -ieq 'Microsoft.ManagedIdentity/userAssignedIdentities' -or
        $_.Type -ieq 'Microsoft.CognitiveServices/accounts/deployments' -or
        $_.Type -ieq 'Microsoft.Insights/components' -or $_.Type -ieq 'Microsoft.OperationalInsights/workspaces' }).Count -ne 0) {
    throw 'The MCP-only Standard template must not create identities, models, or Application Insights resources.'
}
$principalParameter = $standard['parameters']['sharedProjectPrincipalId']
if ($principalParameter['type'] -cne 'string' -or $principalParameter['minLength'] -ne 36 -or
    $principalParameter['maxLength'] -ne 36 -or $principalParameter.Contains('defaultValue')) {
    throw 'The shared project principal must be a required, GUID-length string parameter.'
}
$nativeGrants = @($standardResources | Where-Object { $_.Type -ieq 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments' })
if ($nativeGrants.Count -ne 1) { throw 'The Standard bundle must retain its per-account Cosmos native data grant.' }
$nativeGrant = $nativeGrants[0].Definition
$nativeRoleDefinition = [string] $nativeGrant['properties']['roleDefinitionId']
# The compiler may retain the shared role-definition expression as an ARM variable.
if ($nativeRoleDefinition -ceq '[variables(''cosmosDataContributorRoleDefinitionId'')]') {
    $nativeRoleDefinition = [string] $standard['variables']['cosmosDataContributorRoleDefinitionId']
}
if ($nativeRoleDefinition -notmatch '00000000-0000-0000-0000-000000000002' -or
    [string] $nativeGrant['properties']['scope'] -notmatch '/dbs/enterprise_memory' -or
    $nativeGrant['properties']['principalId'] -cne $standard['outputs']['projectPrincipalId']['value'] -or
    ($nativeGrant['dependsOn'] -join ' ') -notmatch 'projectCapabilityHost|Microsoft\.CognitiveServices/accounts/projects/capabilityHosts') {
    throw 'Cosmos SQL Data Contributor must target enterprise_memory for the shared project principal after its capability host.'
}
$connections = @($standardResources | Where-Object { $_.Type -ieq 'Microsoft.CognitiveServices/accounts/projects/connections' })
$accountHosts = @($standardResources | Where-Object { $_.Type -ieq 'Microsoft.CognitiveServices/accounts/capabilityHosts' })
$projectHosts = @($standardResources | Where-Object { $_.Type -ieq 'Microsoft.CognitiveServices/accounts/projects/capabilityHosts' })
if ($connections.Count -ne 3 -or @($connections | Where-Object { $_.Definition['properties']['authType'] -cne 'AAD' }).Count -ne 0 -or
    $accountHosts.Count -ne 1 -or $projectHosts.Count -ne 1) {
    throw 'The Standard bundle must retain three AAD connections and both capability hosts.'
}

if ($sample['parameters']['mcpPat']['type'] -ine 'secureString') {
    throw 'The MCP PAT must compile to an ARM secureString parameter.'
}
$models = @($sampleResources | Where-Object { $_.Type -ieq 'Microsoft.CognitiveServices/accounts/deployments' })
if ($models.Count -ne 1 -or $sample['parameters'].Contains('validationModel') -or
    $sample['parameters'].Contains('runnerPrincipalId') -or
    $sample['outputs']['environment']['value'].Contains('LLM_VALIDATION_PROJECT_ENDPOINT') -or
    ($sample['outputs'] | ConvertTo-Json -Depth 100 -Compress) -match 'mcpPat|MCP_GITHUB_PAT') {
    throw 'Sample resources must contain one model, no runner IAM parameter, and no secret or validation endpoint output.'
}
Write-Host 'Three worker templates and two identity-skill assets compiled; shared identities, zero worker ARM IAM, native Cosmos grant, and secure single-model MCP contract verified.'

# Only fictional bindings are used to validate the dynamic .bicepparam file.
$bindings = @{
    SAMPLE_CI_ACCOUNT_NAME = 'example-account'
    SAMPLE_CI_PROJECT_NAME = 'example-project'
    SAMPLE_CI_AGENT_NAME = 'sample-preview'
    SAMPLE_CI_MODEL_NAME = 'gpt-5.2'
    SAMPLE_CI_MODEL_VERSION = '2025-12-11'
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
    $compiledParameters = Invoke-BicepCompilation -Path (Join-Path $infra 'sample-resources.bicepparam') -Parameters
    # CLI versions may return either the parameter object or a parametersJson wrapper.
    if ($compiledParameters.Contains('parametersJson')) {
        try {
            $compiledParameters = $compiledParameters['parametersJson'] | ConvertFrom-Json -AsHashtable -ErrorAction Stop
        } catch {
            throw 'Bicep returned invalid protected parameter JSON; output suppressed.'
        }
    }
    if ($compiledParameters['parameters'] -isnot [System.Collections.IDictionary] -or
        $compiledParameters['parameters'].Contains('runnerPrincipalId') -or
        $compiledParameters['parameters']['mcpPat']['value'] -cne '' -or
        $compiledParameters['parameters']['sampleModel']['value']['name'] -cne 'gpt-5.2') {
        throw 'Bicep parameter compilation must use only the fictional single-model bindings and an empty PAT.'
    }
} finally {
    foreach ($entry in $original.GetEnumerator()) { [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value) }
    $compiledParameters = $null
}
Write-Host 'Bicep parameter file compiled with fictional values; no secret values were logged or saved.'

# Optional, separate provenance check. The parent downloader remains responsible
# for fetching the original 14 pinned files; this checker never downloads or patches them.
if (-not [string]::IsNullOrWhiteSpace($StandardTemplatePath)) {
    if ((Split-Path -Leaf $StandardTemplatePath) -cne 'main.bicep') { throw 'The official reference must be the pinned main.bicep.' }
    $sourceLock = Get-Content -LiteralPath (Join-Path $infra 'standard-setup.lock.json') -Raw | ConvertFrom-Json -AsHashtable
    if ($sourceLock['repository'] -cne 'microsoft-foundry/foundry-samples' -or
        $sourceLock['commit'] -cne 'fbbe89b701c758e871922adaceea0ac0e4dae40f' -or $sourceLock['files'].Count -ne 14) {
        throw 'Unexpected official Standard source pin.'
    }
    $officialRoot = Split-Path -Parent ([IO.Path]::GetFullPath($StandardTemplatePath))
    foreach ($entry in $sourceLock['files'].GetEnumerator()) {
        if ($entry.Key -notmatch '^(main\.bicep|modules-standard/[a-z-]+\.bicep)$' -or $entry.Value -notmatch '^[a-f0-9]{64}$') {
            throw 'Invalid official Bicep source path or hash.'
        }
        $bytes = [IO.File]::ReadAllBytes((Join-Path $officialRoot $entry.Key))
        $hash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
        if ($hash -cne $entry.Value) { throw 'Official Bicep source hash mismatch; no source was changed.' }
    }
    $null = Invoke-BicepCompilation -Path $StandardTemplatePath
    Write-Host 'All 14 unchanged pinned official sources verified and compiled separately; bootstrap IAM remains allowed only outside worker templates.'
}