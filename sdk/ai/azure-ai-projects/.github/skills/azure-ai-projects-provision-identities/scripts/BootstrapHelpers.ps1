# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

# Private bootstrap-only helpers. No worker dependency, authentication fallback,
# state discovery, or module-level Azure calls.
function Invoke-BootstrapAzure {
    param([Parameter(Mandatory)] [string[]] $Arguments, [switch] $Sensitive)
    if (-not $Sensitive) { throw 'Bootstrap CLI responses must remain protected.' }
    if ($Arguments[0] -ceq 'rest') {
        $urlIndex = [Array]::IndexOf($Arguments, '--url')
        if (($Arguments[0..2] -join ' ') -cne 'rest --method get' -or $urlIndex -lt 0 -or
            $Arguments[$urlIndex + 1] -notmatch '^https://management\.azure\.com/' -or -not $script:bootstrapArmHeaders) {
            throw 'Bootstrap HTTP metadata requests must be approved current-user ARM GETs.'
        }
        try {
            $response = Invoke-RestMethod -Method Get -Uri $Arguments[$urlIndex + 1] -Headers $script:bootstrapArmHeaders -TimeoutSec 45 -MaximumRedirection 0
            return ,($response | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable -NoEnumerate)
        } catch { throw 'Bootstrap ARM metadata GET failed; raw response suppressed.' }
    }
    $PSNativeCommandUseErrorActionPreference = $false
    try { $captured = @(& az @Arguments --only-show-errors --output json 2>&1); $exitCode = $LASTEXITCODE }
    catch { throw 'Bootstrap CLI execution failed; response content suppressed.' }
    if ($exitCode -ne 0) { throw 'Bootstrap CLI failed; response content suppressed.' }
    try { $parsed = ($captured -join [Environment]::NewLine) | ConvertFrom-Json -AsHashtable -NoEnumerate -ErrorAction Stop }
    catch { throw 'Bootstrap CLI returned invalid protected JSON; response content suppressed.' }
    return ,$parsed
}

function Assert-BootstrapKeys {
    param($Value, [string[]] $Required, [string[]] $Optional = @())
    if ($Value -isnot [System.Collections.IDictionary]) { throw 'Invalid bootstrap object schema.' }
    foreach ($key in $Required) { if (-not $Value.Contains($key)) { throw 'Incomplete bootstrap object schema.' } }
    foreach ($key in $Value.Keys) { if ($key -cnotin ($Required + $Optional)) { throw 'Unexpected bootstrap object property.' } }
}

function Assert-BootstrapGuid {
    param($Value)
    if ($Value -isnot [string] -or $Value -cnotmatch '^[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}$' -or
        [guid] $Value -eq [guid]::Empty) { throw 'Bootstrap metadata requires explicit, nonzero GUIDs.' }
}

function Test-BootstrapText {
    param($Value, [string] $Expected, [switch] $IgnoreCase)
    if ($Value -isnot [string]) { return $false }
    $comparison = if ($IgnoreCase) { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
    return [string]::Equals($Value, $Expected, $comparison)
}

function Get-SampleArmGuid {
    param([Parameter(Mandatory)] [AllowEmptyString()] [string[]] $Values)
    # Original ARM guid() seeds and RFC 4122 UUIDv5 network byte order.
    $namespace = ([guid] '11fb06fb-712d-4ddd-98c7-e71bbd588830').ToByteArray()
    [Array]::Reverse($namespace, 0, 4); [Array]::Reverse($namespace, 4, 2); [Array]::Reverse($namespace, 6, 2)
    $hash = [Security.Cryptography.SHA1]::HashData([byte[]] ($namespace + [Text.Encoding]::UTF8.GetBytes(($Values -join '-'))))
    $bytes = [byte[]]::new(16); [Array]::Copy($hash, $bytes, 16)
    $bytes[6] = ($bytes[6] -band 0x0f) -bor 0x50; $bytes[8] = ($bytes[8] -band 0x3f) -bor 0x80
    [Array]::Reverse($bytes, 0, 4); [Array]::Reverse($bytes, 4, 2); [Array]::Reverse($bytes, 6, 2)
    return ([guid]::new($bytes)).ToString('D')
}

function Assert-BootstrapEqual {
    param($Actual, $Expected)
    if ($null -eq $Expected) { if ($null -ne $Actual) { throw 'Bootstrap contract value differs.' }; return }
    if ($Expected -is [System.Collections.IDictionary]) {
        Assert-BootstrapKeys -Value $Actual -Required @($Expected.Keys)
        foreach ($key in $Expected.Keys) { Assert-BootstrapEqual -Actual $Actual[$key] -Expected $Expected[$key] }
    } elseif ($Expected -is [System.Collections.IList]) {
        if ($Actual -isnot [System.Collections.IList] -or $Actual.Count -ne $Expected.Count) { throw 'Bootstrap contract array differs.' }
        for ($index = 0; $index -lt $Expected.Count; $index++) { Assert-BootstrapEqual -Actual $Actual[$index] -Expected $Expected[$index] }
    } elseif ($Expected -is [string]) {
        if ($Actual -isnot [string] -or $Actual -cne $Expected) { throw 'Bootstrap contract value differs.' }
    } elseif ($null -eq $Actual -or $Actual.GetType() -ne $Expected.GetType() -or $Actual -ne $Expected) { throw 'Bootstrap contract value differs.' }
}

function Assert-BootstrapExpression {
    param($Actual, [string[]] $Expected)
    # Whitespace is normalized ONLY outside quoted ARM literals (never ABAC).
    if ($Actual -isnot [string]) { throw 'Invalid compiled bootstrap expression.' }
    $normalized = foreach ($text in (@($Actual) + @($Expected))) {
        $builder = [Text.StringBuilder]::new(); $quoted = $false
        for ($index = 0; $index -lt $text.Length; $index++) {
            $character = $text[$index]
            if ($character -eq "'") {
                $null = $builder.Append($character)
                if ($quoted -and $index + 1 -lt $text.Length -and $text[$index + 1] -eq "'") { $null = $builder.Append($text[++$index]) }
                else { $quoted = -not $quoted }
            } elseif ($quoted -or -not [char]::IsWhiteSpace($character)) { $null = $builder.Append($character) }
        }
        if ($quoted) { throw 'Invalid compiled bootstrap expression quoting.' }
        $builder.ToString()
    }
    if ($normalized[0] -cnotin $normalized[1..($normalized.Count - 1)]) { throw 'Compiled bootstrap expression differs from the approved contract.' }
}

function ConvertTo-BootstrapCanonicalValue {
    param($Value)
    if ($Value -is [System.Collections.IDictionary]) {
        $result = [ordered]@{}; $keys = [string[]] @($Value.Keys); [Array]::Sort($keys, [StringComparer]::Ordinal)
        foreach ($key in $keys) { $result[$key] = ConvertTo-BootstrapCanonicalValue -Value $Value[$key] }
        return $result
    }
    if ($Value -is [System.Collections.IList]) {
        $result = [object[]]::new($Value.Count)
        for ($index = 0; $index -lt $Value.Count; $index++) { $result[$index] = ConvertTo-BootstrapCanonicalValue -Value $Value[$index] }
        return ,$result
    }
    return ,$Value
}

function Get-BootstrapGrantPlan {
    $roles = @('53ca6127-db72-4b80-b1b0-d745d6d5456d', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe',
        'b7e6dc6d-f1e8-4753-8033-0f276bb0955b', '230815da-be43-4aae-9cb4-875f7bd000aa',
        '7ca78c08-252a-4471-8644-bb5ff32d4ba0', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
    $condition = "((!(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read'})  AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/filter/action'}) AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write'}) ) OR (@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringLikeIgnoreCase '*-azureml-agent'))"
    foreach ($role in $roles) {
        $filter = if ($role -ceq $roles[2]) { $condition } else { '' }
        $roleId = "$scope/providers/Microsoft.Authorization/roleDefinitions/$role"
        $name = Get-SampleArmGuid -Values @($expectedIds.project.ToLowerInvariant(), $scope.ToLowerInvariant(), $roleId.ToLowerInvariant(), $filter)
        @{ kind = 'project'; roleAssignmentId = "$scope/providers/Microsoft.Authorization/roleAssignments/$name";
            roleDefinitionId = $roleId; scope = $scope; condition = $filter; conditionVersion = $(if ($filter) { '2.0' } else { '' }) }
    }
    if ($PipelinePrincipalId) {
        $roleId = "$scope/providers/Microsoft.Authorization/roleDefinitions/$($roles[0])"
        $name = Get-SampleArmGuid -Values @($PipelinePrincipalId.ToLowerInvariant(), $scope.ToLowerInvariant(), $roleId.ToLowerInvariant(), '')
        @{ kind = 'pipeline'; roleAssignmentId = "$scope/providers/Microsoft.Authorization/roleAssignments/$name";
            roleDefinitionId = $roleId; scope = $scope; condition = ''; conditionVersion = '' }
    }
}

function Get-BootstrapParameters {
    param([string] $OwnerToken, [string] $PipelineMode, [string] $AssignmentId)
    $parameters = @{ identityResourceGroup = @{ value = $identityGroup };
        location = @{ value = $Location }; ownerToken = @{ value = $OwnerToken }; pipelinePrincipalId = @{ value = $PipelinePrincipalId };
        pipelineRoleAssignmentId = @{ value = $AssignmentId }; createPipelineGrant = @{ value = ($PipelineMode -ceq 'Create') } }
    if ($schemaVersion -eq 2) { $parameters['namePrefix'] = @{ value = $namePrefix } }
    else { $parameters['identityNamePattern'] = @{ value = $IdentityNamePattern } }
    return $parameters
}

function Assert-BootstrapState {
    param($State)
    $extra = if ($legacy) { @() } else { @('location', 'pipelineMode', 'existingPipelineAssignmentId', 'parameters', 'prediction', 'validation') +
        @($(if ($schemaVersion -eq 2) { 'setName' } else { 'identityNamePattern' })) }
    Assert-BootstrapKeys -Value $State -Required (@('schemaVersion', 'status', 'subscriptionId', 'tenantId', 'identityResourceGroup', 'ownerToken',
        'pipelinePrincipalId', 'pipelineClientId', 'expectedCallerPrincipalId', 'deploymentName', 'identityResourceIds', 'templateHash') + $extra) -Optional @('outputs', 'identities')
    if (($State['schemaVersion'] -isnot [int] -and $State['schemaVersion'] -isnot [long]) -or $State['schemaVersion'] -ne $schemaVersion -or
        $State['status'] -isnot [string] -or $State['status'] -cnotin @('Previewed', 'Applying', 'Failed', 'Created', 'Verified') -or
        $State['ownerToken'] -isnot [string] -or $State['ownerToken'] -cnotmatch '^[a-f0-9]{32}$' -or
        $State['templateHash'] -isnot [string] -or $State['templateHash'] -cnotmatch '^[a-f0-9]{64}$') { throw 'Invalid bootstrap state schema or status.' }
    foreach ($binding in @(@('subscriptionId', $subscription), @('tenantId', $tenant), @('expectedCallerPrincipalId', $ExpectedCallerPrincipalId))) {
        Assert-BootstrapGuid -Value $State[$binding[0]]
        if ($State[$binding[0]] -ine $binding[1]) { throw 'Bootstrap state differs from the explicit approved target.' }
    }
    foreach ($name in @('pipelinePrincipalId', 'pipelineClientId')) {
        $expected = if ($name -ceq 'pipelinePrincipalId') { $PipelinePrincipalId } else { $PipelineClientId }
        if ($legacy -or $expected) { Assert-BootstrapGuid -Value $State[$name] }
        if (-not (Test-BootstrapText -Value $State[$name] -Expected $expected -IgnoreCase)) { throw 'Bootstrap pipeline binding differs.' }
    }
    Assert-BootstrapEqual -Actual $State['identityResourceIds'] -Expected $expectedIds
    $prefix = if ($legacy) { 'sample-ci-shared-identities-' } else { 'azsdk-identities-' }
    if (-not (Test-BootstrapText -Value $State['identityResourceGroup'] -Expected $identityGroup) -or
        -not (Test-BootstrapText -Value $State['deploymentName'] -Expected ($prefix + $State['ownerToken'].Substring(0, 12)))) {
        throw 'Bootstrap state has a foreign resource group or deployment name.'
    }
    if (-not $legacy) {
        Assert-BootstrapEqual -Actual $State['location'] -Expected $Location
        if ($schemaVersion -eq 2) { Assert-BootstrapEqual -Actual $State['setName'] -Expected $SetName }
        else { Assert-BootstrapEqual -Actual $State['identityNamePattern'] -Expected $IdentityNamePattern }
        if ($State['pipelineMode'] -isnot [string] -or $State['pipelineMode'] -cnotin @('None', 'Create', 'Reuse') -or
            $State['existingPipelineAssignmentId'] -isnot [string]) { throw 'Invalid pipeline grant mode.' }
        if (($PipelinePrincipalId -and $State['pipelineMode'] -ceq 'None') -or (-not $PipelinePrincipalId -and $State['pipelineMode'] -cne 'None')) { throw 'Pipeline mode differs from the approved inputs.' }
        $assignmentId = if ($PipelinePrincipalId) { $grants[6].roleAssignmentId } else { '' }
        if ($State['pipelineMode'] -ceq 'Reuse') {
            $id = $State['existingPipelineAssignmentId']
            if ($id -isnot [string] -or -not $id.StartsWith(($scope + '/providers/Microsoft.Authorization/roleAssignments/'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid reused pipeline assignment scope.' }
            Assert-BootstrapGuid -Value $id.Split('/')[-1]
            if ($id.Split('/').Count -ne 7) { throw 'Invalid reused pipeline assignment ID.' }
            $assignmentId = $id
        } elseif ($State['existingPipelineAssignmentId'] -cne '') { throw 'Unexpected existing pipeline assignment ID.' }
        Assert-BootstrapEqual -Actual $State['parameters'] -Expected (Get-BootstrapParameters -OwnerToken $State['ownerToken'] -PipelineMode $State['pipelineMode'] -AssignmentId $assignmentId)
        # The exact validated prediction is part of the approval, not a mutable log.
        $savedGrants = $grants
        try {
            if ($State['pipelineMode'] -ceq 'Reuse') { $grants = @($grants[0..5]) + @(@{} + $grants[6]); $grants[6].roleAssignmentId = $assignmentId }
            Assert-BootstrapValidation -Validation $State['validation']
            Assert-BootstrapPrediction -Prediction $State['prediction'] -Validation $State['validation'] -PipelineGrantExists ($State['pipelineMode'] -ceq 'Reuse')
        } finally { $grants = $savedGrants }
    }
    if (($State['status'] -ceq 'Previewed' -and ($State.Contains('outputs') -or $State.Contains('identities'))) -or
        ($State['status'] -cin @('Created', 'Verified') -and $State['outputs'] -isnot [System.Collections.IDictionary]) -or
        ($State.Contains('identities') -and $State['status'] -cne 'Verified') -or
        ($State['status'] -ceq 'Verified' -and $State['identities'] -isnot [System.Collections.IDictionary])) { throw 'Bootstrap state metadata does not match its status.' }
}

function Save-BootstrapState {
    param([System.Collections.IDictionary] $State)
    if ($readonlyLegacy) { throw 'Legacy bootstrap state is immutable; no save or upgrade is permitted.' }
    Assert-BootstrapState -State $State
    $directory = Split-Path -Parent $StatePath; $null = [IO.Directory]::CreateDirectory($directory)
    $temporary = Join-Path $directory ([guid]::NewGuid().ToString('N') + '.tmp'); $lock = $null
    try {
        try { $lock = [IO.File]::Open($StatePath + '.lock', [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None) }
        catch { throw 'Bootstrap state is in use; no replay is permitted.' }
        if ([IO.File]::Exists($StatePath)) {
            try { $current = [IO.File]::ReadAllText($StatePath) | ConvertFrom-Json -AsHashtable -ErrorAction Stop }
            catch { throw 'Cannot reconcile the current bootstrap state; no overwrite is permitted.' }
            Assert-BootstrapState -State $current
            foreach ($key in @('ownerToken', 'deploymentName', 'templateHash', 'parameters', 'pipelineMode', 'existingPipelineAssignmentId', 'prediction', 'validation')) {
                Assert-BootstrapEqual -Actual $current[$key] -Expected $State[$key]
            }
            foreach ($key in @('outputs', 'identities')) {
                if ($current.Contains($key)) { Assert-BootstrapEqual -Actual $State[$key] -Expected $current[$key] }
            }
            $allowedPrevious = switch ($State['status']) {
                'Previewed' { @('Previewed') }; 'Applying' { @('Previewed') }; 'Created' { @('Applying') }; 'Failed' { @('Applying') }
                'Verified' { @('Applying', 'Failed', 'Created', 'Verified') }
            }
            if ($current['status'] -cnotin $allowedPrevious) { throw 'A bootstrap attempt is already recorded; no replay or state downgrade is permitted.' }
        } elseif ($State['status'] -cne 'Previewed') { throw 'The recorded bootstrap state disappeared; no replay is permitted.' }
        [IO.File]::WriteAllText($temporary, ($State | ConvertTo-Json -Depth 100), [Text.UTF8Encoding]::new($false))
        [IO.File]::Move($temporary, $StatePath, $true)
    } finally { if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }; if ($null -ne $lock) { $lock.Dispose() } }
}

function Get-BootstrapGroupExists {
    $exists = Invoke-BootstrapAzure -Arguments @('group', 'exists', '--name', $identityGroup, '--subscription', $subscription) -Sensitive
    if ($exists -isnot [bool]) { throw 'The group-exists response must be an actual JSON boolean.' }
    return $exists
}

function Assert-BootstrapIdentityNamesAbsent {
    # Subscription-wide exact-name lookup, not just the new hashed RG. Never
    # adopt an old/default set elsewhere, trust a filtered result, or follow a
    # pagination link outside the explicit protected ARM collection.
    $path = "$scope/providers/Microsoft.ManagedIdentity/userAssignedIdentities"
    $uri = 'https://management.azure.com' + $path + '?api-version=2023-01-31'
    $pages = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $ids = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $wanted = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($name in $naming.names.Values) { if (-not $wanted.Add($name)) { throw 'Duplicate expanded MI names.' } }
    do {
        $parsed = $null
        if (-not [uri]::TryCreate($uri, [UriKind]::Absolute, [ref] $parsed) -or $parsed.Scheme -cne 'https' -or
            $parsed.Host -ine 'management.azure.com' -or $parsed.Port -ne 443 -or $parsed.UserInfo -or $parsed.Fragment -or
            $parsed.AbsolutePath -ine $path -or -not $pages.Add($uri) -or $pages.Count -gt 1000) { throw 'Unexpected identity-name pagination target.' }
        $query = @{}
        foreach ($part in $parsed.Query.TrimStart('?').Split('&')) {
            $pair = $part.Split('=', 2); $key = [uri]::UnescapeDataString($pair[0])
            if ($pair.Count -ne 2 -or $key -cnotin @('api-version', '$skiptoken', 'skiptoken') -or $query.ContainsKey($key)) { throw 'Unexpected identity-name pagination query.' }
            $query[$key] = [uri]::UnescapeDataString($pair[1])
        }
        if ($query['api-version'] -cne '2023-01-31') { throw 'Identity-name pagination changed API version.' }
        $page = Invoke-BootstrapAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url', $uri) -Sensitive
        if ($page -isnot [System.Collections.IDictionary] -or $page['value'] -isnot [System.Collections.IList] -or
            ($page.Contains('error') -and $null -ne $page['error']) -or ($null -ne $page['nextLink'] -and $page['nextLink'] -isnot [string])) { throw 'Invalid protected identity-name list response.' }
        foreach ($identity in $page['value']) {
            if ($identity -isnot [System.Collections.IDictionary] -or $identity['id'] -isnot [string] -or
                $identity['id'] -inotmatch ('\A' + [regex]::Escape($scope) + '/resourceGroups/[^/]+/providers/Microsoft\.ManagedIdentity/userAssignedIdentities/[A-Za-z0-9][A-Za-z0-9_-]{2,127}\z') -or
                -not (Test-BootstrapText -Value $identity['type'] -Expected 'Microsoft.ManagedIdentity/userAssignedIdentities' -IgnoreCase) -or
                -not (Test-BootstrapText -Value $identity['name'] -Expected $identity['id'].Split('/')[-1] -IgnoreCase) -or
                -not $ids.Add($identity['id'])) { throw 'Ambiguous, duplicate or invalid identity-name metadata.' }
            if ($wanted.Contains($identity['name'])) { throw 'An expanded MI name already exists in this subscription; refusing adoption or duplicate names across resource groups.' }
        }
        $uri = $page['nextLink']
    } while ($uri)
}

function Get-BootstrapAssignmentSignature {
    param($Assignment)
    if ($Assignment -isnot [System.Collections.IDictionary] -or $Assignment['id'] -isnot [string] -or
        $Assignment['id'] -notmatch '^/(?:.+/)?providers/Microsoft\.Authorization/roleAssignments/[a-fA-F0-9-]{36}$' -or
        $Assignment['properties'] -isnot [System.Collections.IDictionary]) { throw 'Invalid role-assignment response schema.' }
    Assert-BootstrapGuid -Value ($Assignment['id'].Split('/')[-1]); $properties = $Assignment['properties']
    Assert-BootstrapGuid -Value $properties['principalId']
    foreach ($field in @('scope', 'roleDefinitionId')) {
        if ($properties[$field] -isnot [string] -or -not $properties[$field].StartsWith('/')) { throw 'Incomplete role-assignment metadata.' }
    }
    if ($Assignment.Contains('type') -and -not (Test-BootstrapText -Value $Assignment['type'] -Expected 'Microsoft.Authorization/roleAssignments' -IgnoreCase)) { throw 'Unexpected assignment resource type.' }
    $signature = @{}
    foreach ($field in @('principalId', 'scope', 'roleDefinitionId', 'principalType', 'condition', 'conditionVersion', 'delegatedManagedIdentityResourceId')) {
        $value = $properties[$field]
        if ($null -ne $value -and $value -isnot [string]) { throw 'Invalid assignment property type.' }
        $signature[$field] = if ($null -eq $value) { '' } elseif ($field -cin @('condition', 'conditionVersion')) { $value } else { $value.ToLowerInvariant() }
    }
    return $signature
}

function Get-BootstrapAllAssignments {
    param([Parameter(Mandatory)] [string] $SubscriptionId)
    $path = '/subscriptions/' + $SubscriptionId + '/providers/Microsoft.Authorization/roleAssignments'; $all = [Collections.Generic.List[object]]::new()
    foreach ($atScope in @($false, $true)) {
        $uri = 'https://management.azure.com' + $path + '?api-version=2022-04-01'
        if ($atScope) { $uri += '&$filter=atScope()' }
        $seenPages = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        do {
            $parsed = $null
            if (-not [uri]::TryCreate($uri, [UriKind]::Absolute, [ref] $parsed) -or $parsed.Scheme -cne 'https' -or
                $parsed.Host -ine 'management.azure.com' -or $parsed.Port -ne 443 -or $parsed.UserInfo -or $parsed.Fragment -or
                $parsed.AbsolutePath -ine $path -or -not $seenPages.Add($uri) -or $seenPages.Count -gt 1000) { throw 'Unexpected authorization pagination target.' }
            $query = @{}
            foreach ($part in $parsed.Query.TrimStart('?').Split('&')) {
                $pair = $part.Split('=', 2); $key = [uri]::UnescapeDataString($pair[0])
                if ($pair.Count -ne 2 -or $key -notin @('api-version', '$filter', '$skiptoken', 'skiptoken') -or $query.ContainsKey($key)) { throw 'Unexpected authorization pagination query.' }
                $query[$key] = [uri]::UnescapeDataString($pair[1])
            }
            if ($query['api-version'] -cne '2022-04-01' -or $query.ContainsKey('$filter') -ne $atScope -or
                ($atScope -and $query['$filter'] -cne 'atScope()')) { throw 'Authorization pagination changed the requested scope.' }
            $page = Invoke-BootstrapAzure -Arguments @('rest', '--method', 'get', '--subscription', $SubscriptionId, '--url', $uri) -Sensitive
            if ($page -isnot [System.Collections.IDictionary] -or $page['value'] -isnot [System.Collections.IList] -or
                ($page.Contains('error') -and $null -ne $page['error']) -or ($null -ne $page['nextLink'] -and $page['nextLink'] -isnot [string])) { throw 'Invalid authorization list response.' }
            foreach ($assignment in $page['value']) { $all.Add($assignment) }; $uri = $page['nextLink']
        } while ($uri)
    }
    $byId = @{}
    foreach ($assignment in $all) {
        $signature = Get-BootstrapAssignmentSignature -Assignment $assignment; $id = $assignment['id'].ToLowerInvariant()
        if ($byId.ContainsKey($id)) { Assert-BootstrapEqual -Actual (Get-BootstrapAssignmentSignature -Assignment $byId[$id]) -Expected $signature }
        else { $byId[$id] = $assignment }
    }
    return @($byId.Values)
}

function Assert-BootstrapGrant {
    param($Assignment, $Grant, [string] $PrincipalId)
    $null = Get-BootstrapAssignmentSignature -Assignment $Assignment; $properties = $Assignment['properties']
    if ($Assignment['id'] -ine $Grant.roleAssignmentId -or $properties['principalId'] -ine $PrincipalId -or
        $properties['principalType'] -cne 'ServicePrincipal' -or $properties['scope'] -ine $scope -or
        $properties['roleDefinitionId'] -ine $Grant.roleDefinitionId -or [string] $properties['condition'] -cne $Grant.condition -or
        [string] $properties['conditionVersion'] -cne $Grant.conditionVersion -or $properties['delegatedManagedIdentityResourceId']) {
        throw 'An approved permanent grant could not be verified exactly.'
    }
}

function Get-BootstrapExistingPipelineGrant {
    param([object[]] $Assignments)
    foreach ($assignment in $Assignments) {
        if ($assignment['id'] -iin @($grants[0..5].roleAssignmentId)) { throw 'A project assignment already exists; reject stale or replacement identity grants.' }
    }
    if (-not $PipelinePrincipalId) { return '' }
    $grant = $grants[6]
    $matching = @($Assignments | Where-Object { $_['id'] -ieq $grant.roleAssignmentId -or
        ($_.properties.principalId -ieq $PipelinePrincipalId -and $_.properties.scope -ieq $scope -and $_.properties.roleDefinitionId -ieq $grant.roleDefinitionId) })
    if ($matching.Count -gt 1) { throw 'Duplicate pipeline Foundry User grants; no existing assignment will be changed.' }
    if ($matching.Count -eq 1) {
        $candidate = @{} + $grant; $candidate.roleAssignmentId = $matching[0]['id']
        Assert-BootstrapGrant -Assignment $matching[0] -Grant $candidate -PrincipalId $PipelinePrincipalId
        return [string] $matching[0]['id']
    }
    return ''
}

function Assert-BootstrapOutputs {
    param($Outputs)
    Assert-BootstrapKeys -Value $Outputs -Required @('identityResourceGroupId', 'identities', 'roleDefinitionIds', 'blobOwnerCondition', 'roleAssignments')
    foreach ($key in $Outputs.Keys) {
        Assert-BootstrapKeys -Value $Outputs[$key] -Required @('type', 'value')
        $type = if ($key -cin @('identityResourceGroupId', 'blobOwnerCondition')) { 'string' } else { 'object' }
        if (-not (Test-BootstrapText -Value $Outputs[$key]['type'] -Expected $type -IgnoreCase)) { throw 'Invalid saved deployment output type.' }
    }
    if (-not (Test-BootstrapText -Value $Outputs['identityResourceGroupId']['value'] -Expected $identityGroupId -IgnoreCase) -or
        -not (Test-BootstrapText -Value $Outputs['blobOwnerCondition']['value'] -Expected $grants[2].condition)) { throw 'Foreign bootstrap deployment outputs.' }
    $identities = $Outputs['identities']['value']; Assert-BootstrapKeys -Value $identities -Required @('project', 'account', 'search', 'function')
    $principalIds = @($PipelinePrincipalId, $ExpectedCallerPrincipalId); $clientIds = @($PipelineClientId)
    foreach ($purpose in @('project', 'account', 'search', 'function')) {
        $metadata = $identities[$purpose]; Assert-BootstrapKeys -Value $metadata -Required @('resourceId', 'principalId', 'clientId', 'tenantId')
        foreach ($field in @('principalId', 'clientId', 'tenantId')) { Assert-BootstrapGuid -Value $metadata[$field] }
        if (-not (Test-BootstrapText -Value $metadata['resourceId'] -Expected $expectedIds[$purpose] -IgnoreCase) -or $metadata['tenantId'] -ine $tenant -or
            $metadata['principalId'] -iin $principalIds -or $metadata['clientId'] -iin $clientIds) { throw 'Invalid or duplicate immutable identity metadata.' }
        $principalIds += $metadata['principalId']; $clientIds += $metadata['clientId']
    }
    $roleNames = @('foundryUser', 'storageBlobDataContributor', 'storageBlobDataOwner', 'cosmosDbOperator', 'searchServiceContributor', 'searchIndexDataContributor'); $definitions = @{}
    for ($index = 0; $index -lt 6; $index++) { $definitions[$roleNames[$index]] = $grants[$index].roleDefinitionId }
    Assert-BootstrapEqual -Actual $Outputs['roleDefinitionIds']['value'] -Expected $definitions
    $assignments = $Outputs['roleAssignments']['value']; Assert-BootstrapKeys -Value $assignments -Required @('project', 'pipeline')
    if ($assignments['project'] -isnot [System.Collections.IList] -or $assignments['project'].Count -ne 6) { throw 'Deployment outputs must record exactly six project grants.' }
    for ($index = 0; $index -lt $grants.Count; $index++) {
        $expected = @{} + $grants[$index]; $expected.Remove('kind')
        $expected['principalId'] = if ($index -eq 6) { $PipelinePrincipalId } else { $identities.project.principalId }
        $actual = if ($index -eq 6) { $assignments['pipeline'] } else { $assignments['project'][$index] }
        Assert-BootstrapEqual -Actual $actual -Expected $expected
    }
    if (-not $PipelinePrincipalId -and $null -ne $assignments['pipeline']) { throw 'No-pipeline output must be JSON null.' }
    return $identities
}

function Assert-BootstrapValidation {
    param($Validation)
    if ($Validation -isnot [System.Collections.IDictionary] -or ($Validation.Contains('error') -and $null -ne $Validation['error'])) { throw 'ARM validation did not return a successful object.' }
    $properties = $Validation['properties']
    if ($null -ne $properties -and $properties -isnot [System.Collections.IDictionary]) { throw 'Invalid ARM validation properties.' }
    if ($properties -is [System.Collections.IDictionary] -and $properties.Contains('error') -and $null -ne $properties['error']) { throw 'ARM validation returned a deployment error.' }
    foreach ($envelope in @($Validation, $properties)) {
        if ($envelope -isnot [System.Collections.IDictionary]) { continue }
        foreach ($field in @('status', 'provisioningState')) {
            if ($envelope.Contains($field) -and -not (Test-BootstrapText -Value $envelope[$field] -Expected 'Succeeded')) { throw 'ARM validation contains an unsuccessful or malformed status.' }
        }
    }
    if ($properties -is [System.Collections.IDictionary] -and $properties.Contains('provisioningState')) { return }
    if (-not $Validation.Contains('error') -or $null -ne $Validation['error']) { throw 'ARM validation has no explicit success evidence.' }
}

function Assert-BootstrapPrediction {
    param($Prediction, $Validation, [bool] $PipelineGrantExists)
    if ($Prediction -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $Prediction['status'] -Expected 'Succeeded') -or
        $Prediction['changes'] -isnot [System.Collections.IList] -or ($Prediction.Contains('error') -and $null -ne $Prediction['error'])) {
        throw 'What-if must return a successful JSON object with a changes array.'
    }
    $allowed = @{}; $allowed[$identityGroupId.ToLowerInvariant()] = 'Microsoft.Resources/resourceGroups'
    foreach ($id in $expectedIds.Values) { $allowed[$id.ToLowerInvariant()] = 'Microsoft.ManagedIdentity/userAssignedIdentities' }
    $deployGrants = @($grants | Where-Object { $_.kind -ceq 'project' -or -not $PipelineGrantExists })
    foreach ($grant in $deployGrants) { $allowed[$grant.roleAssignmentId.ToLowerInvariant()] = 'Microsoft.Authorization/roleAssignments' }
    # Preserve exact validated module ID, not a wildcard. Saved predictions carry
    # the evaluated validation evidence so approval remains independently checked.
    $moduleId = $null
    if ($Validation['properties'] -is [System.Collections.IDictionary] -and $null -ne $Validation['properties']['validatedResources']) {
        if ($Validation['properties']['validatedResources'] -isnot [System.Collections.IList]) { throw 'Invalid validated-resource schema.' }
        foreach ($resource in $Validation['properties']['validatedResources']) {
            if ($resource -isnot [System.Collections.IDictionary]) { throw 'Invalid validated resource.' }
            if (Test-BootstrapText -Value $resource['type'] -Expected 'Microsoft.Resources/deployments' -IgnoreCase) {
                $prefix = $identityGroupId + '/providers/Microsoft.Resources/deployments/'
                if ($moduleId -or $resource['id'] -isnot [string] -or -not $resource['id'].StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) -or
                    $resource['id'].Substring($prefix.Length) -cnotmatch '^shared-identities-[a-z2-7]{13}$') { throw 'Unexpected validated module deployment.' }
                $moduleId = $resource['id']; $allowed[$moduleId.ToLowerInvariant()] = 'Microsoft.Resources/deployments'
            }
        }
    }
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($change in $Prediction['changes']) {
        if ($change -isnot [System.Collections.IDictionary] -or $change['resourceId'] -isnot [string] -or
            -not $allowed.ContainsKey($change['resourceId'].ToLowerInvariant()) -or -not $seen.Add($change['resourceId']) -or
            $change['after'] -isnot [System.Collections.IDictionary] -or $change['changeType'] -isnot [string]) { throw 'What-if contains an unknown or duplicate resource ID.' }
        $id = $change['resourceId']; $after = $change['after']; $type = $allowed[$id.ToLowerInvariant()]
        if (-not (Test-BootstrapText -Value $after['type'] -Expected $type -IgnoreCase) -or
            ($after.Contains('id') -and -not (Test-BootstrapText -Value $after['id'] -Expected $id -IgnoreCase)) -or
            ($after.Contains('name') -and -not (Test-BootstrapText -Value $after['name'] -Expected $id.Split('/')[-1] -IgnoreCase))) { throw 'What-if resource type or payload ID differs.' }
        $matching = @($deployGrants | Where-Object { $_.roleAssignmentId -ieq $id })
        if ($matching.Count -eq 1) {
            $grant = $matching[0]
            if ($grant.kind -ceq 'pipeline') {
                if ($change['changeType'] -cne 'Create') { throw 'What-if would change an existing or unverified pipeline grant.' }
                $properties = $after['properties']
                if ($properties -isnot [System.Collections.IDictionary]) { throw 'What-if pipeline grant has no exact properties.' }
                $assignment = @{ id = $id; properties = @{} + $properties }
                if (-not $assignment.properties.Contains('scope')) { $assignment.properties['scope'] = $scope }
                if (-not $assignment.properties.Contains('principalType')) { $assignment.properties['principalType'] = 'ServicePrincipal' }
                Assert-BootstrapGrant -Assignment $assignment -Grant $grant -PrincipalId $PipelinePrincipalId
            } elseif ($change['changeType'] -cnotin @('Create', 'Unsupported')) { throw 'What-if would change an existing project grant.' }
            elseif ($after['properties'] -is [System.Collections.IDictionary]) {
                $properties = $after['properties']
                foreach ($field in @('roleDefinitionId', 'condition', 'conditionVersion', 'scope')) {
                    if ($properties.Contains($field) -and -not (Test-BootstrapText -Value $properties[$field] -Expected $grant[$field])) { throw 'What-if project grant properties differ.' }
                }
                if ($properties.Contains('principalType') -and -not (Test-BootstrapText -Value $properties['principalType'] -Expected 'ServicePrincipal')) { throw 'What-if project principal type differs.' }
            }
        } elseif ($change['changeType'] -cne 'Create') { throw 'Only new group, identity, and module resources may be created.' }
    }
    foreach ($id in @($identityGroupId) + @($expectedIds.Values) + @($deployGrants.roleAssignmentId)) {
        if (-not $seen.Contains($id)) { throw 'What-if omitted an approved resource or grant.' }
    }
}