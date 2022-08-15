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
# Examples Total  : 18
# Examples Tested : 18
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.keyvault
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtKeyVault(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.keyvault.KeyVaultManagementClient
        )
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_keyvault(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47" # self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        VAULT_NAME = "myValtZikfikxz"
        OPERATION_KIND = "add"
        LOCATION = "eastus"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "myPrivateEndpointConnection"

        # /Vaults/put/Create a new vault or update an existing vault[put]
        BODY = {
          "location": LOCATION,
          "properties": {
            "tenant_id": TENANT_ID,
            "sku": {
              "family": "A",
              "name": "standard"
            },
            "access_policies": [
              {
                "tenant_id": TENANT_ID,
                "object_id": "00000000-0000-0000-0000-000000000000",
                "permissions": {
                  "keys": [
                    "encrypt",
                    "decrypt",
                    "wrapKey",
                    "unwrapKey",
                    "sign",
                    "verify",
                    "get",
                    "list",
                    "create",
                    "update",
                    "import",
                    "delete",
                    "backup",
                    "restore",
                    "recover",
                    "purge"
                  ],
                  "secrets": [
                    "get",
                    "list",
                    "set",
                    "delete",
                    "backup",
                    "restore",
                    "recover",
                    "purge"
                  ],
                  "certificates": [
                    "get",
                    "list",
                    "delete",
                    "create",
                    "import",
                    "update",
                    "managecontacts",
                    "getissuers",
                    "listissuers",
                    "setissuers",
                    "deleteissuers",
                    "manageissuers",
                    "recover",
                    "purge"
                  ]
                }
              }
            ],
            "enabled_for_deployment": True,
            "enabled_for_disk_encryption": True,
            "enabled_for_template_deployment": True
          }
        }
        result = self.mgmt_client.vaults.begin_create_or_update(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, parameters=BODY)
        result = result.result()

        # /Vaults/put/Create or update a vault with network acls[put]
        BODY = {
          "location": LOCATION,
          "properties": {
            "tenant_id": "00000000-0000-0000-0000-000000000000",
            "sku": {
              "family": "A",
              "name": "standard"
            },
            "network_acls": {
              "default_action": "Deny",
              "bypass": "AzureServices",
              "ip_rules": [
                {
                  "value": "124.56.78.91"
                },
                {
                  "value": "'10.91.4.0/24'"
                }
              ],
              "virtual_network_rules": [
                {
                  "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworkstest-vnet/subnetssubnet1"
                }
              ]
            },
            "enabled_for_deployment": True,
            "enabled_for_disk_encryption": True,
            "enabled_for_template_deployment": True
          }
        }
        #result = self.mgmt_client.vaults.create_or_update(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, parameters=BODY)
        #result = result.result()

        # /Vaults/put/Add an access policy, or update an access policy with new permissions[put]
        PARAMETERS = {
          "properties": {
            "access_policies": [
              {
                "tenant_id": TENANT_ID,
                "object_id": "00000000-0000-0000-0000-000000000000",
                "permissions": {
                  "keys": [
                    "encrypt"
                  ],
                  "secrets": [
                    "get"
                  ],
                  "certificates": [
                    "get"
                  ]
                }
              }
            ]
          }
        }
        
        result = self.mgmt_client.vaults.update_access_policy(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, operation_kind=OPERATION_KIND, parameters=PARAMETERS)

        # /PrivateEndpointConnections/put/KeyVaultPutPrivateEndpointConnection[put]
        BODY = {
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "My name is Joe and I'm approving this."
          }
        }
        # result = self.mgmt_client.private_endpoint_connections.put(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME, properties=BODY)

        # /PrivateEndpointConnections/get/KeyVaultGetPrivateEndpointConnection[get]
        # result = self.mgmt_client.private_endpoint_connections.get(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)

        # /PrivateLinkResources/get/KeyVaultListPrivateLinkResources[get]
        # result = self.mgmt_client.private_link_resources.list_by_vault(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)

        # /Vaults/get/Retrieve a vault[get]
        result = self.mgmt_client.vaults.get(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)

        # /Vaults/get/List vaults in the specified resource group[get]
        result = self.mgmt_client.vaults.list_by_resource_group(resource_group_name=RESOURCE_GROUP, top="1")

        # /Vaults/get/List deleted vaults in the specified subscription[get]
        result = self.mgmt_client.vaults.list_deleted()

        # /Vaults/get/List vaults in the specified subscription[get]
        result = self.mgmt_client.vaults.list_by_subscription(top="1")

        # /Vaults/get/List vaults in the specified subscription[get]
        result = self.mgmt_client.vaults.list_by_subscription(top="1")

        # /Operations/get/Lists available Rest API operations.[get]
        result = self.mgmt_client.operations.list()

        # /Vaults/patch/Update an existing vault[patch]
        PROPERTIES = {
          "tenant_id": TENANT_ID,
          "sku": {
            "family": "A",
            "name": "standard"
          },
          "access_policies": [
            {
              "tenant_id": TENANT_ID,
              "object_id": "00000000-0000-0000-0000-000000000000",
              "permissions": {
                "keys": [
                  "encrypt",
                  "decrypt",
                  "wrapKey",
                  "unwrapKey",
                  "sign",
                  "verify",
                  "get",
                  "list",
                  "create",
                  "update",
                  "import",
                  "delete",
                  "backup",
                  "restore",
                  "recover",
                  "purge"
                ],
                "secrets": [
                  "get",
                  "list",
                  "set",
                  "delete",
                  "backup",
                  "restore",
                  "recover",
                  "purge"
                ],
                "certificates": [
                  "get",
                  "list",
                  "delete",
                  "create",
                  "import",
                  "update",
                  "managecontacts",
                  "getissuers",
                  "listissuers",
                  "setissuers",
                  "deleteissuers",
                  "manageissuers",
                  "recover",
                  "purge"
                ]
              }
            }
          ],
          "enabled_for_deployment": True,
          "enabled_for_disk_encryption": True,
          "enabled_for_template_deployment": True
        }
        result = self.mgmt_client.vaults.update(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, parameters=PROPERTIES)

        # /Vaults/post/Validate a vault name[post]
        result = self.mgmt_client.vaults.check_name_availability({ 'name': 'sample-vault', 'type': 'Microsoft.KeyVault/vaults' })

        # /PrivateEndpointConnections/delete/KeyVaultDeletePrivateEndpointConnection[delete]
        # result = self.mgmt_client.private_endpoint_connections.delete(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
        # result = result.result()

        # /Vaults/delete/Delete a vault[delete]
        result = self.mgmt_client.vaults.delete(resource_group_name=RESOURCE_GROUP, vault_name=VAULT_NAME)

        # /Vaults/get/Retrieve a deleted vault[get]
        result = self.mgmt_client.vaults.get_deleted(location=LOCATION, vault_name=VAULT_NAME)

        # /Vaults/post/Purge a deleted vault[post]
        result = self.mgmt_client.vaults.begin_purge_deleted(location=LOCATION, vault_name=VAULT_NAME)
        result = result.result()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
