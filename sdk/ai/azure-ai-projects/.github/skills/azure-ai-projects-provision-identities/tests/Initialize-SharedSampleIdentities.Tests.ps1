# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

. (Join-Path $PSScriptRoot 'BootstrapFixtures.ps1')

Describe 'Shared identity bootstrap fails closed through the real entry point' {
    BeforeEach {
        $script:bootstrapOriginalSubscription = $env:AZURE_SUBSCRIPTION_ID; $script:bootstrapOriginalTenant = $env:AZURE_TENANT_ID
        $script:bootstrapFixture = New-BootstrapCliFixture
        $env:AZURE_SUBSCRIPTION_ID = $script:bootstrapFixture.subscriptionId; $env:AZURE_TENANT_ID = $script:bootstrapFixture.tenantId
    }
    AfterEach { $env:AZURE_SUBSCRIPTION_ID = $script:bootstrapOriginalSubscription; $env:AZURE_TENANT_ID = $script:bootstrapOriginalTenant }

    # Original 75 regression cases, adapted to the generic schema-2 plan. Reuse now
    # excludes the pipeline resource altogether (stronger than the old NoChange).
    It 'previews the exact twelve IDs and independent RFC4122 UUIDv5 grant names in uksouth' {
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Previewed'; $result.state.schemaVersion | Should Be 2
        $result.state.location | Should Be 'uksouth'; $result.state.setName | Should Be 'unit-test'
        $result.state.identityResourceGroup | Should Be 'rg-azsdk-identities-unit-test-uksouth'
        @($result.state.prediction.changes).Count | Should Be 12
        @($result.calls | Where-Object { $_ -match '^deployment sub what-if .*--no-pretty-print .*--result-format FullResourcePayloads' }).Count | Should Be 1
        $result.mutations.Count | Should Be 0
    }
    It 'requires a separately saved dry run before apply' {
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Match 'separate dry run'; $result.calls.Count | Should Be 0; $result.state | Should BeNullOrEmpty
    }
    It 'never replays recorded <Status>, even with an absent RG' -TestCases @(
        @{ Status = 'Applying' }, @{ Status = 'Failed' }, @{ Status = 'Created' }, @{ Status = 'Verified' }
    ) {
        param($Status)
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status $Status; $script:bootstrapFixture.groupExists = $false
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Match 'already recorded'; $result.calls.Count | Should Be 0; $result.bytes | Should Be $result.originalBytes
    }
    It 'rejects malformed state <Label> before any CLI invocation' -TestCases @(
        @{ Label = 'schema number as a string'; Field = 'schemaVersion'; Value = '2' }, @{ Label = 'schema boolean'; Field = 'schemaVersion'; Value = $true },
        @{ Label = 'unknown status'; Field = 'status'; Value = 'Retryable' }, @{ Label = 'status array'; Field = 'status'; Value = @('Previewed') },
        @{ Label = 'foreign deployment'; Field = 'deploymentName'; Value = 'another-deployment' }
    ) {
        param($Label, $Field, $Value)
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture; $script:bootstrapFixture.state[$Field] = $Value
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty; $result.calls.Count | Should Be 0; $result.bytes | Should Be $result.originalBytes
    }
    It 'requires group-exists to be a JSON boolean, not <Label>' -TestCases @(
        @{ Label = 'null'; Value = $null }, @{ Label = 'a string'; Value = 'false' }, @{ Label = 'zero'; Value = 0 },
        @{ Label = 'an object'; Value = @{} }, @{ Label = 'a singleton JSON array'; Value = @($false) }
    ) {
        param($Label, $Value)
        $script:bootstrapFixture.groupExists = $Value; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'actual JSON boolean'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects validation without explicit success: <Label>' -TestCases @(
        @{ Label = 'null'; Value = $null }, @{ Label = 'empty object'; Value = @{} },
        @{ Label = 'failed state plus null error'; Value = @{ properties = @{ provisioningState = 'Failed' }; error = $null } },
        @{ Label = 'state array'; Value = @{ properties = @{ provisioningState = @('Succeeded') }; error = $null } },
        @{ Label = 'failed status plus null error'; Value = @{ status = 'Failed'; error = $null } },
        @{ Label = 'contradictory status'; Value = @{ status = 'Failed'; properties = @{ provisioningState = 'Succeeded' }; error = $null } },
        @{ Label = 'error envelope'; Value = @{ error = @{ code = 'Denied' } } }, @{ Label = 'singleton root array'; Value = @(@{ error = $null }) }
    ) {
        param($Label, $Value)
        $script:bootstrapFixture.validation = $Value; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'validation'; $result.state | Should BeNullOrEmpty
        @($result.calls | Where-Object { $_ -match '^deployment sub what-if ' }).Count | Should Be 0; $result.mutations.Count | Should Be 0
    }
    It 'accepts native validation error:null success without inventing success for missing error' {
        $script:bootstrapFixture.validation = @{ error = $null }; $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Previewed'; $result.mutations.Count | Should Be 0
    }
    It 'rejects malformed what-if <Label>' -TestCases @(
        @{ Label = 'null'; Value = $null }, @{ Label = 'empty object'; Value = @{} },
        @{ Label = 'failed status'; Value = @{ status = 'Failed'; changes = @() } }, @{ Label = 'status array'; Value = @{ status = @('Succeeded'); changes = @() } },
        @{ Label = 'null changes'; Value = @{ status = 'Succeeded'; changes = $null } }, @{ Label = 'changes string'; Value = @{ status = 'Succeeded'; changes = '[]' } },
        @{ Label = 'singleton root array'; Value = @(@{ status = 'Succeeded'; changes = @() }) }
    ) {
        param($Label, $Value)
        $script:bootstrapFixture.prediction = $Value; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'What-if'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects foreign what-if IDs even for <ChangeType>' -TestCases @(@{ ChangeType = 'Create' }, @{ ChangeType = 'NoChange' }, @{ ChangeType = 'Unsupported' }) {
        param($ChangeType)
        $script:bootstrapFixture.prediction.changes += @{ resourceId = ($script:bootstrapFixture.scope + '/providers/Microsoft.Authorization/roleAssignments/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'); changeType = $ChangeType; after = @{ type = 'Microsoft.Authorization/roleAssignments' } }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'unknown or duplicate resource ID'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'does not wildcard resources under the approved identity RG' {
        $script:bootstrapFixture.prediction.changes += @{ resourceId = ($script:bootstrapFixture.groupId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/not-approved'); changeType = 'Create'; after = @{ type = 'Microsoft.ManagedIdentity/userAssignedIdentities' } }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'unknown or duplicate resource ID'; $result.mutations.Count | Should Be 0
    }
    It 'limits Unsupported to the six exact project assignment IDs' {
        $script:bootstrapFixture.prediction.changes[1].changeType = 'Unsupported'; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'Only new group, identity, and module'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'checks all seven grant definitions in the compiled schema before ARM validation' {
        $script:bootstrapFixture.compiled.variables.approvedRoleDefinitionIds.foundryUser = "[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635')]"
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'Compiled bootstrap expression'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0; $result.state | Should BeNullOrEmpty
    }
    It 'rejects opaque union project properties before ARM validation' {
        $script:bootstrapFixture.compiled.resources.projectRoleAssignments.properties = "[union(createObject('principalId', reference('sharedIdentities').outputs.identities.value.project.principalId, 'principalType', 'ServicePrincipal', 'roleDefinitionId', variables('projectServiceGrants')[copyIndex()].roleDefinitionId), if(empty(variables('projectServiceGrants')[copyIndex()].condition), createObject(), createObject('condition', variables('projectServiceGrants')[copyIndex()].condition, 'conditionVersion', '2.0')))]"
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'bootstrap object schema'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects changed compiled project <Field>: <Label> before ARM validation' -TestCases @(
        @{ Field = 'principalId'; Label = 'another identity'; Value = "[reference('sharedIdentities').outputs.identities.value.account.principalId]" },
        @{ Field = 'principalType'; Label = 'another principal type'; Value = 'User' },
        @{ Field = 'roleDefinitionId'; Label = 'fixed role'; Value = "[variables('approvedRoleDefinitionIds').foundryUser]" },
        @{ Field = 'condition'; Label = 'missing null branch'; Value = "[variables('projectServiceGrants')[copyIndex()].condition]" },
        @{ Field = 'conditionVersion'; Label = 'unconditional version'; Value = '2.0' },
        @{ Field = 'condition'; Label = 'literal JSON null'; Value = $null }, @{ Field = 'conditionVersion'; Label = 'literal JSON null'; Value = $null }
    ) {
        param($Field, $Label, $Value)
        $script:bootstrapFixture.compiled.resources.projectRoleAssignments.properties[$Field] = $Value; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'contract value differs'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects a redirected module principal output before granting roles to another identity' {
        $script:bootstrapFixture.compiled.resources.sharedIdentities.properties.template.outputs.identities.value.project.principalId = "[reference('managedIdentities[1]').principalId]"
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'Compiled bootstrap expression'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0; $result.mutations.Count | Should Be 0
    }
    It 'reuses an exact existing pipeline grant without deploying it and deduplicates list views by ID' {
        $fixture = $script:bootstrapFixture; $assignment = New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId
        $fixture.descendants = @($assignment); $fixture.parents = @($assignment); $fixture.prediction.changes = @($fixture.prediction.changes[0..10])
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Previewed'; $result.state.pipelineMode | Should Be 'Reuse'
        $result.state.parameters.createPipelineGrant.value | Should Be $false; $result.state.existingPipelineAssignmentId | Should Be $assignment.id; $result.mutations.Count | Should Be 0
    }
    It 'accepts omitted principalType only in the schema-checked what-if payload' {
        $script:bootstrapFixture.prediction.changes[-1].after.properties.Remove('principalType'); $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Previewed'; $result.mutations.Count | Should Be 0
    }
    It 'rejects explicit invalid what-if principalType: <Label>' -TestCases @(@{ Label = 'user'; Value = 'User' }, @{ Label = 'null'; Value = $null }, @{ Label = 'empty'; Value = '' }) {
        param($Label, $Value)
        $script:bootstrapFixture.prediction.changes[-1].after.properties['principalType'] = $Value; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'could not be verified exactly'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects an existing grant whose actual GET metadata omits principalType' {
        $fixture = $script:bootstrapFixture; $assignment = New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId
        $assignment.properties.Remove('principalType'); $fixture.descendants = @($assignment); $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'could not be verified exactly'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'does not relax principalType verification after creation' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture; $script:bootstrapFixture.descendants[0].properties.Remove('principalType'); $script:bootstrapFixture.parents = @($script:bootstrapFixture.descendants)
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'could not be verified exactly'; $result.state.status | Should Be 'Created'; $result.mutations.Count | Should Be 0
    }
    It 'rejects an unverified NoChange pipeline grant instead of trusting the prediction' {
        $script:bootstrapFixture.prediction.changes[-1].changeType = 'NoChange'; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'unverified pipeline grant'; $result.mutations.Count | Should Be 0
    }
    It 'rejects a stale project assignment before any ARM preview rather than reusing its stable name' {
        $fixture = $script:bootstrapFixture; $fixture.descendants = @(New-BootstrapFixtureAssignment -Grant $fixture.grants[0] -PrincipalId 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee')
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'stale or replacement identity'
        @($result.calls | Where-Object { $_ -match '^deployment sub (validate|what-if|create) ' }).Count | Should Be 0; $result.mutations.Count | Should Be 0
    }
    It 'refuses a pipeline grant whose condition metadata differs instead of modifying it' {
        $fixture = $script:bootstrapFixture; $assignment = New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId
        $assignment.properties.conditionVersion = '2.0'; $fixture.descendants = @($assignment); $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'could not be verified exactly'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'keeps WhatIf apply in Previewed without submitting a create' {
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture; $result = Invoke-IsolatedBootstrap -Apply -Preview
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Previewed'; $result.mutations.Count | Should Be 0
    }
    It 'cannot overwrite a concurrently recorded attempt with Previewed or apply it again' {
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture; $script:bootstrapFixture.stateDuringWhatIf = 'Applying'; $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Match 'no replay or state downgrade'; $result.state.status | Should Be 'Applying'; $result.mutations.Count | Should Be 0
    }
    It 'verifies immutable outputs and exact six/zero assignment sets using both list views' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture; $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Verified'; $result.state.identities.project.principalId | Should Be $script:bootstrapFixture.identities.project.principalId
        @($result.calls | Where-Object { $_ -match '/roleAssignments\?api-version=2022-04-01$' }).Count | Should Be 1
        @($result.calls | Where-Object { $_ -match '\$filter=atScope\(\)' }).Count | Should Be 1; $result.mutations.Count | Should Be 0
    }
    It 'rejects a same-name same-tags replacement of <Purpose> (<Field>)' -TestCases @(
        @{ Purpose = 'project'; Field = 'principalId' }, @{ Purpose = 'account'; Field = 'principalId' }, @{ Purpose = 'search'; Field = 'principalId' },
        @{ Purpose = 'function'; Field = 'principalId' }, @{ Purpose = 'project'; Field = 'clientId' }
    ) {
        param($Purpose, $Field)
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture; $script:bootstrapFixture.live[$Purpose].properties[$Field] = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'replacement identity'; $result.bytes | Should Be $result.originalBytes
        @($result.calls | Where-Object { $_ -match '/providers/Microsoft.Resources/deployments/' }).Count | Should Be 0; $result.mutations.Count | Should Be 0
    }
    It 'detects an extra <Boundary> assignment for <Purpose>, not merely atScope grants' -TestCases @(
        @{ Purpose = 'project'; Boundary = 'RG' }, @{ Purpose = 'project'; Boundary = 'resource' }, @{ Purpose = 'project'; Boundary = 'inherited' },
        @{ Purpose = 'account'; Boundary = 'RG' }, @{ Purpose = 'search'; Boundary = 'resource' }, @{ Purpose = 'function'; Boundary = 'inherited' }
    ) {
        param($Purpose, $Boundary)
        $fixture = $script:bootstrapFixture; Set-BootstrapRecordedFixture -Fixture $fixture
        $target = switch ($Boundary) { 'RG' { $fixture.scope + '/resourceGroups/another-group' }; 'resource' { $fixture.scope + '/resourceGroups/another-group/providers/Microsoft.Storage/storageAccounts/example' }; 'inherited' { '/providers/Microsoft.Management/managementGroups/example-parent' } }
        $grant = @{ roleAssignmentId = ($target + '/providers/Microsoft.Authorization/roleAssignments/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'); roleDefinitionId = ($fixture.scope + '/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c'); scope = $target; condition = ''; conditionVersion = '' }
        $assignment = New-BootstrapFixtureAssignment -Grant $grant -PrincipalId $fixture.identities[$Purpose].principalId
        if ($Boundary -ceq 'inherited') { $fixture.parents += $assignment } else { $fixture.descendants += $assignment }
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'exact identity grant set differs'; $result.bytes | Should Be $result.originalBytes; $result.mutations.Count | Should Be 0
    }
    It 'reconciles ambiguous <Status> using only the recorded deployment GET outputs' -TestCases @(@{ Status = 'Applying' }, @{ Status = 'Failed' }) {
        param($Status)
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status $Status; $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Verified'; $result.state.outputs.identities.value.function.clientId | Should Be $script:bootstrapFixture.identities.function.clientId
        @($result.calls | Where-Object { $_ -match '^rest --method get .*?/providers/Microsoft.Resources/deployments/azsdk-identities-0123456789ab\?api-version=2022-09-01' }).Count | Should Be 1; $result.mutations.Count | Should Be 0
    }
    It 'does not mark an ambiguous attempt verified without successful recorded outputs' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Failed; $script:bootstrapFixture.recorded.properties.provisioningState = 'Failed'; $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'immutable output baseline'; $result.bytes | Should Be $result.originalBytes; $result.state.status | Should Be 'Failed'; $result.mutations.Count | Should Be 0
    }
    It 'does not refresh Verified metadata from a different saved identity binding' {
        Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Verified; $script:bootstrapFixture.state.identities.search.clientId = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'contract value differs'; $result.bytes | Should Be $result.originalBytes; $result.mutations.Count | Should Be 0
    }

    # New consolidation, generic parameter/state, legacy immutability and create lifecycle coverage.
    It 'requires explicit new <Field> and does not fall back to environment or active account' -TestCases @(
        @{ Field = 'SubscriptionId' }, @{ Field = 'TenantId' }, @{ Field = 'Location' }, @{ Field = 'SetName' }, @{ Field = 'ExpectedCallerPrincipalId' }
    ) {
        param($Field)
        $script:bootstrapFixture.inputOverride[$Field] = ''; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Not BeNullOrEmpty; $result.calls.Count | Should Be 0; $result.state | Should BeNullOrEmpty
    }
    It 'binds preview input <Field> and rejects apply drift before Azure' -TestCases @(
        @{ Field = 'SubscriptionId'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' }, @{ Field = 'TenantId'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' },
        @{ Field = 'Location'; Value = 'eastus2' }, @{ Field = 'SetName'; Value = 'other-set' },
        @{ Field = 'ExpectedCallerPrincipalId'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' },
        @{ Field = 'PipelinePrincipalId'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' }, @{ Field = 'PipelineClientId'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' }
    ) {
        param($Field, $Value)
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture; $script:bootstrapFixture.inputOverride[$Field] = $Value; $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty; $result.calls.Count | Should Be 0; $result.bytes | Should Be $result.originalBytes
    }
    It 'rejects persisted parameter drift for <Name>' -TestCases @(
        @{ Name = 'identityResourceGroup' }, @{ Name = 'namePrefix' }, @{ Name = 'location' }, @{ Name = 'ownerToken' },
        @{ Name = 'pipelinePrincipalId' }, @{ Name = 'pipelineRoleAssignmentId' }, @{ Name = 'createPipelineGrant' }
    ) {
        param($Name)
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture; $script:bootstrapFixture.state.parameters[$Name].value = 'foreign'; $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty; $result.calls.Count | Should Be 0; $result.bytes | Should Be $result.originalBytes
    }
    It 'supports a different canonical region and set' {
        $script:bootstrapFixture = New-BootstrapCliFixture -Region australiaeast -Set another-set; $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.identityResourceGroup | Should Be 'rg-azsdk-identities-another-set-australiaeast'; $result.mutations.Count | Should Be 0
    }
    It 'rejects noncanonical or malformed region metadata <Label>' -TestCases @(
        @{ Label = 'wrong canonical region'; Value = @(@{ name = 'eastus2'; displayName = 'uksouth' }) }, @{ Label = 'object instead of array'; Value = @{ name = 'uksouth' } },
        @{ Label = 'duplicate'; Value = @(@{ name = 'uksouth' }, @{ name = 'uksouth' }) }, @{ Label = 'null'; Value = $null }
    ) {
        param($Label, $Value)
        $script:bootstrapFixture.locations = $Value; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'canonical region'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects unregistered provider without registering it' {
        $script:bootstrapFixture.cliOverride = { param($Arguments, $Fixture) if (($Arguments[0..1] -join ' ') -ceq 'provider show') { '{"registrationState":"NotRegistered"}' } }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'already be registered'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'requires pipeline principal and client IDs as a pair: <Field>' -TestCases @(@{ Field = 'PipelinePrincipalId' }, @{ Field = 'PipelineClientId' }) {
        param($Field)
        $script:bootstrapFixture.inputOverride[$Field] = ''; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'supplied together'; $result.calls.Count | Should Be 0
    }
    It 'previews None with six grants, empty pipeline bindings and no directory lookup' {
        $script:bootstrapFixture = New-BootstrapCliFixture -NoPipeline; $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.pipelineMode | Should Be 'None'; $result.state.parameters.createPipelineGrant.value | Should Be $false
        $result.state.parameters.pipelineRoleAssignmentId.value | Should Be ''; $result.state.parameters.pipelinePrincipalId.value | Should Be ''
        @($result.state.prediction.changes).Count | Should Be 11; @($result.calls | Where-Object { $_ -match '^ad sp show ' }).Count | Should Be 0; $result.mutations.Count | Should Be 0
    }
    It 'verifies None with JSON null pipeline output' {
        $script:bootstrapFixture = New-BootstrapCliFixture -NoPipeline; Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture; $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Verified'; $result.state.outputs.roleAssignments.value.pipeline | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects non-null None pipeline output: <Label>' -TestCases @(@{ Label = 'empty object'; Value = @{} }, @{ Label = 'empty string'; Value = '' }) {
        param($Label, $Value)
        $script:bootstrapFixture = New-BootstrapCliFixture -NoPipeline; Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture
        $script:bootstrapFixture.state.outputs.roleAssignments.value.pipeline = $Value; $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'JSON null'; $result.bytes | Should Be $result.originalBytes; $result.mutations.Count | Should Be 0
    }
    It 'reuses a differently named exact direct grant and preserves unrelated roles without modifying either' {
        $fixture = $script:bootstrapFixture; $fixture.grants[6].roleAssignmentId = $fixture.scope + '/providers/Microsoft.Authorization/roleAssignments/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
        $fixture.prediction.changes = @($fixture.prediction.changes[0..10]); Set-BootstrapPreviewFixture -Fixture $fixture -PipelineMode Reuse
        $unrelated = @{ roleAssignmentId = ($fixture.scope + '/providers/Microsoft.Authorization/roleAssignments/ffffffff-ffff-4fff-8fff-ffffffffffff'); scope = $fixture.scope; roleDefinitionId = ($fixture.scope + '/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c'); condition = ''; conditionVersion = '' }
        $fixture.descendants += New-BootstrapFixtureAssignment -Grant $unrelated -PrincipalId $fixture.pipelinePrincipalId
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Created'; $result.state.pipelineMode | Should Be 'Reuse'
        $result.state.parameters.createPipelineGrant.value | Should Be $false; $result.state.outputs.roleAssignments.value.pipeline.roleAssignmentId | Should Be $fixture.grants[6].roleAssignmentId
        $fixture.createObservedStatus | Should Be 'Applying'; $result.mutations.Count | Should Be 1
    }
    It 'does not redeploy an existing grant even as NoChange' {
        $fixture = $script:bootstrapFixture; $fixture.descendants = @(New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId)
        $fixture.prediction.changes[-1].changeType = 'NoChange'; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'unknown or duplicate'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects actual existing grant drift <Field>' -TestCases @(
        @{ Field = 'principalType'; Value = 'User' }, @{ Field = 'scope'; Value = '/providers/Microsoft.Management/managementGroups/parent' },
        @{ Field = 'condition'; Value = 'foreign' }, @{ Field = 'conditionVersion'; Value = '2.0' }, @{ Field = 'delegatedManagedIdentityResourceId'; Value = '/foreign' }
    ) {
        param($Field, $Value)
        $fixture = $script:bootstrapFixture; $assignment = New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId
        $assignment.properties[$Field] = $Value; $fixture.descendants = @($assignment); $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'could not be verified exactly'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects duplicate existing pipeline grants rather than selecting or repairing one' {
        $fixture = $script:bootstrapFixture; $one = New-BootstrapFixtureAssignment -Grant $fixture.grants[6] -PrincipalId $fixture.pipelinePrincipalId
        $two = $one | ConvertTo-Json -Depth 10 | ConvertFrom-Json -AsHashtable; $two.id = $fixture.scope + '/providers/Microsoft.Authorization/roleAssignments/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
        $fixture.descendants = @($one, $two); $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'Duplicate pipeline'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'records Applying before exactly one successful simulated create, then Created' {
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture; $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should BeNullOrEmpty; $script:bootstrapFixture.createObservedStatus | Should Be 'Applying'; $result.state.status | Should Be 'Created'
        $result.state.outputs.identities.value.project.principalId | Should Be $script:bootstrapFixture.identities.project.principalId; $result.mutations.Count | Should Be 1
        $script:bootstrapFixture.state = $result.state; $script:bootstrapFixture.calls.Clear(); $again = Invoke-IsolatedBootstrap -Apply
        $again.failure | Should Match 'already recorded'; $again.calls.Count | Should Be 0; $again.bytes | Should Be $again.originalBytes
    }
    It 'records Failed after ambiguous create then reconciles GET-only without a retry' {
        $fixture = $script:bootstrapFixture; Set-BootstrapPreviewFixture -Fixture $fixture; $fixture.createFailure = $true; $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty; $fixture.createObservedStatus | Should Be 'Applying'; $result.state.status | Should Be 'Failed'; $result.mutations.Count | Should Be 1
        $fixture.state = $result.state; $fixture.calls.Clear(); $replay = Invoke-IsolatedBootstrap -Apply
        $replay.failure | Should Match 'already recorded'; $replay.calls.Count | Should Be 0
        $fixture.calls.Clear(); $fixture.groupExists = $true
        $fixture.descendants = @(for ($index = 0; $index -lt 7; $index++) { New-BootstrapFixtureAssignment -Grant $fixture.grants[$index] -PrincipalId $(if ($index -eq 6) { $fixture.pipelinePrincipalId } else { $fixture.identities.project.principalId }) })
        $verified = Invoke-IsolatedBootstrap -VerifyOnly
        $verified.failure | Should BeNullOrEmpty; $verified.state.status | Should Be 'Verified'; $verified.mutations.Count | Should Be 0
    }
    It 'records Failed rather than Created for malformed create result <Label>' -TestCases @(
        @{ Label = 'unsuccessful'; Field = 'provisioningState'; Value = 'Failed' }, @{ Label = 'state array'; Field = 'provisioningState'; Value = @('Succeeded') },
        @{ Label = 'error'; Field = 'error'; Value = @{ code = 'Denied' } }
    ) {
        param($Label, $Field, $Value)
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture; $script:bootstrapFixture.createResponse.properties[$Field] = $Value
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty; $result.state.status | Should Be 'Failed'; $script:bootstrapFixture.createObservedStatus | Should Be 'Applying'; $result.mutations.Count | Should Be 1
    }
    It 'refuses template hash drift after a separate preview' {
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture; $script:bootstrapFixture.compiled.metadata = @{ changed = 'after approval' }; $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Match 'compiled template changed'; $result.bytes | Should Be $result.originalBytes; $result.mutations.Count | Should Be 0
    }
    It 'refuses pipeline mode drift from Create to Reuse after preview' {
        Set-BootstrapPreviewFixture -Fixture $script:bootstrapFixture
        $script:bootstrapFixture.descendants = @(New-BootstrapFixtureAssignment -Grant $script:bootstrapFixture.grants[6] -PrincipalId $script:bootstrapFixture.pipelinePrincipalId)
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty; $result.bytes | Should Be $result.originalBytes; $result.mutations.Count | Should Be 0
    }
    It 'rejects changed or unknown compiled resource <Label>' -TestCases @(@{ Label = 'unknown top resource'; Nested = $false }, @{ Label = 'unknown nested resource'; Nested = $true }) {
        param($Label, $Nested)
        $resources = if ($Nested) { $script:bootstrapFixture.compiled.resources.sharedIdentities.properties.template.resources } else { $script:bootstrapFixture.compiled.resources }
        $resources.foreign = @{ type = 'Microsoft.Authorization/roleAssignments'; apiVersion = '2022-04-01'; name = 'foreign' }; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Not BeNullOrEmpty; @($result.calls | Where-Object { $_ -match '^deployment sub ' }).Count | Should Be 0; $result.mutations.Count | Should Be 0
    }
    It 'retains the literal ABAC whitespace contract' {
        $script:bootstrapFixture.compiled.variables.storageBlobOwnerCondition = $script:bootstrapFixture.condition.Replace('  AND  ', ' AND '); $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'contract value differs'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects pipeline conditional deployment depending on principal emptiness instead of create flag' {
        $script:bootstrapFixture.compiled.resources.pipelineFoundryUser.condition = "[not(empty(parameters('pipelinePrincipalId')))]"; $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'Compiled bootstrap expression'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'denies legacy <Mode> before any Azure call without changing a byte' -TestCases @(@{ Mode = 'Preview' }, @{ Mode = 'Apply' }) {
        param($Mode)
        $script:bootstrapFixture = New-BootstrapCliFixture -Legacy; Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Verified
        $result = Invoke-IsolatedBootstrap -Apply:($Mode -ceq 'Apply')
        $result.failure | Should Match 'verification-only'; $result.calls.Count | Should Be 0; $result.bytes | Should Be $result.originalBytes; $result.lockExists | Should Be $false
    }
    It 'verifies legacy <Status> preserving original bytes and hash without templates, compilation or state writes' -TestCases @(
        @{ Status = 'Verified' }, @{ Status = 'Created' }, @{ Status = 'Applying' }, @{ Status = 'Failed' }
    ) {
        param($Status)
        $fixture = New-BootstrapCliFixture -Legacy; $script:bootstrapFixture = $fixture; Set-BootstrapRecordedFixture -Fixture $fixture -Status $Status
        $fixture.state.templateHash = ('a' * 64); $fixture.noTemplates = $true; $hash = $fixture.state.templateHash
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be $Status; $result.state.templateHash | Should Be $hash
        $result.bytes | Should Be $result.originalBytes; $result.lockExists | Should Be $false; $result.mutations.Count | Should Be 0
        @($result.calls | Where-Object { $_ -match '^(bicep|deployment sub|account list-locations|provider)' }).Count | Should Be 0
        @($result.calls | Where-Object { $_ -match '/providers/Microsoft.Resources/deployments/' }).Count | Should Be $(if ($Status -cin @('Applying', 'Failed')) { 1 } else { 0 })
    }
    It 'keeps legacy environment-only target compatibility restricted to VerifyOnly' {
        $script:bootstrapFixture = New-BootstrapCliFixture -Legacy; Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Verified
        $script:bootstrapFixture.omitTargetInputs = $true; $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty; $result.bytes | Should Be $result.originalBytes; $result.mutations.Count | Should Be 0
    }
    It 'fails legacy verification without rewriting state or touching resources: <Fault>' -TestCases @(
        @{ Fault = 'replacement principal' }, @{ Fault = 'replacement client' }, @{ Fault = 'saved identity drift' },
        @{ Fault = 'missing grant' }, @{ Fault = 'grant metadata' }, @{ Fault = 'extra reserved grant' },
        @{ Fault = 'unsuccessful recorded deployment' }
    ) {
        param($Fault)
        $fixture = New-BootstrapCliFixture -Legacy; $script:bootstrapFixture = $fixture
        Set-BootstrapRecordedFixture -Fixture $fixture -Status $(if ($Fault -ceq 'unsuccessful recorded deployment') { 'Failed' } else { 'Verified' })
        $fixture.noTemplates = $true
        switch ($Fault) {
            'replacement principal' { $fixture.live.project.properties.principalId = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' }
            'replacement client' { $fixture.live.search.properties.clientId = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' }
            'saved identity drift' { $fixture.state.identities.account.clientId = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' }
            'missing grant' { $fixture.descendants = @($fixture.descendants[1..6]); $fixture.parents = @($fixture.descendants) }
            'grant metadata' { $fixture.descendants[0].properties.Remove('principalType'); $fixture.parents = @($fixture.descendants) }
            'extra reserved grant' {
                $fixture.descendants += New-BootstrapFixtureAssignment -Grant $fixture.grants[0] -PrincipalId $fixture.identities.function.principalId
            }
            'unsuccessful recorded deployment' { $fixture.recorded.properties.provisioningState = 'Failed' }
        }
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Not BeNullOrEmpty; $result.bytes | Should Be $result.originalBytes
        $result.lockExists | Should Be $false; $result.mutations.Count | Should Be 0
        @($result.calls | Where-Object { $_ -match '^(bicep|deployment sub|account list-locations|provider)' }).Count | Should Be 0
    }
    It 'rejects legacy deployment reconciliation parameter drift <Name>' -TestCases @(@{ Name = 'identityResourceGroup' }, @{ Name = 'namePrefix' }, @{ Name = 'location' }, @{ Name = 'ownerToken' }, @{ Name = 'pipelinePrincipalId' }) {
        param($Name)
        $script:bootstrapFixture = New-BootstrapCliFixture -Legacy; Set-BootstrapRecordedFixture -Fixture $script:bootstrapFixture -Status Failed
        $script:bootstrapFixture.recorded.properties.parameters[$Name].value = 'foreign'; $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should Match 'contract value differs'; $result.bytes | Should Be $result.originalBytes; $result.mutations.Count | Should Be 0; $result.lockExists | Should Be $false
    }

    It 'creates None once with only six grants and verifies its immutable outputs' {
        $script:bootstrapFixture = New-BootstrapCliFixture -NoPipeline; $fixture = $script:bootstrapFixture
        Set-BootstrapPreviewFixture -Fixture $fixture; $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Created'; $result.state.outputs.roleAssignments.value.pipeline | Should BeNullOrEmpty
        $fixture.createObservedStatus | Should Be 'Applying'; $result.mutations.Count | Should Be 1
        $fixture.state = $result.state; $fixture.calls.Clear(); $fixture.groupExists = $true
        $fixture.descendants = @(foreach ($grant in $fixture.grants) { New-BootstrapFixtureAssignment -Grant $grant -PrincipalId $fixture.identities.project.principalId })
        $verified = Invoke-IsolatedBootstrap -VerifyOnly
        $verified.failure | Should BeNullOrEmpty; $verified.state.status | Should Be 'Verified'; $verified.mutations.Count | Should Be 0
    }
    It 'verifies a reused differently named pipeline assignment without deploying or compiling' {
        $fixture = $script:bootstrapFixture; $fixture.grants[6].roleAssignmentId = $fixture.scope + '/providers/Microsoft.Authorization/roleAssignments/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
        $fixture.prediction.changes = @($fixture.prediction.changes[0..10]); Set-BootstrapRecordedFixture -Fixture $fixture -PipelineMode Reuse
        $fixture.noTemplates = $true; $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Verified'; $result.state.existingPipelineAssignmentId | Should Be $fixture.grants[6].roleAssignmentId
        @($result.calls | Where-Object { $_ -match '^(bicep|deployment sub)' }).Count | Should Be 0; $result.mutations.Count | Should Be 0
    }
    It 'rejects caller account mismatch <Field> without any state save' -TestCases @(
        @{ Field = 'id'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' }, @{ Field = 'tenantId'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' },
        @{ Field = 'state'; Value = 'Disabled' }, @{ Field = 'user'; Value = @{ type = 'servicePrincipal' } }
    ) {
        param($Field, $Value)
        $script:bootstrapFixture.overrideField = $Field; $script:bootstrapFixture.overrideValue = $Value
        $script:bootstrapFixture.cliOverride = {
            param($Arguments, $Fixture)
            if (($Arguments[0..1] -join ' ') -ceq 'account show') {
                $account = @{ id = $Fixture.subscriptionId; tenantId = $Fixture.tenantId; state = 'Enabled'; user = @{ type = 'user' } }
                $account[$Fixture.overrideField] = $Fixture.overrideValue; $account | ConvertTo-Json -Depth 10
            }
        }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'approved current administrator'; $result.state | Should BeNullOrEmpty; $result.calls.Count | Should Be 1; $result.mutations.Count | Should Be 0
    }
    It 'rejects token claim mismatch <Field> while suppressing token text' -TestCases @(
        @{ Field = 'tid'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' }, @{ Field = 'oid'; Value = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee' },
        @{ Field = 'scp'; Value = '' }, @{ Field = 'scp'; Value = @('user_impersonation') }
    ) {
        param($Field, $Value)
        $script:bootstrapFixture.overrideField = $Field; $script:bootstrapFixture.overrideValue = $Value
        $script:bootstrapFixture.cliOverride = {
            param($Arguments, $Fixture)
            if (($Arguments[0..1] -join ' ') -ceq 'account get-access-token') {
                $claims = @{ tid = $Fixture.tenantId; oid = $Fixture.callerId; scp = 'user_impersonation' }; $claims[$Fixture.overrideField] = $Fixture.overrideValue
                $payload = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($claims | ConvertTo-Json -Compress))).TrimEnd('=').Replace('+', '-').Replace('/', '_')
                @{ accessToken = ('fixture-secret-marker.' + $payload + '.not-real') } | ConvertTo-Json -Compress
            }
        }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'token suppressed'; $result.failure | Should Not Match 'fixture-secret-marker'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'protects raw malformed JSON and native failures: <Label>' -TestCases @(
        @{ Label = 'malformed JSON'; NativeFailure = $false }, @{ Label = 'native failure'; NativeFailure = $true }
    ) {
        param($Label, $NativeFailure)
        $script:bootstrapFixture.overrideValue = $NativeFailure
        $script:bootstrapFixture.cliOverride = {
            param($Arguments, $Fixture)
            if (($Arguments[0..1] -join ' ') -ceq 'account show') {
                if ($Fixture.overrideValue) { $global:LASTEXITCODE = 1 }
                '{"fixture-secret-marker":"do-not-disclose"'
            }
        }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'suppressed'; $result.failure | Should Not Match 'fixture-secret-marker'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'requires ARM pagination to keep its exact metadata target: <Label>' -TestCases @(
        @{ Label = 'host'; Link = 'https://example.invalid/subscriptions/11111111-1111-1111-1111-111111111111/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01' },
        @{ Label = 'scope'; Link = 'https://management.azure.com/subscriptions/eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01' },
        @{ Label = 'query'; Link = 'https://management.azure.com/subscriptions/11111111-1111-1111-1111-111111111111/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01&unexpected=true' },
        @{ Label = 'filter'; Link = 'https://management.azure.com/subscriptions/11111111-1111-1111-1111-111111111111/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01&$filter=atScope()' }
    ) {
        param($Label, $Link)
        $script:bootstrapFixture.overrideValue = $Link
        $script:bootstrapFixture.cliOverride = {
            param($Arguments, $Fixture)
            if (($Arguments[0..2] -join ' ') -ceq 'rest --method get') { @{ value = @(); nextLink = $Fixture.overrideValue } | ConvertTo-Json -Depth 10 }
        }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'pagination'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'rejects an omitted or duplicated exact what-if resource: <Label>' -TestCases @(@{ Label = 'omitted'; Duplicate = $false }, @{ Label = 'duplicated'; Duplicate = $true }) {
        param($Label, $Duplicate)
        if ($Duplicate) { $script:bootstrapFixture.prediction.changes += $script:bootstrapFixture.prediction.changes[0] }
        else { $script:bootstrapFixture.prediction.changes = @($script:bootstrapFixture.prediction.changes[1..11]) }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match $(if ($Duplicate) { 'unknown or duplicate' } else { 'omitted' }); $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }
    It 'retains a single exact validated module ID in the saved approval and apply' {
        $fixture = $script:bootstrapFixture; $moduleId = $fixture.groupId + '/providers/Microsoft.Resources/deployments/shared-identities-abcdefghijklm'
        $fixture.validation.properties.validatedResources = @(@{ id = $moduleId; type = 'Microsoft.Resources/deployments' })
        $fixture.prediction.changes += @{ resourceId = $moduleId; changeType = 'Create'; after = @{ type = 'Microsoft.Resources/deployments' } }
        Set-BootstrapPreviewFixture -Fixture $fixture; $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Created'; $result.state.validation.properties.validatedResources[0].id | Should Be $moduleId; $result.mutations.Count | Should Be 1
    }
}

Describe 'Single bootstrap owner remains compatible with existing live-test bindings' {
    It 'matches the worker role definitions, literal Blob Owner condition and legacy identity resource IDs' {
        & {
            # Load definitions only; every entry-point side effect remains in isolated fixtures.
            $packageRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../..'))
            . (Join-Path $packageRoot 'tests/samples/ci/SampleCiHelpers.ps1')
            . (Join-Path $PSScriptRoot '../scripts/BootstrapHelpers.ps1')
            $fixture = New-BootstrapCliFixture -Legacy
            $scope = $fixture.scope; $expectedIds = $fixture.ids; $PipelinePrincipalId = $fixture.pipelinePrincipalId
            $grants = @(Get-BootstrapGrantPlan)
            $roles = @(Get-SampleProjectRoleIds)
            $roles.Count | Should Be 6; $grants.Count | Should Be 7
            for ($index = 0; $index -lt 6; $index++) {
                $grants[$index].roleDefinitionId | Should Be "$scope/providers/Microsoft.Authorization/roleDefinitions/$($roles[$index])"
                $grants[$index].roleAssignmentId | Should Be $fixture.grants[$index].roleAssignmentId
            }
            $grants[2].condition | Should BeExactly (Get-SampleBlobOwnerCondition)
            $grants[2].conditionVersion | Should Be '2.0'
            $PipelinePrincipalId | Should BeExactly $fixture.pipelinePrincipalId
            $grants[6].roleAssignmentId | Should BeExactly $fixture.grants[6].roleAssignmentId
            $workerIds = Get-SampleSharedIdentityIds -SubscriptionId $fixture.subscriptionId
            foreach ($purpose in @('project', 'account', 'search', 'function')) {
                $workerIds[$purpose] | Should BeExactly $expectedIds[$purpose]
            }
        }
    }

    It 'keeps provisioning default recreation separate from guarded create and legacy verification' {
        $skillRoot = Join-Path $PSScriptRoot '..'
        $skill = Get-Content -LiteralPath (Join-Path $skillRoot 'SKILL.md') -Raw
        $contract = Get-Content -LiteralPath (Join-Path $skillRoot 'references/recreation.md') -Raw
        $skill | Should Match 're-create the same named set'
        $contract | Should Match 'fresh exact dry run|fresh deletion dry run|dry-run deletion list'
        $contract | Should Match 'explicit\s+approval'
        $contract | Should Match 'pipeline.*Foundry User, Contributor'
        $contract | Should Match 'schema-1 CI state'
        $contract | Should Match 'new external state path'
        $contract | Should Match 'client/principal IDs\s+must differ'
    }
}