# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 12
# Methods Covered : 11
# Examples Total  : 11
# Examples Tested : 11
# Coverage %      : 92
# ----------------------

import unittest

import azure.mgmt.powerbidedicated
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtPowerBIDedicatedTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtPowerBIDedicatedTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.powerbidedicated.PowerBIDedicatedManagementClient
        )
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_powerbidedicated(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        DEDICATED_CAPACITY_NAME = "mydedicatedcapacity"
        LOCATION = "myLocation"

        # /Capacities/put/Create capacity[put]i
        BODY = {
          "sku": {
            "name": "A1",
            "tier": "PBIE_Azure"
          },
          "tags": {
            "test_key": "testValue"
          },
          "administration": {
           "members": [
             "user1@microsoft.com",
             "user2@microsoft.com"
           ]
          },
          "location": "eastus"
        }
        result = self.mgmt_client.capacities.create(resource_group_name=RESOURCE_GROUP, dedicated_capacity_name=DEDICATED_CAPACITY_NAME, capacity_parameters=BODY)
        result = result.result()

        # /Capacities/get/List eligible SKUs for an existing capacity[get]
        result = self.mgmt_client.capacities.list_skus_for_capacity(resource_group_name=RESOURCE_GROUP, dedicated_capacity_name=DEDICATED_CAPACITY_NAME)

        # /Capacities/get/Get details of a capacity[get]
        result = self.mgmt_client.capacities.get_details(resource_group_name=RESOURCE_GROUP, dedicated_capacity_name=DEDICATED_CAPACITY_NAME)

        # /Capacities/get/List capacities in resource group[get]
        result = self.mgmt_client.capacities.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /Capacities/get/Get details of a capacity[get]
        result = self.mgmt_client.capacities.get_details(resource_group_name=RESOURCE_GROUP, dedicated_capacity_name=DEDICATED_CAPACITY_NAME)

        # /Capacities/get/List eligible SKUs for a new capacity[get]
        result = self.mgmt_client.capacities.list_skus()

        # /Capacities/post/Suspend capacity[post]
        result = self.mgmt_client.capacities.suspend(resource_group_name=RESOURCE_GROUP, dedicated_capacity_name=DEDICATED_CAPACITY_NAME)
        result = result.result()

        # /Capacities/post/Get details of a capacity[post]
        result = self.mgmt_client.capacities.resume(resource_group_name=RESOURCE_GROUP, dedicated_capacity_name=DEDICATED_CAPACITY_NAME)
        result = result.result()

        # /Capacities/patch/Update capacity parameters[patch]
        BODY = {
          "sku": {
            "name": "A1",
            "tier": "PBIE_Azure"
          },
          "tags": {
            "test_key": "testValue"
          },
          "administration": {
            "members": [
             "user1@microsoft.com",
             "user2@microsoft.com"
            ]
          }
        }
        result = self.mgmt_client.capacities.update(resource_group_name=RESOURCE_GROUP, dedicated_capacity_name=DEDICATED_CAPACITY_NAME, capacity_update_parameters=BODY)
        result = result.result()

        # /Capacities/post/Check name availability of a capacity[post]
        result = self.mgmt_client.capacities.check_name_availability(location="eastus", name="azsdktest", type="Microsoft.PowerBIDedicated/capacities")

        # /Capacities/delete/Get details of a capacity[delete]
        result = self.mgmt_client.capacities.delete(resource_group_name=RESOURCE_GROUP, dedicated_capacity_name=DEDICATED_CAPACITY_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
