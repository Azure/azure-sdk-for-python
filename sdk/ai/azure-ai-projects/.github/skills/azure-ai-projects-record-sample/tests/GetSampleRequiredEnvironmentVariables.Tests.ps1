# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot

Describe "GetSampleRequiredEnvironmentVariables.ps1" {
    BeforeAll {
        $script:packageRoot = Join-Path $TestDrive "scanner-package"
        New-SyntheticPackage $packageRoot
    }

    It "returns the required variables for a selected sample" {
        $actual = @(& $paths.EnvironmentScanner -PackageRoot $packageRoot -SamplePath "sample_unique.py")
        ($actual -join ",") | Should Be "DIRECT_REQUIRED,HELPER_REQUIRED"
    }

    It "excludes writes, defaults, and fallbacks" {
        $actual = @(& $paths.EnvironmentScanner -PackageRoot $packageRoot -SamplePath "sample_unique.py")
        ($actual -join ",") | Should Not Match "ASSIGNED_ONLY|OPTIONAL_WITH_DEFAULT|OPTIONAL_WITH_FALLBACK"
    }

    It "returns sorted unique names for the full sample tree" {
        $actual = @(& $paths.EnvironmentScanner -PackageRoot $packageRoot)
        $sortedUnique = @($actual | Sort-Object -Unique)
        $actual.Count | Should Be 6
        ($actual -join "`n") | Should Be ($sortedUnique -join "`n")
    }

    It "merges multiple selected samples" {
        $actual = @(
            & $paths.EnvironmentScanner -PackageRoot $packageRoot `
                -SamplePath "sample_unique", "sample_async.py"
        )
        ($actual -join ",") | Should Be "ASYNC_REQUIRED,DIRECT_REQUIRED,HELPER_REQUIRED"
    }

    It "rejects an ambiguous filename" {
        $caught = $null
        try { & $paths.EnvironmentScanner -PackageRoot $packageRoot -SamplePath "util.py" } catch { $caught = $_ }
        $caught | Should Not BeNullOrEmpty
    }

    It "rejects a missing sample" {
        $caught = $null
        try { & $paths.EnvironmentScanner -PackageRoot $packageRoot -SamplePath "missing.py" } catch { $caught = $_ }
        $caught | Should Not BeNullOrEmpty
    }
}