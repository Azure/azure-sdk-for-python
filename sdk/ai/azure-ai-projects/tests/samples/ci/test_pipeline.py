# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline checks for the on-demand pipeline's automatic live-run flow."""

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def pipeline():
    path = Path(__file__).resolve().parents[3] / "tests.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def live_stages(pipeline):
    stages = pipeline["extends"]["parameters"]["stages"]
    return next(
        group["${{ if eq(parameters.runMode, 'run-and-cleanup') }}"] for group in stages if "stage" not in group
    )


def test_no_manual_approval_stage_or_task(pipeline):
    stages = live_stages(pipeline)
    assert [stage["stage"] for stage in stages] == ["RunSamples"]
    for stage in stages:
        for job in stage["jobs"]:
            assert job.get("pool") != "server"
            assert not any(step.get("task", "").startswith("ManualValidation@") for step in job["steps"])


def test_live_run_remains_opt_in_and_requires_successful_preview(pipeline):
    mode = next(parameter for parameter in pipeline["parameters"] if parameter["name"] == "runMode")
    assert mode["default"] == "preview"
    assert mode["values"] == ["preview", "run-and-cleanup"]
    stages = pipeline["extends"]["parameters"]["stages"]
    assert [stage["stage"] for stage in stages if "stage" in stage] == ["Preview"]
    run_stage = next(stage for stage in live_stages(pipeline) if stage["stage"] == "RunSamples")
    assert run_stage["dependsOn"] == "Preview"
    assert run_stage["condition"] == "succeeded()"


def test_cleanup_and_result_publication_still_run_on_failure(pipeline):
    run_stage = next(stage for stage in live_stages(pipeline) if stage["stage"] == "RunSamples")
    job = run_stage["jobs"][0]
    assert job["cancelTimeoutInMinutes"] == 30
    cleanup = next(step for step in job["steps"] if "Remove-SampleResources.ps1" in str(step))
    assert cleanup["condition"] == "always()"
    assert "-ConfirmCleanup" in cleanup["inputs"]["inlineScript"]
    results = next(step for step in job["steps"] if step.get("task") == "PublishTestResults@2")
    assert results["condition"] == "always()"


def test_pat_stays_scoped_to_provisioning_task(pipeline):
    run_stage = next(stage for stage in live_stages(pipeline) if stage["stage"] == "RunSamples")
    steps = run_stage["jobs"][0]["steps"]
    secret_steps = [step for step in steps if "MCP_GITHUB_PAT" in step.get("env", {})]
    assert len(secret_steps) == 1
    provisioning = secret_steps[0]
    assert provisioning["env"]["MCP_GITHUB_PAT"] == "$(MCP_GITHUB_PAT)"
    assert "Invoke-SampleProvisioning.ps1" in provisioning["inputs"]["inlineScript"]
    assert "-ConfirmProvisioning" in provisioning["inputs"]["inlineScript"]
    assert "MCP_GITHUB_PAT" not in {parameter["name"] for parameter in pipeline["parameters"]}


def test_failed_runner_captures_safe_diagnostics_before_cleanup(pipeline):
    run_stage = next(stage for stage in live_stages(pipeline) if stage["stage"] == "RunSamples")
    steps = run_stage["jobs"][0]["steps"]
    runner = next(step for step in steps if "run_samples.py" in str(step))
    script = runner["inputs"]["inlineScript"]
    assert "$sampleExitCode = $LASTEXITCODE" in script
    assert "if ($sampleExitCode -ne 0)" in script
    assert "Save-SampleReadinessDiagnostics -State $sampleState" in script
    assert "readiness-diagnostics.json" in script
    assert "throw 'Selected sample runner failed" in script
    assert steps.index(runner) < next(i for i, step in enumerate(steps) if "Remove-SampleResources.ps1" in str(step))
