# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)] [string] $StatePath,
    [Parameter(Mandatory)] [ValidatePattern('^[a-fA-F0-9-]{36}$')] [string] $PipelinePrincipalId,
    [Parameter(Mandatory)] [ValidatePattern('^[a-fA-F0-9-]{36}$')] [string] $PipelineClientId,
    [Parameter(Mandatory)] [ValidatePattern('^[a-fA-F0-9-]{36}$')] [string] $ExpectedCallerPrincipalId,
    [switch] $Apply,
    [switch] $VerifyOnly
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '../SampleCiHelpers.ps1')

# These guards belong to this administrator-only entry point, not the worker helper.
function Invoke-BootstrapAzure {
    param([Parameter(Mandatory)] [string[]] $Arguments, [switch] $Sensitive)
    if (-not $Sensitive) { throw 'Bootstrap CLI responses must remain protected.' }
    if ($Arguments[0] -ceq 'rest') {
        $urlIndex = [Array]::IndexOf($Arguments, '--url')
        if (($Arguments[0..2] -join ' ') -cne 'rest --method get' -or $urlIndex -lt 0 -or
            $Arguments[$urlIndex + 1] -notmatch '^https://management\.azure\.com/' -or -not $bootstrapArmHeaders) {
            throw 'Bootstrap HTTP metadata requests must be approved current-user ARM GETs.'
        }
        try {
            $response = Invoke-RestMethod -Method Get -Uri $Arguments[$urlIndex + 1] -Headers $bootstrapArmHeaders -TimeoutSec 45 -MaximumRedirection 0
            return ,($response | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable -NoEnumerate)
        } catch { throw 'Bootstrap ARM metadata GET failed; raw response suppressed.' }
    }
    $PSNativeCommandUseErrorActionPreference = $false
    try {
        $captured = @(& az @Arguments --only-show-errors --output json 2>&1)
        $exitCode = $LASTEXITCODE
    } catch { throw 'Bootstrap CLI execution failed; response content suppressed.' }
    if ($exitCode -ne 0) {
        $codes = @(Get-SampleAzureCliErrorCodes -Text ($captured -join [Environment]::NewLine))
        throw ('Bootstrap CLI failed; response content suppressed. ARM error codes: ' + ($codes -join ', '))
    }
    try {
        # The worker wrapper enumerates root JSON arrays. This entry point must retain
        # them so [false] and [{...}] cannot masquerade as a boolean or an object.
        $parsed = ($captured -join [Environment]::NewLine) | ConvertFrom-Json -AsHashtable -NoEnumerate -ErrorAction Stop
    } catch { throw 'Bootstrap CLI returned invalid protected JSON; response content suppressed.' }
    return ,$parsed
}

function Assert-BootstrapKeys {
    param($Value, [string[]] $Required, [string[]] $Optional = @())
    if ($Value -isnot [System.Collections.IDictionary]) { throw 'Invalid bootstrap object schema.' }
    foreach ($key in $Required) {
        if (-not $Value.Contains($key)) { throw 'Incomplete bootstrap object schema.' }
    }
    foreach ($key in $Value.Keys) {
        if ($key -cnotin ($Required + $Optional)) { throw 'Unexpected bootstrap object property.' }
    }
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
    # ARM guid(): RFC 4122 UUIDv5, with the arguments joined by a literal hyphen.
    $namespace = ([guid] '11fb06fb-712d-4ddd-98c7-e71bbd588830').ToByteArray()
    [Array]::Reverse($namespace, 0, 4)
    [Array]::Reverse($namespace, 4, 2)
    [Array]::Reverse($namespace, 6, 2)
    $name = [Text.Encoding]::UTF8.GetBytes(($Values -join '-'))
    $hash = [Security.Cryptography.SHA1]::HashData([byte[]] ($namespace + $name))
    $bytes = [byte[]]::new(16)
    [Array]::Copy($hash, $bytes, 16)
    $bytes[6] = ($bytes[6] -band 0x0f) -bor 0x50
    $bytes[8] = ($bytes[8] -band 0x3f) -bor 0x80
    [Array]::Reverse($bytes, 0, 4)
    [Array]::Reverse($bytes, 4, 2)
    [Array]::Reverse($bytes, 6, 2)
    return ([guid]::new($bytes)).ToString('D')
}

function Assert-BootstrapEqual {
    param($Actual, $Expected)
    if ($Expected -is [System.Collections.IDictionary]) {
        Assert-BootstrapKeys -Value $Actual -Required @($Expected.Keys)
        foreach ($key in $Expected.Keys) { Assert-BootstrapEqual -Actual $Actual[$key] -Expected $Expected[$key] }
    } elseif ($Expected -is [System.Collections.IList]) {
        if ($Actual -isnot [System.Collections.IList] -or $Actual.Count -ne $Expected.Count) { throw 'Bootstrap contract array differs.' }
        for ($index = 0; $index -lt $Expected.Count; $index++) {
            Assert-BootstrapEqual -Actual $Actual[$index] -Expected $Expected[$index]
        }
    } elseif ($Expected -is [string]) {
        if ($Actual -isnot [string] -or $Actual -cne $Expected) { throw 'Bootstrap contract value differs.' }
    } elseif ($null -eq $Actual -or $Actual.GetType() -ne $Expected.GetType() -or $Actual -ne $Expected) {
        throw 'Bootstrap contract value differs.'
    }
}

function Assert-BootstrapExpression {
    param($Actual, [string[]] $Expected)
    # Normalize only whitespace OUTSIDE ARM string literals. Never weaken the ABAC condition.
    if ($Actual -isnot [string]) { throw 'Invalid compiled bootstrap expression.' }
    $normalized = foreach ($text in (@($Actual) + @($Expected))) {
        $builder = [Text.StringBuilder]::new()
        $quoted = $false
        for ($index = 0; $index -lt $text.Length; $index++) {
            $character = $text[$index]
            if ($character -eq "'") {
                $null = $builder.Append($character)
                if ($quoted -and $index + 1 -lt $text.Length -and $text[$index + 1] -eq "'") {
                    $null = $builder.Append($text[++$index])
                } else { $quoted = -not $quoted }
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
        $result = [ordered]@{}
        $keys = [string[]] @($Value.Keys)
        [Array]::Sort($keys, [StringComparer]::Ordinal)
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
    Assert-BootstrapEqual -Actual @(Get-SampleProjectRoleIds) -Expected $roles
    $condition = "((!(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read'})  AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/filter/action'}) AND  !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write'}) ) OR (@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringLikeIgnoreCase '*-azureml-agent'))"
    Assert-BootstrapEqual -Actual (Get-SampleBlobOwnerCondition) -Expected $condition
    foreach ($role in $roles) {
        $filter = if ($role -ceq $roles[2]) { $condition } else { '' }
        $roleId = "$scope/providers/Microsoft.Authorization/roleDefinitions/$role"
        $name = Get-SampleArmGuid -Values @($expectedIds.project.ToLowerInvariant(), $scope.ToLowerInvariant(), $roleId.ToLowerInvariant(), $filter)
        @{ kind = 'project'; roleAssignmentId = "$scope/providers/Microsoft.Authorization/roleAssignments/$name";
            roleDefinitionId = $roleId; scope = $scope; condition = $filter; conditionVersion = $(if ($filter) { '2.0' } else { '' }) }
    }
    $roleId = "$scope/providers/Microsoft.Authorization/roleDefinitions/$($roles[0])"
    $name = Get-SampleArmGuid -Values @($PipelinePrincipalId.ToLowerInvariant(), $scope.ToLowerInvariant(), $roleId.ToLowerInvariant(), '')
    @{ kind = 'pipeline'; roleAssignmentId = "$scope/providers/Microsoft.Authorization/roleAssignments/$name";
        roleDefinitionId = $roleId; scope = $scope; condition = ''; conditionVersion = '' }
}

function Assert-BootstrapTemplate {
    param($Compiled)
    # Type imports force symbolic ARM. Unknown compiler shapes fail closed for review.
    if ($Compiled -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $Compiled['languageVersion'] -Expected '2.0') -or
        $Compiled.Contains('functions') -or $Compiled.Contains('extensions')) { throw 'Unsupported compiled bootstrap schema.' }
    Assert-BootstrapKeys -Value $Compiled['parameters'] -Required @('identityResourceGroup', 'namePrefix', 'location', 'ownerToken', 'pipelinePrincipalId')
    foreach ($binding in @(@('identityResourceGroup', $identityGroup), @('namePrefix', 'mi-azsdk-sample'), @('location', 'westus3'))) {
        $parameter = $Compiled['parameters'][$binding[0]]
        Assert-BootstrapKeys -Value $parameter -Required @('type', 'allowedValues') -Optional @('metadata')
        Assert-BootstrapEqual -Actual $parameter['type'] -Expected 'string'
        Assert-BootstrapEqual -Actual $parameter['allowedValues'] -Expected @($binding[1])
    }
    foreach ($binding in @(@('ownerToken', 32), @('pipelinePrincipalId', 36))) {
        $parameter = $Compiled['parameters'][$binding[0]]
        Assert-BootstrapKeys -Value $parameter -Required @('type', 'minLength', 'maxLength') -Optional @('metadata')
        if (-not (Test-BootstrapText -Value $parameter['type'] -Expected 'string') -or
            ($parameter['minLength'] -isnot [int] -and $parameter['minLength'] -isnot [long]) -or
            ($parameter['maxLength'] -isnot [int] -and $parameter['maxLength'] -isnot [long]) -or $parameter['minLength'] -ne $binding[1] -or
            $parameter['maxLength'] -ne $binding[1]) { throw 'Compiled bootstrap parameter constraints differ.' }
    }
    $variables = $Compiled['variables']
    Assert-BootstrapKeys -Value $variables -Required @('locationSuffix', 'approvedRoleDefinitionIds', 'storageBlobOwnerCondition', 'projectServiceGrants', 'projectIdentityResourceId')
    Assert-BootstrapEqual -Actual $variables['locationSuffix'] -Expected 'wus3'
    Assert-BootstrapEqual -Actual $variables['storageBlobOwnerCondition'] -Expected $grants[2].condition
    $roleNames = @('foundryUser', 'storageBlobDataContributor', 'storageBlobDataOwner', 'cosmosDbOperator', 'searchServiceContributor', 'searchIndexDataContributor')
    Assert-BootstrapKeys -Value $variables['approvedRoleDefinitionIds'] -Required $roleNames
    if ($variables['projectServiceGrants'] -isnot [System.Collections.IList] -or $variables['projectServiceGrants'].Count -ne 6) {
        throw 'Compiled bootstrap must contain exactly six ordinary project service grants.'
    }
    for ($index = 0; $index -lt 6; $index++) {
        $role = $grants[$index].roleDefinitionId.Split('/')[-1]
        Assert-BootstrapExpression -Actual $variables['approvedRoleDefinitionIds'][$roleNames[$index]] -Expected "[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '$role')]"
        $grant = $variables['projectServiceGrants'][$index]
        Assert-BootstrapKeys -Value $grant -Required @('roleDefinitionId', 'condition')
        Assert-BootstrapExpression -Actual $grant['roleDefinitionId'] -Expected "[variables('approvedRoleDefinitionIds').$($roleNames[$index])]"
        Assert-BootstrapEqual -Actual $grant['condition'] -Expected $(if ($index -eq 2) { "[variables('storageBlobOwnerCondition')]" } else { '' })
    }
    Assert-BootstrapExpression -Actual $variables['projectIdentityResourceId'] -Expected "[resourceId(subscription().subscriptionId, parameters('identityResourceGroup'), 'Microsoft.ManagedIdentity/userAssignedIdentities', format('{0}-project-{1}', parameters('namePrefix'), variables('locationSuffix')))]"
    $resources = $Compiled['resources']
    Assert-BootstrapKeys -Value $resources -Required @('identityResources', 'sharedIdentities', 'projectRoleAssignments', 'pipelineFoundryUser')
    foreach ($resource in $resources.Values) {
        Assert-BootstrapKeys -Value $resource -Required @('type', 'apiVersion', 'name') -Optional @('location', 'tags', 'properties', 'copy', 'dependsOn', 'resourceGroup')
        foreach ($field in @('type', 'apiVersion', 'name')) {
            if ($resource[$field] -isnot [string]) { throw 'Invalid compiled bootstrap resource schema.' }
        }
    }
    $group = $resources['identityResources']
    if ($group['type'] -cne 'Microsoft.Resources/resourceGroups' -or $group['apiVersion'] -cne '2024-03-01' -or
        $group.Contains('copy') -or $group.Contains('properties') -or $group.Contains('resourceGroup')) { throw 'Unexpected compiled identity group resource.' }
    Assert-BootstrapExpression -Actual $group['name'] -Expected "[parameters('identityResourceGroup')]"
    Assert-BootstrapExpression -Actual $group['location'] -Expected "[parameters('location')]"
    Assert-BootstrapEqual -Actual $group['tags'] -Expected @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = "[parameters('ownerToken')]"; 'sample-ci-retention' = 'permanent' }
    $project = $resources['projectRoleAssignments']
    $pipeline = $resources['pipelineFoundryUser']
    foreach ($assignment in @($project, $pipeline)) {
        if ($assignment['type'] -cne 'Microsoft.Authorization/roleAssignments' -or $assignment['apiVersion'] -cne '2022-04-01' -or
            $assignment.Contains('resourceGroup') -or $assignment.Contains('location') -or $assignment.Contains('tags')) {
            throw 'Unexpected compiled role assignment scope or type.'
        }
    }
    Assert-BootstrapEqual -Actual $project['copy'] -Expected @{ name = 'projectRoleAssignments'; count = "[length(variables('projectServiceGrants'))]" }
    Assert-BootstrapExpression -Actual $project['name'] -Expected "[guid(toLower(variables('projectIdentityResourceId')), toLower(subscription().id), toLower(variables('projectServiceGrants')[copyIndex()].roleDefinitionId), variables('projectServiceGrants')[copyIndex()].condition)]"
    Assert-BootstrapEqual -Actual $project['properties'] -Expected @{
        principalId = "[reference('sharedIdentities').outputs.identities.value.project.principalId]"
        principalType = 'ServicePrincipal'
        roleDefinitionId = "[variables('projectServiceGrants')[copyIndex()].roleDefinitionId]"
        condition = "[if(empty(variables('projectServiceGrants')[copyIndex()].condition), null(), variables('projectServiceGrants')[copyIndex()].condition)]"
        conditionVersion = "[if(empty(variables('projectServiceGrants')[copyIndex()].condition), null(), '2.0')]"
    }
    if ($pipeline.Contains('copy')) { throw 'The pipeline may receive only one ordinary service grant.' }
    Assert-BootstrapExpression -Actual $pipeline['name'] -Expected "[guid(toLower(parameters('pipelinePrincipalId')), toLower(subscription().id), toLower(variables('approvedRoleDefinitionIds').foundryUser), '')]"
    Assert-BootstrapEqual -Actual $pipeline['properties'] -Expected @{ principalId = "[parameters('pipelinePrincipalId')]"; principalType = 'ServicePrincipal'; roleDefinitionId = "[variables('approvedRoleDefinitionIds').foundryUser]" }
    $module = $resources['sharedIdentities']
    if ($module['type'] -cne 'Microsoft.Resources/deployments' -or $module['apiVersion'] -cnotin @('2022-09-01', '2024-03-01', '2025-04-01') -or
        $module.Contains('copy') -or $module.Contains('location') -or $module.Contains('tags')) { throw 'Unexpected compiled identity module.' }
    Assert-BootstrapExpression -Actual $module['name'] -Expected "[format('shared-identities-{0}', uniqueString(subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('identityResourceGroup')), parameters('namePrefix'), variables('locationSuffix')))]"
    Assert-BootstrapExpression -Actual $module['resourceGroup'] -Expected "[parameters('identityResourceGroup')]"
    $properties = $module['properties']
    Assert-BootstrapKeys -Value $properties -Required @('expressionEvaluationOptions', 'mode', 'parameters', 'template')
    Assert-BootstrapEqual -Actual $properties['mode'] -Expected 'Incremental'
    Assert-BootstrapEqual -Actual $properties['expressionEvaluationOptions'] -Expected @{ scope = 'inner' }
    $parameters = @{}
    foreach ($name in @('namePrefix', 'location', 'ownerToken')) { $parameters[$name] = @{ value = "[parameters('$name')]" } }
    $parameters['locationSuffix'] = @{ value = "[variables('locationSuffix')]" }
    Assert-BootstrapEqual -Actual $properties['parameters'] -Expected $parameters
    $nested = $properties['template']
    if ($nested -isnot [System.Collections.IDictionary] -or $nested.Contains('functions') -or $nested.Contains('extensions')) { throw 'Unexpected nested identity template.' }
    Assert-BootstrapEqual -Actual $nested['variables'] -Expected @{ identityPurposes = @('project', 'account', 'search', 'function') }
    Assert-BootstrapKeys -Value $nested['parameters'] -Required @('namePrefix', 'location', 'locationSuffix', 'ownerToken')
    foreach ($name in @('namePrefix', 'location', 'locationSuffix', 'ownerToken')) {
        $expected = if ($name -ceq 'ownerToken') { @{ type = 'string'; minLength = 32; maxLength = 32 } }
            else { @{ type = 'string'; allowedValues = @(@{ namePrefix = 'mi-azsdk-sample'; location = 'westus3'; locationSuffix = 'wus3' }[$name]) } }
        $actual = @{} + $nested['parameters'][$name]
        $actual.Remove('metadata')
        # JSON numbers may be Int64; compare numeric constraints explicitly.
        if ($name -ceq 'ownerToken') {
            Assert-BootstrapKeys -Value $actual -Required @('type', 'minLength', 'maxLength')
            if (-not (Test-BootstrapText -Value $actual['type'] -Expected 'string') -or
                ($actual['minLength'] -isnot [int] -and $actual['minLength'] -isnot [long]) -or
                ($actual['maxLength'] -isnot [int] -and $actual['maxLength'] -isnot [long]) -or
                $actual['minLength'] -ne 32 -or $actual['maxLength'] -ne 32) { throw 'Unexpected identity owner constraint.' }
        } else { Assert-BootstrapEqual -Actual $actual -Expected $expected }
    }
    Assert-BootstrapKeys -Value $nested['resources'] -Required @('managedIdentities')
    $identity = $nested['resources']['managedIdentities']
    Assert-BootstrapKeys -Value $identity -Required @('type', 'apiVersion', 'name', 'location', 'tags', 'copy')
    if (-not (Test-BootstrapText -Value $identity['type'] -Expected 'Microsoft.ManagedIdentity/userAssignedIdentities') -or
        -not (Test-BootstrapText -Value $identity['apiVersion'] -Expected '2023-01-31')) { throw 'Unexpected compiled identity type.' }
    Assert-BootstrapEqual -Actual $identity['copy'] -Expected @{ name = 'managedIdentities'; count = "[length(variables('identityPurposes'))]" }
    Assert-BootstrapExpression -Actual $identity['name'] -Expected "[format('{0}-{1}-{2}', parameters('namePrefix'), variables('identityPurposes')[copyIndex()], parameters('locationSuffix'))]"
    Assert-BootstrapExpression -Actual $identity['location'] -Expected "[parameters('location')]"
    Assert-BootstrapEqual -Actual $identity['tags'] -Expected @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = "[parameters('ownerToken')]";
        'sample-ci-retention' = 'permanent'; 'sample-ci-identity' = "[variables('identityPurposes')[copyIndex()]]" }
    Assert-BootstrapKeys -Value $Compiled['outputs'] -Required @('identityResourceGroupId', 'identities', 'roleDefinitionIds', 'blobOwnerCondition', 'roleAssignments')
    Assert-BootstrapKeys -Value $nested['outputs'] -Required @('identities')
    foreach ($output in @($Compiled['outputs'].Values) + @($nested['outputs'].Values)) {
        Assert-BootstrapKeys -Value $output -Required @('value') -Optional @('type', '$ref', 'metadata')
    }
    Assert-BootstrapExpression -Actual $Compiled['outputs']['identityResourceGroupId']['value'] -Expected @(
        "[subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('identityResourceGroup'))]", "[resourceInfo('identityResources').id]")
    Assert-BootstrapExpression -Actual $Compiled['outputs']['identities']['value'] -Expected "[reference('sharedIdentities').outputs.identities.value]"
    Assert-BootstrapExpression -Actual $Compiled['outputs']['roleDefinitionIds']['value'] -Expected "[variables('approvedRoleDefinitionIds')]"
    Assert-BootstrapExpression -Actual $Compiled['outputs']['blobOwnerCondition']['value'] -Expected "[variables('storageBlobOwnerCondition')]"
    # This is also the principal source used by the six real assignments. Checking
    # only resource types would allow a changed module output to redirect the grants.
    $metadata = $nested['outputs']['identities']['value']
    $purposes = @('project', 'account', 'search', 'function')
    Assert-BootstrapKeys -Value $metadata -Required $purposes
    for ($index = 0; $index -lt 4; $index++) {
        $entry = $metadata[$purposes[$index]]
        Assert-BootstrapKeys -Value $entry -Required @('resourceId', 'principalId', 'clientId', 'tenantId')
        $resourceId = "resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', format('{0}-{1}-{2}', parameters('namePrefix'), variables('identityPurposes')[$index], parameters('locationSuffix')))"
        Assert-BootstrapExpression -Actual $entry['resourceId'] -Expected @(
            "[$resourceId]", "[resourceInfo('managedIdentities[$index]').id]", "[resourceInfo(format('managedIdentities[{0}]', $index)).id]")
        foreach ($field in @('principalId', 'clientId', 'tenantId')) {
            Assert-BootstrapExpression -Actual $entry[$field] -Expected @(
                "[reference('managedIdentities[$index]').$field]", "[reference(format('managedIdentities[{0}]', $index)).$field]",
                "[reference($resourceId, '2023-01-31').$field]")
        }
    }
    $outputGrants = $Compiled['outputs']['roleAssignments']['value']
    Assert-BootstrapKeys -Value $outputGrants -Required @('project', 'pipeline')
    Assert-BootstrapExpression -Actual $outputGrants['project'] -Expected "[map(variables('projectServiceGrants'), lambda('grant', createObject('roleAssignmentId', subscriptionResourceId('Microsoft.Authorization/roleAssignments', guid(toLower(variables('projectIdentityResourceId')), toLower(subscription().id), toLower(lambdaVariables('grant').roleDefinitionId), lambdaVariables('grant').condition)), 'principalId', reference('sharedIdentities').outputs.identities.value.project.principalId, 'roleDefinitionId', lambdaVariables('grant').roleDefinitionId, 'scope', subscription().id, 'condition', lambdaVariables('grant').condition, 'conditionVersion', if(empty(lambdaVariables('grant').condition), '', '2.0'))))]"
    $pipelineOutput = $outputGrants['pipeline']
    Assert-BootstrapKeys -Value $pipelineOutput -Required @('roleAssignmentId', 'principalId', 'roleDefinitionId', 'scope', 'condition', 'conditionVersion')
    Assert-BootstrapExpression -Actual $pipelineOutput['roleAssignmentId'] -Expected @(
        "[subscriptionResourceId('Microsoft.Authorization/roleAssignments', guid(toLower(parameters('pipelinePrincipalId')), toLower(subscription().id), toLower(variables('approvedRoleDefinitionIds').foundryUser), ''))]",
        "[resourceInfo('pipelineFoundryUser').id]")
    Assert-BootstrapExpression -Actual $pipelineOutput['principalId'] -Expected "[parameters('pipelinePrincipalId')]"
    Assert-BootstrapExpression -Actual $pipelineOutput['roleDefinitionId'] -Expected "[variables('approvedRoleDefinitionIds').foundryUser]"
    Assert-BootstrapExpression -Actual $pipelineOutput['scope'] -Expected "[subscription().id]"
    Assert-BootstrapEqual -Actual $pipelineOutput['condition'] -Expected ''
    Assert-BootstrapEqual -Actual $pipelineOutput['conditionVersion'] -Expected ''
}

function Assert-BootstrapState {
    param($State)
    Assert-BootstrapKeys -Value $State -Required @('schemaVersion', 'status', 'subscriptionId', 'tenantId', 'identityResourceGroup', 'ownerToken',
        'pipelinePrincipalId', 'pipelineClientId', 'expectedCallerPrincipalId', 'deploymentName', 'identityResourceIds', 'templateHash') -Optional @('outputs', 'identities')
    if (($State['schemaVersion'] -isnot [int] -and $State['schemaVersion'] -isnot [long]) -or $State['schemaVersion'] -ne 1 -or
        $State['status'] -isnot [string] -or $State['status'] -cnotin @('Previewed', 'Applying', 'Failed', 'Created', 'Verified') -or
        $State['ownerToken'] -isnot [string] -or $State['ownerToken'] -cnotmatch '^[a-f0-9]{32}$' -or
        $State['templateHash'] -isnot [string] -or $State['templateHash'] -cnotmatch '^[a-f0-9]{64}$') { throw 'Invalid bootstrap state schema or status.' }
    foreach ($binding in @(@('subscriptionId', $subscription), @('tenantId', $tenant), @('pipelinePrincipalId', $PipelinePrincipalId),
        @('pipelineClientId', $PipelineClientId), @('expectedCallerPrincipalId', $ExpectedCallerPrincipalId))) {
        Assert-BootstrapGuid -Value $State[$binding[0]]
        if ($State[$binding[0]] -ine $binding[1]) { throw 'Bootstrap state differs from the explicit approved target.' }
    }
    Assert-BootstrapEqual -Actual $State['identityResourceIds'] -Expected $expectedIds
    if (-not (Test-BootstrapText -Value $State['identityResourceGroup'] -Expected $identityGroup) -or
        -not (Test-BootstrapText -Value $State['deploymentName'] -Expected ('sample-ci-shared-identities-' + $State['ownerToken'].Substring(0, 12)))) {
        throw 'Bootstrap state has a foreign resource group or deployment name.'
    }
    if (($State['status'] -ceq 'Previewed' -and ($State.Contains('outputs') -or $State.Contains('identities'))) -or
        ($State['status'] -cin @('Created', 'Verified') -and $State['outputs'] -isnot [System.Collections.IDictionary]) -or
        ($State.Contains('identities') -and $State['status'] -cne 'Verified') -or
        ($State['status'] -ceq 'Verified' -and $State['identities'] -isnot [System.Collections.IDictionary])) { throw 'Bootstrap state metadata does not match its status.' }
}

function Save-BootstrapState {
    param([System.Collections.IDictionary] $State)
    Assert-BootstrapState -State $State
    $directory = Split-Path -Parent $StatePath
    $null = [IO.Directory]::CreateDirectory($directory)
    $temporary = Join-Path $directory ([guid]::NewGuid().ToString('N') + '.tmp')
    $lock = $null
    try {
        # Serialize compare-and-save, including concurrent previews. Never downgrade an
        # attempt back to Previewed, or let two callers advance Previewed to Applying.
        try { $lock = [IO.File]::Open($StatePath + '.lock', [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None) }
        catch { throw 'Bootstrap state is in use; no replay is permitted.' }
        if ([IO.File]::Exists($StatePath)) {
            try { $current = [IO.File]::ReadAllText($StatePath) | ConvertFrom-Json -AsHashtable -ErrorAction Stop }
            catch { throw 'Cannot reconcile the current bootstrap state; no overwrite is permitted.' }
            Assert-BootstrapState -State $current
            foreach ($key in @('ownerToken', 'deploymentName', 'templateHash')) {
                Assert-BootstrapEqual -Actual $current[$key] -Expected $State[$key]
            }
            $allowedPrevious = switch ($State['status']) {
                'Previewed' { @('Previewed') }
                'Applying' { @('Previewed') }
                'Created' { @('Applying') }
                'Failed' { @('Applying') }
                'Verified' { @('Applying', 'Failed', 'Created', 'Verified') }
            }
            if ($current['status'] -cnotin $allowedPrevious) { throw 'A bootstrap attempt is already recorded; no replay or state downgrade is permitted.' }
        } elseif ($State['status'] -cne 'Previewed') { throw 'The recorded bootstrap state disappeared; no replay is permitted.' }
        [IO.File]::WriteAllText($temporary, ($State | ConvertTo-Json -Depth 40), [Text.UTF8Encoding]::new($false))
        [IO.File]::Move($temporary, $StatePath, $true)
    } finally {
        if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }
        if ($null -ne $lock) { $lock.Dispose() }
    }
}

function Get-BootstrapGroupExists {
    $exists = Invoke-BootstrapAzure -Arguments @('group', 'exists', '--name', $identityGroup, '--subscription', $subscription) -Sensitive
    if ($exists -isnot [bool]) { throw 'The group-exists response must be an actual JSON boolean.' }
    return $exists
}

function Get-BootstrapAssignmentSignature {
    param($Assignment)
    if ($Assignment -isnot [System.Collections.IDictionary] -or $Assignment['id'] -isnot [string] -or
        $Assignment['id'] -notmatch '^/(?:.+/)?providers/Microsoft\.Authorization/roleAssignments/[a-fA-F0-9-]{36}$' -or
        $Assignment['properties'] -isnot [System.Collections.IDictionary]) { throw 'Invalid role-assignment response schema.' }
    Assert-BootstrapGuid -Value ($Assignment['id'].Split('/')[-1])
    $properties = $Assignment['properties']
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
    # First list without a filter to include RG/resource descendants. Also retain the
    # existing atScope query for ancestors, without changing the worker-owned helper.
    $path = '/subscriptions/' + $SubscriptionId + '/providers/Microsoft.Authorization/roleAssignments'
    $all = [Collections.Generic.List[object]]::new()
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
                $pair = $part.Split('=', 2)
                $key = [uri]::UnescapeDataString($pair[0])
                if ($pair.Count -ne 2 -or $key -notin @('api-version', '$filter', '$skiptoken', 'skiptoken') -or $query.ContainsKey($key)) { throw 'Unexpected authorization pagination query.' }
                $query[$key] = [uri]::UnescapeDataString($pair[1])
            }
            if ($query['api-version'] -cne '2022-04-01' -or $query.ContainsKey('$filter') -ne $atScope -or
                ($atScope -and $query['$filter'] -cne 'atScope()')) { throw 'Authorization pagination changed the requested scope.' }
            $page = Invoke-BootstrapAzure -Arguments @('rest', '--method', 'get', '--subscription', $SubscriptionId, '--url', $uri) -Sensitive
            if ($page -isnot [System.Collections.IDictionary] -or $page['value'] -isnot [System.Collections.IList] -or
                ($page.Contains('error') -and $null -ne $page['error']) -or
                ($null -ne $page['nextLink'] -and $page['nextLink'] -isnot [string])) { throw 'Invalid authorization list response.' }
            foreach ($assignment in $page['value']) { $all.Add($assignment) }
            $uri = $page['nextLink']
        } while ($uri)
    }
    $byId = @{}
    foreach ($assignment in $all) {
        $signature = Get-BootstrapAssignmentSignature -Assignment $assignment
        $id = $assignment['id'].ToLowerInvariant()
        if ($byId.ContainsKey($id)) {
            Assert-BootstrapEqual -Actual (Get-BootstrapAssignmentSignature -Assignment $byId[$id]) -Expected $signature
        } else { $byId[$id] = $assignment }
    }
    return @($byId.Values)
}

function Assert-BootstrapGrant {
    param($Assignment, $Grant, [string] $PrincipalId)
    $null = Get-BootstrapAssignmentSignature -Assignment $Assignment
    $properties = $Assignment['properties']
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
    $grant = $grants[6]
    $matchingAssignments = @($Assignments | Where-Object { $_['id'] -ieq $grant.roleAssignmentId -or
        ($_.properties.principalId -ieq $PipelinePrincipalId -and $_.properties.scope -ieq $scope -and $_.properties.roleDefinitionId -ieq $grant.roleDefinitionId) })
    if ($matchingAssignments.Count -gt 1) { throw 'Duplicate pipeline Foundry User grants; no existing assignment will be changed.' }
    if ($matchingAssignments.Count -eq 1) { Assert-BootstrapGrant -Assignment $matchingAssignments[0] -Grant $grant -PrincipalId $PipelinePrincipalId; return $true }
    return $false
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
    $identities = $Outputs['identities']['value']
    Assert-BootstrapKeys -Value $identities -Required @('project', 'account', 'search', 'function')
    $principalIds = @($PipelinePrincipalId, $ExpectedCallerPrincipalId)
    $clientIds = @($PipelineClientId)
    foreach ($purpose in @('project', 'account', 'search', 'function')) {
        $metadata = $identities[$purpose]
        Assert-BootstrapKeys -Value $metadata -Required @('resourceId', 'principalId', 'clientId', 'tenantId')
        foreach ($field in @('principalId', 'clientId', 'tenantId')) { Assert-BootstrapGuid -Value $metadata[$field] }
        if (-not (Test-BootstrapText -Value $metadata['resourceId'] -Expected $expectedIds[$purpose] -IgnoreCase) -or $metadata['tenantId'] -ine $tenant -or
            $metadata['principalId'] -iin $principalIds -or $metadata['clientId'] -iin $clientIds) { throw 'Invalid or duplicate immutable identity metadata.' }
        $principalIds += $metadata['principalId']; $clientIds += $metadata['clientId']
    }
    $roleNames = @('foundryUser', 'storageBlobDataContributor', 'storageBlobDataOwner', 'cosmosDbOperator', 'searchServiceContributor', 'searchIndexDataContributor')
    $definitions = @{}
    for ($index = 0; $index -lt 6; $index++) { $definitions[$roleNames[$index]] = $grants[$index].roleDefinitionId }
    Assert-BootstrapEqual -Actual $Outputs['roleDefinitionIds']['value'] -Expected $definitions
    $assignments = $Outputs['roleAssignments']['value']
    Assert-BootstrapKeys -Value $assignments -Required @('project', 'pipeline')
    if ($assignments['project'] -isnot [System.Collections.IList] -or $assignments['project'].Count -ne 6) { throw 'Deployment outputs must record exactly seven grants.' }
    for ($index = 0; $index -lt 7; $index++) {
        $grant = $grants[$index]
        $expected = @{} + $grant
        $expected.Remove('kind')
        $expected['principalId'] = if ($index -eq 6) { $PipelinePrincipalId } else { $identities.project.principalId }
        $actual = if ($index -eq 6) { $assignments['pipeline'] } else { $assignments['project'][$index] }
        Assert-BootstrapEqual -Actual $actual -Expected $expected
    }
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
            if ($envelope.Contains($field) -and -not (Test-BootstrapText -Value $envelope[$field] -Expected 'Succeeded')) {
                throw 'ARM validation contains an unsuccessful or malformed status.'
            }
        }
    }
    if ($properties -is [System.Collections.IDictionary] -and $properties.Contains('provisioningState')) {
        if (-not (Test-BootstrapText -Value $properties['provisioningState'] -Expected 'Succeeded')) { throw 'ARM validation provisioning state is not Succeeded.' }
        return
    }
    # DeploymentValidateResult can omit provisioningState, but success then requires EXPLICIT error:null.
    if (-not $Validation.Contains('error') -or $null -ne $Validation['error']) { throw 'ARM validation has no explicit success evidence.' }
}

function Assert-BootstrapPrediction {
    param($Prediction, $Validation, [bool] $PipelineGrantExists)
    if ($Prediction -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $Prediction['status'] -Expected 'Succeeded') -or
        $Prediction['changes'] -isnot [System.Collections.IList] -or ($Prediction.Contains('error') -and $null -ne $Prediction['error'])) {
        throw 'What-if must return a successful JSON object with a changes array.'
    }
    $allowed = @{}
    $allowed[$identityGroupId.ToLowerInvariant()] = 'Microsoft.Resources/resourceGroups'
    foreach ($id in $expectedIds.Values) { $allowed[$id.ToLowerInvariant()] = 'Microsoft.ManagedIdentity/userAssignedIdentities' }
    foreach ($grant in $grants) { $allowed[$grant.roleAssignmentId.ToLowerInvariant()] = 'Microsoft.Authorization/roleAssignments' }
    # Some ARM versions expose the module as well. Only its evaluated ID from validation
    # of the pinned, schema-checked template is eligible; never whitelist a name wildcard.
    $moduleId = $null
    if ($Validation['properties'] -is [System.Collections.IDictionary] -and $null -ne $Validation['properties']['validatedResources']) {
        if ($Validation['properties']['validatedResources'] -isnot [System.Collections.IList]) { throw 'Invalid validated-resource schema.' }
        foreach ($resource in $Validation['properties']['validatedResources']) {
            if ($resource -isnot [System.Collections.IDictionary]) { throw 'Invalid validated resource.' }
            if (Test-BootstrapText -Value $resource['type'] -Expected 'Microsoft.Resources/deployments' -IgnoreCase) {
                $prefix = $identityGroupId + '/providers/Microsoft.Resources/deployments/'
                if ($moduleId -or $resource['id'] -isnot [string] -or -not $resource['id'].StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) -or
                    $resource['id'].Substring($prefix.Length) -cnotmatch '^shared-identities-[a-z2-7]{13}$') { throw 'Unexpected validated module deployment.' }
                $moduleId = $resource['id']
                $allowed[$moduleId.ToLowerInvariant()] = 'Microsoft.Resources/deployments'
            }
        }
    }
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($change in $Prediction['changes']) {
        if ($change -isnot [System.Collections.IDictionary] -or $change['resourceId'] -isnot [string] -or
            -not $allowed.ContainsKey($change['resourceId'].ToLowerInvariant()) -or -not $seen.Add($change['resourceId']) -or
            $change['after'] -isnot [System.Collections.IDictionary] -or $change['changeType'] -isnot [string]) { throw 'What-if contains an unknown or duplicate resource ID.' }
        $id = $change['resourceId']
        $after = $change['after']
        $type = $allowed[$id.ToLowerInvariant()]
        if (-not (Test-BootstrapText -Value $after['type'] -Expected $type -IgnoreCase) -or
            ($after.Contains('id') -and -not (Test-BootstrapText -Value $after['id'] -Expected $id -IgnoreCase)) -or
            ($after.Contains('name') -and -not (Test-BootstrapText -Value $after['name'] -Expected $id.Split('/')[-1] -IgnoreCase))) { throw 'What-if resource type or payload ID differs.' }
        $matching = @($grants | Where-Object { $_.roleAssignmentId -ieq $id })
        if ($matching.Count -eq 1) {
            $grant = $matching[0]
            if ($grant.kind -ceq 'pipeline') {
                $expectedChange = if ($PipelineGrantExists) { 'NoChange' } else { 'Create' }
                if ($change['changeType'] -cne $expectedChange) { throw 'What-if would change an existing or unverified pipeline grant.' }
                $properties = $after['properties']
                if ($properties -isnot [System.Collections.IDictionary]) { throw 'What-if pipeline grant has no exact properties.' }
                $assignment = @{ id = $id; properties = @{} + $properties }
                if (-not $assignment.properties.Contains('scope')) { $assignment.properties['scope'] = $scope }
                # What-if can omit this metadata; the compiled template already fixes it.
                # Never default an explicit null/wrong value or an actual assignment GET.
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
    foreach ($id in @($identityGroupId) + @($expectedIds.Values) + @($grants.roleAssignmentId)) {
        if (-not $seen.Contains($id)) { throw 'What-if omitted an approved resource or grant.' }
    }
}

# This entry point never logs in, switches identity, repairs grants, or deploys workloads.
if ($Apply -and $VerifyOnly) { throw '-Apply and -VerifyOnly are mutually exclusive.' }
$StatePath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($StatePath)
$subscription = Get-SampleSubscriptionId
$tenant = Get-SampleTenantId
foreach ($guid in @($subscription, $tenant, $PipelinePrincipalId, $PipelineClientId, $ExpectedCallerPrincipalId)) { Assert-BootstrapGuid -Value $guid }
$PipelinePrincipalId = $PipelinePrincipalId.ToLowerInvariant()
$PipelineClientId = $PipelineClientId.ToLowerInvariant()
$ExpectedCallerPrincipalId = $ExpectedCallerPrincipalId.ToLowerInvariant()
$scope = '/subscriptions/' + $subscription
$identityGroup = 'rg-azsdk-sample-identities-wus3'
$identityGroupId = "$scope/resourceGroups/$identityGroup"
$expectedIds = Get-SampleSharedIdentityIds -SubscriptionId $subscription
$grants = @(Get-BootstrapGrantPlan)
$previous = $null
if (Test-Path -LiteralPath $StatePath) {
    try { $previous = Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json -AsHashtable -ErrorAction Stop }
    catch { throw 'Cannot parse bootstrap state; no request or write attempted.' }
    Assert-BootstrapState -State $previous
    # An absent RG is NOT permission to replay a failed/ambiguous deployment.
    if (-not $VerifyOnly -and $previous['status'] -cne 'Previewed') { throw 'A bootstrap attempt is already recorded. Use -VerifyOnly; never reapply, even if the RG is absent.' }
}
if ($VerifyOnly -and ($null -eq $previous -or $previous['status'] -ceq 'Previewed')) { throw 'Verification requires a recorded bootstrap attempt.' }
if ($Apply -and $null -eq $previous) { throw 'Save and review a separate dry run before using -Apply.' }
$tokenResponse = $null; $privateToken = $null; $claims = $null; $payload = $null; $compiledPath = $null; $bootstrapArmHeaders = $null
try {
    $account = Invoke-BootstrapAzure -Arguments @('account', 'show', '--subscription', $subscription) -Sensitive
    if ($account -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $account['id'] -Expected $subscription -IgnoreCase) -or
        -not (Test-BootstrapText -Value $account['tenantId'] -Expected $tenant -IgnoreCase) -or -not (Test-BootstrapText -Value $account['state'] -Expected 'Enabled') -or
        $account['user'] -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $account['user']['type'] -Expected 'user')) {
        throw 'Use the approved current administrator user in the explicit target tenant/subscription.'
    }
    $tokenResponse = Invoke-BootstrapAzure -Arguments @('account', 'get-access-token', '--subscription', $subscription, '--resource', 'https://management.azure.com/') -Sensitive
    try {
        $privateToken = $tokenResponse['accessToken']
        if ($privateToken -isnot [string] -or $privateToken.Split('.').Count -ne 3) { throw 'Invalid token.' }
        $payload = $privateToken.Split('.')[1].Replace('-', '+').Replace('_', '/')
        $payload = $payload.PadRight($payload.Length + ((4 - $payload.Length % 4) % 4), '=')
        $claims = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($payload)) | ConvertFrom-Json -AsHashtable -ErrorAction Stop
        if ($claims -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $claims['tid'] -Expected $tenant -IgnoreCase) -or
            -not (Test-BootstrapText -Value $claims['oid'] -Expected $ExpectedCallerPrincipalId -IgnoreCase) -or
            $claims['scp'] -isnot [string] -or [string]::IsNullOrWhiteSpace($claims['scp'])) { throw 'Unexpected caller.' }
        $bootstrapArmHeaders = @{ Authorization = 'Bearer ' + $privateToken }
    } catch { throw 'Cannot verify the approved bootstrap caller; token suppressed.' }
    finally { $privateToken = $null; $tokenResponse = $null; $claims = $null; $payload = $null }
    $application = Invoke-BootstrapAzure -Arguments @('ad', 'sp', 'show', '--id', $PipelinePrincipalId,
        '--query', '{id:id,appId:appId,accountEnabled:accountEnabled}') -Sensitive
    if ($application -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $application['id'] -Expected $PipelinePrincipalId -IgnoreCase) -or
        -not (Test-BootstrapText -Value $application['appId'] -Expected $PipelineClientId -IgnoreCase) -or
        $application['accountEnabled'] -isnot [bool] -or -not $application['accountEnabled']) { throw 'Cannot verify the approved pipeline service principal.' }
    $exists = Get-BootstrapGroupExists
    if ($exists -and -not $VerifyOnly) { throw 'The identity RG already exists; refusing to adopt, retag, or replay it.' }
    if ($VerifyOnly) {
        if (-not $exists) { throw 'The recorded bootstrap identity RG does not exist; reapply remains forbidden.' }
        $group = Invoke-BootstrapAzure -Arguments @('group', 'show', '--name', $identityGroup, '--subscription', $subscription) -Sensitive
        if ($group -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $group['id'] -Expected $identityGroupId -IgnoreCase) -or
            -not (Test-BootstrapText -Value $group['location'] -Expected 'westus3') -or $group['tags'] -isnot [System.Collections.IDictionary] -or
            -not (Test-BootstrapText -Value $group['tags']['purpose'] -Expected 'azsdk-sample-identities') -or
            -not (Test-BootstrapText -Value $group['tags']['sample-ci-owner'] -Expected $previous.ownerToken) -or
            -not (Test-BootstrapText -Value $group['tags']['sample-ci-retention'] -Expected 'permanent')) { throw 'The identity RG does not match exact bootstrap ownership.' }
        $outputs = $previous['outputs']
        if (-not $previous.Contains('outputs')) {
            # Applying/Failed may mean the CLI lost its response. Reconcile this ONE recorded deployment by GET, never another create.
            $deploymentId = "$scope/providers/Microsoft.Resources/deployments/$($previous.deploymentName)"
            $recorded = Invoke-BootstrapAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url',
                ('https://management.azure.com{0}?api-version=2022-09-01' -f $deploymentId)) -Sensitive
            if ($recorded -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $recorded['id'] -Expected $deploymentId -IgnoreCase) -or
                -not (Test-BootstrapText -Value $recorded['name'] -Expected $previous.deploymentName) -or
                -not (Test-BootstrapText -Value $recorded['type'] -Expected 'Microsoft.Resources/deployments' -IgnoreCase) -or
                $recorded['properties'] -isnot [System.Collections.IDictionary] -or
                -not (Test-BootstrapText -Value $recorded['properties']['provisioningState'] -Expected 'Succeeded') -or
                ($recorded['properties'].Contains('error') -and $null -ne $recorded['properties']['error'])) { throw 'The recorded deployment has no successful immutable output baseline; no retry is permitted.' }
            $parameters = @{ identityResourceGroup = @{ value = $identityGroup }; namePrefix = @{ value = 'mi-azsdk-sample' };
                location = @{ value = 'westus3' }; ownerToken = @{ value = $previous.ownerToken }; pipelinePrincipalId = @{ value = $PipelinePrincipalId } }
            Assert-BootstrapEqual -Actual $recorded['properties']['parameters'] -Expected $parameters
            $outputs = $recorded['properties']['outputs']
        }
        $identities = Assert-BootstrapOutputs -Outputs $outputs
        if ($previous.Contains('identities')) { Assert-BootstrapEqual -Actual $previous['identities'] -Expected $identities }
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $identity = Invoke-BootstrapAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url',
                ('https://management.azure.com{0}?api-version=2023-01-31' -f $expectedIds[$purpose])) -Sensitive
            if ($identity -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $identity['id'] -Expected $expectedIds[$purpose] -IgnoreCase) -or
                -not (Test-BootstrapText -Value $identity['type'] -Expected 'Microsoft.ManagedIdentity/userAssignedIdentities' -IgnoreCase) -or
                -not (Test-BootstrapText -Value $identity['location'] -Expected 'westus3') -or
                $identity['properties'] -isnot [System.Collections.IDictionary] -or $identity['tags'] -isnot [System.Collections.IDictionary] -or
                -not (Test-BootstrapText -Value $identity['tags']['purpose'] -Expected 'azsdk-sample-identities') -or
                -not (Test-BootstrapText -Value $identity['tags']['sample-ci-owner'] -Expected $previous.ownerToken) -or
                -not (Test-BootstrapText -Value $identity['tags']['sample-ci-retention'] -Expected 'permanent') -or
                -not (Test-BootstrapText -Value $identity['tags']['sample-ci-identity'] -Expected $purpose)) { throw 'An identity does not match exact bootstrap ownership.' }
            foreach ($field in @('principalId', 'clientId', 'tenantId')) {
                Assert-BootstrapGuid -Value $identity['properties'][$field]
                if ($identity['properties'][$field] -ine $identities[$purpose][$field]) { throw 'An immutable identity binding changed; refusing a replacement identity.' }
            }
        }
        $assignments = @(Get-BootstrapAllAssignments -SubscriptionId $subscription)
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $owned = @($assignments | Where-Object { $_.properties.principalId -ieq $identities[$purpose].principalId })
            $expectedCount = if ($purpose -ceq 'project') { 6 } else { 0 }
            if ($owned.Count -ne $expectedCount) { throw 'The exact identity grant set differs: project must have six assignments; reserved identities must have zero, including descendants and inherited grants.' }
            if ($purpose -ceq 'project') {
                foreach ($grant in $grants[0..5]) {
                    $matching = @($owned | Where-Object { $_.id -ieq $grant.roleAssignmentId })
                    if ($matching.Count -ne 1) { throw 'An approved project assignment ID is missing or duplicated.' }
                    Assert-BootstrapGrant -Assignment $matching[0] -Grant $grant -PrincipalId $identities.project.principalId
                }
            }
        }
        $pipeline = @($assignments | Where-Object { $_.id -ieq $grants[6].roleAssignmentId -or
            ($_.properties.principalId -ieq $PipelinePrincipalId -and $_.properties.scope -ieq $scope -and $_.properties.roleDefinitionId -ieq $grants[6].roleDefinitionId) })
        if ($pipeline.Count -ne 1) { throw 'The exact approved pipeline Foundry User grant is missing or duplicated.' }
        Assert-BootstrapGrant -Assignment $pipeline[0] -Grant $grants[6] -PrincipalId $PipelinePrincipalId
        # Preserve the deployment's original immutable metadata, rather than adopting live IDs.
        $previous['outputs'] = $outputs; $previous['identities'] = $identities; $previous['status'] = 'Verified'
        Save-BootstrapState -State $previous
        [pscustomobject]@{ status = 'Verified'; subscriptionId = $subscription; tenantId = $tenant; identities = $identities;
            projectServiceGrants = 6; pipelineFoundryUserGrant = $true; iamAdministrationGranted = $false } | ConvertTo-Json -Depth 8
        return
    }
    $provider = Invoke-BootstrapAzure -Arguments @('provider', 'show', '--subscription', $subscription, '--namespace', 'Microsoft.ManagedIdentity', '--query', '{registrationState:registrationState}') -Sensitive
    if ($provider -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $provider['registrationState'] -Expected 'Registered')) { throw 'Microsoft.ManagedIdentity must already be registered.' }
    $template = Join-Path $PSScriptRoot '../infra/bootstrap-identities.bicep'
    $compiled = Invoke-BootstrapAzure -Arguments @('bicep', 'build', '--file', $template, '--stdout') -Sensitive
    Assert-BootstrapTemplate -Compiled $compiled
    # Stable on PowerShell 7.2 too, where ConvertFrom-Json returns unordered hashtables.
    $compiledText = ConvertTo-BootstrapCanonicalValue -Value $compiled | ConvertTo-Json -Depth 100 -Compress
    $templateHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($compiledText))).ToLowerInvariant()
    if ($previous -and $previous['templateHash'] -cne $templateHash) { throw 'The compiled template changed after preview; a new reviewed dry run is required.' }
    # Validate, preview, and create the SAME bytes, not three independently recompiled Bicep inputs.
    $compiledPath = [IO.Path]::GetTempFileName()
    [IO.File]::WriteAllText($compiledPath, $compiledText, [Text.UTF8Encoding]::new($false))
    $assignments = @(Get-BootstrapAllAssignments -SubscriptionId $subscription)
    $pipelineGrantExists = Get-BootstrapExistingPipelineGrant -Assignments $assignments
    $ownerToken = if ($previous) { $previous.ownerToken } else { [guid]::NewGuid().ToString('N') }
    $deploymentName = 'sample-ci-shared-identities-' + $ownerToken.Substring(0, 12)
    $arguments = @('--name', $deploymentName, '--location', 'westus3', '--subscription', $subscription, '--template-file', $compiledPath,
        '--parameters', "identityResourceGroup=$identityGroup", 'namePrefix=mi-azsdk-sample', 'location=westus3', "ownerToken=$ownerToken", "pipelinePrincipalId=$PipelinePrincipalId")
    $validation = Invoke-BootstrapAzure -Arguments (@('deployment', 'sub', 'validate') + $arguments) -Sensitive
    Assert-BootstrapValidation -Validation $validation
    $prediction = Invoke-BootstrapAzure -Arguments (@('deployment', 'sub', 'what-if') + $arguments + @('--no-pretty-print', '--result-format', 'FullResourcePayloads')) -Sensitive
    Assert-BootstrapPrediction -Prediction $prediction -Validation $validation -PipelineGrantExists $pipelineGrantExists
    $state = @{ schemaVersion = 1; status = 'Previewed'; subscriptionId = $subscription; tenantId = $tenant; identityResourceGroup = $identityGroup;
        ownerToken = $ownerToken; pipelinePrincipalId = $PipelinePrincipalId; pipelineClientId = $PipelineClientId; expectedCallerPrincipalId = $ExpectedCallerPrincipalId;
        deploymentName = $deploymentName; identityResourceIds = $expectedIds; templateHash = $templateHash }
    Save-BootstrapState -State $state
    [pscustomobject]@{ mode = 'DRY RUN'; subscriptionId = $subscription; tenantId = $tenant; identityResourceGroup = $identityGroup; identities = $expectedIds;
        changes = @($prediction['changes'] | ForEach-Object { @{ resourceId = $_.resourceId; type = $_['after']['type']; changeType = $_.changeType } });
        note = 'Only the new RG, four UAMIs, and seven approved service grants; existing pipeline grant must be exact NoChange. No IAM administration, deletes, or workloads.' } | ConvertTo-Json -Depth 8
    if (-not $Apply -or -not $PSCmdlet.ShouldProcess($scope, 'Create four permanent UAMIs and only the seven approved service-role grants')) { return }
    if (Get-BootstrapGroupExists) { throw 'The identity RG appeared after preview; no create attempted.' }
    $latestPipelineGrant = Get-BootstrapExistingPipelineGrant -Assignments @(Get-BootstrapAllAssignments -SubscriptionId $subscription)
    if ($latestPipelineGrant -ne $pipelineGrantExists) { throw 'The pipeline grant changed after preview; no create attempted.' }
    $state['status'] = 'Applying'
    Save-BootstrapState -State $state
    try {
        $created = Invoke-BootstrapAzure -Arguments (@('deployment', 'sub', 'create') + $arguments) -Sensitive
        if ($created -isnot [System.Collections.IDictionary] -or $created['properties'] -isnot [System.Collections.IDictionary] -or
            -not (Test-BootstrapText -Value $created['properties']['provisioningState'] -Expected 'Succeeded') -or
            ($created['properties'].Contains('error') -and $null -ne $created['properties']['error'])) { throw 'Bootstrap deployment did not succeed; reconcile the recorded attempt.' }
        $null = Assert-BootstrapOutputs -Outputs $created['properties']['outputs']
        $state['outputs'] = $created['properties']['outputs']; $state['status'] = 'Created'
    } catch { $state['status'] = 'Failed'; throw }
    finally { Save-BootstrapState -State $state }
    Write-Host 'Bootstrap deployment completed. Use -VerifyOnly; no reapply or automatic deletion is permitted.'
} finally {
    $bootstrapArmHeaders = $null
    $privateToken = $null; $tokenResponse = $null; $claims = $null; $payload = $null
    if ($compiledPath -and [IO.File]::Exists($compiledPath)) { [IO.File]::Delete($compiledPath) }
}