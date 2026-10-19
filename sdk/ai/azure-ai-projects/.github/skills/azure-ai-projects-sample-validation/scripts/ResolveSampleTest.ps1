# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [Alias("Sample")]
    [string]$SamplePath,

    [string]$PythonExecutable,
    [string]$PackageRoot
)

$ErrorActionPreference = "Stop"
if ($PackageRoot) {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $PackageRoot).Path).FullName
} else {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path).FullName
}
$samplesRoot = Join-Path $packageRoot "samples"

if (-not $PythonExecutable) {
    $windowsVenvPython = Join-Path $packageRoot ".venv\Scripts\python.exe"
    $posixVenvPython = Join-Path $packageRoot ".venv\bin\python"
    if (Test-Path -LiteralPath $windowsVenvPython) {
        $PythonExecutable = $windowsVenvPython
    } elseif (Test-Path -LiteralPath $posixVenvPython) {
        $PythonExecutable = $posixVenvPython
    } else {
        $PythonExecutable = "python"
    }
}

function Resolve-SampleFile {
    param([string]$RequestedPath)

    $candidate = $RequestedPath
    if (-not [System.IO.Path]::IsPathRooted($candidate)) {
        $candidate = Join-Path $packageRoot $candidate
    }
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        return (Get-Item -LiteralPath $candidate).FullName
    }

    $name = [System.IO.Path]::GetFileName($RequestedPath)
    if (-not $name.EndsWith(".py", [System.StringComparison]::OrdinalIgnoreCase)) {
        $name += ".py"
    }
    $sampleMatches = @(Get-ChildItem -Path $samplesRoot -Recurse -File -Filter $name)
    if ($sampleMatches.Count -eq 0) {
        throw "Could not find sample '$RequestedPath' under '$samplesRoot'."
    }
    if ($sampleMatches.Count -gt 1) {
        throw "Sample '$RequestedPath' matched multiple files. Pass a path relative to the package root."
    }
    return $sampleMatches[0].FullName
}

$hasWildcard = [System.Management.Automation.WildcardPattern]::ContainsWildcardCharacters($SamplePath)
$resolvedSample = if ($hasWildcard) { $null } else { Resolve-SampleFile $SamplePath }
$testFiles = @(
    Get-ChildItem -Path (Join-Path $packageRoot "tests\samples") -File -Filter "test_samples*.py" |
        Where-Object { -not $_.Name.EndsWith("_helpers.py") } |
        ForEach-Object { $_.FullName }
)

$temporaryDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("resolve-sample-test-{0}" -f [guid]::NewGuid())
$pluginPath = Join-Path $temporaryDirectory "sample_node_collector.py"
$outputPath = Join-Path $temporaryDirectory "sample-nodes.json"
$pluginSource = @'
import json
import os
from pathlib import Path


def pytest_collection_finish(session):
    records = []
    for item in session.items:
        callspec = getattr(item, "callspec", None)
        if callspec is None:
            continue
        sample_path = callspec.params.get("sample_path")
        if sample_path is None:
            continue
        records.append(
            {
                "samplePath": str(Path(str(sample_path)).resolve()),
                "nodeId": item.nodeid,
            }
        )
    Path(os.environ["AZURE_AI_PROJECTS_SAMPLE_NODE_OUTPUT"]).write_text(
        json.dumps(records), encoding="utf-8"
    )
'@

New-Item -ItemType Directory -Path $temporaryDirectory | Out-Null
[System.IO.File]::WriteAllText($pluginPath, $pluginSource, [System.Text.UTF8Encoding]::new($false))

$oldPythonPath = $env:PYTHONPATH
$oldOutputPath = $env:AZURE_AI_PROJECTS_SAMPLE_NODE_OUTPUT
try {
    $env:PYTHONPATH = if ($oldPythonPath) { "$temporaryDirectory$([System.IO.Path]::PathSeparator)$oldPythonPath" } else { $temporaryDirectory }
    $env:AZURE_AI_PROJECTS_SAMPLE_NODE_OUTPUT = $outputPath
    Push-Location $packageRoot
    try {
        $collectionOutput = @(
            & $PythonExecutable -m pytest --collect-only -q -p sample_node_collector @testFiles `
                --azure_test_run_live=false --azure_skip_live_recording=true 2>&1
        )
        if ($LASTEXITCODE -ne 0) {
            throw "pytest collection failed:`n$($collectionOutput -join [Environment]::NewLine)"
        }
    } finally {
        Pop-Location
    }

    $records = @(Get-Content -LiteralPath $outputPath -Raw | ConvertFrom-Json)
} finally {
    $env:PYTHONPATH = $oldPythonPath
    $env:AZURE_AI_PROJECTS_SAMPLE_NODE_OUTPUT = $oldOutputPath
    Remove-Item -LiteralPath $temporaryDirectory -Recurse -Force -ErrorAction SilentlyContinue
}

$pathComparison = if ($env:OS -eq "Windows_NT") {
    [System.StringComparison]::OrdinalIgnoreCase
} else {
    [System.StringComparison]::Ordinal
}
$normalizedPattern = $SamplePath.Replace("\", "/")
$wildcardPattern = if ($hasWildcard) {
    [System.Management.Automation.WildcardPattern]::new(
        $normalizedPattern,
        [System.Management.Automation.WildcardOptions]::IgnoreCase
    )
} else {
    $null
}

$matchingRecords = @(
    foreach ($record in $records) {
        if (-not (Test-Path -LiteralPath $record.samplePath -PathType Leaf)) {
            continue
        }
        $absoluteSamplePath = (Get-Item -LiteralPath $record.samplePath).FullName
        $isMatch = if ($hasWildcard) {
            $packageRelativePath = [System.IO.Path]::GetRelativePath($packageRoot, $absoluteSamplePath).Replace("\", "/")
            $samplesRelativePath = [System.IO.Path]::GetRelativePath($samplesRoot, $absoluteSamplePath).Replace("\", "/")
            $wildcardPattern.IsMatch($packageRelativePath) -or
                $wildcardPattern.IsMatch($samplesRelativePath) -or
                $wildcardPattern.IsMatch([System.IO.Path]::GetFileName($absoluteSamplePath))
        } else {
            [string]::Equals($absoluteSamplePath, $resolvedSample, $pathComparison)
        }
        if (-not $isMatch) {
            continue
        }

        $normalizedNodeId = $record.nodeId.Replace("\", "/")
        $testsIndex = $normalizedNodeId.IndexOf("tests/")
        if ($testsIndex -ge 0) {
            $normalizedNodeId = $normalizedNodeId.Substring($testsIndex)
        }
        [pscustomobject]@{
            SamplePath = [System.IO.Path]::GetRelativePath($packageRoot, $absoluteSamplePath).Replace("/", "\")
            NodeId = $normalizedNodeId
        }
    }
)

if ($matchingRecords.Count -eq 0) {
    if ($hasWildcard) {
        throw "No collected sample tests match wildcard '$SamplePath'."
    }
    throw "No collected sample test executes '$resolvedSample'. The sample may be excluded from the recorded sample harness."
}

$matchingRecords |
    Sort-Object SamplePath, NodeId -Unique |
    Write-Output
