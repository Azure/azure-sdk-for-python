# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

$summaryScript = Join-Path (Split-Path $PSScriptRoot) "scripts\PublishSampleValidationSummary.ps1"

Describe "PublishSampleValidationSummary.ps1" {
    It "lists every test outcome with direct result links" {
        $requestedUris = [System.Collections.Generic.List[string]]::new()
        $requestInvoker = {
            param($RequestUri, $RequestHeaders)
            $requestedUris.Add($RequestUri)
            $RequestHeaders.Authorization | Should Be "Bearer token"
            if ($RequestUri -match "/test/runs\?buildUri=") {
                return [pscustomobject]@{ value = @([pscustomobject]@{ id = 11 }) }
            }
            if ($RequestUri -match "/test/runs/11/results\?") {
                return [pscustomobject]@{
                    value = @(
                        [pscustomobject]@{ id = 100; outcome = "Passed"; testCaseTitle = "passing test"; durationInMs = 1250 },
                        [pscustomobject]@{ id = 101; outcome = "Failed"; testCaseTitle = "failing | test"; durationInMs = 2500 }
                    )
                }
            }
            throw "Unexpected URI: $RequestUri"
        }.GetNewClosure()
        $outputPath = Join-Path $TestDrive "summary\all-results.md"

        $actual = & $summaryScript -BuildId 42 -BearerToken "token" -OutputPath $outputPath `
            -RequestInvoker $requestInvoker
        $content = Get-Content -LiteralPath $outputPath -Raw

        $actual.Total | Should Be 2
        $actual.Passed | Should Be 1
        $actual.Failed | Should Be 1
        $actual.Other | Should Be 0
        $content | Should Match "2 total.*1 passed.*1 failed.*0 other"
        $content | Should Match "\| Passed \| passing test \| 1\.25s \|"
        $content | Should Match "\| Failed \| failing \\\| test \| 2\.50s \|"
        $content | Should Match "runId=11&resultId=100&paneView=attachments"
        $content | Should Match "runId=11&resultId=101&paneView=attachments"
        ($requestedUris -join "`n") | Should Match "vstfs%3A%2F%2F%2FBuild%2FBuild%2F42"
    }
}
