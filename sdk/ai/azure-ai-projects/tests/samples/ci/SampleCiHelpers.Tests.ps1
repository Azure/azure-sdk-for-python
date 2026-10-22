# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot 'SampleCiHelpers.ps1')

Describe 'Run-owned ephemeral resource guard' {
    BeforeEach {
        $script:plan = @{
            schemaVersion = 1
            definitionId = $(if ($env:SYSTEM_DEFINITIONID) { $env:SYSTEM_DEFINITIONID } else { '8392' })
            buildId = $(if ($env:BUILD_BUILDID) { $env:BUILD_BUILDID } else { '12345' })
            jobAttempt = '1'
            ownerToken = '0123456789abcdef0123456789abcdef'
        }
        $script:plan['resourceGroup'] = 'azsdk-samples-{0}-{1}-1-01234567' -f $script:plan.definitionId, $script:plan.buildId
        $script:subscription = '00000000-0000-0000-0000-000000000000'
        $script:group = @{
            id = '/subscriptions/{0}/resourceGroups/{1}' -f $script:subscription, $script:plan.resourceGroup
            tags = Get-SampleOwnershipTags -Plan $script:plan
        }
    }

    It 'accepts only exact run ownership' {
        Assert-SampleResourceGroupOwnership -Plan $script:plan -ResourceGroup $script:group -SubscriptionId $script:subscription
    }

    It 'rejects an unrelated resource group name' {
        $script:plan.resourceGroup = 'production-resource-group'
        { Assert-SampleRunPlan -Plan $script:plan } | Should Throw 'run-owned ephemeral'
    }

    It 'rejects a different subscription' {
        { Assert-SampleResourceGroupOwnership -Plan $script:plan -ResourceGroup $script:group `
            -SubscriptionId '11111111-1111-1111-1111-111111111111' } | Should Throw 'outside the deployment state'
    }

    It 'rejects a missing ownership tag' {
        $script:group.tags.Remove('sample-ci-owner')
        { Assert-SampleResourceGroupOwnership -Plan $script:plan -ResourceGroup $script:group `
            -SubscriptionId $script:subscription } | Should Throw 'exact CI ownership tags'
    }

    It 'rejects an incorrect ownership tag' {
        $script:group.tags['sample-ci-owner'] = 'a-different-run'
        { Assert-SampleResourceGroupOwnership -Plan $script:plan -ResourceGroup $script:group `
            -SubscriptionId $script:subscription } | Should Throw 'exact CI ownership tags'
    }

    It 'rejects groups with no tags' {
        $script:group.Remove('tags')
        { Assert-SampleResourceGroupOwnership -Plan $script:plan -ResourceGroup $script:group `
            -SubscriptionId $script:subscription } | Should Throw 'without ownership tags'
    }

    It 'rejects malformed ownership metadata' {
        $script:plan.ownerToken = 'not-a-run-token'
        { Assert-SampleRunPlan -Plan $script:plan } | Should Throw 'Invalid CI run ownership'
    }
}

Describe 'GitHub MCP secret validation' {
    BeforeEach { $script:originalPat = $env:MCP_GITHUB_PAT }
    AfterEach { $env:MCP_GITHUB_PAT = $script:originalPat }

    It 'accepts a complete prefixed PAT without returning its value' {
        $env:MCP_GITHUB_PAT = 'github_pat_' + 'unit_test_placeholder'
        @(Assert-SampleMcpPat).Count | Should Be 0
    }

    It 'accepts a classic PAT prefix' {
        $env:MCP_GITHUB_PAT = 'ghp_' + 'UnitTestPlaceholder'
        @(Assert-SampleMcpPat).Count | Should Be 0
    }

    It 'rejects suffix-only tokens instead of adding a duplicate prefix' {
        $env:MCP_GITHUB_PAT = 'suffix-only-placeholder'
        { Assert-SampleMcpPat } | Should Throw 'complete GitHub PAT'
    }

    It 'rejects an undefined ADO macro' {
        $env:MCP_GITHUB_PAT = '$(MCP_GITHUB_PAT)'
        { Assert-SampleMcpPat } | Should Throw 'ADO secret'
    }

    It 'rejects a Bearer-prefixed value' {
        $env:MCP_GITHUB_PAT = 'Bearer github_pat_' + 'unit_test_placeholder'
        { Assert-SampleMcpPat } | Should Throw 'complete GitHub PAT'
    }
}

Describe 'Model availability preflight' {
    BeforeEach {
        $script:catalog = @(@{ model = @{
            name = 'gpt-4.1'; format = 'OpenAI'; version = '2025-04-14'; isDefaultVersion = $true
            skus = @(@{ name = 'GlobalStandard'; usageName = 'OpenAI.GlobalStandard.gpt-4.1';
                capacity = @{ minimum = 1; maximum = 100; step = 1 } })
        } })
    }

    It 'resolves a unique default model version and SKU' {
        $model = Resolve-SampleModel -Catalog $script:catalog -Name 'gpt-4.1' -Version 'auto' -Sku 'GlobalStandard' -Capacity 10
        $model.version | Should Be '2025-04-14'
        $model.usageName | Should Be 'OpenAI.GlobalStandard.gpt-4.1'
    }

    It 'rejects an unavailable model SKU' {
        { Resolve-SampleModel -Catalog $script:catalog -Name 'gpt-4.1' -Version 'auto' -Sku 'Standard' -Capacity 10 } |
            Should Throw 'unavailable'
    }

    It 'rejects an unavailable explicit version' {
        { Resolve-SampleModel -Catalog $script:catalog -Name 'gpt-4.1' -Version 'missing' -Sku 'GlobalStandard' -Capacity 10 } |
            Should Throw 'unavailable'
    }

    It 'rejects capacity outside the SKU limits' {
        { Resolve-SampleModel -Catalog $script:catalog -Name 'gpt-4.1' -Version 'auto' -Sku 'GlobalStandard' -Capacity 101 } |
            Should Throw 'SKU limits'
    }

    It 'rejects an ambiguous default version' {
        $other = @{ model = @{ name = 'gpt-4.1'; format = 'OpenAI'; version = 'another-default'; isDefaultVersion = $true } }
        { Resolve-SampleModel -Catalog @($script:catalog[0], $other) -Name 'gpt-4.1' -Version 'auto' -Sku 'GlobalStandard' -Capacity 10 } |
            Should Throw 'exactly one default'
    }
}
