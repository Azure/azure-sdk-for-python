# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.mgmt.devopsinfrastructure import DevOpsInfrastructureMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


class TestMgmtDevOpsInfrastructure(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(DevOpsInfrastructureMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_list_pools_by_resource_group(self, resource_group):
        assert list(self.client.pools.list_by_resource_group(resource_group.name)) == []

    @recorded_by_proxy
    def test_list_sku(self):
        assert list(self.client.sku.list_by_location(AZURE_LOCATION)) != []

    @recorded_by_proxy
    def test_list_subscription_usages(self):
        assert list(self.client.subscription_usages.list_by_location(AZURE_LOCATION)) != []

    @recorded_by_proxy
    def test_list_operations(self):
        assert list(self.client.operations.list())
