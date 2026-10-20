# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [Alias("Sample", "SamplePath")]
    [string]$SamplePattern,

    [Alias("NodeId")]
    [string]$TestPattern,

    [string[]]$EnvironmentVariable,

    [ValidateSet("record-and-playback", "record-only", "playback-only", "live-test-locally", "live-test-by-pipeline")]
    [string]$Mode,

    [string]$EnvFile,
    [string]$PythonExecutable,
    [string]$PackageRoot,
    [ValidateSet("main", "feature/azure-ai-projects/vnext")]
    [string]$BaseBranch,
    [string]$RecordingConflictCheckScript,
    [string]$RecordingCleanupScript,
    [string]$PipelineQueueScript,
    [string]$PipelineWaitScript,
    [string]$PipelineOrganization = "azure-sdk",
    [string]$PipelineProject = "internal",
    [int]$PipelineDefinitionId = 8392,
    [string]$PipelineSourceBranch,
    [string]$PipelineBearerToken,
    [int]$PipelinePollIntervalSeconds = 15,
    [int]$PipelineTimeoutMinutes = 120,
    [string]$JUnitXml,
    [switch]$HideEnvironmentValues,
    [switch]$Run,
    [switch]$ConfirmSelection,
    [switch]$ConfirmRecording,
    [switch]$ConfirmLive,
    [switch]$ConfirmPipeline
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($Mode)) {
    throw "Mode is required. Choose record-and-playback, record-only, playback-only, live-test-locally, or live-test-by-pipeline."
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
if ($Mode -eq "live-test-by-pipeline" -and -not $PipelineQueueScript) {
    $PipelineQueueScript = Join-Path $scriptRoot "QueueSampleValidationPipeline.ps1"
}
if ($Mode -eq "live-test-by-pipeline" -and -not $PipelineWaitScript) {
    $PipelineWaitScript = Join-Path $scriptRoot "WaitSampleValidationPipeline.ps1"
}

$resolvedNodes = @(
    & $resolver -SamplePath $SamplePattern -PackageRoot $packageRoot -PythonExecutable $PythonExecutable
)
if ($TestPattern) {
    $normalizedTestPattern = $TestPattern.Replace("\", "/")
    $exactNodeMatches = @(
        $resolvedNodes | Where-Object {
            $candidate = $_.NodeId.Replace("\", "/")
            $candidate -eq $normalizedTestPattern -or $candidate.EndsWith($normalizedTestPattern)
        }
    )
    if ($exactNodeMatches.Count -gt 0) {
        $resolvedNodes = $exactNodeMatches
    } elseif ([System.Management.Automation.WildcardPattern]::ContainsWildcardCharacters($normalizedTestPattern)) {
        $nodeWildcard = [System.Management.Automation.WildcardPattern]::new(
            $normalizedTestPattern,
            [System.Management.Automation.WildcardOptions]::IgnoreCase
        )
        $resolvedNodes = @(
            $resolvedNodes | Where-Object {
                $candidate = $_.NodeId.Replace("\", "/")
                $nodeWildcard.IsMatch($candidate)
            }
        )
    } else {
        $resolvedNodes = @()
    }
    if ($resolvedNodes.Count -eq 0) {
        throw "Test pattern '$TestPattern' does not match any nodes selected by '$SamplePattern'."
    }
}
$resolvedNodes = @($resolvedNodes | Sort-Object SamplePath, NodeId -Unique)
$resolvedSamplePaths = @(
    $resolvedNodes.SamplePath |
        Select-Object -Unique |
        ForEach-Object { Join-Path $packageRoot $_ }
)

$requiredNames = @(
    & $requiredVariableScanner -SamplePath $resolvedSamplePaths -PackageRoot $packageRoot
)

$metadataScript = @'
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys


root = Path(sys.argv[1]).resolve()
selections = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))


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


uses_llm_validation = False
harness_names: set[str] = set()
for selection in selections:
    sample_path = Path(selection["SamplePath"]).resolve()
    node_id = selection["NodeId"].replace("\\", "/")
    tests_index = node_id.find("tests/")
    if tests_index < 0:
        raise RuntimeError(f"Node id has no tests/ path: {node_id}")
    parts = node_id[tests_index:].split("::")
    test_path = root / parts[0]
    method_name = parts[-1].split("[", 1)[0]
    parameter_match = re.search(r"\[(?P<id>.*)\]$", node_id)
    parameter_id = parameter_match.group("id") if parameter_match else ""
    tree = parse(test_path)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
            uses_llm_validation = uses_llm_validation or any(
                isinstance(child, ast.Attribute)
                and child.attr in {"validate_print_calls_by_llm", "validate_print_calls_by_llm_async"}
                for child in ast.walk(node)
            )
            break

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
$metadataInputPath = Join-Path ([System.IO.Path]::GetTempPath()) ("sample-validation-{0}.json" -f [guid]::NewGuid())
$metadataSelections = @(
    $resolvedNodes | ForEach-Object {
        [ordered]@{
            SamplePath = Join-Path $packageRoot $_.SamplePath
            NodeId = $_.NodeId
        }
    }
)
[System.IO.File]::WriteAllText(
    $metadataInputPath,
    (ConvertTo-Json -InputObject $metadataSelections -Depth 3),
    [System.Text.UTF8Encoding]::new($false)
)
try {
    $metadataJson = @($metadataScript | & $PythonExecutable - $packageRoot $metadataInputPath)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect the selected sample test metadata."
    }
} finally {
    Remove-Item -LiteralPath $metadataInputPath -Force -ErrorAction SilentlyContinue
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
$environmentSourceByName = @{}
foreach ($variable in $envFileVariables) {
    $envByName[$variable.Name] = $variable.Value
    $environmentSourceByName[$variable.Name] = ".env"
}
$overrideNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($assignment in @($EnvironmentVariable | Where-Object { $null -ne $_ })) {
    $separatorIndex = $assignment.IndexOf("=")
    if ($separatorIndex -le 0) {
        throw "EnvironmentVariable must use NAME=VALUE syntax: '$assignment'"
    }
    $name = $assignment.Substring(0, $separatorIndex)
    if ($name -notmatch "^[A-Za-z_][A-Za-z0-9_]*$") {
        throw "EnvironmentVariable has an invalid name: '$name'"
    }
    $envByName[$name] = $assignment.Substring($separatorIndex + 1)
    $environmentSourceByName[$name] = "command line"
    $null = $overrideNames.Add($name)
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
foreach ($name in @($overrideNames | Sort-Object)) {
    if ($usedEnvironmentNames.Contains($name)) {
        continue
    }
    $value = [string]$envByName[$name]
    if ([string]::IsNullOrEmpty($value)) {
        if (-not $emptyNames.Contains($name)) {
            $emptyNames.Add($name)
        }
        continue
    }
    if ($optionMap.ContainsKey($name)) {
        $commandLineValues[$optionMap[$name]] = $value
    } else {
        $processEnvironmentValues[$name] = $value
    }
    $null = $usedEnvironmentNames.Add($name)
}

$steps = switch ($Mode) {
    "record-and-playback" { @("record", "playback") }
    "record-only" { @("record") }
    "playback-only" { @("playback") }
    "live-test-locally" { @("live") }
    "live-test-by-pipeline" { @("pipeline") }
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
Write-Output "Sample pattern: $SamplePattern"
foreach ($sample in @($resolvedNodes.SamplePath | Select-Object -Unique)) {
    Write-Output "Sample: $sample"
}
foreach ($node in $resolvedNodes.NodeId) {
    Write-Output "Node: $node"
}
Write-Output "Required: $((@($allRequiredNames | Sort-Object) -join ', '))"
Write-Output "Harness-supplied: $($harnessNames -join ', ')"
Write-Output "Missing: $($missingNames -join ', ')"
Write-Output "Empty: $($emptyNames -join ', ')"
if ($usedEnvironmentNames.Count -eq 0) {
    Write-Output "Environment variables used: <none>"
} else {
    Write-Output "Environment variables used:"
    foreach ($name in @($usedEnvironmentNames | Sort-Object)) {
        $displayValue = if ($HideEnvironmentValues) { "<redacted>" } else { $envByName[$name] }
        Write-Output "  $name=$displayValue [$($environmentSourceByName[$name])]"
    }
}
Write-Output "Steps: $($steps -join ', ')"
if ($recordingConflictResult) {
    Write-Output "Recording conflict check: safe ($($recordingConflictResult.AssetRelationship))"
}
Write-Output "CLI values loaded: $($commandLineValues.Count); process values loaded: $($processEnvironmentValues.Count)"
if ($steps -contains "pipeline") {
    if (-not $PipelineSourceBranch) {
        $PipelineSourceBranch = (& git -C $packageRoot branch --show-current).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $PipelineSourceBranch) {
            throw "PipelineSourceBranch is required from a detached HEAD."
        }
    }
    if (-not $PipelineSourceBranch.StartsWith("refs/heads/")) {
        $PipelineSourceBranch = "refs/heads/$PipelineSourceBranch"
    }
    Write-Output "Pipeline: $PipelineOrganization/$PipelineProject definition $PipelineDefinitionId"
    Write-Output "Pipeline source branch: $PipelineSourceBranch"
}

if (-not $Run) {
    foreach ($step in $steps) {
        if ($step -eq "pipeline") {
            Write-Output "pipeline command: queue definition $PipelineDefinitionId with the selected sample and test patterns"
            continue
        }
        $redactedOptions = @($commandLineValues.Keys | ForEach-Object { "--$_=<environment value>" })
        Write-Output "$step command: pytest $($resolvedNodes.NodeId -join ' ') -s $($redactedOptions -join ' ') $($flags[$step] -join ' ')"
    }
    return
}

if (($steps -contains "record" -or $steps -contains "live" -or $steps -contains "pipeline") -and -not $ConfirmSelection) {
    throw "Execution selection was not confirmed. Review the sample, node, and environment variable names, then rerun with -Run -ConfirmSelection."
}
if ($steps -contains "record" -and -not $ConfirmRecording) {
    throw "Recording may modify files. Rerun with -Run -ConfirmRecording after user approval."
}
if ($steps -contains "live" -and -not $ConfirmLive) {
    throw "Live execution contacts Azure. Rerun with -Run -ConfirmLive after user approval."
}
if ($steps -contains "pipeline" -and -not $ConfirmPipeline) {
    throw "Pipeline execution contacts Azure. Rerun with -Run -ConfirmPipeline after user approval."
}

if ($steps -contains "pipeline") {
    $pipelineEnvironmentVariables = @(
        $usedEnvironmentNames | Sort-Object | ForEach-Object { "$_=$($envByName[$_])" }
    )
    $adoAccessToken = $PipelineBearerToken
    if (-not $adoAccessToken) {
        $adoAccessToken = & az account get-access-token `
            --resource "499b84ac-1321-427f-aa17-267ca6975798" `
            --query accessToken --output tsv 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $adoAccessToken) {
            throw "Unable to acquire an Azure DevOps bearer token. Run az login, then retry."
        }
    }

    $pipelineResult = & $PipelineQueueScript `
        -Organization $PipelineOrganization `
        -Project $PipelineProject `
        -DefinitionId $PipelineDefinitionId `
        -SourceBranch $PipelineSourceBranch `
        -SamplePattern $SamplePattern `
        -TestPattern $TestPattern `
        -EnvironmentVariable $pipelineEnvironmentVariables `
        -BearerToken $adoAccessToken
    Write-Output "pipeline result: queued"
    if ($pipelineResult.Url) {
        Write-Output "Pipeline URL: $($pipelineResult.Url)"
    }
    $completedPipeline = & $PipelineWaitScript `
        -Organization $PipelineOrganization `
        -Project $PipelineProject `
        -BuildId $pipelineResult.BuildId `
        -BearerToken $adoAccessToken `
        -PollIntervalSeconds $PipelinePollIntervalSeconds `
        -TimeoutMinutes $PipelineTimeoutMinutes
    Write-Output "pipeline completion result: $($completedPipeline.Result)"
    return
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
        $pytestArguments = @("-m", "pytest") + @($resolvedNodes.NodeId)
        if ($JUnitXml) {
            $pytestArguments += @(
                "--capture=tee-sys",
                "--junitxml=$JUnitXml",
                "-o", "junit_logging=system-out",
                "-o", "junit_log_passing_tests=true"
            )
        } else {
            $pytestArguments += "-s"
        }
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

        $hostedNodes = @(
            $resolvedNodes | Where-Object { $_.SamplePath.Replace("/", "\").StartsWith("samples\hosted_agents\") }
        )
        if ($step -eq "record" -and $hostedNodes.Count -gt 0) {
            $repairScript = Join-Path $packageRoot "tests\samples\repair_hosted_agent_sample_recording.py"
            if ($results[$step] -eq 0 -and (Test-Path -LiteralPath $repairScript)) {
                $repairExitCode = 0
                foreach ($hostedNode in $hostedNodes) {
                    & $PythonExecutable $repairScript $hostedNode.NodeId
                    if ($LASTEXITCODE -ne 0) {
                        $repairExitCode = $LASTEXITCODE
                    }
                }
                $results["repair"] = $repairExitCode
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