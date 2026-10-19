# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$PackageRoot,
    [scriptblock]$ProcessProvider = { Get-Process },
    [scriptblock]$ProcessStopper = { param($Processes) $Processes | Stop-Process -Force }
)

$ErrorActionPreference = "Stop"
if ($PackageRoot) {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $PackageRoot).Path).FullName
} else {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path).FullName
}

$testProxyProcesses = @(
    & $ProcessProvider | Where-Object {
        ($_.ProcessName -replace "[-_ ]", "") -like "*testproxy*"
    }
)
if ($testProxyProcesses.Count -gt 0) {
    & $ProcessStopper $testProxyProcesses
}

Remove-Item -Recurse -Force (Join-Path $packageRoot ".pytest_cache") -ErrorAction SilentlyContinue