# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from functools import partial

from azure.mgmt.platformvalidation import PlatformValidationMgmtClient
from azure.mgmt.platformvalidation.models import (
    ExecutionPlanRun,
    ExecutionPlanRunProperties,
    ValidationExecutionPlan,
    ValidationExecutionPlanProperties,
    ValidationExecutionPlanUpdate,
)
from devtools_testutils import recorded_by_proxy

from _execution_prerequisites import (
    ExecutionEnvironmentPreparer,
    ExecutionPrerequisitesPreparer,
    ExecutionResourceGroupPreparer,
)
from _execution_testcase import (
    ExecutionTestCase,
    ExistingExecutionPreparer,
    assert_missing,
    cleanup_execution,
    complete,
    image_source,
    operation_status_target,
    plan_configuration,
    protect_execution_errors,
    wait_for_run,
)


class TestExecutionLifecycle(ExecutionTestCase):
    @ExistingExecutionPreparer()
    @recorded_by_proxy
    def test_execution_plan_lifecycle(
        self,
        platformvalidation_location,
        platformvalidation_execution_resource_group,
        platformvalidation_execution_cloud_validation,
        platformvalidation_execution_ownership,
    ):
        self.exercise_lifecycle(
            platformvalidation_location,
            platformvalidation_execution_resource_group,
            platformvalidation_execution_cloud_validation,
            platformvalidation_execution_ownership,
            execute=False,
        )

    @ExecutionEnvironmentPreparer()
    @ExecutionResourceGroupPreparer(name_prefix="platformvalidationexec", random_name_enabled=True, location="eastus")
    @ExecutionPrerequisitesPreparer()
    @recorded_by_proxy
    def test_execution_lifecycle(
        self,
        platformvalidation_location,
        resource_group,
        cloud_validation_name,
    ):
        self.exercise_lifecycle(
            platformvalidation_location,
            resource_group.name,
            cloud_validation_name,
            "owned-parent",
            execute=True,
        )

    @protect_execution_errors
    def exercise_lifecycle(
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
        name = self.get_resource_name("pyexec")
        run_name = self.get_resource_name("pyrun")
        args = (group, cv, name)
        run_args = (*args, run_name)
        plan_id = f"{self.resource_id(group, cv)}/validationExecutionPlans/{name}"
        run_id = f"{plan_id}/executionPlanRuns/{run_name}"
        description = f"SDK owned execution {run_name}"
        configuration = plan_configuration(name, image_source(self.is_live))
        tags = {"sdk-test": name}
        with self.create_mgmt_client(PlatformValidationMgmtClient) as client:
            self.assert_parent(
                client.cloud_validations.get(group, cv),
                group,
                cv,
                platformvalidation_execution_ownership,
            )
            assert_missing(client.validation_execution_plans.get, *args)
            try:
                plan = complete(
                    client.validation_execution_plans.begin_create_or_update(
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
                    client.validation_execution_plans.get(*args),
                    plan_id,
                    name,
                    tags,
                    "SDK boot plan",
                    configuration,
                )
                matches = [
                    p
                    for p in client.validation_execution_plans.list_by_resource_group(group, cv)
                    if p.id.lower() == plan_id.lower()
                ]
                assert len(matches) == 1
                tags = {**tags, "phase": "updated"}
                target = []
                updated = complete(
                    client.validation_execution_plans.begin_update(
                        *args,
                        ValidationExecutionPlanUpdate(tags=tags),
                        raw_response_hook=partial(operation_status_target, target=target),
                    )
                )
                self.assert_plan(updated, plan_id, name, tags, "SDK boot plan", configuration)
                self.assert_plan(
                    client.validation_execution_plans.get(*args),
                    plan_id,
                    name,
                    tags,
                    "SDK boot plan",
                    configuration,
                )
                assert len(target) == 2, "PATCH must expose a supported operation-status route."
                assert client.operation_status.get(*target).status == "Succeeded"
                if not execute:
                    return
                assert_missing(client.execution_plan_runs.get, *run_args)
                complete(
                    client.execution_plan_runs.begin_create_or_update(
                        *run_args,
                        ExecutionPlanRun(properties=ExecutionPlanRunProperties(description=description)),
                    )
                )
                self.assert_workload(wait_for_run(client, run_args), run_id, description)
                runs = list(client.execution_plan_runs.list_by_execution_plan(*args))
                assert len(runs) == 1
                self.assert_workload(runs[0], run_id, description)
                tests = list(client.validation_test_runs.list_by_execution_plan_run(*run_args))
                assert len(tests) == 1
                self.assert_test_run(tests[0], run_id)
                self.assert_test_run(client.validation_test_runs.get(*run_args, tests[0].name), run_id)
            finally:
                cleanup_execution(client, args, plan_id, run_name, description)
