# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

Describe 'Offline deployment-plan defaults' {
    BeforeEach {
        $script:originalSubscription = $env:AZURE_SUBSCRIPTION_ID
        $script:originalTenant = $env:AZURE_TENANT_ID
        $script:originalQueue = $env:SAMPLE_QUEUE_NAME
        $env:AZURE_SUBSCRIPTION_ID = '11111111-1111-1111-1111-111111111111'
        $env:AZURE_TENANT_ID = '22222222-2222-2222-2222-222222222222'
        $env:SAMPLE_QUEUE_NAME = 'q1'
        $script:planDirectory = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
        $manifest = Join-Path $TestDrive 'selection.json'
        @{ schemaVersion = 1; tests = @(@{
            node_id = 'tests/samples/test_samples.py::TestSamples::test_agent_tools_samples[sample_agent_mcp_with_project_connection]'
            sample_path = 'samples/agents/tools/sample_agent_mcp_with_project_connection.py'
        }) } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifest -Encoding utf8
        $script:planArguments = @{
            SelectionManifest = $manifest
            OutputDirectory = $script:planDirectory
            QueueName = 'q1'
            DefinitionId = $(if ($env:SYSTEM_DEFINITIONID) { $env:SYSTEM_DEFINITIONID } else { '8392' })
            BuildId = $(if ($env:BUILD_BUILDID) { $env:BUILD_BUILDID } else { '12345' })
            JobAttempt = '1'
        }
        $script:planScript = Join-Path $PSScriptRoot '../New-SampleDeploymentPlan.ps1'
    }
    AfterEach {
        $env:AZURE_SUBSCRIPTION_ID = $script:originalSubscription
        $env:AZURE_TENANT_ID = $script:originalTenant
        $env:SAMPLE_QUEUE_NAME = $script:originalQueue
    }

    It 'defaults to the proven West US 3 GPT-5.2 version without contacting Azure' {
        & {
            function az { throw 'Offline planning must not contact Azure.' }
            & $script:planScript @script:planArguments
        }
        $plan = Get-Content -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') -Raw | ConvertFrom-Json -AsHashtable
        $plan.location | Should BeExactly ''
        $plan.identityResolution | Should BeExactly 'Pending'
        $plan.sharedIdentities.Count | Should Be 0
        $plan.projectIdentityName | Should Be 'mi-azsdk-sample-project-wus3'
        $plan.identityNamePattern | Should BeExactly 'mi-azsdk-sample-{resource}-wus3'
        $plan.sampleModel.name | Should Be 'gpt-5.2'
        $plan.sampleModel.version | Should Be '2025-12-11'
        $plan.sampleModel.sku | Should Be 'GlobalStandard'
        $plan.sampleModel.capacity | Should Be 10
        $plan.subscriptionId | Should Be $env:AZURE_SUBSCRIPTION_ID
        $plan.tenantId | Should Be $env:AZURE_TENANT_ID
    }

    It 'retains auto as an explicit model-version override' {
        & $script:planScript @script:planArguments -ModelVersion auto
        $plan = Get-Content -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') -Raw | ConvertFrom-Json -AsHashtable
        $plan.sampleModel.version | Should Be 'auto'
    }

    It 'accepts arbitrary MI pattern names without inventing Azure IDs or location' {
        & {
            function az { throw 'Offline planning must not contact Azure.' }
            & $script:planScript @script:planArguments -IdentityNamePattern 'custom_{resource}_blue'
        }
        $plan = Get-Content -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') -Raw | ConvertFrom-Json -AsHashtable
        $plan.location | Should BeExactly ''
        $plan.identityResolution | Should BeExactly 'Pending'
        $plan.sharedIdentities.Count | Should Be 0
        $plan.projectIdentityName | Should Be 'custom_project_blue'
        $plan.identityNamePattern | Should BeExactly 'custom_{resource}_blue'
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $plan.sharedIdentityNames[$purpose] | Should BeExactly "custom_${purpose}_blue"
        }
    }

    It 'retains the old concrete project-name argument for existing local callers' {
        & $script:planScript @script:planArguments -ProjectIdentityName mi-azsdk-unit-test-project-uksouth
        $plan = Get-Content -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') -Raw | ConvertFrom-Json -AsHashtable
        $plan.identityNamePattern | Should BeExactly 'mi-azsdk-unit-test-{resource}-uksouth'
        $plan.projectIdentityName | Should BeExactly 'mi-azsdk-unit-test-project-uksouth'
    }

    It 'rejects a conflicting concrete project name and pattern before saving a plan' {
        { & $script:planScript @script:planArguments -ProjectIdentityName mi-azsdk-unit-project-westus3 -IdentityNamePattern 'mi-azsdk-other-{resource}-westus3' } |
            Should Throw 'differs from the selected MI name pattern'
        Test-Path -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') | Should Be $false
    }

    It 'rejects invalid MI name patterns before saving a plan: <Label>' -TestCases @(
        @{ Label = 'empty'; Name = '' }, @{ Label = 'whitespace'; Name = ' ' },
        @{ Label = 'concrete MI'; Name = 'mi-azsdk-unit-project-westus3' },
        @{ Label = 'resource ID'; Name = '/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/elsewhere/providers/Microsoft.ManagedIdentity/userAssignedIdentities/example' },
        @{ Label = 'macro'; Name = '$(identityNamePattern)' }, @{ Label = 'shell text'; Name = 'mi-azsdk-{resource}-uksouth;Write-Host bad' },
        @{ Label = 'illegal punctuation'; Name = 'MI.test-{resource}-blue' },
        @{ Label = 'newline'; Name = "mi-azsdk-unit-{resource}-uksouth`n" },
        @{ Label = 'duplicate placeholder'; Name = 'mi-azsdk-{resource}-{resource}-uksouth' },
        @{ Label = 'unknown placeholder'; Name = 'mi-azsdk-unit-{Resource}-uksouth' },
        @{ Label = 'unknown extra placeholder'; Name = 'mi-azsdk-{set}-{resource}-uksouth' }
    ) {
        param($Label, $Name)
        & {
            function az { throw 'Offline planning must not contact Azure.' }
            { & $script:planScript @script:planArguments -IdentityNamePattern $Name } | Should Throw 'MI name pattern'
        }
        Test-Path -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') | Should Be $false
    }
}