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
            IdentityResourceGroup = 'rg-azsdk-identities-westus3-102826_164519'
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
        $plan.identityResourceGroup | Should BeExactly 'rg-azsdk-identities-westus3-102826_164519'
        $plan.ContainsKey('identityNamePattern') | Should Be $false
        $plan.ContainsKey('projectIdentityName') | Should Be $false
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

    It 'requires the identity resource group instead of a name pattern' {
        $arguments = @{} + $script:planArguments
        $arguments.Remove('IdentityResourceGroup')
        { & $script:planScript @arguments -IdentityNamePattern 'mi-azsdk-sample-{resource}-wus3' } | Should Throw
        Test-Path -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') | Should Be $false
    }

    It 'accepts any existing resource group name without inventing Azure IDs or location: <Name>' -TestCases @(
        @{ Name = 'rg-azsdk-identities-uksouth-010126_000000' }, @{ Name = 'Custom_RG.(blue)' }, @{ Name = 'a' }
    ) {
        param($Name)
        $arguments = @{} + $script:planArguments
        $arguments.IdentityResourceGroup = $Name
        & {
            function az { throw 'Offline planning must not contact Azure.' }
            & $script:planScript @arguments
        }
        $plan = Get-Content -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') -Raw | ConvertFrom-Json -AsHashtable
        $plan.location | Should BeExactly ''
        $plan.identityResolution | Should BeExactly 'Pending'
        $plan.sharedIdentities.Count | Should Be 0
        $plan.identityResourceGroup | Should BeExactly $Name
    }

    It 'rejects an invalid identity resource group before saving a plan: <Label>' -TestCases @(
        @{ Label = 'empty'; Name = '' }, @{ Label = 'whitespace'; Name = ' ' },
        @{ Label = 'resource ID'; Name = '/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/elsewhere' },
        @{ Label = 'macro'; Name = '$(identityResourceGroup)' }, @{ Label = 'shell text'; Name = 'rg-x;Write-Host bad' },
        @{ Label = 'path'; Name = '../rg' }, @{ Label = 'trailing period'; Name = 'rg-x.' },
        @{ Label = 'newline'; Name = "rg-x`n" }, @{ Label = 'oversized'; Name = ('a' * 91) }
    ) {
        param($Label, $Name)
        $arguments = @{} + $script:planArguments
        $arguments.IdentityResourceGroup = $Name
        & {
            function az { throw 'Offline planning must not contact Azure.' }
            { & $script:planScript @arguments } | Should Throw 'Invalid shared identity resource group'
        }
        Test-Path -LiteralPath (Join-Path $script:planDirectory 'deployment-plan.json') | Should Be $false
    }
}