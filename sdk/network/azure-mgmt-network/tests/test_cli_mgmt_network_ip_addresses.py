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
# Examples Total  : 15
# Examples Tested : 15
# Coverage %      : 100
# ----------------------

#  public_ip_prefixes: 6/6
#  public_ip_addresses: 6/6

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

        SERVICE_NAME = "myapimrndxyz"
        PUBLIC_IPPREFIX_NAME = self.get_resource_name("publicipprefix")
        PUBLIC_IP_ADDRESS_NAME = self.get_resource_name("publicipaddress")

        # # Create public IP prefix allocation method[put]
        # BODY = {
        #   "location": "westus",
        #   "properties": {
        #     "public_ip_address_version": "IPv4",
        #     "prefix_length": "30"
        #   },
        #   "sku": {
        #     "name": "Standard"
        #   }
        # }
        # result = self.mgmt_client.public_ip_prefixes.create_or_update(resource_group.name, PUBLIC_IPPREFIX_NAME, BODY)
        # result = result.result()

        # Create public IP prefix defaults[put]
        BODY = {
          "location": "westus",
          "prefix_length": "30",
          "sku": {
            "name": "Standard"
          }
        }
        result = self.mgmt_client.public_ip_prefixes.begin_create_or_update(resource_group.name, PUBLIC_IPPREFIX_NAME, BODY)
        result = result.result()

        # Create public IP address defaults[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.public_ip_addresses.begin_create_or_update(resource_group.name, PUBLIC_IP_ADDRESS_NAME, BODY)
        result = result.result()

        # # Create public IP address allocation method[put]
        # BODY = {
        #   "properties": {
        #     "public_ipallocation_method": "Static",
        #     "idle_timeout_in_minutes": "10",
        #     "public_ip_address_version": "IPv4"
        #   },
        #   "sku": {
        #     "name": "Standard"
        #   },
        #   "location": "eastus"
        # }
        # result = self.mgmt_client.public_ip_addresses.create_or_update(resource_group.name, PUBLIC_IP_ADDRESS_NAME, BODY)
        # result = result.result()

        # # Create public IP address DNS[put]
        # BODY = {
        #   "properties": {
        #     "dns_settings": {
        #       "domain_name_label": "dnslbl"
        #     }
        #   },
        #   "location": "eastus"
        # }
        # result = self.mgmt_client.public_ip_addresses.create_or_update(resource_group.name, PUBLIC_IP_ADDRESS_NAME, BODY)
        # result = result.result()

        # Get public IP address[get]
        result = self.mgmt_client.public_ip_addresses.get(resource_group.name, PUBLIC_IP_ADDRESS_NAME)

        # Get public IP prefix[get]
        result = self.mgmt_client.public_ip_prefixes.get(resource_group.name, PUBLIC_IPPREFIX_NAME)

        # List resource group public IP addresses[get]
        result = self.mgmt_client.public_ip_addresses.list(resource_group.name)

        # List resource group public IP prefixes[get]
        result = self.mgmt_client.public_ip_prefixes.list(resource_group.name)

        # List all public IP addresses[get]
        result = self.mgmt_client.public_ip_addresses.list_all()

        # List all public IP prefixes[get]
        result = self.mgmt_client.public_ip_prefixes.list_all()

        # Update public IP address tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.public_ip_addresses.update_tags(resource_group.name, PUBLIC_IP_ADDRESS_NAME, BODY)

        # Update public IP prefix tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.public_ip_prefixes.update_tags(resource_group.name, PUBLIC_IPPREFIX_NAME, BODY)

        # Delete public IP address[delete]
        result = self.mgmt_client.public_ip_addresses.begin_delete(resource_group.name, PUBLIC_IP_ADDRESS_NAME)
        result = result.result()

        # Delete public IP prefix[delete]
        result = self.mgmt_client.public_ip_prefixes.begin_delete(resource_group.name, PUBLIC_IPPREFIX_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
