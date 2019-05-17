# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools

from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import ResourceGroupPreparer
from preparer import VaultClientPreparer
from test_case import KeyVaultTestCase

from azure.security.keyvault.aio.vault_client import VaultClient

from dateutil import parser as date_parse
import time


def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
       upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        # TODO: this is a workaround for VaultClientPreparer creating a sync client
        vault_client = kwargs.get("vault_client")
        credentials = test_class_instance.settings.get_credentials(resource="https://vault.azure.net")
        aio_client = VaultClient(vault_client.vault_url, credentials)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, vault_client=aio_client))

    return run


class KeyVaultKeyTest(KeyVaultTestCase):
    async def _poll_until_resource_found(self, fn, key_names, max_retries=20, retry_delay=6):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        if not self.is_live:
            return

        for i in range(max_retries):
            await asyncio.sleep(retry_delay)
            try:
                for name in key_names:
                    # TODO: this enables polling get_key but it'd be better if caller applied args to fn
                    await fn(name, version="")
                break
            except ResourceNotFoundError:
                if i == max_retries - 1:
                    raise

    def _assert_key_attributes_equal(self, k1, k2):
        self.assertEqual(k1.name, k2.name)
        self.assertEqual(k1.vault_url, k2.vault_url)
        self.assertEqual(k1.enabled, k2.enabled)
        self.assertEqual(k1.not_before, k2.not_before)
        self.assertEqual(k1.expires, k2.expires)
        self.assertEqual(k1.created, k2.created)
        self.assertEqual(k1.updated, k2.updated)
        self.assertEqual(k1.tags, k2.tags)
        self.assertEqual(k1.recovery_level, k2.recovery_level)

    async def _create_rsa_key(self, client, key_name, key_type):
        # create key with optional arguments
        key_size = 2048
        key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
        tags = {"purpose": "unit test", "test name ": "CreateRSAKeyTest"}
        created_key = await client.create_rsa_key(
            key_name, key_type=key_type, size=key_size, key_ops=key_ops, tags=tags
        )
        self.assertTrue(created_key.tags, "Missing the optional key attributes.")
        self.assertEqual(tags, created_key.tags)
        self._validate_rsa_key_bundle(created_key, client.vault_url, key_name, key_type)
        return created_key

    async def _create_ec_key(self, client, key_name, key_type):
        # create ec key with optional arguments
        enabled = True
        tags = {"purpose": "unit test", "test name": "CreateECKeyTest"}
        created_key = await client.create_ec_key(key_name, key_type=key_type, enabled=enabled)
        self.assertTrue(created_key.enabled, "Missing the optional key attributes.")
        self.assertEqual(enabled, created_key.enabled)
        self._validate_ec_key_bundle(created_key, client.vault_url, key_name, key_type)
        return created_key

    def _validate_ec_key_bundle(self, key_attributes, vault, key_name, kty):
        key_curve = "P-256"
        prefix = "/".join(s.strip("/") for s in [vault, "keys", key_name])
        key = key_attributes.key_material
        kid = key_attributes.id
        self.assertEqual(key_curve, key.crv)
        self.assertTrue(kid.index(prefix) == 0, "Key Id should start with '{}', but value is '{}'".format(prefix, kid))
        self.assertEqual(key.kty, kty, "kty should by '{}', but is '{}'".format(key, key.kty))
        self.assertTrue(key_attributes.created and key_attributes.updated, "Missing required date attributes.")

    def _validate_rsa_key_bundle(self, key_attributes, vault, key_name, kty, key_ops=None):
        prefix = "/".join(s.strip("/") for s in [vault, "keys", key_name])
        key_ops = key_ops or ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
        key = key_attributes.key_material
        kid = key_attributes.id
        self.assertTrue(kid.index(prefix) == 0, "Key Id should start with '{}', but value is '{}'".format(prefix, kid))
        self.assertEqual(key.kty, kty, "kty should by '{}', but is '{}'".format(key, key.kty))
        self.assertTrue(key.n and key.e, "Bad RSA public material.")
        self.assertEqual(key_ops, key.key_ops, "keyOps should be '{}', but is '{}'".format(key_ops, key.key_ops))
        self.assertTrue(key_attributes.created and key_attributes.updated, "Missing required date attributes.")

    async def _update_key(self, client, key):
        expires = date_parse.parse("2050-01-02T08:00:00.000Z")
        tags = {"foo": "updated tag"}
        key_bundle = await client.update_key(key.name, key.version, expires=expires, tags=tags)
        self.assertEqual(tags, key_bundle.tags)
        self.assertEqual(key.id, key_bundle.id)
        self.assertNotEqual(key.updated, key_bundle.updated)
        return key_bundle

    async def _validate_key_list(self, keys, expected):
        async for key in keys:
            if key.name in expected.keys():
                self._assert_key_attributes_equal(expected[key.name], key)
                del expected[key.name]
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_key_crud_operations(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.keys

        # create ec key
        created_ec_key = await self._create_ec_key(client, key_name="crud-ec-key", key_type="EC")

        # create rsa key
        created_rsa_key = await self._create_rsa_key(client, key_name="crud-rsa-key", key_type="RSA")

        # get the created key with version
        key = await client.get_key(created_rsa_key.name, created_rsa_key.version)
        self.assertEqual(key.version, created_rsa_key.version)
        self._assert_key_attributes_equal(created_rsa_key, key)

        # get key without version
        self._assert_key_attributes_equal(created_rsa_key, await client.get_key(created_rsa_key.name, ""))

        # update key with version
        if self.is_live:
            # wait to ensure the key's update time won't equal its creation time
            time.sleep(1)
        self._update_key(client, created_rsa_key)

        # delete the new key
        deleted_key = await client.delete_key(created_rsa_key.name)
        self.assertIsNotNone(deleted_key)
        self.assertEqual(created_rsa_key.key_material, deleted_key.key_material)
        self.assertEqual(deleted_key.id, created_rsa_key.id)
        self.assertTrue(
            deleted_key.recovery_id and deleted_key.deleted_date and deleted_key.scheduled_purge_date,
            "Missing required deleted key attributes.",
        )

        if self.is_live:
            # wait to ensure the key has been deleted
            time.sleep(30)
        # get the deleted key when soft deleted enabled
        deleted_key = await client.get_deleted_key(created_rsa_key.name)
        self.assertIsNotNone(deleted_key)
        self.assertEqual(created_rsa_key.id, deleted_key.id)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    @await_prepared_test
    async def test_key_list(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.keys

        max_keys = self.list_test_size
        expected = {}

        # create many keys
        for x in range(0, max_keys):
            key_name = "key{}".format(x)
            key = await client.create_key(key_name, "RSA")
            expected[key.name] = key

        # list keys
        result = client.list_keys(max_page_size=max_keys)
        self._validate_key_list(result, expected)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    @await_prepared_test
    async def test_list_versions(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.keys
        key_name = self.get_resource_name("testKey")

        max_keys = self.list_test_size
        expected = {}

        # create many key versions
        for _ in range(0, max_keys):
            key = await client.create_key(key_name, "RSA")
            expected[key.id] = key

        result = await client.list_key_versions(key_name)

        # validate list key versions with attributes
        async for key in result:
            if key.id in expected.keys():
                expected_key = expected[key.id]
                del expected[key.id]
                self._assert_key_attributes_equal(expected_key, key)
        self.assertEqual(0, len(expected))

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_list_deleted_keys(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.keys
        key_name = self.get_resource_name("sec")
        key_type = "RSA"
        expected = {}

        # create keys to delete
        for _ in range(0, self.list_test_size):
            expected[key_name] = await client.create_key(key_name, key_type)

        # delete all keys
        for key_name in expected.keys():
            await client.delete_key(key_name)

        await self._poll_until_resource_found(client.get_deleted_key, expected.keys())

        # validate all our deleted keys are returned by list_deleted_keys
        result = await client.list_deleted_keys()
        await self._validate_key_list(result, expected)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    @await_prepared_test
    async def test_backup_restore(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.keys
        key_name = self.get_resource_name("keybak")
        key_type = "RSA"

        # create key
        created_bundle = await client.create_key(key_name, key_type)

        # backup key
        key_backup = await client.backup_key(created_bundle.name)
        self.assertIsNotNone(key_backup, "key_backup")

        # delete key
        await client.delete_key(created_bundle.name)
        # can add test case to see if we do get_deleted should return error

        # restore key
        restored = await client.restore_key(key_backup)
        self.assertEqual(created_bundle.id, restored.id)
        self._assert_key_attributes_equal(created_bundle, restored)

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_recover_purge(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.keys
        keys = {}

        # create keys to recover
        for i in range(0, self.list_test_size):
            key_name = self.get_resource_name("keyrec{}".format(str(i)))
            keys[key_name] = await client.create_key(key_name, "RSA")

        # create keys to purge
        for i in range(0, self.list_test_size):
            key_name = self.get_resource_name("keyprg{}".format(str(i)))
            keys[key_name] = await client.create_key(key_name, "RSA")

        # delete all keys
        for key_name in keys.keys():
            await client.delete_key(key_name)

        await self._poll_until_resource_found(client.get_deleted_key, keys.keys())

        # recover select keys
        for key_name in [s for s in keys.keys() if s.startswith("keyrec")]:
            recovered_key = await client.recover_deleted_key(key_name)
            expected_key = keys[key_name]
            self._assert_key_attributes_equal(expected_key, recovered_key)

        # purge select keys
        for key_name in [s for s in keys.keys() if s.startswith("keyprg")]:
            await client.purge_deleted_key(key_name)

        # validate the recovered keys
        expected = {k: v for k, v in keys.items() if k.startswith("keyrec")}
        await self._poll_until_resource_found(client.get_key, expected.keys())

        actual = {}
        for k in expected.keys():
            actual[k] = await client.get_key(k, "")

        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))

        # validate none of our purged keys are returned by list_deleted_keys
        async for deleted_key in await client.list_deleted_keys():
            self.assertTrue(not any(s in deleted_key for s in keys.keys()))
