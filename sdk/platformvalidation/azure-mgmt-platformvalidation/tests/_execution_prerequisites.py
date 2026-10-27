# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from contextlib import ExitStack
from functools import partial
import logging
import time
from typing import TypeVar

from azure.core.exceptions import AzureError, ResourceExistsError, ResourceNotFoundError
from azure.core.polling import LROPoller
from azure.mgmt.platformvalidation import PlatformValidationMgmtClient
from azure.mgmt.platformvalidation.models import CloudValidation, CloudValidationProperties
from azure.mgmt.resource.resources import ResourceManagementClient
from devtools_testutils import AzureMgmtPreparer, EnvironmentVariableLoader, ResourceGroupPreparer
from devtools_testutils import add_general_string_sanitizer

from _cloud_validation_testcase import OPERATION_TIMEOUT, wait_for_managed_group_deletion

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")
CV_DELETE_ATTEMPTS = 30
CV_DELETE_INTERVAL = 10

ExecutionEnvironmentPreparer = partial(
    EnvironmentVariableLoader,
    "platformvalidation",
    platformvalidation_location="eastus",
)


def complete_prerequisite_operation(poller: LROPoller[_ResultT]) -> _ResultT:
    result = poller.result(timeout=OPERATION_TIMEOUT)
    if not poller.done():
        raise TimeoutError("Execution prerequisite operation did not finish within the timeout.")
    return result


class ExecutionResourceGroupPreparer(ResourceGroupPreparer):
    """Keep the parent group when child cleanup fails; never cascade-delete a plan."""

    def remove_resource(self, name, **kwargs):
        if not self.is_live or not self._need_creation:
            return
        group = self._prefix_name(name)
        try:
            cleaned_name = getattr(self.test_class_instance, "_cleaned_execution_cv", None)
            attempted = getattr(self.test_class_instance, "_execution_cv_attempted", False)
            assert (
                not attempted or cleaned_name
            ), f"Refusing to delete {group}: CloudValidation prerequisite cleanup was not confirmed."
            remaining = list(self.client.resources.list_by_resource_group(group))
            for resource in remaining:
                expected_id = (
                    f"/subscriptions/{self.test_class_instance.get_settings_value('SUBSCRIPTION_ID')}"
                    f"/resourceGroups/{group}/providers/Microsoft.PlatformValidation/cloudValidations/{cleaned_name}"
                )
                assert (
                    cleaned_name and resource.id and resource.id.lower() == expected_id.lower()
                ), f"Refusing to delete {group}: resources remain after execution prerequisite cleanup."
                # ARM's generic listing may lag a completed provider DELETE.
                # Recheck only this test's verified-deleted CV, never arbitrary children.
                with self.create_mgmt_client(PlatformValidationMgmtClient) as cv:
                    try:
                        cv.cloud_validations.get(group, cleaned_name)
                    except ResourceNotFoundError as error:
                        if error.status_code != 404:
                            raise
                    else:
                        raise AssertionError(f"Refusing to delete {group}: CloudValidation still exists.")
            complete_prerequisite_operation(self.client.resource_groups.begin_delete(group))
            wait_for_managed_group_deletion(self.client, group)
        finally:
            self.client.close()


class ExecutionPrerequisitesPreparer(AzureMgmtPreparer):
    """Create an isolated CV and verify its service-managed MRG without permission changes."""

    def __init__(self):
        super().__init__("pyexec", 24, disable_recording=True, random_name_enabled=True)
        self.resource_moniker = "executioncv"
        self._clients = ExitStack()
        self._cv_attempted = False

    def create_resource(self, name, **kwargs):
        if not self.is_live:
            return {"cloud_validation_name": name}
        # Reset per invocation; decorator instances can be reused by the test runner.
        self._clients = ExitStack()
        self._cv_attempted = False
        self.test_class_instance._execution_cv_attempted = False
        self.test_class_instance._cleaned_execution_cv = None
        self.name = name
        self.group = kwargs["resource_group"].name
        self.location = kwargs["platformvalidation_location"]
        self.subscription = self.test_class_instance.get_settings_value("SUBSCRIPTION_ID")
        self.managed_group = f"{name}-mrg"
        self.tags = {"sdk-test": name}
        add_general_string_sanitizer(target=name, value=self.moniker)
        _LOGGER.warning(
            "Execution prerequisites: subscription=%s, group=%s, cv=%s, managed_group=%s (service-managed)",
            self.subscription,
            self.group,
            name,
            self.managed_group,
        )
        try:
            self.resources = self._clients.enter_context(self.create_mgmt_client(ResourceManagementClient))
            self.cv = self._clients.enter_context(self.create_mgmt_client(PlatformValidationMgmtClient))
            if self.resources.resource_groups.check_existence(self.managed_group):
                raise AssertionError("Refusing to adopt an existing managed group.")
            try:
                self.cv.cloud_validations.get(self.group, name)
            except ResourceNotFoundError as error:
                if error.status_code != 404:
                    raise
            else:
                raise AssertionError("Refusing to overwrite an existing CloudValidation.")
            self._cv_attempted = True
            self.test_class_instance._execution_cv_attempted = True
            result = complete_prerequisite_operation(
                self.cv.cloud_validations.begin_create_or_update(
                    self.group,
                    name,
                    CloudValidation(
                        location=self.location,
                        tags=self.tags,
                        properties=CloudValidationProperties(description="SDK execution prerequisites"),
                    ),
                )
            )
            assert result.properties.provisioning_state == "Succeeded"
            assert self.resources.resource_groups.check_existence(
                self.managed_group
            ), "Service-managed MRG is absent; no fallback to manual provisioning."
            managed = self.resources.resource_groups.get(self.managed_group)
            expected_id = (
                f"/subscriptions/{self.subscription}/resourceGroups/{self.group}"
                f"/providers/Microsoft.PlatformValidation/cloudValidations/{name}"
            )
            assert (
                managed.managed_by and managed.managed_by.lower() == expected_id.lower()
            ), "Service-managed MRG is not associated with this test's CloudValidation."
            return {"cloud_validation_name": name}
        except (AzureError, AssertionError, TimeoutError, ValueError):
            # Framework preparers do not run remove_resource when create_resource fails.
            try:
                if self._cv_attempted:
                    self._cleanup()
            except (AzureError, AssertionError, TimeoutError):
                _LOGGER.exception("Prerequisite cleanup failed; retain the logged resource names for recovery.")
            finally:
                self._clients.close()
            raise

    def _cleanup(self) -> None:
        try:
            parent = self.cv.cloud_validations.get(self.group, self.name)
        except ResourceNotFoundError as error:
            if error.status_code != 404:
                raise
            parent = None
        if parent is not None:
            expected = (
                f"/subscriptions/{self.subscription}/resourceGroups/{self.group}"
                f"/providers/Microsoft.PlatformValidation/cloudValidations/{self.name}"
            )
            assert parent.id and parent.id.lower() == expected.lower()
            assert (
                parent.tags and parent.tags.get("sdk-test") == self.name
            ), "Refusing to delete a CloudValidation without this test's ownership tag."
            assert parent.properties.provisioning_state in (
                "Succeeded",
                "Failed",
                "Canceled",
            ), "Refusing cleanup while CloudValidation provisioning is nonterminal."
        if parent is not None:
            self._delete_cloud_validation()
            try:
                self.cv.cloud_validations.get(self.group, self.name)
            except ResourceNotFoundError as error:
                if error.status_code != 404:
                    raise
            else:
                raise AssertionError("CloudValidation still exists after cleanup.")
        wait_for_managed_group_deletion(self.resources, self.managed_group)
        if parent is not None:
            self.test_class_instance._cleaned_execution_cv = self.name

    def _delete_cloud_validation(self) -> None:
        for attempt in range(CV_DELETE_ATTEMPTS):
            assert not list(
                self.cv.validation_execution_plans.list_by_resource_group(self.group, self.name)
            ), "Execution plans remain: delete EPRs and VEPs before removing prerequisites."
            try:
                complete_prerequisite_operation(self.cv.cloud_validations.begin_delete(self.group, self.name))
                return
            except ResourceExistsError as error:
                code = getattr(getattr(error, "error", None), "code", None)
                if error.status_code != 409 or code != "CannotDeleteResource" or attempt + 1 == CV_DELETE_ATTEMPTS:
                    raise
                _LOGGER.warning(
                    "CV %s deletion still reports nested resources after an empty plan list; retrying (%s/%s).",
                    self.name,
                    attempt + 1,
                    CV_DELETE_ATTEMPTS,
                )
                time.sleep(CV_DELETE_INTERVAL)

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            try:
                self._cleanup()
            finally:
                self._clients.close()
