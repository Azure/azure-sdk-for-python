# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot 'TestHelpers.ps1')

Describe 'Endpoint-specific exact test profile execution' {
    BeforeEach {
        $script:root = Join-Path $TestDrive ([guid]::NewGuid().ToString())
        New-ProjectRunnerFixture $root
        $script:first = New-ProfileFixture
        $script:second = New-ProfileFixture -Case two
        $script:endpoint = 'https://example.services.ai.azure.com/api/projects/staging'
        $script:arguments = @{
            ProfilesJson = New-RegistryFixture @($first, $second)
            TestIdsJson = ConvertTo-Json -InputObject @($first.TestId, $second.TestId) -Compress
            FoundryProjectEndpoint = $endpoint; ExpectedEndpointHash = Get-TestProjectEndpointHash $endpoint
            Values = @{ TEST_VALUE = 'original=value' }; PackageRoot = $root
            ResolverScript = Join-Path $root 'resolver.ps1'; RunnerScript = Join-Path $root 'runner.ps1'
            ResultsDirectory = Join-Path $root 'results'
        }
    }

    It 'previews exact assigned tests without live execution, collection, or values in output' {
        $plan = @(& $projectRunner @arguments)
        $plan.Count | Should Be 2
        ($plan | ConvertTo-Json -Depth 10) | Should Not Match 'original=value|https://'
        (Test-Path -LiteralPath (Join-Path $root 'events.txt')) | Should Be $false
    }

    It 'preflights all nodes before separate live invocations and preserves environment strings' {
        & $projectRunner @arguments -Run -ConfirmLive | Out-Null
        $events = @(Get-Content -LiteralPath (Join-Path $root 'events.txt'))
        $events.Count | Should Be 4
        $events[0] | Should Match '^preview:'
        $events[1] | Should Match '^preview:'
        $events[2] | Should Match '^run:'
        $runs = @(Get-Content -LiteralPath (Join-Path $root 'runs.jsonl') | ForEach-Object { $_ | ConvertFrom-Json })
        $runs.Count | Should Be 2
        $runs[0].JUnit | Should Not Be $runs[1].JUnit
        ($runs[0].Environment -contains 'MULTIPLE_REQUIRED=original=value') | Should Be $true
        ($runs[0].Environment -contains "FOUNDRY_PROJECT_ENDPOINT=$endpoint") | Should Be $true
        (Test-Path -LiteralPath $runs[0].EnvFile) | Should Be $false
        (Get-Content -LiteralPath (Join-Path $root 'results/test-profile-summary.md') -Raw) | Should Not Match 'original=value|https://'
    }

    It 'runs only the current endpoint membership and skips globally disabled tests' {
        $second.Enabled = $false
        $arguments.ProfilesJson = New-RegistryFixture @($first, $second)
        $plan = @(& $projectRunner @arguments)
        $plan.Count | Should Be 1
        $plan[0].TestId | Should Be $first.TestId
        $arguments.FoundryProjectEndpoint = 'https://example.services.ai.azure.com/api/projects/other'
        { & $projectRunner @arguments } | Should Throw 'does not match this pipeline'
    }

    It 'refuses unregistered, duplicate, scalar memberships and missing values' {
        foreach ($ids in @('"scalar"', '[]', '["missing"]')) {
            $arguments.TestIdsJson = $ids
            $caught = $null
            try { & $projectRunner @arguments } catch { $caught = $_ }
            $caught | Should Not BeNullOrEmpty
        }
        $arguments.TestIdsJson = ConvertTo-Json -InputObject @($first.TestId, $first.TestId)
        { & $projectRunner @arguments } | Should Throw 'duplicates'
        $arguments.TestIdsJson = ConvertTo-Json -InputObject @($first.TestId)
        $arguments.Values = @{}
        { & $projectRunner @arguments } | Should Throw 'required project value is missing'
    }

    It 'requires explicit live approval and rejects unresolved mappings' {
        { & $projectRunner @arguments -Run } | Should Throw 'ConfirmLive'
        $arguments.Values.TEST_VALUE = '$(TEST_VALUE)'
        { & $projectRunner @arguments } | Should Throw 'unmapped'
    }

    It 'fails closed when an exact test disappears instead of falling back to a wildcard' {
        '[]' | Set-Content -LiteralPath (Join-Path $root 'nodes.json')
        { & $projectRunner @arguments -Run -ConfirmLive } | Should Throw 'exactly one collected'
        (Test-Path -LiteralPath (Join-Path $root 'runs.jsonl')) | Should Be $false
    }

    It 'does not start any test when preflight discovers missing harness values' {
        $null = New-Item -ItemType File -Path (Join-Path $root 'missing-value')
        { & $projectRunner @arguments -Run -ConfirmLive } | Should Throw 'sample/harness'
        (Test-Path -LiteralPath (Join-Path $root 'runs.jsonl')) | Should Be $false
    }

    It 'continues other profiles after a failure without echoing sensitive exceptions' {
        $null = New-Item -ItemType File -Path (Join-Path $root 'fail-first')
        $caught = $null
        try { & $projectRunner @arguments -Run -ConfirmLive } catch { $caught = $_ }
        $caught.Exception.Message | Should Match 'test profiles failed'
        $caught.Exception.Message | Should Not Match 'sensitive-failure-details'
        @(Get-Content -LiteralPath (Join-Path $root 'runs.jsonl')).Count | Should Be 2
        $summary = Get-Content -LiteralPath (Join-Path $root 'results/test-profile-summary.md') -Raw
        $summary | Should Match 'failed'
        $summary | Should Match 'succeeded'
    }

    It 'uses dictionary enumeration safely for variable references named Keys or Values' {
        $first.Environment[1].Variable = 'KEYS'
        $second.Environment[1].Variable = 'VALUES'
        $arguments.ProfilesJson = New-RegistryFixture @($first, $second)
        $arguments.Values = [ordered]@{ KEYS = 'key-secret'; VALUES = 'value-secret' }
        $plan = @(& $projectRunner @arguments)
        $plan.Count | Should Be 2
        ($plan | ConvertTo-Json -Depth 10) | Should Not Match 'key-secret|value-secret'
    }

    It 'keeps case-distinct exact IDs and their environments separate during execution' {
        $second.TestId = $first.TestId.Replace('variant-one', 'variant-ONE')
        $second.SamplePath = 'samples/second/sample_multiple.py'
        $second.Environment[1].Variable = 'SECOND_VALUE'
        $arguments.ProfilesJson = New-RegistryFixture @($first, $second)
        $arguments.TestIdsJson = ConvertTo-Json -InputObject @($first.TestId, $second.TestId)
        $arguments.Values.SECOND_VALUE = 'second=value'
        @(@{ NodeId = $first.TestId }, @{ NodeId = $second.TestId }) | ConvertTo-Json |
            Set-Content -LiteralPath (Join-Path $root 'nodes.json')
        & $projectRunner @arguments -Run -ConfirmLive | Out-Null
        $runs = @(Get-Content -LiteralPath (Join-Path $root 'runs.jsonl') | ForEach-Object { $_ | ConvertFrom-Json })
        $runs[0].Node | Should Be $first.TestId
        ($runs[0].Node -ceq $first.TestId) | Should Be $true
        ($runs[1].Node -ceq $second.TestId) | Should Be $true
        ($runs[0].Environment -contains 'MULTIPLE_REQUIRED=original=value') | Should Be $true
        ($runs[1].Environment -contains 'MULTIPLE_REQUIRED=second=value') | Should Be $true
    }

    It 'does not classify skipped, missing, collection-only, or stale JUnit as successful tests' {
        foreach ($marker in @('collect-only', 'skip-test', 'no-junit')) {
            $null = New-Item -ItemType File -Path (Join-Path $root $marker)
            # Place an old passing result at the expected location to verify it is removed.
            $null = New-Item -ItemType Directory -Path $arguments.ResultsDirectory -Force
            $key = (Get-TestProfileDigest $first.TestId).Substring(0, 16)
            '<testsuite tests="1"><testcase classname="tests.samples.test_samples" name="test_multiple[variant-one]" /></testsuite>' |
                Set-Content -LiteralPath (Join-Path $arguments.ResultsDirectory "test-junit-$key.xml")
            { & $projectRunner @arguments -Run -ConfirmLive } | Should Throw 'test profiles failed'
            $summary = Get-Content -LiteralPath (Join-Path $root 'results/test-profile-summary.md') -Raw
            $summary | Should Not Match 'succeeded'
            Remove-Item -LiteralPath (Join-Path $root $marker)
        }
    }

    It 'rejects inherited pytest overrides before collection or live execution' {
        $original = $env:PYTEST_ADDOPTS
        try {
            $env:PYTEST_ADDOPTS = '--collect-only'
            { & $projectRunner @arguments -Run -ConfirmLive } | Should Throw 'inherited PYTEST'
            (Test-Path -LiteralPath (Join-Path $root 'events.txt')) | Should Be $false
        } finally { $env:PYTEST_ADDOPTS = $original }
    }

    It 'rejects a passing JUnit testcase for a different exact node' {
        $junit = Join-Path $root 'wrong-test.xml'
        '<testsuite tests="1"><testcase classname="tests.samples.test_samples" name="test_multiple[OTHER]" /></testsuite>' |
            Set-Content -LiteralPath $junit
        { Assert-TestProfileJUnitResult $first.TestId $junit } | Should Throw 'does not match'
    }
}