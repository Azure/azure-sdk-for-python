# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

<#
.SYNOPSIS
Preview or register multiple samples in the recorded sample-test harness.
.DESCRIPTION
Defaults to a read-only preview. Pass -Apply after reviewing the plan.
Also adds missing required environment names to .env.template and sanitized
playback defaults to servicePreparer. Never reads or writes .env.
Python 3.10+ is used only for standard-library AST parsing, not test execution.
.PARAMETER SanitizedValue
Optional NAME-to-string mapping for new playback defaults. Use only fictional,
sanitized values, never live secrets. Existing servicePreparer values are preserved.
.EXAMPLE
./AddSampleTestCase.ps1 -SamplePath @("samples/agents/sample_agent_basic.py", "samples/agents/sample_agent_basic_async.py")
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [Alias("SamplePaths")]
    [ValidateNotNullOrEmpty()]
    [string[]]$SamplePath,

    [string]$PackageRoot,
    [string]$PythonExecutable,
    [hashtable]$SanitizedValue = @{},
    [switch]$Apply,
    [switch]$AsJson
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $PackageRoot) {
    $PackageRoot = Join-Path $PSScriptRoot "../../../.."
}
$PackageRoot = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $PackageRoot).Path).FullName

if (-not $PythonExecutable) {
    $candidates = @(".venv/Scripts/python.exe", ".venv/bin/python")
    foreach ($candidate in $candidates) {
        $path = Join-Path $PackageRoot $candidate
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $PythonExecutable = $path
            break
        }
    }
    if (-not $PythonExecutable) {
        $PythonExecutable = "python"
    }
}

$helper = Join-Path $PSScriptRoot "sample_test_plan.py"
$output = @(& $PythonExecutable -B $helper --package-root $PackageRoot -- @SamplePath)
if ($LASTEXITCODE -ne 0) {
    throw "Sample registration planning failed. No test files were changed."
}
$plan = ($output -join [Environment]::NewLine) | ConvertFrom-Json
# Resolve requests once through the registration planner so the duplicated
# scanner receives exact files even for samples-relative paths or unique names.
$resolvedSamples = @($plan.samples | ForEach-Object { Join-Path $PackageRoot $_.samplePath })
$scanner = Join-Path $PSScriptRoot "GetSampleRequiredEnvironmentVariables.ps1"
$requiredNames = @(& $scanner -SamplePath $resolvedSamples -PackageRoot $PackageRoot)
$environmentInput = ConvertTo-Json -InputObject @{
    names = @($requiredNames)
    sanitizedValues = $SanitizedValue
} -Depth 5 -Compress
$environmentHelper = Join-Path $PSScriptRoot "sample_environment_plan.py"
$environmentOutput = @($environmentInput | & $PythonExecutable -B $environmentHelper --package-root $PackageRoot)
if ($LASTEXITCODE -ne 0) {
    throw "Sample environment planning failed. No files were changed."
}
$environmentPlan = ($environmentOutput -join [Environment]::NewLine) | ConvertFrom-Json
$files = @($plan.files) + @($environmentPlan.files)
$writtenFiles = @()
$mode = "preview"

if ($Apply -and $files.Count -gt 0) {
    # Validate the complete batch before writing anything. Never overwrite a
    # file that changed between planning and applying.
    foreach ($file in $files) {
        $exists = Test-Path -LiteralPath $file.path -PathType Leaf
        if ($null -eq $file.before) {
            if ($exists) {
                throw "A planned new file already exists: $($file.path). Rerun preview."
            }
        } elseif (-not $exists -or [System.IO.File]::ReadAllText($file.path) -cne $file.before) {
            throw "A planned file changed while planning: $($file.path). Rerun preview."
        }
    }

    if ($PSCmdlet.ShouldProcess(($files.relativePath -join ", "), "Register samples and required environment defaults")) {
        foreach ($file in $files) {
            $encoding = [System.Text.UTF8Encoding]::new([bool]$file.bom)
            [System.IO.File]::WriteAllText($file.path, $file.after, $encoding)
            $writtenFiles += $file.relativePath
        }
        $mode = "applied"
    } else {
        $mode = "not-applied"
    }
} elseif ($Apply) {
    $mode = "unchanged"
}

$result = [pscustomobject]@{
    Mode = $mode
    Samples = @($plan.samples)
    Environment = $environmentPlan.environment
    ChangedFiles = @($files | ForEach-Object { $_.relativePath })
    WrittenFiles = @($writtenFiles)
}
if ($AsJson) {
    $result | ConvertTo-Json -Depth 10
} else {
    foreach ($sample in $result.Samples) {
        Write-Host "$($sample.action): $($sample.samplePath)"
        foreach ($nodeId in $sample.nodeIds) {
            Write-Host "  $nodeId"
        }
    }
    Write-Host "Required environment variables: $(@($result.Environment.requiredNames) -join ', ')"
    foreach ($name in $result.Environment.templateAdded) {
        Write-Host "Template addition: $name="
    }
    foreach ($entry in $result.Environment.servicePreparerAdded) {
        Write-Host "servicePreparer addition: $($entry.keyword)=$($entry.value)"
    }
    if (@($result.Environment.servicePreparerAdded).Count -gt 0) {
        Write-Warning "New servicePreparer keys are required by every live test using it. Review the playback values; use -SanitizedValue for special formats."
    }
    foreach ($file in $files) {
        Write-Host "Planned file: $($file.relativePath)"
    }
    Write-Host "Mode: $mode. Planned files: $($files.Count). Written files: $($writtenFiles.Count)."
    if (-not $Apply -and $files.Count -gt 0) {
        Write-Host "Review the plan, then rerun with -Apply to register these samples."
    }
}