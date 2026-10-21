# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$ProfilesJson = $env:SAMPLE_TEST_PROFILES_JSON,
    [string]$TestIdsJson = $env:SAMPLE_TEST_PROFILE_IDS,
    [string]$FoundryProjectEndpoint = $env:FOUNDRY_PROJECT_ENDPOINT,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedEndpointHash,
    [string]$PackageRoot,
    [string]$PythonExecutable,
    [string]$ResultsDirectory,
    [switch]$Run,
    [switch]$ConfirmLive,
    [Collections.IDictionary]$Values,
    [string]$ResolverScript,
    [string]$RunnerScript
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'TestProfileHelpers.ps1')
$registry = ConvertFrom-TestProfileRegistry $ProfilesJson
if ($ExpectedEndpointHash -cnotmatch '^[0-9a-f]{32}$' -or (Get-TestProjectEndpointHash $FoundryProjectEndpoint) -cne $ExpectedEndpointHash) {
    throw 'The endpoint group does not match this pipeline. Create/configure a separate pipeline for the other endpoint.'
}
try { $ids = ConvertFrom-Json -InputObject $TestIdsJson -NoEnumerate -ErrorAction Stop } catch { throw 'SAMPLE_TEST_PROFILE_IDS must be a JSON array of exact TestIds.' }
if ($ids -isnot [array] -or $ids.Count -eq 0) { throw 'SAMPLE_TEST_PROFILE_IDS must be a nonempty JSON array.' }
$uniqueIds = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$selected = @(
    foreach ($id in $ids) {
        if ($id -isnot [string] -or -not $uniqueIds.Add($id)) { throw 'Project TestIds must be strings without duplicates.' }
        $matchingProfiles = @($registry.Profiles | Where-Object { $_.TestId -ceq $id })
        if ($matchingProfiles.Count -ne 1) { throw 'A project TestId has no registered exact test profile.' }
        if ($matchingProfiles[0].Enabled) { $matchingProfiles[0] }
    }
)
if ($selected.Count -eq 0) { throw 'No enabled profiles are assigned to this project.' }
if (-not $PackageRoot) { $PackageRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path }
$scriptRoot = Join-Path $PackageRoot '.github/skills/azure-ai-projects-sample-validation/scripts'
if (-not $ResolverScript) { $ResolverScript = Join-Path $scriptRoot 'ResolveSampleTest.ps1' }
if (-not $RunnerScript) { $RunnerScript = Join-Path $scriptRoot 'InvokeSampleValidation.ps1' }
$environments = [Collections.Generic.Dictionary[string, object]]::new([StringComparer]::Ordinal)
foreach ($testProfile in $selected) {
    $environment = [ordered]@{}
    foreach ($binding in $testProfile.Environment) {
        if ($binding.Source -eq 'ProjectEndpoint') { $value = $FoundryProjectEndpoint }
        elseif ($null -ne $Values) {
            if (-not $Values.Contains($binding.Variable)) { throw 'A required project value is missing; review the profile variable references.' }
            $value = $Values[$binding.Variable]
        } else { $value = [Environment]::GetEnvironmentVariable("SAMPLE_PROFILE_VALUE_$($binding.Variable)", 'Process') }
        if ($value -isnot [string] -or [string]::IsNullOrEmpty($value) -or $value -ceq ('$({0})' -f $binding.Variable)) {
            throw 'A required value is missing, empty, or unmapped. Review the endpoint group and wrapper mappings.'
        }
        $environment[$binding.Name] = $value
    }
    $environments[$testProfile.TestId] = $environment
}
if (-not $Run) {
    $selected | ForEach-Object {
        [pscustomobject]@{ TestId = $_.TestId; SamplePath = $_.SamplePath; EnvironmentNames = @($_.Environment.Name); Execution = 'Not run' }
    }
    return
}
if (-not $ConfirmLive) { throw 'Live execution requires -Run -ConfirmLive after approval.' }
if ([string]::IsNullOrWhiteSpace($ResultsDirectory)) { throw 'ResultsDirectory is required for live profile execution.' }
foreach ($name in @('PYTEST_ADDOPTS', 'PYTEST_PLUGINS')) {
    if (-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, 'Process'))) {
        throw 'Remove inherited PYTEST_ADDOPTS/PYTEST_PLUGINS overrides before running endpoint profiles.'
    }
}
$null = New-Item -ItemType Directory -Path $ResultsDirectory -Force
$emptyEnv = Join-Path ([IO.Path]::GetTempPath()) ("test-profile-{0}.env" -f [guid]::NewGuid())
[IO.File]::WriteAllText($emptyEnv, '', [Text.UTF8Encoding]::new($false))
$rows = [Collections.Generic.List[object]]::new()
try {
    $argumentsById = [Collections.Generic.Dictionary[string, object]]::new([StringComparer]::Ordinal)
    # Collect and preview ALL exact nodes before any live execution. Brackets in parameter IDs
    # are compared literally rather than interpreted as PowerShell wildcard character classes.
    foreach ($testProfile in $selected) {
        $resolveArguments = @{ SamplePath = $testProfile.SamplePath; PackageRoot = $PackageRoot }
        if ($PythonExecutable) { $resolveArguments.PythonExecutable = $PythonExecutable }
        $nodes = @(& $ResolverScript @resolveArguments | Where-Object { $_.NodeId -ceq $testProfile.TestId })
        if ($nodes.Count -ne 1) { throw 'An assigned TestId no longer resolves to exactly one collected sample test.' }
        $environment = $environments[$testProfile.TestId]
        $arguments = @{
            PackageRoot = $PackageRoot; SamplePattern = $testProfile.SamplePath; TestPattern = $testProfile.TestId
            Mode = 'live-test-locally'; EnvFile = $emptyEnv; HideEnvironmentValues = $true
            EnvironmentVariable = @($environment.GetEnumerator() | ForEach-Object { '{0}={1}' -f $_.Key, $_.Value })
        }
        if ($PythonExecutable) { $arguments.PythonExecutable = $PythonExecutable }
        $preview = @(& $RunnerScript @arguments)
        $previewNodes = @($preview | Where-Object { $_ -is [string] -and $_.StartsWith('Node: ') })
        if ($previewNodes.Count -ne 1 -or $previewNodes[0].Substring(6) -cne $testProfile.TestId) {
            throw 'The existing runner preview did not confirm exactly the assigned TestId.'
        }
        if (@($preview | Where-Object { $_ -match '^(Missing|Empty):\s*\S' }).Count -gt 0) {
            throw 'Required sample/harness environment values are missing. Complete the profile before running.'
        }
        $argumentsById[$testProfile.TestId] = $arguments
    }
    foreach ($testProfile in $selected) {
        $arguments = $argumentsById[$testProfile.TestId]
        $key = (Get-TestProfileDigest $testProfile.TestId).Substring(0, 16)
        $junit = Join-Path $ResultsDirectory "test-junit-$key.xml"
        $row = [pscustomobject]@{ TestId = $testProfile.TestId; Result = 'failed'; JUnit = $junit }
        $rows.Add($row)
        try {
            # An old report must never establish success for a run that did not write results.
            if (Test-Path -LiteralPath $junit) { Remove-Item -LiteralPath $junit -Force }
            # Each invocation starts a separate pytest process. Never combine different
            # profile environments in one pytest invocation or mutate a client mid-test.
            & $RunnerScript @arguments -Run -ConfirmSelection -ConfirmLive -JUnitXml $junit
            Assert-TestProfileJUnitResult $testProfile.TestId $junit
            $row.Result = 'succeeded'
        } catch { Write-Warning 'A test profile failed; continue with the remaining profiles and inspect its test output.' }
    }
} finally { Remove-Item -LiteralPath $emptyEnv -Force -ErrorAction SilentlyContinue }
$lines = @('# Project test-profile results', '', '| Exact test ID | Result |', '| --- | --- |')
foreach ($row in $rows) { $lines += "| $(ConvertTo-TestProfileMarkdown $row.TestId) | $($row.Result) |" }
$lines | Set-Content -LiteralPath (Join-Path $ResultsDirectory 'test-profile-summary.md') -Encoding UTF8
$rows
if (@($rows | Where-Object { $_.Result -ne 'succeeded' }).Count -gt 0) { throw 'One or more test profiles failed. See the published per-test results.' }