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

Describe 'Foundry account quota preflight' {
    BeforeEach {
        $script:accountQuota = @{ name = @{ value = 'AccountCount' }; currentValue = 3; limit = 200; unit = 'Count' }
        $script:modelQuota = @{ name = @{ value = 'OpenAI.GlobalStandard.gpt-4.1' }; currentValue = 0; limit = 1000 }
    }

    It 'accepts available account quota independently of model quota' {
        @(Assert-SampleAccountQuota -Usages @($script:modelQuota, $script:accountQuota) -Location 'eastus').Count | Should Be 0
    }

    It 'accepts exactly one remaining account slot' {
        $script:accountQuota.currentValue = 199
        Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'westus3'
    }

    It 'accepts numeric JSON doubles and an explicitly included status' {
        $script:accountQuota.currentValue = [double] 3
        $script:accountQuota.limit = [double] 200
        $script:accountQuota.status = 'Included'
        Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'westus3'
    }

    It 'rejects exhausted account quota even when model quota is available' {
        $script:accountQuota.currentValue = 200
        { Assert-SampleAccountQuota -Usages @($script:modelQuota, $script:accountQuota) -Location 'eastus' } |
            Should Throw "Insufficient Cognitive Services account quota in 'eastus'"
    }

    It 'rejects account quota already in overage' {
        $script:accountQuota.currentValue = 201
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'No resources were created'
    }

    It 'rejects blocked account quota even when the numeric limit has room' {
        $script:accountQuota.status = 'Blocked'
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'status: Blocked'
    }

    It 'rejects unknown account quota status' {
        $script:accountQuota.status = 'Unknown'
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'status: Unknown'
    }

    It 'rejects an empty usage response' {
        { Assert-SampleAccountQuota -Usages @() -Location 'eastus' } | Should Throw 'Cannot verify'
    }

    It 'rejects a missing account quota instead of treating model quota as account quota' {
        { Assert-SampleAccountQuota -Usages @($script:modelQuota) -Location 'eastus' } | Should Throw 'Cannot verify'
    }

    It 'rejects ambiguous duplicate account quota entries' {
        { Assert-SampleAccountQuota -Usages @($script:accountQuota, $script:accountQuota) -Location 'eastus' } | Should Throw 'Cannot verify'
    }

    It 'rejects a missing current count rather than assuming zero' {
        $script:accountQuota.Remove('currentValue')
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'Cannot verify'
    }

    It 'rejects a missing quota limit' {
        $script:accountQuota.Remove('limit')
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'Cannot verify'
    }

    It 'rejects nonnumeric usage values' {
        $script:accountQuota.currentValue = 'not-a-number'
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'Cannot verify'
    }

    It 'rejects a negative usage value' {
        $script:accountQuota.currentValue = -1
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'Cannot verify'
    }

    It 'rejects a nonfinite quota limit' {
        $script:accountQuota.limit = [double]::PositiveInfinity
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'Cannot verify'
    }

    It 'rejects a quota with the wrong unit' {
        $script:accountQuota.unit = 'CountPerSecond'
        { Assert-SampleAccountQuota -Usages @($script:accountQuota) -Location 'eastus' } | Should Throw 'Cannot verify'
    }
}

Describe 'Secret-safe ARM error diagnostics' {
    It 'extracts nested ARM error codes without returning messages or credentials' {
        $details = @{ error = @{ code = 'DeploymentFailed'; message = 'Bearer secret-placeholder'; details = @(
            @{ code = 'BadRequest'; message = 'github_pat_unit_test_placeholder'; request = @{ code = 'NotAnError' } }
        ) } }
        $codes = @(Get-SampleAzureErrorCodes -ErrorDetails $details)
        ($codes -join ',') | Should Be 'BadRequest,DeploymentFailed'
    }

    It 'deduplicates error codes' {
        $details = @{ code = 'DeploymentFailed'; details = @(@{ code = 'BadRequest' }, @{ code = 'BadRequest' }) }
        (@(Get-SampleAzureErrorCodes -ErrorDetails $details) -join ',') | Should Be 'BadRequest,DeploymentFailed'
    }

    It 'does not treat raw text as an error code' {
        @(Get-SampleAzureErrorCodes -ErrorDetails 'Bearer secret-placeholder').Count | Should Be 0
    }

    It 'rejects token-shaped code fields' {
        @(Get-SampleAzureErrorCodes -ErrorDetails @{ code = 'github_pat_unit_test_placeholder' }).Count | Should Be 0
        @(Get-SampleAzureErrorCodes -ErrorDetails @{ code = 'ghp_UnitTestPlaceholder' }).Count | Should Be 0
    }

    It 'rejects multiline code fields' {
        @(Get-SampleAzureErrorCodes -ErrorDetails @{ code = "BadRequest`nBearer secret-placeholder" }).Count | Should Be 0
    }

    It 'handles absent ARM error details' {
        @(Get-SampleAzureErrorCodes -ErrorDetails $null).Count | Should Be 0
    }

    It 'persists only error codes and resource identifiers from failed deployments' {
        $owner = '0123456789abcdef0123456789abcdef'
        $plan = @{
            schemaVersion = 1
            definitionId = $(if ($env:SYSTEM_DEFINITIONID) { $env:SYSTEM_DEFINITIONID } else { '8392' })
            buildId = $(if ($env:BUILD_BUILDID) { $env:BUILD_BUILDID } else { '12345' })
            jobAttempt = '1'
            ownerToken = $owner
        }
        $plan['resourceGroup'] = 'azsdk-samples-{0}-{1}-1-01234567' -f $plan.definitionId, $plan.buildId
        $state = @{ plan = $plan; subscriptionId = '00000000-0000-0000-0000-000000000000' }
        Mock Invoke-SampleAzure {
            param($Arguments, $Sensitive)
            if (-not $Sensitive) { throw 'Deployment diagnostics must suppress raw CLI errors.' }
            if ($Arguments[2] -eq 'list') {
                return @(@{ name = 'sample-resources'; state = 'Failed' })
            }
            if ($Arguments[2] -eq 'show') {
                return @{ code = 'DeploymentFailed'; message = 'Bearer secret-placeholder'; details = @(@{ code = 'BadRequest' }) }
            }
            return @(@{
                resourceId = '/subscriptions/placeholder/resourceGroups/run/providers/Microsoft.CognitiveServices/accounts/account/projects/project/connections/mcp'
                resourceType = 'Microsoft.CognitiveServices/accounts/projects/connections'
                error = '{"error":{"code":"BadRequest","message":"github_pat_unit_test_placeholder","request":{"credentials":"secret-placeholder"}}}'
            })
        }
        $path = Join-Path $TestDrive 'deployment-diagnostics.json'
        Save-SampleDeploymentDiagnostics -State $state -OutputPath $path
        $text = Get-Content -LiteralPath $path -Raw
        $text.Contains('DeploymentFailed') | Should Be $true
        $text.Contains('BadRequest') | Should Be $true
        $text.Contains('secret-placeholder') | Should Be $false
        $text.Contains('github_pat_') | Should Be $false
        $text.Contains('message') | Should Be $false
        $text.Contains('credentials') | Should Be $false
        $text.Contains('request') | Should Be $false
    }
}
