# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   SyncAgents: 6/6
#   SyncGroups: 10/11
#   SyncMembers: 7/7

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

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sync_member(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        DATABASE_NAME = "mydatabase"
        SYNC_DATABASE_NAME = "mysyncdatabase"
        SYNC_MEMBER_NAME = "mysyncmember"
        # SYNC_MEMBER_NAME = SYNC_DATABASE_NAME
        SYNC_GROUP_NAME = "mysyncgroup"

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
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=SYNC_DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/put/Create a sync group[put]
#--------------------------------------------------------------------------
        BODY = {
          "interval": "-1",
          "conflict_resolution_policy": "HubWin",
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + SYNC_DATABASE_NAME,
          "hub_database_user_name": "hubUser",
          "use_private_link_connection": False
        }
        result = self.mgmt_client.sync_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncMembers/put/Create a new sync member[put]
#--------------------------------------------------------------------------
        BODY = {
          "database_type": "AzureSqlDatabase",
          "server_name": SERVER_NAME,
          "database_name": DATABASE_NAME, 
          "user_name": "dummylogin",
          "password": "Un53cuRE!",
          "sync_direction": "Bidirectional",
          "use_private_link_connection": False,
          "sync_state": "UnProvisioned"
        }
        result = self.mgmt_client.sync_members.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncMembers/get/Get a sync member schema[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.list_member_schemas(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME)

#--------------------------------------------------------------------------
        # /SyncMembers/get/Get a sync member[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME)

#--------------------------------------------------------------------------
        # /SyncMembers/get/List sync members under a sync group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.list_by_sync_group(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /SyncMembers/post/Refresh a sync member database schema[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.begin_refresh_member_schema(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncMembers/patch/Update an existing sync member[patch]
#--------------------------------------------------------------------------
        BODY = {
          "use_private_link_connection": False
        }
        result = self.mgmt_client.sync_members.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncMembers/delete/Delete a sync member[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/post/Cancel a sync group synchronization[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.cancel_sync(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/delete/Delete a sync group[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=SYNC_DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sync_group(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        DATABASE_NAME = "mydatabase"
        SYNC_DATABASE_NAME = "mysyncdatabase"
        SYNC_GROUP_NAME = "mysyncgroup"

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
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=SYNC_DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/put/Create a sync group[put]
#--------------------------------------------------------------------------
        BODY = {
          "interval": "-1",
          "conflict_resolution_policy": "HubWin",
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + SYNC_DATABASE_NAME,
          "hub_database_user_name": "hubUser",
          "use_private_link_connection": False
        }
        result = self.mgmt_client.sync_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/get/Get a hub database schema.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.list_hub_schemas(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/get/Get sync group logs[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.list_logs(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, start_time="2017-01-01T00:00:00", end_time="2017-12-31T00:00:00", type="All")

#--------------------------------------------------------------------------
        # /SyncGroups/get/Get a sync group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/get/List sync groups under a given database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/get/Get a sync database ID[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.list_sync_database_ids(location_name=AZURE_LOCATION)

#--------------------------------------------------------------------------
        # /SyncGroups/post/Refresh a hub database schema.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.begin_refresh_hub_schema(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/post/Trigger a sync group synchronization.[post]
#--------------------------------------------------------------------------
        # TODO: [Kaihui] (SyncOperation_GenericFailure) Failed to perform data sync operation: '' is not an active sync group.
        # result = self.mgmt_client.sync_groups.trigger_sync(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/patch/Update a sync group[patch]
#--------------------------------------------------------------------------
        BODY = {
          "interval": "-1",
          "conflict_resolution_policy": "HubWin",
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + SYNC_DATABASE_NAME,
          "hub_database_user_name": "hubUser",
          "hub_database_password": "hubPassword",
          "use_private_link_connection": False
        }
        result = self.mgmt_client.sync_groups.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/post/Cancel a sync group synchronization[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.cancel_sync(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/delete/Delete a sync group[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=SYNC_DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
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
