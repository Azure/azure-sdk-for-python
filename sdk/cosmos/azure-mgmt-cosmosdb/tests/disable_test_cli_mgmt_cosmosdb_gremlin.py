# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   GremlinResources: 16/16

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
    def test_gremlin_resource(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        GRAPH_NAME = "myGraph"

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
          "capabilities": [
            {
              "name": "EnableGremlin"
            }
          ],
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/put/CosmosDBGremlinDatabaseCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": DATABASE_NAME
          },
          "options": {
            "throughput": "2000"
          }
        }
        result = self.mgmt_client.gremlin_resources.begin_create_update_gremlin_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_gremlin_database_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/put/CosmosDBGremlinGraphCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": GRAPH_NAME,
            "indexing_policy": {
              "indexing_mode": "Consistent",
              "automatic": True,
              "included_paths": [
                {
                  "path": "/*",
                  "indexes": [
                    {
                      "kind": "Range",
                      "data_type": "String",
                      "precision": "-1"
                    },
                    {
                      "kind": "Range",
                      "data_type": "Number",
                      "precision": "-1"
                    }
                  ]
                }
              ],
              "excluded_paths": []
            },
            "partition_key": {
              "paths": [
                "/AccountNumber"
              ],
              "kind": "Hash"
            },
            "default_ttl": "100",
            "conflict_resolution_policy": {
              "mode": "LastWriterWins",
              "conflict_resolution_path": "/path"
            }
          },
          "options": {
            "throughput": "2000"
          }
        }
        result = self.mgmt_client.gremlin_resources.begin_create_update_gremlin_graph(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME, create_update_gremlin_graph_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/put/CosmosDBGremlinDatabaseThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.gremlin_resources.begin_update_gremlin_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/put/CosmosDBGremlinGraphThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.gremlin_resources.begin_update_gremlin_graph_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinGraphThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.get_gremlin_graph_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinDatabaseThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.get_gremlin_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinGraphGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.get_gremlin_graph(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinGraphList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.list_gremlin_graphs(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinDatabaseGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.get_gremlin_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinDatabaseList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.list_gremlin_databases(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/post/CosmosDBGremlinGraphMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_migrate_gremlin_graph_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/post/CosmosDBGremlinGraphMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_migrate_gremlin_graph_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/post/CosmosDBGremlinDatabaseMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_migrate_gremlin_database_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/post/CosmosDBGremlinDatabaseMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_migrate_gremlin_database_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/delete/CosmosDBGremlinGraphDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_delete_gremlin_graph(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/delete/CosmosDBGremlinDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_delete_gremlin_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()
