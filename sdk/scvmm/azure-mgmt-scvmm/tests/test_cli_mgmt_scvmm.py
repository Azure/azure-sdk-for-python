# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.mgmt.scvmm import ScVmmMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtScVmm(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(ScVmmMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_availability_sets_list_by_resource_group(self, resource_group):
        assert list(self.client.availability_sets.list_by_resource_group(resource_group.name)) == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_clouds_list_by_resource_group(self, resource_group):
        assert list(self.client.clouds.list_by_resource_group(resource_group.name)) == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_virtual_machine_templates_list_by_resource_group(self, resource_group):
        assert list(self.client.virtual_machine_templates.list_by_resource_group(resource_group.name)) == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_virtual_networks_list_by_resource_group(self, resource_group):
        assert list(self.client.virtual_networks.list_by_resource_group(resource_group.name)) == []

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_vmm_servers_list_by_resource_group(self, resource_group):
        assert list(self.client.vmm_servers.list_by_resource_group(resource_group.name)) == []

    @recorded_by_proxy
    def test_list_operations(self):
        assert list(self.client.operations.list())
