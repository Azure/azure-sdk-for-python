# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest

import azure.mgmt.appconfiguration
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAppConfigurationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAppConfigurationTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.appconfiguration.AppConfigurationManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_appconfiguration(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        CONFIGURATION_STORE_NAME = "contoso1"

        # ConfigurationStores_Create[put]
        BODY = {
          "location": "westus",
          "tags": {
            "my_tag": "myTagValue"
          }
        }
        result = self.mgmt_client.configuration_stores.create(resource_group.name, CONFIGURATION_STORE_NAME, BODY["location"], BODY["tags"])
        result = result.result()
        self.assertEqual(result.name, CONFIGURATION_STORE_NAME)
        self.assertEqual(result.provisioning_state, "Succeeded")

        # ConfigurationStores_Get[get]
        result = self.mgmt_client.configuration_stores.get(resource_group.name, CONFIGURATION_STORE_NAME)
        self.assertEqual(result.name, CONFIGURATION_STORE_NAME)
        self.assertEqual(result.provisioning_state, "Succeeded")

        # ConfigurationStores_CheckNameAvailable[post]
        result = self.mgmt_client.operations.check_name_availability(CONFIGURATION_STORE_NAME)
        self.assertEqual(result.name_available, False)

        # ConfigurationStores_ListKeys[post]
        BODY = {}
        result = self.mgmt_client.configuration_stores.list_keys(resource_group.name, CONFIGURATION_STORE_NAME)

        # ConfigurationStores_List[get]
        result = self.mgmt_client.configuration_stores.list()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
