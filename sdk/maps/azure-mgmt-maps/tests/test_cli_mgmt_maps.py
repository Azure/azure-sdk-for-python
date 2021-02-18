# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 10
# Methods Covered : 10
# Examples Total  : 10
# Examples Tested : 9
# Coverage %      : 90
# ----------------------

import unittest

import azure.mgmt.maps
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtMapsManagementClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMapsManagementClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.maps.MapsManagementClient
        )
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_maps(self, resource_group):

        ACCOUNT_NAME = "accountname"
        # CreateAccount[put]
        BODY = {
          "location": "global",
          "sku": {
            "name": "S0"
          },
          "tags": {
            "test": "true"
          }
        }
        result = self.mgmt_client.accounts.create_or_update(resource_group.name, ACCOUNT_NAME, BODY)

        # GetAccount[get]
        result = self.mgmt_client.accounts.get(resource_group.name, ACCOUNT_NAME)

        # ListAccountsByResourceGroup[get]
        result = self.mgmt_client.accounts.list_by_resource_group(resource_group.name)

        # ListAccountsBySubscription[get]
        result = self.mgmt_client.accounts.list_by_subscription()

        # GetOperations[get]
        result = self.mgmt_client.accounts.list_operations()

        # RegenerateKey[post]
        # BODY = {
        #   "key_type": "primary"
        # }
        key_type = "primary"
        result = self.mgmt_client.accounts.regenerate_keys(resource_group.name, ACCOUNT_NAME, key_type)

        # ListKeys[post]
        result = self.mgmt_client.accounts.list_keys(resource_group.name, ACCOUNT_NAME)

        # UpdateAccount[patch]
        BODY = {
          "tags": {
            "special_tag": "true"
          }
        }
        result = self.mgmt_client.accounts.update(resource_group.name, ACCOUNT_NAME, BODY)

        # TODO: Multiple resources involved
        # # MoveAccounts[post]
        # BODY = {
        #   "target_resource_group": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "",
        #   "resource_ids": [
        #     "/subscriptions/21a9967a-e8a9-4656-a70b-96ff1c4d05a0/resourceGroups/myResourceGroup/providers/Microsoft.Maps/accounts/myMapsAccount",
        #     "/subscriptions/21a9967a-e8a9-4656-a70b-96ff1c4d05a0/resourceGroups/myResourceGroup/providers/Microsoft.Maps/accounts/myMapsAccount2"
        #   ]
        # }
        # result = self.mgmt_client.accounts.move(resource_group.name, BODY)

        # DeleteAccount[delete]
        result = self.mgmt_client.accounts.delete(resource_group.name, ACCOUNT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
