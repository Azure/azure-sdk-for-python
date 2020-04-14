# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 17
# Methods Covered : 16
# Examples Total  : 19
# Examples Tested : 6
# Coverage %      : 30
# ----------------------

import unittest

import azure.mgmt.appconfiguration
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAppConfigurationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAppConfigurationTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.appconfiguration.AppConfigurationManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_appconfiguration(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        CONFIG_STORE_NAME = "myConfigStore"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "myPrivateEndpointConnection"
        GROUP_NAME = "myGroup"

        # /ConfigurationStores/put/ConfigurationStores_Create[put]
        BODY = {
          "location": "westus",
          "sku": {
            "name": "Standard"
          },
          "tags": {
            "my_tag": "myTagValue"
          }
        }
        result = self.mgmt_client.configuration_stores.create(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, config_store_creation_parameters=BODY)
        result = result.result()

        # /ConfigurationStores/put/ConfigurationStores_Create_WithIdentity[put]
        BODY = {
          "location": "westus",
          "sku": {
            "name": "Standard"
          },
          "tags": {
            "my_tag": "myTagValue"
          },
          "identity": {
            "type": "SystemAssigned, UserAssigned",
            "user_assigned_identities": {}
          }
        }
        # result = self.mgmt_client.configuration_stores.create(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, config_store_creation_parameters=BODY)
        # result = result.result()

        # /PrivateEndpointConnections/put/PrivateEndpointConnection_CreateOrUpdate[put]
        BODY = {
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "Auto-Approved"
          }
        }
        # result = self.mgmt_client.private_endpoint_connections.create_or_update(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME, private_endpoint_connection=BODY)
        # result = result.result()

        # /PrivateEndpointConnections/get/PrivateEndpointConnection_GetConnection[get]
        # result = self.mgmt_client.private_endpoint_connections.get(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)

        # /PrivateLinkResources/get/PrivateLinkResources_Get[get]
        # result = self.mgmt_client.private_link_resources.get(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, group_name=GROUP_NAME)

        # /PrivateEndpointConnections/get/PrivateEndpointConnection_List[get]
        # result = self.mgmt_client.private_endpoint_connections.list_by_configuration_store(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME)

        # /PrivateLinkResources/get/PrivateLinkResources_ListGroupIds[get]
        # result = self.mgmt_client.private_link_resources.list_by_configuration_store(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME)

        # /ConfigurationStores/get/ConfigurationStores_Get[get]
        result = self.mgmt_client.configuration_stores.get(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME)

        # /ConfigurationStores/get/ConfigurationStores_ListByResourceGroup[get]
        result = self.mgmt_client.configuration_stores.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /ConfigurationStores/get/ConfigurationStores_List[get]
        result = self.mgmt_client.configuration_stores.list()

        # /ConfigurationStores/post/ConfigurationStores_RegenerateKey[post]
        # result = self.mgmt_client.configuration_stores.regenerate_key(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, id="439AD01B4BE67DB1")

        # /ConfigurationStores/post/ConfigurationStores_ListKeyValue[post]
        # result = self.mgmt_client.configuration_stores.list_key_value(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, key="MaxRequests", label="dev")

        # /ConfigurationStores/post/ConfigurationStores_ListKeys[post]
        result = self.mgmt_client.configuration_stores.list_keys(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME)

        # /ConfigurationStores/patch/ConfigurationStores_Update[patch]
        BODY = {
          "tags": {
            "category": "Marketing"
          },
          "sku": {
            "name": "Standard"
          }
        }
        # result = self.mgmt_client.configuration_stores.update(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, config_store_update_parameters=BODY)
        # result = result.result()

        # /ConfigurationStores/patch/ConfigurationStores_Update_WithIdentity[patch]
        BODY = {
          "tags": {
            "category": "Marketing"
          },
          "sku": {
            "name": "Standard"
          },
          "identity": {
            "type": "SystemAssigned, UserAssigned",
            "user_assigned_identities": {}
          }
        }
        # result = self.mgmt_client.configuration_stores.update(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, config_store_update_parameters=BODY)
        # result = result.result()

        # /Operations/post/ConfigurationStores_CheckNameNotAvailable[post]
        # result = self.mgmt_client.operations.check_name_availability(name="contoso", type="Microsoft.AppConfiguration/configurationStores")

        # /Operations/post/ConfigurationStores_CheckNameAvailable[post]
        # result = self.mgmt_client.operations.check_name_availability(name="contoso", type="Microsoft.AppConfiguration/configurationStores")

        # /PrivateEndpointConnections/delete/PrivateEndpointConnections_Delete[delete]
        # result = self.mgmt_client.private_endpoint_connections.delete(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
        # result = result.result()

        # /ConfigurationStores/delete/ConfigurationStores_Delete[delete]
        result = self.mgmt_client.configuration_stores.delete(resource_group_name=RESOURCE_GROUP, config_store_name=CONFIG_STORE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
