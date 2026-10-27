# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

# Migrated Pester-4 entry-point fixtures. Independent UUIDv5 and compiled-schema
# oracles; all CLI and HTTP calls terminate in child-scope functions, never Azure.
function Get-BootstrapFixtureGuid {
    param([string[]] $Parts)
    $namespace = [Convert]::FromHexString('11fb06fb712d4ddd98c7e71bbd588830')
    $hash = [Security.Cryptography.SHA1]::HashData([byte[]] ($namespace + [Text.Encoding]::UTF8.GetBytes(($Parts -join '-'))))
    $hash[6] = ($hash[6] -band 15) -bor 80; $hash[8] = ($hash[8] -band 63) -bor 128
    $hex = [Convert]::ToHexString([byte[]] $hash[0..15]).ToLowerInvariant()
    return '{0}-{1}-{2}-{3}-{4}' -f $hex.Substring(0, 8), $hex.Substring(8, 4), $hex.Substring(12, 4), $hex.Substring(16, 4), $hex.Substring(20, 12)
}

function ConvertTo-BootstrapFixtureCanonicalValue {
    param($Value)
    if ($Value -is [System.Collections.IDictionary]) {
        $ordered = [ordered]@{}; $keys = [string[]] @($Value.Keys); [Array]::Sort($keys, [StringComparer]::Ordinal)
        foreach ($key in $keys) { $ordered[$key] = ConvertTo-BootstrapFixtureCanonicalValue -Value $Value[$key] }; return $ordered
    }
    if ($Value -is [System.Collections.IList]) {
        $items = [object[]]::new($Value.Count)
        for ($index = 0; $index -lt $items.Count; $index++) { $items[$index] = ConvertTo-BootstrapFixtureCanonicalValue -Value $Value[$index] }; return ,$items
    }
    return ,$Value
}

function New-BootstrapCompiledFixture {
    param($Fixture)
    $roleNames = @('foundryUser', 'storageBlobDataContributor', 'storageBlobDataOwner', 'cosmosDbOperator', 'searchServiceContributor', 'searchIndexDataContributor')
    $definitions = @{}; $serviceGrants = @()
    for ($index = 0; $index -lt 6; $index++) {
        $role = $Fixture.grants[$index].roleDefinitionId.Split('/')[-1]
        $definitions[$roleNames[$index]] = "[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '$role')]"
        $serviceGrants += @{ roleDefinitionId = "[variables('approvedRoleDefinitionIds').$($roleNames[$index])]";
            condition = $(if ($index -eq 2) { "[variables('storageBlobOwnerCondition')]" } else { '' }) }
    }
    $nestedParameters = @{}
    foreach ($entry in @{ identityNamePattern = 130; location = 30 }.GetEnumerator()) { $nestedParameters[$entry.Key] = @{ type = 'string'; minLength = 1; maxLength = $entry.Value } }
    $nestedParameters['ownerToken'] = @{ type = 'string'; minLength = 32; maxLength = 32 }
    $moduleParameters = @{}
    foreach ($name in @('identityNamePattern', 'location', 'ownerToken')) { $moduleParameters[$name] = @{ value = "[parameters('$name')]" } }
    $identityOutput = @{}; $purposes = @('project', 'account', 'search', 'function')
    for ($index = 0; $index -lt 4; $index++) {
        $identityOutput[$purposes[$index]] = @{
            resourceId = "[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', replace(parameters('identityNamePattern'), '{resource}', variables('identityPurposes')[$index]))]"
            principalId = "[reference('managedIdentities[$index]').principalId]"; clientId = "[reference('managedIdentities[$index]').clientId]"; tenantId = "[reference('managedIdentities[$index]').tenantId]"
        }
    }
    $nested = @{
        languageVersion = '2.0'; parameters = $nestedParameters; variables = @{ identityPurposes = $purposes }
        resources = @{ managedIdentities = @{
            type = 'Microsoft.ManagedIdentity/userAssignedIdentities'; apiVersion = '2023-01-31'
            name = "[replace(parameters('identityNamePattern'), '{resource}', variables('identityPurposes')[copyIndex()])]"
            location = "[parameters('location')]"; copy = @{ name = 'managedIdentities'; count = "[length(variables('identityPurposes'))]" }
            tags = @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = "[parameters('ownerToken')]";
                'sample-ci-retention' = 'permanent'; 'sample-ci-identity' = "[variables('identityPurposes')[copyIndex()]]" }
        } }; outputs = @{ identities = @{ type = 'object'; value = $identityOutput } }
    }
    return @{
        languageVersion = '2.0'; parameters = @{
            identityResourceGroup = @{ type = 'string'; minLength = 1; maxLength = 90 }; identityNamePattern = @{ type = 'string'; minLength = 1; maxLength = 130 }
            location = @{ type = 'string'; minLength = 1; maxLength = 30 }; ownerToken = @{ type = 'string'; minLength = 32; maxLength = 32 }
            pipelinePrincipalId = @{ type = 'string' }; pipelineRoleAssignmentId = @{ type = 'string' }; createPipelineGrant = @{ type = 'bool' }
        }; variables = @{
            approvedRoleDefinitionIds = $definitions; storageBlobOwnerCondition = $Fixture.condition; projectServiceGrants = $serviceGrants
            projectIdentityResourceId = "[resourceId(subscription().subscriptionId, parameters('identityResourceGroup'), 'Microsoft.ManagedIdentity/userAssignedIdentities', replace(parameters('identityNamePattern'), '{resource}', 'project'))]"
        }; resources = @{
            identityResources = @{
                type = 'Microsoft.Resources/resourceGroups'; apiVersion = '2024-03-01'; name = "[parameters('identityResourceGroup')]"; location = "[parameters('location')]"
                tags = @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = "[parameters('ownerToken')]"; 'sample-ci-retention' = 'permanent' }
            }; sharedIdentities = @{
                type = 'Microsoft.Resources/deployments'; apiVersion = '2025-04-01'
                name = "[format('shared-identities-{0}', uniqueString(subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('identityResourceGroup')), parameters('identityNamePattern'), parameters('location')))]"
                resourceGroup = "[parameters('identityResourceGroup')]"
                properties = @{ expressionEvaluationOptions = @{ scope = 'inner' }; mode = 'Incremental'; parameters = $moduleParameters; template = $nested }
            }; projectRoleAssignments = @{
                type = 'Microsoft.Authorization/roleAssignments'; apiVersion = '2022-04-01'; copy = @{ name = 'projectRoleAssignments'; count = "[length(variables('projectServiceGrants'))]" }
                name = "[guid(toLower(variables('projectIdentityResourceId')), toLower(subscription().id), toLower(variables('projectServiceGrants')[copyIndex()].roleDefinitionId), variables('projectServiceGrants')[copyIndex()].condition)]"
                properties = @{
                    principalId = "[reference('sharedIdentities').outputs.identities.value.project.principalId]"; principalType = 'ServicePrincipal'
                    roleDefinitionId = "[variables('projectServiceGrants')[copyIndex()].roleDefinitionId]"
                    condition = "[if(empty(variables('projectServiceGrants')[copyIndex()].condition), null(), variables('projectServiceGrants')[copyIndex()].condition)]"
                    conditionVersion = "[if(empty(variables('projectServiceGrants')[copyIndex()].condition), null(), '2.0')]"
                }
            }; pipelineFoundryUser = @{
                type = 'Microsoft.Authorization/roleAssignments'; apiVersion = '2022-04-01'; condition = "[parameters('createPipelineGrant')]"
                name = "[guid(toLower(parameters('pipelinePrincipalId')), toLower(subscription().id), toLower(variables('approvedRoleDefinitionIds').foundryUser), '')]"
                properties = @{ principalId = "[parameters('pipelinePrincipalId')]"; principalType = 'ServicePrincipal'; roleDefinitionId = "[variables('approvedRoleDefinitionIds').foundryUser]" }
            }
        }; outputs = @{
            identityResourceGroupId = @{ type = 'string'; value = "[subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('identityResourceGroup'))]" }
            identities = @{ type = 'object'; value = "[reference('sharedIdentities').outputs.identities.value]" }
            roleDefinitionIds = @{ type = 'object'; value = "[variables('approvedRoleDefinitionIds')]" }; blobOwnerCondition = @{ type = 'string'; value = "[variables('storageBlobOwnerCondition')]" }
            roleAssignments = @{ type = 'object'; value = @{
                project = "[map(variables('projectServiceGrants'), lambda('grant', createObject('roleAssignmentId', subscriptionResourceId('Microsoft.Authorization/roleAssignments', guid(toLower(variables('projectIdentityResourceId')), toLower(subscription().id), toLower(lambdaVariables('grant').roleDefinitionId), lambdaVariables('grant').condition)), 'principalId', reference('sharedIdentities').outputs.identities.value.project.principalId, 'roleDefinitionId', lambdaVariables('grant').roleDefinitionId, 'scope', subscription().id, 'condition', lambdaVariables('grant').condition, 'conditionVersion', if(empty(lambdaVariables('grant').condition), '', '2.0'))))]"
                pipeline = "[if(empty(parameters('pipelinePrincipalId')), null(), createObject('roleAssignmentId', parameters('pipelineRoleAssignmentId'), 'principalId', parameters('pipelinePrincipalId'), 'roleDefinitionId', variables('approvedRoleDefinitionIds').foundryUser, 'scope', subscription().id, 'condition', '', 'conditionVersion', ''))]"
            } }
        }
    }
}

function New-BootstrapFixtureAssignment {
    param($Grant, [string] $PrincipalId)
    return @{ id = $Grant.roleAssignmentId; type = 'Microsoft.Authorization/roleAssignments'; properties = @{
        principalId = $PrincipalId; principalType = 'ServicePrincipal'; roleDefinitionId = $Grant.roleDefinitionId
        scope = $Grant.scope; condition = $Grant.condition; conditionVersion = $Grant.conditionVersion
    } }
}

function New-BootstrapCliFixture {
    param([switch] $Legacy, [switch] $LegacySchema2, [switch] $NoPipeline, [string] $Region = 'uksouth', [string] $Set = 'unit-test', [string] $Pattern = '')
    $fixture = @{
        subscriptionId = '11111111-1111-1111-1111-111111111111'; tenantId = '22222222-2222-2222-2222-222222222222'
        pipelinePrincipalId = '88888888-8888-8888-8888-888888888888'; pipelineClientId = '99999999-9999-9999-9999-999999999999'
        callerId = '33333333-3333-3333-3333-333333333333'; ownerToken = '0123456789abcdef0123456789abcdef'
        groupExists = $false; state = $null; descendants = @(); parents = @(); calls = [Collections.Generic.List[string]]::new()
        validation = @{ properties = @{ provisioningState = 'Succeeded' }; error = $null }; prediction = @{ status = 'Succeeded'; changes = @(); error = $null }
        stateDuringWhatIf = $null; ids = @{}; identities = @{}; live = @{}; grants = @(); recorded = $null; legacy = [bool] $Legacy
        location = $Region; setName = $Set; sourceDirectory = $PSScriptRoot; createResponse = $null; createFailure = $false; createObservedStatus = $null
        cliOverride = $null; inputOverride = @{}; omitTargetInputs = $false; noTemplates = $false; useDefaultPattern = $false
        schemaVersion = $(if ($Legacy) { 1 } elseif ($LegacySchema2) { 2 } else { 3 })
        identityList = @{ value = @(); nextLink = $null }; identityResponses = $null; identityListCalls = 0
        condition = "((!(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read'})  AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/filter/action'}) AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write'}) ) OR (@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringLikeIgnoreCase '*-azureml-agent'))"
    }
    if ($NoPipeline) { $fixture.pipelinePrincipalId = ''; $fixture.pipelineClientId = '' }
    if ($Legacy) { $fixture.location = 'westus3'; $fixture.setName = '' }
    $fixture.scope = '/subscriptions/' + $fixture.subscriptionId
    $fixture.namePrefix = if ($Legacy) { 'mi-azsdk-sample' } else { "mi-azsdk-$Set" }; $suffix = if ($Legacy) { 'wus3' } else { $Region }
    $fixture.pattern = if ($Pattern) { $Pattern } else { $fixture.namePrefix + '-{resource}-' + $suffix }
    $patternHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($fixture.pattern))).ToLowerInvariant().Substring(0, 12)
    $fixture.groupName = if ($Legacy) { 'rg-azsdk-sample-identities-wus3' } elseif ($LegacySchema2) { "rg-azsdk-identities-$Set-$Region" } else { "rg-azsdk-identities-$patternHash-$Region" }
    $fixture.groupId = $fixture.scope + '/resourceGroups/' + $fixture.groupName
    $fixture.locations = @(@{ name = $fixture.location; displayName = 'Not the canonical name' })
    $principals = @('44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555555', '66666666-6666-6666-6666-666666666666', '77777777-7777-7777-7777-777777777777')
    $clients = @('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb', 'cccccccc-cccc-4ccc-8ccc-cccccccccccc', 'dddddddd-dddd-4ddd-8ddd-dddddddddddd')
    $fixture.prediction.changes += @{ resourceId = $fixture.groupId; changeType = 'Create'; after = @{ type = 'Microsoft.Resources/resourceGroups' } }
    $purposes = @('project', 'account', 'search', 'function')
    for ($index = 0; $index -lt 4; $index++) {
        $purpose = $purposes[$index]; $id = $fixture.groupId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/' + $fixture.pattern.Replace('{resource}', $purpose)
        $fixture.ids[$purpose] = $id; $fixture.identities[$purpose] = @{ resourceId = $id; principalId = $principals[$index]; clientId = $clients[$index]; tenantId = $fixture.tenantId }
        $fixture.live[$purpose] = @{ id = $id; type = 'Microsoft.ManagedIdentity/userAssignedIdentities'; location = $fixture.location
            properties = @{ principalId = $principals[$index]; clientId = $clients[$index]; tenantId = $fixture.tenantId }
            tags = @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = $fixture.ownerToken; 'sample-ci-retention' = 'permanent'; 'sample-ci-identity' = $purpose } }
        $fixture.prediction.changes += @{ resourceId = $id; changeType = 'Create'; after = @{ type = 'Microsoft.ManagedIdentity/userAssignedIdentities' } }
    }
    $roles = @('53ca6127-db72-4b80-b1b0-d745d6d5456d', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe', 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b',
        '230815da-be43-4aae-9cb4-875f7bd000aa', '7ca78c08-252a-4471-8644-bb5ff32d4ba0', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
    $count = if ($NoPipeline) { 6 } else { 7 }
    for ($index = 0; $index -lt $count; $index++) {
        $role = if ($index -eq 6) { $roles[0] } else { $roles[$index] }; $condition = if ($index -eq 2) { $fixture.condition } else { '' }
        $definition = $fixture.scope + '/providers/Microsoft.Authorization/roleDefinitions/' + $role
        $seed = if ($index -eq 6) { $fixture.pipelinePrincipalId } else { $fixture.ids.project }
        $name = Get-BootstrapFixtureGuid -Parts @($seed.ToLowerInvariant(), $fixture.scope.ToLowerInvariant(), $definition.ToLowerInvariant(), $condition)
        $grant = @{ kind = $(if ($index -eq 6) { 'pipeline' } else { 'project' }); roleAssignmentId = ($fixture.scope + '/providers/Microsoft.Authorization/roleAssignments/' + $name)
            roleDefinitionId = $definition; scope = $fixture.scope; condition = $condition; conditionVersion = $(if ($condition) { '2.0' } else { '' }) }
        $fixture.grants += $grant; $properties = @{ roleDefinitionId = $definition; scope = $fixture.scope; condition = $condition; conditionVersion = $grant.conditionVersion; principalType = 'ServicePrincipal' }
        if ($index -eq 6) { $properties['principalId'] = $fixture.pipelinePrincipalId }
        $fixture.prediction.changes += @{ resourceId = $grant.roleAssignmentId; changeType = $(if ($index -eq 6) { 'Create' } else { 'Unsupported' }); after = @{ type = 'Microsoft.Authorization/roleAssignments'; properties = $properties } }
    }
    $fixture.compiled = New-BootstrapCompiledFixture -Fixture $fixture
    return $fixture
}

function Set-BootstrapRecordedFixture {
    param($Fixture, [string] $Status = 'Created', [string] $PipelineMode = '')
    if (-not $PipelineMode) { $PipelineMode = if ($Fixture.pipelinePrincipalId) { 'Create' } else { 'None' } }
    $Fixture.state = @{ schemaVersion = $Fixture.schemaVersion; status = $Status; subscriptionId = $Fixture.subscriptionId; tenantId = $Fixture.tenantId
        pipelinePrincipalId = $Fixture.pipelinePrincipalId; pipelineClientId = $Fixture.pipelineClientId; expectedCallerPrincipalId = $Fixture.callerId
        identityResourceGroup = $Fixture.groupName; ownerToken = $Fixture.ownerToken
        deploymentName = ($(if ($Fixture.legacy) { 'sample-ci-shared-identities-' } else { 'azsdk-identities-' }) + $Fixture.ownerToken.Substring(0, 12)); identityResourceIds = $Fixture.ids
        templateHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes((ConvertTo-BootstrapFixtureCanonicalValue -Value $Fixture.compiled | ConvertTo-Json -Depth 100 -Compress)))).ToLowerInvariant() }
    $parameters = @{ identityResourceGroup = @{ value = $Fixture.groupName }; location = @{ value = $Fixture.location };
        ownerToken = @{ value = $Fixture.ownerToken }; pipelinePrincipalId = @{ value = $Fixture.pipelinePrincipalId } }
    if ($Fixture.schemaVersion -in @(1, 2)) { $parameters.namePrefix = @{ value = $Fixture.namePrefix } }
    else { $parameters.identityNamePattern = @{ value = $Fixture.pattern } }
    if (-not $Fixture.legacy) {
        $parameters.pipelineRoleAssignmentId = @{ value = $(if ($Fixture.pipelinePrincipalId) { $Fixture.grants[6].roleAssignmentId } else { '' }) }; $parameters.createPipelineGrant = @{ value = ($PipelineMode -ceq 'Create') }
        $Fixture.state.location = $Fixture.location; $Fixture.state.pipelineMode = $PipelineMode
        if ($Fixture.schemaVersion -eq 2) { $Fixture.state.setName = $Fixture.setName }
        else { $Fixture.state.identityNamePattern = $Fixture.pattern }
        $Fixture.state.existingPipelineAssignmentId = if ($PipelineMode -ceq 'Reuse') { $Fixture.grants[6].roleAssignmentId } else { '' }
        $Fixture.state.parameters = $parameters
        $Fixture.state.prediction = $Fixture.prediction | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable
        $Fixture.state.validation = $Fixture.validation | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable
    }
    $definitions = @{}; $roleNames = @('foundryUser', 'storageBlobDataContributor', 'storageBlobDataOwner', 'cosmosDbOperator', 'searchServiceContributor', 'searchIndexDataContributor'); $metadata = @()
    for ($index = 0; $index -lt $Fixture.grants.Count; $index++) {
        $grant = $Fixture.grants[$index]; $entry = @{} + $grant; $entry.Remove('kind')
        $entry['principalId'] = if ($index -eq 6) { $Fixture.pipelinePrincipalId } else { $Fixture.identities.project.principalId }; $metadata += $entry
        if ($index -lt 6) { $definitions[$roleNames[$index]] = $grant.roleDefinitionId }
    }
    $outputs = @{ identityResourceGroupId = @{ type = 'String'; value = $Fixture.groupId }; identities = @{ type = 'Object'; value = $Fixture.identities }
        blobOwnerCondition = @{ type = 'String'; value = $Fixture.condition }; roleDefinitionIds = @{ type = 'Object'; value = $definitions }
        roleAssignments = @{ type = 'Object'; value = @{ project = @($metadata[0..5]); pipeline = $(if ($metadata.Count -eq 7) { $metadata[6] } else { $null }) } } }
    if ($Status -cin @('Created', 'Verified')) { $Fixture.state['outputs'] = $outputs }
    if ($Status -ceq 'Verified') { $Fixture.state['identities'] = $Fixture.identities | ConvertTo-Json -Depth 10 | ConvertFrom-Json -AsHashtable }
    $Fixture.recorded = @{ id = ($Fixture.scope + '/providers/Microsoft.Resources/deployments/' + $Fixture.state.deploymentName); name = $Fixture.state.deploymentName; type = 'Microsoft.Resources/deployments'
        properties = @{ provisioningState = 'Succeeded'; outputs = $outputs; parameters = $parameters } }
    $Fixture.createResponse = $Fixture.recorded; $Fixture.groupExists = $true; $Fixture.descendants = @()
    for ($index = 0; $index -lt $Fixture.grants.Count; $index++) {
        $principal = if ($index -eq 6) { $Fixture.pipelinePrincipalId } else { $Fixture.identities.project.principalId }
        $Fixture.descendants += New-BootstrapFixtureAssignment -Grant $Fixture.grants[$index] -PrincipalId $principal
    }
    $Fixture.parents = @($Fixture.descendants)
}

function Set-BootstrapPreviewFixture {
    param($Fixture, [string] $PipelineMode = '')
    Set-BootstrapRecordedFixture -Fixture $Fixture -Status Previewed -PipelineMode $PipelineMode
    $Fixture.groupExists = $false; $Fixture.descendants = @(); $Fixture.parents = @()
    if ($PipelineMode -ceq 'Reuse') {
        $Fixture.descendants = @(New-BootstrapFixtureAssignment -Grant $Fixture.grants[6] -PrincipalId $Fixture.pipelinePrincipalId)
        $Fixture.parents = @($Fixture.descendants)
    }
}

function Invoke-IsolatedBootstrap {
    param([switch] $Apply, [switch] $VerifyOnly, [switch] $Preview)
    $fixture = $script:bootstrapFixture; $sandbox = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
    $scriptsDirectory = Join-Path $sandbox 'scripts'; $infraDirectory = Join-Path $sandbox 'infra'
    $null = New-Item -ItemType Directory -Path $scriptsDirectory, $infraDirectory -Force
    foreach ($name in @('Initialize-SharedSampleIdentities.ps1', 'BootstrapHelpers.ps1', 'BootstrapTemplateContract.ps1', 'IdentityNaming.ps1')) {
        Copy-Item -LiteralPath (Join-Path $fixture.sourceDirectory ('../scripts/' + $name)) -Destination $scriptsDirectory
    }
    if (-not $fixture.noTemplates) {
        foreach ($name in @('bootstrap.bicep', 'identities.bicep')) { Copy-Item -LiteralPath (Join-Path $fixture.sourceDirectory ('../infra/' + $name)) -Destination $infraDirectory }
    } else { Remove-Item -LiteralPath (Join-Path $scriptsDirectory 'BootstrapTemplateContract.ps1') }
    $fixture.statePath = Join-Path $sandbox 'bootstrap-state.json'
    if ($null -ne $fixture.state) {
        # Deliberately noncanonical CRLF, BOM and trailing whitespace for byte-preservation assertions.
        $json = ($fixture.state | ConvertTo-Json -Depth 100).Replace("`r`n", "`n").Replace("`n", "`r`n") + "`r`n  "
        [IO.File]::WriteAllText($fixture.statePath, $json, [Text.UTF8Encoding]::new($true))
    }
    $original = if (Test-Path -LiteralPath $fixture.statePath) { Get-Content -LiteralPath $fixture.statePath -Raw } else { $null }
    $originalBytes = if ($null -ne $original) { [Convert]::ToBase64String([IO.File]::ReadAllBytes($fixture.statePath)) } else { $null }
    & {
        function Invoke-RestMethod {
            param($Method, $Uri, $Headers, $TimeoutSec, $MaximumRedirection)
            if ($Method -cne 'Get' -or $Uri -notmatch '^https://management\.azure\.com/' -or $Headers.Count -ne 1 -or $TimeoutSec -ne 45 -or $MaximumRedirection -ne 0) { throw 'Unexpected HTTP metadata request in isolated bootstrap fixture.' }
            $json = az rest --method get --url $Uri; return ($json | ConvertFrom-Json -AsHashtable -NoEnumerate)
        }
        function az {
            $global:LASTEXITCODE = 0; $fixture.calls.Add(($args -join ' '))
            if ($fixture.cliOverride) {
                $override = & $fixture.cliOverride -Arguments $args -Fixture $fixture
                if ($null -ne $override) { return ,$override }
            }
            if ($args[0] -ceq 'account' -and $args[1] -ceq 'show') { return (@{ id = $fixture.subscriptionId; tenantId = $fixture.tenantId; state = 'Enabled'; user = @{ type = 'user' } } | ConvertTo-Json -Depth 5) }
            if ($args[0] -ceq 'account' -and $args[1] -ceq 'list-locations') { return (ConvertTo-Json -InputObject $fixture.locations -Depth 10) }
            if ($args[0] -ceq 'account' -and $args[1] -ceq 'get-access-token') {
                $claims = @{ tid = $fixture.tenantId; oid = $fixture.callerId; scp = 'user_impersonation' }
                $payload = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($claims | ConvertTo-Json -Compress))).TrimEnd('=').Replace('+', '-').Replace('/', '_')
                return (@{ accessToken = ('fixture.' + $payload + '.not-a-real-token') } | ConvertTo-Json -Compress)
            }
            if (($args[0..2] -join ' ') -ceq 'ad sp show') { return (@{ id = $fixture.pipelinePrincipalId; appId = $fixture.pipelineClientId; accountEnabled = $true } | ConvertTo-Json) }
            if (($args[0..1] -join ' ') -ceq 'group exists') { return (ConvertTo-Json -InputObject $fixture.groupExists -Depth 10) }
            if (($args[0..1] -join ' ') -ceq 'group show') { return (@{ id = $fixture.groupId; location = $fixture.location; tags = @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = $fixture.ownerToken; 'sample-ci-retention' = 'permanent' } } | ConvertTo-Json -Depth 5) }
            if (($args[0..1] -join ' ') -ceq 'provider show') { return '{"registrationState":"Registered"}' }
            if (($args[0..1] -join ' ') -ceq 'bicep build') { return ($fixture.compiled | ConvertTo-Json -Depth 100) }
            if (($args[0..2] -join ' ') -ceq 'deployment sub validate') { return (ConvertTo-Json -InputObject $fixture.validation -Depth 100) }
            if (($args[0..2] -join ' ') -ceq 'deployment sub what-if') {
                if ($fixture.stateDuringWhatIf) {
                    $changed = Get-Content -LiteralPath $fixture.statePath -Raw | ConvertFrom-Json -AsHashtable; $changed['status'] = $fixture.stateDuringWhatIf
                    $changed | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $fixture.statePath -Encoding utf8
                }
                return (ConvertTo-Json -InputObject $fixture.prediction -Depth 100)
            }
            if (($args[0..2] -join ' ') -ceq 'deployment sub create') {
                $atCreate = Get-Content -LiteralPath $fixture.statePath -Raw | ConvertFrom-Json -AsHashtable
                $fixture.createObservedStatus = $atCreate.status
                if ($fixture.createFailure) { throw 'Synthetic ambiguous transport failure, NOT a live deployment.' }
                if ($null -eq $fixture.createResponse) { throw 'No synthetic create response configured.' }
                return (ConvertTo-Json -InputObject $fixture.createResponse -Depth 100)
            }
            if (($args[0..2] -join ' ') -ceq 'rest --method get') {
                $url = $args[[Array]::IndexOf($args, '--url') + 1]
                $identityBase = 'https://management.azure.com' + $fixture.scope + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities?api-version=2023-01-31'
                if ($url.StartsWith($identityBase, [StringComparison]::Ordinal)) {
                    $response = $fixture.identityList
                    if ($null -ne $fixture.identityResponses) { $response = $fixture.identityResponses[$fixture.identityListCalls] }
                    $fixture.identityListCalls++
                    return (ConvertTo-Json -InputObject $response -Depth 20)
                }
                $base = 'https://management.azure.com' + $fixture.scope + '/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01'
                if ($url -ceq $base) { return (@{ value = @($fixture.descendants); nextLink = $null } | ConvertTo-Json -Depth 20) }
                if ($url -ceq ($base + '&$filter=atScope()')) { return (@{ value = @($fixture.parents); nextLink = $null } | ConvertTo-Json -Depth 20) }
                if ($fixture.recorded -and $url -ceq ('https://management.azure.com' + $fixture.recorded.id + '?api-version=2022-09-01')) { return ($fixture.recorded | ConvertTo-Json -Depth 100) }
                foreach ($purpose in @('project', 'account', 'search', 'function')) {
                    if ($url -ceq ('https://management.azure.com' + $fixture.ids[$purpose] + '?api-version=2023-01-31')) { return ($fixture.live[$purpose] | ConvertTo-Json -Depth 10) }
                }
            }
            throw 'Unexpected or mutating CLI command in the isolated bootstrap fixture.'
        }
        if ((Get-Command az).CommandType -cne 'Function' -or (Get-Command Invoke-RestMethod).CommandType -cne 'Function') { throw 'Azure CLI / HTTP isolation failed.' }
        $failure = $null
        $inputs = @{ StatePath = $fixture.statePath; PipelinePrincipalId = $fixture.pipelinePrincipalId; PipelineClientId = $fixture.pipelineClientId;
            ExpectedCallerPrincipalId = $fixture.callerId; Apply = $Apply; VerifyOnly = $VerifyOnly; WhatIf = $Preview; Confirm = $false }
        if (-not $fixture.omitTargetInputs) { $inputs.SubscriptionId = $fixture.subscriptionId; $inputs.TenantId = $fixture.tenantId }
        if (-not $fixture.legacy) {
            $inputs.Location = $fixture.location
            if ($fixture.schemaVersion -eq 2) { $inputs.SetName = $fixture.setName }
            elseif (-not $fixture.useDefaultPattern) { $inputs.IdentityNamePattern = $fixture.pattern }
        }
        foreach ($key in $fixture.inputOverride.Keys) { $inputs[$key] = $fixture.inputOverride[$key] }
        try { $null = & (Join-Path $scriptsDirectory 'Initialize-SharedSampleIdentities.ps1') @inputs }
        catch { $failure = $_.Exception.Message }
        $text = if (Test-Path -LiteralPath $fixture.statePath) { Get-Content -LiteralPath $fixture.statePath -Raw } else { $null }
        [pscustomobject]@{ failure = $failure; state = $(if ($text) { $text | ConvertFrom-Json -AsHashtable } else { $null }); original = $original; text = $text; originalBytes = $originalBytes
            bytes = $(if ($text) { [Convert]::ToBase64String([IO.File]::ReadAllBytes($fixture.statePath)) } else { $null })
            lockExists = (Test-Path -LiteralPath ($fixture.statePath + '.lock')); calls = @($fixture.calls)
            mutations = @($fixture.calls | Where-Object { $_ -match '^(deployment sub create|group (create|delete)|rest --method (put|patch|post|delete)|account (set|login)|provider register)\b' }) }
    }
}