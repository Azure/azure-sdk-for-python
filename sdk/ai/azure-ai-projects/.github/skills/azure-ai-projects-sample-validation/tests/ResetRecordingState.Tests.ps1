# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot

Describe "ResetRecordingState.ps1" {
    It "stops only test proxy processes and deletes pytest cache" {
        $packageRoot = Join-Path $TestDrive "cleanup-package"
        $cachePath = Join-Path $packageRoot ".pytest_cache"
        New-Item -ItemType Directory -Path $cachePath -Force | Out-Null
        "cache" | Set-Content -LiteralPath (Join-Path $cachePath "marker.txt") -Encoding UTF8

        $stoppedNames = [System.Collections.Generic.List[string]]::new()
        $provider = {
            @(
                [pscustomobject]@{ ProcessName = "testproxy" },
                [pscustomobject]@{ ProcessName = "prefix-testproxy-child" },
                [pscustomobject]@{ ProcessName = "test-proxy" },
                [pscustomobject]@{ ProcessName = "test_proxy_worker" },
                [pscustomobject]@{ ProcessName = "python" }
            )
        }.GetNewClosure()
        $stopper = {
            param($Processes)
            foreach ($process in $Processes) {
                $stoppedNames.Add($process.ProcessName)
            }
        }.GetNewClosure()

        & $paths.RecordingStateReset -PackageRoot $packageRoot `
            -ProcessProvider $provider -ProcessStopper $stopper

        ($stoppedNames -join ",") | Should Be "testproxy,prefix-testproxy-child,test-proxy,test_proxy_worker"
        (Test-Path -LiteralPath $cachePath) | Should Be $false
    }

    It "succeeds when there are no matching processes or cache" {
        $packageRoot = Join-Path $TestDrive "empty-cleanup-package"
        New-Item -ItemType Directory -Path $packageRoot -Force | Out-Null
        $provider = { @([pscustomobject]@{ ProcessName = "python" }) }.GetNewClosure()
        $stopper = { param($Processes) throw "Process stopper should not be called." }

        & $paths.RecordingStateReset -PackageRoot $packageRoot `
            -ProcessProvider $provider -ProcessStopper $stopper
    }
}