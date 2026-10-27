# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from functools import partial

from azure.mgmt.platformvalidation.aio import PlatformValidationMgmtClient
from azure.mgmt.platformvalidation.models import (
    ExecutionPlanRun,
    ExecutionPlanRunProperties,
    ValidationExecutionPlan,
    ValidationExecutionPlanProperties,
    ValidationExecutionPlanUpdate,
)
from devtools_testutils.aio import recorded_by_proxy_async

from _execution_prerequisites import (
    ExecutionEnvironmentPreparer,
    ExecutionPrerequisitesPreparer,
    ExecutionResourceGroupPreparer,
)
from _execution_testcase import (
    ExecutionTestCase,
    ExistingExecutionPreparer,
    assert_missing_async,
    cleanup_execution_async,
    complete_async,
    image_source,
    operation_status_target,
    plan_configuration,
    protect_execution_errors,
    wait_for_run_async,
)


class TestExecutionLifecycleAsync(ExecutionTestCase):
    @ExistingExecutionPreparer()
    @recorded_by_proxy_async
    async def test_execution_plan_lifecycle(
        self,
        platformvalidation_location,
        platformvalidation_execution_resource_group,
        platformvalidation_execution_cloud_validation,
        platformvalidation_execution_ownership,
    ):
        await self.exercise_lifecycle(
            platformvalidation_location,
            platformvalidation_execution_resource_group,
            platformvalidation_execution_cloud_validation,
            platformvalidation_execution_ownership,
            execute=False,
        )

    @ExecutionEnvironmentPreparer()
    @ExecutionResourceGroupPreparer(name_prefix="platformvalidationexec", random_name_enabled=True, location="eastus")
    @ExecutionPrerequisitesPreparer()
    @recorded_by_proxy_async
    async def test_execution_lifecycle(
        self,
        platformvalidation_location,
        resource_group,
        cloud_validation_name,
    ):
        await self.exercise_lifecycle(
            platformvalidation_location,
            resource_group.name,
            cloud_validation_name,
            "owned-parent",
            execute=True,
        )

    @protect_execution_errors
    async def exercise_lifecycle(
        self,
        platformvalidation_location,
        platformvalidation_execution_resource_group,
        platformvalidation_execution_cloud_validation,
        platformvalidation_execution_ownership,
        *,
        execute,
    ):
        group = platformvalidation_execution_resource_group
        cv = platformvalidation_execution_cloud_validation
        name = self.get_resource_name("pyaexec")
        run_name = self.get_resource_name("pyarun")
        args = (group, cv, name)
        run_args = (*args, run_name)
        plan_id = f"{self.resource_id(group, cv)}/validationExecutionPlans/{name}"
        run_id = f"{plan_id}/executionPlanRuns/{run_name}"
        description = f"SDK owned execution {run_name}"
        configuration = plan_configuration(name, image_source(self.is_live))
        tags = {"sdk-test": name}
        credential = self.get_credential(PlatformValidationMgmtClient, is_async=True)
        try:
            async with self.create_client_from_credential(
                PlatformValidationMgmtClient,
                credential,
                subscription_id=self.get_settings_value("SUBSCRIPTION_ID"),
            ) as client:
                self.assert_parent(
                    await client.cloud_validations.get(group, cv),
                    group,
                    cv,
                    platformvalidation_execution_ownership,
                )
                await assert_missing_async(client.validation_execution_plans.get, *args)
                try:
                    plan = await complete_async(
                        await client.validation_execution_plans.begin_create_or_update(
                            *args,
                            ValidationExecutionPlan(
                                location=platformvalidation_location,
                                tags=tags,
                                properties=ValidationExecutionPlanProperties(
                                    description="SDK boot plan",
                                    plan_configuration_json=configuration,
                                ),
                            ),
                        )
                    )
                    self.assert_plan(plan, plan_id, name, tags, "SDK boot plan", configuration)
                    self.assert_plan(
                        await client.validation_execution_plans.get(*args),
                        plan_id,
                        name,
                        tags,
                        "SDK boot plan",
                        configuration,
                    )
                    matches = [
                        p
                        async for p in client.validation_execution_plans.list_by_resource_group(group, cv)
                        if p.id.lower() == plan_id.lower()
                    ]
                    assert len(matches) == 1
                    tags = {**tags, "phase": "updated"}
                    target = []
                    updated = await complete_async(
                        await client.validation_execution_plans.begin_update(
                            *args,
                            ValidationExecutionPlanUpdate(tags=tags),
                            raw_response_hook=partial(operation_status_target, target=target),
                        )
                    )
                    self.assert_plan(updated, plan_id, name, tags, "SDK boot plan", configuration)
                    self.assert_plan(
                        await client.validation_execution_plans.get(*args),
                        plan_id,
                        name,
                        tags,
                        "SDK boot plan",
                        configuration,
                    )
                    assert len(target) == 2, "PATCH must expose a supported operation-status route."
                    assert (await client.operation_status.get(*target)).status == "Succeeded"
                    if not execute:
                        return
                    await assert_missing_async(client.execution_plan_runs.get, *run_args)
                    await complete_async(
                        await client.execution_plan_runs.begin_create_or_update(
                            *run_args,
                            ExecutionPlanRun(properties=ExecutionPlanRunProperties(description=description)),
                        )
                    )
                    self.assert_workload(await wait_for_run_async(client, run_args), run_id, description)
                    runs = [run async for run in client.execution_plan_runs.list_by_execution_plan(*args)]
                    assert len(runs) == 1
                    self.assert_workload(runs[0], run_id, description)
                    tests = [test async for test in client.validation_test_runs.list_by_execution_plan_run(*run_args)]
                    assert len(tests) == 1
                    self.assert_test_run(tests[0], run_id)
                    self.assert_test_run(
                        await client.validation_test_runs.get(*run_args, tests[0].name),
                        run_id,
                    )
                finally:
                    await cleanup_execution_async(client, args, plan_id, run_name, description)
        finally:
            await credential.close()
