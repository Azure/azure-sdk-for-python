# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   CassandraResources: 16/16

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
    def test_cassandra_resource(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        KEYSPACE_NAME = "myKeyspace"
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
            },
          ],
          "capabilities": [
            {
              "name": "EnableCassandra"
            }
          ],
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/put/CosmosDBCassandraKeyspaceCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": KEYSPACE_NAME
          },
          "options": {
            "throughput": "2000"
          }
        }
        result = self.mgmt_client.cassandra_resources.begin_create_update_cassandra_keyspace(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, create_update_cassandra_keyspace_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/put/CosmosDBCassandraTableCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": TABLE_NAME,
            "default_ttl": "100",
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
              ]
              
            }
          },
          "options": {
            "throughput": "2000"
          }
        }
        result = self.mgmt_client.cassandra_resources.begin_create_update_cassandra_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME, create_update_cassandra_table_parameters=BODY)
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
        result = self.mgmt_client.cassandra_resources.begin_update_cassandra_keyspace_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, update_throughput_parameters=BODY)
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
        result = self.mgmt_client.cassandra_resources.begin_update_cassandra_table_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraTableThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.get_cassandra_table_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraKeyspaceThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.get_cassandra_keyspace_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraTableGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.get_cassandra_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraTableList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.list_cassandra_tables(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraKeyspaceGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.get_cassandra_keyspace(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/get/CosmosDBCassandraKeyspaceList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.list_cassandra_keyspaces(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /CassandraResources/post/CosmosDBCassandraTableMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_migrate_cassandra_table_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/post/CosmosDBCassandraTableMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_migrate_cassandra_table_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/post/CosmosDBCassandraKeyspaceMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_migrate_cassandra_keyspace_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/post/CosmosDBCassandraKeyspaceMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_migrate_cassandra_keyspace_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/delete/CosmosDBCassandraTableDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_delete_cassandra_table(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME, table_name=TABLE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /CassandraResources/delete/CosmosDBCassandraKeyspaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.cassandra_resources.begin_delete_cassandra_keyspace(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, keyspace_name=KEYSPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()
