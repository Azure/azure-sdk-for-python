# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot
$queueScript = Join-Path (Split-Path $paths.SampleTestRunner) "QueueSampleValidationPipeline.ps1"

Describe "QueueSampleValidationPipeline.ps1" {
    It "queues selectors as template parameters and values as secret build variables" {
        $state = [pscustomobject]@{
            Uri = $null
            Headers = $null
            Body = $null
        }
        $requestInvoker = {
            param($RequestUri, $RequestHeaders, $RequestBody)
            $state.Uri = $RequestUri
            $state.Headers = $RequestHeaders
            $state.Body = $RequestBody
            [pscustomobject]@{
                id = 42
                definition = @{ name = "python - azure-ai-projects - tests" }
                _links = @{ web = @{ href = "https://dev.azure.com/example/build/42" } }
            }
        }.GetNewClosure()

        $actual = & $queueScript -SourceBranch "topic" -SamplePattern "samples\agents\*.py" `
            -TestPattern "*basic*" -EnvironmentVariable @("TOKEN=secret=value", "ENDPOINT=https://example") `
            -BearerToken "ado-token" -PipelineRevision 3 -RequestInvoker $requestInvoker

        $actual.BuildId | Should Be 42
        $state.Uri | Should Be "https://dev.azure.com/azure-sdk/internal/_apis/pipelines/8392/runs?pipelineVersion=3&api-version=7.1"
        $state.Headers.Authorization | Should Be "Bearer ado-token"
        $state.Body.resources.repositories.self.refName | Should Be "refs/heads/topic"
        $state.Body.templateParameters.SamplePattern | Should Be "samples\agents\*.py"
        $state.Body.templateParameters.TestPattern | Should Be "*basic*"
        $environmentPayload = $state.Body.variables.SAMPLE_ENVIRONMENT_VARIABLES_JSON.value | ConvertFrom-Json
        $environmentPayload.TOKEN | Should Be "secret=value"
        $environmentPayload.ENDPOINT | Should Be "https://example"
        $state.Body.variables.SAMPLE_ENVIRONMENT_VARIABLES_JSON.isSecret | Should Be $true
        ($state.Body.templateParameters | ConvertTo-Json) | Should Not Match "secret=value|https://example"
    }

    It "rejects duplicate environment names" {
        $caught = $null
        try {
            & $queueScript -SourceBranch "topic" -SamplePattern "*.py" `
                -EnvironmentVariable @("VALUE=one", "VALUE=two") -BearerToken "ado-token" `
                -PipelineRevision 3 -RequestInvoker { throw "should not queue" }
        } catch { $caught = $_ }
        $caught.Exception.Message | Should Match "duplicate name"
    }
}