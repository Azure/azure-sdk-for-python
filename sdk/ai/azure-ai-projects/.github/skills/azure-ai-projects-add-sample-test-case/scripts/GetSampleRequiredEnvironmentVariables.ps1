# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [Alias("Sample")]
    [string[]]$SamplePath,

    [string]$PackageRoot
)

$ErrorActionPreference = "Stop"
if ($PackageRoot) {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $PackageRoot).Path).FullName
} else {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path).FullName
}
$samplesRoot = Join-Path $packageRoot "samples"

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

$files = if ($SamplePath) {
    @($SamplePath | ForEach-Object { Resolve-SampleFile $_ })
} else {
    @(Get-ChildItem -Path $samplesRoot -Recurse -File -Filter "*.py" | ForEach-Object { $_.FullName })
}

$patterns = @(
    'os\.environ\s*\[\s*["''](?<name>[A-Z][A-Z0-9_]*)["'']\s*\](?!\s*=)',
    '(?:os\.environ\.get|os\.getenv)\s*\(\s*["''](?<name>[A-Z][A-Z0-9_]*)["'']\s*\)(?!\s*or\b)',
    'get_required_env_var\s*\(\s*["''](?<name>[A-Z][A-Z0-9_]*)["'']\s*\)'
)

$names = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($file in $files) {
    $content = Get-Content -LiteralPath $file -Raw
    foreach ($pattern in $patterns) {
        foreach ($match in [regex]::Matches($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)) {
            $null = $names.Add($match.Groups["name"].Value)
        }
    }
}

$names | Sort-Object
