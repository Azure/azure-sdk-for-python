# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.mgmt.sql.aio import SqlManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = 'eastus'

class TestMgmtSqlAsync(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(SqlManagementClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_server_list_by_resource_group(self, resource_group):
        response = self.client.servers.list_by_resource_group(resource_group.name)
        assert [r async for r in response] == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_managed_instances_list_by_resource_group(self, resource_group):
        response = self.client.managed_instances.list_by_resource_group(resource_group.name)
        assert [r async for r in response] == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_instance_pools_list_by_resource_group(self, resource_group):
        response = self.client.instance_pools.list_by_resource_group(resource_group.name)
        assert [r async for r in response] == []

    @recorded_by_proxy_async
    async def test_list_operations(self):
        response = self.client.operations.list()
        assert response
