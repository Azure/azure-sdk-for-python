# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.mgmt.appcontainers.aio import ContainerAppsAPIClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = 'eastus'

class TestMgmtContainerApps(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(ContainerAppsAPIClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_list_by_resource_group(self, resource_group):
        response = self.client.container_apps.list_by_resource_group(resource_group.name)
        result = [r async for r in response]
        assert result == []

    @recorded_by_proxy_async
    async def test_list_operations(self):
        response = self.client.operations.list()
        result = [r async for r in response]
        assert result