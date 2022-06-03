# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import unittest
import azure.mgmt.apimanagement
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtApimanagementTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtApimanagementTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.apimanagement.ApiManagementClient
        )

    @unittest.skip('Bad request')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_apiservice3(self, resource_group):
        # create
        SERVICE_NAME = self.get_resource_name('apiservice')
        BODY = {
            "location": AZURE_LOCATION,
        }
        result = self.mgmt_client.api_management_service.begin_create_or_update(resource_group.name, SERVICE_NAME, BODY)
        result.result()

        # get
        self.mgmt_client.api_management_service.get(resource_group.name, SERVICE_NAME)

        # update
        BODY = {
            "properties": {
                "customProperties": {
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10": "false"
                }
            }
        }
        result = self.mgmt_client.api_management_service.begin_update(resource_group.name, SERVICE_NAME, BODY)
        result.result()

        # delete
        result = self.mgmt_client.api_management_service.delete(resource_group.name, SERVICE_NAME)
        result.result()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
