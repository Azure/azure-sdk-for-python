# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 6
# Methods Covered : 6
# Examples Total  : 6
# Examples Tested : 6
# Coverage %      : 100
# ----------------------

#  nat_gateways: 6/6

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

    def create_public_ip_addresses(self, group_name, location, public_ip_name):
        # Create PublicIP
        BODY = {
            'location': location,
            'public_ip_allocation_method': 'Static',
            'idle_timeout_in_minutes': 4,
            'sku': {
              'name': 'Standard'
            }
        }
        result = self.mgmt_client.public_ip_addresses.begin_create_or_update(
            group_name,
            public_ip_name,
            BODY
        )
        return result.result()

    def create_public_ip_prefixes(self, group_name, location, public_ip_prefix_name):
        # Create public IP prefix defaults[put]
        BODY = {
          "location": location,
          "prefix_length": "30",
          "sku": {
            "name": "Standard"
          }
        }
        result = self.mgmt_client.public_ip_prefixes.begin_create_or_update(group_name, public_ip_prefix_name, BODY)
        return result.result()
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        NAT_GATEWAY_NAME = "myNatGateway"
        PUBLIC_IP_ADDRESS_NAME = "publicipaddress"
        PUBLIC_IP_PREFIX_NAME = "publicipprefix"

        self.create_public_ip_addresses(RESOURCE_GROUP, AZURE_LOCATION, PUBLIC_IP_ADDRESS_NAME)
        self.create_public_ip_prefixes(RESOURCE_GROUP, AZURE_LOCATION, PUBLIC_IP_PREFIX_NAME)

        # /NatGateways/put/Create nat gateway[put]
        BODY = {
          "location": "eastus",
          "sku": {
            "name": "Standard"
          },
          "public_ip_addresses": [
            {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME
            }
          ],
          "public_ip_prefixes": [
            {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPPrefixes/" + PUBLIC_IP_PREFIX_NAME
            }
          ]
        }
        result = self.mgmt_client.nat_gateways.begin_create_or_update(resource_group_name=RESOURCE_GROUP, nat_gateway_name=NAT_GATEWAY_NAME, parameters=BODY)
        result = result.result()

        # /NatGateways/get/Get nat gateway[get]
        result = self.mgmt_client.nat_gateways.get(resource_group_name=RESOURCE_GROUP, nat_gateway_name=NAT_GATEWAY_NAME)

        # /NatGateways/get/List nat gateways in resource group[get]
        result = self.mgmt_client.nat_gateways.list(resource_group_name=RESOURCE_GROUP)

        # /NatGateways/get/List all nat gateways[get]
        result = self.mgmt_client.nat_gateways.list_all()

        # /NatGateways/patch/Update nat gateway tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.nat_gateways.update_tags(resource_group_name=RESOURCE_GROUP, nat_gateway_name=NAT_GATEWAY_NAME, parameters=BODY)

        # /NatGateways/delete/Delete nat gateway[delete]
        result = self.mgmt_client.nat_gateways.begin_delete(resource_group_name=RESOURCE_GROUP, nat_gateway_name=NAT_GATEWAY_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
