# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [Alias("Sample")]
    [string]$SamplePath,

    [string]$NodeId,

    [ValidateSet("record-and-playback", "record-only", "playback-only", "live-test-locally")]
    [string]$Mode,

    [string]$EnvFile,
    [string]$PythonExecutable,
    [string]$PackageRoot,
    [ValidateSet("main", "feature/azure-ai-projects/vnext")]
    [string]$BaseBranch,
    [string]$RecordingConflictCheckScript,
    [string]$RecordingCleanupScript,
    [switch]$Run,
    [switch]$ConfirmSelection,
    [switch]$ConfirmRecording,
    [switch]$ConfirmLive
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($Mode)) {
    throw "Mode is required. Choose record-and-playback, record-only, playback-only, or live-test-locally."
}
$scriptRoot = $PSScriptRoot
if ($PackageRoot) {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $PackageRoot).Path).FullName
} else {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path (Join-Path $scriptRoot "..\..\..\..")).Path).FullName
}
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
if (-not $EnvFile) {
    $EnvFile = Join-Path $packageRoot ".env"
}

$resolver = Join-Path $scriptRoot "ResolveSampleTest.ps1"
$requiredVariableScanner = Join-Path $scriptRoot "GetSampleRequiredEnvironmentVariables.ps1"
$environmentFileScanner = Join-Path $scriptRoot "GetEnvironmentFileVariables.ps1"
if (-not $RecordingCleanupScript) {
    $RecordingCleanupScript = Join-Path $scriptRoot "ResetRecordingState.ps1"
}
if (-not $RecordingConflictCheckScript) {
    $RecordingConflictCheckScript = Join-Path $scriptRoot "TestRecordingGitConflicts.ps1"
}

$resolvedNodes = @(
    & $resolver -SamplePath $SamplePath -PackageRoot $packageRoot -PythonExecutable $PythonExecutable
)
if ($NodeId) {
    $normalizedRequestedNode = $NodeId.Replace("\", "/")
    $resolvedNodes = @(
        $resolvedNodes | Where-Object {
            $candidate = $_.NodeId.Replace("\", "/")
            $candidate -eq $normalizedRequestedNode -or $candidate.EndsWith($normalizedRequestedNode)
        }
    )
    if ($resolvedNodes.Count -eq 0) {
        throw "The requested node id does not execute '$SamplePath': $NodeId"
    }
}
if ($resolvedNodes.Count -gt 1) {
    $choices = $resolvedNodes.NodeId -join [Environment]::NewLine
    throw "Multiple pytest nodes execute this sample. Rerun with -NodeId and one of:$([Environment]::NewLine)$choices"
}
$resolved = $resolvedNodes[0]
$NodeId = $resolved.NodeId
$resolvedSamplePath = Join-Path $packageRoot $resolved.SamplePath

$requiredNames = @(
    & $requiredVariableScanner -SamplePath $resolvedSamplePath -PackageRoot $packageRoot
)

$metadataScript = @'
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys


root = Path(sys.argv[1]).resolve()
sample_path = Path(sys.argv[2]).resolve()
node_id = sys.argv[3].replace("\\", "/")


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))


def literal_keyword(call: ast.Call, name: str):
    keyword = next((item for item in call.keywords if item.arg == name), None)
    if keyword is None:
        return None
    try:
        return ast.literal_eval(keyword.value)
    except (TypeError, ValueError):
        return None


tests_index = node_id.find("tests/")
if tests_index < 0:
    raise RuntimeError(f"Node id has no tests/ path: {node_id}")
parts = node_id[tests_index:].split("::")
test_path = root / parts[0]
method_name = parts[-1].split("[", 1)[0]
parameter_match = re.search(r"\[(?P<id>.*)\]$", node_id)
parameter_id = parameter_match.group("id") if parameter_match else ""
tree = parse(test_path)

uses_llm_validation = False
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
        uses_llm_validation = any(
            isinstance(child, ast.Attribute)
            and child.attr in {"validate_print_calls_by_llm", "validate_print_calls_by_llm_async"}
            for child in ast.walk(node)
        )
        break

harness_names: set[str] = set()
for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
    function_name = call.func.id if isinstance(call.func, ast.Name) else getattr(call.func, "attr", None)
    if function_name != "AdditionalSampleTestDetail":
        continue
    filename = literal_keyword(call, "sample_filename")
    test_id = literal_keyword(call, "test_id")
    env_vars = literal_keyword(call, "env_vars") or {}
    if not test_id:
        test_id = f"{Path(filename).stem}-[{','.join(sorted(env_vars))}]"
    if filename == sample_path.name and test_id == parameter_id:
        harness_names.update(env_vars)

option_map: dict[str, str] = {}
test_base_path = root / "tests" / "test_base.py"
if test_base_path.is_file():
    for node in parse(test_base_path).body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "servicePreparer" for target in node.targets):
            continue
        if isinstance(node.value, ast.Call):
            for keyword in node.value.keywords:
                if keyword.arg:
                    option_map[keyword.arg.upper()] = keyword.arg

print(
    json.dumps(
        {
            "HarnessNames": sorted(harness_names),
            "UsesLlmValidation": uses_llm_validation,
            "OptionMap": option_map,
        }
    )
)
'@
$metadataJson = @($metadataScript | & $PythonExecutable - $packageRoot $resolvedSamplePath $NodeId)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect the selected sample test metadata."
}
$metadata = $metadataJson -join [Environment]::NewLine | ConvertFrom-Json

$allRequiredNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($name in $requiredNames) {
    $null = $allRequiredNames.Add([string]$name)
}
if ($metadata.UsesLlmValidation) {
    $null = $allRequiredNames.Add("LLM_VALIDATION_PROJECT_ENDPOINT")
}
$harnessNames = @($metadata.HarnessNames)

$envFileVariables = if (Test-Path -LiteralPath $EnvFile -PathType Leaf) {
    @(
        & $environmentFileScanner -EnvFile $EnvFile -PackageRoot $packageRoot `
            -PythonExecutable $PythonExecutable -IncludeValues
    )
} else {
    @()
}
$envByName = @{}
foreach ($variable in $envFileVariables) {
    $envByName[$variable.Name] = $variable.Value
}

$optionMap = @{}
foreach ($property in $metadata.OptionMap.PSObject.Properties) {
    $optionMap[$property.Name] = [string]$property.Value
}
$commandLineValues = [ordered]@{}
$processEnvironmentValues = [ordered]@{}
$missingNames = [System.Collections.Generic.List[string]]::new()
$emptyNames = [System.Collections.Generic.List[string]]::new()
$usedEnvironmentNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)

foreach ($name in @($allRequiredNames | Sort-Object)) {
    if (-not $envByName.ContainsKey($name)) {
        $missingNames.Add($name)
        continue
    }
    $value = $envByName[$name]
    if ([string]::IsNullOrEmpty([string]$value)) {
        $emptyNames.Add($name)
        continue
    }
    if ($optionMap.ContainsKey($name)) {
        $commandLineValues[$optionMap[$name]] = [string]$value
    } else {
        $processEnvironmentValues[$name] = [string]$value
    }
    $null = $usedEnvironmentNames.Add($name)
}
foreach ($name in $harnessNames) {
    if (-not $envByName.ContainsKey($name) -or [string]::IsNullOrEmpty([string]$envByName[$name])) {
        continue
    }
    if ($optionMap.ContainsKey($name)) {
        $commandLineValues[$optionMap[$name]] = [string]$envByName[$name]
    } else {
        $processEnvironmentValues[$name] = [string]$envByName[$name]
    }
    $null = $usedEnvironmentNames.Add([string]$name)
}

$steps = switch ($Mode) {
    "record-and-playback" { @("record", "playback") }
    "record-only" { @("record") }
    "playback-only" { @("playback") }
    "live-test-locally" { @("live") }
}
$flags = @{
    record = @("--azure_test_run_live=true", "--azure_skip_live_recording=false")
    playback = @("--azure_test_run_live=false", "--azure_skip_live_recording=true")
    live = @("--azure_test_run_live=true", "--azure_skip_live_recording=true")
}

$conflictCheckArguments = $null
$recordingConflictResult = $null
if ($steps -contains "record") {
    $conflictCheckArguments = @{ PackageRoot = $packageRoot }
    if ($BaseBranch) {
        $conflictCheckArguments.BaseBranch = $BaseBranch
    }
    $recordingConflictResult = & $RecordingConflictCheckScript @conflictCheckArguments
}

Write-Output "Mode: $Mode"
Write-Output "Sample: $($resolved.SamplePath)"
Write-Output "Node: $NodeId"
Write-Output "Required: $((@($allRequiredNames | Sort-Object) -join ', '))"
Write-Output "Harness-supplied: $($harnessNames -join ', ')"
Write-Output "Missing: $($missingNames -join ', ')"
Write-Output "Empty: $($emptyNames -join ', ')"
if ($usedEnvironmentNames.Count -eq 0) {
    Write-Output "Environment variables used: <none>"
} else {
    Write-Output "Environment variables used:"
    foreach ($name in @($usedEnvironmentNames | Sort-Object)) {
        Write-Output "  $name=$($envByName[$name])"
    }
}
Write-Output "Steps: $($steps -join ', ')"
if ($recordingConflictResult) {
    Write-Output "Recording conflict check: safe ($($recordingConflictResult.AssetRelationship))"
}
Write-Output "CLI values loaded: $($commandLineValues.Count); process values loaded: $($processEnvironmentValues.Count)"

if (-not $Run) {
    foreach ($step in $steps) {
        $redactedOptions = @($commandLineValues.Keys | ForEach-Object { "--$_=<from .env>" })
        Write-Output "$step command: pytest <node-id> -s $($redactedOptions -join ' ') $($flags[$step] -join ' ')"
    }
    return
}

if (($steps -contains "record" -or $steps -contains "live") -and -not $ConfirmSelection) {
    throw "Execution selection was not confirmed. Review the sample, node, and environment variable names, then rerun with -Run -ConfirmSelection."
}
if ($steps -contains "record" -and -not $ConfirmRecording) {
    throw "Recording may modify files. Rerun with -Run -ConfirmRecording after user approval."
}
if ($steps -contains "live" -and -not $ConfirmLive) {
    throw "Live execution contacts Azure. Rerun with -Run -ConfirmLive after user approval."
}

$originalEnvironment = @{}
foreach ($entry in $processEnvironmentValues.GetEnumerator()) {
    $originalEnvironment[$entry.Key] = [Environment]::GetEnvironmentVariable($entry.Key, "Process")
    [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, "Process")
}

$results = [ordered]@{}
try {
    foreach ($step in $steps) {
        if ($step -eq "record") {
            $recordingConflictResult = & $RecordingConflictCheckScript @conflictCheckArguments
            Write-Output "recording conflict recheck: safe ($($recordingConflictResult.AssetRelationship))"
            & $RecordingCleanupScript -PackageRoot $packageRoot
            Write-Output "recording cleanup: completed"
        }
        $pytestArguments = @("-m", "pytest", $NodeId, "-s")
        foreach ($entry in $commandLineValues.GetEnumerator()) {
            $pytestArguments += "--$($entry.Key)=$($entry.Value)"
        }
        $pytestArguments += $flags[$step]
        Push-Location $packageRoot
        try {
            & $PythonExecutable @pytestArguments
            $results[$step] = $LASTEXITCODE
        } finally {
            Pop-Location
        }

        if ($step -eq "record" -and $resolved.SamplePath.Replace("/", "\").StartsWith("samples\hosted_agents\")) {
            $repairScript = Join-Path $packageRoot "tests\samples\repair_hosted_agent_sample_recording.py"
            if ($results[$step] -eq 0 -and (Test-Path -LiteralPath $repairScript)) {
                & $PythonExecutable $repairScript $NodeId
                $results["repair"] = $LASTEXITCODE
            } else {
                $results["repair"] = "not run"
            }
        }
    }
} finally {
    foreach ($entry in $originalEnvironment.GetEnumerator()) {
        [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, "Process")
    }
}

foreach ($entry in $results.GetEnumerator()) {
    Write-Output "$($entry.Key) result: $($entry.Value)"
}
$failedResults = @(
    $results.GetEnumerator() | Where-Object { $_.Value -is [int] -and $_.Value -ne 0 }
)
if ($failedResults.Count -gt 0) {
    $failureSummary = @($failedResults | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ", "
    throw "Sample test workflow failed: $failureSummary"
}