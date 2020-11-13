# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   FailoverGroups: 7/7

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
    def test_failover_group(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        PARTNER_SERVER_NAME = "mypartnerserverxpxy"
        FAILOVER_GROUP_NAME = "myfailovergroupxyz"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": "eastus2",
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=PARTNER_SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/put/Create failover group[put]
#--------------------------------------------------------------------------
        BODY = {
          "read_write_endpoint": {
            "failover_policy": "Automatic",
            "failover_with_data_loss_grace_period_minutes": "480"
          },
          "read_only_endpoint": {
            "failover_policy": "Disabled"
          },
          "partner_servers": [
            {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + PARTNER_SERVER_NAME
            }
          ],
          "databases": [
            # "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/Default/providers/Microsoft.Sql/servers/failover-group-primary-server/databases/testdb-1",
          ]
        }
        result = self.mgmt_client.failover_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/get/Get failover group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME)

#--------------------------------------------------------------------------
        # /FailoverGroups/get/List failover group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /FailoverGroups/post/Forced failover of a failover group allowing data loss[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.begin_force_failover_allow_data_loss(resource_group_name=RESOURCE_GROUP, server_name=PARTNER_SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/patch/Update failover group[patch]
#--------------------------------------------------------------------------
        BODY = {
          "read_write_endpoint": {
            "failover_policy": "Automatic",
            "failover_with_data_loss_grace_period_minutes": "120"
          },
          "databases": [
            # "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/Default/providers/Microsoft.Sql/servers/failover-group-primary-server/databases/testdb-1"
          ]
        }
        result = self.mgmt_client.failover_groups.begin_update(resource_group_name=RESOURCE_GROUP, server_name=PARTNER_SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/post/Planned failover of a failover group[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.begin_failover(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/delete/Delete failover group[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=PARTNER_SERVER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()
