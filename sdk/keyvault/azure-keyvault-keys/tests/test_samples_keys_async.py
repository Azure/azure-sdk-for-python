# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os

import pytest
from azure.keyvault.keys import KeyType
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import AsyncKeysClientPreparer, get_decorator
from _shared.test_case_async import KeyVaultTestCase

all_api_versions = get_decorator(is_async=True, only_vault=True)
only_hsm = get_decorator(only_hsm=True, is_async=True)


def print(*args):
    assert all(arg is not None for arg in args)


@pytest.mark.asyncio
async def test_create_key_client():
    vault_url = "vault_url"
    # pylint:disable=unused-variable
    # [START create_key_client]
    from azure.identity.aio import DefaultAzureCredential
    from azure.keyvault.keys.aio import KeyClient

    # Create a KeyClient using default Azure credentials
    credential = DefaultAzureCredential()
    key_client = KeyClient(vault_url, credential)

    # the client and credential should be closed when no longer needed
    # (both are also async context managers)
    await key_client.close()
    await credential.close()
    # [END create_key_client]


class TestExamplesKeyVault(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",all_api_versions)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_example_key_crud_operations(self, key_client, **kwargs):
        if (self.is_live and os.environ["KEYVAULT_SKU"] != "premium"):
            pytest.skip("This test is not supported on standard SKU vaults. Follow up with service team")

        key_name = self.get_resource_name("key-name")

        # [START create_key]
        from dateutil import parser as date_parse

        key_size = 2048
        key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
        expires_on = date_parse.parse("2050-02-02T08:00:00.000Z")

        # create a key with optional arguments
        key = await key_client.create_key(
            key_name, KeyType.rsa, size=key_size, key_operations=key_ops, expires_on=expires_on
        )

        print(key.id)
        print(key.name)
        print(key.key_type)
        print(key.properties.enabled)
        print(key.properties.expires_on)
        # [END create_key]

        # [START create_rsa_key]
        # create an rsa key in a hardware security module
        key = await key_client.create_rsa_key(key_name, hardware_protected=True, size=2048)

        print(key.id)
        print(key.name)
        print(key.key_type)
        # [END create_rsa_key]

        # [START create_ec_key]
        # create an elliptic curve (ec) key
        key_curve = "P-256"
        ec_key = await key_client.create_ec_key(key_name, curve=key_curve)

        print(ec_key.id)
        print(ec_key.name)
        print(ec_key.key_type)
        print(ec_key.key.crv)
        # [END create_ec_key]

        # [START get_key]
        # get the latest version of a key
        key = await key_client.get_key(key_name)

        # alternatively, specify a version
        key_version = key.properties.version
        key = await key_client.get_key(key_name, key_version)

        print(key.id)
        print(key.name)
        print(key.properties.version)
        print(key.key_type)
        print(key.properties.vault_url)
        # [END get_key]

        # [START update_key]
        # update attributes of an existing key
        expires_on = date_parse.parse("2050-01-02T08:00:00.000Z")
        tags = {"foo": "updated tag"}
        updated_key = await key_client.update_key_properties(key.name, expires_on=expires_on, tags=tags)

        print(updated_key.properties.version)
        print(updated_key.properties.updated_on)
        print(updated_key.properties.expires_on)
        print(updated_key.properties.tags)
        print(updated_key.key_type)
        # [END update_key]

        # [START delete_key]
        # delete a key
        deleted_key = await key_client.delete_key(key_name)

        print(deleted_key.name)

        # if the vault has soft-delete enabled, the key's
        # scheduled purge date, deleted_date and recovery id are set
        print(deleted_key.deleted_date)
        print(deleted_key.scheduled_purge_date)
        print(deleted_key.recovery_id)
        # [END delete_key]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",only_hsm)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_example_create_oct_key(self, key_client, **kwargs):
        key_name = self.get_resource_name("key")

        # [START create_oct_key]
        key = await key_client.create_oct_key(key_name, size=256, hardware_protected=True)

        print(key.id)
        print(key.name)
        print(key.key_type)
        # [END create_oct_key]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",all_api_versions)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_example_key_list_operations(self, key_client, **kwargs):
        for i in range(4):
            key_name = self.get_resource_name(f"key{i}")
            await key_client.create_ec_key(key_name)
        for i in range(4):
            key_name = self.get_resource_name(f"key{i}")
            await key_client.create_rsa_key(key_name)

        # [START list_keys]
        # list keys
        keys = key_client.list_properties_of_keys()

        async for key in keys:
            print(key.id)
            print(key.created_on)
            print(key.name)
            print(key.updated_on)
            print(key.enabled)
        # [END list_keys]

        # [START list_properties_of_key_versions]
        # get an iterator of all versions of a key
        key_versions = key_client.list_properties_of_key_versions("key-name")

        async for key in key_versions:
            print(key.id)
            print(key.updated_on)
            print(key.properties.version)
            print(key.expires_on)
        # [END list_properties_of_key_versions]

        # [START list_deleted_keys]
        # get an iterator of deleted keys (requires soft-delete enabled for the vault)
        deleted_keys = key_client.list_deleted_keys()

        async for key in deleted_keys:
            print(key.id)
            print(key.name)
            print(key.scheduled_purge_date)
            print(key.recovery_id)
            print(key.deleted_date)
        # [END list_deleted_keys]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",all_api_versions)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_example_keys_backup_restore(self, key_client, **kwargs):
        key_name = self.get_resource_name("key-name")
        await key_client.create_key(key_name, "RSA")
        # [START backup_key]
        # backup key
        key_backup = await key_client.backup_key(key_name)

        # returns the raw bytes of the backup
        print(key_backup)
        # [END backup_key]

        await key_client.delete_key(key_name)
        await key_client.purge_deleted_key(key_name)

        if self.is_live:
            # perform operations to prevent our connection from getting closed while waiting
            await asyncio.sleep(60)
            wait_key_name = self.get_resource_name("waitkey")
            await key_client.create_key(wait_key_name, "RSA")
            await asyncio.sleep(60)
            await key_client.get_key(wait_key_name)
            await asyncio.sleep(60)

        # [START restore_key_backup]
        # restores a backup
        restored_key = await key_client.restore_key_backup(key_backup)
        print(restored_key.id)
        print(restored_key.name)
        print(restored_key.properties.version)
        # [END restore_key_backup]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",all_api_versions)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_example_keys_recover(self, key_client, **kwargs):
        key_name = self.get_resource_name("key-name")
        created_key = await key_client.create_key(key_name, "RSA")

        await key_client.delete_key(created_key.name)

        # [START get_deleted_key]
        # get a deleted key (requires soft-delete enabled for the vault)
        deleted_key = await key_client.get_deleted_key(key_name)
        print(deleted_key.name)
        # [END get_deleted_key]

        # [START recover_deleted_key]
        # recover deleted key to its latest version (requires soft-delete enabled for the vault)
        recovered_key = await key_client.recover_deleted_key(key_name)
        print(recovered_key.id)
        print(recovered_key.name)
        # [END recover_deleted_key]
