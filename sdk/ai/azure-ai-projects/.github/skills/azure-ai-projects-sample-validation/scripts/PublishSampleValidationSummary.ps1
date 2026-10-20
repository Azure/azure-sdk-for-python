# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$Organization = "azure-sdk",
    [string]$Project = "internal",
    [Parameter(Mandatory = $true)]
    [int]$BuildId,
    [Parameter(Mandatory = $true)]
    [string]$BearerToken,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath,
    [scriptblock]$RequestInvoker
)

$ErrorActionPreference = "Stop"
$headers = @{ Authorization = "Bearer $BearerToken" }
if (-not $RequestInvoker) {
    $RequestInvoker = {
        param($RequestUri, $RequestHeaders)
        Invoke-RestMethod -Method Get -Uri $RequestUri -Headers $RequestHeaders
    }
}

function ConvertTo-MarkdownCell {
    param([object]$Value)

    return ([string]$Value).Replace("|", "\|").Replace("`r", " ").Replace("`n", " ")
}

$buildUri = [Uri]::EscapeDataString("vstfs:///Build/Build/$BuildId")
$runsUri = "https://dev.azure.com/$Organization/$Project/_apis/test/runs?buildUri=$buildUri&api-version=7.1"
$runsResponse = & $RequestInvoker $runsUri $headers
$rows = @(
    foreach ($run in @($runsResponse.value)) {
        $resultsUri = "https://dev.azure.com/$Organization/$Project/_apis/test/runs/$($run.id)/results?`$top=10000&api-version=7.1"
        $resultsResponse = & $RequestInvoker $resultsUri $headers
        foreach ($result in @($resultsResponse.value)) {
            $duration = if ($null -ne $result.durationInMs) {
                "{0:N2}s" -f ([double]$result.durationInMs / 1000)
            } else {
                ""
            }
            $resultUrl = "https://dev.azure.com/$Organization/$Project/_build/results?buildId=$BuildId&view=ms.vss-test-web.build-test-results-tab&runId=$($run.id)&resultId=$($result.id)&paneView=attachments"
            [pscustomobject]@{
                Outcome = ConvertTo-MarkdownCell $result.outcome
                Title = ConvertTo-MarkdownCell $result.testCaseTitle
                Duration = $duration
                Url = $resultUrl
            }
        }
    }
)

$passedCount = @($rows | Where-Object { $_.Outcome -eq "Passed" }).Count
$failedCount = @($rows | Where-Object { $_.Outcome -eq "Failed" }).Count
$otherCount = $rows.Count - $passedCount - $failedCount
$buildUrl = "https://dev.azure.com/$Organization/$Project/_build/results?buildId=$BuildId"
$lines = @(
    "# All sample validation results",
    "",
    "Build [#$BuildId]($buildUrl): **$($rows.Count) total**, **$passedCount passed**, **$failedCount failed**, **$otherCount other**.",
    ""
)

if ($rows.Count -gt 0) {
    $lines += @(
        "| Outcome | Test | Duration | Details |",
        "| --- | --- | ---: | --- |"
    )
    foreach ($row in $rows) {
        $lines += "| $($row.Outcome) | $($row.Title) | $($row.Duration) | [Open result and attachments]($($row.Url)) |"
    }
} else {
    $lines += "No test results were published for this build."
}

$outputDirectory = Split-Path -Parent $OutputPath
if ($outputDirectory -and -not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}
$lines | Set-Content -LiteralPath $OutputPath -Encoding UTF8

[pscustomobject]@{
    OutputPath = $OutputPath
    Total = $rows.Count
    Passed = $passedCount
    Failed = $failedCount
    Other = $otherCount
}
