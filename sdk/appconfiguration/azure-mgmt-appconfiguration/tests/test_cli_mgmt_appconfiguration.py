# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 17
# Methods Covered : 17
# Examples Total  : 19
# Examples Tested : 19
# Coverage %      : 100
# ----------------------

# covered ops:
#   configuration_stores: 9/9
#   operations: 2/2
#   private_endpoint_connections: 4/4
#   private_link_resources: 2/2

import time
import unittest

import azure.mgmt.appconfiguration
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'
KEY_UUID = "test_key_a6af8952-54a6-11e9-b600-2816a84d0309"
LABEL_UUID = "1d7b2b28-549e-11e9-b51c-2816a84d0309"
KEY = "PYTHON_UNIT_" + KEY_UUID
LABEL = "test_label1_" + LABEL_UUID
TEST_CONTENT_TYPE = "test content type"
TEST_VALUE = "test value"

class MgmtAppConfigurationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAppConfigurationTest, self).setUp()
        from azure.mgmt.appconfiguration import AppConfigurationManagementClient
        self.mgmt_client = self.create_mgmt_client(
            AppConfigurationManagementClient
        )

        if self.is_live:
            import azure.mgmt.network
            self.network_client = self.create_mgmt_client(
              azure.mgmt.network.NetworkManagementClient
            )

    def create_kv(self, connection_str):
        from azure.appconfiguration import (
            AzureAppConfigurationClient,
            ConfigurationSetting
        )
        app_config_client = AzureAppConfigurationClient.from_connection_string(connection_str)
        kv = ConfigurationSetting(
            key=KEY,
            label=LABEL,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"}
        )
        created_kv = app_config_client.add_configuration_setting(kv)
        return created_kv
        

    # TODO: update to track 2 version later
    def create_endpoint(self, group_name, vnet_name, sub_net, endpoint_name, conf_store_id):
        # Create VNet
        async_vnet_creation = self.network_client.virtual_networks.create_or_update(
            group_name,
            vnet_name,
            {
                'location': AZURE_LOCATION,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            }
        )
        async_vnet_creation.wait()

        # Create Subnet
        async_subnet_creation = self.network_client.subnets.create_or_update(
            group_name,
            vnet_name,
            sub_net,
            {
              'address_prefix': '10.0.0.0/24',
               'private_link_service_network_policies': 'disabled',
               'private_endpoint_network_policies': 'disabled'
            }
        )
        subnet_info = async_subnet_creation.result()

        # Create private endpoint
        BODY = {
          "location": "eastus",
          "properties": {
            "privateLinkServiceConnections": [
              # {
              #   "name": PRIVATE_LINK_SERVICES,  # TODO: This is needed, but was not showed in swagger.
              #   "private_link_service_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/privateLinkServices/" + PRIVATE_LINK_SERVICES,
              # },
              {
                "name": "myconnection",
                # "private_link_service_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + group_name + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + ""
                "private_link_service_id": conf_store_id,
                "group_ids": ["configurationStores"]
              }
            ],
            "subnet": {
              "id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + sub_net
            }
          }
        }
        result = self.network_client.private_endpoints.create_or_update(group_name, endpoint_name, BODY)

        return result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_appconfiguration_list_key_values(self, resource_group):
        CONFIGURATION_STORE_NAME = self.get_resource_name("configuration")

        # ConfigurationStores_Create[put]
        BODY = {
          "location": "westus",
          "sku": {
            "name": "Standard"  # Free can not use private endpoint
          },
          "tags": {
            "my_tag": "myTagValue"
          }
        }
        result = self.mgmt_client.configuration_stores.begin_create(resource_group.name, CONFIGURATION_STORE_NAME, BODY)
        conf_store = result.result()

        # ConfigurationStores_ListKeys[post]
        keys = list(self.mgmt_client.configuration_stores.list_keys(resource_group.name, CONFIGURATION_STORE_NAME))

        # ConfigurationStores_RegenerateKey[post]
        BODY = {
          "id": keys[0].id
        }
        key = self.mgmt_client.configuration_stores.regenerate_key(resource_group.name, CONFIGURATION_STORE_NAME, BODY)

        if self.is_live:
            # create key-value
            self.create_kv(key.connection_string)

        # ConfigurationStores_ListKeyValue[post]
        BODY = {
          "key": KEY,
          "label": LABEL
        }
        result = self.mgmt_client.configuration_stores.list_key_value(resource_group.name, CONFIGURATION_STORE_NAME, BODY)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_appconfiguration(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        VNET_NAME = "vnetname"
        SUB_NET = "subnetname"
        ENDPOINT_NAME = "endpointxyz"
        CONFIGURATION_STORE_NAME = self.get_resource_name("configuration")
        PRIVATE_ENDPOINT_CONNECTION_NAME = self.get_resource_name("privateendpoint")

        # ConfigurationStores_Create[put]
        BODY = {
          "location": "westus",
          "sku": {
            "name": "Standard"  # Free can not use private endpoint
          },
          "tags": {
            "my_tag": "myTagValue"
          }
        }
        result = self.mgmt_client.configuration_stores.begin_create(resource_group.name, CONFIGURATION_STORE_NAME, BODY)
        conf_store = result.result()

        if self.is_live:
            # create endpoint
            endpoint = self.create_endpoint(resource_group.name, VNET_NAME, SUB_NET, ENDPOINT_NAME, conf_store.id)

        # ConfigurationStores_Create_WithIdentity[put]
        # BODY = {
        #   "location": "westus",
        #   "sku": {
        #     "name": "Free"
        #   },
        #   "tags": {
        #     "my_tag": "myTagValue"
        #   },
        #   "identity": {
        #     "type": "SystemAssigned, UserAssigned",
        #     "user_assigned_identities": {}
        #   }
        # }
        # result = self.mgmt_client.configuration_stores.begin_create(resource_group.name, CONFIGURATION_STORE_NAME, BODY)
        # result = result.result()

        # ConfigurationStores_Get[get]
        conf_store = self.mgmt_client.configuration_stores.get(resource_group.name, CONFIGURATION_STORE_NAME)

        PRIVATE_ENDPOINT_CONNECTION_NAME = conf_store.private_endpoint_connections[0].name
        private_connection_id = conf_store.private_endpoint_connections[0].id

        # PrivateEndpointConnection_CreateOrUpdate[put]
        BODY = {
          # "id": "https://management.azure.com/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.AppConfiguration/configurationStores/" + CONFIGURATION_STORE_NAME + "/privateEndpointConnections/" + PRIVATE_ENDPOINT_CONNECTION_NAME,
          "id": private_connection_id,
          "private_endpoint": {
            "id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.Network/privateEndpoints/" + ENDPOINT_NAME,
          },
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "Auto-Approved"
          }
        }
        result = self.mgmt_client.private_endpoint_connections.begin_create_or_update(
            resource_group.name,
            CONFIGURATION_STORE_NAME,
            PRIVATE_ENDPOINT_CONNECTION_NAME,
            BODY)
            # id=BODY["id"],
            # private_endpoint=BODY["private_endpoint"],
            # private_link_service_connection_state=BODY["private_link_service_connection_state"])
        result = result.result()
          
        # PrivateEndpointConnection_GetConnection[get]
        result = self.mgmt_client.private_endpoint_connections.get(resource_group.name, CONFIGURATION_STORE_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)

        # PrivateLinkResources_ListGroupIds[get]
        privatelinks = list(self.mgmt_client.private_link_resources.list_by_configuration_store(resource_group.name, CONFIGURATION_STORE_NAME))
        PRIVATE_LINK_RESOURCE_NAME = privatelinks[0].name

        # PrivateLinkResources_Get[get]
        result = self.mgmt_client.private_link_resources.get(resource_group.name, CONFIGURATION_STORE_NAME, PRIVATE_LINK_RESOURCE_NAME)

        # PrivateEndpointConnection_List[get]
        result = list(self.mgmt_client.private_endpoint_connections.list_by_configuration_store(resource_group.name, CONFIGURATION_STORE_NAME))

        # List the operations available
        result = self.mgmt_client.operations.list()

        # ConfigurationStores_ListByResourceGroup[get]
        result = self.mgmt_client.configuration_stores.list_by_resource_group(resource_group.name)

        # ConfigurationStores_List[get]
        result = self.mgmt_client.configuration_stores.list()

        # ConfigurationStores_Update[patch]
        BODY = {
          "tags": {
            "category": "Marketing"
          },
          "sku": {
            "name": "Standard"
          }
        }
        result = self.mgmt_client.configuration_stores.begin_update(resource_group.name, CONFIGURATION_STORE_NAME, BODY)
        result = result.result()

        # ConfigurationStores_Update_WithIdentity[patch]
        # BODY = {
        #   "tags": {
        #     "category": "Marketing"
        #   },
        #   "sku": {
        #     "name": "Standard"
        #   },
        #   "identity": {
        #     "type": "SystemAssigned, UserAssigned",
        #     "user_assigned_identities": {}
        #   }
        # }
        # result = self.mgmt_client.configuration_stores.begin_update(resource_group.name, CONFIGURATION_STORE_NAME, BODY)
        # result = result.result()

        # ConfigurationStores_CheckNameNotAvailable[post]
        BODY = {
          "name": "contoso",
          "type": "Microsoft.AppConfiguration/configurationStores"
        }
        result = self.mgmt_client.operations.check_name_availability(BODY)

        # ConfigurationStores_CheckNameAvailable[post]
        BODY = {
          "name": "contoso",
          "type": "Microsoft.AppConfiguration/configurationStores"
        }
        result = self.mgmt_client.operations.check_name_availability(BODY)

        # PrivateEndpointConnections_Delete[delete]
        result = self.mgmt_client.private_endpoint_connections.begin_delete(resource_group.name, CONFIGURATION_STORE_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)
        result = result.result()

        # ConfigurationStores_Delete[delete]
        result = self.mgmt_client.configuration_stores.begin_delete(resource_group.name, CONFIGURATION_STORE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
