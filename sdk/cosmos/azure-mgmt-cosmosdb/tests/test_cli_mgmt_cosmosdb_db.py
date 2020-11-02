# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   DatabaseAccounts: 16/18
#   Operations: 1/1

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
    def test_dbaccount(self, resource_group):
        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"

#--------------------------------------------------------------------------
        # /Operations/get/CosmosDBOperationsList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.operations.list()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/put/CosmosDBDatabaseAccountCreateMin[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "database_account_offer_type": "Standard",
          "locations": [
            {
              "failover_priority": "2",
              "location_name": "southcentralus",
              "is_zone_redundant": False
            },
            {
              "location_name": "eastus",
              "failover_priority": "1"
            },
            {
              "location_name": "westus",
              "failover_priority": "0"
            }
          ]
        }
        result = self.mgmt_client.database_accounts.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, create_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/get/CosmosDBDatabaseAccountGetMetricDefinitions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_metric_definitions(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

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
            },
            {
              "failover_priority": "2",
              "location_name": "southcentralus"
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
        # /DatabaseAccountRegion/get/CosmosDBDatabaseAccountRegionGetMetrics[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.database_account_region.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region=REGION, filter="$filter=(name.value eq 'Total Requests') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /CollectionRegion/get/CosmosDBRegionCollectionGetMetrics[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.collection_region.list_metrics(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region=REGION, database_rid=DATABASE_RID, collection_rid=COLLECTION_RID, filter="$filter=(name.value eq 'Total Requests') and timeGrain eq duration'PT5M' and startTime eq '2017-11-19T23:53:55.2780000Z' and endTime eq '2017-11-20T00:13:55.2780000Z")

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountOfflineRegion[post]
#--------------------------------------------------------------------------
        BODY = {
            "region": "eastus"
        }
        # result = self.mgmt_client.database_accounts.begin_offline_region(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region_parameter_for_offline=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountOnlineRegion[post]
#--------------------------------------------------------------------------
        BODY = {
            "region": "eastus"
        }
        # result = self.mgmt_client.database_accounts.begin_online_region(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, region_parameter_for_online=BODY)
        # result = result.result()

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
        # /DatabaseAccounts/post/CosmosDBDatabaseAccountListKeys[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.list_keys(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/patch/CosmosDBDatabaseAccountPatch[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "dept": "finance"
          }
        }
        result = self.mgmt_client.database_accounts.begin_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/head/CosmosDBDatabaseAccountCheckNameExists[head]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.check_name_exists(account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()

