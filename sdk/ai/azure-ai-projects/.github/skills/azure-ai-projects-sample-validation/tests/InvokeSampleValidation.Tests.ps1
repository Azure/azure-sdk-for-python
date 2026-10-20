# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot

Describe "InvokeSampleValidation.ps1 plan and guards" {
    BeforeAll {
        $script:packageRoot = Join-Path $TestDrive "runner-unit-package"
        New-SyntheticPackage $packageRoot
        $script:conflictCheckScript = Join-Path $packageRoot "synthetic-recording-conflict-check.ps1"
        $script:recordAndPlaybackPlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -SamplePath "sample_unique.py" -Mode "record-and-playback")
        $script:recordOnlyPlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -RecordingConflictCheckScript $conflictCheckScript -SamplePath "sample_unique.py" -Mode "record-only")
        $script:playbackOnlyPlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py" -Mode "playback-only")
        $script:livePlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py" -Mode "live-test-locally")
        $script:pipelinePlan = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -PipelineQueueScript (Join-Path $packageRoot "synthetic-pipeline-queue.ps1") -PipelineWaitScript (Join-Path $packageRoot "synthetic-pipeline-wait.ps1") -PipelineSourceBranch "topic" -SamplePath "sample_unique.py" -Mode "live-test-by-pipeline")
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
        ($pipelinePlan -join "`n") | Should Match "Pipeline source branch: refs/heads/topic"
        ($pipelinePlan -join "`n") | Should Match "pipeline command: queue definition 8392"
    }

    It "preserves wildcard selections in every execution mode" {
        foreach ($mode in @("record-and-playback", "record-only", "playback-only", "live-test-locally", "live-test-by-pipeline")) {
            $arguments = @{
                PackageRoot = $packageRoot
                PythonExecutable = $paths.PythonExecutable
                RecordingConflictCheckScript = $conflictCheckScript
                PipelineQueueScript = (Join-Path $packageRoot "synthetic-pipeline-queue.ps1")
                PipelineWaitScript = (Join-Path $packageRoot "synthetic-pipeline-wait.ps1")
                PipelineSourceBranch = "topic"
                SamplePattern = "samples\multiple\sample_*.py"
                TestPattern = "*variant-*"
                Mode = $mode
            }
            $actual = @(& $paths.SampleTestRunner @arguments) -join "`n"
            $actual | Should Match "variant-one"
            $actual | Should Match "variant-two"
        }
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
        $commandPreview | Should Match "--direct_required=<environment value>"
    }

    It "applies repeatable environment overrides before mapping values" {
        $actual = @(
            & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable `
                -SamplePath "sample_unique.py" -Mode "playback-only" `
                -EnvironmentVariable @("DIRECT_REQUIRED=override-direct", "EXTRA_SETTING=extra=value")
        )
        $text = $actual -join "`n"
        $text | Should Match "DIRECT_REQUIRED=override-direct \[command line\]"
        $text | Should Match "EXTRA_SETTING=extra=value \[command line\]"
        $text | Should Match "HELPER_REQUIRED=real-helper-value \[\.env\]"
        $text | Should Match "CLI values loaded: 2; process values loaded: 3"
        $commandPreview = @($actual | Where-Object { $_ -like "* command: *" }) -join "`n"
        $commandPreview | Should Not Match "override-direct|extra=value"
    }

    It "redacts effective values when requested by pipeline execution" {
        $actual = @(
            & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable `
                -SamplePath "sample_unique.py" -Mode "playback-only" -HideEnvironmentValues
        ) -join "`n"
        $actual | Should Match "DIRECT_REQUIRED=<redacted> \[\.env\]"
        $actual | Should Not Match "real-direct-value|real-helper-value|real-harness-value"
    }

    It "rejects malformed environment overrides" {
        $caught = $null
        try {
            & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable `
                -SamplePath "sample_unique.py" -Mode "playback-only" -EnvironmentVariable "NOT-AN-ASSIGNMENT"
        } catch { $caught = $_ }
        $caught.Exception.Message | Should Match "NAME=VALUE"
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

    It "requires selection and pipeline confirmations for ADO execution" {
        $selectionError = $null
        $pipelineError = $null
        $arguments = @{
            PackageRoot = $packageRoot
            PythonExecutable = $paths.PythonExecutable
            PipelineQueueScript = (Join-Path $packageRoot "synthetic-pipeline-queue.ps1")
            PipelineWaitScript = (Join-Path $packageRoot "synthetic-pipeline-wait.ps1")
            PipelineSourceBranch = "topic"
            PipelineBearerToken = "synthetic-token"
            SamplePath = "sample_unique.py"
            Mode = "live-test-by-pipeline"
            Run = $true
        }
        try { & $paths.SampleTestRunner @arguments } catch { $selectionError = $_ }
        $arguments.ConfirmSelection = $true
        try { & $paths.SampleTestRunner @arguments } catch { $pipelineError = $_ }
        $selectionError.Exception.Message | Should Match "selection was not confirmed"
        $pipelineError.Exception.Message | Should Match "Pipeline execution contacts Azure"
    }

    It "selects an exact node and includes all matching nodes by default" {
        $actual = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_multiple.py" -NodeId "tests/samples/test_samples.py::test_multiple[variant-one]" -Mode "playback-only")
        ($actual -join "`n") | Should Match "variant-one"
        $selectedNodes = @(& $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_multiple.py" -Mode "playback-only")
        ($selectedNodes -join "`n") | Should Match "variant-one"
        ($selectedNodes -join "`n") | Should Match "variant-two"
    }

    It "rejects an invalid explicit node" {
        $caught = $null
        try { & $paths.SampleTestRunner -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "sample_multiple.py" -NodeId "tests/samples/test_samples.py::missing[node]" -Mode "playback-only" } catch { $caught = $_ }
        $caught.Exception.Message | Should Match "does not match any nodes"
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