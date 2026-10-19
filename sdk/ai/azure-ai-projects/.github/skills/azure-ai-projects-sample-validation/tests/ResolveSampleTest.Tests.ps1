# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot

Describe "ResolveSampleTest.ps1" {
    BeforeAll {
        $script:packageRoot = Join-Path $TestDrive "resolver-package"
        New-SyntheticPackage $packageRoot
        $script:uniqueResult = @(
            & $paths.SampleResolver -PackageRoot $packageRoot `
                -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py"
        )
        $script:multipleResults = @(
            & $paths.SampleResolver -PackageRoot $packageRoot `
                -PythonExecutable $paths.PythonExecutable -SamplePath "sample_multiple.py"
        )
        $script:asyncResult = @(
            & $paths.SampleResolver -PackageRoot $packageRoot `
                -PythonExecutable $paths.PythonExecutable -SamplePath "sample_async.py"
        )
        $script:evaluationResult = @(
            & $paths.SampleResolver -PackageRoot $packageRoot `
                -PythonExecutable $paths.PythonExecutable -SamplePath "sample_evaluation.py"
        )
        $script:wildcardResults = @(
            & $paths.SampleResolver -PackageRoot $packageRoot `
                -PythonExecutable $paths.PythonExecutable -SamplePath "samples\*\sample_*.py"
        )
    }

    It "resolves a filename to one synchronous pytest node" {
        $uniqueResult.Count | Should Be 1
        $uniqueResult[0].SamplePath | Should Be "samples\unique\sample_unique.py"
        $uniqueResult[0].NodeId | Should Match "test_samples.py::test_unique\[unique-case\]$"
    }

    It "returns every collected node for a sample" {
        $multipleResults.Count | Should Be 2
        ($multipleResults.NodeId -join "`n") | Should Match "variant-one\]"
        ($multipleResults.NodeId -join "`n") | Should Match "variant-two\]"
    }

    It "resolves async and evaluation harnesses" {
        $asyncResult[0].NodeId | Should Match "test_samples_async.py::test_async\[async-case\]$"
        $evaluationResult[0].NodeId | Should Match "test_samples_evaluations.py::test_evaluation\[evaluation-case\]$"
    }

    It "resolves a wildcard to multiple sample paths and nodes" {
        $wildcardResults.Count | Should Be 8
        @($wildcardResults.SamplePath | Select-Object -Unique).Count | Should Be 7
        ($wildcardResults.SamplePath -join "`n") | Should Match "samples\\unique\\sample_unique.py"
        ($wildcardResults.SamplePath -join "`n") | Should Match "samples\\hosted_agents\\sample_hosted.py"
    }

    It "rejects ambiguous and missing filenames" {
        $ambiguous = $null
        $missing = $null
        try { & $paths.SampleResolver -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "util.py" } catch { $ambiguous = $_ }
        try { & $paths.SampleResolver -PackageRoot $packageRoot -PythonExecutable $paths.PythonExecutable -SamplePath "missing.py" } catch { $missing = $_ }
        $ambiguous | Should Not BeNullOrEmpty
        $missing | Should Not BeNullOrEmpty
    }

    It "rejects a sample absent from the pytest harness" {
        $caught = $null
        try {
            & $paths.SampleResolver -PackageRoot $packageRoot `
                -PythonExecutable $paths.PythonExecutable -SamplePath "sample_uncollected.py"
        } catch { $caught = $_ }
        $caught | Should Not BeNullOrEmpty
    }

    It "reports pytest collection failures" {
        $brokenRoot = Join-Path $TestDrive "broken-resolver-package"
        New-SyntheticPackage $brokenRoot
        "this is not valid python !!!" | Set-Content -LiteralPath (Join-Path $brokenRoot "tests\samples\test_samples.py") -Encoding UTF8
        $caught = $null
        try {
            & $paths.SampleResolver -PackageRoot $brokenRoot `
                -PythonExecutable $paths.PythonExecutable -SamplePath "sample_unique.py"
        } catch { $caught = $_ }
        $caught.Exception.Message | Should Match "pytest collection failed"
    }
}