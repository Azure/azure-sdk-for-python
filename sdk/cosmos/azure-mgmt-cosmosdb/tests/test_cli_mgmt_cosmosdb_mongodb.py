# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   MongoDBResources: 16/16

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
    def test_mongodb_resource(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        COLLECTION_NAME = "myCollection"

#--------------------------------------------------------------------------
        # /DatabaseAccounts/put/CosmosDBDatabaseAccountCreateMin[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "kind": "MongoDB",
          "database_account_offer_type": "Standard",
          "locations": [
            {
              "location_name": "eastus",
              "is_zone_redundant": False,
              "failover_priority": "0"
            }
          ],
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/put/CosmosDBMongoDBDatabaseCreateUpdate[put]
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
        result = self.mgmt_client.mongo_db_resources.begin_create_update_mongo_db_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_mongo_db_database_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/put/CosmosDBMongoDBCollectionCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": COLLECTION_NAME,
            "shard_key": {
              "theShardKey": "Hash"
            }
          },
          "options": {
            "throughput": "2000"
          }
        }
        result = self.mgmt_client.mongo_db_resources.begin_create_update_mongo_db_collection(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME, create_update_mongo_db_collection_parameters=BODY)
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
        result = self.mgmt_client.mongo_db_resources.begin_update_mongo_db_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, update_throughput_parameters=BODY)
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
        result = self.mgmt_client.mongo_db_resources.begin_update_mongo_db_collection_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBCollectionThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.get_mongo_db_collection_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBDatabaseThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.get_mongo_db_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBCollectionGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.get_mongo_db_collection(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBCollectionList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.list_mongo_db_collections(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBDatabaseGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.get_mongo_db_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/get/CosmosDBMongoDBDatabaseList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.list_mongo_db_databases(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /MongoDBResources/post/CosmosDBMongoDBCollectionMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.begin_migrate_mongo_db_collection_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/post/CosmosDBMongoDBCollectionMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.begin_migrate_mongo_db_collection_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/post/CosmosDBMongoDBDatabaseMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.begin_migrate_mongo_db_database_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/post/CosmosDBMongoDBDatabaseMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.begin_migrate_mongo_db_database_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/delete/CosmosDBMongoDBCollectionDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.begin_delete_mongo_db_collection(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, collection_name=COLLECTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /MongoDBResources/delete/CosmosDBMongoDBDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.mongo_db_resources.begin_delete_mongo_db_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()
