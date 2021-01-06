# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 7
# Methods Covered : 7
# Examples Total  : 9
# Examples Tested : 9
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.databricks
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtDatabricksClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDatabricksClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.databricks.DatabricksClient
        )
        
    @ unittest.skip("unavailable in track2")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_databricks(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        WORKSPACE_NAME = "workspace1"
        RESOURCE_GROUP = "test_mgmt_databricks_test_resource_groups457f10501"

        # Create or update workspace[put]
        BODY = {
          "managed_resource_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "",
          "location": "westus"
        }
        result = self.mgmt_client.workspaces.create_or_update(BODY, resource_group.name, WORKSPACE_NAME)
        result = result.result()

        WORKSPACE_NAME_2 = WORKSPACE_NAME + "2"
        # Create or update workspace with custom parameters[put]
        BODY = {
          "managed_resource_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "",
          "location": "westus"
        }
        result = self.mgmt_client.workspaces.create_or_update(BODY, resource_group.name, WORKSPACE_NAME)
        result = result.result()

        # Get a workspace with custom parameters[get]
        result = self.mgmt_client.workspaces.get(resource_group.name, WORKSPACE_NAME)

        # Get a workspace[get]
        result = self.mgmt_client.workspaces.get(resource_group.name, WORKSPACE_NAME)

        # Lists workspaces[get]
        result = self.mgmt_client.workspaces.list_by_resource_group(resource_group.name)

        # Lists workspaces[get]
        result = self.mgmt_client.workspaces.list_by_resource_group(resource_group.name)

        # Operations[get]
        result = self.mgmt_client.operations.list()

        # Update a workspace's tags.[patch]
        # BODY = {
        #   "tags": {
        #     "mytag1": "myvalue1"
        #   }
        # }
        TAGS = {
          "mytag1": "myvalue1"
        }
        result = self.mgmt_client.workspaces.update(resource_group.name, WORKSPACE_NAME, TAGS)
        result = result.result()

        # Delete a workspace[delete]
        result = self.mgmt_client.workspaces.delete(resource_group.name, WORKSPACE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
