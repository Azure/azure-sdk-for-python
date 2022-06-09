# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 4
# Methods Covered : 4
# Examples Total  : 4
# Examples Tested : 4
# Coverage %      : 100
# ----------------------

#  available_service_aliases: 2/2
#  available_resource_group_delegations: 2/2

import unittest
import pytest

import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        LOCATION_NAME = AZURE_LOCATION

        # Get available service aliases in the resource group[get]
        result = self.mgmt_client.available_service_aliases.list_by_resource_group(resource_group.name, LOCATION_NAME)

        # Get available delegations in the resource group[get]
        result = self.mgmt_client.available_resource_group_delegations.list(resource_group.name, LOCATION_NAME)

        # Get available service aliases[get]
        result = self.mgmt_client.available_service_aliases.list(LOCATION_NAME)

        # Get available delegations[get]
        result = self.mgmt_client.available_delegations.list(LOCATION_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
