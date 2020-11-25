# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   ServerKeys: 4/4
#   ServerAzureADOnlyAuthentications: 0/4
#   EncryptionProtectors: 4/4
#   ManagedInstanceKeys: 4/4
#   ManagedInstanceEncryptionProtectors: 3/4

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

    def create_key(self, group_name, location, key_vault, tenant_id, object_id, object_id_2):
        if self.is_live:
            result = self.keyvault_client.vaults.begin_create_or_update(
                group_name,
                key_vault,
                {
                  'location': location,
                  'properties': {
                    'sku': {
                      'family': 'A',
                      'name': 'standard'
                    },
                    'tenant_id': tenant_id,
                    "access_policies": [
                      {
                        "tenant_id": tenant_id,
                        "object_id": object_id,
                        "permissions": {
                          "keys": [
                            "get",
                            "create",
                            "delete",
                            "list",
                            "update",
                            "import",
                            "backup",
                            "restore",
                            "recover"
                          ],
                          "secrets": [
                            "get",
                            "list",
                            "set",
                            "delete",
                            "backup",
                            "restore",
                            "recover"
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
                            "recover"
                          ],
                          "storage": [
                            "get",
                            "list",
                            "delete",
                            "set",
                            "update",
                            "regeneratekey",
                            "setsas",
                            "listsas",
                            "getsas",
                            "deletesas"
                          ]
                        }
                      },
                      {
                        "tenantId": tenant_id,
                        "objectId": object_id_2,
                        "permissions": {
                          "keys": [
                            "unwrapKey",
                            "get",
                            "wrapKey",
                            "list"
                          ]
                        }
                      }
                    ],
                    'enabled_for_disk_encryption': True,
                    'enable_soft_delete': True,
                    'soft_delete_retention_in_days': 90,
                    'nework_acls': {
                      'bypass': 'AzureServices',
                      'default_action': "Allow",
                      'ip_rules': [],
                      'virtual_network_rules': []
                    }
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

    def test_managed_instance_encryption_protector(self):

        RESOURCE_GROUP = "testManagedInstance"
        MANAGED_INSTANCE_NAME = "testinstancexxy"
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        CLIENT_OID = self.settings.CLIENT_OID if self.is_live else "000"
        KEY_VAULT_NAME = self.get_resource_name("keyvaultxmmxh")
        ENCRYPTION_PROTECTOR_NAME = "current"

#--------------------------------------------------------------------------
        # /ManagedInstances/get/Get managed instance[get]
#--------------------------------------------------------------------------
        instance = self.mgmt_client.managed_instances.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)
        oid2 = instance.identity.principal_id

        VAULT_ID, KEY_URI = self.create_key(RESOURCE_GROUP, AZURE_LOCATION, KEY_VAULT_NAME, TENANT_ID, CLIENT_OID, oid2)

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/put/Creates or updates a managed instance key[put]
#--------------------------------------------------------------------------
        KEY_NAME = KEY_VAULT_NAME + "_testkey_" + KEY_URI.split("/")[-1]
        BODY = {
          "server_key_type": "AzureKeyVault",
          "uri": KEY_URI
        }
        result = self.mgmt_client.managed_instance_keys.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, key_name=KEY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/put/Update the encryption protector to key vault[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "AzureKeyVault",
          "server_key_name": KEY_NAME
        }
        result = self.mgmt_client.managed_instance_encryption_protectors.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/get/Get the encryption protector[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_encryption_protectors.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/get/List encryption protectors by managed instance[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_encryption_protectors.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/post/Revalidates the encryption protector[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_instance_encryption_protectors.begin_revalidate(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/delete/Delete the managed instance key[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_instance_keys.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, key_name=KEY_NAME)
        # result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_encryption_protector(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        CLIENT_OID = self.settings.CLIENT_OID if self.is_live else "000"
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpczk"
        KEY_VAULT_NAME = self.get_resource_name("keyvaultxmmxkk")
        ENCRYPTION_PROTECTOR_NAME = "current"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "identity": {
            "type": "SystemAssigned"
          },
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0",
          "public_network_access":"Enabled"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        server = result.result()
        oid2 = server.identity.principal_id

        VAULT_ID, KEY_URI = self.create_key(RESOURCE_GROUP, AZURE_LOCATION, KEY_VAULT_NAME, TENANT_ID, CLIENT_OID, oid2)

#--------------------------------------------------------------------------
        # /ServerKeys/put/Creates or updates a server key[put]
#--------------------------------------------------------------------------
        KEY_NAME = KEY_VAULT_NAME + "_testkey_" + KEY_URI.split("/")[-1]
        BODY = {
          "server_key_type": "AzureKeyVault",
          "uri": KEY_URI
        }
        result = self.mgmt_client.server_keys.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, key_name=KEY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /EncryptionProtectors/put/Update the encryption protector to service managed[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "AzureKeyVault",
          "server_key_name": KEY_NAME
        }
        result = self.mgmt_client.encryption_protectors.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /EncryptionProtectors/get/Get the encryption protector[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.encryption_protectors.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME)

#--------------------------------------------------------------------------
        # /EncryptionProtectors/get/List encryption protectors by server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.encryption_protectors.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /EncryptionProtectors/post/Revalidates the encryption protector[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.encryption_protectors.begin_revalidate(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    def test_instance_key(self):
        
        RESOURCE_GROUP = "testManagedInstance"
        MANAGED_INSTANCE_NAME = "testinstancexxy"
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        CLIENT_OID = self.settings.CLIENT_OID if self.is_live else "000"
        KEY_VAULT_NAME = self.get_resource_name("keyvaultxmmxh")

#--------------------------------------------------------------------------
        # /ManagedInstances/get/Get managed instance[get]
#--------------------------------------------------------------------------
        instance = self.mgmt_client.managed_instances.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)
        oid2 = instance.identity.principal_id

        VAULT_ID, KEY_URI = self.create_key(RESOURCE_GROUP, AZURE_LOCATION, KEY_VAULT_NAME, TENANT_ID, CLIENT_OID, oid2)

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/put/Creates or updates a managed instance key[put]
#--------------------------------------------------------------------------
        KEY_NAME = KEY_VAULT_NAME + "_testkey_" + KEY_URI.split("/")[-1]
        BODY = {
          "server_key_type": "AzureKeyVault",
          "uri": KEY_URI
        }
        result = self.mgmt_client.managed_instance_keys.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, key_name=KEY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/get/Get the managed instance key[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_keys.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, key_name=KEY_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/get/List the keys for a managed instance.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_keys.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/delete/Delete the managed instance key[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_keys.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, key_name=KEY_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_key(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        CLIENT_OID = self.settings.CLIENT_OID if self.is_live else "000"
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpczk"
        KEY_VAULT_NAME = self.get_resource_name("keyvaultxmmxhh")
        # KEY_NAME = "mykeyzz"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "identity": {
            "type": "SystemAssigned"
          },
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0",
          "public_network_access":"Enabled"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        server = result.result()
        oid2 = server.identity.principal_id

        VAULT_ID, KEY_URI = self.create_key(RESOURCE_GROUP, AZURE_LOCATION, KEY_VAULT_NAME, TENANT_ID, CLIENT_OID, oid2)

#--------------------------------------------------------------------------
        # /ServerKeys/put/Creates or updates a server key[put]
#--------------------------------------------------------------------------
        KEY_NAME = KEY_VAULT_NAME + "_testkey_" + KEY_URI.split("/")[-1]
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
