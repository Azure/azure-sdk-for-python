# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

# Pester 4 entry-point fixtures. Every native CLI invocation resolves to a child-scope
# function. Entry-point invocations below use fixture tokens and never read .env.
function Get-BootstrapFixtureGuid {
    param([string[]] $Parts)
    # Independent UUIDv5 oracle: construct the network-order bytes from hex, NOT Guid.ToByteArray().
    $namespace = [Convert]::FromHexString('11fb06fb712d4ddd98c7e71bbd588830')
    $hash = [Security.Cryptography.SHA1]::HashData([byte[]] ($namespace + [Text.Encoding]::UTF8.GetBytes(($Parts -join '-'))))
    $hash[6] = ($hash[6] -band 15) -bor 80
    $hash[8] = ($hash[8] -band 63) -bor 128
    $hex = [Convert]::ToHexString([byte[]] $hash[0..15]).ToLowerInvariant()
    return '{0}-{1}-{2}-{3}-{4}' -f $hex.Substring(0, 8), $hex.Substring(8, 4), $hex.Substring(12, 4), $hex.Substring(16, 4), $hex.Substring(20, 12)
}

function ConvertTo-BootstrapFixtureCanonicalValue {
    param($Value)
    if ($Value -is [System.Collections.IDictionary]) {
        $ordered = [ordered]@{}
        $keys = [string[]] @($Value.Keys)
        [Array]::Sort($keys, [StringComparer]::Ordinal)
        foreach ($key in $keys) { $ordered[$key] = ConvertTo-BootstrapFixtureCanonicalValue -Value $Value[$key] }
        return $ordered
    }
    if ($Value -is [System.Collections.IList]) {
        $items = [object[]]::new($Value.Count)
        for ($index = 0; $index -lt $items.Count; $index++) { $items[$index] = ConvertTo-BootstrapFixtureCanonicalValue -Value $Value[$index] }
        return ,$items
    }
    return ,$Value
}

function New-BootstrapCompiledFixture {
    param($Fixture)
    $roleNames = @('foundryUser', 'storageBlobDataContributor', 'storageBlobDataOwner', 'cosmosDbOperator', 'searchServiceContributor', 'searchIndexDataContributor')
    $definitions = @{}
    $serviceGrants = @()
    for ($index = 0; $index -lt 6; $index++) {
        $role = $Fixture.grants[$index].roleDefinitionId.Split('/')[-1]
        $definitions[$roleNames[$index]] = "[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '$role')]"
        $serviceGrants += @{ roleDefinitionId = "[variables('approvedRoleDefinitionIds').$($roleNames[$index])]";
            condition = $(if ($index -eq 2) { "[variables('storageBlobOwnerCondition')]" } else { '' }) }
    }
    $nestedParameters = @{}
    foreach ($entry in @{ namePrefix = 'mi-azsdk-sample'; location = 'westus3'; locationSuffix = 'wus3' }.GetEnumerator()) {
        $nestedParameters[$entry.Key] = @{ type = 'string'; allowedValues = @($entry.Value) }
    }
    $nestedParameters['ownerToken'] = @{ type = 'string'; minLength = 32; maxLength = 32 }
    $moduleParameters = @{}
    foreach ($name in @('namePrefix', 'location', 'ownerToken')) { $moduleParameters[$name] = @{ value = "[parameters('$name')]" } }
    $moduleParameters['locationSuffix'] = @{ value = "[variables('locationSuffix')]" }
    $identityOutput = @{}
    $purposes = @('project', 'account', 'search', 'function')
    for ($index = 0; $index -lt 4; $index++) {
        $identityOutput[$purposes[$index]] = @{
            resourceId = "[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', format('{0}-{1}-{2}', parameters('namePrefix'), variables('identityPurposes')[$index], parameters('locationSuffix')))]"
            principalId = "[reference('managedIdentities[$index]').principalId]"; clientId = "[reference('managedIdentities[$index]').clientId]"
            tenantId = "[reference('managedIdentities[$index]').tenantId]"
        }
    }
    $nested = @{
        languageVersion = '2.0'; parameters = $nestedParameters
        variables = @{ identityPurposes = @('project', 'account', 'search', 'function') }
        resources = @{ managedIdentities = @{
            type = 'Microsoft.ManagedIdentity/userAssignedIdentities'; apiVersion = '2023-01-31'
            name = "[format('{0}-{1}-{2}', parameters('namePrefix'), variables('identityPurposes')[copyIndex()], parameters('locationSuffix'))]"
            location = "[parameters('location')]"
            copy = @{ name = 'managedIdentities'; count = "[length(variables('identityPurposes'))]" }
            tags = @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = "[parameters('ownerToken')]";
                'sample-ci-retention' = 'permanent'; 'sample-ci-identity' = "[variables('identityPurposes')[copyIndex()]]" }
        } }
        outputs = @{ identities = @{ type = 'object'; value = $identityOutput } }
    }
    return @{
        languageVersion = '2.0'
        parameters = @{
            identityResourceGroup = @{ type = 'string'; allowedValues = @('rg-azsdk-sample-identities-wus3') }
            namePrefix = @{ type = 'string'; allowedValues = @('mi-azsdk-sample') }
            location = @{ type = 'string'; allowedValues = @('westus3') }
            ownerToken = @{ type = 'string'; minLength = 32; maxLength = 32 }
            pipelinePrincipalId = @{ type = 'string'; minLength = 36; maxLength = 36 }
        }
        variables = @{
            locationSuffix = 'wus3'; approvedRoleDefinitionIds = $definitions; storageBlobOwnerCondition = $Fixture.condition
            projectServiceGrants = $serviceGrants
            projectIdentityResourceId = "[resourceId(subscription().subscriptionId, parameters('identityResourceGroup'), 'Microsoft.ManagedIdentity/userAssignedIdentities', format('{0}-project-{1}', parameters('namePrefix'), variables('locationSuffix')))]"
        }
        resources = @{
            identityResources = @{
                type = 'Microsoft.Resources/resourceGroups'; apiVersion = '2024-03-01'; name = "[parameters('identityResourceGroup')]"; location = "[parameters('location')]"
                tags = @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = "[parameters('ownerToken')]"; 'sample-ci-retention' = 'permanent' }
            }
            sharedIdentities = @{
                type = 'Microsoft.Resources/deployments'; apiVersion = '2025-04-01'
                name = "[format('shared-identities-{0}', uniqueString(subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('identityResourceGroup')), parameters('namePrefix'), variables('locationSuffix')))]"
                resourceGroup = "[parameters('identityResourceGroup')]"
                properties = @{ expressionEvaluationOptions = @{ scope = 'inner' }; mode = 'Incremental'; parameters = $moduleParameters; template = $nested }
            }
            projectRoleAssignments = @{
                type = 'Microsoft.Authorization/roleAssignments'; apiVersion = '2022-04-01'
                copy = @{ name = 'projectRoleAssignments'; count = "[length(variables('projectServiceGrants'))]" }
                name = "[guid(toLower(variables('projectIdentityResourceId')), toLower(subscription().id), toLower(variables('projectServiceGrants')[copyIndex()].roleDefinitionId), variables('projectServiceGrants')[copyIndex()].condition)]"
                properties = @{
                    principalId = "[reference('sharedIdentities').outputs.identities.value.project.principalId]"
                    principalType = 'ServicePrincipal'
                    roleDefinitionId = "[variables('projectServiceGrants')[copyIndex()].roleDefinitionId]"
                    condition = "[if(empty(variables('projectServiceGrants')[copyIndex()].condition), null(), variables('projectServiceGrants')[copyIndex()].condition)]"
                    conditionVersion = "[if(empty(variables('projectServiceGrants')[copyIndex()].condition), null(), '2.0')]"
                }
            }
            pipelineFoundryUser = @{
                type = 'Microsoft.Authorization/roleAssignments'; apiVersion = '2022-04-01'
                name = "[guid(toLower(parameters('pipelinePrincipalId')), toLower(subscription().id), toLower(variables('approvedRoleDefinitionIds').foundryUser), '')]"
                properties = @{ principalId = "[parameters('pipelinePrincipalId')]"; principalType = 'ServicePrincipal'; roleDefinitionId = "[variables('approvedRoleDefinitionIds').foundryUser]" }
            }
        }
        outputs = @{
            identityResourceGroupId = @{ type = 'string'; value = "[subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('identityResourceGroup'))]" }
            identities = @{ type = 'object'; value = "[reference('sharedIdentities').outputs.identities.value]" }
            roleDefinitionIds = @{ type = 'object'; value = "[variables('approvedRoleDefinitionIds')]" }
            blobOwnerCondition = @{ type = 'string'; value = "[variables('storageBlobOwnerCondition')]" }
            roleAssignments = @{ type = 'object'; value = @{
                project = "[map(variables('projectServiceGrants'), lambda('grant', createObject('roleAssignmentId', subscriptionResourceId('Microsoft.Authorization/roleAssignments', guid(toLower(variables('projectIdentityResourceId')), toLower(subscription().id), toLower(lambdaVariables('grant').roleDefinitionId), lambdaVariables('grant').condition)), 'principalId', reference('sharedIdentities').outputs.identities.value.project.principalId, 'roleDefinitionId', lambdaVariables('grant').roleDefinitionId, 'scope', subscription().id, 'condition', lambdaVariables('grant').condition, 'conditionVersion', if(empty(lambdaVariables('grant').condition), '', '2.0'))))]"
                pipeline = @{
                    roleAssignmentId = "[subscriptionResourceId('Microsoft.Authorization/roleAssignments', guid(toLower(parameters('pipelinePrincipalId')), toLower(subscription().id), toLower(variables('approvedRoleDefinitionIds').foundryUser), ''))]"
                    principalId = "[parameters('pipelinePrincipalId')]"; roleDefinitionId = "[variables('approvedRoleDefinitionIds').foundryUser]"
                    scope = "[subscription().id]"; condition = ''; conditionVersion = ''
                }
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
    $fixture = @{
        subscriptionId = '11111111-1111-1111-1111-111111111111'; tenantId = '22222222-2222-2222-2222-222222222222'
        pipelinePrincipalId = '88888888-8888-8888-8888-888888888888'; pipelineClientId = '99999999-9999-9999-9999-999999999999'
        callerId = '33333333-3333-3333-3333-333333333333'; ownerToken = '0123456789abcdef0123456789abcdef'
        groupExists = $false; state = $null; descendants = @(); parents = @(); calls = [Collections.Generic.List[string]]::new()
        validation = @{ properties = @{ provisioningState = 'Succeeded' }; error = $null }
        prediction = @{ status = 'Succeeded'; changes = @(); error = $null }; stateDuringWhatIf = $null
        ids = @{}; identities = @{}; live = @{}; grants = @(); recorded = $null
        condition = "((!(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read'})  AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/filter/action'}) AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write'}) ) OR (@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringLikeIgnoreCase '*-azureml-agent'))"
    }
    $fixture.scope = '/subscriptions/' + $fixture.subscriptionId
    $fixture.groupId = $fixture.scope + '/resourceGroups/rg-azsdk-sample-identities-wus3'
    $purposes = @('project', 'account', 'search', 'function')
    $principals = @('44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555555',
        '66666666-6666-6666-6666-666666666666', '77777777-7777-7777-7777-777777777777')
    $clients = @('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
        'cccccccc-cccc-4ccc-8ccc-cccccccccccc', 'dddddddd-dddd-4ddd-8ddd-dddddddddddd')
    $fixture.prediction.changes += @{ resourceId = $fixture.groupId; changeType = 'Create'; after = @{ type = 'Microsoft.Resources/resourceGroups' } }
    for ($index = 0; $index -lt 4; $index++) {
        $purpose = $purposes[$index]
        $id = $fixture.groupId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mi-azsdk-sample-' + $purpose + '-wus3'
        $fixture.ids[$purpose] = $id
        $fixture.identities[$purpose] = @{ resourceId = $id; principalId = $principals[$index]; clientId = $clients[$index]; tenantId = $fixture.tenantId }
        $fixture.live[$purpose] = @{ id = $id; type = 'Microsoft.ManagedIdentity/userAssignedIdentities'; location = 'westus3'
            properties = @{ principalId = $principals[$index]; clientId = $clients[$index]; tenantId = $fixture.tenantId }
            tags = @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = $fixture.ownerToken; 'sample-ci-retention' = 'permanent'; 'sample-ci-identity' = $purpose } }
        $fixture.prediction.changes += @{ resourceId = $id; changeType = 'Create'; after = @{ type = 'Microsoft.ManagedIdentity/userAssignedIdentities' } }
    }
    $roles = @('53ca6127-db72-4b80-b1b0-d745d6d5456d', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe',
        'b7e6dc6d-f1e8-4753-8033-0f276bb0955b', '230815da-be43-4aae-9cb4-875f7bd000aa',
        '7ca78c08-252a-4471-8644-bb5ff32d4ba0', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
    for ($index = 0; $index -lt 7; $index++) {
        $role = if ($index -eq 6) { $roles[0] } else { $roles[$index] }
        $condition = if ($index -eq 2) { $fixture.condition } else { '' }
        $definition = $fixture.scope + '/providers/Microsoft.Authorization/roleDefinitions/' + $role
        $seed = if ($index -eq 6) { $fixture.pipelinePrincipalId } else { $fixture.ids.project }
        $name = Get-BootstrapFixtureGuid -Parts @($seed.ToLowerInvariant(), $fixture.scope.ToLowerInvariant(), $definition.ToLowerInvariant(), $condition)
        $grant = @{ kind = $(if ($index -eq 6) { 'pipeline' } else { 'project' }); roleAssignmentId = ($fixture.scope + '/providers/Microsoft.Authorization/roleAssignments/' + $name)
            roleDefinitionId = $definition; scope = $fixture.scope; condition = $condition; conditionVersion = $(if ($condition) { '2.0' } else { '' }) }
        $fixture.grants += $grant
        $properties = @{ roleDefinitionId = $definition; scope = $fixture.scope; condition = $condition; conditionVersion = $grant.conditionVersion; principalType = 'ServicePrincipal' }
        if ($index -eq 6) { $properties['principalId'] = $fixture.pipelinePrincipalId }
        $fixture.prediction.changes += @{ resourceId = $grant.roleAssignmentId; changeType = $(if ($index -eq 6) { 'Create' } else { 'Unsupported' })
            after = @{ type = 'Microsoft.Authorization/roleAssignments'; properties = $properties } }
    }
    $fixture.compiled = New-BootstrapCompiledFixture -Fixture $fixture
    return $fixture
}

function Set-BootstrapRecordedFixture {
    param($Fixture, [string] $Status = 'Created')
    $Fixture.state = @{ schemaVersion = 1; status = $Status; subscriptionId = $Fixture.subscriptionId; tenantId = $Fixture.tenantId
        pipelinePrincipalId = $Fixture.pipelinePrincipalId; pipelineClientId = $Fixture.pipelineClientId; expectedCallerPrincipalId = $Fixture.callerId
        identityResourceGroup = 'rg-azsdk-sample-identities-wus3'; ownerToken = $Fixture.ownerToken
        deploymentName = ('sample-ci-shared-identities-' + $Fixture.ownerToken.Substring(0, 12)); identityResourceIds = $Fixture.ids
        templateHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes((ConvertTo-BootstrapFixtureCanonicalValue -Value $Fixture.compiled | ConvertTo-Json -Depth 100 -Compress)))).ToLowerInvariant() }
    $definitions = @{}
    $roleNames = @('foundryUser', 'storageBlobDataContributor', 'storageBlobDataOwner', 'cosmosDbOperator', 'searchServiceContributor', 'searchIndexDataContributor')
    $metadata = @()
    for ($index = 0; $index -lt 7; $index++) {
        $grant = $Fixture.grants[$index]
        $entry = @{} + $grant
        $entry.Remove('kind')
        $entry['principalId'] = if ($index -eq 6) { $Fixture.pipelinePrincipalId } else { $Fixture.identities.project.principalId }
        $metadata += $entry
        if ($index -lt 6) { $definitions[$roleNames[$index]] = $grant.roleDefinitionId }
    }
    $outputs = @{ identityResourceGroupId = @{ type = 'String'; value = $Fixture.groupId }
        identities = @{ type = 'Object'; value = $Fixture.identities }; blobOwnerCondition = @{ type = 'String'; value = $Fixture.condition }
        roleDefinitionIds = @{ type = 'Object'; value = $definitions }
        roleAssignments = @{ type = 'Object'; value = @{ project = @($metadata[0..5]); pipeline = $metadata[6] } } }
    if ($Status -cin @('Created', 'Verified')) { $Fixture.state['outputs'] = $outputs }
    if ($Status -ceq 'Verified') { $Fixture.state['identities'] = $Fixture.identities | ConvertTo-Json -Depth 10 | ConvertFrom-Json -AsHashtable }
    $Fixture.recorded = @{ id = ($Fixture.scope + '/providers/Microsoft.Resources/deployments/' + $Fixture.state.deploymentName)
        name = $Fixture.state.deploymentName; type = 'Microsoft.Resources/deployments'
        properties = @{ provisioningState = 'Succeeded'; outputs = $outputs; parameters = @{
            identityResourceGroup = @{ value = 'rg-azsdk-sample-identities-wus3' }; namePrefix = @{ value = 'mi-azsdk-sample' }
            location = @{ value = 'westus3' }; ownerToken = @{ value = $Fixture.ownerToken }; pipelinePrincipalId = @{ value = $Fixture.pipelinePrincipalId }
        } } }
    $Fixture.groupExists = $true
    $Fixture.descendants = @()
    for ($index = 0; $index -lt 7; $index++) {
        $principal = if ($index -eq 6) { $Fixture.pipelinePrincipalId } else { $Fixture.identities.project.principalId }
        $Fixture.descendants += New-BootstrapFixtureAssignment -Grant $Fixture.grants[$index] -PrincipalId $principal
    }
    $Fixture.parents = @($Fixture.descendants)
}

Describe 'Shared identity bootstrap fails closed through the real entry point' {
    BeforeEach {
        $script:bootstrapOriginalSubscription = $env:AZURE_SUBSCRIPTION_ID
        $script:bootstrapOriginalTenant = $env:AZURE_TENANT_ID
        $script:bootstrapFixture = New-BootstrapCliFixture
        $env:AZURE_SUBSCRIPTION_ID = $script:bootstrapFixture.subscriptionId
        $env:AZURE_TENANT_ID = $script:bootstrapFixture.tenantId
        $script:bootstrapFixture.sourceDirectory = $PSScriptRoot
    }
    AfterEach {
        $env:AZURE_SUBSCRIPTION_ID = $script:bootstrapOriginalSubscription
        $env:AZURE_TENANT_ID = $script:bootstrapOriginalTenant
    }

    function Invoke-IsolatedBootstrap {
        param([switch] $Apply, [switch] $VerifyOnly, [switch] $Preview)
        $fixture = $script:bootstrapFixture
        $sandbox = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
        $validationDirectory = Join-Path $sandbox 'validation'
        $infraDirectory = Join-Path $sandbox 'infra'
        $null = New-Item -ItemType Directory -Path $validationDirectory, $infraDirectory -Force
        Copy-Item -LiteralPath (Join-Path $fixture.sourceDirectory 'Initialize-SharedSampleIdentities.ps1') -Destination $validationDirectory
        Copy-Item -LiteralPath (Join-Path $fixture.sourceDirectory '../SampleCiHelpers.ps1') -Destination $sandbox
        foreach ($name in @('bootstrap-identities.bicep', 'shared-identities.bicep')) {
            Copy-Item -LiteralPath (Join-Path $fixture.sourceDirectory ('../infra/' + $name)) -Destination $infraDirectory
        }
        $fixture.statePath = Join-Path $sandbox 'bootstrap-state.json'
        if ($null -ne $fixture.state) { $fixture.state | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $fixture.statePath -Encoding utf8 }
        $original = if (Test-Path -LiteralPath $fixture.statePath) { Get-Content -LiteralPath $fixture.statePath -Raw } else { $null }
        & {
            function Invoke-RestMethod {
                param($Method, $Uri, $Headers, $TimeoutSec, $MaximumRedirection)
                if ($Method -cne 'Get' -or $Uri -notmatch '^https://management\.azure\.com/' -or
                    $Headers.Count -ne 1 -or $TimeoutSec -ne 45 -or $MaximumRedirection -ne 0) {
                    throw 'Unexpected HTTP metadata request in isolated bootstrap fixture.'
                }
                $json = az rest --method get --url $Uri
                return ($json | ConvertFrom-Json -AsHashtable -NoEnumerate)
            }
            function az {
                $global:LASTEXITCODE = 0
                $fixture.calls.Add(($args -join ' '))
                if ($args[0] -ceq 'account' -and $args[1] -ceq 'show') {
                    return (@{ id = $fixture.subscriptionId; tenantId = $fixture.tenantId; state = 'Enabled'; user = @{ type = 'user' } } | ConvertTo-Json -Depth 5)
                }
                if ($args[0] -ceq 'account' -and $args[1] -ceq 'get-access-token') {
                    $claims = @{ tid = $fixture.tenantId; oid = $fixture.callerId; scp = 'user_impersonation' }
                    $payload = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($claims | ConvertTo-Json -Compress))).TrimEnd('=').Replace('+', '-').Replace('/', '_')
                    return (@{ accessToken = ('fixture.' + $payload + '.not-a-real-token') } | ConvertTo-Json -Compress)
                }
                if (($args[0..2] -join ' ') -ceq 'ad sp show') {
                    return (@{ id = $fixture.pipelinePrincipalId; appId = $fixture.pipelineClientId; accountEnabled = $true } | ConvertTo-Json)
                }
                if (($args[0..1] -join ' ') -ceq 'group exists') { return (ConvertTo-Json -InputObject $fixture.groupExists -Depth 10) }
                if (($args[0..1] -join ' ') -ceq 'group show') {
                    return (@{ id = $fixture.groupId; location = 'westus3'; tags = @{ purpose = 'azsdk-sample-identities';
                        'sample-ci-owner' = $fixture.ownerToken; 'sample-ci-retention' = 'permanent' } } | ConvertTo-Json -Depth 5)
                }
                if (($args[0..1] -join ' ') -ceq 'provider show') { return '{"registrationState":"Registered"}' }
                if (($args[0..1] -join ' ') -ceq 'bicep build') { return ($fixture.compiled | ConvertTo-Json -Depth 100) }
                if (($args[0..2] -join ' ') -ceq 'deployment sub validate') { return (ConvertTo-Json -InputObject $fixture.validation -Depth 100) }
                if (($args[0..2] -join ' ') -ceq 'deployment sub what-if') {
                    if ($fixture.stateDuringWhatIf) {
                        $changed = Get-Content -LiteralPath $fixture.statePath -Raw | ConvertFrom-Json -AsHashtable
                        $changed['status'] = $fixture.stateDuringWhatIf
                        $changed | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $fixture.statePath -Encoding utf8
                    }
                    return (ConvertTo-Json -InputObject $fixture.prediction -Depth 100)
                }
                if (($args[0..2] -join ' ') -ceq 'rest --method get') {
                    $url = $args[[Array]::IndexOf($args, '--url') + 1]
                    $base = 'https://management.azure.com' + $fixture.scope + '/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01'
                    if ($url -ceq $base) { return (@{ value = @($fixture.descendants); nextLink = $null } | ConvertTo-Json -Depth 20) }
                    if ($url -ceq ($base + '&$filter=atScope()')) { return (@{ value = @($fixture.parents); nextLink = $null } | ConvertTo-Json -Depth 20) }
                    if ($fixture.recorded -and $url -ceq ('https://management.azure.com' + $fixture.recorded.id + '?api-version=2022-09-01')) {
                        return ($fixture.recorded | ConvertTo-Json -Depth 40)
                    }
                    foreach ($purpose in @('project', 'account', 'search', 'function')) {
                        if ($url -ceq ('https://management.azure.com' + $fixture.ids[$purpose] + '?api-version=2023-01-31')) { return ($fixture.live[$purpose] | ConvertTo-Json -Depth 10) }
                    }
                }
                throw 'Unexpected or mutating CLI command in the isolated bootstrap fixture.'
            }
            if ((Get-Command az).CommandType -cne 'Function') { throw 'Azure CLI isolation failed.' }
            $failure = $null
            try {
                $null = & (Join-Path $validationDirectory 'Initialize-SharedSampleIdentities.ps1') -StatePath $fixture.statePath `
                    -PipelinePrincipalId $fixture.pipelinePrincipalId -PipelineClientId $fixture.pipelineClientId `
                    -ExpectedCallerPrincipalId $fixture.callerId -Apply:$Apply -VerifyOnly:$VerifyOnly -WhatIf:$Preview -Confirm:$false
            } catch { $failure = $_.Exception.Message }
            $text = if (Test-Path -LiteralPath $fixture.statePath) { Get-Content -LiteralPath $fixture.statePath -Raw } else { $null }
            [pscustomobject]@{ failure = $failure; state = $(if ($text) { $text | ConvertFrom-Json -AsHashtable } else { $null }); original = $original; text = $text
                calls = @($fixture.calls); mutations = @($fixture.calls | Where-Object { $_ -match '^(deployment sub create|group (create|delete)|rest --method (put|patch|post|delete)|account (set|login)|provider register)\b' }) }
        }
    }

    It 'previews the exact twelve resource IDs, including six runtime-only role IDs derived by RFC4122 UUIDv5' {
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty
        $result.state.status | Should Be 'Previewed'
        @($result.calls | Where-Object { $_ -match '^deployment sub what-if .*--no-pretty-print .*--result-format FullResourcePayloads' }).Count | Should Be 1
        $result.mutations.Count | Should Be 0
    }

    It 'requires a separately saved dry run before apply' {
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Match 'separate dry run'
        $result.calls.Count | Should Be 0
        $result.state | Should BeNullOrEmpty
    }

    It 'never replays recorded <Status>, even with an absent RG' -TestCases @(
        @{ Status = 'Applying' }, @{ Status = 'Failed' }, @{ Status = 'Created' }, @{ Status = 'Verified' }
    ) {
        param($Status)
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status $Status
        $script:bootstrapFixture.groupExists = $false
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Match 'already recorded'
        $result.calls.Count | Should Be 0
        $result.text | Should Be $result.original
    }

    It 'rejects malformed state <Label> before any CLI invocation' -TestCases @(
        @{ Label = 'schema number as a string'; Field = 'schemaVersion'; Value = '1' },
        @{ Label = 'schema boolean'; Field = 'schemaVersion'; Value = $true },
        @{ Label = 'unknown status'; Field = 'status'; Value = 'Retryable' },
        @{ Label = 'status array'; Field = 'status'; Value = @('Previewed') },
        @{ Label = 'foreign deployment'; Field = 'deploymentName'; Value = 'another-deployment' }
    ) {
        param($Label, $Field, $Value)
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Previewed
        $script:bootstrapFixture.state[$Field] = $Value
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty
        $result.calls.Count | Should Be 0
        $result.text | Should Be $result.original
    }

    It 'requires group-exists to be a JSON boolean, not <Label>' -TestCases @(
        @{ Label = 'null'; Value = $null }, @{ Label = 'a string'; Value = 'false' }, @{ Label = 'zero'; Value = 0 },
        @{ Label = 'an object'; Value = @{} }, @{ Label = 'a singleton JSON array'; Value = @($false) }
    ) {
        param($Label, $Value)
        $script:bootstrapFixture.groupExists = $Value
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'actual JSON boolean'
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'rejects validation without explicit success: <Label>' -TestCases @(
        @{ Label = 'null'; Value = $null }, @{ Label = 'empty object'; Value = @{} },
        @{ Label = 'failed state plus null error'; Value = @{ properties = @{ provisioningState = 'Failed' }; error = $null } },
        @{ Label = 'state array'; Value = @{ properties = @{ provisioningState = @('Succeeded') }; error = $null } },
        @{ Label = 'failed status plus null error'; Value = @{ status = 'Failed'; error = $null } },
        @{ Label = 'contradictory status'; Value = @{ status = 'Failed'; properties = @{ provisioningState = 'Succeeded' }; error = $null } },
        @{ Label = 'error envelope'; Value = @{ error = @{ code = 'Denied' } } },
        @{ Label = 'singleton root array'; Value = @(@{ error = $null }) }
    ) {
        param($Label, $Value)
        $script:bootstrapFixture.validation = $Value
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'validation'
        $result.state | Should BeNullOrEmpty
        @($result.calls | Where-Object { $_ -match '^deployment sub what-if ' }).Count | Should Be 0
        $result.mutations.Count | Should Be 0
    }

    It 'accepts the native validation error:null success shape without inventing success for missing error' {
        $script:bootstrapFixture.validation = @{ error = $null }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty
        $result.state.status | Should Be 'Previewed'
        $result.mutations.Count | Should Be 0
    }

    It 'rejects malformed what-if <Label>' -TestCases @(
        @{ Label = 'null'; Value = $null }, @{ Label = 'empty object'; Value = @{} },
        @{ Label = 'failed status'; Value = @{ status = 'Failed'; changes = @() } },
        @{ Label = 'status array'; Value = @{ status = @('Succeeded'); changes = @() } },
        @{ Label = 'null changes'; Value = @{ status = 'Succeeded'; changes = $null } },
        @{ Label = 'changes string'; Value = @{ status = 'Succeeded'; changes = '[]' } },
        @{ Label = 'singleton root array'; Value = @(@{ status = 'Succeeded'; changes = @() }) }
    ) {
        param($Label, $Value)
        $script:bootstrapFixture.prediction = $Value
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'What-if'
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'rejects foreign what-if IDs even for <ChangeType>' -TestCases @(@{ ChangeType = 'Create' }, @{ ChangeType = 'NoChange' }, @{ ChangeType = 'Unsupported' }) {
        param($ChangeType)
        $script:bootstrapFixture.prediction.changes += @{ resourceId = ($script:bootstrapFixture.scope + '/providers/Microsoft.Authorization/roleAssignments/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee')
            changeType = $ChangeType; after = @{ type = 'Microsoft.Authorization/roleAssignments' } }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'unknown or duplicate resource ID'
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'does not wildcard resources under the approved identity RG' {
        $script:bootstrapFixture.prediction.changes += @{ resourceId = ($script:bootstrapFixture.groupId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/not-approved')
            changeType = 'Create'; after = @{ type = 'Microsoft.ManagedIdentity/userAssignedIdentities' } }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'unknown or duplicate resource ID'
        $result.mutations.Count | Should Be 0
    }

    It 'limits Unsupported to the six exact project assignment IDs' {
        $script:bootstrapFixture.prediction.changes[1].changeType = 'Unsupported'
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'Only new group, identity, and module'
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'checks all seven grant definitions in the compiled schema before ARM validation' {
        $script:bootstrapFixture.compiled.variables.approvedRoleDefinitionIds.foundryUser = "[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635')]"
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'Compiled bootstrap expression'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0
        $result.state | Should BeNullOrEmpty
    }

    It 'rejects the opaque union project properties before ARM validation' {
        $script:bootstrapFixture.compiled.resources.projectRoleAssignments.properties = "[union(createObject('principalId', reference('sharedIdentities').outputs.identities.value.project.principalId, 'principalType', 'ServicePrincipal', 'roleDefinitionId', variables('projectServiceGrants')[copyIndex()].roleDefinitionId), if(empty(variables('projectServiceGrants')[copyIndex()].condition), createObject(), createObject('condition', variables('projectServiceGrants')[copyIndex()].condition, 'conditionVersion', '2.0')))]"
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'bootstrap object schema'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'rejects changed compiled project <Field>: <Label> before ARM validation' -TestCases @(
        @{ Field = 'principalId'; Label = 'another identity'; Value = "[reference('sharedIdentities').outputs.identities.value.account.principalId]" },
        @{ Field = 'principalType'; Label = 'another principal type'; Value = 'User' },
        @{ Field = 'roleDefinitionId'; Label = 'a fixed role instead of the six grants'; Value = "[variables('approvedRoleDefinitionIds').foundryUser]" },
        @{ Field = 'condition'; Label = 'missing null branch'; Value = "[variables('projectServiceGrants')[copyIndex()].condition]" },
        @{ Field = 'conditionVersion'; Label = 'unconditional version'; Value = '2.0' },
        @{ Field = 'condition'; Label = 'literal JSON null'; Value = $null },
        @{ Field = 'conditionVersion'; Label = 'literal JSON null'; Value = $null }
    ) {
        param($Field, $Label, $Value)
        $script:bootstrapFixture.compiled.resources.projectRoleAssignments.properties[$Field] = $Value
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'contract value differs'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'rejects a redirected module principal output before it can grant the roles to another identity' {
        $script:bootstrapFixture.compiled.resources.sharedIdentities.properties.template.outputs.identities.value.project.principalId = "[reference('managedIdentities[1]').principalId]"
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'Compiled bootstrap expression'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0
        $result.mutations.Count | Should Be 0
    }

    It 'accepts NoChange only for an already exact pipeline grant and deduplicates list views by ID' {
        $fixture = $script:bootstrapFixture
        $assignment = New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId
        $fixture.descendants = @($assignment); $fixture.parents = @($assignment)
        $fixture.prediction.changes[-1].changeType = 'NoChange'
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty
        $result.state.status | Should Be 'Previewed'
        $result.mutations.Count | Should Be 0
    }

    It 'accepts omitted principalType only in the schema-checked what-if payload' {
        $script:bootstrapFixture.prediction.changes[-1].after.properties.Remove('principalType')
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty
        $result.state.status | Should Be 'Previewed'
        $result.mutations.Count | Should Be 0
    }

    It 'rejects explicit invalid what-if principalType: <Label>' -TestCases @(
        @{ Label = 'user'; Value = 'User' }, @{ Label = 'null'; Value = $null }, @{ Label = 'empty'; Value = '' }
    ) {
        param($Label, $Value)
        $script:bootstrapFixture.prediction.changes[-1].after.properties['principalType'] = $Value
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'could not be verified exactly'
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'rejects an existing grant whose actual GET metadata omits principalType' {
        $fixture = $script:bootstrapFixture
        $assignment = New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId
        $assignment.properties.Remove('principalType')
        $fixture.descendants = @($assignment)
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'could not be verified exactly'
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'does not relax principalType verification after creation' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture
        $script:bootstrapFixture.descendants[0].properties.Remove('principalType')
        $script:bootstrapFixture.parents = @($script:bootstrapFixture.descendants)
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'could not be verified exactly'
        $result.state.status | Should Be 'Created'
        $result.mutations.Count | Should Be 0
    }

    It 'rejects an unverified NoChange pipeline grant instead of trusting the prediction' {
        $script:bootstrapFixture.prediction.changes[-1].changeType = 'NoChange'
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'unverified pipeline grant'
        $result.mutations.Count | Should Be 0
    }

    It 'rejects a stale project assignment before any ARM preview rather than reusing its stable name' {
        $fixture = $script:bootstrapFixture
        $fixture.descendants = @(New-BootstrapFixtureAssignment -Grant $fixture.grants[0] -PrincipalId 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee')
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'stale or replacement identity'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0
        $result.mutations.Count | Should Be 0
    }

    It 'refuses a pipeline grant whose condition metadata differs instead of modifying it' {
        $fixture = $script:bootstrapFixture
        $assignment = New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId
        $assignment.properties.conditionVersion = '2.0'
        $fixture.descendants = @($assignment)
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'could not be verified exactly'
        $result.state | Should BeNullOrEmpty
        $result.mutations.Count | Should Be 0
    }

    It 'keeps WhatIf apply in Previewed without submitting a create' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Previewed
        $script:bootstrapFixture.groupExists = $false
        $script:bootstrapFixture.descendants = @(); $script:bootstrapFixture.parents = @()
        $result = Invoke-IsolatedBootstrap -Apply -Preview
        $result.failure | Should BeNullOrEmpty
        $result.state.status | Should Be 'Previewed'
        $result.mutations.Count | Should Be 0
    }

    It 'cannot overwrite a concurrently recorded attempt with Previewed or apply it again' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Previewed
        $script:bootstrapFixture.groupExists = $false
        $script:bootstrapFixture.descendants = @(); $script:bootstrapFixture.parents = @()
        $script:bootstrapFixture.stateDuringWhatIf = 'Applying'
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Match 'no replay or state downgrade'
        $result.state.status | Should Be 'Applying'
        $result.mutations.Count | Should Be 0
    }

    It 'verifies immutable outputs and the exact six/zero assignment sets using both list views' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty
        $result.state.status | Should Be 'Verified'
        $result.state.identities.project.principalId | Should Be $script:bootstrapFixture.identities.project.principalId
        @($result.calls | Where-Object { $_ -match '/roleAssignments\?api-version=2022-04-01$' }).Count | Should Be 1
        @($result.calls | Where-Object { $_ -match '\$filter=atScope\(\)' }).Count | Should Be 1
        $result.mutations.Count | Should Be 0
    }

    It 'rejects a same-name, same-tags replacement of <Purpose> (<Field>)' -TestCases @(
        @{ Purpose = 'project'; Field = 'principalId' }, @{ Purpose = 'account'; Field = 'principalId' },
        @{ Purpose = 'search'; Field = 'principalId' }, @{ Purpose = 'function'; Field = 'principalId' },
        @{ Purpose = 'project'; Field = 'clientId' }
    ) {
        param($Purpose, $Field)
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture
        $script:bootstrapFixture.live[$Purpose].properties[$Field] = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'replacement identity'
        $result.text | Should Be $result.original
        @($result.calls | Where-Object { $_ -match '/providers/Microsoft.Resources/deployments/' }).Count | Should Be 0
        $result.mutations.Count | Should Be 0
    }

    It 'detects an extra <Boundary> assignment for <Purpose>, not merely atScope grants' -TestCases @(
        @{ Purpose = 'project'; Boundary = 'RG' }, @{ Purpose = 'project'; Boundary = 'resource' }, @{ Purpose = 'project'; Boundary = 'inherited' },
        @{ Purpose = 'account'; Boundary = 'RG' }, @{ Purpose = 'search'; Boundary = 'resource' }, @{ Purpose = 'function'; Boundary = 'inherited' }
    ) {
        param($Purpose, $Boundary)
        $fixture = $script:bootstrapFixture
        Set-BootstrapRecordedFixture -Fixture $fixture
        $target = switch ($Boundary) {
            'RG' { $fixture.scope + '/resourceGroups/another-group' }
            'resource' { $fixture.scope + '/resourceGroups/another-group/providers/Microsoft.Storage/storageAccounts/example' }
            'inherited' { '/providers/Microsoft.Management/managementGroups/example-parent' }
        }
        $grant = @{ roleAssignmentId = ($target + '/providers/Microsoft.Authorization/roleAssignments/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee')
            roleDefinitionId = ($fixture.scope + '/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c')
            scope = $target; condition = ''; conditionVersion = '' }
        $assignment = New-BootstrapFixtureAssignment -Grant $grant -PrincipalId $fixture.identities[$Purpose].principalId
        if ($Boundary -ceq 'inherited') { $fixture.parents += $assignment } else { $fixture.descendants += $assignment }
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'exact identity grant set differs'
        $result.text | Should Be $result.original
        $result.mutations.Count | Should Be 0
    }

    It 'reconciles ambiguous <Status> using only the recorded deployment GET outputs' -TestCases @(@{ Status = 'Applying' }, @{ Status = 'Failed' }) {
        param($Status)
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status $Status
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty
        $result.state.status | Should Be 'Verified'
        $result.state.outputs.identities.value.function.clientId | Should Be $script:bootstrapFixture.identities.function.clientId
        @($result.calls | Where-Object { $_ -match '^rest --method get .*?/providers/Microsoft.Resources/deployments/sample-ci-shared-identities-0123456789ab\?api-version=2022-09-01' }).Count | Should Be 1
        $result.mutations.Count | Should Be 0
    }

    It 'does not mark an ambiguous attempt verified without successful recorded outputs' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Failed
        $script:bootstrapFixture.recorded.properties.provisioningState = 'Failed'
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'immutable output baseline'
        $result.text | Should Be $result.original
        $result.state.status | Should Be 'Failed'
        $result.mutations.Count | Should Be 0
    }

    It 'does not refresh Verified metadata from a different saved identity binding' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Verified
        $script:bootstrapFixture.state.identities.search.clientId = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'contract value differs'
        $result.text | Should Be $result.original
        $result.mutations.Count | Should Be 0
    }
}