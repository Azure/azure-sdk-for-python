# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot 'TestHelpers.ps1')
$repositoryPackage = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
. (Join-Path $repositoryPackage '.github/skills/azure-ai-projects-sample-validation/tests/TestHelpers.ps1')

Describe 'Profile runner integration with the unchanged sample runner' {
    It 'executes one synthetic exact node with its own environment and JUnit result without Azure access' {
        $root = Join-Path $TestDrive 'synthetic-profile-package'
        New-SyntheticPackage $root
        $testProfile = [pscustomobject]@{
            TestId = 'tests/samples/test_samples.py::test_unique[unique-case]'
            SamplePath = 'samples/unique/sample_unique.py'
            Enabled = $true
            Environment = @(
                [pscustomobject]@{ Name = 'FOUNDRY_PROJECT_ENDPOINT'; Source = 'ProjectEndpoint' }
                [pscustomobject]@{ Name = 'DIRECT_REQUIRED'; Source = 'Variable'; Variable = 'DIRECT_VALUE' }
                [pscustomobject]@{ Name = 'HELPER_REQUIRED'; Source = 'Variable'; Variable = 'HELPER_VALUE' }
                [pscustomobject]@{ Name = 'HARNESS_VALUE'; Source = 'Variable'; Variable = 'HARNESS_VALUE' }
                [pscustomobject]@{ Name = 'LLM_VALIDATION_PROJECT_ENDPOINT'; Source = 'Variable'; Variable = 'VALIDATION_ENDPOINT' }
            )
        }
        $endpoint = 'https://example.services.ai.azure.com/api/projects/test'
        $scriptRoot = Join-Path $repositoryPackage '.github/skills/azure-ai-projects-sample-validation/scripts'
        $original = $env:FOUNDRY_PROJECT_ENDPOINT
        try {
            $env:FOUNDRY_PROJECT_ENDPOINT = 'before-test'
            $output = @(& $projectRunner -ProfilesJson (New-RegistryFixture @($testProfile)) `
                -TestIdsJson (ConvertTo-Json -InputObject @($testProfile.TestId) -Compress) `
                -FoundryProjectEndpoint $endpoint -ExpectedEndpointHash (Get-TestProjectEndpointHash $endpoint) `
                -PackageRoot $root -PythonExecutable (Join-Path $repositoryPackage '.venv/Scripts/python.exe') `
                -ResolverScript (Join-Path $scriptRoot 'ResolveSampleTest.ps1') `
                -RunnerScript (Join-Path $scriptRoot 'InvokeSampleValidation.ps1') -ResultsDirectory (Join-Path $root 'results') `
                -Values @{ DIRECT_VALUE = 'profile-direct'; HELPER_VALUE = 'profile-helper'; HARNESS_VALUE = 'profile-harness'; VALIDATION_ENDPOINT = 'https://validation.example' } `
                -Run -ConfirmLive)
            $rows = @($output | Where-Object { $_ -is [pscustomobject] -and $_.PSObject.Properties.Name -contains 'JUnit' })
            $rows.Count | Should Be 1
            $rows[0].Result | Should Be 'succeeded'
            $junit = Get-Content -LiteralPath $rows[0].JUnit -Raw
            $junit | Should Match 'tests="1"'
            $junit | Should Match 'failures="0"'
            ($output -join "`n") | Should Not Match 'profile-direct|profile-helper|profile-harness|https://validation.example'
            $env:FOUNDRY_PROJECT_ENDPOINT | Should Be 'before-test'
        } finally { $env:FOUNDRY_PROJECT_ENDPOINT = $original }
    }
}