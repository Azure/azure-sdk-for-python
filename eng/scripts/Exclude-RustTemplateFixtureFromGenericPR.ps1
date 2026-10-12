# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

param (
    [string] $PackagePropertiesFolder = ''
)

$ErrorActionPreference = 'Stop'

if ($PackagePropertiesFolder -and (Test-Path $PackagePropertiesFolder)) {
    Get-ChildItem -Path $PackagePropertiesFolder -Recurse -File -Filter 'azure-template-three.json' |
        ForEach-Object {
            Write-Host 'Generic PR builds do not enable the Rust toolchain setup; excluding azure-template-three, which template CI validates.'
            Remove-Item -LiteralPath $_.FullName
        }
}

# Matrix jobs can already have TargetingString set and skip normal targeting resolution.
if ($env:TARGETINGSTRING) {
    $targets = @($env:TARGETINGSTRING.Split(',') | ForEach-Object { $_.Trim() } |
        Where-Object { $_ -and $_ -ne 'azure-template-three' })
    if ($targets.Count -eq 0) {
        $targets = @('null')
    }
    Write-Host "##vso[task.setvariable variable=TargetingString;]$($targets -join ',')"
}
