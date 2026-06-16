# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

<#
.SYNOPSIS
Extracts Python APIView metadata from API markdown and writes api.metadata.yml.

.DESCRIPTION
Reads an API markdown file, extracts parser and Python runtime versions from the
Python APIView metadata header, removes that header from the markdown, trims leading
blank lines from the markdown body, and writes api.metadata.yml beside the markdown file.

.PARAMETER ApiMarkdownPath
Optional. Path to API markdown file. If omitted, api.md will be resolved from OutputPath.

.PARAMETER OutputPath
Optional. Directory containing API markdown output. Defaults to current directory.

.EXAMPLE
./Extract-APIViewMetadata-Python.ps1 -OutputPath ./sdk/template/azure-template

.EXAMPLE
./Extract-APIViewMetadata-Python.ps1 -ApiMarkdownPath ./sdk/template/azure-template/api.md
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ApiMarkdownPath,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "."
)

Set-StrictMode -Version 3
$ErrorActionPreference = 'Stop'

function Resolve-ApiMarkdownPath {
    param(
        [string]$ProvidedPath,
        [string]$OutputDirectory
    )

    if ($ProvidedPath) {
        return $ProvidedPath
    }

    $resolvedOutput = Resolve-Path -LiteralPath $OutputDirectory -ErrorAction Stop
    $apiLower = Join-Path $resolvedOutput.Path "api.md"
    if (Test-Path -LiteralPath $apiLower -PathType Leaf) {
        return $apiLower
    }

    throw "Could not find API markdown file in '$OutputDirectory'. Expected api.md."
}

function Trim-LeadingBlankLines {
    param([string[]]$Lines)

    $start = 0
    while ($start -lt $Lines.Count -and [string]::IsNullOrWhiteSpace($Lines[$start])) {
        $start++
    }

    if ($start -eq 0) {
        return $Lines
    }

    if ($start -ge $Lines.Count) {
        return @()
    }

    return $Lines[$start..($Lines.Count - 1)]
}

function Get-Sha256Hex {
    param([string]$Text)

    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        $hashBytes = $sha256.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($hashBytes)).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha256.Dispose()
    }
}

$resolvedApiPath = Resolve-ApiMarkdownPath -ProvidedPath $ApiMarkdownPath -OutputDirectory $OutputPath
if (-not (Test-Path -LiteralPath $resolvedApiPath -PathType Leaf)) {
    throw "API markdown file not found: $resolvedApiPath"
}

$metadataPattern = '^# Package is parsed using apiview-stub-generator\(version:([^\)]+)\), Python version:\s*([^\s]+)\s*$'

$fileText = Get-Content -LiteralPath $resolvedApiPath -Raw
$lineEnding = if ($fileText -match "`r`n") { "`r`n" } else { "`n" }
$lines = $fileText -split '\r?\n'

$metadata = [ordered]@{}
$filtered = [System.Collections.Generic.List[string]]::new()

foreach ($line in $lines) {
    $match = [regex]::Match($line, $metadataPattern)
    if ($match.Success) {
        # Alphabetical keys in output YAML.
        $metadata['parserVersion'] = $match.Groups[1].Value
        $metadata['pythonVersion'] = $match.Groups[2].Value
        continue
    }

    $filtered.Add($line)
}

# Remove blank lines after opening fence so markdown body starts at namespace.
if ($filtered.Count -gt 0 -and $filtered[0].StartsWith('```')) {
    $fence = $filtered[0]
    $body = Trim-LeadingBlankLines -Lines @($filtered | Select-Object -Skip 1)
    $rewritten = [System.Collections.Generic.List[string]]::new()
    $rewritten.Add($fence)
    foreach ($line in $body) {
        $rewritten.Add($line)
    }
    $filtered = $rewritten
}
else {
    $trimmed = Trim-LeadingBlankLines -Lines @($filtered)
    $filtered = [System.Collections.Generic.List[string]]::new($trimmed)
}

$normalizedLinesForHash = @($filtered | ForEach-Object { $_.TrimEnd() })
$newlineForHash = [string][char]10
$normalizedTextForHash = $normalizedLinesForHash -join $newlineForHash
$metadata['apiMdSha256'] = Get-Sha256Hex -Text $normalizedTextForHash

Set-Content -LiteralPath $resolvedApiPath -Value ($filtered -join $lineEnding) -NoNewline -Encoding utf8
Write-Host "Updated markdown: $resolvedApiPath"

$metadataPath = Join-Path (Split-Path -Parent $resolvedApiPath) "api.metadata.yml"
if ($metadata.Count -gt 0) {
    $yamlLines = [System.Collections.Generic.List[string]]::new()
    foreach ($key in ($metadata.Keys | Sort-Object)) {
        $yamlLines.Add(("{0}: {1}" -f $key, $metadata[$key]))
    }

    Set-Content -LiteralPath $metadataPath -Value ($yamlLines -join $lineEnding) -Encoding utf8
    Write-Host "Generated metadata: $metadataPath"
}
elseif (Test-Path -LiteralPath $metadataPath) {
    Remove-Item -LiteralPath $metadataPath -Force
    Write-Host "Removed stale metadata: $metadataPath"
}
