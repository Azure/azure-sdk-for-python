# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest

import azure.mgmt.web
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtWebSiteTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtWebSiteTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_appservice(self, resource_group):

        SERVERFARM_NAME = "myapimrndxyz"
        BODY = {
          "kind": "app",
          "location": "East US",
          "sku": {
            "name": "P1",
            "tier": "Premium",
            "size": "P1",
            "family": "P",
            "capacity": "1"
          }
        }
        azure_operation_poller = self.mgmt_client.app_service_plans.create_or_update(resource_group.name, SERVERFARM_NAME, BODY)
        result_create = azure_operation_poller.result()

        self.mgmt_client.list_skus()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()