# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio

from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import ResourceGroupPreparer
from async_preparer import AsyncVaultClientPreparer
from async_test_case import AsyncKeyVaultTestCase


from dateutil import parser as date_parse


class KeyVaultSecretTest(AsyncKeyVaultTestCase):
    def _assert_secret_attributes_equal(self, s1, s2):
        # self.assertEqual(s1.id , s2.id)
        self.assertEqual(s1.content_type, s2.content_type)
        self.assertEqual(s1.enabled, s2.enabled)
        self.assertEqual(s1.not_before, s2.not_before)
        self.assertEqual(s1.expires, s2.expires)
        self.assertEqual(s1.created, s2.created)
        self.assertEqual(s1.updated, s2.updated)
        self.assertEqual(s1.recovery_level, s2.recovery_level)
        self.assertEqual(s1.key_id, s2.key_id)

    def _validate_secret_bundle(self, secret_attributes, vault, secret_name, secret_value):
        prefix = "/".join(s.strip("/") for s in [vault, "secrets", secret_name])
        id = secret_attributes.id
        self.assertTrue(id.index(prefix) == 0, "Id should start with '{}', but value is '{}'".format(prefix, id))
        self.assertEqual(
            secret_attributes.value,
            secret_value,
            "value should be '{}', but is '{}'".format(secret_value, secret_attributes.value),
        )
        self.assertTrue(secret_attributes.created and secret_attributes.updated, "Missing required date attributes.")

    async def _validate_secret_list(self, secrets, expected):
        async for secret in secrets:
            # TODO: what if secrets contains unexpected entries?
            if secret.name in expected.keys():
                expected_secret = expected[secret.name]
                self._assert_secret_attributes_equal(expected_secret, secret)
                del expected[secret.name]
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_secret_crud_operations(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets
        secret_name = "crud-secret"
        secret_value = self.get_resource_name("crud_secret_value")

        # create secret
        created = await client.set_secret(secret_name, secret_value)
        self._validate_secret_bundle(created, vault_client.vault_url, secret_name, secret_value)

        # set secret with optional arguments
        not_before = date_parse.parse("2015-02-02T08:00:00.000Z")
        enabled = True
        tags = {"foo": "created tag"}
        created = await client.set_secret(secret_name, secret_value, enabled=enabled, not_before=not_before, tags=tags)
        self._validate_secret_bundle(created, vault_client.vault_url, secret_name, secret_value)
        self.assertEqual(enabled, created.enabled)
        self.assertEqual(not_before, created.not_before)
        self.assertEqual(tags, created.tags)

        # get secret without version
        retrieved_secret = await client.get_secret(created.name, "")
        self.assertEqual(created.id, retrieved_secret.id)
        self._assert_secret_attributes_equal(created, retrieved_secret)

        # get secret with version
        secret_with_version = await client.get_secret(created.name, created.version)
        self.assertEqual(created.id, retrieved_secret.id)
        self._assert_secret_attributes_equal(created, secret_with_version)

        async def _update_secret(secret):
            content_type = "text/plain"
            expires = date_parse.parse("2050-02-02T08:00:00.000Z")
            tags = {"foo": "updated tag"}
            enabled = not secret.enabled
            updated_secret = await client.update_secret(
                secret.name, secret.version, content_type=content_type, expires=expires, tags=tags, enabled=enabled
            )
            self.assertEqual(tags, updated_secret.tags)
            self.assertEqual(secret.id, updated_secret.id)
            self.assertEqual(content_type, updated_secret.content_type)
            self.assertEqual(expires, updated_secret.expires)
            self.assertNotEqual(secret.enabled, updated_secret.enabled)
            self.assertNotEqual(secret.updated, updated_secret.updated)
            return updated_secret

        # update secret with version
        if self.is_live:
            # wait a second to ensure the secret's update time won't equal its creation time
            await asyncio.sleep(1)

        updated = await _update_secret(created)

        # delete secret
        deleted = await client.delete_secret(updated.name)
        self.assertIsNotNone(deleted)

        await self._poll_until_exception(
            client.get_secret, updated.name, expected_exception=ResourceNotFoundError
        )

    @ResourceGroupPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_secret_list(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets

        max_secrets = self.list_test_size
        expected = {}

        # create many secrets
        for x in range(0, max_secrets):
            secret_name = "sec{}".format(x)
            secret_value = self.get_resource_name("secVal{}".format(x))
            secret = None
            while not secret:
                secret = await client.set_secret(secret_name, secret_value)
                expected[secret_name] = secret

        # list secrets
        result = client.list_secrets(max_results=max_secrets)
        await self._validate_secret_list(result, expected)

    @ResourceGroupPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_list_versions(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets
        secret_name = self.get_resource_name("sec")
        secret_value = self.get_resource_name("secVal")

        max_secrets = self.list_test_size
        expected = {}

        # create many secret versions
        for _ in range(0, max_secrets):
            secret = None
            while not secret:
                secret = await client.set_secret(secret_name, secret_value)
                expected[secret.id] = secret

        # list secret versions
        result = client.list_secret_versions(secret_name)

        # validate list secret versions with attributes
        async for secret in result:
            if secret.id in expected.keys():
                expected_secret = expected[secret.id]
                del expected[secret.id]
                self._assert_secret_attributes_equal(expected_secret, secret)
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer()
    @AsyncVaultClientPreparer(enable_soft_delete=True)
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_list_deleted_secrets(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets
        secret_name = self.get_resource_name("sec")
        secret_value = self.get_resource_name("secval")
        expected = {}

        # create secrets to delete
        for _ in range(0, self.list_test_size):
            expected[secret_name] = await client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in expected.keys():
            await client.delete_secret(secret_name)

        await self._poll_until_no_exception(
            client.get_deleted_secret, *expected.keys(), expected_exception=ResourceNotFoundError
        )

        # validate all our deleted secrets are returned by list_deleted_secrets
        result = client.list_deleted_secrets()
        await self._validate_secret_list(result, expected)

    @ResourceGroupPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_backup_restore(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets
        secret_name = self.get_resource_name("secbak")
        secret_value = self.get_resource_name("secVal")

        # create secret
        created_bundle = await client.set_secret(secret_name, secret_value)

        # backup secret
        secret_backup = await client.backup_secret(created_bundle.name)
        self.assertIsNotNone(secret_backup, "secret_backup")

        # delete secret
        await client.delete_secret(created_bundle.name)

        # restore secret
        restored = await client.restore_secret(secret_backup)
        self.assertEqual(created_bundle.id, restored.id)
        self._assert_secret_attributes_equal(created_bundle, restored)

    @ResourceGroupPreparer()
    @AsyncVaultClientPreparer(enable_soft_delete=True)
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_recover(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets

        secrets = {}

        # create secrets to recover
        for i in range(self.list_test_size):
            secret_name = "secret{}".format(i)
            secret_value = "value{}".format(i)
            secrets[secret_name] = await client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            await client.delete_secret(secret_name)
        await self._poll_until_no_exception(
            client.get_deleted_secret, *secrets.keys(), expected_exception=ResourceNotFoundError
        )

        # validate all our deleted secrets are returned by list_deleted_secrets
        async for deleted_secret in client.list_deleted_secrets():
            assert deleted_secret.name in secrets

        # recover select secrets
        for secret_name in secrets.keys():
            await client.recover_deleted_secret(secret_name)

        # validate the recovered secrets exist
        await self._poll_until_no_exception(
            client.get_secret, *secrets.keys(), expected_exception=ResourceNotFoundError
        )

    @ResourceGroupPreparer()
    @AsyncVaultClientPreparer(enable_soft_delete=True)
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_purge(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets

        secrets = {}

        # create secrets to purge
        for i in range(self.list_test_size):
            secret_name = "secret{}".format(i)
            secret_value = "value{}".format(i)
            secrets[secret_name] = await client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            await client.delete_secret(secret_name)
        await self._poll_until_no_exception(
            client.get_deleted_secret, *secrets.keys(), expected_exception=ResourceNotFoundError
        )

        # validate all our deleted secrets are returned by list_deleted_secrets
        async for deleted_secret in client.list_deleted_secrets():
            assert deleted_secret.name in secrets

        # purge secrets
        for secret_name in secrets.keys():
            await client.purge_deleted_secret(secret_name)
