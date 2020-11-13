# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   NotebookWorkspaces: 0/7

import unittest

import azure.mgmt.cosmosdb
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtCosmosDBTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCosmosDBTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.cosmosdb.CosmosDBManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_notebook_workspace(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        NOTEBOOK_WORKSPACE_NAME = "myNotebookWorkspace"

#--------------------------------------------------------------------------
        # /DatabaseAccounts/put/CosmosDBDatabaseAccountCreateMin[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "kind": "GlobalDocumentDB",
          "database_account_offer_type": "Standard",
          "locations": [
            {
              "location_name": "eastus",
              "is_zone_redundant": False,
              "failover_priority": "0"
            },
          ],
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/put/CosmosDBNotebookWorkspaceCreate[put]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.notebook_workspaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME, notebook_create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/get/CosmosDBNotebookWorkspaceGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.get(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME)

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/get/CosmosDBNotebookWorkspaceList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.list_by_database_account(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/post/CosmosDBNotebookWorkspaceRegenerateAuthToken[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.begin_regenerate_auth_token(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/post/CosmosDBNotebookWorkspaceListConnectionInfo[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.list_connection_info(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME)

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/post/CosmosDBNotebookWorkspaceStart[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.begin_start(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/delete/CosmosDBNotebookWorkspaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()
