# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 132
# Methods Covered : 132
# Examples Total  : 134
# Examples Tested : 134
# Coverage %      : 100
# ----------------------

# Current Operation Coverage:
#   DatabaseAccounts: 18/18
#   Operations: 1/1
#   Database: 3/3
#   Collection: 3/3
#   CollectionRegion: 1/1
#   DatabaseAccountRegion: 1/1
#   PercentileSourceTarget: 1/1
#   PercentileTarget: 1/1
#   Percentile: 1/1
#   CollectionPartitionRegion: 1/1
#   CollectionPartition: 2/2
#   PartitionKeyRangeId: 1/1
#   PartitionKeyRangeIdRegion: 1/1
#   SqlResources: 28/28
#   MongoDBResources: 16/16
#   TableResources: 8/8
#   CassandraResources: 16/16
#   GremlinResources: 16/16
#   NotebookWorkspaces: 7/7
#   PrivateLinkResources: 2/2
#   PrivateEndpointConnections: 4/4

import unittest

import azure.mgmt.cosmosdb
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtCosmosDBTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCosmosDBTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.cosmosdb.CosmosDBManagementClient
        )
    

        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):

        azure_operation_poller = self.network_client.virtual_networks.create_or_update(
            group_name,
            network_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            },
        )
        result_create = azure_operation_poller.result()

        async_subnet_creation = self.network_client.subnets.create_or_update(
            group_name,
            network_name,
            subnet_name,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()

        return subnet_info

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_cosmosdb(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myAccount"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mySubnet"
        DATABASE_RID = "myDatabaseRid"
        COLLECTION_RID = "myCollectionRid"
        REGION = "myRegion"
        SOURCE_REGION = "mySourceRegion"
        TARGET_REGION = "myTargetRegion"
        PERCENTILE_NAME = "myPercentile"
        PARTITION_NAME = "myPartition"
        PARTITION_KEY_RANGE_ID = "myPartitionKeyRangeId"
        DATABASE_NAME = "myDatabase"
        THROUGHPUT_SETTING_NAME = "myThroughputSetting"
        CONTAINER_NAME = "myContainer"
        STORED_PROCEDURE_NAME = "myStoredProcedure"
        USER_DEFINED_FUNCTION_NAME = "myUserDefinedFunction"
        TRIGGER_NAME = "myTrigger"
        COLLECTION_NAME = "myCollection"
        TABLE_NAME = "myTable"
        KEYSPACE_NAME = "myKeyspace"
        GRAPH_NAME = "myGraph"
        NOTEBOOK_WORKSPACE_NAME = "myNotebookWorkspace"
        GROUP_NAME = "myGroup"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "myPrivateEndpointConnection"

#--------------------------------------------------------------------------
        # /DatabaseAccounts/put/CosmosDBDatabaseAccountCreateMin[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "database_account_offer_type": "Standard",
          "locations": [
            {
              "failover_priority": "0",
              "location_name": "southcentralus",
              "is_zone_redundant": False
            }
          ]
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/put/CosmosDBDatabaseAccountCreateMax[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "kind": "MongoDB",
          "database_account_offer_type": "Standard",
          "ip_rules": [
            {
              "ip_address_or_range": "23.43.230.120"
            },
            {
              "ip_address_or_range": "110.12.240.0/12"
            }
          ],
          "is_virtual_network_filter_enabled": True,
          "virtual_network_rules": [
            {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
              "ignore_missing_vnet_service_endpoint": False
            }
          ],
          "locations": [
            {
              "failover_priority": "0",
              "location_name": "southcentralus",
              "is_zone_redundant": False
            },
            {
              "failover_priority": "1",
              "location_name": "eastus",
              "is_zone_redundant": False
            }
          ],
          "consistency_policy": {
            "default_consistency_level": "BoundedStaleness",
            "max_interval_in_seconds": "10",
            "max_staleness_prefix": "200"
          },
          "key_vault_key_uri": "https://myKeyVault.vault.azure.net",
          "enable_free_tier": False,
          "api_properties": {
            "server_version": "3.2"
          },
          "enable_analytical_storage": True,
          "cors": [
            {
              "allowed_origins": "https://test"
            }
          ]
        }
        # result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /TableResources/put/CosmosDBTableReplace[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "tableName"
          }
        }
        result = self.mgmt_client.table_resources.begin_create_update_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME, create_update_table_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlDatabaseCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "databaseName"
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_sql_database_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/put/CosmosDBMongoDBDatabaseCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "databaseName"
          }
        }
        result = self.mgmt_client.mongo_dbresources.begin_create_update_mongo_dbdatabase(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_mongo_dbdatabase_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/put/CosmosDBGremlinDatabaseCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "databaseName"
          }
        }
        result = self.mgmt_client.gremlin_resources.begin_create_update_gremlin_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_gremlin_database_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/put/CosmosDBCassandraKeyspaceCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "keyspaceName"
          }
        }
        result = self.mgmt_client.cassandra_resources.begin_create_update_cassandra_keyspace(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, create_update_cassandra_keyspace_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/put/CosmosDBNotebookWorkspaceCreate[put]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.notebook_workspaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME, notebook_create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/put/CosmosDBGremlinGraphCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "graphName",
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
            "unique_key_policy": {
              "unique_keys": [
                {
                  "paths": [
                    "/testPath"
                  ]
                }
              ]
            },
            "conflict_resolution_policy": {
              "mode": "LastWriterWins",
              "conflict_resolution_path": "/path"
            }
          }
        }
        result = self.mgmt_client.gremlin_resources.begin_create_update_gremlin_graph(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME, create_update_gremlin_graph_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/put/CosmosDBCassandraTableCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "tableName",
            "default_ttl": "100",
            "analytical_storage_ttl": "500",
            "schema": {
              "columns": [
                {
                  "name": "columnA",
                  "type": "Ascii"
                }
              ],
              "partition_keys": [
                {
                  "name": "columnA"
                }
              ],
              "cluster_keys": [
                {
                  "name": "columnA",
                  "order_by": "Asc"
                }
              ]
            }
          }
        }
        result = self.mgmt_client.cassandra_resources.begin_create_update_cassandra_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME, create_update_cassandra_table_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlContainerCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "containerName",
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
            "unique_key_policy": {
              "unique_keys": [
                {
                  "paths": [
                    "/testPath"
                  ]
                }
              ]
            },
            "conflict_resolution_policy": {
              "mode": "LastWriterWins",
              "conflict_resolution_path": "/path"
            }
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, create_update_sql_container_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/put/Approve or reject a private endpoint connection with a given name.[put]
#--------------------------------------------------------------------------
        BODY = {
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "Approved by johndoe@contoso.com"
          }
        }
        result = self.mgmt_client.private_endpoint_connections.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/put/CosmosDBMongoDBCollectionCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": "collectionName",
            "indexes": [
              {
                "key": {
                  "keys": [
                    "testKey"
                  ]
                },
                "options": {
                  "expire_after_seconds": "100",
                  "unique": True
                }
              }
            ],
            "shard_key": {
              "test_key": "Hash"
            },
            "analytical_storage_ttl": "500"
          }
        }
        result = self.mgmt_client.mongo_dbresources.begin_create_update_mongo_dbcollection(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME, create_update_mongo_dbcollection_parameters=BODY)
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
        result = self.mgmt_client.table_resources.begin_update_table_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlDatabaseThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.sql_resources.begin_update_sql_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/put/CosmosDBMongoDBDatabaseThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.mongo_dbresources.begin_update_mongo_dbdatabase_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
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
        result = self.mgmt_client.gremlin_resources.begin_update_gremlin_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/put/CosmosDBCassandraKeyspaceThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.cassandra_resources.begin_update_cassandra_keyspace_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlTriggerCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "resource": {
            "id": "triggerName",
            "body": "body",
            "trigger_type": "triggerType",
            "trigger_operation": "triggerOperation"
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_trigger(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, trigger_name=TRIGGER_NAME, create_update_sql_trigger_parameters=BODY)
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
        result = self.mgmt_client.gremlin_resources.begin_update_gremlin_graph_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlStoredProcedureCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "resource": {
            "id": "storedProcedureName",
            "body": "body"
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_stored_procedure(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, stored_procedure_name=STORED_PROCEDURE_NAME, create_update_sql_stored_procedure_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/put/CosmosDBCassandraTableThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.cassandra_resources.begin_update_cassandra_table_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlContainerThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.sql_resources.begin_update_sql_container_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlUserDefinedFunctionCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "resource": {
            "id": "userDefinedFunctionName",
            "body": "body"
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_user_defined_function(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, user_defined_function_name=USER_DEFINED_FUNCTION_NAME, create_update_sql_user_defined_function_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/put/CosmosDBMongoDBCollectionThroughputUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "throughput": "400"
          }
        }
        result = self.mgmt_client.mongo_dbresources.begin_update_mongo_dbcollection_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /PartitionKeyRangeIdRegion/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.partition_key_range_id_region.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region=REGION, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, partition_key_range_id=PARTITION_KEY_RANGE_ID, filter="$filter=(name.value eq 'Max RUs Per Second') and timeGrain eq duration'PT1M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T23:58:55.2780000Z")

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBCollectionThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.get_mongo_dbcollection_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlUserDefinedFunctionGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_user_defined_function(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, user_defined_function_name=USER_DEFINED_FUNCTION_NAME)

#--------------------------------------------------------------------------
        # /PartitionKeyRangeId/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.partition_key_range_id.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, partition_key_range_id=PARTITION_KEY_RANGE_ID, filter="$filter=(name.value eq 'Max RUs Per Second') and timeGrain eq duration'PT1M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T23:58:55.2780000Z")

#--------------------------------------------------------------------------
        # /CollectionPartitionRegion/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.collection_partition_region.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region=REGION, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, partition_name=PARTITION_NAME, filter="$filter=(name.value eq 'Max RUs Per Second') and timeGrain eq duration'PT1M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T23:58:55.2780000Z")

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlContainerThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_container_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraTableThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.get_cassandra_table_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlStoredProcedureGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_stored_procedure(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, stored_procedure_name=STORED_PROCEDURE_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinGraphThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.get_gremlin_graph_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /PercentileSourceTarget/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.percentile_source_target.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, source_region=SOURCE_REGION, target_region=TARGET_REGION, percentile_name=PERCENTILE_NAME, filter="$filter=(name.value eq 'Probabilistic Bounded Staleness') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /CollectionPartition/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.collection_partition.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, partition_name=PARTITION_NAME, filter="$filter=(name.value eq 'Max RUs Per Second') and timeGrain eq duration'PT1M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T23:58:55.2780000Z")

#--------------------------------------------------------------------------
        # /CollectionPartition/get/CosmosDBCollectionGetUsages[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.collection_partition.list_usages(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, partition_name=PARTITION_NAME, filter="$filter=name.value eq 'Partition Storage'")

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlTriggerGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_trigger(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, trigger_name=TRIGGER_NAME)

#--------------------------------------------------------------------------
        # /CollectionRegion/get/CosmosDBRegionCollectionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.collection_region.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region=REGION, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, filter="$filter=(name.value eq 'Total Requests') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraKeyspaceThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.get_cassandra_keyspace_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinDatabaseThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.get_gremlin_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlUserDefinedFunctionList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_user_defined_functions(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBDatabaseThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.get_mongo_dbdatabase_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlStoredProcedureList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_stored_procedures(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlDatabaseThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /Collection/get/CosmosDBCollectionGetMetricDefinitions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.collection.list_metric_definitions(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlTriggerList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_triggers(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /TableResources/get/CosmosDBTableThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.get_table_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBCollectionGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.get_mongo_dbcollection(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME)

#--------------------------------------------------------------------------
        # /Collection/get/CosmosDBCollectionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.collection.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, filter="$filter=(name.value eq 'Total Requests') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /Collection/get/CosmosDBCollectionGetUsages[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.collection.list_usages(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, filter="$filter=name.value eq 'Storage'")

#--------------------------------------------------------------------------
        # /PercentileTarget/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.percentile_target.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, target_region=TARGET_REGION, percentile_name=PERCENTILE_NAME, filter="$filter=(name.value eq 'Probabilistic Bounded Staleness') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.list_by_database_account(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlContainerGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraTableGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.get_cassandra_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinGraphGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.get_gremlin_graph(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBCollectionList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.list_mongo_dbcollections(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/get/CosmosDBNotebookWorkspaceGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.get(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME)

#--------------------------------------------------------------------------
        # /Database/get/CosmosDBDatabaseGetMetricDefinitions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database.list_metric_definitions(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraTableList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.list_cassandra_tables(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinGraphList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.list_gremlin_graphs(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlContainerList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_containers(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraKeyspaceGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.get_cassandra_keyspace(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)

#--------------------------------------------------------------------------
        # /PrivateLinkResources/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_link_resources.list_by_database_account(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /Database/get/CosmosDBDatabaseGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID, filter="$filter=(name.value eq 'Total Requests') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinDatabaseGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.get_gremlin_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBDatabaseGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.get_mongo_dbdatabase(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Database/get/CosmosDBDatabaseGetUsages[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database.list_usages(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_rid=DATABASE_RID, filter="$filter=name.value eq 'Storage'")

#--------------------------------------------------------------------------
        # /Percentile/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.percentile.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, percentile_name=PERCENTILE_NAME, filter="$filter=(name.value eq 'Probabilistic Bounded Staleness') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlDatabaseGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccountRegion/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_account_region.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region=REGION, filter="$filter=(name.value eq 'Total Requests') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.list_by_database_account(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /TableResources/get/CosmosDBTableGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.get_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME)

#--------------------------------------------------------------------------
        # /PrivateLinkResources/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_link_resources.list_by_database_account(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraKeyspaceList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.list_cassandra_keyspaces(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/get/CosmosDBNotebookWorkspaceList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.list_by_database_account(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/get/CosmosDBDatabaseAccountGetMetricDefinitions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_metric_definitions(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBDatabaseList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.list_mongo_dbdatabases(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /GremlinResources/get/CosmosDBGremlinDatabaseList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.list_gremlin_databases(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlDatabaseList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_databases(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/get/CosmosDBDatabaseAccountListReadOnlyKeys[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.get_read_only_keys(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/get/CosmosDBDatabaseAccountGetMetrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, filter="$filter=(name.value eq 'Total Requests') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /DatabaseAccounts/get/CosmosDBDatabaseAccountGetUsages[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_usages(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, filter="$filter=name.value eq 'Storage'")

#--------------------------------------------------------------------------
        # /TableResources/get/CosmosDBTableList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.list_tables(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/get/CosmosDBDatabaseAccountGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.get(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/get/CosmosDBDatabaseAccountListByResourceGroup[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/get/CosmosDBDatabaseAccountList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list()

#--------------------------------------------------------------------------
        # /Operations/get/CosmosDBOperationsList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.operations.list()

#--------------------------------------------------------------------------
        # /MongoDBResources/post/CosmosDBMongoDBCollectionMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.begin_migrate_mongo_dbcollection_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/post/CosmosDBSqlContainerMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_migrate_sql_container_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/post/CosmosDBMongoDBCollectionMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.begin_migrate_mongo_dbcollection_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/post/CosmosDBCassandraTableMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_migrate_cassandra_table_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/post/CosmosDBGremlinGraphMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_migrate_gremlin_graph_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/post/CosmosDBSqlContainerMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_migrate_sql_container_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/post/CosmosDBCassandraTableMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_migrate_cassandra_table_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/post/CosmosDBGremlinGraphMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_migrate_gremlin_graph_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/post/CosmosDBCassandraKeyspaceMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_migrate_cassandra_keyspace_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/post/CosmosDBMongoDBDatabaseMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.begin_migrate_mongo_dbdatabase_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/post/CosmosDBGremlinDatabaseMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_migrate_gremlin_database_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/post/CosmosDBSqlDatabaseMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_migrate_sql_database_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/post/CosmosDBCassandraKeyspaceMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_migrate_cassandra_keyspace_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/post/CosmosDBMongoDBDatabaseMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.begin_migrate_mongo_dbdatabase_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/post/CosmosDBGremlinDatabaseMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_migrate_gremlin_database_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/post/CosmosDBSqlDatabaseMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_migrate_sql_database_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /TableResources/post/CosmosDBTableMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.begin_migrate_table_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /TableResources/post/CosmosDBTableMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.table_resources.begin_migrate_table_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, table_name=TABLE_NAME, throughput_setting_name=THROUGHPUT_SETTING_NAME)
        result = result.result()

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
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountFailoverPriorityChange[post]
#--------------------------------------------------------------------------
        BODY = {
          "failover_policies": [
            {
              "location_name": "eastus",
              "failover_priority": "0"
            },
            {
              "location_name": "westus",
              "failover_priority": "1"
            }
          ]
        }
        result = self.mgmt_client.database_accounts.begin_failover_priority_change(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, failover_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountListConnectionStrings[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_connection_strings(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountListConnectionStringsMongo[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_connection_strings(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountOfflineRegion[post]
#--------------------------------------------------------------------------
        [
          {
            "region": "North Europe"
          }
        ]
        result = self.mgmt_client.database_accounts.begin_offline_region(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region_parameter_for_offline=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountRegenerateKey[post]
#--------------------------------------------------------------------------
        BODY = {
          "key_kind": "primary"
        }
        result = self.mgmt_client.database_accounts.begin_regenerate_key(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, key_to_regenerate=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountListReadOnlyKeys[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_read_only_keys(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountOnlineRegion[post]
#--------------------------------------------------------------------------
        [
          {
            "region": "North Europe"
          }
        ]
        result = self.mgmt_client.database_accounts.begin_online_region(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region_parameter_for_online=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountListKeys[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_keys(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/patch/CosmosDBDatabaseAccountPatch[patch]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "dept": "finance"
          },
          "ip_rules": [
            {
              "ip_address_or_range": "23.43.230.120"
            },
            {
              "ip_address_or_range": "110.12.240.0/12"
            }
          ],
          "is_virtual_network_filter_enabled": True,
          "virtual_network_rules": [
            {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
              "ignore_missing_vnet_service_endpoint": False
            }
          ],
          "consistency_policy": {
            "default_consistency_level": "BoundedStaleness",
            "max_interval_in_seconds": "10",
            "max_staleness_prefix": "200"
          },
          "enable_free_tier": False,
          "enable_analytical_storage": True
        }
        result = self.mgmt_client.database_accounts.begin_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/head/CosmosDBDatabaseAccountCheckNameExists[head]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.check_name_exists(account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlUserDefinedFunctionDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_user_defined_function(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, user_defined_function_name=USER_DEFINED_FUNCTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlStoredProcedureDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_stored_procedure(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, stored_procedure_name=STORED_PROCEDURE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlTriggerDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_trigger(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, trigger_name=TRIGGER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/delete/CosmosDBMongoDBCollectionDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.begin_delete_mongo_dbcollection(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/delete/Deletes a private endpoint connection with a given name.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlContainerDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/delete/CosmosDBCassandraTableDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_delete_cassandra_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/delete/CosmosDBGremlinGraphDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_delete_gremlin_graph(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, graph_name=GRAPH_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /NotebookWorkspaces/delete/CosmosDBNotebookWorkspaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.notebook_workspaces.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, notebook_workspace_name=NOTEBOOK_WORKSPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/delete/CosmosDBCassandraKeyspaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_delete_cassandra_keyspace(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/delete/CosmosDBMongoDBDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_dbresources.begin_delete_mongo_dbdatabase(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /GremlinResources/delete/CosmosDBGremlinDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.gremlin_resources.begin_delete_gremlin_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
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


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
