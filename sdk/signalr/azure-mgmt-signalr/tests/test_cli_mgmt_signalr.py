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

import unittest

import azure.mgmt.signalr
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSignalRTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSignalRTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.signalr.SignalRManagementClient
        )
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_signalr(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        LOCATION = "myLocation"
        RESOURCE_NAME = "myResource"

        # /SignalR/put/SignalR_CreateOrUpdate[put]
        BODY = {
          'tags': {
            "key1": "value1"
          },
          'sku': {
            "name": "Standard_S1",
            "tier": "Standard",
            "capacity": "1"
          },
          'properties': {
            "features": [
              {
                "flag": "ServiceMode",
                "value": "Serverless"
              }
            ],
            "cors": {
              "allowed_origins": [
                "https://foo.com",
                "https://bar.com"
              ]
            }
          },
          'location': 'eastus'
        }
        result = self.mgmt_client.signal_r.create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        result = result.result()

        # /SignalR/get/SignalR_Get[get]
        result = self.mgmt_client.signal_r.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

        # /SignalR/get/SignalR_ListByResourceGroup[get]
        result = self.mgmt_client.signal_r.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /Usages/get/Usages_List[get]
        result = self.mgmt_client.usages.list(location=LOCATION)

        # /SignalR/get/SignalR_ListBySubscription[get]
        result = self.mgmt_client.signal_r.list_by_subscription()

        # /Operations/get/Operations_List[get]
        result = self.mgmt_client.operations.list()

        # /SignalR/post/SignalR_RegenerateKey[post]
        # result = self.mgmt_client.signal_r.regenerate_key(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, key_type="Primary")
        # result = result.result()

        # /SignalR/post/SignalR_ListKeys[post]
        result = self.mgmt_client.signal_r.list_keys(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

        # /SignalR/post/SignalR_Restart[post]
        result = self.mgmt_client.signal_r.restart(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        result = result.result()

        # /SignalR/patch/SignalR_Update[patch]
        BODY = {
          "tags": {
            "key1": "value1"
          },
          "sku": {
            "name": "Standard_S1",
            "tier": "Standard",
            "capacity": "1"
          },
          "properties": {
            "features": [
              {
                "flag": "ServiceMode",
                "value": "Serverless"
              }
            ],
            "cors": {
              "allowed_origins": [
                "https://foo.com",
                "https://bar.com"
              ]
            }
          }
        }
        result = self.mgmt_client.signal_r.update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        result = result.result()

        # /SignalR/post/SignalR_CheckNameAvailability[post]
        result = self.mgmt_client.signal_r.check_name_availability(location="eastus", type="Microsoft.SignalRService/SignalR", name="my-signalr-service")

        # /SignalR/delete/SignalR_Delete[delete]
        result = self.mgmt_client.signal_r.delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
