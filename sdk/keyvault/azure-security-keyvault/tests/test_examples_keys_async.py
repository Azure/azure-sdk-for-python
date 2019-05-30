# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import functools

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError, HttpResponseError
from devtools_testutils import ResourceGroupPreparer
from preparer import VaultClientPreparer
from test_case import KeyVaultTestCase
from azure.security.keyvault.aio import VaultClient


def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
       upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        # TODO: this is a workaround for VaultClientPreparer creating a sync client; let's obviate it
        vault_client = kwargs.get("vault_client")
        credentials = test_class_instance.settings.get_credentials(resource="https://vault.azure.net")
        aio_client = VaultClient(vault_client.vault_url, credentials)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, vault_client=aio_client))

    return run


def create_vault_client():
    client_id = ""
    client_secret = ""
    tenant_id = ""
    vault_url = ""

    # [START create_vault_client]
    from azure.security.keyvault.aio import VaultClient
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # [END create_vault_client]
    return vault_client


def create_key_client():
    client_id = ""
    client_secret = ""
    tenant_id = ""
    vault_url = ""

    # [START create_key_client]
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.security.keyvault.aio import KeyClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new key client using Azure credentials
    key_client = KeyClient(vault_url=vault_url, credentials=credentials)
    # [END create_key_client]
    return key_client


class TestExamplesKeyVault(KeyVaultTestCase):
    @ResourceGroupPreparer()
    @VaultClientPreparer()
    @await_prepared_test
    async def test_example_key_crud_operations(self, vault_client, **kwargs):
        from dateutil import parser as date_parse

        key_client = vault_client.keys
        try:
            # [START create_key]
            from dateutil import parser as date_parse

            key_size = 2048
            key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
            expires = date_parse.parse("2050-02-02T08:00:00.000Z")

            # create a key with optional arguments
            key = await key_client.create_key(
                "key-name", "RSA", size=key_size, key_ops=key_ops, enabled=True, expires=expires
            )

            print(key.id)
            print(key.version)
            print(key.key_material.kty)
            print(key.enabled)
            print(key.expires)

            # [END create_key]
            # [START create_rsa_key]

            key_size = 2048
            key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]

            # create an rsa key with size specification
            # RSA key can be created with default size of '2048'
            key = await key_client.create_rsa_key("key-name", hsm=True, size=key_size, enabled=True, key_ops=key_ops)

            print(key.id)
            print(key.version)
            print(key.key_material.kty)
            print(key.key_material.key_ops)

            # [END create_rsa_key]

            # [START create_ec_key]
            from dateutil import parser as date_parse

            key_curve = "P-256"

            # create an ec (Elliptic curve) key with curve specification
            # EC key can be created with default curve of 'P-256'
            ec_key = await key_client.create_ec_key("key-name", hsm=False, curve=key_curve)

            print(ec_key.id)
            print(ec_key.version)
            print(ec_key.key_material.kty)
            print(ec_key.key_material.crv)

            # [END create_ec_key]
        except HttpResponseError:
            pass

        try:
            # [START get_key]

            # if no version is specified the latest
            # version of the key will be returned
            key = await key_client.get_key("key-name")

            # get key with version
            key_version = key.version
            key = await key_client.get_key("key-name", key_version)

            print(key.id)
            print(key.name)
            print(key.version)
            print(key.key_material.kty)
            print(key.vault_url)
            # [END get_key]
            # [START update_key]

            # update attributes of an existing key
            expires = date_parse.parse("2050-01-02T08:00:00.000Z")
            tags = {"foo": "updated tag"}
            key_version = key.version
            updated_key = await key_client.update_key(key.name, key_version, expires=expires, tags=tags)

            print(updated_key.version)
            print(updated_key.updated)
            print(updated_key.expires)
            print(updated_key.tags)
            print(key.key_material.kty)

            # [END update_key]
        except ResourceNotFoundError:
            pass

        try:
            # [START delete_key]

            # delete a key
            deleted_key = await key_client.delete_key("key-name")

            print(deleted_key.name)
            # when vault has soft-delete enabled, deleted_key exposes the purge date, recover id
            # and deleted date of the key
            print(deleted_key.deleted_date)
            print(deleted_key.recovery_id)
            print(deleted_key.scheduled_purge_date)

            # [END delete_key]
        except ResourceNotFoundError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_example_key_list_operations(self, vault_client, **kwargs):
        key_client = vault_client.keys
        try:
            # [START list_keys]

            # list keys
            keys = key_client.list_keys()

            async for key in keys:
                print(key.id)
                print(key.name)
                print(key.key_material.kty)

            # [END list_keys]
        except HttpResponseError:
            pass

        try:
            # [START list_key_versions]
            # get an iterator of all versions of a key
            key_versions = key_client.list_key_versions("key-name")

            async for key in key_versions:
                print(key.id)
                print(key.version)
                print(key.key_material.kty)

            # [END list_key_versions]
        except HttpResponseError:
            pass

        try:
            # [START list_deleted_keys]

            # get an iterator of DeletedKey (requires soft-delete enabled for the vault)
            deleted_keys = key_client.list_deleted_keys()

            async for key in deleted_keys:
                print(key.id)
                print(key.name)

            # [END list_deleted_keys]
        except HttpResponseError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    @await_prepared_test
    async def test_example_keys_backup_restore(self, vault_client, **kwargs):
        key_client = vault_client.keys
        created_key = await key_client.create_key("keyrec", "RSA")
        key_name = created_key.name
        try:
            # [START backup_key]
            # backup key
            key_backup = await key_client.backup_key(key_name)

            # returns the raw bytes of the backed up key
            print(key_backup)

            # [END backup_key]

            await key_client.delete_key("keyrec")
            if self.is_live:
                # wait a second to ensure the key has been deleted
                await asyncio.sleep(20)
            # [START restore_key]

            # restores a backed up key
            restored_key = await key_client.restore_key(key_backup)
            print(restored_key.id)
            print(restored_key.version)

            # [END restore_key]
        except ResourceExistsError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_example_keys_recover_purge(self, vault_client, **kwargs):
        key_client = vault_client.keys
        created_key = await key_client.create_key("key-name", "RSA")
        if self.is_live:
            # wait a second to ensure the key has been created
            await asyncio.sleep(20)
        await key_client.delete_key(created_key.name)
        if self.is_live:
            # wait a second to ensure the key has been deleted
            await asyncio.sleep(30)

        try:
            # [START get_deleted_key]
            # gets a deleted key (requires soft-delete enabled for the vault)
            deleted_key = await key_client.get_deleted_key("key-name")
            print(deleted_key.name)

            # [END get_deleted_key]
        except ResourceNotFoundError:
            pass

        try:
            # [START recover_deleted_key]

            # recover deleted key to its latest version
            recover_deleted_key = await key_client.recover_deleted_key("key-name")
            print(recover_deleted_key.id)
            print(recover_deleted_key.name)

            # [END recover_deleted_key]
        except HttpResponseError:
            pass

        try:
            if self.is_live:
                # wait a second to ensure the key has been recovered
                await asyncio.sleep(20)
            await key_client.delete_key("key-name")
            if self.is_live:
                # wait a second to ensure the key has been deleted
                await asyncio.sleep(20)
            # [START purge_deleted_key]

            # if the vault has soft-delete enabled, purge permanently deletes the key
            # (without soft-delete, an ordinary delete is permanent)
            # key must be deleted prior to be purged
            await key_client.purge_deleted_key("key-name")

            # [END purge_deleted_key]
        except HttpResponseError:
            pass
