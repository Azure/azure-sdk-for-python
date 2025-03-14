# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.managementgroups.aio import ManagementGroupsAPI

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestManagementGroupsAPIManagementGroupSubscriptionsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ManagementGroupsAPI, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create(self, resource_group):
        response = await self.client.management_group_subscriptions.create(
            group_id="str",
            subscription_id="str",
            api_version="2021-04-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_delete(self, resource_group):
        response = await self.client.management_group_subscriptions.delete(
            group_id="str",
            subscription_id="str",
            api_version="2021-04-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_get_subscription(self, resource_group):
        response = await self.client.management_group_subscriptions.get_subscription(
            group_id="str",
            subscription_id="str",
            api_version="2021-04-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_get_subscriptions_under_management_group(self, resource_group):
        response = self.client.management_group_subscriptions.get_subscriptions_under_management_group(
            group_id="str",
            api_version="2021-04-01",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...
