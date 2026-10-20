# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

function Get-RecordSampleTestPaths {
    param([string]$TestScriptRoot)

    $skillRoot = (Resolve-Path (Join-Path $TestScriptRoot "..")).Path
    $repositoryPackageRoot = (Resolve-Path (Join-Path $TestScriptRoot "..\..\..\..")).Path
    [pscustomobject]@{
        EnvironmentScanner = Join-Path $skillRoot "scripts\GetSampleRequiredEnvironmentVariables.ps1"
        EnvironmentFileScanner = Join-Path $skillRoot "scripts\GetEnvironmentFileVariables.ps1"
        SampleResolver = Join-Path $skillRoot "scripts\ResolveSampleTest.ps1"
        SampleTestRunner = Join-Path $skillRoot "scripts\InvokeSampleValidation.ps1"
        RecordingConflictCheck = Join-Path $skillRoot "scripts\TestRecordingGitConflicts.ps1"
        RecordingStateReset = Join-Path $skillRoot "scripts\ResetRecordingState.ps1"
        PythonExecutable = Join-Path $repositoryPackageRoot ".venv\Scripts\python.exe"
    }
}

function New-SyntheticPackage {
    param([string]$Root)

    $directories = @(
        "samples\unique",
        "samples\multiple",
        "samples\async",
        "samples\evaluations",
        "samples\failures",
        "samples\first",
        "samples\hosted_agents",
        "samples\second",
        "samples\uncollected",
        "tests\samples"
    )
    foreach ($directory in $directories) {
        New-Item -ItemType Directory -Path (Join-Path $Root $directory) -Force | Out-Null
    }

    @'
import os

direct = os.environ["DIRECT_REQUIRED"]
helper = get_required_env_var("HELPER_REQUIRED")
os.environ["ASSIGNED_ONLY"] = "value"
optional = os.environ.get("OPTIONAL_WITH_DEFAULT", "default")
fallback = os.getenv("OPTIONAL_WITH_FALLBACK") or "default"
'@ | Set-Content -LiteralPath (Join-Path $Root "samples\unique\sample_unique.py") -Encoding UTF8

    'import os; value = os.environ["MULTIPLE_REQUIRED"]' |
        Set-Content -LiteralPath (Join-Path $Root "samples\multiple\sample_multiple.py") -Encoding UTF8
    'import os; value = os.environ["ASYNC_REQUIRED"]' |
        Set-Content -LiteralPath (Join-Path $Root "samples\async\sample_async.py") -Encoding UTF8
    'import os; value = os.environ["EVALUATION_REQUIRED"]' |
        Set-Content -LiteralPath (Join-Path $Root "samples\evaluations\sample_evaluation.py") -Encoding UTF8
    '# synthetic record failure sample' |
        Set-Content -LiteralPath (Join-Path $Root "samples\failures\sample_record_failure.py") -Encoding UTF8
    'import os; value = os.environ["FAILURE_PROCESS_VALUE"]' |
        Set-Content -LiteralPath (Join-Path $Root "samples\failures\sample_playback_failure.py") -Encoding UTF8
    '# synthetic hosted-agent sample' |
        Set-Content -LiteralPath (Join-Path $Root "samples\hosted_agents\sample_hosted.py") -Encoding UTF8
    '# intentionally absent from pytest collection' |
        Set-Content -LiteralPath (Join-Path $Root "samples\uncollected\sample_uncollected.py") -Encoding UTF8
    '# duplicate filename fixture' |
        Set-Content -LiteralPath (Join-Path $Root "samples\first\util.py") -Encoding UTF8
    '# duplicate filename fixture' |
        Set-Content -LiteralPath (Join-Path $Root "samples\second\util.py") -Encoding UTF8

    @'
def pytest_addoption(parser):
    parser.addoption("--azure_test_run_live")
    parser.addoption("--azure_skip_live_recording")
    parser.addoption("--direct_required")
    parser.addoption("--llm_validation_project_endpoint")
'@ | Set-Content -LiteralPath (Join-Path $Root "conftest.py") -Encoding UTF8

    @'
[CmdletBinding()]
param([string]$PackageRoot)

if (-not (Test-Path -LiteralPath (Join-Path $PackageRoot "recording-conflict-check-called.txt"))) {
    throw "Recording conflict check did not run before cleanup."
}
New-Item -ItemType File -Path (Join-Path $PackageRoot "recording-cleanup-called.txt") -Force | Out-Null
Remove-Item -Recurse -Force (Join-Path $PackageRoot ".pytest_cache") -ErrorAction SilentlyContinue
'@ | Set-Content -LiteralPath (Join-Path $Root "synthetic-recording-cleanup.ps1") -Encoding UTF8

    @'
[CmdletBinding()]
param([string]$PackageRoot, [string]$BaseBranch)

New-Item -ItemType File -Path (Join-Path $PackageRoot "recording-conflict-check-called.txt") -Force | Out-Null
[pscustomobject]@{ AssetRelationship = "synthetic"; SafeToRecord = $true }
'@ | Set-Content -LiteralPath (Join-Path $Root "synthetic-recording-conflict-check.ps1") -Encoding UTF8

    @'
[CmdletBinding()]
param(
    [string]$Organization,
    [string]$Project,
    [int]$DefinitionId,
    [string]$SourceBranch,
    [string]$SamplePattern,
    [string]$TestPattern,
    [string[]]$EnvironmentVariable,
    [string]$BearerToken
)

if ($BearerToken -ne "synthetic-token") {
    throw "Unexpected bearer token."
}
[ordered]@{
    Organization = $Organization
    Project = $Project
    DefinitionId = $DefinitionId
    SourceBranch = $SourceBranch
    SamplePattern = $SamplePattern
    TestPattern = $TestPattern
    EnvironmentVariables = $EnvironmentVariable
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot "pipeline-queue.json") -Encoding UTF8
[pscustomobject]@{
    BuildId = 123
    PipelineName = "synthetic sample validation"
    Url = "https://dev.azure.com/example/build/123"
    SourceBranch = $SourceBranch
}
'@ | Set-Content -LiteralPath (Join-Path $Root "synthetic-pipeline-queue.ps1") -Encoding UTF8

    @'
[CmdletBinding()]
param(
    [string]$Organization,
    [string]$Project,
    [int]$BuildId,
    [string]$BearerToken,
    [int]$PollIntervalSeconds,
    [int]$TimeoutMinutes
)

[pscustomobject]@{
    BuildId = $BuildId
    Status = "completed"
    Result = "succeeded"
    Url = "https://dev.azure.com/example/build/$BuildId"
}
'@ | Set-Content -LiteralPath (Join-Path $Root "synthetic-pipeline-wait.ps1") -Encoding UTF8

    @'
def loader(**kwargs):
    return kwargs


servicePreparer = loader(
    direct_required="sanitized-direct",
    llm_validation_project_endpoint="sanitized-validation-endpoint",
)
'@ | Set-Content -LiteralPath (Join-Path $Root "tests\test_base.py") -Encoding UTF8

    @'
DIRECT_REQUIRED=real-direct-value
HELPER_REQUIRED=real-helper-value
LLM_VALIDATION_PROJECT_ENDPOINT=https://validation.example.test/api/projects/example
HARNESS_VALUE=real-harness-value
FAILURE_PROCESS_VALUE=real-failure-process-value
'@ | Set-Content -LiteralPath (Join-Path $Root ".env") -Encoding UTF8

    @'
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
UNIQUE = str(ROOT / "samples" / "unique" / "sample_unique.py")
MULTIPLE = str(ROOT / "samples" / "multiple" / "sample_multiple.py")
RECORD_FAILURE = str(ROOT / "samples" / "failures" / "sample_record_failure.py")
PLAYBACK_FAILURE = str(ROOT / "samples" / "failures" / "sample_playback_failure.py")
HOSTED = str(ROOT / "samples" / "hosted_agents" / "sample_hosted.py")


@pytest.mark.parametrize("sample_path", [pytest.param(UNIQUE, id="unique-case")])
def test_unique(sample_path, pytestconfig):
    live = pytestconfig.getoption("azure_test_run_live") == "true"
    skip_recording = pytestconfig.getoption("azure_skip_live_recording") == "true"
    if live and not skip_recording:
        assert (ROOT / "recording-conflict-check-called.txt").is_file()
        assert (ROOT / "recording-cleanup-called.txt").is_file()
        assert not (ROOT / ".pytest_cache").exists()
    if False:
        executor.validate_print_calls_by_llm()


if False:
    AdditionalSampleTestDetail(
        test_id="unique-case",
        sample_filename="sample_unique.py",
        env_vars={"HARNESS_VALUE": "sanitized-harness-value"},
    )


@pytest.mark.parametrize(
    "sample_path",
    [
        pytest.param(MULTIPLE, id="variant-one"),
        pytest.param(MULTIPLE, id="variant-two"),
    ],
)
def test_multiple(sample_path):
    pass


@pytest.mark.parametrize("sample_path", [pytest.param(RECORD_FAILURE, id="record-failure")])
def test_record_failure(sample_path, pytestconfig):
    live = pytestconfig.getoption("azure_test_run_live") == "true"
    skip_recording = pytestconfig.getoption("azure_skip_live_recording") == "true"
    if live and not skip_recording:
        pytest.fail("synthetic recording failure")
    (ROOT / "playback-after-record-failure.txt").write_text("played", encoding="utf-8")


@pytest.mark.parametrize("sample_path", [pytest.param(PLAYBACK_FAILURE, id="playback-failure")])
def test_playback_failure(sample_path, pytestconfig):
    live = pytestconfig.getoption("azure_test_run_live") == "true"
    skip_recording = pytestconfig.getoption("azure_skip_live_recording") == "true"
    if not live and skip_recording:
        pytest.fail("synthetic playback failure")


@pytest.mark.parametrize("sample_path", [pytest.param(HOSTED, id="hosted-case")])
def test_hosted(sample_path, pytestconfig):
    live = pytestconfig.getoption("azure_test_run_live") == "true"
    if not live:
        assert (ROOT / "tests" / "samples" / "repair-called.txt").is_file()
'@ | Set-Content -LiteralPath (Join-Path $Root "tests\samples\test_samples.py") -Encoding UTF8

    @'
from pathlib import Path
import sys

Path(__file__).with_name("repair-called.txt").write_text(sys.argv[1], encoding="utf-8")
print("synthetic repair completed")
'@ | Set-Content -LiteralPath (Join-Path $Root "tests\samples\repair_hosted_agent_sample_recording.py") -Encoding UTF8

    @'
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
ASYNC_SAMPLE = str(ROOT / "samples" / "async" / "sample_async.py")


@pytest.mark.parametrize("sample_path", [pytest.param(ASYNC_SAMPLE, id="async-case")])
async def test_async(sample_path):
    pass
'@ | Set-Content -LiteralPath (Join-Path $Root "tests\samples\test_samples_async.py") -Encoding UTF8

    @'
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
EVALUATION_SAMPLE = str(ROOT / "samples" / "evaluations" / "sample_evaluation.py")


@pytest.mark.parametrize("sample_path", [pytest.param(EVALUATION_SAMPLE, id="evaluation-case")])
def test_evaluation(sample_path):
    pass
'@ | Set-Content -LiteralPath (Join-Path $Root "tests\samples\test_samples_evaluations.py") -Encoding UTF8
}