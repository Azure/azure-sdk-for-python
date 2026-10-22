# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest
import pytest

import azure.mgmt.hybridnetwork
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtHybridnetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.hybridnetwork.HybridNetworkManagementClient
        )
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_hybridnetwork(self, resource_group):

        assert list(self.mgmt_client.publishers.list_by_resource_group(resource_group.name)) == []

        assert list(self.mgmt_client.operations.list())

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
