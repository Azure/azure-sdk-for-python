# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

function Assert-BootstrapStringParameter {
    param($Value, [int] $Minimum, [int] $Maximum)
    Assert-BootstrapKeys -Value $Value -Required @('type', 'minLength', 'maxLength') -Optional @('metadata')
    if (-not (Test-BootstrapText -Value $Value['type'] -Expected 'string') -or
        ($Value['minLength'] -isnot [int] -and $Value['minLength'] -isnot [long]) -or
        ($Value['maxLength'] -isnot [int] -and $Value['maxLength'] -isnot [long]) -or
        $Value['minLength'] -ne $Minimum -or $Value['maxLength'] -ne $Maximum) { throw 'Compiled bootstrap parameter constraints differ.' }
}

function Assert-BootstrapTemplate {
    param($Compiled)
    # Exact symbolic graph, literals and output/principal expressions from the
    # original guard. Generic inputs change constraints, never the resource allowlist.
    if ($Compiled -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $Compiled['languageVersion'] -Expected '2.0') -or
        $Compiled.Contains('functions') -or $Compiled.Contains('extensions')) { throw 'Unsupported compiled bootstrap schema.' }
    Assert-BootstrapKeys -Value $Compiled -Required @('languageVersion', 'parameters', 'variables', 'resources', 'outputs') -Optional @('$schema', 'contentVersion', 'metadata', 'definitions')
    Assert-BootstrapKeys -Value $Compiled['parameters'] -Required @('identityResourceGroup', 'namePrefix', 'location', 'ownerToken', 'pipelinePrincipalId', 'pipelineRoleAssignmentId', 'createPipelineGrant')
    foreach ($binding in @(@('identityResourceGroup', 1, 90), @('namePrefix', 1, 33), @('location', 1, 30), @('ownerToken', 32, 32))) {
        Assert-BootstrapStringParameter -Value $Compiled['parameters'][$binding[0]] -Minimum $binding[1] -Maximum $binding[2]
    }
    foreach ($name in @('pipelinePrincipalId', 'pipelineRoleAssignmentId', 'createPipelineGrant')) {
        Assert-BootstrapEqual -Actual $Compiled['parameters'][$name] -Expected @{ type = $(if ($name -ceq 'createPipelineGrant') { 'bool' } else { 'string' }) }
    }
    $variables = $Compiled['variables']
    Assert-BootstrapKeys -Value $variables -Required @('locationSuffix', 'approvedRoleDefinitionIds', 'storageBlobOwnerCondition', 'projectServiceGrants', 'projectIdentityResourceId')
    Assert-BootstrapExpression -Actual $variables['locationSuffix'] -Expected "[parameters('location')]"
    Assert-BootstrapEqual -Actual $variables['storageBlobOwnerCondition'] -Expected $grants[2].condition
    $roleNames = @('foundryUser', 'storageBlobDataContributor', 'storageBlobDataOwner', 'cosmosDbOperator', 'searchServiceContributor', 'searchIndexDataContributor')
    Assert-BootstrapKeys -Value $variables['approvedRoleDefinitionIds'] -Required $roleNames
    if ($variables['projectServiceGrants'] -isnot [System.Collections.IList] -or $variables['projectServiceGrants'].Count -ne 6) { throw 'Compiled bootstrap must contain exactly six ordinary project service grants.' }
    for ($index = 0; $index -lt 6; $index++) {
        $role = $grants[$index].roleDefinitionId.Split('/')[-1]
        Assert-BootstrapExpression -Actual $variables['approvedRoleDefinitionIds'][$roleNames[$index]] -Expected "[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '$role')]"
        $grant = $variables['projectServiceGrants'][$index]; Assert-BootstrapKeys -Value $grant -Required @('roleDefinitionId', 'condition')
        Assert-BootstrapExpression -Actual $grant['roleDefinitionId'] -Expected "[variables('approvedRoleDefinitionIds').$($roleNames[$index])]"
        Assert-BootstrapEqual -Actual $grant['condition'] -Expected $(if ($index -eq 2) { "[variables('storageBlobOwnerCondition')]" } else { '' })
    }
    Assert-BootstrapExpression -Actual $variables['projectIdentityResourceId'] -Expected "[resourceId(subscription().subscriptionId, parameters('identityResourceGroup'), 'Microsoft.ManagedIdentity/userAssignedIdentities', format('{0}-project-{1}', parameters('namePrefix'), variables('locationSuffix')))]"
    $resources = $Compiled['resources']
    Assert-BootstrapKeys -Value $resources -Required @('identityResources', 'sharedIdentities', 'projectRoleAssignments', 'pipelineFoundryUser')
    foreach ($name in $resources.Keys) {
        $resource = $resources[$name]
        $optional = @('location', 'tags', 'properties', 'copy', 'dependsOn', 'resourceGroup')
        if ($name -ceq 'pipelineFoundryUser') { $optional += 'condition' }
        Assert-BootstrapKeys -Value $resource -Required @('type', 'apiVersion', 'name') -Optional $optional
        foreach ($field in @('type', 'apiVersion', 'name')) { if ($resource[$field] -isnot [string]) { throw 'Invalid compiled bootstrap resource schema.' } }
    }
    $group = $resources['identityResources']
    if ($group['type'] -cne 'Microsoft.Resources/resourceGroups' -or $group['apiVersion'] -cne '2024-03-01' -or
        $group.Contains('copy') -or $group.Contains('properties') -or $group.Contains('resourceGroup')) { throw 'Unexpected compiled identity group resource.' }
    Assert-BootstrapExpression -Actual $group['name'] -Expected "[parameters('identityResourceGroup')]"
    Assert-BootstrapExpression -Actual $group['location'] -Expected "[parameters('location')]"
    Assert-BootstrapEqual -Actual $group['tags'] -Expected @{ purpose = 'azsdk-sample-identities'; 'sample-ci-owner' = "[parameters('ownerToken')]"; 'sample-ci-retention' = 'permanent' }
    $project = $resources['projectRoleAssignments']; $pipeline = $resources['pipelineFoundryUser']
    foreach ($assignment in @($project, $pipeline)) {
        if ($assignment['type'] -cne 'Microsoft.Authorization/roleAssignments' -or $assignment['apiVersion'] -cne '2022-04-01' -or
            $assignment.Contains('resourceGroup') -or $assignment.Contains('location') -or $assignment.Contains('tags')) { throw 'Unexpected compiled role assignment scope or type.' }
    }
    Assert-BootstrapEqual -Actual $project['copy'] -Expected @{ name = 'projectRoleAssignments'; count = "[length(variables('projectServiceGrants'))]" }
    Assert-BootstrapExpression -Actual $project['name'] -Expected "[guid(toLower(variables('projectIdentityResourceId')), toLower(subscription().id), toLower(variables('projectServiceGrants')[copyIndex()].roleDefinitionId), variables('projectServiceGrants')[copyIndex()].condition)]"
    Assert-BootstrapEqual -Actual $project['properties'] -Expected @{
        principalId = "[reference('sharedIdentities').outputs.identities.value.project.principalId]"; principalType = 'ServicePrincipal'
        roleDefinitionId = "[variables('projectServiceGrants')[copyIndex()].roleDefinitionId]"
        condition = "[if(empty(variables('projectServiceGrants')[copyIndex()].condition), null(), variables('projectServiceGrants')[copyIndex()].condition)]"
        conditionVersion = "[if(empty(variables('projectServiceGrants')[copyIndex()].condition), null(), '2.0')]"
    }
    if ($pipeline.Contains('copy')) { throw 'The pipeline may receive only one ordinary service grant.' }
    Assert-BootstrapExpression -Actual $pipeline['condition'] -Expected "[parameters('createPipelineGrant')]"
    Assert-BootstrapExpression -Actual $pipeline['name'] -Expected "[guid(toLower(parameters('pipelinePrincipalId')), toLower(subscription().id), toLower(variables('approvedRoleDefinitionIds').foundryUser), '')]"
    Assert-BootstrapEqual -Actual $pipeline['properties'] -Expected @{ principalId = "[parameters('pipelinePrincipalId')]"; principalType = 'ServicePrincipal'; roleDefinitionId = "[variables('approvedRoleDefinitionIds').foundryUser]" }
    $module = $resources['sharedIdentities']
    if ($module['type'] -cne 'Microsoft.Resources/deployments' -or $module['apiVersion'] -cnotin @('2022-09-01', '2024-03-01', '2025-04-01') -or
        $module.Contains('copy') -or $module.Contains('location') -or $module.Contains('tags')) { throw 'Unexpected compiled identity module.' }
    Assert-BootstrapExpression -Actual $module['name'] -Expected "[format('shared-identities-{0}', uniqueString(subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('identityResourceGroup')), parameters('namePrefix'), variables('locationSuffix')))]"
    Assert-BootstrapExpression -Actual $module['resourceGroup'] -Expected "[parameters('identityResourceGroup')]"
    $properties = $module['properties']; Assert-BootstrapKeys -Value $properties -Required @('expressionEvaluationOptions', 'mode', 'parameters', 'template')
    Assert-BootstrapEqual -Actual $properties['mode'] -Expected 'Incremental'
    Assert-BootstrapEqual -Actual $properties['expressionEvaluationOptions'] -Expected @{ scope = 'inner' }
    $parameters = @{}
    foreach ($name in @('namePrefix', 'location', 'ownerToken')) { $parameters[$name] = @{ value = "[parameters('$name')]" } }
    $parameters['locationSuffix'] = @{ value = "[variables('locationSuffix')]" }
    Assert-BootstrapEqual -Actual $properties['parameters'] -Expected $parameters
    $nested = $properties['template']
    Assert-BootstrapKeys -Value $nested -Required @('languageVersion', 'parameters', 'variables', 'resources', 'outputs') -Optional @('$schema', 'contentVersion', 'metadata', 'definitions')
    Assert-BootstrapEqual -Actual $nested['languageVersion'] -Expected '2.0'
    Assert-BootstrapEqual -Actual $nested['variables'] -Expected @{ identityPurposes = @('project', 'account', 'search', 'function') }
    Assert-BootstrapKeys -Value $nested['parameters'] -Required @('namePrefix', 'location', 'locationSuffix', 'ownerToken')
    foreach ($binding in @(@('namePrefix', 1, 33), @('location', 1, 30), @('locationSuffix', 1, 30), @('ownerToken', 32, 32))) {
        Assert-BootstrapStringParameter -Value $nested['parameters'][$binding[0]] -Minimum $binding[1] -Maximum $binding[2]
    }
    Assert-BootstrapKeys -Value $nested['resources'] -Required @('managedIdentities'); $identity = $nested['resources']['managedIdentities']
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
    foreach ($output in @($Compiled['outputs'].Values) + @($nested['outputs'].Values)) { Assert-BootstrapKeys -Value $output -Required @('value') -Optional @('type', '$ref', 'metadata') }
    Assert-BootstrapExpression -Actual $Compiled['outputs']['identityResourceGroupId']['value'] -Expected @(
        "[subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('identityResourceGroup'))]", "[resourceInfo('identityResources').id]")
    Assert-BootstrapExpression -Actual $Compiled['outputs']['identities']['value'] -Expected "[reference('sharedIdentities').outputs.identities.value]"
    Assert-BootstrapExpression -Actual $Compiled['outputs']['roleDefinitionIds']['value'] -Expected "[variables('approvedRoleDefinitionIds')]"
    Assert-BootstrapExpression -Actual $Compiled['outputs']['blobOwnerCondition']['value'] -Expected "[variables('storageBlobOwnerCondition')]"
    $metadata = $nested['outputs']['identities']['value']; $purposes = @('project', 'account', 'search', 'function')
    Assert-BootstrapKeys -Value $metadata -Required $purposes
    for ($index = 0; $index -lt 4; $index++) {
        $entry = $metadata[$purposes[$index]]; Assert-BootstrapKeys -Value $entry -Required @('resourceId', 'principalId', 'clientId', 'tenantId')
        $resourceId = "resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', format('{0}-{1}-{2}', parameters('namePrefix'), variables('identityPurposes')[$index], parameters('locationSuffix')))"
        Assert-BootstrapExpression -Actual $entry['resourceId'] -Expected @("[$resourceId]", "[resourceInfo('managedIdentities[$index]').id]", "[resourceInfo(format('managedIdentities[{0}]', $index)).id]")
        foreach ($field in @('principalId', 'clientId', 'tenantId')) {
            Assert-BootstrapExpression -Actual $entry[$field] -Expected @("[reference('managedIdentities[$index]').$field]", "[reference(format('managedIdentities[{0}]', $index)).$field]", "[reference($resourceId, '2023-01-31').$field]")
        }
    }
    $outputGrants = $Compiled['outputs']['roleAssignments']['value']; Assert-BootstrapKeys -Value $outputGrants -Required @('project', 'pipeline')
    Assert-BootstrapExpression -Actual $outputGrants['project'] -Expected "[map(variables('projectServiceGrants'), lambda('grant', createObject('roleAssignmentId', subscriptionResourceId('Microsoft.Authorization/roleAssignments', guid(toLower(variables('projectIdentityResourceId')), toLower(subscription().id), toLower(lambdaVariables('grant').roleDefinitionId), lambdaVariables('grant').condition)), 'principalId', reference('sharedIdentities').outputs.identities.value.project.principalId, 'roleDefinitionId', lambdaVariables('grant').roleDefinitionId, 'scope', subscription().id, 'condition', lambdaVariables('grant').condition, 'conditionVersion', if(empty(lambdaVariables('grant').condition), '', '2.0'))))]"
    Assert-BootstrapExpression -Actual $outputGrants['pipeline'] -Expected "[if(empty(parameters('pipelinePrincipalId')), null(), createObject('roleAssignmentId', parameters('pipelineRoleAssignmentId'), 'principalId', parameters('pipelinePrincipalId'), 'roleDefinitionId', variables('approvedRoleDefinitionIds').foundryUser, 'scope', subscription().id, 'condition', '', 'conditionVersion', ''))]"
}