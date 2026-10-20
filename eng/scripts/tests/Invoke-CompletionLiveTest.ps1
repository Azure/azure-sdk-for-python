# TEST ONLY. The only mutations are status updates to the two disposable, owned test fixtures.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('BeforeResolve', 'BeforeCompletion', 'AfterCompletion')]
    [string]$Phase,
    [Parameter(Mandatory = $true)]
    [int]$SecondaryPlanId,
    [Parameter(Mandatory = $true)]
    [string]$AzsdkExePath,
    [string]$ResolvedSdkPr = ''
)

Set-StrictMode -Version 4
$ErrorActionPreference = 'Stop'
$primaryId = 37070
$expectedPr = 'https://github.com/Azure/azure-sdk-for-python/pull/48030'
$marker = 'Completion-Pilot-49390-20261020'
$evidenceDirectory = Join-Path $env:PIPELINE_WORKSPACE 'completion-fixture'
$pipelineUrl = "$($env:SYSTEM_COLLECTIONURI)$($env:SYSTEM_TEAMPROJECT)/_build/results?buildId=$($env:BUILD_BUILDID)"
if ($SecondaryPlanId -le $primaryId) { throw 'The separately provisioned disposable ambiguity fixture is required.' }
if ($env:AZSDKTOOLS_AGENT_TESTING -cne 'true') { throw 'Test mode is required.' }
$version = (& $AzsdkExePath --version | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $version -ne '0.6.54') { throw 'Expected the released CLI 0.6.54.' }

$tokenResult = az account get-access-token --resource '499b84ac-1321-427f-aa17-267ca6975798' --output json
if ($LASTEXITCODE -ne 0) { throw 'Hosted identity cannot obtain the existing ADO audience token.' }
$authentication = ($tokenResult -join "`n") | ConvertFrom-Json
$headers = @{ Authorization = 'Bearer ' + $authentication.accessToken }

function Get-TestFixture([int]$Id) {
    if ($Id -notin @($primaryId, $SecondaryPlanId)) { throw 'This test cannot access a non-fixture work item.' }
    $item = Invoke-RestMethod -Uri "https://dev.azure.com/azure-sdk/Release/_apis/wit/workitems/${Id}?api-version=7.1" -Headers $headers -TimeoutSec 45
    if ($item.fields.'System.CreatedBy'.uniqueName -ne 'gaoh@microsoft.com' -or
        $item.fields.'System.Tags' -notlike '*Release Planner App Test*' -or
        $item.fields.'System.Tags' -notlike "*$marker*" -or
        $item.fields.'System.State' -ne 'In Progress' -or
        [string]$item.fields.'Custom.ReleasePlanID' -ne [string]$Id -or
        $item.fields.'Custom.PythonPackageName' -ne 'azure-template' -or
        $item.fields.'Custom.ReleaseStatusForDotnet' -ne 'Not applicable' -or
        $item.fields.'Custom.ReleaseExclusionStatusForDotnet' -eq 'Approved') {
        throw "Fixture $Id does not match the owned, test-only, non-finishing setup."
    }
    return $item
}

function Get-BusinessSnapshot($Item, [string[]]$Exclude = @()) {
    $result = [ordered]@{}
    foreach ($property in @($Item.fields.PSObject.Properties | Sort-Object Name)) {
        if (($property.Name.StartsWith('Custom.') -or $property.Name -in @('System.State', 'System.Title', 'System.Tags')) -and $property.Name -notin $Exclude) {
            $result[$property.Name] = $property.Value
        }
    }
    return ConvertTo-Json -InputObject $result -Depth 10 -Compress
}

function Set-TestPr($Item, [string]$Url) {
    $null = Get-TestFixture $Item.id
    $patch = @(
        @{ op = 'test'; path = '/rev'; value = $Item.rev },
        @{ op = 'add'; path = '/fields/Custom.SDKPullRequestForPython'; value = $Url }
    )
    return Invoke-RestMethod -Method Patch -Uri "https://dev.azure.com/azure-sdk/Release/_apis/wit/workitems/$($Item.id)?api-version=7.1" `
        -Headers $headers -ContentType 'application/json-patch+json' -Body (ConvertTo-Json -InputObject $patch -Depth 5) -TimeoutSec 45
}

function Invoke-NegativeCorrelation([string]$Name, [string]$SdkPr, [string]$ExpectedError) {
    $before = @(Get-TestFixture $primaryId; Get-TestFixture $SecondaryPlanId)
    $scriptPath = Join-Path $PSScriptRoot '../../common/scripts/Mark-ReleasePlanCompletion.ps1'
    $messages = @(& $scriptPath -PackageInfoFilePath (Join-Path $evidenceDirectory 'azure-template.json') `
        -AzsdkExePath $AzsdkExePath -SdkPullRequest $SdkPr -PipelineUrl $pipelineUrl 3>&1 6>&1)
    $details = @($messages | ForEach-Object { if ([string]$_ -match '^Details: (\{.*\})$') { $Matches[1] | ConvertFrom-Json } })
    if ($details.Count -ne 1 -or $details[0].operation_status -ne 'Failed' -or $details[0].response_error -notmatch $ExpectedError) {
        throw "Negative case '$Name' did not produce its expected correlation rejection."
    }
    if (($messages | Out-String) -match 'LEGACY_RELEASE_PLAN_LOOKUP') { throw 'A correlated failure fell back to package lookup.' }
    $after = @(Get-TestFixture $primaryId; Get-TestFixture $SecondaryPlanId)
    for ($i = 0; $i -lt $before.Count; $i++) {
        if ($before[$i].rev -ne $after[$i].rev -or (Get-BusinessSnapshot $before[$i]) -cne (Get-BusinessSnapshot $after[$i])) {
            throw "Negative case '$Name' changed a fixture."
        }
    }
    Write-Host ('LIVE_COMPLETION_ASSERTION ' + (ConvertTo-Json -Compress -InputObject @{ case = $Name; result = 'Passed'; workItemWrites = 0; fallback = $false }))
}

try {
    New-Item -ItemType Directory -Path $evidenceDirectory -Force | Out-Null
    $primary = Get-TestFixture $primaryId
    $secondary = Get-TestFixture $SecondaryPlanId
    if ($primary.fields.'Custom.SDKPullRequestForPython' -cne $expectedPr) { throw 'Primary fixture PR is not the real selected event.' }
    switch ($Phase) {
        'BeforeResolve' {
            if ($primary.fields.'Custom.ReleaseStatusForPython' -ne 'Not applicable') { throw 'Primary fixture was already used; inspect rather than repeat.' }
            Write-Host 'LIVE_COMPLETION_ASSERTION {"case":"released-cli-and-owned-fixtures","result":"Passed","version":"0.6.54"}'
        }
        'BeforeCompletion' {
            if ($ResolvedSdkPr -cne $expectedPr -or $primary.fields.'Custom.ReleaseStatusForPython' -ne 'Release In Progress' -or
                $primary.fields.'Custom.ReleasePipelineForPython' -cne $pipelineUrl) {
                throw 'Actual resolver output/progress did not reach the completion stage.'
            }
            @{ Name = 'azure-template'; Version = '1.0.0b1'; SdkType = 'client'; TestOnly = $true } |
                ConvertTo-Json | Set-Content -LiteralPath (Join-Path $evidenceDirectory 'azure-template.json')
            Write-Host 'LIVE_COMPLETION_ASSERTION {"case":"real-pr-resolution-and-stage-output","result":"Passed","sdkPr":48030}'
            Invoke-NegativeCorrelation -Name 'unmatched-sdk-pr' -SdkPr 'https://github.com/Azure/azure-sdk-for-python/pull/49390' -ExpectedError 'found 0'
            Invoke-NegativeCorrelation -Name 'invalid-spec-pr-repository' -SdkPr 'https://github.com/Azure/azure-rest-api-specs/pull/48030' -ExpectedError 'SDK pull request must'
            $originalPr = [string]$secondary.fields.'Custom.SDKPullRequestForPython'
            $duplicate = Set-TestPr $secondary $expectedPr
            try {
                Invoke-NegativeCorrelation -Name 'ambiguous-sdk-pr' -SdkPr $expectedPr -ExpectedError 'found 2'
            }
            finally {
                $current = Get-TestFixture $SecondaryPlanId
                if ($current.rev -ne $duplicate.rev) { throw 'Secondary fixture changed independently; do not overwrite it.' }
                $null = Set-TestPr $current $originalPr
            }
            $snapshot = @{
                primary = Get-BusinessSnapshot (Get-TestFixture $primaryId) @('Custom.ReleaseStatusForPython', 'Custom.ReleasedVersionForPython', 'Custom.ReleasePipelineForPython')
                secondary = Get-BusinessSnapshot (Get-TestFixture $SecondaryPlanId)
            }
            $snapshot | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $evidenceDirectory 'before-completion.json')
        }
        'AfterCompletion' {
            $before = Get-Content -LiteralPath (Join-Path $evidenceDirectory 'before-completion.json') -Raw | ConvertFrom-Json
            if ($primary.fields.'Custom.ReleaseStatusForPython' -ne 'Released' -or
                $primary.fields.'Custom.ReleasedVersionForPython' -ne '1.0.0b1' -or
                $primary.fields.'Custom.ReleasePipelineForPython' -cne $pipelineUrl) {
                throw 'Released CLI did not persist expected completion fields.'
            }
            if ((Get-BusinessSnapshot $primary @('Custom.ReleaseStatusForPython', 'Custom.ReleasedVersionForPython', 'Custom.ReleasePipelineForPython')) -cne $before.primary -or
                (Get-BusinessSnapshot $secondary) -cne $before.secondary) {
                throw 'Completion changed an unrelated plan/language/business field.'
            }
            Write-Host ('LIVE_COMPLETION_ASSERTION ' + (ConvertTo-Json -Compress -InputObject @{ case = 'exact-plan-language-package-completion'; result = 'Passed'; releasePlanId = $primaryId; language = 'Python'; package = 'azure-template'; planState = $primary.fields.'System.State'; publication = $false }))
        }
    }
}
finally {
    $headers.Clear()
    $authentication = $null
    $tokenResult = $null
}