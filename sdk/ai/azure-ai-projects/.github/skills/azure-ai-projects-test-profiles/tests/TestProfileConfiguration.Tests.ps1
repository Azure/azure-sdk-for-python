# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot 'TestHelpers.ps1')

Describe 'Independent test-profile configuration' {
    It 'previews and saves an untested profile without a build ID or live execution' {
        $profileFile = Join-Path $TestDrive 'profile.json'
        $registryFile = Join-Path $TestDrive 'registry.json'
        New-ProfileFixture | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $profileFile
        $preview = & $setProfile -ProfileFile $profileFile -RegistryFile $registryFile
        $preview.Execution | Should Be 'Not run (configuration only)'
        $preview.Applied | Should Be $false
        (Test-Path -LiteralPath $registryFile) | Should Be $false
        $saved = & $setProfile -ProfileFile $profileFile -RegistryFile $registryFile -Run -ConfirmSave -ExpectedDigest $preview.ExpectedDigest
        $saved.Applied | Should Be $true
        $registry = Get-Content -LiteralPath $registryFile -Raw | ConvertFrom-Json
        $registry.Profiles.Count | Should Be 1
        $registry.Profiles[0].DefinitionId | Should BeNullOrEmpty
        $registry.Profiles[0].Environment[0].Source | Should Be 'ProjectEndpoint'
    }

    It 'requires explicit save approval and detects edited profile content after preview' {
        $profileFile = Join-Path $TestDrive 'edited.json'
        $registryFile = Join-Path $TestDrive 'edited-registry.json'
        $testProfile = New-ProfileFixture
        $testProfile | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $profileFile
        $arguments = @{ ProfileFile = $profileFile; RegistryFile = $registryFile }
        $plan = & $setProfile @arguments
        { & $setProfile @arguments -Run } | Should Throw 'Preview first'
        $testProfile.Enabled = $false
        $testProfile | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $profileFile
        { & $setProfile @arguments -Run -ConfirmSave -ExpectedDigest $plan.ExpectedDigest } | Should Throw 'changed since preview'
        (Test-Path -LiteralPath $registryFile) | Should Be $false
    }

    It 'prevents duplicate profiles and updates only the matching exact TestId' {
        $profileFile = Join-Path $TestDrive 'update.json'
        $registryFile = Join-Path $TestDrive 'update-registry.json'
        $first = New-ProfileFixture
        $second = New-ProfileFixture -Case two
        New-RegistryFixture @($first, $second) | Set-Content -LiteralPath $registryFile
        $first.Enabled = $false
        $first | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $profileFile
        $arguments = @{ ProfileFile = $profileFile; RegistryFile = $registryFile }
        { & $setProfile @arguments } | Should Throw 'already has a profile'
        $preview = & $setProfile @arguments -Update
        & $setProfile @arguments -Update -Run -ConfirmSave -ExpectedDigest $preview.ExpectedDigest | Out-Null
        $registry = Get-Content -LiteralPath $registryFile -Raw | ConvertFrom-Json
        $registry.Profiles.Count | Should Be 2
        ($registry.Profiles | Where-Object { $_.TestId -ceq $first.TestId }).Enabled | Should Be $false
        ($registry.Profiles | Where-Object { $_.TestId -ceq $second.TestId }).Enabled | Should Be $true
    }

    It 'rejects embedded values, endpoint overrides, pipeline IDs, wildcards, and parent paths' {
        foreach ($failure in @('value', 'endpoint', 'pipeline', 'wildcard', 'path', 'duplicate')) {
            $testProfile = New-ProfileFixture
            if ($failure -eq 'value') { $testProfile.Environment[1] | Add-Member -NotePropertyName Value -NotePropertyValue 'must-not-persist' }
            if ($failure -eq 'endpoint') { $testProfile.Environment[0].Source = 'Variable' }
            if ($failure -eq 'pipeline') { $testProfile | Add-Member -NotePropertyName DefinitionId -NotePropertyValue 8392 }
            if ($failure -eq 'wildcard') { $testProfile.TestId = 'tests/samples/test_samples.py::test_*' }
            if ($failure -eq 'path') { $testProfile.SamplePath = 'samples/../outside.py' }
            if ($failure -eq 'duplicate') { $testProfile.Environment += $testProfile.Environment[1] }
            $caught = $null
            try { Assert-TestProfile $testProfile } catch { $caught = $_ }
            $caught | Should Not BeNullOrEmpty
            $caught.Exception.Message | Should Not Match 'must-not-persist'
        }
    }

    It 'rejects duplicate exact test IDs and supports literal parameter brackets' {
        $testProfile = New-ProfileFixture
        $testProfile.TestId = 'tests/samples/test_samples.py::test_multiple[variant-[one,*]]'
        $null = ConvertFrom-TestProfileRegistry (New-RegistryFixture @($testProfile))
        { ConvertFrom-TestProfileRegistry (New-RegistryFixture @($testProfile, $testProfile)) } | Should Throw 'one profile'
    }

    It 'refuses profile-controlled collection mode, plugins, interpreter paths, and recording flags' {
        foreach ($name in @('PYTEST_ADDOPTS', 'PYTEST_PLUGINS', 'PYTHONPATH', 'PATH', 'AZURE_SKIP_LIVE_RECORDING')) {
            $testProfile = New-ProfileFixture
            $testProfile.Environment[1].Name = $name
            { Assert-TestProfile $testProfile } | Should Throw 'execution controls'
        }
    }

    It 'saves metadata to ADO Library without touching endpoint secrets or creating a pipeline' {
        $profileFile = Join-Path $TestDrive 'ado-profile.json'
        New-ProfileFixture | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $profileFile
        $state = [pscustomobject]@{ Group = New-ProfileGroupFixture; Calls = [Collections.Generic.List[object]]::new(); Saved = $null; IgnoreSave = $false }
        $arguments = @{ ProfileFile = $profileFile; RegistryGroupId = 12; BearerToken = 'ado-token'; RequestInvoker = New-GroupRequestFixture $state }
        $preview = & $setProfile @arguments
        ($state.Calls.Method -join ',') | Should Be 'Get'
        $actual = & $setProfile @arguments -Run -ConfirmSave -ExpectedDigest $preview.ExpectedDigest
        $actual.Applied | Should Be $true
        ($state.Calls.Method -join ',') | Should Be 'Get,Get,Get,Put'
        $state.Calls[3].Uri | Should Be 'https://dev.azure.com/azure-sdk/_apis/distributedtask/variablegroups/12?api-version=7.1'
        $state.Saved.variables.OTHER_METADATA.value | Should Be 'preserve'
        ($state.Saved | ConvertTo-Json -Depth 20) | Should Not Match 'ado-token|FOUNDRY_PROJECT_ENDPOINT.*https'
    }

    It 'refuses metadata-group secrets and stale remote reviews without mutation' {
        $profileFile = Join-Path $TestDrive 'group-profile.json'
        New-ProfileFixture | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $profileFile
        $state = [pscustomobject]@{ Group = New-ProfileGroupFixture; Calls = [Collections.Generic.List[object]]::new(); Saved = $null; IgnoreSave = $false }
        $arguments = @{ ProfileFile = $profileFile; RegistryGroupId = 12; BearerToken = 'ado-token'; RequestInvoker = New-GroupRequestFixture $state }
        $preview = & $setProfile @arguments
        $state.Group.modifiedOn = '2026-01-02T00:00:00Z'
        { & $setProfile @arguments -Run -ConfirmSave -ExpectedDigest $preview.ExpectedDigest } | Should Throw 'changed since preview'
        $state.Group.variables | Add-Member -NotePropertyName SECRET_ENTRY -NotePropertyValue @{ isSecret = $true; value = $null }
        { & $setProfile @arguments } | Should Throw 'metadata-only'
        @($state.Calls | Where-Object { $_.Method -ne 'Get' }).Count | Should Be 0
    }

    It 'does not claim success when ADO does not confirm the metadata save' {
        $profileFile = Join-Path $TestDrive 'ignored-profile.json'
        New-ProfileFixture | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $profileFile
        $state = [pscustomobject]@{ Group = New-ProfileGroupFixture; Calls = [Collections.Generic.List[object]]::new(); Saved = $null; IgnoreSave = $true }
        $arguments = @{ ProfileFile = $profileFile; RegistryGroupId = 12; BearerToken = 'ado-token'; RequestInvoker = New-GroupRequestFixture $state }
        $preview = & $setProfile @arguments
        { & $setProfile @arguments -Run -ConfirmSave -ExpectedDigest $preview.ExpectedDigest } | Should Throw 'did not confirm'
    }

    It 'generates one no-input wrapper per normalized endpoint with no endpoint values in source' {
        $endpoint = 'https://example.services.ai.azure.com/api/projects/staging'
        $arguments = @{ FoundryProjectEndpoint = $endpoint; ProjectVariableGroup = 'project-staging'; ValueVariable = @('TEST_VALUE'); PackageRoot = $TestDrive }
        $preview = & $newPipeline @arguments
        (Test-Path -LiteralPath $preview.OutputPath) | Should Be $false
        $saved = & $newPipeline @arguments -Run -ConfirmWrite
        $saved.Applied | Should Be $true
        $yaml = Get-Content -LiteralPath $saved.OutputPath -Raw
        $yaml | Should Match 'trigger: none'
        $yaml | Should Match 'pr: none'
        $yaml | Should Match 'test-profile-project.yml'
        $yaml | Should Match 'TEST_VALUE'
        $yaml | Should Not Match 'https://|example.services|/staging|SourceBuildId'
        (& $newPipeline @arguments -FoundryProjectEndpoint ($endpoint + '/')).OutputPath | Should Be $saved.OutputPath
        { & $newPipeline @arguments -Run -ConfirmWrite } | Should Throw 'already has a wrapper'
    }

    It 'rejects insecure endpoint URLs, reserved mapping names, and group macro injection' {
        { Get-TestProjectEndpointHash 'http://example/api/projects/test' } | Should Throw 'HTTPS'
        { Get-TestProjectEndpointHash 'https://user:pass@example/api/projects/test' } | Should Throw 'HTTPS'
        { Get-TestProjectEndpointHash 'https://example/api/projects/test?secret=value' } | Should Throw 'HTTPS'
        { & $newPipeline -FoundryProjectEndpoint 'https://example/api/projects/test' -ProjectVariableGroup '$(BAD)' } | Should Throw 'plain ADO'
        { & $newPipeline -FoundryProjectEndpoint 'https://example/api/projects/test' -ProjectVariableGroup 'test' -ValueVariable FOUNDRY_PROJECT_ENDPOINT } | Should Throw 'ValueVariable'
    }
}