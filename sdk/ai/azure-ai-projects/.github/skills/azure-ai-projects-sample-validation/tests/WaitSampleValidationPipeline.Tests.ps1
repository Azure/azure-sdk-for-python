# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot
$waitScript = Join-Path (Split-Path $paths.SampleTestRunner) "WaitSampleValidationPipeline.ps1"

Describe "WaitSampleValidationPipeline.ps1" {
    It "returns a successful terminal pipeline result" {
        $statusInvoker = {
            param($StatusUri, $Headers)
            [pscustomobject]@{
                status = "completed"
                result = "succeeded"
                _links = @{ web = @{ href = "https://dev.azure.com/example/build/42" } }
            }
        }

        $actual = & $waitScript -BuildId 42 -BearerToken "token" -StatusInvoker $statusInvoker

        $actual.BuildId | Should Be 42
        $actual.Result | Should Be "succeeded"
    }

    It "throws when the pipeline completes unsuccessfully" {
        $statusInvoker = {
            param($StatusUri, $Headers)
            [pscustomobject]@{
                status = "completed"
                result = "failed"
                _links = @{ web = @{ href = "https://dev.azure.com/example/build/43" } }
            }
        }
        $caught = $null
        try {
            & $waitScript -BuildId 43 -BearerToken "token" -StatusInvoker $statusInvoker
        } catch { $caught = $_ }

        $caught.Exception.Message | Should Match "completed with result 'failed'"
    }

    It "times out a pipeline that never completes" {
        $statusInvoker = {
            param($StatusUri, $Headers)
            [pscustomobject]@{ status = "inProgress"; result = $null }
        }
        $caught = $null
        try {
            & $waitScript -BuildId 44 -BearerToken "token" -TimeoutMinutes 0 `
                -PollIntervalSeconds 0 -StatusInvoker $statusInvoker
        } catch { $caught = $_ }

        $caught.Exception.Message | Should Match "Timed out waiting"
    }
}
