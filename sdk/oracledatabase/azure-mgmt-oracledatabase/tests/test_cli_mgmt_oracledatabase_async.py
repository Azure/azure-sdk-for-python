# coding: utf-8
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
from azure.mgmt.oracledatabase.aio import OracleDatabaseMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = 'eastus'

class TestMgmtOracleDatabaseAsync(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(OracleDatabaseMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_list_cloud_vm_clusters_by_resource_group(self, resource_group):
        response = self.client.cloud_vm_clusters.list_by_resource_group(resource_group.name)
        assert [r async for r in response] == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_list_cloud_exadata_infrastructures_by_resource_group(self, resource_group):
        response = self.client.cloud_exadata_infrastructures.list_by_resource_group(resource_group.name)
        assert [r async for r in response] == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_list_autonomous_databases_by_resource_group(self, resource_group):
        response = self.client.autonomous_databases.list_by_resource_group(resource_group.name)
        assert [r async for r in response] == []

    @pytest.mark.skip("Lack of permission")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_list_db_system_shapes_by_resource_group(self, resource_group):
        response = self.client.db_system_shapes.list_by_location(location=AZURE_LOCATION)
        assert [r async for r in response] == []

    @recorded_by_proxy_async
    async def test_list_operations(self):
        response = self.client.operations.list()
        assert len([r async for r in response]) > 0
