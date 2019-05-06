# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time

from azure.keyvault.keys import KeyClient
from azure.core.exceptions import ClientRequestError
from devtools_testutils import ResourceGroupPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase


def create_vault_client():
    client_id = ''
    client_secret = ''
    tenant_id = ''
    vault_url = ''

    # [START create_vault_client
    from azure.keyvault.vault_client import VaultClient
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=client_id,
        secret=client_secret,
        tenant=tenant_id,
        resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # [END create_vault_client]
    return vault_client


def create_key_client():
    client_id = ''
    client_secret = ''
    tenant_id = ''
    vault_url = ''

    # [START create_secret_client
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.keyvault.secrets._client import SecretClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id,
        secret=client_secret,
        tenant=tenant_id,
        resource='https://vault.azure.net'
    )

    # Create a new key client using Azure credentials
    key_client = Key_Client(vault_url=vault_url, credentials=credentials)
    # [END create_key_client]
    return key_client


class TestExamplesKeyVault(KeyvaultTestCase):

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_example_key_crud_operations(self, vault_client, **kwargs):
        key_client = vault_client.keys
        try:
            # [START create_key]
            from dateutil import parser as date_parse
            key_size = 2048
            key_ops = [
                "encrypt",
                "decrypt",
                "sign",
                "verify",
                "wrapKey",
                "unwrapKey"
            ]
            expires = date_parse.parse('2050-02-02T08:00:00.000Z')

            # create a key with optional arguments
            key = key_client.create_key('key-name', 'RSA', size=key_size, key_ops=key_ops, enabled=True, expires=expires)

            print(key.id)
            print(key.version)
            print(key.key_material)
            print(key.enabled)
            print(key.expires)

            # [END create_key]
        except ClientRequestError:
            pass

        try:
            # [START get_key]
            key_version = key.version

            # get key with version
            key = key_client.get_key('key-name', key_version)

            # if the version argument is the empty string or None, the latest
            # version of the key will be returned
            key = key_client.get_key('key-name', '')

            print(key.id)
            print(key.name)
            print(key.version)
            print(key.key_material)
            print(key.vault_url)
            # [END get_key]
        except ClientRequestError:
            pass

        try:
            from dateutil import parser as date_parse
            # [START update_key]

            # update attributes of an existing key
            expires = date_parse.parse('2050-01-02T08:00:00.000Z')
            tags = {'foo': 'updated tag'}
            key_version = key.version
            updated_key = key_client.update_key(
                'key-name', key_version, expires=expires, tags=tags
            )

            print(updated_key.version)
            print(updated_key.updated)
            print(updated_key.expires)
            print(updated_key.tags)
            print(key.key_material)

            # [END update_key]
        except ClientRequestError:
            pass

        try:
            # [START delete_key]

            # delete a key
            deleted_key = key_client.delete_key('key-name')

            print(deleted_key.name)
            print(deleted_key.deleted_date)
            print(deleted_key.recovery_id)
            print(deleted_key.scheduled_purge_date)

            # [END delete_key]
        except ClientRequestError:
            pass

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_example_key_list_operations(self, vault_client, **kwargs):
        key_client = vault_client.keys
        try:
            # [START list_keys]

            # list keys
            keys = key_client.list_keys()

            for key in keys:
                print(key.id)
                print(key.name)
                print(key.key_material)

            # [END list_keys]
        except ClientRequestError:
            pass

        try:
            # [START list_key_versions]
            # gets a list of all versions of a key
            key_versions = key_client.list_key_versions('key-name')

            for key in key_versions:
                print(key.id)
                print(key.version)
                print(key.key_material)

            # [END list_key_versions]
        except ClientRequestError:
            pass

        try:
            # [START list_deleted_keys]

            # get a list of deleted keys (requires soft-delete enabled for the vault)
            deleted_keys = key_client.list_deleted_keys()

            for key in deleted_keys:
                # the list doesn't include key_material
                print(key.id)
                print(key.name)

            # [END list_deleted_keys]
        except ClientRequestError:
            pass

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_example_keys_backup_restore(self, vault_client, **kwargs):
        key_client = vault_client.keys
        created_key = key_client.create_key('keyrec', 'RSA')
        key_name = created_key.name
        try:
            # [START backup_key]
            # backup key
            key_backup = key_client.backup_key(key_name)

            # returns the raw bytes of the backed up key
            print(key_backup)

            # [END backup_key]
        except ClientRequestError:
            pass

        try:
            deleted_key = key_client.delete_key(key_name)
            if self.is_live:
                # wait a second to ensure the key has been deleted
                time.sleep(20)

            # [START get_deleted_key]
            # gets a deleted key (requires soft-delete enabled for the vault)
            deleted_key = key_client.get_deleted_key('keyrec')
            print(deleted_key.name)

            # [END get_deleted_key]
        except ClientRequestError:
            pass

        try:
            key_client.purge_deleted_key('keyrec')
            if self.is_live:
                # wait a second to ensure the key has been deleted
                time.sleep(20)
            # [START restore_key]

            # restores a backed up key
            restored_key = key_client.restore_key(key_backup)
            print(restored_key.id)
            print(restored_key.version)

            # [END restore_key]
        except ClientRequestError:
            pass

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_example_keys_recover_purge(self, vault_client, **kwargs):
        key_client = vault_client.keys
        created_key = key_client.create_key('key-name', 'RSA')
        if self.is_live:
            # wait a second to ensure the key has been deleted
            time.sleep(20)
        key_client.delete_key(created_key.name)
        if self.is_live:
            # wait a second to ensure the key has been deleted
            time.sleep(30)

        try:
            # [START recover_deleted_key]

            # recover deleted key to its latest version
            recover_deleted_key = key_client.recover_deleted_key('key-name')
            print(recover_deleted_key.id)
            print(recover_deleted_key.name)

            # [END recover_deleted_key]
        except ClientRequestError:
            pass

        try:
            if self.is_live:
                # wait a second to ensure the key has been recovered
                time.sleep(20)
            key_client.delete_key('key-name')
            if self.is_live:
                # wait a second to ensure the key has been deleted
                time.sleep(20)
            # [START purge_deleted_key]

            # if the vault has soft-delete enabled, purge permanently deletes the key
            # (without soft-delete, an ordinary delete is permanent)
            # key must be deleted prior to be purged
            key_client.purge_deleted_key('key-name')

            # [END purge_deleted_key]
        except ClientRequestError:
            pass
