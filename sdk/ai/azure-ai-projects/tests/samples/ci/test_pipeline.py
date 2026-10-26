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
    assert results["inputs"]["publishRunAttachments"] is True
    assert results["inputs"]["failTaskOnFailureToPublishResults"] is True


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
    runner = next(step for step in steps if step.get("task") == "AzureCLI@2" and "--junit" in str(step))
    script = runner["inputs"]["inlineScript"]
    assert "$sampleExitCode = $LASTEXITCODE" in script
    assert "if ($sampleExitCode -ne 0)" in script
    assert "Save-SampleReadinessDiagnostics -State $sampleState" in script
    assert "readiness-diagnostics.json" in script
    assert "throw 'Selected sample runner failed" in script
    assert steps.index(runner) < next(i for i, step in enumerate(steps) if "Remove-SampleResources.ps1" in str(step))


def test_external_validator_is_env_only_and_checked_before_provisioning(pipeline):
    parameters = {parameter["name"] for parameter in pipeline["parameters"]}
    assert {"LLM_VALIDATION_PROJECT_ENDPOINT", "validationModelVersion", "validationModelCapacity"}.isdisjoint(
        parameters
    )
    steps = live_stages(pipeline)[0]["jobs"][0]["steps"]
    validation_steps = [step for step in steps if "LLM_VALIDATION_PROJECT_ENDPOINT" in step.get("env", {})]
    assert len(validation_steps) == 2
    preflight = next(step for step in validation_steps if "--check-validation-config" in str(step))
    runner = next(step for step in validation_steps if "--junit" in str(step))
    provisioning = next(step for step in steps if "Invoke-SampleProvisioning.ps1" in str(step))
    for step in validation_steps:
        assert step["env"]["LLM_VALIDATION_PROJECT_ENDPOINT"] == "$(LLM_VALIDATION_PROJECT_ENDPOINT)"
    assert "LLM_VALIDATION_PROJECT_ENDPOINT" not in provisioning.get("env", {})
    assert steps.index(preflight) < steps.index(provisioning) < steps.index(runner)
    assert preflight["task"] == "AzureCLI@2"
    assert preflight["inputs"]["azureSubscription"] == provisioning["inputs"]["azureSubscription"]
    assert "Set-SampleSubscriptionContext" in preflight["inputs"]["inlineScript"]
    assert "pipeline-identity.json" in preflight["inputs"]["inlineScript"]
    assert "MCP_GITHUB_PAT" not in preflight.get("env", {})


def test_validator_model_is_absent_from_plan_and_provisioning_sources():
    directory = Path(__file__).resolve().parent
    for name in ("New-SampleDeploymentPlan.ps1", "Invoke-SampleProvisioning.ps1", "infra/sample-resources.bicepparam"):
        source = (directory / name).read_text(encoding="utf-8").lower()
        assert "validationmodel" not in source
        assert "validation_model" not in source
    template = (directory / "infra/sample-resources.bicep").read_text(encoding="utf-8")
    assert "validationDeployment" not in template
    assert "validationModel" not in template
    assert "LLM_VALIDATION_PROJECT_ENDPOINT" not in template


@pytest.mark.parametrize("variable", ["AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID"])
def test_target_ids_are_explicit_in_preview_and_every_live_azure_task(pipeline, variable):
    stages = pipeline["extends"]["parameters"]["stages"]
    preview = next(stage for stage in stages if stage.get("stage") == "Preview")
    plan = next(step for step in preview["jobs"][0]["steps"] if "New-SampleDeploymentPlan.ps1" in str(step))
    assert plan["env"][variable] == f"$({variable})"
    azure_tasks = [step for step in live_stages(pipeline)[0]["jobs"][0]["steps"] if step.get("task") == "AzureCLI@2"]
    assert len(azure_tasks) == 4
    for step in azure_tasks:
        assert step["env"][variable] == f"$({variable})"
    assert variable not in {parameter["name"] for parameter in pipeline["parameters"]}
    assert variable not in pipeline["variables"]
    preflight = next(step for step in azure_tasks if "--check-validation-config" in str(step))
    runner = next(step for step in azure_tasks if "--junit" in str(step))
    assert "Set-SampleSubscriptionContext -Plan" in preflight["inputs"]["inlineScript"]
    assert "Set-SampleSubscriptionContext -Plan" in runner["inputs"]["inlineScript"]


def test_default_model_and_region_use_verified_gpt5_configuration(pipeline):
    parameters = {parameter["name"]: parameter for parameter in pipeline["parameters"]}
    assert parameters["location"]["default"] == "westus3"
    assert parameters["modelName"]["default"] == "gpt-5.2"
    assert parameters["modelVersion"]["default"] == "2025-12-11"
    assert parameters["modelSku"]["default"] == "GlobalStandard"
    assert parameters["modelCapacity"]["default"] == 10


def test_preview_runs_pinned_pester_safety_tests_before_planning(pipeline):
    stages = pipeline["extends"]["parameters"]["stages"]
    preview = next(stage for stage in stages if stage.get("stage") == "Preview")
    steps = preview["jobs"][0]["steps"]
    guards = next(step for step in steps if "Invoke-Pester" in step.get("pwsh", ""))
    assert "Get-PSRepository -Name PSGallery -ErrorAction SilentlyContinue" in guards["pwsh"]
    assert "Register-PSRepository -Default -ErrorAction Stop" in guards["pwsh"]
    assert guards["pwsh"].index("Register-PSRepository") < guards["pwsh"].index("Install-Module")
    assert "-RequiredVersion 4.10.1" in guards["pwsh"]
    assert "-Script './tests/samples/ci'" in guards["pwsh"]
    assert "$result.TotalCount -eq 0" in guards["pwsh"]
    assert "$result.FailedCount -ne 0" in guards["pwsh"]
    assert steps.index(guards) < next(i for i, step in enumerate(steps) if "New-SampleDeploymentPlan.ps1" in str(step))


def test_subscription_is_not_derived_from_the_service_connection_default():
    directory = Path(__file__).resolve().parent
    source = (directory / "Invoke-SampleProvisioning.ps1").read_text(encoding="utf-8")
    assert "$subscription = [string] $account.id" not in source
    assert "Set-SampleSubscriptionContext -Plan $plan" in source
    assert "$subscription = Get-SampleSubscriptionId" in source
    plan = (directory / "New-SampleDeploymentPlan.ps1").read_text(encoding="utf-8")
    assert "subscriptionId = $subscription" in plan
    cleanup = (directory / "Remove-SampleResources.ps1").read_text(encoding="utf-8")
    assert "$state['subscriptionId'] -ine $state.plan.subscriptionId" in cleanup
    assert "Set-SampleSubscriptionContext -Plan $state.plan" in cleanup


def test_tenant_is_required_from_environment_and_bound_to_plan_and_cleanup():
    directory = Path(__file__).resolve().parent
    plan = (directory / "New-SampleDeploymentPlan.ps1").read_text(encoding="utf-8")
    assert "$tenant = Get-SampleTenantId" in plan
    assert "tenantId = $tenant" in plan
    provisioning = (directory / "Invoke-SampleProvisioning.ps1").read_text(encoding="utf-8")
    assert "tenantId = $runnerIdentity.tenantId" in provisioning
    assert "$state.environment['AZURE_TENANT_ID'] = $runnerIdentity.tenantId" in provisioning
    cleanup = (directory / "Remove-SampleResources.ps1").read_text(encoding="utf-8")
    assert "$state['tenantId'] -ine $state.plan.tenantId" in cleanup
