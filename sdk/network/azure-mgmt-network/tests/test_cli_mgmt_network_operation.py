# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 1
# Methods Covered : 1
# Examples Total  : 1
# Examples Tested : 1
# Coverage %      : 100
# ----------------------

#  operations: 1/1
#  usages: 2/2

import unittest

import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
import pytest

AZURE_LOCATION = 'eastus'


@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        LOCATION = AZURE_LOCATION

        # /Operations/get/Get a list of operations for a resource provider[get]
        result = self.mgmt_client.operations.list()

        # /Usages/get/List usages spaced location[get]
        result = self.mgmt_client.usages.list(location=LOCATION)

        # /Usages/get/List usages[get]
        result = self.mgmt_client.usages.list(location=LOCATION)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
