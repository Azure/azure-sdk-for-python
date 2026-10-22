# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.0

Set-StrictMode -Version Latest

function Invoke-SampleAzure {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string[]] $Arguments, [switch] $Sensitive)

    if ($Sensitive) {
        # Deployment errors can include a submitted body. Never log secret-bearing requests.
        $output = & az @Arguments --only-show-errors --output json 2>$null
    } else {
        $output = & az @Arguments --only-show-errors --output json
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Azure operation '$($Arguments[0]) $($Arguments[1])' failed (exit $LASTEXITCODE)."
    }
    $text = $output -join [Environment]::NewLine
    if (-not [string]::IsNullOrWhiteSpace($text)) {
        return ($text | ConvertFrom-Json -AsHashtable)
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
    $runnerTokenResponse = $null
    $runnerAccessToken = $null
    try {
        $runnerTokenResponse = Invoke-SampleAzure -Arguments @('account', 'get-access-token', '--resource', 'https://management.azure.com/') -Sensitive
        $runnerAccessToken = [string] $runnerTokenResponse.accessToken
        $payload = $runnerAccessToken.Split('.')[1].Replace('-', '+').Replace('_', '/')
        $payload = $payload.PadRight($payload.Length + ((4 - $payload.Length % 4) % 4), '=')
        $claims = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($payload)) | ConvertFrom-Json -AsHashtable
        if ($claims['oid'] -notmatch '^[a-fA-F0-9-]{36}$' -or ($claims['idtyp'] -ne 'app' -and -not $claims.ContainsKey('appid'))) {
            throw 'An Azure service connection application identity is required.'
        }
        return [string] $claims.oid
    } finally {
        $runnerAccessToken = $null
        $runnerTokenResponse = $null
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
