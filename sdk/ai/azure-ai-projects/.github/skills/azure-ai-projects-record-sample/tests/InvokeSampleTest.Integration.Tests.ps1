# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot

Describe "InvokeSampleTest.ps1 integration" {
    BeforeAll {
        $script:packageRoot = Join-Path $TestDrive "runner-integration-package"
        New-SyntheticPackage $packageRoot
        $script:conflictCheckScript = Join-Path $packageRoot "synthetic-recording-conflict-check.ps1"
        $script:cleanupScript = Join-Path $packageRoot "synthetic-recording-cleanup.ps1"
    }

    It "executes playback without live approval" {
        $actual = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py" -Mode "playback-only" -Run)
        ($actual -join "`n") | Should Match "playback result: 0"
    }

    It "executes record-only and live modes with approval" {
        $cachePath = Join-Path $packageRoot ".pytest_cache"
        New-Item -ItemType Directory -Path $cachePath -Force | Out-Null
        $record = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -RecordingCleanupScript $cleanupScript -SamplePath "sample_unique.py" -Mode "record-only" -Run -ConfirmSelection -ConfirmRecording)
        Remove-Item -LiteralPath (Join-Path $packageRoot "recording-conflict-check-called.txt") -Force
        $live = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py" -Mode "live-test-locally" -Run -ConfirmSelection -ConfirmLive)
        ($record -join "`n") | Should Match "record result: 0"
        ($live -join "`n") | Should Match "live result: 0"
        (Test-Path -LiteralPath (Join-Path $packageRoot "recording-conflict-check-called.txt")) | Should Be $false
    }

    It "executes record then playback in order" {
        $actual = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -RecordingCleanupScript $cleanupScript -SamplePath "sample_unique.py" -Mode "record-and-playback" -Run -ConfirmSelection -ConfirmRecording)
        $text = $actual -join "`n"
        $text.IndexOf("record result: 0") | Should BeLessThan $text.IndexOf("playback result: 0")
    }

    It "continues to playback when recording fails" {
        $marker = Join-Path $packageRoot "playback-after-record-failure.txt"
        $caught = $null
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -RecordingCleanupScript $cleanupScript -SamplePath "sample_record_failure.py" -Mode "record-and-playback" -Run -ConfirmSelection -ConfirmRecording } catch { $caught = $_ }
        $caught.Exception.Message | Should Match "record=1"
        (Test-Path -LiteralPath $marker) | Should Be $true
    }

    It "propagates playback failures and restores process environment" {
        $original = $env:FAILURE_PROCESS_VALUE
        $env:FAILURE_PROCESS_VALUE = "before-run"
        $caught = $null
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_playback_failure.py" -Mode "playback-only" -Run } catch { $caught = $_ } finally { $restored = $env:FAILURE_PROCESS_VALUE; $env:FAILURE_PROCESS_VALUE = $original }
        $caught.Exception.Message | Should Match "playback=1"
        $restored | Should Be "before-run"
    }

    It "repairs hosted-agent recordings before playback" {
        $marker = Join-Path $packageRoot "tests\samples\repair-called.txt"
        $actual = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -RecordingCleanupScript $cleanupScript -SamplePath "sample_hosted.py" -Mode "record-and-playback" -Run -ConfirmSelection -ConfirmRecording)
        (Test-Path -LiteralPath $marker) | Should Be $true
        ($actual -join "`n") | Should Match "repair result: 0"
        ($actual -join "`n") | Should Match "playback result: 0"
    }
}