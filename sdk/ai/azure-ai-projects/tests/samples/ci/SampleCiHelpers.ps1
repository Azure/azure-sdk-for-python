# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot '../../../.github/skills/azure-ai-projects-provision-identities/scripts/IdentityNaming.ps1')

function Invoke-SampleAzure {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string[]] $Arguments, [switch] $Sensitive)

    if ($Sensitive) {
        # Capture both streams in memory. Only parsed error codes may leave a failed secret-bearing request.
        $output = & az @Arguments --only-show-errors --output json 2>&1
    } else {
        $output = & az @Arguments --only-show-errors --output json
    }
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        $message = "Azure operation '$($Arguments[0]) $($Arguments[1])' failed (exit $exitCode)."
        if ($Sensitive) {
            $codes = @(Get-SampleAzureCliErrorCodes -Text ($output -join [Environment]::NewLine))
            if ($codes.Count -gt 0) { $message += ' ARM error codes: ' + ($codes -join ', ') + '.' }
        }
        throw $message
    }
    $text = $output -join [Environment]::NewLine
    if (-not [string]::IsNullOrWhiteSpace($text)) {
        try {
            return ($text | ConvertFrom-Json -AsHashtable -ErrorAction Stop)
        } catch {
            if ($Sensitive) { throw 'Azure operation returned invalid protected JSON; response content was suppressed.' }
            throw
        }
    }
}

function Get-SampleStandardTemplate {
    param([Parameter(Mandatory)] [string] $OutputDirectory)

    $sourceLock = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'infra/standard-setup.lock.json') -Raw | ConvertFrom-Json -AsHashtable
    if ($sourceLock.repository -cne 'microsoft-foundry/foundry-samples' -or $sourceLock.commit -notmatch '^[a-f0-9]{40}$') {
        throw 'Invalid official Standard setup source pin.'
    }
    $baseUri = 'https://raw.githubusercontent.com/{0}/{1}/{2}/' -f $sourceLock.repository, $sourceLock.commit, $sourceLock.path
    $client = [Net.Http.HttpClient]::new()
    try {
        foreach ($entry in $sourceLock.files.GetEnumerator()) {
            if ($entry.Key -notmatch '^(main\.bicep|modules-standard/[a-z-]+\.bicep)$' -or $entry.Value -notmatch '^[a-f0-9]{64}$') {
                throw 'Invalid Bicep source path or checksum in the source pin.'
            }
            $bytes = $client.GetByteArrayAsync($baseUri + $entry.Key).GetAwaiter().GetResult()
            $checksum = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
            if ($checksum -cne $entry.Value) { throw "Official Bicep source checksum mismatch: $($entry.Key)" }
            $destination = Join-Path $OutputDirectory $entry.Key
            $null = New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force
            [IO.File]::WriteAllBytes($destination, $bytes)
        }
    } finally {
        $client.Dispose()
    }
    Write-Host ('Verified {0} official Standard setup Bicep files at commit {1}.' -f $sourceLock.files.Count, $sourceLock.commit)
    return (Join-Path $OutputDirectory 'main.bicep')
}

function Read-SampleManifest {
    param([Parameter(Mandatory)] [string] $Path, [Parameter(Mandatory)] [string] $PackageRoot)

    $manifest = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -AsHashtable
    if ($manifest['schemaVersion'] -ne 1 -or @($manifest['tests']).Count -eq 0) {
        throw 'The sample manifest is empty or has an unsupported schema.'
    }
    foreach ($test in $manifest.tests) {
        if ($test['node_id'] -notmatch '^tests/samples/test_samples(?:_async)?\.py::TestSamples(?:Async)?::\w+\[[^\r\n]+\]$') {
            throw 'Manifest contains a node outside the sync/async sample test harness.'
        }
        $samplePath = [IO.Path]::GetFullPath((Join-Path $PackageRoot $test.sample_path))
        $sampleRoot = [IO.Path]::GetFullPath((Join-Path $PackageRoot 'samples')) + [IO.Path]::DirectorySeparatorChar
        if (-not $samplePath.StartsWith($sampleRoot, [StringComparison]::OrdinalIgnoreCase) -or
            -not (Test-Path -LiteralPath $samplePath -PathType Leaf)) {
            throw 'Manifest sample path must identify an existing file under samples/.'
        }
    }
    return $manifest
}

function Get-SampleSubscriptionId {
    param([AllowNull()] [AllowEmptyString()] [string] $SubscriptionId = $env:AZURE_SUBSCRIPTION_ID)

    if ($SubscriptionId -notmatch '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$') {
        throw 'Set AZURE_SUBSCRIPTION_ID to the target Azure subscription GUID; no resources were changed.'
    }
    return ([guid] $SubscriptionId).ToString('D')
}

function Get-SampleTenantId {
    param([AllowNull()] [AllowEmptyString()] [string] $TenantId = $env:AZURE_TENANT_ID)

    if ($TenantId -notmatch '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$') {
        throw 'Set AZURE_TENANT_ID to the target Azure tenant GUID; no resources were changed.'
    }
    return ([guid] $TenantId).ToString('D')
}

function Set-SampleSubscriptionContext {
    param([Parameter(Mandatory)] [hashtable] $Plan)

    $subscription = Get-SampleSubscriptionId
    $tenant = Get-SampleTenantId
    Assert-SampleRunPlan -Plan $Plan
    if ($subscription -ine $Plan.subscriptionId) {
        throw 'AZURE_SUBSCRIPTION_ID does not match the deployment plan; no resources were changed.'
    }
    if ($tenant -ine $Plan.tenantId) {
        throw 'AZURE_TENANT_ID does not match the deployment plan; no resources were changed.'
    }
    $active = Invoke-SampleAzure -Arguments @('account', 'show') -Sensitive
    if ($active['user']['type'] -ne 'servicePrincipal') {
        throw 'An authorized Azure service connection application is required, not a personal login.'
    }
    try {
        $target = Invoke-SampleAzure -Arguments @('account', 'show', '--subscription', $subscription) -Sensitive
    } catch {
        throw 'The authorized service connection cannot access AZURE_SUBSCRIPTION_ID; no resources were changed. Use an approved connection for the target subscription.'
    }
    if ($target['id'] -ine $subscription -or $target['state'] -ne 'Enabled' -or
        $target['tenantId'] -ine $tenant -or $active['tenantId'] -ine $tenant -or
        $target['user']['type'] -ne 'servicePrincipal' -or
        $target['user']['name'] -ine $active['user']['name']) {
        throw 'The target subscription must be enabled and accessible by the same application and tenant specified by AZURE_TENANT_ID; no resources were changed.'
    }
    $identity = Get-SampleRunnerIdentity -SubscriptionId $subscription
    if ($identity.tenantId -ine $tenant -or $identity.clientId -ine $target['user']['name']) {
        throw 'The target subscription application identity does not match the authorized connection; no resources were changed.'
    }
    # Select only a subscription already accessible to this application. Never log in or change identities.
    if ($active['id'] -ine $subscription) {
        $null = Invoke-SampleAzure -Arguments @('account', 'set', '--subscription', $subscription) -Sensitive
    }
    $confirmed = Invoke-SampleAzure -Arguments @('account', 'show') -Sensitive
    if ($confirmed['id'] -ine $subscription -or $confirmed['tenantId'] -ine $identity.tenantId -or
        $confirmed['user']['type'] -ne 'servicePrincipal' -or $confirmed['user']['name'] -ine $identity.clientId) {
        throw 'Could not confirm the requested subscription application identity; no resources were changed.'
    }
    Write-Host ('Subscription preflight: AZURE_SUBSCRIPTION_ID={0}; AZURE_TENANT_ID={1}.' -f $subscription, $tenant)
    return $identity
}

function Assert-SampleRunPlan {
    param([Parameter(Mandatory)] [hashtable] $Plan, [string] $QueueName = $env:SAMPLE_QUEUE_NAME)

    if ($Plan['schemaVersion'] -ne 1 -or $Plan['definitionId'] -notmatch '^\d+$' -or $Plan['buildId'] -notmatch '^\d+$' -or
        $Plan['jobAttempt'] -notmatch '^\d+$' -or $Plan['ownerToken'] -notmatch '^[a-f0-9]{32}$' -or
        $Plan['queueName'] -cnotmatch '^q[1-4]$') {
        throw 'Invalid CI run ownership metadata.'
    }
    if ($QueueName -and $QueueName -cne $Plan.queueName) {
        throw 'The deployment plan belongs to a different test queue; no resources were changed.'
    }
    $expectedName = 'azsdk-samples-{0}-{1}-{2}-{3}-{4}' -f $Plan.definitionId, $Plan.buildId, $Plan.queueName, $Plan.jobAttempt, $Plan.ownerToken.Substring(0, 8)
    if ($Plan['resourceGroup'] -cne $expectedName) {
        throw 'Resource group does not match the run-owned ephemeral naming convention.'
    }
    $null = Get-SampleSubscriptionId -SubscriptionId $Plan['subscriptionId']
    $null = Get-SampleTenantId -TenantId $Plan['tenantId']
    if ($Plan.ContainsKey('identityNamePattern') -or $Plan.ContainsKey('projectIdentityName')) {
        $configuration = Get-SamplePlanIdentityConfiguration -Plan $Plan
        if ($Plan.ContainsKey('identityResolution')) {
            if ($Plan['identityResolution'] -cnotin @('Pending', 'Resolved') -or
                $Plan['sharedIdentityNames'] -isnot [System.Collections.IDictionary] -or $Plan.sharedIdentityNames.Count -ne 4) {
                throw 'Invalid MI name pattern resolution metadata.'
            }
            foreach ($purpose in $configuration.names.Keys) {
                if ($Plan.sharedIdentityNames[$purpose] -cne $configuration.names[$purpose]) { throw 'Unexpected shared identity binding.' }
            }
            if ($Plan['identityResolution'] -ceq 'Pending') {
                if ($Plan['location'] -cne '' -or $Plan['sharedIdentities'] -isnot [System.Collections.IDictionary] -or
                    $Plan.sharedIdentities.Count -ne 0) { throw 'Pending identity selection must not invent resource IDs or a region.' }
            } else {
                Assert-SampleResolvedIdentityBindings -Plan $Plan -Names $configuration.names
            }
        } else {
            # Preserve the exact historic naming bindings for old saved states.
            $historic = Get-SampleHistoricIdentityConfiguration -SubscriptionId $Plan.subscriptionId -ProjectIdentityName $configuration.projectIdentityName
            if ($Plan['location'] -cne $historic.location) { throw 'The planned region does not match the selected MI name pattern.' }
            if ($Plan['sharedIdentities'] -isnot [System.Collections.IDictionary] -or $Plan.sharedIdentities.Count -ne 4) {
                throw 'The deployment plan must bind the four bootstrap-owned shared identities.'
            }
            foreach ($purpose in $historic.sharedIdentities.Keys) {
                if ($Plan.sharedIdentities[$purpose] -cne $historic.sharedIdentities[$purpose]) { throw 'Unexpected shared identity binding.' }
            }
        }
    }
    foreach ($binding in @(@('SYSTEM_DEFINITIONID', 'definitionId'), @('BUILD_BUILDID', 'buildId'))) {
        $current = [Environment]::GetEnvironmentVariable($binding[0])
        if (-not [string]::IsNullOrWhiteSpace($current) -and $current -cne [string] $Plan[$binding[1]]) {
            throw 'The deployment plan belongs to a different pipeline run.'
        }
    }
}

function Get-SampleOwnershipTags {
    param([Parameter(Mandatory)] [hashtable] $Plan)

    Assert-SampleRunPlan -Plan $Plan
    return @{
        'purpose' = 'azure-ai-projects-sample-ci'
        'sample-ci-run' = '{0}-{1}-{2}-{3}' -f $Plan.definitionId, $Plan.buildId, $Plan.queueName, $Plan.jobAttempt
        'sample-ci-owner' = $Plan.ownerToken
        'sample-ci-queue' = $Plan.queueName
    }
}

function Assert-SampleResourceGroupOwnership {
    param(
        [Parameter(Mandatory)] [hashtable] $Plan,
        [Parameter(Mandatory)] [hashtable] $ResourceGroup,
        [Parameter(Mandatory)] [string] $SubscriptionId
    )

    $expectedId = '/subscriptions/{0}/resourceGroups/{1}' -f $SubscriptionId, $Plan.resourceGroup
    if ($Plan['subscriptionId'] -ine $SubscriptionId -or $ResourceGroup['id'] -ine $expectedId -or
        $ResourceGroup['tags'] -isnot [System.Collections.IDictionary]) {
        throw 'Refusing a resource group outside the deployment state or without ownership tags.'
    }
    $tags = Get-SampleOwnershipTags -Plan $Plan
    foreach ($key in $tags.Keys) {
        if ($ResourceGroup.tags[$key] -cne $tags[$key]) {
            throw 'Refusing a resource group without all exact CI ownership tags.'
        }
    }
}

function Assert-SampleMcpPat {
    # No PAT command-line parameter, .env import, or secret-bearing return value.
    if ([string] $env:MCP_GITHUB_PAT -notmatch '^(github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+)$') {
        throw 'Set MCP_GITHUB_PAT as an ADO secret containing the complete GitHub PAT (github_pat_... or ghp_...).'
    }
}

function Get-SampleSharedIdentityConfiguration {
    param([Parameter(Mandatory)] [string] $SubscriptionId,
        [AllowNull()] [AllowEmptyString()] [string] $IdentityNamePattern = 'mi-azsdk-sample-{resource}-wus3',
        [AllowNull()] [AllowEmptyString()] [string] $ProjectIdentityName)

    $subscription = Get-SampleSubscriptionId -SubscriptionId $SubscriptionId
    if ($PSBoundParameters.ContainsKey('ProjectIdentityName')) {
        if ($PSBoundParameters.ContainsKey('IdentityNamePattern')) {
            $expanded = Resolve-IdentityNamePattern -IdentityNamePattern $IdentityNamePattern
            if ($expanded.names.project -cne $ProjectIdentityName) { throw 'The saved project MI name differs from the selected MI name pattern.' }
        } else {
            $IdentityNamePattern = ConvertTo-IdentityNamePattern -ProjectIdentityName $ProjectIdentityName
        }
    }
    $naming = Resolve-IdentityNamePattern -IdentityNamePattern $IdentityNamePattern
    return @{ identityNamePattern = $naming.identityNamePattern; projectIdentityName = $naming.names.project;
        names = $naming.names; subscriptionId = $subscription }
}

function Get-SamplePlanIdentityConfiguration {
    param([Parameter(Mandatory)] [hashtable] $Plan)

    # Older saved queue states retain their exact concrete project name; plans
    # predating selection retain the original fixed set. Neither is rewritten.
    $bindings = @{ SubscriptionId = $Plan.subscriptionId }
    if ($Plan.ContainsKey('identityNamePattern')) { $bindings.IdentityNamePattern = $Plan['identityNamePattern'] }
    if ($Plan.ContainsKey('projectIdentityName')) { $bindings.ProjectIdentityName = $Plan['projectIdentityName'] }
    return Get-SampleSharedIdentityConfiguration @bindings
}

function Get-SampleSharedIdentityIds {
    param([Parameter(Mandatory)] [string] $SubscriptionId,
        [string] $IdentityNamePattern = 'mi-azsdk-sample-{resource}-wus3')

    $names = Resolve-IdentityNamePattern -IdentityNamePattern $IdentityNamePattern
    return (Get-SampleHistoricIdentityConfiguration -SubscriptionId $SubscriptionId -ProjectIdentityName $names.names.project).sharedIdentities
}

function Get-SampleHistoricIdentityConfiguration {
    param([string] $SubscriptionId, [string] $ProjectIdentityName)

    # This compatibility path is ONLY for pre-resolution saved plans. New input
    # is resolved from Azure metadata, never this original naming convention.
    if ($ProjectIdentityName -ceq 'mi-azsdk-sample-project-wus3') {
        $group = 'rg-azsdk-sample-identities-wus3'; $prefix = 'mi-azsdk-sample'; $suffix = 'wus3'; $location = 'westus3'
    } else {
        $match = [regex]::Match($ProjectIdentityName, '\Ami-azsdk-(?<set>[a-z0-9](?:[a-z0-9-]{0,22}[a-z0-9])?)-project-(?<region>[a-z][a-z0-9]{0,29})\z')
        if (-not $match.Success) { throw 'Unsupported historic project MI binding.' }
        $location = $match.Groups['region'].Value; $set = $match.Groups['set'].Value
        $group = "rg-azsdk-identities-$set-$location"; $prefix = "mi-azsdk-$set"; $suffix = $location
    }
    $ids = @{}
    foreach ($purpose in @('project', 'account', 'search', 'function')) {
        $ids[$purpose] = "/subscriptions/$SubscriptionId/resourceGroups/$group/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$prefix-$purpose-$suffix"
    }
    return @{ location = $location; sharedIdentities = $ids }
}

function Assert-SampleResolvedIdentityBindings {
    param([hashtable] $Plan, [System.Collections.IDictionary] $Names)

    if ($Plan['location'] -cnotmatch '\A[a-z][a-z0-9]{0,29}\z' -or
        $Plan['identityOwner'] -cnotmatch '\A[a-f0-9]{32}\z' -or
        $Plan['sharedIdentities'] -isnot [System.Collections.IDictionary] -or $Plan.sharedIdentities.Count -ne 4 -or
        $Plan['identityPrincipalIds'] -isnot [System.Collections.IDictionary] -or $Plan.identityPrincipalIds.Count -ne 4) {
        throw 'The deployment plan must bind the four bootstrap-owned shared identities and verified region.'
    }
    $groupPrefix = $null
    foreach ($purpose in @('project', 'account', 'search', 'function')) {
        $id = $Plan.sharedIdentities[$purpose]
        $binding = [regex]::Match([string]$id, '\A/subscriptions/(?<sub>[a-fA-F0-9-]{36})/resourceGroups/(?<rg>[^/]+)/providers/Microsoft.ManagedIdentity/userAssignedIdentities/(?<name>[^/]+)\z')
        if (-not $binding.Success -or $binding.Groups['sub'].Value -ine $Plan.subscriptionId -or
            $binding.Groups['name'].Value -cne $Names[$purpose] -or
            $Plan.identityPrincipalIds[$purpose] -notmatch '\A[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}\z' -or
            $Plan.identityPrincipalIds[$purpose] -eq '00000000-0000-0000-0000-000000000000') { throw 'Unexpected shared identity binding.' }
        if ($groupPrefix -and $groupPrefix -cne $binding.Groups['rg'].Value) { throw 'All shared identities must belong to one verified resource group.' }
        $groupPrefix = $binding.Groups['rg'].Value
    }
}

function Resolve-SampleIdentitySelection {
    param([Parameter(Mandatory)] [hashtable] $Plan)

    Assert-SampleRunPlan -Plan $Plan
    if ($Plan['identityResolution'] -cne 'Pending') { throw 'Identity selection has already been resolved; do not overwrite its bindings.' }
    $configuration = Get-SamplePlanIdentityConfiguration -Plan $Plan
    $path = '/subscriptions/' + $Plan.subscriptionId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities'
    $uri = 'https://management.azure.com' + $path + '?api-version=2023-01-31'
    $all = @(); $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    do {
        $parsed = [uri] $uri
        if ($parsed.Scheme -cne 'https' -or $parsed.Host -ine 'management.azure.com' -or $parsed.Port -ne 443 -or
            $parsed.UserInfo -or $parsed.Fragment -or $parsed.AbsolutePath -ine $path -or -not $seen.Add($uri) -or $seen.Count -gt 1000) {
            throw 'Unexpected identity metadata pagination target.'
        }
        $query = @{}
        foreach ($part in $parsed.Query.TrimStart('?').Split('&')) {
            $pair = $part.Split('=',2); $key = [uri]::UnescapeDataString($pair[0])
            if ($pair.Count -ne 2 -or $key -cnotin @('api-version','$skiptoken','skiptoken') -or $query.ContainsKey($key)) {
                throw 'Unexpected identity metadata pagination query.'
            }
            $query[$key] = [uri]::UnescapeDataString($pair[1])
        }
        if ($query['api-version'] -cne '2023-01-31') { throw 'Unexpected identity metadata pagination API version.' }
        $page = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $Plan.subscriptionId, '--url', $uri) -Sensitive
        if ($page -isnot [System.Collections.IDictionary] -or $page['value'] -isnot [System.Collections.IList] -or
            ($page.Contains('error') -and $null -ne $page['error']) -or
            ($null -ne $page['nextLink'] -and $page['nextLink'] -isnot [string])) { throw 'Cannot verify identity metadata listing.' }
        $all += @($page.value); $uri = [string] $page['nextLink']
    } while ($uri)
    $ids = @{}; $principals = @{}; $location = $null; $owner = $null
    foreach ($purpose in @('project', 'account', 'search', 'function')) {
        $candidates = @($all | Where-Object { $_ -is [System.Collections.IDictionary] -and $_['name'] -ieq $configuration.names[$purpose] })
        if ($candidates.Count -ne 1) { throw 'Each expanded MI name must identify exactly one existing identity in the explicit subscription; missing or duplicate matches are not allowed.' }
        $identity = $candidates[0]
        if ($identity['name'] -cne $configuration.names[$purpose] -or $identity['properties'] -isnot [System.Collections.IDictionary] -or
            $identity['tags'] -isnot [System.Collections.IDictionary] -or $identity['type'] -ine 'Microsoft.ManagedIdentity/userAssignedIdentities' -or
            $identity['properties']['tenantId'] -ine $Plan.tenantId -or $identity['location'] -cnotmatch '\A[a-z][a-z0-9]{0,29}\z' -or
            $identity['tags']['purpose'] -cne 'azsdk-sample-identities' -or $identity['tags']['sample-ci-retention'] -cne 'permanent' -or
            $identity['tags']['sample-ci-identity'] -cne $purpose -or $identity['tags']['sample-ci-owner'] -cnotmatch '\A[a-f0-9]{32}\z') {
            throw 'Cannot verify the bootstrap-owned shared identity metadata.'
        }
        if ($location -and $location -cne $identity.location) { throw 'All shared identities must have one verified region.' }
        if ($owner -and $owner -cne $identity.tags['sample-ci-owner']) { throw 'All shared identities must belong to one bootstrap-owned set.' }
        $location = $identity.location; $owner = $identity.tags['sample-ci-owner']
        $ids[$purpose] = $identity.id; $principals[$purpose] = $identity.properties.principalId
    }
    $resolved = @{} + $Plan
    $resolved.identityResolution = 'Resolved'; $resolved.location = $location
    $resolved.sharedIdentities = $ids; $resolved.identityPrincipalIds = $principals; $resolved.identityOwner = $owner
    Assert-SampleRunPlan -Plan $resolved
    return $resolved
}

function Get-SampleBlobOwnerCondition {
    # One-time, explicitly approved shared-subscription variant of the pinned workspace condition.
    return "((!(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read'})  AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/filter/action'}) AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write'}) ) OR (@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringLikeIgnoreCase '*-azureml-agent'))"
}

function Get-SampleProjectRoleIds {
    return @('53ca6127-db72-4b80-b1b0-d745d6d5456d', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe',
        'b7e6dc6d-f1e8-4753-8033-0f276bb0955b', '230815da-be43-4aae-9cb4-875f7bd000aa',
        '7ca78c08-252a-4471-8644-bb5ff32d4ba0', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
}

function Get-SampleSubscriptionAssignments {
    param([Parameter(Mandatory)] [string] $SubscriptionId)

    $uri = 'https://management.azure.com/subscriptions/' + (Get-SampleSubscriptionId -SubscriptionId $SubscriptionId) +
        '/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01'
    $assignments = @()
    do {
        if ($uri -notmatch '^https://management\.azure\.com/') { throw 'Unexpected authorization metadata host.' }
        $page = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $SubscriptionId, '--url', $uri) -Sensitive
        $assignments += @($page['value'])
        $uri = [string] $page['nextLink']
    } while ($uri)
    return $assignments
}

function Get-SampleSharedIdentities {
    param([Parameter(Mandatory)] [hashtable] $Plan)

    Assert-SampleRunPlan -Plan $Plan
    $configuration = Get-SamplePlanIdentityConfiguration -Plan $Plan
    if ($Plan.ContainsKey('identityResolution')) {
        if ($Plan.identityResolution -cne 'Resolved') { throw 'Resolve the MI names to verified Azure metadata before provisioning.' }
        $expected = $Plan.sharedIdentities
    } else {
        $historic = Get-SampleHistoricIdentityConfiguration -SubscriptionId $Plan.subscriptionId -ProjectIdentityName $configuration.projectIdentityName
        if ($Plan['location'] -cne $historic.location) { throw 'The planned region does not match the selected MI name pattern.' }
        $expected = $historic.sharedIdentities
    }
    if ($Plan['sharedIdentities'] -isnot [System.Collections.IDictionary] -or $Plan.sharedIdentities.Count -ne 4) {
        throw 'The deployment plan must bind the four bootstrap-owned shared identities.'
    }
    $identities = @{}
    $identityOwner = $null
    foreach ($purpose in $expected.Keys) {
        if ($Plan.sharedIdentities[$purpose] -cne $expected[$purpose]) { throw 'Unexpected shared identity binding.' }
        $identity = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $Plan.subscriptionId, '--url',
            ('https://management.azure.com{0}?api-version=2023-01-31' -f $expected[$purpose])) -Sensitive
        if ($identity -isnot [System.Collections.IDictionary] -or
            $identity['properties'] -isnot [System.Collections.IDictionary] -or $identity['tags'] -isnot [System.Collections.IDictionary] -or
            $identity['id'] -ine $expected[$purpose] -or $identity['type'] -ine 'Microsoft.ManagedIdentity/userAssignedIdentities' -or
            $identity['location'] -cne $Plan.location -or $identity['properties']['tenantId'] -ine $Plan.tenantId -or
            $identity['properties']['principalId'] -notmatch '^[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}$' -or
            $identity['properties']['principalId'] -eq '00000000-0000-0000-0000-000000000000' -or
            $identity['tags']['purpose'] -cne 'azsdk-sample-identities' -or
            $identity['tags']['sample-ci-owner'] -cnotmatch '^[a-f0-9]{32}$' -or
            $identity['tags']['sample-ci-retention'] -cne 'permanent' -or
            $identity['tags']['sample-ci-identity'] -cne $purpose) {
            throw 'Cannot verify the bootstrap-owned shared identity; no resources were changed.'
        }
        if ($identityOwner -and $identityOwner -cne $identity.tags['sample-ci-owner']) {
            throw 'The four shared identities do not belong to one bootstrap-owned set.'
        }
        $identityOwner = $identity.tags['sample-ci-owner']
        if ($Plan.ContainsKey('identityResolution') -and ($Plan.identityOwner -cne $identityOwner -or
            $Plan.identityPrincipalIds[$purpose] -ine $identity.properties.principalId)) { throw 'The resolved identity generation changed; no resources were changed.' }
        $identities[$purpose] = @{ resourceId = $identity.id; principalId = $identity.properties.principalId }
    }
    return $identities
}

function Assert-SampleSharedIdentityGrants {
    param([Parameter(Mandatory)] [hashtable] $Plan, [Parameter(Mandatory)] [hashtable] $Identities,
        [Parameter(Mandatory)] [string] $RunnerPrincipalId)

    $scope = '/subscriptions/' + $Plan.subscriptionId
    $assignments = @(Get-SampleSubscriptionAssignments -SubscriptionId $Plan.subscriptionId)
    foreach ($role in @(Get-SampleProjectRoleIds)) {
        $matching = @($assignments | Where-Object {
            $_['properties']['principalId'] -ieq $Identities.project.principalId -and
            $_['properties']['scope'] -ieq $scope -and $_['properties']['roleDefinitionId'] -ieq "$scope/providers/Microsoft.Authorization/roleDefinitions/$role"
        })
        $condition = if ($role -eq 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b') { Get-SampleBlobOwnerCondition } else { '' }
        if ($matching.Count -ne 1 -or [string] $matching[0]['properties']['condition'] -cne $condition -or
            ($condition -and $matching[0]['properties']['conditionVersion'] -cne '2.0')) {
            throw 'The approved shared project-identity service grants are missing or differ; no resources were changed.'
        }
    }
    $callerAccess = @($assignments | Where-Object {
        $_['properties']['principalId'] -ieq $RunnerPrincipalId -and $_['properties']['scope'] -ieq $scope -and
        $_['properties']['roleDefinitionId'] -ieq "$scope/providers/Microsoft.Authorization/roleDefinitions/53ca6127-db72-4b80-b1b0-d745d6d5456d" -and
        -not $_['properties']['condition']
    })
    if ($callerAccess.Count -ne 1) { throw 'Preconfigure the pipeline Foundry User grant; workers never create Azure IAM assignments.' }
}

function Assert-SampleBatchCapacity {
    param([Parameter(Mandatory)] [hashtable[]] $Plans)

    if ($Plans.Count -lt 1 -or $Plans.Count -gt 4 -or @($Plans.queueName | Sort-Object -Unique).Count -ne $Plans.Count -or
        @($Plans.resourceGroup | Sort-Object -Unique).Count -ne $Plans.Count) {
        throw 'A test batch must contain one to four distinct queue plans.'
    }
    $first = $Plans[0]
    $nodes = @()
    foreach ($plan in $Plans) {
        Assert-SampleRunPlan -Plan $plan -QueueName $plan.queueName
        $selected = @($plan['selectedTests'] | Where-Object { $null -ne $_ })
        if ($selected.Count -eq 0 -or @($selected | Where-Object { [string]::IsNullOrWhiteSpace($_['node_id']) }).Count -gt 0) {
            throw 'Each test queue must contain a nonempty selection of unique test nodes.'
        }
        $nodes += @($selected | ForEach-Object { $_['node_id'] })
        foreach ($key in @('subscriptionId', 'tenantId', 'definitionId', 'buildId', 'location', 'identityNamePattern', 'projectIdentityName')) {
            if ($plan[$key] -cne $first[$key]) { throw 'Test queues must share one explicit target and pipeline run.' }
        }
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            if ($plan['sharedIdentities'][$purpose] -cne $first['sharedIdentities'][$purpose]) {
                throw 'All test queues must use the same shared identity set.'
            }
            if ($plan.ContainsKey('identityPrincipalIds') -and
                $plan.identityPrincipalIds[$purpose] -cne $first.identityPrincipalIds[$purpose]) { throw 'All test queues must use the same verified identity generation.' }
        }
        if ($plan.ContainsKey('identityOwner') -and $plan.identityOwner -cne $first.identityOwner) { throw 'All test queues must use the same verified identity generation.' }
        if (($plan.sampleModel | ConvertTo-Json -Compress) -cne ($first.sampleModel | ConvertTo-Json -Compress)) {
            # Compare fields, not Hashtable property ordering.
            foreach ($key in @('name', 'version', 'sku', 'capacity')) {
                if ($plan.sampleModel[$key] -cne $first.sampleModel[$key]) { throw 'Test queues must use the same sample model configuration.' }
            }
        }
    }
    if (@($nodes | Sort-Object -Unique -CaseSensitive).Count -ne $nodes.Count) {
        throw 'Test queues must partition unique test nodes without repeats.'
    }
    $leftovers = @(Invoke-SampleAzure -Arguments @('group', 'list', '--subscription', $first.subscriptionId,
        '--query', "[?tags.purpose=='azure-ai-projects-sample-ci'].{id:id,name:name}" ) -Sensitive)
    if ($leftovers.Count -gt 0) { throw 'Temporary sample RGs from another attempt still exist; reconcile cleanup before admitting another batch.' }
    Assert-SampleRegionAvailability -SubscriptionId $first.subscriptionId -Location $first.location
    $usages = @(Invoke-SampleAzure -Arguments @('cognitiveservices', 'usage', 'list', '--location', $first.location, '--subscription', $first.subscriptionId))
    $null = Get-SampleQuotaAvailable -Usages $usages -UsageName 'AccountCount' -Unit 'Count' -RequiredCapacity $Plans.Count -Description 'batch Foundry account quota'
    $searchUsage = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $first.subscriptionId, '--url',
        ('https://management.azure.com/subscriptions/{0}/providers/Microsoft.Search/locations/{1}/usages?api-version=2025-05-01' -f $first.subscriptionId, $first.location)) -Sensitive
    $null = Get-SampleQuotaAvailable -Usages @($searchUsage['value']) -UsageName 'standard' -Unit 'Count' -RequiredCapacity $Plans.Count -Description 'batch Search S1 quota'
    $catalog = @(Invoke-SampleAzure -Arguments @('cognitiveservices', 'model', 'list', '--location', $first.location, '--subscription', $first.subscriptionId))
    $model = Resolve-SampleModel -Catalog $catalog -Name $first.sampleModel.name -Version $first.sampleModel.version -Sku $first.sampleModel.sku -Capacity $first.sampleModel.capacity
    $null = Get-SampleQuotaAvailable -Usages $usages -UsageName $model.usageName -RequiredCapacity ($Plans.Count * $model.capacity) -Description 'batch sample-model quota'
    Write-Host ('Admission passed for {0} fresh RGs. No cross-run lock or capacity reservation: wait for all cleanup before another run.' -f $Plans.Count)
}

function Resolve-SampleModel {
    param(
        [Parameter(Mandatory)] [object[]] $Catalog,
        [Parameter(Mandatory)] [string] $Name,
        [Parameter(Mandatory)] [string] $Version,
        [Parameter(Mandatory)] [string] $Sku,
        [Parameter(Mandatory)] [int] $Capacity
    )

    $candidates = @($Catalog | Where-Object { $_.model.name -ceq $Name -and $_.model.format -eq 'OpenAI' })
    if ($Version -eq 'auto') {
        $versions = @($candidates | Where-Object { $_.model.isDefaultVersion } | ForEach-Object { $_.model.version } | Sort-Object -Unique)
        if ($versions.Count -ne 1) {
            throw "Cannot resolve exactly one default version of '$Name'; set an explicit model version."
        }
        $Version = $versions[0]
    }
    $skuDetails = @($candidates | Where-Object { $_.model.version -ceq $Version } | ForEach-Object { $_.model.skus } |
        Where-Object { $_.name -ceq $Sku })
    if ($skuDetails.Count -eq 0) {
        throw "Model '$Name' version '$Version' with SKU '$Sku' is unavailable in the selected region."
    }
    $limits = $skuDetails[0]['capacity']
    if ($Capacity -lt 1 -or ($null -ne $limits['minimum'] -and $Capacity -lt $limits['minimum']) -or
        ($null -ne $limits['maximum'] -and $Capacity -gt $limits['maximum']) -or
        ($null -ne $limits['step'] -and $limits['step'] -gt 0 -and ($Capacity % $limits['step']) -ne 0)) {
        throw "Capacity $Capacity does not satisfy model '$Name' SKU limits."
    }
    return @{ name = $Name; version = $Version; sku = $Sku; capacity = $Capacity; usageName = $skuDetails[0]['usageName'] }
}

function Get-SampleQuotaAvailable {
    param(
        [Parameter(Mandatory)] [AllowEmptyCollection()] [object[]] $Usages,
        [Parameter(Mandatory)] [ValidateNotNullOrEmpty()] [string] $UsageName,
        [Parameter(Mandatory)] [string] $Description,
        [ValidateRange(1, 1000000)] [int] $RequiredCapacity = 1,
        [string] $Unit = ''
    )

    $quota = @($Usages | Where-Object {
        $_ -is [System.Collections.IDictionary] -and $_['name'] -is [System.Collections.IDictionary] -and
        $_['name']['value'] -ceq $UsageName
    })
    if ($quota.Count -ne 1) {
        throw "Cannot verify $Description; no resources were created."
    }
    $usage = $quota[0]
    foreach ($key in @('currentValue', 'limit')) {
        $value = $usage[$key]
        if (($value -isnot [int] -and $value -isnot [long] -and $value -isnot [double] -and $value -isnot [decimal]) -or
            -not [double]::IsFinite([double] $value) -or $value -lt 0) {
            throw "Cannot verify $Description; no resources were created."
        }
    }
    if ($Unit -and $usage['unit'] -cne $Unit) {
        throw "Cannot verify $Description; no resources were created."
    }
    $available = $usage.limit - $usage.currentValue
    if ($available -lt $RequiredCapacity -or $usage['status'] -in @('Blocked', 'InOverage', 'Unknown')) {
        $message = 'Insufficient {0} ({1}: {2}/{3}, status: {4}).' -f `
            $Description, $UsageName, $usage.currentValue, $usage.limit, $usage['status']
        throw ($message + ' No resources were created. Choose a region with available account quota or ask an administrator to review quota; ' +
            'existing accounts will not be deleted.')
    }
    return $available
}

function Assert-SampleAccountQuota {
    param(
        [Parameter(Mandatory)] [AllowEmptyCollection()] [object[]] $Usages,
        [Parameter(Mandatory)] [string] $Location
    )

    # Account creation has a separate quota from model deployment capacity.
    $available = Get-SampleQuotaAvailable -Usages $Usages -UsageName 'AccountCount' -Unit 'Count' `
        -Description "Cognitive Services account quota in '$Location'"
    Write-Host ('Account preflight: {0}, AccountCount available slots: {1}.' -f $Location, $available)
}

function Assert-SampleRegionAvailability {
    param(
        [Parameter(Mandatory)] [string] $SubscriptionId,
        [Parameter(Mandatory)] [ValidatePattern('^[a-z0-9]+$')] [string] $Location
    )

    $subscription = Get-SampleSubscriptionId -SubscriptionId $SubscriptionId
    $root = 'https://management.azure.com'
    $scope = "$root/subscriptions/$subscription/providers"
    $offerings = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url',
        "$root/providers/Microsoft.Search/offerings?api-version=2025-02-01-preview") -Sensitive
    $searchRegions = @($offerings['value'] | Where-Object { ($_['regionName'] -replace '\s', '') -ieq $Location })
    if ($searchRegions.Count -ne 1) { throw "Cannot verify AI Search offerings in '$Location'; no resources were created." }
    $searchSkus = @($searchRegions[0]['skus'] | Where-Object {
        $_['name'] -ceq 'standard' -or ($_['sku'] -and $_['sku']['name'] -ceq 'standard')
    })
    if ($searchSkus.Count -ne 1) { throw "AI Search S1 is not offered in '$Location'; no resources were created." }
    $searchUsage = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url',
        "$scope/Microsoft.Search/locations/$Location/usages?api-version=2025-05-01") -Sensitive
    $null = Get-SampleQuotaAvailable -Usages @($searchUsage['value']) -UsageName 'standard' -Unit 'Count' `
        -Description "AI Search S1 service quota in '$Location'"

    $cosmosLocations = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url',
        "$scope/Microsoft.DocumentDB/locations?api-version=2025-04-15") -Sensitive
    $cosmosRegions = @($cosmosLocations['value'] | Where-Object { ($_['name'] -replace '\s', '') -ieq $Location })
    if ($cosmosRegions.Count -ne 1) { throw "Cannot verify Cosmos DB regional access in '$Location'; no resources were created." }
    $access = $cosmosRegions[0]['properties']['isSubscriptionRegionAccessAllowedForRegular']
    if ($access -isnot [bool] -or -not $access) {
        throw "Cosmos DB account creation is not allowed for this subscription in '$Location'; no resources were created."
    }

    # Match the deployed local shared-identity template, not the upstream
    # reference's regional GRS fallback. Never approve a different SKU's evidence.
    $storageSku = 'Standard_ZRS'
    $storageSkus = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url',
        "$scope/Microsoft.Storage/skus?api-version=2023-05-01") -Sensitive
    $storage = @($storageSkus['value'] | Where-Object {
        $_['name'] -ceq $storageSku -and $_['kind'] -ceq 'StorageV2' -and
        $Location -iin @($_['locations'] | ForEach-Object { $_ -replace '\s', '' })
    })
    if ($storage.Count -ne 1) { throw "Cannot verify StorageV2 $storageSku in '$Location'; no resources were created." }
    foreach ($restriction in @($storage[0]['restrictions'] | Where-Object { $null -ne $_ })) {
        $restricted = @($restriction['values'] | ForEach-Object { $_ -replace '\s', '' })
        if ($restriction['type'] -ine 'Location' -or $restricted.Count -eq 0 -or $Location -iin $restricted) {
            throw "StorageV2 $storageSku is restricted in '$Location'; no resources were created."
        }
    }
    Write-Host ('Regional dependency preflight: {0}, Search S1, Cosmos DB and StorageV2 {1} are eligible.' -f $Location, $storageSku)
}

function Get-SampleRunnerIdentity {
    param([string] $SubscriptionId = '')

    $runnerTokenResponse = $null
    $runnerAccessToken = $null
    $claims = $null
    try {
        $tokenArguments = @('account', 'get-access-token', '--resource', 'https://management.azure.com/')
        if ($SubscriptionId) { $tokenArguments += @('--subscription', (Get-SampleSubscriptionId -SubscriptionId $SubscriptionId)) }
        $runnerTokenResponse = Invoke-SampleAzure -Arguments $tokenArguments -Sensitive
        $runnerAccessToken = [string] $runnerTokenResponse.accessToken
        $payload = $runnerAccessToken.Split('.')[1].Replace('-', '+').Replace('_', '/')
        $payload = $payload.PadRight($payload.Length + ((4 - $payload.Length % 4) % 4), '=')
        $claims = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($payload)) | ConvertFrom-Json -AsHashtable
        $clientId = if ($claims['appid']) { [string] $claims['appid'] } else { [string] $claims['azp'] }
        if ($claims['oid'] -notmatch '^[a-fA-F0-9-]{36}$' -or $claims['tid'] -notmatch '^[a-fA-F0-9-]{36}$' -or
            $clientId -notmatch '^[a-fA-F0-9-]{36}$' -or $claims['idtyp'] -notin @($null, 'app') -or $claims.ContainsKey('scp')) {
            throw 'An Azure service connection application identity is required.'
        }
        # Metadata only: never return or persist the token, authorization headers, or other claims.
        return @{ principalId = [string] $claims.oid; clientId = $clientId; tenantId = [string] $claims.tid }
    } catch {
        throw 'Could not identify the Azure service-connection application; token and raw response were suppressed.'
    } finally {
        $runnerAccessToken = $null
        $runnerTokenResponse = $null
        $claims = $null
    }
}

function Save-SampleInventory {
    param([Parameter(Mandatory)] [hashtable] $State, [Parameter(Mandatory)] [string] $OutputPath)

    $exists = Invoke-SampleAzure -Arguments @('group', 'exists', '--name', $State.plan.resourceGroup, '--subscription', $State.subscriptionId)
    $resources = @()
    if ($exists) {
        $resources = @(Invoke-SampleAzure -Arguments @('resource', 'list', '--resource-group', $State.plan.resourceGroup,
            '--subscription', $State.subscriptionId, '--query', '[].{id:id,name:name,type:type,location:location}'))
    }
    ConvertTo-Json -InputObject $resources -Depth 5 | Set-Content -LiteralPath $OutputPath -Encoding utf8
}

function Get-SampleAzureErrorCodes {
    param([AllowNull()] [object] $ErrorDetails)

    # Traverse only ARM error envelopes, never message, request, parameter or credential fields.
    $codes = @()
    if ($ErrorDetails -is [System.Collections.IDictionary]) {
        $code = $ErrorDetails['code']
        if ($code -is [string] -and $code -cmatch '^[A-Za-z][A-Za-z0-9_.-]{0,127}$' -and
            $code -notmatch '^(github_pat_|ghp_|eyJ)') {
            $codes += $code
        }
        foreach ($key in @('error', 'details')) {
            if ($ErrorDetails.Contains($key)) { $codes += @(Get-SampleAzureErrorCodes -ErrorDetails $ErrorDetails[$key]) }
        }
    } elseif ($ErrorDetails -is [System.Collections.IEnumerable] -and $ErrorDetails -isnot [string]) {
        foreach ($detail in $ErrorDetails) { $codes += @(Get-SampleAzureErrorCodes -ErrorDetails $detail) }
    }
    return @($codes | Sort-Object -Unique)
}

function Get-SampleAzureCliErrorCodes {
    param([AllowEmptyString()] [string] $Text)

    $codes = @()
    foreach ($line in ($Text -split '\r?\n')) {
        $json = $line.Trim() -replace '^ERROR:\s*', ''
        if ($json.StartsWith('{') -and $json.EndsWith('}')) {
            try {
                $details = $json | ConvertFrom-Json -AsHashtable -ErrorAction Stop
                $codes += @(Get-SampleAzureErrorCodes -ErrorDetails $details)
            } catch { }
        } elseif ($line -cmatch '^ERROR:\s*\((?<armCode>[A-Za-z][A-Za-z0-9_.-]{0,127})\)') {
            $codes += @(Get-SampleAzureErrorCodes -ErrorDetails @{ code = $Matches.armCode })
        }
    }
    return @($codes | Sort-Object -Unique)
}
