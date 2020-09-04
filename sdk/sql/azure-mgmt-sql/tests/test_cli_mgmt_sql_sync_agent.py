# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   SyncAgents: 6/6

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

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sync_agent(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        DATABASE_NAME = "mydatabase"
        SYNC_AGENT_NAME = "mysyncagent"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncAgents/put/Create a new sync agent[put]
#--------------------------------------------------------------------------
        BODY = {
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.sync_agents.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncAgents/get/Get sync agent linked databases[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.list_linked_databases(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME)

#--------------------------------------------------------------------------
        # /SyncAgents/get/Get a sync agent[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME)

#--------------------------------------------------------------------------
        # /SyncAgents/get/Get sync agents under a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /SyncAgents/post/Generate a sync agent key[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.generate_key(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME)

#--------------------------------------------------------------------------
        # /SyncAgents/delete/Delete a sync agent[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()
