# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   TableResources: 8/8

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
        
    @unittest.skip('hard to test')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_table_resource(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        TABLE_NAME = "myTable"


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
            }
          ],
          "capabilities": [{
            "name": "EnableTable"
          }],
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /TableResources/put/CosmosDBTableReplace[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": TABLE_NAME
          },
          "options": {}
        }
        result = self.mgmt_client.table_resources.begin_create_update_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME, create_update_table_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /TableResources/put/CosmosDBTableThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.table_resources.begin_update_table_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /TableResources/get/CosmosDBTableThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.get_table_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME)

#--------------------------------------------------------------------------
        # /TableResources/get/CosmosDBTableList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.list_tables(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /TableResources/post/CosmosDBTableMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.begin_migrate_table_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /TableResources/post/CosmosDBTableMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.begin_migrate_table_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /TableResources/delete/CosmosDBTableDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.begin_delete_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()
