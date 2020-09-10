# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   ServerKeys: 0/4
#   ServerAzureADOnlyAuthentications: 0/4

import unittest

import azure.mgmt.sql
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSqlTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )

        if self.is_live:
            from azure.mgmt.keyvault import KeyVaultManagementClient
            self.keyvault_client = self.create_mgmt_client(
                KeyVaultManagementClient
            )

    def create_key(self, group_name, location, key_vault, tenant_id, object_id):
        if self.is_live:
            result = self.keyvault_client.vaults.begin_create_or_update(
                group_name,
                key_vault,
                {
                  'location': location,
                  'properties': {
                    'sku': {
                      'name': 'standard'
                    },
                    'tenant_id': tenant_id,
                    "access_policies": [
                      {
                        "tenant_id": tenant_id,
                        "object_id": object_id,
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
                          ]
                        }
                      }
                    ],
                    'enabled_for_disk_encryption': True,
                  }
                }
            ).result()
            vault_url = result.properties.vault_uri
            vault_id = result.id

            from azure.keyvault.keys import KeyClient
            credentials = self.settings.get_azure_core_credentials()
            key_client = KeyClient(vault_url, credentials)

            # [START create_key]
            from dateutil import parser as date_parse
            expires_on = date_parse.parse("2050-02-02T08:00:00.000Z")

            key = key_client.create_key(
              "testkey",
              "RSA",
              size=2048,
              expires_on=expires_on
            )
            return (vault_id, key.id)
        else:
            return ('000', '000')

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_key(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        CLIENT_OID = self.settings.CLIENT_OID if self.is_live else "000"
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpcz"
        KEY_VAULT_NAME = "mykeyvaultaxcydzc"
        KEY_NAME = "mykeyzz"

        VAULT_ID, KEY_URI = self.create_key(RESOURCE_GROUP, AZURE_LOCATION, KEY_VAULT_NAME, TENANT_ID, CLIENT_OID)

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerKeys/put/Creates or updates a server key[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "AzureKeyVault",
        #   "uri": "https://someVault.vault.azure.net/keys/someKey/01234567890123456789012345678901"
          "uri": KEY_URI
        }
        result = self.mgmt_client.server_keys.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, key_name=KEY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerKeys/get/Get the server key[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_keys.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, key_name=KEY_NAME)

#--------------------------------------------------------------------------
        # /ServerKeys/get/List the server keys by server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_keys.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerKeys/delete/Delete the server key[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_keys.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, key_name=KEY_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_azure_adonly_authentication(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        AUTHENTICATION_NAME = "myauthentication"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerAzureADOnlyAuthentications/put/Creates or updates Azure Active Directory only authentication object.[put]
#--------------------------------------------------------------------------
        BODY = {
          "azure_ad_only_authentication": False
        }
        result = self.mgmt_client.server_azure_ad_only_authentications.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, authentication_name=AUTHENTICATION_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerAzureADOnlyAuthentications/get/Gets a Azure Active Directory only authentication property.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_ad_only_authentications.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, authentication_name=AUTHENTICATION_NAME)

#--------------------------------------------------------------------------
        # /ServerAzureADOnlyAuthentications/get/Gets a list of Azure Active Directory only authentication object.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_ad_only_authentications.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerAzureADOnlyAuthentications/delete/Deletes Azure Active Directory only authentication object.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_ad_only_authentications.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, authentication_name=AUTHENTICATION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()
