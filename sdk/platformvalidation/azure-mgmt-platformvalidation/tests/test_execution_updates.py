# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.mgmt.platformvalidation import PlatformValidationMgmtClient
from devtools_testutils import recorded_by_proxy

from _execution_testcase import (
    ExecutionTestCase,
    ExistingExecutionPreparer,
    assert_missing,
    cleanup_execution,
    complete,
    image_source,
    plan_configuration,
    protect_execution_errors,
)
from _update_testcase import (
    plan_update,
    replacement_plan,
    response_observation,
    updated_configuration,
)


class TestExecutionUpdates(ExecutionTestCase):
    @ExistingExecutionPreparer()
    @recorded_by_proxy
    def test_configuration_and_put_updates(
        self,
        platformvalidation_location,
        platformvalidation_execution_resource_group,
        platformvalidation_execution_cloud_validation,
        platformvalidation_execution_ownership,
    ):
        self.exercise_updates(
            platformvalidation_location,
            platformvalidation_execution_resource_group,
            platformvalidation_execution_cloud_validation,
            platformvalidation_execution_ownership,
            include_description=False,
        )

    @ExistingExecutionPreparer()
    @recorded_by_proxy
    def test_plan_updates(
        self,
        platformvalidation_location,
        platformvalidation_execution_resource_group,
        platformvalidation_execution_cloud_validation,
        platformvalidation_execution_ownership,
    ):
        self.exercise_updates(
            platformvalidation_location,
            platformvalidation_execution_resource_group,
            platformvalidation_execution_cloud_validation,
            platformvalidation_execution_ownership,
        )

    @protect_execution_errors
    def exercise_updates(self, location, group, cv, ownership, *, include_description=True):
        name = self.get_resource_name("pyupd")
        args = (group, cv, name)
        plan_id = f"{self.resource_id(group, cv)}/validationExecutionPlans/{name}"
        tags = {"sdk-test": name}
        description = "SDK isolated update plan"
        configuration = plan_configuration(name, image_source(self.is_live))
        self.update_observations = []

        def observe(response):
            self.update_observations.append(response_observation(response))

        with self.create_mgmt_client(PlatformValidationMgmtClient) as client:
            operations = client.validation_execution_plans
            self.assert_parent(client.cloud_validations.get(group, cv), group, cv, ownership)
            assert_missing(operations.get, *args)
            try:
                created = complete(
                    operations.begin_create_or_update(
                        *args,
                        replacement_plan(location, tags, description, configuration),
                        raw_response_hook=observe,
                    )
                )
                self.assert_plan(created, plan_id, name, tags, description, configuration)
                if include_description:
                    description = "Description-only PATCH"
                    patched = complete(
                        operations.begin_update(*args, plan_update(description=description), raw_response_hook=observe)
                    )
                    self.assert_plan(patched, plan_id, name, tags, description, configuration)
                    self.assert_plan(operations.get(*args), plan_id, name, tags, description, configuration)
                configuration = updated_configuration(configuration)
                patched = complete(
                    operations.begin_update(
                        *args,
                        plan_update(tags=tags, plan_configuration_json=configuration),
                        raw_response_hook=observe,
                    )
                )
                self.assert_plan(patched, plan_id, name, tags, description, configuration)
                self.assert_plan(operations.get(*args), plan_id, name, tags, description, configuration)
                for phase in ("idempotent", "metadata-replacement"):
                    if phase == "metadata-replacement":
                        tags = {**tags, "phase": phase}
                        description = "PUT existing plan metadata"
                    replaced = complete(
                        operations.begin_create_or_update(
                            *args,
                            replacement_plan(location, tags, description, configuration),
                            raw_response_hook=observe,
                        )
                    )
                    self.assert_plan(replaced, plan_id, name, tags, description, configuration)
                    self.assert_plan(operations.get(*args), plan_id, name, tags, description, configuration)
                self.assert_plan(operations.get(*args), plan_id, name, tags, description, configuration)
                assert not list(client.execution_plan_runs.list_by_execution_plan(*args))
            finally:
                cleanup_execution(client, args, plan_id, "never-submitted", "No execution was submitted")
