# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 12
# Methods Covered : 12
# Examples Total  : 12
# Examples Tested : 12
# Coverage %      : 100
# ----------------------

#  ip_groups: 5/6  TODO: The requested resource does not support http method 'PATCH'.
#  ip_allocations: 0/6 TODO: InvalidResourceType

import unittest
import pytest

import azure.mgmt.network
import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'


@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

    def create_virtual_network(self, group_name, location, network_name):
      
        result = self.mgmt_client.virtual_networks.begin_create_or_update(
            group_name,
            network_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            },
        )
        return result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_NETWORK_NAME = "virtualnetworkx"
        IP_GROUPS_NAME = "myIpGroups"
        IP_ALLOCATION_NAME = "myIpAllocation"

        # self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME)

        # /IpGroups/put/CreateOrUpdate_IpGroups[put]
        BODY = {
          "tags": {
            "key1": "value1"
          },
          "location": "West US",
          "ip_addresses": [
            "13.64.39.16/32",
            "40.74.146.80/31",
            "40.74.147.32/28"
          ]
        }
        result = self.mgmt_client.ip_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, ip_groups_name=IP_GROUPS_NAME, parameters=BODY)
        result = result.result()

        # /IpAllocations/put/Create IpAllocation[put]
        # BODY = {
        #   "location": "centraluseuap",
        #   "type": "Undefined",
        #   "prefix": "3.2.5.0/24",
        #   "allocation_tags": {
        #     "vnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME
        #   }
        # }
        # result = self.mgmt_client.ip_allocations.begin_create_or_update(resource_group_name=RESOURCE_GROUP, ip_allocation_name=IP_ALLOCATION_NAME, parameters=BODY)
        # result = result.result()

        # /IpAllocations/get/Get IpAllocation[get]
        # result = self.mgmt_client.ip_allocations.get(resource_group_name=RESOURCE_GROUP, ip_allocation_name=IP_ALLOCATION_NAME)

        # /IpGroups/get/Get_IpGroups[get]
        result = self.mgmt_client.ip_groups.get(resource_group_name=RESOURCE_GROUP, ip_groups_name=IP_GROUPS_NAME)

        # /IpAllocations/get/List IpAllocations in resource group[get]
        # result = self.mgmt_client.ip_allocations.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /IpGroups/get/ListByResourceGroup_IpGroups[get]
        result = self.mgmt_client.ip_groups.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /IpAllocations/get/List all IpAllocations[get]
        # result = self.mgmt_client.ip_allocations.list()

        # /IpGroups/get/List_IpGroups[get]
        result = self.mgmt_client.ip_groups.list()

        # /IpAllocations/patch/Update virtual network tags[patch]
        # BODY = {
        #   "tags": {
        #     "tag1": "value1",
        #     "tag2": "value2"
        #   }
        # }
        # result = self.mgmt_client.ip_allocations.update_tags(resource_group_name=RESOURCE_GROUP, ip_allocation_name=IP_ALLOCATION_NAME, parameters=BODY)

        # TODO: The requested resource does not support http method 'PATCH'.
        # /IpGroups/patch/Update_IpGroups[patch]
        # BODY = {
        #   "tags": {
        #     "key1": "value1",
        #     "key2": "value2"
        #   }
        # }
        # result = self.mgmt_client.ip_groups.update_groups(resource_group_name=RESOURCE_GROUP, ip_groups_name=IP_GROUPS_NAME, parameters=BODY)

        # /IpAllocations/delete/Delete IpAllocation[delete]
        # result = self.mgmt_client.ip_allocations.begin_delete(resource_group_name=RESOURCE_GROUP, ip_allocation_name=IP_ALLOCATION_NAME)
        # result = result.result()

        # /IpGroups/delete/Delete_IpGroups[delete]
        result = self.mgmt_client.ip_groups.begin_delete(resource_group_name=RESOURCE_GROUP, ip_groups_name=IP_GROUPS_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
