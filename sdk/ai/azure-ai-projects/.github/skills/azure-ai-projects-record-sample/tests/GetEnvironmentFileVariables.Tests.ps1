# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

. (Join-Path $PSScriptRoot "TestHelpers.ps1")
$paths = Get-RecordSampleTestPaths $PSScriptRoot

Describe "GetEnvironmentFileVariables.ps1" {
    BeforeAll {
        $script:envFile = Join-Path $TestDrive ".env"
        @'
# ignored comment
FIRST=old-value
EMPTY=
export EXPORTED="quoted value"
MULTILINE="first line
second line"
FIRST=effective-value
BARE
'@ | Set-Content -LiteralPath $envFile -Encoding UTF8
    }

    It "returns names in bottom-to-top effective assignment order" {
        $actual = @(& $paths.EnvironmentFileScanner -EnvFile $envFile -PythonExecutable $paths.PythonExecutable)
        ($actual -join ",") | Should Be "BARE,FIRST,MULTILINE,EXPORTED,EMPTY"
    }

    It "returns last duplicate values and source lines" {
        $actual = @(
            & $paths.EnvironmentFileScanner -EnvFile $envFile `
                -PythonExecutable $paths.PythonExecutable -IncludeValues
        )
        $first = @($actual | Where-Object { $_.Name -eq "FIRST" })
        $multiline = @($actual | Where-Object { $_.Name -eq "MULTILINE" })
        $first.Count | Should Be 1
        $first[0].Value | Should Be "effective-value"
        $first[0].LineNumber | Should Be 7
        $multiline[0].Value | Should Be ("first line", "second line" -join "`n")
    }

    It "uses the package-root .env by default" {
        $packageRoot = Join-Path $TestDrive "default-env-package"
        New-Item -ItemType Directory -Path $packageRoot | Out-Null
        "DEFAULT_NAME=default-value" | Set-Content -LiteralPath (Join-Path $packageRoot ".env") -Encoding UTF8
        $actual = @(
            & $paths.EnvironmentFileScanner -PackageRoot $packageRoot `
                -PythonExecutable $paths.PythonExecutable
        )
        ($actual -join ",") | Should Be "DEFAULT_NAME"
    }

    It "returns no names for an empty environment file" {
        $emptyEnv = Join-Path $TestDrive "empty.env"
        "# no assignments" | Set-Content -LiteralPath $emptyEnv -Encoding UTF8
        $actual = @(& $paths.EnvironmentFileScanner -EnvFile $emptyEnv -PythonExecutable $paths.PythonExecutable)
        $actual.Count | Should Be 0
    }

    It "rejects a missing environment file" {
        $caught = $null
        try {
            & $paths.EnvironmentFileScanner -EnvFile (Join-Path $TestDrive "missing.env") `
                -PythonExecutable $paths.PythonExecutable
        } catch { $caught = $_ }
        $caught | Should Not BeNullOrEmpty
    }

    It "reports a Python execution failure" {
        $caught = $null
        try {
            & $paths.EnvironmentFileScanner -EnvFile $envFile `
                -PythonExecutable (Join-Path $TestDrive "missing-python.exe")
        } catch { $caught = $_ }
        $caught | Should Not BeNullOrEmpty
    }
}