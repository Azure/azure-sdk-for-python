# coding: utf-8
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
from azure.mgmt.oracledatabase import OracleDatabaseMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtOracleDatabase(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(OracleDatabaseMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_list_cloud_vm_clusters_by_resource_group(self, resource_group):
        assert list(self.client.cloud_vm_clusters.list_by_resource_group(resource_group.name)) == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_list_cloud_exadata_infrastructures_by_resource_group(self, resource_group):
        assert list(self.client.cloud_exadata_infrastructures.list_by_resource_group(resource_group.name)) == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_list_autonomous_databases_by_resource_group(self, resource_group):
        assert list(self.client.autonomous_databases.list_by_resource_group(resource_group.name)) == []

    @pytest.mark.skip("Lack of permission")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_list_db_system_shapes_by_resource_group(self, resource_group):
        assert list(self.client.db_system_shapes.list_by_location(location=AZURE_LOCATION)) == []

    @recorded_by_proxy
    def test_list_operations(self):
        assert list(self.client.operations.list())
