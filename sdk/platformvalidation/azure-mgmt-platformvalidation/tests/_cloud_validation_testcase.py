# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from functools import partial
import asyncio
import time

from azure.mgmt.platformvalidation.models import CloudValidation
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.resource.resources.aio import ResourceManagementClient as AsyncResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, EnvironmentVariableLoader

PlatformValidationPreparer = partial(
    EnvironmentVariableLoader,
    "platformvalidation",
    platformvalidation_location="eastus",
)

OPERATION_TIMEOUT = 600
MANAGED_GROUP_CHECKS = 60
MANAGED_GROUP_CHECK_INTERVAL = 10
MANAGED_GROUP_ABSENCE_CONFIRMATIONS = 3


def wait_for_managed_group_deletion(client: ResourceManagementClient, name: str) -> None:
    absent = 0
    for attempt in range(MANAGED_GROUP_CHECKS):
        absent = 0 if client.resource_groups.check_existence(name) else absent + 1
        if absent == MANAGED_GROUP_ABSENCE_CONFIRMATIONS:
            return
        if attempt + 1 < MANAGED_GROUP_CHECKS:
            time.sleep(MANAGED_GROUP_CHECK_INTERVAL)
    raise AssertionError(
        f"Managed resource group {name} cleanup was not confirmed. No explicit RG deletion was attempted."
    )


async def wait_for_managed_group_deletion_async(client: AsyncResourceManagementClient, name: str) -> None:
    absent = 0
    for attempt in range(MANAGED_GROUP_CHECKS):
        absent = 0 if await client.resource_groups.check_existence(name) else absent + 1
        if absent == MANAGED_GROUP_ABSENCE_CONFIRMATIONS:
            return
        if attempt + 1 < MANAGED_GROUP_CHECKS:
            await asyncio.sleep(MANAGED_GROUP_CHECK_INTERVAL)
    raise AssertionError(
        f"Managed resource group {name} cleanup was not confirmed. No explicit RG deletion was attempted."
    )


class CloudValidationTestCase(AzureMgmtRecordedTestCase):
    def resource_id(self, resource_group: str, name: str) -> str:
        subscription = self.get_settings_value("SUBSCRIPTION_ID")
        return (
            f"/subscriptions/{subscription}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.PlatformValidation/cloudValidations/{name}"
        )

    def assert_identity(self, resource: CloudValidation, resource_group: str, name: str) -> None:
        assert resource.id is not None
        assert resource.id.lower() == self.resource_id(resource_group, name).lower()
        assert resource.name == name
        assert resource.type is not None
        assert resource.type.lower() == "microsoft.platformvalidation/cloudvalidations"

    def assert_resource(
        self,
        resource: CloudValidation,
        resource_group: str,
        name: str,
        location: str,
        description: str,
        tags: dict[str, str],
    ) -> None:
        self.assert_identity(resource, resource_group, name)
        assert resource.location == location
        assert resource.tags == tags
        assert resource.properties is not None
        assert resource.properties.description == description
        assert resource.properties.provisioning_state == "Succeeded"

    def assert_list_contains_resource(self, resources: list[CloudValidation], resource_group: str, name: str) -> None:
        resource_id = self.resource_id(resource_group, name).lower()
        matches = [resource for resource in resources if resource.id and resource.id.lower() == resource_id]
        assert len(matches) == 1
        self.assert_identity(matches[0], resource_group, name)
