# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.mgmt.platformvalidation import PlatformValidationMgmtClient
from azure.mgmt.platformvalidation.aio import PlatformValidationMgmtClient as AsyncPlatformValidationMgmtClient
from devtools_testutils import recorded_by_proxy
from devtools_testutils.aio import recorded_by_proxy_async

from _execution_testcase import ExecutionTestCase, ExistingRunPreparer, protect_execution_errors


class TestExecutionResults(ExecutionTestCase):
    @ExistingRunPreparer()
    @recorded_by_proxy
    @protect_execution_errors
    def test_existing_execution_results(
        self,
        platformvalidation_execution_resource_group,
        platformvalidation_execution_cloud_validation,
        platformvalidation_execution_plan,
        platformvalidation_execution_run,
        platformvalidation_execution_ownership,
    ):
        group = platformvalidation_execution_resource_group
        cv = platformvalidation_execution_cloud_validation
        args = (group, cv, platformvalidation_execution_plan, platformvalidation_execution_run)
        run_id = f"{self.resource_id(group, cv)}/validationExecutionPlans/{args[2]}" f"/executionPlanRuns/{args[3]}"
        with self.create_mgmt_client(PlatformValidationMgmtClient) as client:
            self.assert_parent(
                client.cloud_validations.get(group, cv), group, cv, platformvalidation_execution_ownership
            )
            run = client.execution_plan_runs.get(*args)
            self.assert_workload(run, run_id, run.properties.description)
            matches = [
                item
                for item in client.execution_plan_runs.list_by_execution_plan(*args[:3])
                if item.id.lower() == run_id.lower()
            ]
            assert len(matches) == 1
            self.assert_workload(matches[0], run_id, run.properties.description)
            tests = list(client.validation_test_runs.list_by_execution_plan_run(*args))
            assert len(tests) == 1
            self.assert_test_run(tests[0], run_id)
            self.assert_test_run(client.validation_test_runs.get(*args, tests[0].name), run_id)

    @ExistingRunPreparer()
    @recorded_by_proxy_async
    @protect_execution_errors
    async def test_existing_execution_results_async(
        self,
        platformvalidation_execution_resource_group,
        platformvalidation_execution_cloud_validation,
        platformvalidation_execution_plan,
        platformvalidation_execution_run,
        platformvalidation_execution_ownership,
    ):
        group = platformvalidation_execution_resource_group
        cv = platformvalidation_execution_cloud_validation
        args = (group, cv, platformvalidation_execution_plan, platformvalidation_execution_run)
        run_id = f"{self.resource_id(group, cv)}/validationExecutionPlans/{args[2]}" f"/executionPlanRuns/{args[3]}"
        credential = self.get_credential(AsyncPlatformValidationMgmtClient, is_async=True)
        try:
            async with self.create_client_from_credential(
                AsyncPlatformValidationMgmtClient,
                credential,
                subscription_id=self.get_settings_value("SUBSCRIPTION_ID"),
            ) as client:
                self.assert_parent(
                    await client.cloud_validations.get(group, cv), group, cv, platformvalidation_execution_ownership
                )
                run = await client.execution_plan_runs.get(*args)
                self.assert_workload(run, run_id, run.properties.description)
                matches = [
                    item
                    async for item in client.execution_plan_runs.list_by_execution_plan(*args[:3])
                    if item.id.lower() == run_id.lower()
                ]
                assert len(matches) == 1
                self.assert_workload(matches[0], run_id, run.properties.description)
                tests = [test async for test in client.validation_test_runs.list_by_execution_plan_run(*args)]
                assert len(tests) == 1
                self.assert_test_run(tests[0], run_id)
                self.assert_test_run(await client.validation_test_runs.get(*args, tests[0].name), run_id)
        finally:
            await credential.close()
