# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

. (Join-Path $PSScriptRoot 'BootstrapFixtures.ps1')

Describe 'Bootstrap MI pattern input through the real guarded entry point' {
    BeforeEach {
        $script:bootstrapFixture = New-BootstrapCliFixture -Region westus3 -Pattern 'custom_{resource}_blue'
    }

    It 'accepts a pattern without a set name or encoded region and preserves exact names/role seeds' {
        $fixture = $script:bootstrapFixture
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Previewed'
        $result.state.ContainsKey('setName') | Should Be $false
        $result.state.identityNamePattern | Should BeExactly 'custom_{resource}_blue'
        # Independently calculated with Node's SHA256, not the fixture builder.
        $result.state.identityResourceGroup | Should BeExactly 'rg-azsdk-identities-a4f85bbc1926-westus3'
        $result.state.location | Should BeExactly 'westus3'
        $result.state.schemaVersion | Should Be 3
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $result.state.identityResourceIds[$purpose] | Should BeExactly $fixture.ids[$purpose]
            $result.state.identityResourceIds[$purpose].Split('/')[-1] | Should BeExactly "custom_${purpose}_blue"
        }
        for ($index = 0; $index -lt 6; $index++) {
            $result.state.prediction.changes[5 + $index].resourceId | Should BeExactly $fixture.grants[$index].roleAssignmentId
        }
        $result.mutations.Count | Should Be 0
    }

    It 'applies the separately recorded literal pattern once through the compiled parameter contract' {
        $fixture = $script:bootstrapFixture
        Set-BootstrapPreviewFixture -Fixture $fixture
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should BeNullOrEmpty; $result.state.status | Should Be 'Created'
        $fixture.createObservedStatus | Should Be 'Applying'; $result.mutations.Count | Should Be 1
        $result.state.parameters.identityNamePattern.value | Should BeExactly 'custom_{resource}_blue'
        $result.state.parameters.ContainsKey('namePrefix') | Should Be $false
        $result.state.parameters.location.value | Should BeExactly 'westus3'
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $result.state.outputs.identities.value[$purpose].resourceId | Should BeExactly $fixture.ids[$purpose]
        }
    }

    It 'rejects malformed or conflicting pattern inputs before any Azure call: <Label>' -TestCases @(
        @{ Label = 'no placeholder'; Pattern = 'custom_project_blue'; Location = 'westus3'; Set = '' },
        @{ Label = 'two placeholders'; Pattern = 'custom_{resource}_{resource}'; Location = 'westus3'; Set = '' },
        @{ Label = 'empty'; Pattern = ''; Location = 'westus3'; Set = '' },
        @{ Label = 'invalid character'; Pattern = 'custom.{resource}'; Location = 'westus3'; Set = '' },
        @{ Label = 'missing explicit region'; Pattern = 'custom_{resource}_blue'; Location = ''; Set = '' },
        @{ Label = 'obsolete set input'; Pattern = 'custom_{resource}_blue'; Location = 'westus3'; Set = 'other-set' }
    ) {
        param($Label, $Pattern, $Location, $Set)
        $fixture = $script:bootstrapFixture
        $fixture.inputOverride.IdentityNamePattern = $Pattern
        $fixture.inputOverride.Location = $Location; $fixture.inputOverride.SetName = $Set
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Not BeNullOrEmpty
        $result.calls.Count | Should Be 0; $result.state | Should BeNullOrEmpty
    }

    It 'binds the pattern to a saved generation before Azure or state changes' {
        $fixture = $script:bootstrapFixture
        Set-BootstrapPreviewFixture -Fixture $fixture
        $fixture.inputOverride.IdentityNamePattern = 'different_{resource}'
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty; $result.calls.Count | Should Be 0
        $result.bytes | Should Be $result.originalBytes
    }

    It 'accepts the exact original pattern for legacy VerifyOnly without rewriting its state' {
        $fixture = New-BootstrapCliFixture -Legacy; $script:bootstrapFixture = $fixture
        Set-BootstrapRecordedFixture -Fixture $fixture -Status Verified
        $fixture.inputOverride.IdentityNamePattern = 'mi-azsdk-sample-{resource}-wus3'
        $fixture.inputOverride.Location = 'westus3'; $fixture.noTemplates = $true
        $result = Invoke-IsolatedBootstrap -VerifyOnly
        $result.failure | Should BeNullOrEmpty; $result.bytes | Should Be $result.originalBytes
        $result.lockExists | Should Be $false; $result.mutations.Count | Should Be 0
        @($result.calls | Where-Object { $_ -match '^(bicep|deployment sub)' }).Count | Should Be 0
    }

    It 'does not turn a default pattern into permission to recreate a recorded legacy set' {
        $fixture = New-BootstrapCliFixture -Legacy; $script:bootstrapFixture = $fixture
        Set-BootstrapRecordedFixture -Fixture $fixture -Status Verified
        $fixture.inputOverride.IdentityNamePattern = 'mi-azsdk-sample-{resource}-wus3'
        $fixture.inputOverride.Location = 'westus3'
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'verification-only'
        $result.calls.Count | Should Be 0; $result.mutations.Count | Should Be 0
        $result.bytes | Should Be $result.originalBytes
    }

    It 'accepts arbitrary prefix/suffix conventions independent of the explicit region: <Pattern>' -TestCases @(
        @{ Pattern = '{resource}' }, @{ Pattern = 'Blue{resource}42' }, @{ Pattern = 'team_{resource}_uksouth' },
        @{ Pattern = '9{resource}__' }, @{ Pattern = 'mi-azsdk-sample-{resource}-wus3' }
    ) {
        param($Pattern)
        $script:bootstrapFixture = New-BootstrapCliFixture -Region westus3 -Pattern $Pattern
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.identityNamePattern | Should BeExactly $Pattern
        $result.state.location | Should BeExactly 'westus3'; $result.mutations.Count | Should Be 0
    }

    It 'uses the original default pattern for a NEW generation only when all exact names are absent' {
        $fixture = New-BootstrapCliFixture -Region westus3 -Pattern 'mi-azsdk-sample-{resource}-wus3'; $script:bootstrapFixture = $fixture
        $fixture.useDefaultPattern = $true
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $result.state.schemaVersion | Should Be 3
        $result.state.identityResourceGroup | Should Not Be 'rg-azsdk-sample-identities-wus3'
        $fixture.identityListCalls | Should Be 1; $result.mutations.Count | Should Be 0
    }

    It 'binds changed schema-3 <Field> before Azure and preserves every state byte' -TestCases @(
        @{ Field = 'location'; Value = 'eastus2' }, @{ Field = 'identityNamePattern'; Value = 'other_{resource}' },
        @{ Field = 'identityResourceGroup'; Value = 'rg-other' }
    ) {
        param($Field, $Value)
        $fixture = $script:bootstrapFixture; Set-BootstrapPreviewFixture -Fixture $fixture
        $fixture.state[$Field] = $Value
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Not BeNullOrEmpty; $result.calls.Count | Should Be 0; $result.bytes | Should Be $result.originalBytes
    }

    It 'rejects each existing expanded name across ANY group without creating a hashed-RG replacement: <Purpose>' -TestCases @(
        @{ Purpose = 'project' }, @{ Purpose = 'account' }, @{ Purpose = 'search' }, @{ Purpose = 'function' }
    ) {
        param($Purpose)
        $fixture = $script:bootstrapFixture
        $existing = @{} + $fixture.live[$Purpose]
        $existing.id = $existing.id.Replace($fixture.groupName, 'another-owned-group'); $existing.name = $existing.id.Split('/')[-1].ToUpperInvariant()
        $fixture.identityList.value = @($existing)
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'already exists'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
        @($result.calls | Where-Object { $_ -match '^deployment sub ' }).Count | Should Be 0
    }

    It 'refuses default names already present in the original legacy group without adopting it' {
        $fixture = New-BootstrapCliFixture -Region westus3 -Pattern 'mi-azsdk-sample-{resource}-wus3'; $script:bootstrapFixture = $fixture
        $existing = @{} + $fixture.live.project
        $existing.id = $existing.id.Replace($fixture.groupName, 'rg-azsdk-sample-identities-wus3'); $existing.name = 'mi-azsdk-sample-project-wus3'
        $fixture.identityList.value = @($existing)
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'already exists'; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }

    It 'rejects malformed or duplicate protected identity-name metadata: <Fault>' -TestCases @(
        @{ Fault = 'null list' }, @{ Fault = 'non-array' }, @{ Fault = 'duplicate' }, @{ Fault = 'foreign subscription' },
        @{ Fault = 'name mismatch' }, @{ Fault = 'wrong type' }, @{ Fault = 'error' }
    ) {
        param($Fault)
        $fixture = $script:bootstrapFixture
        $item = @{ id = ($fixture.groupId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/unrelated'); name = 'unrelated'; type = 'Microsoft.ManagedIdentity/userAssignedIdentities' }
        $fixture.identityList.value = @($item)
        switch ($Fault) {
            'null list' { $fixture.identityList = $null }
            'non-array' { $fixture.identityList.value = @{} }
            'duplicate' { $fixture.identityList.value = @($item, $item) }
            'foreign subscription' { $item.id = $item.id.Replace($fixture.subscriptionId, 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee') }
            'name mismatch' { $item.name = 'other' }
            'wrong type' { $item.type = 'Microsoft.Storage/storageAccounts' }
            'error' { $fixture.identityList.error = @{ code = 'Denied' } }
        }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Not BeNullOrEmpty; $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }

    It 'rejects unsafe identity-name pagination without following it: <Tail>' -TestCases @(
        @{ Tail = 'foreign host' }, @{ Tail = 'foreign scope' }, @{ Tail = 'filter' }, @{ Tail = 'API version' }, @{ Tail = 'loop' }
    ) {
        param($Tail)
        $fixture = $script:bootstrapFixture
        $base = 'https://management.azure.com' + $fixture.scope + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities?api-version=2023-01-31'
        $fixture.identityList.nextLink = switch ($Tail) {
            'foreign host' { $base.Replace('management.azure.com', 'example.invalid') }
            'foreign scope' { $base.Replace($fixture.subscriptionId, 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee') }
            'filter' { $base + '&$filter=name' }; 'API version' { $base.Replace('2023-01-31', '2020-01-01') }; 'loop' { $base }
        }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'pagination'; $fixture.identityListCalls | Should Be 1
        $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }

    It 'checks all pages and rejects an existing name on the second page' {
        $fixture = $script:bootstrapFixture; $item = @{} + $fixture.live.function; $item.name = $item.id.Split('/')[-1]
        $next = 'https://management.azure.com' + $fixture.scope + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities?api-version=2023-01-31&$skiptoken=second'
        $fixture.identityResponses = @(@{ value = @(); nextLink = $next }, @{ value = @($item); nextLink = $null })
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'already exists'; $fixture.identityListCalls | Should Be 2; $result.state | Should BeNullOrEmpty
    }

    It 'accepts unrelated exact metadata on multiple subscription-bound pages' {
        $fixture = $script:bootstrapFixture
        $one = @{ id = ($fixture.groupId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/unrelated_one'); name = 'unrelated_one'; type = 'Microsoft.ManagedIdentity/userAssignedIdentities' }
        $two = @{ id = ($fixture.groupId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/unrelated_two'); name = 'unrelated_two'; type = 'Microsoft.ManagedIdentity/userAssignedIdentities' }
        $next = 'https://management.azure.com' + $fixture.scope + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities?api-version=2023-01-31&$skiptoken=second'
        $fixture.identityResponses = @(@{ value = @($one); nextLink = $next }, @{ value = @($two); nextLink = $null })
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should BeNullOrEmpty; $fixture.identityListCalls | Should Be 2
        $result.state.status | Should Be 'Previewed'; $result.mutations.Count | Should Be 0
    }

    It 'rejects duplicate identity IDs spanning protected pages' {
        $fixture = $script:bootstrapFixture
        $item = @{ id = ($fixture.groupId + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/unrelated'); name = 'unrelated'; type = 'Microsoft.ManagedIdentity/userAssignedIdentities' }
        $next = 'https://management.azure.com' + $fixture.scope + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities?api-version=2023-01-31&$skiptoken=second'
        $fixture.identityResponses = @(@{ value = @($item); nextLink = $next }, @{ value = @($item); nextLink = $null })
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Match 'duplicate'; $fixture.identityListCalls | Should Be 2
        $result.state | Should BeNullOrEmpty; $result.mutations.Count | Should Be 0
    }

    It 'rechecks name absence immediately before a create and refuses an intervening existing name' {
        $fixture = $script:bootstrapFixture; Set-BootstrapPreviewFixture -Fixture $fixture
        $item = @{} + $fixture.live.search; $item.name = $item.id.Split('/')[-1]
        $fixture.identityResponses = @(@{ value = @(); nextLink = $null }, @{ value = @($item); nextLink = $null })
        $result = Invoke-IsolatedBootstrap -Apply
        $result.failure | Should Match 'already exists'; $fixture.identityListCalls | Should Be 2
        $result.state.status | Should Be 'Previewed'; $result.mutations.Count | Should Be 0
    }

    It 'rejects compiled naming substitutions and actual resource-ID seeds that differ: <Fault>' -TestCases @(
        @{ Fault = 'module pattern' }, @{ Fault = 'identity naming' }, @{ Fault = 'project role seed' }
    ) {
        param($Fault)
        $fixture = $script:bootstrapFixture
        switch ($Fault) {
            'module pattern' { $fixture.compiled.resources.sharedIdentities.properties.parameters.identityNamePattern.value = 'forced-{resource}' }
            'identity naming' { $fixture.compiled.resources.sharedIdentities.properties.template.resources.managedIdentities.name = "[concat('forced-', variables('identityPurposes')[copyIndex()])]" }
            'project role seed' { $fixture.compiled.variables.projectIdentityResourceId = "[parameters('identityNamePattern')]" }
        }
        $result = Invoke-IsolatedBootstrap
        $result.failure | Should Not BeNullOrEmpty; $result.state | Should BeNullOrEmpty
        @($result.calls | Where-Object { $_ -match '^deployment sub ' }).Count | Should Be 0; $result.mutations.Count | Should Be 0
    }
}