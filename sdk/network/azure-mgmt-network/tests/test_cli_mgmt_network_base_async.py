# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   virtual_networks: 8/8
#   subnets: 4/6  TODO: SubscriptionNotRegisteredForFeature in Prepare/Unprepare Network Policies

import unittest
import time
import pytest

import azure.mgmt.network.aio
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

from _aio_testcase import AzureMgmtRecordedAsyncTestCase

AZURE_LOCATION = 'eastus'

@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedAsyncTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_aio_client(
            azure.mgmt.network.aio.NetworkManagementClient
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SERVICE_NAME = "myapimrndxyz"
        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        
        VIRTUAL_NETWORK_NAME = "virtualnetworkname"
        SUBNET_NAME = "subnetname"

        # Create virtual network[put]
        BODY = {
          "address_space": {
            "address_prefixes": [
              "10.0.0.0/16"
            ]
          },
          "location": "eastus"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.virtual_networks.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        )
        result = self.event_loop.run_until_complete(
            result.result()
        )

        # Create subnet[put]
        BODY = {
          "address_prefix": "10.0.0.0/24"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.subnets.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME, BODY)
        )
        subnet = self.event_loop.run_until_complete(
            result.result()
        )

        # Check IP address availability[get]
        IP_ADDRESS = "10.0.0.4"
        result = self.event_loop.run_until_complete(
            self.mgmt_client.virtual_networks.check_ip_address_availability(resource_group.name, VIRTUAL_NETWORK_NAME, IP_ADDRESS)
        )

        # Get subnet[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.subnets.get(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        )

        # List subnets[get]
        result = self.to_list(
            self.mgmt_client.subnets.list(resource_group.name, VIRTUAL_NETWORK_NAME)
        )

        # VnetGetUsage[get]
        result = self.to_list(
            self.mgmt_client.virtual_networks.list_usage(resource_group.name, VIRTUAL_NETWORK_NAME)
        )

        # Get virtual network[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.virtual_networks.get(resource_group.name, VIRTUAL_NETWORK_NAME)
        )

        # List virtual networks in resource group[get]
        result = self.to_list(
            self.mgmt_client.virtual_networks.list(resource_group.name)
        )

        # List all virtual networks[get]
        result = self.to_list(
            self.mgmt_client.virtual_networks.list_all()
        )

        # Update virtual network tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.virtual_networks.update_tags(resource_group.name, VIRTUAL_NETWORK_NAME, BODY)
        )

        # Delete subnet[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.subnets.begin_delete(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        )
        result = self.event_loop.run_until_complete(
            result.result()
        )

        # Delete virtual network[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.virtual_networks.begin_delete(resource_group.name, VIRTUAL_NETWORK_NAME)
        )
        result = self.event_loop.run_until_complete(
            result.result()
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()