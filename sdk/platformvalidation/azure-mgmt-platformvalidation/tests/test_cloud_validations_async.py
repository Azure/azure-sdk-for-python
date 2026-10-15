# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, TypeVar

import pytest

from azure.core.exceptions import ResourceNotFoundError
from azure.core.polling import AsyncLROPoller
from azure.mgmt.platformvalidation.aio import PlatformValidationMgmtClient
from azure.mgmt.platformvalidation.models import (
    CloudValidation,
    CloudValidationProperties,
    CloudValidationUpdate,
    CloudValidationUpdateProperties,
)
from azure.mgmt.resource.resources.aio import ResourceManagementClient
from devtools_testutils import ResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

from _cloud_validation_testcase import (
    CloudValidationTestCase,
    OPERATION_TIMEOUT,
    PlatformValidationPreparer,
    wait_for_managed_group_deletion_async,
)

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")


async def complete_operation(poller: AsyncLROPoller[_ResultT]) -> _ResultT:
    result = await asyncio.wait_for(poller.result(), timeout=OPERATION_TIMEOUT)
    assert poller.done(), "CloudValidation operation did not finish within the timeout."
    return result


class TestCloudValidationsAsync(CloudValidationTestCase):
    @asynccontextmanager
    async def create_client(self) -> AsyncIterator[PlatformValidationMgmtClient]:
        credential = self.get_credential(PlatformValidationMgmtClient, is_async=True)
        try:
            async with self.create_client_from_credential(
                PlatformValidationMgmtClient,
                credential,
                subscription_id=self.get_settings_value("SUBSCRIPTION_ID"),
            ) as client:
                yield client
        finally:
            await credential.close()

    @PlatformValidationPreparer()
    @ResourceGroupPreparer(name_prefix="platformvalidation", random_name_enabled=True, location="eastus")
    @recorded_by_proxy_async
    async def test_cloud_validation_lifecycle(self, resource_group, platformvalidation_location: str) -> None:
        group = resource_group.name
        location = platformvalidation_location
        name = self.get_resource_name("pyasdkrec")
        tags = {"sdk-test": name, "phase": "created"}
        description = "Async Python SDK recorded CloudValidation"
        managed_group = f"{name}-mrg"
        credential = self.get_credential(ResourceManagementClient, is_async=True)
        try:
            async with (
                self.create_client() as client,
                self.create_client_from_credential(
                    ResourceManagementClient,
                    credential,
                    subscription_id=self.get_settings_value("SUBSCRIPTION_ID"),
                ) as resources,
            ):
                await self.exercise_lifecycle(
                    client, resources, group, name, location, description, tags, managed_group
                )
        finally:
            await credential.close()

    async def exercise_lifecycle(
        self,
        client: PlatformValidationMgmtClient,
        resources: ResourceManagementClient,
        group: str,
        name: str,
        location: str,
        description: str,
        tags: dict[str, str],
        managed_group: str,
    ) -> None:
        operations = client.cloud_validations
        with pytest.raises(ResourceNotFoundError) as missing:
            await operations.get(group, name)
        assert missing.value.status_code == 404
        assert not await resources.resource_groups.check_existence(
            managed_group
        ), "Managed resource group already exists."

        deleted = False
        try:
            created = await complete_operation(
                await operations.begin_create_or_update(
                    group,
                    name,
                    CloudValidation(
                        location=location,
                        tags=tags,
                        properties=CloudValidationProperties(description=description),
                    ),
                )
            )
            self.assert_resource(created, group, name, location, description, tags)
            self.assert_resource(await operations.get(group, name), group, name, location, description, tags)
            self.assert_list_contains_resource(
                [resource async for resource in operations.list_by_resource_group(group)], group, name
            )
            self.assert_list_contains_resource(
                [resource async for resource in operations.list_by_subscription()], group, name
            )

            tags = {"sdk-test": name, "phase": "updated"}
            description = "Updated async Python SDK recorded CloudValidation"
            updated = await complete_operation(
                await operations.begin_update(
                    group,
                    name,
                    CloudValidationUpdate(
                        tags=tags, properties=CloudValidationUpdateProperties(description=description)
                    ),
                )
            )
            self.assert_resource(updated, group, name, location, description, tags)
            self.assert_resource(await operations.get(group, name), group, name, location, description, tags)

            await self.delete_owned_resource(client, group, name)
            deleted = True
        finally:
            try:
                if not deleted:
                    await self.delete_owned_resource(client, group, name, allow_missing=True)
            finally:
                await wait_for_managed_group_deletion_async(resources, managed_group)

    async def delete_owned_resource(
        self, client: PlatformValidationMgmtClient, group: str, name: str, *, allow_missing: bool = False
    ) -> None:
        try:
            resource = await client.cloud_validations.get(group, name)
        except ResourceNotFoundError as error:
            if not allow_missing or error.status_code != 404:
                raise
            _LOGGER.warning(
                "Cleanup found no CloudValidation. If creation failed or timed out, check for late provisioning."
            )
            return
        self.assert_identity(resource, group, name)
        assert resource.tags and resource.tags.get("sdk-test") == name, "Refusing to delete an unowned resource."
        await complete_operation(await client.cloud_validations.begin_delete(group, name))
        with pytest.raises(ResourceNotFoundError) as missing:
            await client.cloud_validations.get(group, name)
        assert missing.value.status_code == 404

    @PlatformValidationPreparer()
    @ResourceGroupPreparer(name_prefix="platformvalidation", random_name_enabled=True, location="eastus")
    @recorded_by_proxy_async
    async def test_get_missing_cloud_validation_raises_not_found(self, resource_group) -> None:
        async with self.create_client() as client:
            with pytest.raises(ResourceNotFoundError) as missing:
                await client.cloud_validations.get(resource_group.name, self.get_resource_name("pyasdkmissing"))
            assert missing.value.status_code == 404
