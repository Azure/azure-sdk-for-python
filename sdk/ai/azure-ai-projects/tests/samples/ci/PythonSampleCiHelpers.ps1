# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

# Python-only adapter. Shared provisioning and cleanup must not import this file.
function Read-SampleManifest {
    param([Parameter(Mandatory)] [string] $Path, [Parameter(Mandatory)] [string] $PackageRoot)

    $manifest = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -AsHashtable
    if ($manifest['schemaVersion'] -ne 1 -or @($manifest['tests']).Count -eq 0) {
        throw 'The sample manifest is empty or has an unsupported schema.'
    }
    foreach ($test in $manifest.tests) {
        if ($test['node_id'] -notmatch '^tests/samples/test_samples(?:_async)?\.py::TestSamples(?:Async)?::\w+\[[^\r\n]+\]$') {
            throw 'Manifest contains a node outside the sync/async sample test harness.'
        }
        $samplePath = [IO.Path]::GetFullPath((Join-Path $PackageRoot $test.sample_path))
        $sampleRoot = [IO.Path]::GetFullPath((Join-Path $PackageRoot 'samples')) + [IO.Path]::DirectorySeparatorChar
        if (-not $samplePath.StartsWith($sampleRoot, [StringComparison]::OrdinalIgnoreCase) -or
            -not (Test-Path -LiteralPath $samplePath -PathType Leaf)) {
            throw 'Manifest sample path must identify an existing file under samples/.'
        }
    }
    return $manifest
}

function Assert-PythonSamplePartition {
    param([Parameter(Mandatory)] [hashtable[]] $Plans)

    $nodes = @()
    foreach ($plan in $Plans) {
        $selected = @($plan['selectedTests'] | Where-Object { $null -ne $_ })
        if ($selected.Count -eq 0 -or @($selected | Where-Object { [string]::IsNullOrWhiteSpace($_['node_id']) }).Count -gt 0) {
            throw 'Each test queue must contain a nonempty selection of unique test nodes.'
        }
        $nodes += @($selected | ForEach-Object { $_['node_id'] })
    }
    if (@($nodes | Sort-Object -Unique -CaseSensitive).Count -ne $nodes.Count) {
        throw 'Test queues must partition unique test nodes without repeats.'
    }
}
