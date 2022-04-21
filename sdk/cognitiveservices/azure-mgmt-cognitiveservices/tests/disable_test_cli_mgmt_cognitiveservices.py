# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 14
# Methods Covered : 14
# Examples Total  : 15
# Examples Tested : 13
# Coverage %      : 87
# ----------------------

import unittest

import azure.mgmt.cognitiveservices
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtCognitiveServicesTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCognitiveServicesTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.cognitiveservices.CognitiveServicesManagementClient
        )
    
    @unittest.skip('hard to test')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_cognitiveservices(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myAccount"
        LOCATION = "myLocation"

        # /Accounts/put/Create Account Min[put]
        BODY = {
          "location": "West US",
          "kind": "CognitiveServices",
          "sku": {
            "name": "S0"
          },
          "identity": {
            "type": "SystemAssigned"
          }
        }
        result = self.mgmt_client.accounts.create(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, account=BODY)

        # /Accounts/put/Create Account[put]
        BODY = {
          "location": "West US",
          "kind": "Emotion",
          "sku": {
            "name": "S0"
          },
          "properties": {
            "encryption": {
              "key_vault_properties": {
                "key_name": "KeyName",
                "key_version": "891CF236-D241-4738-9462-D506AF493DFA",
                "key_vault_uri": "https://pltfrmscrts-use-pc-dev.vault.azure.net/"
              },
              "key_source": "Microsoft.KeyVault"
            },
            "user_owned_storage": [
              {
                "resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccountsfelixwatest"
              }
            ]
          },
          "identity": {
            "type": "SystemAssigned"
          }
        }
        # result = self.mgmt_client.accounts.create(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, account=BODY)

        # /Accounts/get/Get Usages[get]
        result = self.mgmt_client.accounts.get_usages(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

        # /Accounts/get/List SKUs[get]
        result = self.mgmt_client.accounts.list_skus(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

        # /Accounts/get/Get Account[get]
        result = self.mgmt_client.accounts.get_properties(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

        # /Accounts/get/List Accounts by Resource Group[get]
        result = self.mgmt_client.accounts.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /Accounts/get/List Accounts by Subscription[get]
        result = self.mgmt_client.accounts.list()

        # /ResourceSkus/get/Regenerate Keys[get]
        result = self.mgmt_client.resource_skus.list()

        # /Operations/get/Get Operations[get]
        result = self.mgmt_client.operations.list()

        # /Accounts/post/Regenerate Keys[post]
        result = self.mgmt_client.accounts.regenerate_key(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, key_name="Key2")

        # /Accounts/post/List Keys[post]
        result = self.mgmt_client.accounts.list_keys(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

        # /Accounts/patch/Update Account[patch]
        BODY = {
          "sku": {
            "name": "S2"
          }
        }
        # result = self.mgmt_client.accounts.update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, account=BODY)

        # //post/Check SKU Availability[post]
        SKUS = [
            "S0"
        ]
        result = self.mgmt_client.check_sku_availability(location="eastus", skus=SKUS, kind="Face", type="Microsoft.CognitiveServices/accounts")

        # /Accounts/delete/Delete Account[delete]
        result = self.mgmt_client.accounts.delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
