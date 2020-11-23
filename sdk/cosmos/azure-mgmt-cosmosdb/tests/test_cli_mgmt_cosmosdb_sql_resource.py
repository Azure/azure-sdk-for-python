# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   SqlResources: 28/28

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
    def test_sql_resource(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"

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
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlDatabaseCreateUpdate[put]
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
        result = self.mgmt_client.sql_resources.begin_create_update_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_sql_database_parameters=BODY)
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
        result = self.mgmt_client.sql_resources.begin_update_sql_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlDatabaseThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_database_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlDatabaseGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlDatabaseList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_databases(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/post/CosmosDBSqlDatabaseMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_migrate_sql_database_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/post/CosmosDBSqlDatabaseMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_migrate_sql_database_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sql_container(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        CONTAINER_NAME = "myContainer"

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
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlDatabaseCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": DATABASE_NAME
          },
          "options": {
            "throughput": 1000
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_sql_database_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlContainerCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": CONTAINER_NAME,
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
          },
          "options": {
            "throughput": "2000"
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, create_update_sql_container_parameters=BODY)
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
        result = self.mgmt_client.sql_resources.begin_update_sql_container_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, update_throughput_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlContainerThroughputGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_container_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlContainerGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlContainerList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_containers(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/post/CosmosDBSqlContainerMigrateToAutoscale[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_migrate_sql_container_to_autoscale(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/post/CosmosDBSqlContainerMigrateToManualThroughput[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_migrate_sql_container_to_manual_throughput(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlContainerDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sql_trigger(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        CONTAINER_NAME = "myContainer"
        TRIGGER_NAME = "myTrigger"

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
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlDatabaseCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": DATABASE_NAME
          },
          "options": {
            "throughput": 1000
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_sql_database_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlContainerCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": CONTAINER_NAME,
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
          },
          "options": {}
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, create_update_sql_container_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlTriggerCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "resource": {
            "id": TRIGGER_NAME,
            "body": "body",
            "trigger_type": "Pre",
            "trigger_operation": "All"
          },
          "options": {}
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_trigger(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, trigger_name=TRIGGER_NAME, create_update_sql_trigger_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlTriggerGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_trigger(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, trigger_name=TRIGGER_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlTriggerList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_triggers(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlTriggerDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_trigger(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, trigger_name=TRIGGER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlContainerDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sql_stored_procedure(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        CONTAINER_NAME = "myContainer"
        STORED_PROCEDURE_NAME = "myStoredProcedure"

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
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlDatabaseCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": DATABASE_NAME
          },
          "options": {
            "throughput": 1000
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_sql_database_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlContainerCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": CONTAINER_NAME,
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
          },
          "options": {}
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, create_update_sql_container_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlStoredProcedureCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "resource": {
            "id": STORED_PROCEDURE_NAME,
            "body": "body"
          },
          "options": {}
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_stored_procedure(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, stored_procedure_name=STORED_PROCEDURE_NAME, create_update_sql_stored_procedure_parameters=BODY)
        result = result.result() 

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlStoredProcedureGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_stored_procedure(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, stored_procedure_name=STORED_PROCEDURE_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlStoredProcedureList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_stored_procedures(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlStoredProcedureDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_stored_procedure(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, stored_procedure_name=STORED_PROCEDURE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlContainerDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sql_defined_function(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        CONTAINER_NAME = "myContainer"
        USER_DEFINED_FUNCTION_NAME = "myUserDefinedFunction"

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
          "api_properties": {}
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlDatabaseCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": DATABASE_NAME
          },
          "options": {
            "throughput": 1000
          }
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, create_update_sql_database_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlContainerCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "resource": {
            "id": CONTAINER_NAME,
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
          },
          "options": {}
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, create_update_sql_container_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/put/CosmosDBSqlUserDefinedFunctionCreateUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "resource": {
            "id": USER_DEFINED_FUNCTION_NAME,
            "body": "body"
          },
          "options": {}
        }
        result = self.mgmt_client.sql_resources.begin_create_update_sql_user_defined_function(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, user_defined_function_name=USER_DEFINED_FUNCTION_NAME, create_update_sql_user_defined_function_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlUserDefinedFunctionGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.get_sql_user_defined_function(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, user_defined_function_name=USER_DEFINED_FUNCTION_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/get/CosmosDBSqlUserDefinedFunctionList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.list_sql_user_defined_functions(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlUserDefinedFunctionDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_user_defined_function(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME, user_defined_function_name=USER_DEFINED_FUNCTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlContainerDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_container(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME, container_name=CONTAINER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SqlResources/delete/CosmosDBSqlDatabaseDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sql_resources.begin_delete_sql_database(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()
