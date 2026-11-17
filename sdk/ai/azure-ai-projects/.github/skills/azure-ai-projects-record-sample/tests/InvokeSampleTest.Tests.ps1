# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot

Describe "InvokeSampleTest.ps1 plan and guards" {
    BeforeAll {
        $script:packageRoot = Join-Path $TestDrive "runner-unit-package"
        New-SyntheticPackage $packageRoot
        $script:conflictCheckScript = Join-Path $packageRoot "synthetic-recording-conflict-check.ps1"
        $script:recordAndPlaybackPlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -SamplePath "sample_unique.py" -Mode "record-and-playback")
        $script:recordOnlyPlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -SamplePath "sample_unique.py" -Mode "record-only")
        $script:playbackOnlyPlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py" -Mode "playback-only")
        $script:livePlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py" -Mode "live-test-locally")
    }

    It "plans record followed by playback when explicitly selected" {
        ($recordAndPlaybackPlan -join "`n") | Should Match "Mode: record-and-playback"
        ($recordAndPlaybackPlan -join "`n") | Should Match "Steps: record, playback"
    }

    It "rejects an omitted mode" {
        $caught = $null
        try {
            & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable `
                -SamplePath "sample_unique.py"
        } catch { $caught = $_ }
        $caught.Exception.Message | Should Match "Mode is required"
    }

    It "rejects the retired live-without-recording mode name" {
        $caught = $null
        try {
            & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable `
                -SamplePath "sample_unique.py" -Mode "live-without-recording"
        } catch { $caught = $_ }
        $caught | Should Not BeNullOrEmpty
    }

    It "maps explicit modes to exact flags" {
        ($recordOnlyPlan -join "`n") | Should Match "--azure_test_run_live=true --azure_skip_live_recording=false"
        ($playbackOnlyPlan -join "`n") | Should Match "--azure_test_run_live=false --azure_skip_live_recording=true"
        ($livePlan -join "`n") | Should Match "--azure_test_run_live=true --azure_skip_live_recording=true"
    }

    It "displays effective values while redacting command arguments" {
        $text = $recordAndPlaybackPlan -join "`n"
        $text | Should Match "Harness-supplied: HARNESS_VALUE"
        $text | Should Match "Required: DIRECT_REQUIRED, HELPER_REQUIRED, LLM_VALIDATION_PROJECT_ENDPOINT"
        $text | Should Match "DIRECT_REQUIRED=real-direct-value"
        $text | Should Match "HARNESS_VALUE=real-harness-value"
        $text | Should Match "HELPER_REQUIRED=real-helper-value"
        $text | Should Match "LLM_VALIDATION_PROJECT_ENDPOINT=https://validation.example.test/api/projects/example"
        $text | Should Match "CLI values loaded: 2; process values loaded: 2"
        $commandPreview = @($recordAndPlaybackPlan | Where-Object { $_ -like "* command: *" }) -join "`n"
        $commandPreview | Should Not Match "real-direct-value|real-helper-value|real-harness-value"
        $commandPreview | Should Match "--direct_required=<from .env>"
    }

    It "requires selection and action confirmations for recording and live execution" {
        $recordSelectionError = $null
        $liveSelectionError = $null
        $recordError = $null
        $liveError = $null
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -SamplePath "sample_unique.py" -Mode "record-only" -Run } catch { $recordSelectionError = $_ }
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py" -Mode "live-test-locally" -Run } catch { $liveSelectionError = $_ }
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -SamplePath "sample_unique.py" -Mode "record-only" -Run -ConfirmSelection } catch { $recordError = $_ }
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py" -Mode "live-test-locally" -Run -ConfirmSelection } catch { $liveError = $_ }
        $recordSelectionError.Exception.Message | Should Match "selection was not confirmed"
        $liveSelectionError.Exception.Message | Should Match "selection was not confirmed"
        $recordError.Exception.Message | Should Match "Recording may modify files"
        $liveError.Exception.Message | Should Match "Live execution contacts Azure"
    }

    It "selects a valid explicit node and rejects missing selection" {
        $actual = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_multiple.py" -NodeId "tests/samples/test_samples.py::test_multiple[variant-one]" -Mode "playback-only")
        ($actual -join "`n") | Should Match "variant-one"
        $caught = $null
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_multiple.py" -Mode "playback-only" } catch { $caught = $_ }
        $caught.Exception.Message | Should Match "Multiple pytest nodes"
    }

    It "rejects an invalid explicit node" {
        $caught = $null
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_multiple.py" -NodeId "tests/samples/test_samples.py::missing[node]" -Mode "playback-only" } catch { $caught = $_ }
        $caught.Exception.Message | Should Match "requested node id does not execute"
    }

    It "reports missing and empty required values" {
        $incompleteEnv = Join-Path $TestDrive "incomplete.env"
        "DIRECT_REQUIRED=" | Set-Content -LiteralPath $incompleteEnv -Encoding UTF8
        $actual = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -EnvFile $incompleteEnv -SamplePath "sample_unique.py" -Mode "playback-only")
        $text = $actual -join "`n"
        $text | Should Match "Missing: HELPER_REQUIRED, LLM_VALIDATION_PROJECT_ENDPOINT"
        $text | Should Match "Empty: DIRECT_REQUIRED"
        $text | Should Match "Environment variables used: <none>"
    }
}