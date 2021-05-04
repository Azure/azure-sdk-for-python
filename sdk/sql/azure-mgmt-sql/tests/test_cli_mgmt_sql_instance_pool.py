# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   InstancePools: 0/6

import unittest

import azure.mgmt.sql
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSqlTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )

        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):

        azure_operation_poller = self.network_client.virtual_networks.begin_create_or_update(
            group_name,
            network_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            },
        )
        result_create = azure_operation_poller.result()

        async_subnet_creation = self.network_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()

        return subnet_info

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_instance_pool(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "InstancePool"
        INSTANCE_POOL_NAME = "myinstancepool"

        if self.is_live:
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

#--------------------------------------------------------------------------
        # /InstancePools/put/Create an instance pool with min properties.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": "westeurope",
          "sku": {
            "name": "GP_Gen5",
            "tier": "GeneralPurpose",
            "family": "Gen5"
          },
          "v_cores": 8,
          "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
          "license_type": "LicenseIncluded"
        }
        result = self.mgmt_client.instance_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstancePools/get/Get an instance pool[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_pools.get(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME)

#--------------------------------------------------------------------------
        # /InstancePools/get/List instance pools by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_pools.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /InstancePools/get/List instance pools in the subscription[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_pools.list()

#--------------------------------------------------------------------------
        # /InstancePools/patch/Patch an instance pool[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "x": "y"
          }
        }
        result = self.mgmt_client.instance_pools.begin_update(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstancePools/delete/Delete an instance pool[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_pools.begin_delete(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME)
        result = result.result()
