# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   PrivateLinkResources: 2/2
#   PrivateEndpointConnections: 4/4

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
        if self.is_live:
            import azure.mgmt.network as az_network
            self.network_client = self.create_mgmt_client(
                az_network.NetworkManagementClient
            )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):

        azure_operation_poller = self.network_client.virtual_networks.begin_create_or_update(
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

        async_subnet_creation = self.network_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name,
            {
              'address_prefix': '10.0.0.0/24',
              'delegations': [],
              'private_endpoint_network_policies': 'Disabled',
              'private_link_service_network_policies': 'Disabled'
            }
        )
        subnet_info = async_subnet_creation.result()

        return subnet_info

    def create_private_endpoint(self, subscription_id, group_name, network_name, subnet_name, database_account_name, private_endpoint_name, endpoint_name):

        BODY = {
          "location": AZURE_LOCATION,
          "private_link_service_connections": [
            {
              "name": endpoint_name,
              "private_link_service_id": "/subscriptions/" + subscription_id + "/resourceGroups/" + group_name + "/providers/Microsoft.DocumentDB/databaseAccounts/" + database_account_name,
              "group_ids": [
                "Sql"
              ],
            }
          ],
          "subnet": {
            "id": "/subscriptions/" + subscription_id + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/virtualNetworks/" + network_name + "/subnets/" + subnet_name 
          }
        }
        result = self.network_client.private_endpoints.begin_create_or_update(resource_group_name=group_name, private_endpoint_name=private_endpoint_name, parameters=BODY)
        result = result.result()

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_endpoint(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        ACCOUNT_NAME = "myaccountxxyyzzz"
        DATABASE_NAME = "myDatabase"
        NETWORK_NAME = "myNetwork"
        SUBNET_NAME = "mysubnet"
        ENDPOINT_NAME = "myEndpoint"
        PRIVATE_ENDPOINT_CONNECTION_NAME = PRIVATE_ENDPOINT_NAME = "myPrivateEndpoint"
        GROUP_NAME = "Sql"

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

        if self.is_live:
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, NETWORK_NAME, SUBNET_NAME)
            self.create_private_endpoint(SUBSCRIPTION_ID, RESOURCE_GROUP, NETWORK_NAME, SUBNET_NAME, ACCOUNT_NAME, PRIVATE_ENDPOINT_NAME, ENDPOINT_NAME)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/put/Approve or reject a private endpoint connection with a given name.[put]
#--------------------------------------------------------------------------
        BODY = {
          "private_endpoint": {
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/privateEndpoints/" + PRIVATE_ENDPOINT_CONNECTION_NAME 
          },
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "You are approved!"
          },
          "group_id": "Sql",
          "provisioning_state": "Succeeded"
        }
        result = self.mgmt_client.private_endpoint_connections.begin_create_or_update(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.get(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.list_by_database_account(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /PrivateLinkResources/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_link_resources.get(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, group_name=GROUP_NAME)

#--------------------------------------------------------------------------
        # /PrivateLinkResources/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_link_resources.list_by_database_account(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/delete/Deletes a private endpoint connection with a given name.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAccounts/delete/CosmosDBDatabaseAccountDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_accounts.begin_delete(resource_group_name=RESOURCE_GROUP, account_name=ACCOUNT_NAME)
        result = result.result()
