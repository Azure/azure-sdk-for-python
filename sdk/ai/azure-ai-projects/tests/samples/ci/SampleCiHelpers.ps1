# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.0

Set-StrictMode -Version Latest

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

function Assert-SampleRunPlan {
    param([Parameter(Mandatory)] [hashtable] $Plan)

    if ($Plan['schemaVersion'] -ne 1 -or $Plan['definitionId'] -notmatch '^\d+$' -or $Plan['buildId'] -notmatch '^\d+$' -or
        $Plan['jobAttempt'] -notmatch '^\d+$' -or $Plan['ownerToken'] -notmatch '^[a-f0-9]{32}$') {
        throw 'Invalid CI run ownership metadata.'
    }
    $expectedName = 'azsdk-samples-{0}-{1}-{2}-{3}' -f $Plan.definitionId, $Plan.buildId, $Plan.jobAttempt, $Plan.ownerToken.Substring(0, 8)
    if ($Plan['resourceGroup'] -cne $expectedName) {
        throw 'Resource group does not match the run-owned ephemeral naming convention.'
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
        'sample-ci-run' = '{0}-{1}-{2}' -f $Plan.definitionId, $Plan.buildId, $Plan.jobAttempt
        'sample-ci-owner' = $Plan.ownerToken
    }
}

function Assert-SampleResourceGroupOwnership {
    param(
        [Parameter(Mandatory)] [hashtable] $Plan,
        [Parameter(Mandatory)] [hashtable] $ResourceGroup,
        [Parameter(Mandatory)] [string] $SubscriptionId
    )

    $expectedId = '/subscriptions/{0}/resourceGroups/{1}' -f $SubscriptionId, $Plan.resourceGroup
    if ($ResourceGroup['id'] -ine $expectedId -or $ResourceGroup['tags'] -isnot [System.Collections.IDictionary]) {
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

function Assert-SampleAccountQuota {
    param(
        [Parameter(Mandatory)] [AllowEmptyCollection()] [object[]] $Usages,
        [Parameter(Mandatory)] [string] $Location
    )

    # Account creation has a separate quota from the model deployment capacity checked below.
    # https://learn.microsoft.com/rest/api/aiservices/accountmanagement/usages/list
    $quota = @($Usages | Where-Object { $_['name']['value'] -ceq 'AccountCount' })
    if ($quota.Count -ne 1) {
        throw "Cannot verify Cognitive Services AccountCount quota in '$Location'; no resources were created."
    }
    $usage = $quota[0]
    foreach ($key in @('currentValue', 'limit')) {
        $value = $usage[$key]
        if (($value -isnot [int] -and $value -isnot [long] -and $value -isnot [double] -and $value -isnot [decimal]) -or
            -not [double]::IsFinite([double] $value) -or $value -lt 0) {
            throw "Cannot verify Cognitive Services AccountCount quota in '$Location'; no resources were created."
        }
    }
    if ($usage['unit'] -cne 'Count') {
        throw "Cannot verify Cognitive Services AccountCount quota in '$Location'; no resources were created."
    }
    $current = $usage.currentValue
    $limit = $usage.limit
    if (($limit - $current) -lt 1 -or $usage['status'] -in @('Blocked', 'InOverage', 'Unknown')) {
        $message = "Insufficient Cognitive Services account quota in '{0}' (AccountCount: {1}/{2}, status: {3})." -f `
            $Location, $current, $limit, $usage['status']
        throw ($message + ' No resources were created. Choose a region with available account quota or ask an administrator to review quota; ' +
            'existing accounts will not be deleted.')
    }
    Write-Host ('Account preflight: {0}, AccountCount {1}/{2}; at least one new account slot is available.' -f $Location, $current, $limit)
}

function Get-SampleRunnerPrincipalId {
    return (Get-SampleRunnerIdentity).principalId
}

function Get-SampleRunnerIdentity {
    $runnerTokenResponse = $null
    $runnerAccessToken = $null
    $claims = $null
    try {
        $runnerTokenResponse = Invoke-SampleAzure -Arguments @('account', 'get-access-token', '--resource', 'https://management.azure.com/') -Sensitive
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

function Save-SampleDeploymentDiagnostics {
    param([Parameter(Mandatory)] [hashtable] $State, [Parameter(Mandatory)] [string] $OutputPath)

    Assert-SampleRunPlan -Plan $State.plan
    $records = @()
    $deployments = @(Invoke-SampleAzure -Arguments @('deployment', 'group', 'list', '--resource-group', $State.plan.resourceGroup,
        '--subscription', $State.subscriptionId, '--query', '[].{name:name,state:properties.provisioningState}') -Sensitive)
    foreach ($deployment in @($deployments | Where-Object { $_['state'] -in @('Failed', 'Canceled') })) {
        $errorDetails = Invoke-SampleAzure -Arguments @('deployment', 'group', 'show', '--name', $deployment.name,
            '--resource-group', $State.plan.resourceGroup, '--subscription', $State.subscriptionId, '--query', 'properties.error') -Sensitive
        $operations = @(Invoke-SampleAzure -Arguments @('deployment', 'operation', 'group', 'list', '--name', $deployment.name,
            '--resource-group', $State.plan.resourceGroup, '--subscription', $State.subscriptionId, '--query',
            "[?properties.provisioningState=='Failed'].{resourceId:properties.targetResource.id,resourceType:properties.targetResource.resourceType,error:properties.statusMessage}") -Sensitive)
        $safeOperations = @(foreach ($operation in $operations) {
            $details = $operation['error']
            if ($details -is [string]) {
                try { $details = $details | ConvertFrom-Json -AsHashtable -ErrorAction Stop } catch { $details = $null }
            }
            @{
                resourceId = $operation['resourceId']
                resourceType = $operation['resourceType']
                errorCodes = @(Get-SampleAzureErrorCodes -ErrorDetails $details)
            }
        })
        $codes = @(Get-SampleAzureErrorCodes -ErrorDetails $errorDetails)
        $records += @{ deployment = $deployment.name; state = $deployment.state; errorCodes = $codes; operations = $safeOperations }
        Write-Host ('Deployment diagnostic: {0}, ARM error codes: {1}.' -f $deployment.name, ($codes -join ', '))
        foreach ($operation in $safeOperations) {
            Write-Host ('Failed resource type: {0}, ARM error codes: {1}.' -f $operation.resourceType, ($operation.errorCodes -join ', '))
        }
    }
    # Messages and bodies can echo secure parameters. Persist only the explicit code/ID/type projection above.
    ConvertTo-Json -InputObject @{ schemaVersion = 1; deployments = $records } -Depth 10 |
        Set-Content -LiteralPath $OutputPath -Encoding utf8
}

function Save-SampleReadinessDiagnostics {
    param([Parameter(Mandatory)] [hashtable] $State, [Parameter(Mandatory)] [string] $OutputPath)

    Assert-SampleRunPlan -Plan $State.plan
    $group = Invoke-SampleAzure -Arguments @('group', 'show', '--name', $State.plan.resourceGroup,
        '--subscription', $State.subscriptionId) -Sensitive
    Assert-SampleResourceGroupOwnership -Plan $State.plan -ResourceGroup $group -SubscriptionId $State.subscriptionId
    $resources = @(Invoke-SampleAzure -Arguments @('resource', 'list', '--resource-group', $State.plan.resourceGroup,
        '--subscription', $State.subscriptionId, '--query', '[].{id:id,name:name,type:type}') -Sensitive)
    $projects = @($resources | Where-Object { $_['type'] -eq 'Microsoft.CognitiveServices/accounts/projects' })
    $cosmosAccounts = @($resources | Where-Object { $_['type'] -eq 'Microsoft.DocumentDB/databaseAccounts' })
    if ($projects.Count -ne 1 -or $cosmosAccounts.Count -ne 1) { throw 'Cannot identify the run-owned Standard project and Cosmos DB account.' }
    foreach ($resource in @($projects[0], $cosmosAccounts[0])) {
        if (-not $resource.id.StartsWith($group.id + '/providers/', [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Refusing diagnostics for resources outside the run-owned group.'
        }
    }
    $report = @{ schemaVersion = 1; resourceGroup = $State.plan.resourceGroup }
    $projectUrl = 'https://management.azure.com' + $projects[0].id
    try {
        $project = Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--url', ($projectUrl + '?api-version=2025-10-01-preview'),
            '--query', '{state:properties.provisioningState,principalId:identity.principalId}') -Sensitive
        $hosts = @(Invoke-SampleAzure -Arguments @('rest', '--method', 'get', '--url', ($projectUrl + '/capabilityHosts?api-version=2025-04-01-preview'),
            '--query', 'value[].{name:name,state:properties.provisioningState,threadStorageConnections:properties.threadStorageConnections}') -Sensitive)
        $report['project'] = @{ resourceId = $projects[0].id; state = $project['state']; principalId = $project['principalId'] }
        $report['capabilityHosts'] = @($hosts | ForEach-Object {
            @{ name = $_['name']; state = $_['state']; threadStorageConnections = $_['threadStorageConnections'] }
        })
    } catch { $report['projectStatus'] = 'Unavailable' }

    $cosmosArguments = @('--account-name', $cosmosAccounts[0].name, '--resource-group', $State.plan.resourceGroup,
        '--subscription', $State.subscriptionId)
    try {
        $cosmos = Invoke-SampleAzure -Arguments @('cosmosdb', 'show', '--name', $cosmosAccounts[0].name,
            '--resource-group', $State.plan.resourceGroup, '--subscription', $State.subscriptionId, '--query',
            '{state:provisioningState,publicNetworkAccess:publicNetworkAccess,isVirtualNetworkFilterEnabled:isVirtualNetworkFilterEnabled,ipRules:ipRules,virtualNetworkRules:virtualNetworkRules,disableLocalAuth:disableLocalAuth}') -Sensitive
        $report['cosmos'] = @{ resourceId = $cosmosAccounts[0].id }
        foreach ($key in @('state', 'publicNetworkAccess', 'isVirtualNetworkFilterEnabled', 'disableLocalAuth')) {
            $report.cosmos[$key] = $cosmos[$key]
        }
        # Counts suffice to detect unexpected restrictions without recording address lists.
        $report.cosmos['ipRuleCount'] = @($cosmos['ipRules'] | Where-Object { $null -ne $_ }).Count
        $report.cosmos['virtualNetworkRuleCount'] = @($cosmos['virtualNetworkRules'] | Where-Object { $null -ne $_ }).Count
    } catch { $report['cosmosStatus'] = 'Unavailable' }
    try {
        $containers = @(Invoke-SampleAzure -Arguments (@('cosmosdb', 'sql', 'container', 'list', '--database-name', 'enterprise_memory') +
            $cosmosArguments + @('--query', '[].{name:name}')) -Sensitive)
        $report['containers'] = @($containers | ForEach-Object { $_['name'] })
    } catch { $report['containerStatus'] = 'Unavailable' }
    try {
        $roles = @(Invoke-SampleAzure -Arguments (@('cosmosdb', 'sql', 'role', 'assignment', 'list') + $cosmosArguments +
            @('--query', '[].{principalId:principalId,scope:scope,roleDefinitionId:roleDefinitionId}')) -Sensitive)
        $report['cosmosDataRoles'] = @($roles | ForEach-Object {
            @{ principalId = $_['principalId']; scope = $_['scope']; roleDefinitionId = $_['roleDefinitionId'] }
        })
    } catch { $report['cosmosDataRoleStatus'] = 'Unavailable' }
    # No connection credentials, keys, document contents, request bodies or error messages are queried or saved.
    $report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding utf8
    Write-Host 'Saved run-owned readiness diagnostics (Cosmos networking, container names, role scopes and capability-host state only).'
}
