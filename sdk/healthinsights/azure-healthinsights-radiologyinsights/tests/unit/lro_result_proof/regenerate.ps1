# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# -------------------------------------------------------------------------
#Requires -Version 7.0
param(
    [Parameter(Mandatory)][string]$LocalSpecDirectory,
    [Parameter(Mandatory)][string]$TcgcArchive,
    [Parameter(Mandatory)][string]$AzureCoreArchive,
    [Parameter(Mandatory)][string]$CompilerArchive,
    [Parameter(Mandatory)][string]$OutputDirectory
)

$ErrorActionPreference = "Stop"
$repoRoot = & git -C $PSScriptRoot rev-parse --show-toplevel
if ($LASTEXITCODE) { throw "Cannot find the SDK repository root." }
$repoRoot = [IO.Path]::GetFullPath($repoRoot)
$output = [IO.Path]::GetFullPath($OutputDirectory)
$artifacts = [IO.Path]::GetFullPath((Join-Path $repoRoot ".artifacts")) + [IO.Path]::DirectorySeparatorChar
if (-not $output.StartsWith($artifacts, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Use a private output directory below the SDK repository's .artifacts directory."
}
$localSpec = (Resolve-Path $LocalSpecDirectory).Path
$cli = Join-Path $repoRoot "eng\common\tsp-client\node_modules\@azure-tools\typespec-client-generator-cli\dist\index.js"
if (-not (Test-Path $cli)) { throw "Install the repository's eng\common\tsp-client dependencies first." }

$manifestPath = Join-Path $repoRoot "eng\emitter-package.json"
$lockPath = Join-Path $repoRoot "eng\emitter-package-lock.json"
$originalManifest = [IO.File]::ReadAllBytes($manifestPath)
$originalLock = [IO.File]::ReadAllBytes($lockPath)
$manifest = [IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json -AsHashtable
$pins = @{
    "@azure-tools/typespec-client-generator-core" = $TcgcArchive
    "@azure-tools/typespec-azure-core" = $AzureCoreArchive
    "@typespec/compiler" = $CompilerArchive
}
foreach ($name in $pins.Keys) {
    $archive = (Resolve-Path $pins[$name]).Path
    $manifest.devDependencies[$name] = "file:$($archive.Replace('\', '/'))"
}
$manifest["overrides"] = @{
    "@azure-tools/typespec-client-generator-core" = '$@azure-tools/typespec-client-generator-core'
    "@azure-tools/typespec-azure-core" = '$@azure-tools/typespec-azure-core'
    "@typespec/compiler" = '$@typespec/compiler'
}

try {
    New-Item -ItemType Directory -Force $output | Out-Null
    Copy-Item (Join-Path $repoRoot "sdk\healthinsights\azure-healthinsights-radiologyinsights\tsp-location.yaml") $output
    [IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 20) + "`n")
    & node $cli generate-lock-file --output-dir $output "--npm-args=--package-lock-only --ignore-scripts --no-audit --no-fund" --no-prompt
    if ($LASTEXITCODE) { throw "Generating the matching emitter lock failed: $LASTEXITCODE" }
    & node $cli update --output-dir $output --local-spec-repo $localSpec --emitter-options "api-version=2024-10-01;generate-test=false;generate-sample=false;clear-output-folder=false;generate-packaging-files=true" --save-inputs --no-prompt
    if ($LASTEXITCODE) { throw "tsp-client update failed: $LASTEXITCODE" }
}
finally {
    [IO.File]::WriteAllBytes($manifestPath, $originalManifest)
    [IO.File]::WriteAllBytes($lockPath, $originalLock)
}
