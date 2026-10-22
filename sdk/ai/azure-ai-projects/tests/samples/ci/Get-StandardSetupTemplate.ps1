# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.0

[CmdletBinding()]
param([Parameter(Mandatory)] [string] $OutputDirectory)

$ErrorActionPreference = 'Stop'
$sourceLock = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'infra/standard-setup.lock.json') -Raw | ConvertFrom-Json -AsHashtable
if ($sourceLock.repository -cne 'microsoft-foundry/foundry-samples' -or $sourceLock.commit -notmatch '^[a-f0-9]{40}$') {
    throw 'Invalid official Standard setup source pin.'
}
$baseUri = 'https://raw.githubusercontent.com/{0}/{1}/{2}/' -f $sourceLock.repository, $sourceLock.commit, $sourceLock.path
$client = [Net.Http.HttpClient]::new()
try {
    foreach ($entry in $sourceLock.files.GetEnumerator()) {
        if ($entry.Key -notmatch '^(main\.bicep|modules-standard/[a-z-]+\.bicep)$' -or $entry.Value -notmatch '^[a-f0-9]{64}$') {
            throw 'Invalid Bicep source path or checksum in the source pin.'
        }
        $bytes = $client.GetByteArrayAsync($baseUri + $entry.Key).GetAwaiter().GetResult()
        $checksum = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
        if ($checksum -cne $entry.Value) {
            throw "Official Bicep source checksum mismatch: $($entry.Key)"
        }
        $destination = Join-Path $OutputDirectory $entry.Key
        $null = New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force
        [IO.File]::WriteAllBytes($destination, $bytes)
    }
} finally {
    $client.Dispose()
}
Write-Host ('Verified {0} official Standard setup Bicep files at commit {1}.' -f $sourceLock.files.Count, $sourceLock.commit)
return (Join-Path $OutputDirectory 'main.bicep')
