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
    return [stage for stage in stages if stage.get("stage") == "RunSamples"]


def worker(pipeline):
    return next(job for job in live_stages(pipeline)[0]["jobs"] if job.get("job") == "ProvisionTestCleanup")


def test_no_manual_approval_stage_or_task(pipeline):
    stages = live_stages(pipeline)
    assert [stage["stage"] for stage in stages] == ["RunSamples"]
    for stage in stages:
        for job in stage["jobs"]:
            assert job.get("pool") != "server"
            assert not any(step.get("task", "").startswith("ManualValidation@") for step in job.get("steps", []))


def test_manual_run_requires_successful_internal_planning_without_a_preview_choice(pipeline):
    assert pipeline["trigger"] == "none"
    assert pipeline["pr"] == "none"
    assert "runMode" not in {parameter["name"] for parameter in pipeline["parameters"]}
    stages = pipeline["extends"]["parameters"]["stages"]
    assert [stage["stage"] for stage in stages] == ["Plan", "RunSamples"]
    run_stage = next(stage for stage in live_stages(pipeline) if stage["stage"] == "RunSamples")
    assert run_stage["dependsOn"] == "Plan"
    assert run_stage["condition"] == "succeeded()"


def test_run_form_uses_project_mi_without_connection_group_or_region_fields(pipeline):
    parameters = {parameter["name"]: parameter for parameter in pipeline["parameters"]}
    assert {"runMode", "azureServiceConnection", "secretVariableGroup", "location"}.isdisjoint(parameters)
    assert "projectIdentityName" not in parameters
    assert parameters["identityNamePattern"]["default"] == "mi-azsdk-sample-{resource}-wus3"
    assert "{resource}" in parameters["identityNamePattern"]["displayName"]
    assert pipeline["variables"]["azureServiceConnection"] == "azure-sdk-tests"
    stages = pipeline["extends"]["parameters"]["stages"]
    assert all("variables" not in stage for stage in stages)
    azure_tasks = [
        step for job in live_stages(pipeline)[0]["jobs"] for step in job["steps"] if step.get("task") == "AzureCLI@2"
    ]
    assert len(azure_tasks) == 5
    assert all(step["inputs"]["azureSubscription"] == "${{ variables.azureServiceConnection }}" for step in azure_tasks)


def test_cleanup_and_result_publication_still_run_on_failure(pipeline):
    run_stage = next(stage for stage in live_stages(pipeline) if stage["stage"] == "RunSamples")
    job = worker(pipeline)
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
    steps = worker(pipeline)["steps"]
    secret_steps = [step for step in steps if "MCP_GITHUB_PAT" in step.get("env", {})]
    assert len(secret_steps) == 1
    provisioning = secret_steps[0]
    assert provisioning["env"]["MCP_GITHUB_PAT"] == "$(MCP_GITHUB_PAT)"
    assert "Invoke-SampleProvisioning.ps1" in provisioning["inputs"]["inlineScript"]
    assert "-ConfirmProvisioning" in provisioning["inputs"]["inlineScript"]
    assert "MCP_GITHUB_PAT" not in {parameter["name"] for parameter in pipeline["parameters"]}


def test_failed_runner_still_fails_before_always_run_cleanup(pipeline):
    run_stage = next(stage for stage in live_stages(pipeline) if stage["stage"] == "RunSamples")
    steps = worker(pipeline)["steps"]
    runner = next(step for step in steps if step.get("task") == "AzureCLI@2" and "--junit" in str(step))
    script = runner["inputs"]["inlineScript"]
    assert "$sampleExitCode = $LASTEXITCODE" in script
    assert "if ($sampleExitCode -ne 0)" in script
    assert "throw 'Selected sample runner failed" in script
    assert steps.index(runner) < next(i for i, step in enumerate(steps) if "Remove-SampleResources.ps1" in str(step))


def test_external_validator_is_env_only_and_checked_before_provisioning(pipeline):
    parameters = {parameter["name"] for parameter in pipeline["parameters"]}
    assert {"LLM_VALIDATION_PROJECT_ENDPOINT", "validationModelVersion", "validationModelCapacity"}.isdisjoint(
        parameters
    )
    steps = worker(pipeline)["steps"]
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
def test_target_ids_are_explicit_in_plan_and_every_live_azure_task(pipeline, variable):
    stages = pipeline["extends"]["parameters"]["stages"]
    planning = next(stage for stage in stages if stage.get("stage") == "Plan")
    plan = next(step for step in planning["jobs"][0]["steps"] if "New-SampleDeploymentPlan.ps1" in str(step))
    assert plan["env"][variable] == f"$({variable})"
    azure_tasks = [step for step in worker(pipeline)["steps"] if step.get("task") == "AzureCLI@2"]
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
    assert parameters["identityNamePattern"]["default"] == "mi-azsdk-sample-{resource}-wus3"
    assert parameters["modelName"]["default"] == "gpt-5.2"
    assert parameters["modelVersion"]["default"] == "2025-12-11"
    assert parameters["modelSku"]["default"] == "GlobalStandard"
    assert parameters["modelCapacity"]["default"] == 10


def test_internal_plan_only_collects_and_plans_without_test_framework_bootstrap(pipeline):
    stages = pipeline["extends"]["parameters"]["stages"]
    planning = next(stage for stage in stages if stage.get("stage") == "Plan")
    steps = planning["jobs"][0]["steps"]
    scripts = [step["pwsh"] for step in steps if "pwsh" in step]
    assert len(scripts) == 2  # Dependency installation, then collection and plan generation.
    assert "select_samples.py" in scripts[1]
    assert "New-SampleDeploymentPlan.ps1" in scripts[1]
    assert "-IdentityNamePattern $env:SAMPLE_MI_NAME_PATTERN" in scripts[1]
    assert "-Location" not in scripts[1]
    assert steps[-1]["env"]["SAMPLE_MI_NAME_PATTERN"] == "${{ parameters.identityNamePattern }}"
    assert "SAMPLE_PROJECT_IDENTITY_NAME" not in steps[-1]["env"]
    assert "SAMPLE_LOCATION" not in steps[-1]["env"]
    for script in scripts:
        assert not any(
            command in script
            for command in (
                "Invoke-Pester",
                "Install-Module",
                "Test-BicepTemplates",
                "ConfirmProvisioning",
                "ConfirmCleanup",
            )
        )
    assert not any(step.get("task") == "AzureCLI@2" for step in steps)


def test_provisioning_uses_shared_variant_without_worker_iam_writes():
    directory = Path(__file__).resolve().parent
    source = (directory / "Invoke-SampleProvisioning.ps1").read_text(encoding="utf-8")
    assert source.index("Get-SampleSharedIdentities -Plan $plan") < source.index("$state = @{")
    assert source.index("Assert-SampleSharedIdentityGrants -Plan $plan") < source.index("$state = @{")
    assert source.index("Set-Content -LiteralPath $StatePath") < source.index("@('deployment', 'sub', 'create')")
    assert "[Parameter(Mandatory)] [string] $StandardTemplatePath" not in source
    helper = (directory / "SampleCiHelpers.ps1").read_text(encoding="utf-8")
    assert "function Get-SampleStandardTemplate" in helper
    assert "SHA256]::HashData($bytes)" in helper
    assert "checksum mismatch" in helper
    assert "infra/standard-shared-identities.bicep" in source
    for name in ("sample-resources.bicep", "standard-shared-identities.bicep"):
        assert "'Microsoft.Authorization/roleAssignments@" not in (directory / "infra" / name).read_text(
            encoding="utf-8"
        )


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


def test_round_robin_workers_are_isolated_without_an_environment_dependency(pipeline):
    parameters = {parameter["name"]: parameter for parameter in pipeline["parameters"]}
    assert parameters["testQueueCount"]["default"] == 4
    assert parameters["testQueueCount"]["values"] == [1, 2, 3, 4]
    selection = parameters["selection"]["default"].split(";")
    assert selection == [
        "samples/agents/tools/sample_agent_mcp_with_project_connection.py",
        "samples/agents/tools/sample_agent_mcp_with_project_connection_async.py",
    ]
    stage = live_stages(pipeline)[0]
    assert "lockBehavior" not in stage
    assert all("environment" not in job and "deployment" not in job for job in stage["jobs"])
    admission = next(job for job in stage["jobs"] if job.get("job") == "AdmitTestQueues")
    steps = admission["steps"]
    preflight = next(step for step in steps if step.get("task") == "AzureCLI@2")
    assert "-BatchPlanDirectory" in preflight["inputs"]["inlineScript"]
    assert "-ResolvedPlanDirectory" in preflight["inputs"]["inlineScript"]
    assert admission["templateContext"]["outputs"][0]["artifactName"] == "resolved-sample-plan"
    assert preflight["env"] == {
        "AZURE_SUBSCRIPTION_ID": "$(AZURE_SUBSCRIPTION_ID)",
        "AZURE_TENANT_ID": "$(AZURE_TENANT_ID)",
    }
    job = worker(pipeline)
    download = next(step for step in job["steps"] if step.get("task") == "DownloadPipelineArtifact@2")
    assert download["inputs"]["artifactName"] == "resolved-sample-plan"
    assert job["dependsOn"] == "AdmitTestQueues"
    assert job["strategy"]["maxParallel"] == 4
    assert job["strategy"]["matrix"] == "$[ stageDependencies.Plan.Plan.outputs['Plan.WorkerMatrix'] ]"
    planning = next(stage for stage in pipeline["extends"]["parameters"]["stages"] if stage.get("stage") == "Plan")
    plan = next(step for step in planning["jobs"][0]["steps"] if step.get("name") == "Plan")
    assert "--queue-count $env:SAMPLE_QUEUE_COUNT" in plan["pwsh"]
    assert '"$queueName/selected-tests.json"' in plan["pwsh"]
    assert "queue-matrix.json" in plan["pwsh"]
    assert "variable=WorkerMatrix;isOutput=true" in plan["pwsh"]
    assert job["templateContext"]["outputs"][0]["artifactName"] == "sample-results-$(QueueName)"
    for step in job["steps"]:
        if step.get("task") == "AzureCLI@2":
            assert step["env"]["SAMPLE_QUEUE_NAME"] == "$(QueueName)"
            assert "SYSTEM_ACCESSTOKEN" not in step["env"]
        if step.get("task") == "PublishTestResults@2":
            assert step["inputs"]["searchFolder"].endswith("/$(QueueName)")


def test_batch_admission_retains_guards_without_querying_ado():
    directory = Path(__file__).resolve().parent
    source = (directory / "Invoke-SampleProvisioning.ps1").read_text(encoding="utf-8")
    admission = source.split("if (-not $ConfirmProvisioning)", 1)[0]
    for guard in (
        "Set-SampleSubscriptionContext",
        "Get-SampleSharedIdentities",
        "Assert-SampleSharedIdentityGrants",
        "Assert-SampleBatchCapacity",
    ):
        assert guard in admission
    assert "Assert-SampleCapacityLock" not in source
    helper = (directory / "SampleCiHelpers.ps1").read_text(encoding="utf-8")
    assert "function Assert-SampleCapacityLock" not in helper
    assert "pipelines/checks/configurations" not in helper
