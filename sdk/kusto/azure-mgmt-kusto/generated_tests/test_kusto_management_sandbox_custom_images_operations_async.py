# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.kusto.aio import KustoManagementClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestKustoManagementSandboxCustomImagesOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(KustoManagementClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_sandbox_custom_images_list_by_cluster(self, resource_group):
        response = self.client.sandbox_custom_images.list_by_cluster(
            resource_group_name=resource_group.name,
            cluster_name="str",
            api_version="2024-04-13",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_sandbox_custom_images_get(self, resource_group):
        response = await self.client.sandbox_custom_images.get(
            resource_group_name=resource_group.name,
            cluster_name="str",
            sandbox_custom_image_name="str",
            api_version="2024-04-13",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_sandbox_custom_images_begin_create_or_update(self, resource_group):
        response = await (
            await self.client.sandbox_custom_images.begin_create_or_update(
                resource_group_name=resource_group.name,
                cluster_name="str",
                sandbox_custom_image_name="str",
                parameters={
                    "baseImageName": "str",
                    "id": "str",
                    "language": "str",
                    "languageVersion": "str",
                    "name": "str",
                    "provisioningState": "str",
                    "requirementsFileContent": "str",
                    "type": "str",
                },
                api_version="2024-04-13",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_sandbox_custom_images_begin_update(self, resource_group):
        response = await (
            await self.client.sandbox_custom_images.begin_update(
                resource_group_name=resource_group.name,
                cluster_name="str",
                sandbox_custom_image_name="str",
                parameters={
                    "baseImageName": "str",
                    "id": "str",
                    "language": "str",
                    "languageVersion": "str",
                    "name": "str",
                    "provisioningState": "str",
                    "requirementsFileContent": "str",
                    "type": "str",
                },
                api_version="2024-04-13",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_sandbox_custom_images_begin_delete(self, resource_group):
        response = await (
            await self.client.sandbox_custom_images.begin_delete(
                resource_group_name=resource_group.name,
                cluster_name="str",
                sandbox_custom_image_name="str",
                api_version="2024-04-13",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_sandbox_custom_images_check_name_availability(self, resource_group):
        response = await self.client.sandbox_custom_images.check_name_availability(
            resource_group_name=resource_group.name,
            cluster_name="str",
            resource_name={"name": "str", "type": "Microsoft.Kusto/clusters/sandboxCustomImages"},
            api_version="2024-04-13",
        )

        # please add some check logic here by yourself
        # ...
