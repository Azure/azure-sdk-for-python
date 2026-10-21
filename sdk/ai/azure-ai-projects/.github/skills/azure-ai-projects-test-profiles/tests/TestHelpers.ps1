# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

$skillRoot = Split-Path $PSScriptRoot -Parent
$setProfile = Join-Path $skillRoot 'scripts/SetTestProfile.ps1'
$projectRunner = Join-Path $skillRoot 'scripts/InvokeTestProfileProject.ps1'
$newPipeline = Join-Path $skillRoot 'scripts/NewTestProjectPipeline.ps1'
$masterRunner = Join-Path $skillRoot 'scripts/InvokeTestProjectsMaster.ps1'
. (Join-Path $skillRoot 'scripts/TestProfileHelpers.ps1')

function New-ProfileFixture {
    param([string]$Case = 'one')

    [pscustomobject][ordered]@{
        TestId = "tests/samples/test_samples.py::test_multiple[variant-$Case]"
        SamplePath = 'samples/multiple/sample_multiple.py'
        Enabled = $true
        Environment = @(
            [pscustomobject]@{ Name = 'FOUNDRY_PROJECT_ENDPOINT'; Source = 'ProjectEndpoint' }
            [pscustomobject]@{ Name = 'MULTIPLE_REQUIRED'; Source = 'Variable'; Variable = 'TEST_VALUE' }
        )
    }
}

function New-RegistryFixture {
    param([object[]]$Profiles = @((New-ProfileFixture)))

    ConvertTo-Json -InputObject ([ordered]@{ Version = 1; Profiles = @($Profiles) }) -Depth 10
}

function New-ProfileGroupFixture {
    [pscustomobject]@{
        id = 12; type = 'Vsts'; name = 'profile-metadata'; description = 'Nonsecret metadata only'
        modifiedOn = '2026-01-01T00:00:00Z'
        variableGroupProjectReferences = @(@{ name = 'profile-metadata'; projectReference = @{ id = 'project-id' } })
        variables = [pscustomobject]@{
            SAMPLE_TEST_PROFILES_JSON = [pscustomobject]@{ value = '{"Version":1,"Profiles":[]}'; isSecret = $false }
            OTHER_METADATA = [pscustomobject]@{ value = 'preserve'; isSecret = $false }
        }
    }
}

function New-GroupRequestFixture {
    param($State)

    {
        param($Method, $Uri, $Headers, $Body)
        $State.Calls.Add([pscustomobject]@{ Method = $Method; Uri = $Uri; Headers = $Headers; Body = $Body })
        if ($Method -eq 'Get') { return $State.Group | ConvertTo-Json -Depth 20 | ConvertFrom-Json }
        if ($Method -eq 'Put') {
            $State.Saved = $Body
            $saved = $Body | ConvertTo-Json -Depth 20 | ConvertFrom-Json
            $saved | Add-Member -NotePropertyName id -NotePropertyValue 12
            if ($State.IgnoreSave) { $saved.variables.SAMPLE_TEST_PROFILES_JSON.value = '{"Version":1,"Profiles":[]}' }
            return $saved
        }
        throw 'Unexpected request.'
    }.GetNewClosure()
}

function New-ProjectRunnerFixture {
    param([string]$Root)

    $null = New-Item -ItemType Directory -Path $Root -Force
    @'
param([string]$SamplePath, [string]$PackageRoot, [string]$PythonExecutable)
$index = Join-Path $PackageRoot 'nodes.json'
Get-Content -LiteralPath $index -Raw | ConvertFrom-Json
'@ | Set-Content -LiteralPath (Join-Path $Root 'resolver.ps1')
    @'
param(
    [string]$PackageRoot, [string]$SamplePattern, [string]$TestPattern, [string]$Mode,
    [string]$EnvFile, [string]$PythonExecutable, [string[]]$EnvironmentVariable,
    [switch]$HideEnvironmentValues, [switch]$Run, [switch]$ConfirmSelection, [switch]$ConfirmLive,
    [string]$JUnitXml
)
if ($Mode -ne 'live-test-locally' -or -not $HideEnvironmentValues) { throw 'Wrong execution mode/redaction.' }
if ((Get-Content -LiteralPath $EnvFile -Raw)) { throw 'Must not load a local .env.' }
$events = Join-Path $PackageRoot 'events.txt'
if (-not $Run) {
    Add-Content -LiteralPath $events -Value "preview:$TestPattern"
    Write-Output "Node: $TestPattern"
    if (Test-Path -LiteralPath (Join-Path $PackageRoot 'missing-value')) { Write-Output 'Missing: REQUIRED_VALUE' }
    else { Write-Output 'Missing: ' }
    Write-Output 'Empty: '
    return
}
if (-not $ConfirmSelection -or -not $ConfirmLive) { throw 'Approvals missing.' }
Add-Content -LiteralPath $events -Value "run:$TestPattern"
[ordered]@{ Node = $TestPattern; Environment = $EnvironmentVariable; EnvFile = $EnvFile; JUnit = $JUnitXml } |
    ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $PackageRoot 'runs.jsonl')
if (Test-Path -LiteralPath (Join-Path $PackageRoot 'fail-first')) {
    Remove-Item -LiteralPath (Join-Path $PackageRoot 'fail-first')
    throw 'sensitive-failure-details'
}
$parts = $TestPattern -split '::', 2
$bracket = $parts[1].IndexOf('[')
$baseName = if ($bracket -ge 0) { $parts[1].Substring(0, $bracket) } else { $parts[1] }
$segments = $baseName -split '::'
$caseName = $segments[-1] + $(if ($bracket -ge 0) { $parts[1].Substring($bracket) } else { '' })
$className = $parts[0].Substring(0, $parts[0].Length - 3).Replace('/', '.')
if ($segments.Count -gt 1) { $className += '.' + ($segments[0..($segments.Count - 2)] -join '.') }
$escapedName = [Security.SecurityElement]::Escape($caseName)
$escapedClass = [Security.SecurityElement]::Escape($className)
if (Test-Path -LiteralPath (Join-Path $PackageRoot 'no-junit')) { return }
$skipped = if (Test-Path -LiteralPath (Join-Path $PackageRoot 'skip-test')) { '<skipped />' } else { '' }
$case = "<testcase classname=`"$escapedClass`" name=`"$escapedName`">$skipped</testcase>"
if (Test-Path -LiteralPath (Join-Path $PackageRoot 'collect-only')) { $case = '' }
"<testsuite tests=`"1`" failures=`"0`">$case</testsuite>" | Set-Content -LiteralPath $JUnitXml
'@ | Set-Content -LiteralPath (Join-Path $Root 'runner.ps1')
    @(
        [pscustomobject]@{ NodeId = 'tests/samples/test_samples.py::test_multiple[variant-one]' }
        [pscustomobject]@{ NodeId = 'tests/samples/test_samples.py::test_multiple[variant-two]' }
    ) | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Root 'nodes.json')
}