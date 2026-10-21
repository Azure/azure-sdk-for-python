# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$Organization = 'azure-sdk',
    [string]$Project = 'internal',
    [string]$PipelinesJson = $env:SAMPLE_PROJECT_PIPELINES_JSON,
    [string]$BearerToken = $env:SYSTEM_ACCESSTOKEN,
    [string]$SummaryPath,
    [ValidateRange(1, 1440)][int]$TimeoutMinutes = 120,
    [ValidateRange(0, 3600)][int]$PollIntervalSeconds = 15,
    [switch]$Run,
    [switch]$ConfirmRun,
    [scriptblock]$RequestInvoker,
    [scriptblock]$Clock,
    [scriptblock]$WaitInvoker
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'TestProfileHelpers.ps1')
try { $targets = ConvertFrom-Json -InputObject $PipelinesJson -NoEnumerate -ErrorAction Stop } catch { throw 'SAMPLE_PROJECT_PIPELINES_JSON must be a JSON array.' }
if ($targets -isnot [array] -or $targets.Count -eq 0) { throw 'Configure at least one endpoint pipeline in SAMPLE_PROJECT_PIPELINES_JSON.' }
if ($Organization -notmatch '^[a-zA-Z0-9][a-zA-Z0-9-]*$' -or [string]::IsNullOrWhiteSpace($Project)) { throw 'Invalid ADO organization/project.' }
$ids = [Collections.Generic.HashSet[int]]::new()
foreach ($target in $targets) {
    if (($target.DefinitionId -isnot [int] -and $target.DefinitionId -isnot [long]) -or $target.DefinitionId -le 0 -or
        $target.DefinitionId -gt [int]::MaxValue -or -not $ids.Add([int]$target.DefinitionId) -or
        $target.SourceBranch -cnotmatch '^refs/heads/[^\s]+$' -or $target.SourceBranch -match '[*?\[\]]|\$\(') {
        throw 'Each endpoint target needs one unique positive DefinitionId and explicit refs/heads/ branch.'
    }
}
if (-not $Run) { $targets | Select-Object DefinitionId, SourceBranch; return }
if (-not $ConfirmRun) { throw 'Preview before -Run -ConfirmRun; this starts live endpoint tests.' }
if (-not $SummaryPath) { throw 'SummaryPath is required.' }
if (-not $Clock) { $Clock = { [DateTimeOffset]::UtcNow } }
if (-not $WaitInvoker) {
    $WaitInvoker = {
        param($Seconds)
        $handle = [Threading.ManualResetEventSlim]::new($false)
        try { $null = $handle.Wait([TimeSpan]::FromSeconds($Seconds)) } finally { $handle.Dispose() }
    }
}
$deadline = (& $Clock).AddMinutes($TimeoutMinutes)
$api = "https://dev.azure.com/$Organization/$([Uri]::EscapeDataString($Project))"
function Invoke-EndpointRequest {
    param([string]$Method, [string]$Uri, [object]$Body)

    $remaining = ($deadline - (& $Clock)).TotalSeconds
    if ($remaining -le 0) { throw 'The master deadline was reached.' }
    Invoke-TestProfileRequest -Method $Method -Uri $Uri -Body $Body -BearerToken $BearerToken `
        -RequestInvoker $RequestInvoker -TimeoutSeconds ([int][Math]::Min(60, [Math]::Ceiling($remaining)))
}
$endpointKeys = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$definitions = @{}
foreach ($target in $targets) {
    $definition = Invoke-EndpointRequest -Method Get -Uri "$api/_apis/build/definitions/$($target.DefinitionId)?api-version=7.1"
    $yaml = [string]$definition.process.yamlFilename
    if ($definition.id -ne $target.DefinitionId -or [int]$definition.revision -le 0 -or
        $definition.queueStatus -notin @('enabled', 0) -or
        $yaml.Replace('\', '/').TrimStart('/') -cnotmatch '^sdk/ai/azure-ai-projects/pipelines/projects/foundry-[0-9a-f]{32}\.yml$') {
        throw 'Every target must be an enabled endpoint wrapper pipeline, not the master or the old ad-hoc child.'
    }
    if (-not $endpointKeys.Add($yaml.Replace('\', '/').TrimStart('/'))) { throw 'More than one target is assigned to the same endpoint. No runs were queued.' }
    $definitions[$target.DefinitionId] = $definition
}
$rows = [Collections.Generic.List[object]]::new()
foreach ($target in $targets) {
    $row = [pscustomobject]@{ DefinitionId = $target.DefinitionId; BuildId = $null; Result = 'not queued (deadline)'; Url = ''; Pending = $false }
    $rows.Add($row)
    if ((& $Clock) -ge $deadline) { continue }
    try {
        $body = @{ resources = @{ repositories = @{ self = @{ refName = $target.SourceBranch } } } }
        $revision = $definitions[$target.DefinitionId].revision
        $queued = Invoke-EndpointRequest -Method Post -Uri "$api/_apis/pipelines/$($target.DefinitionId)/runs?pipelineVersion=$revision&api-version=7.1" -Body $body
        if ([int]$queued.id -le 0) { throw 'Invalid queue response.' }
        $row.BuildId = [int]$queued.id; $row.Pending = $true; $row.Result = 'pending'
        $row.Url = "$api/_build/results?buildId=$($row.BuildId)"
    } catch { $row.Result = 'queue not confirmed (inspect ADO before retrying)' }
}
while (@($rows | Where-Object { $_.Pending }).Count -gt 0) {
    foreach ($row in @($rows | Where-Object { $_.Pending })) {
        if ((& $Clock) -ge $deadline) { break }
        try {
            $build = Invoke-EndpointRequest -Method Get -Uri "$api/_apis/build/builds/$($row.BuildId)?api-version=7.1"
            if ($build.id -ne $row.BuildId -or -not $build.status) { throw 'Invalid status.' }
            if ($build.status -eq 'completed') {
                $row.Result = if ($build.result -in @('succeeded', 'failed', 'partiallySucceeded', 'canceled')) { $build.result } else { 'unknown result' }
                $row.Pending = $false
            }
        } catch { $row.Result = 'status unknown (child may still run)'; $row.Pending = $false }
    }
    if ((& $Clock) -ge $deadline) {
        foreach ($row in @($rows | Where-Object { $_.Pending })) { $row.Result = 'timed out (child not canceled)'; $row.Pending = $false }
    }
    if (@($rows | Where-Object { $_.Pending }).Count -gt 0) {
        $null = & $WaitInvoker ([Math]::Min($PollIntervalSeconds, [Math]::Max(0, ($deadline - (& $Clock)).TotalSeconds)))
    }
}
$lines = @('# Endpoint pipeline results', '', '| Pipeline | Result | Build |', '| --- | --- | --- |')
foreach ($row in $rows) {
    $link = if ($row.BuildId) { "[#$($row.BuildId)]($($row.Url))" } else { 'not confirmed' }
    $lines += "| $($row.DefinitionId) | $($row.Result) | $link |"
}
$directory = Split-Path -Parent $SummaryPath
if ($directory) { $null = New-Item -ItemType Directory -Path $directory -Force }
$lines | Set-Content -LiteralPath $SummaryPath -Encoding UTF8
$rows | Select-Object DefinitionId, BuildId, Result, Url
if (@($rows | Where-Object { $_.Result -ne 'succeeded' }).Count -gt 0) { throw 'One or more endpoint pipelines did not succeed.' }