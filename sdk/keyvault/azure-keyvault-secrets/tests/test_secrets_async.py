# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
import logging
import json

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.keyvault.secrets.aio import SecretClient
from azure.keyvault.secrets._shared import HttpChallengeCache
from devtools_testutils import PowerShellPreparer
from dateutil import parser as date_parse

from _shared.test_case_async import KeyVaultTestCase

KeyVaultPreparer = functools.partial(
    PowerShellPreparer,
    "keyvault",
    azure_keyvault_url="https://vaultname.vault.azure.net"
)


# used for logging tests
class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class KeyVaultSecretTest(KeyVaultTestCase):
    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(KeyVaultSecretTest, self).tearDown()

    def create_client(self, vault_uri, **kwargs):
        credential = self.get_credential(SecretClient, is_async=True)
        return self.create_client_from_credential(SecretClient, credential=credential, vault_url=vault_uri, **kwargs)

    def _assert_secret_attributes_equal(self, s1, s2):
        self.assertEqual(s1.name, s2.name)
        self.assertEqual(s1.vault_url, s2.vault_url)
        self.assertEqual(s1.content_type, s2.content_type)
        self.assertEqual(s1.enabled, s2.enabled)
        self.assertEqual(s1.not_before, s2.not_before)
        self.assertEqual(s1.expires_on, s2.expires_on)
        self.assertEqual(s1.created_on, s2.created_on)
        self.assertEqual(s1.updated_on, s2.updated_on)
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
        self.assertTrue(
            secret_attributes.properties.created_on and secret_attributes.properties.updated_on,
            "Missing required date attributes.",
        )

    async def _validate_secret_list(self, secrets, expected):
        async for secret in secrets:
            if secret.name in expected.keys():
                expected_secret = expected[secret.name]
                self._assert_secret_attributes_equal(expected_secret.properties, secret)
                del expected[secret.name]
        self.assertEqual(len(expected), 0)

    @KeyVaultPreparer()
    async def test_secret_crud_operations(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        secret_name = self.get_resource_name("crud-secret")
        secret_value = "crud_secret_value"

        # create secret
        created = await client.set_secret(secret_name, secret_value)
        self._validate_secret_bundle(created, client.vault_url, secret_name, secret_value)

        # set secret with optional arguments
        not_before = date_parse.parse("2015-02-02T08:00:00.000Z")
        enabled = True
        tags = {"foo": "created tag"}
        created = await client.set_secret(secret_name, secret_value, enabled=enabled, not_before=not_before, tags=tags)
        self._validate_secret_bundle(created, client.vault_url, secret_name, secret_value)
        self.assertEqual(enabled, created.properties.enabled)
        self.assertEqual(not_before, created.properties.not_before)
        self.assertEqual(tags, created.properties.tags)

        # get secret without version
        retrieved_secret = await client.get_secret(created.name, "")
        self.assertEqual(created.id, retrieved_secret.id)
        self._assert_secret_attributes_equal(created.properties, retrieved_secret.properties)

        # get secret with version
        secret_with_version = await client.get_secret(created.name, created.properties.version)
        self.assertEqual(created.id, retrieved_secret.id)
        self._assert_secret_attributes_equal(created.properties, secret_with_version.properties)

        async def _update_secret(secret):
            content_type = "text/plain"
            expires = date_parse.parse("2050-02-02T08:00:00.000Z")
            tags = {"foo": "updated tag"}
            enabled = not secret.properties.enabled
            updated_secret = await client.update_secret_properties(
                secret.name,
                version=secret.properties.version,
                content_type=content_type,
                expires_on=expires,
                tags=tags,
                enabled=enabled,
            )
            self.assertEqual(tags, updated_secret.tags)
            self.assertEqual(secret.id, updated_secret.id)
            self.assertEqual(content_type, updated_secret.content_type)
            self.assertEqual(expires, updated_secret.expires_on)
            self.assertNotEqual(secret.properties.enabled, updated_secret.enabled)
            self.assertNotEqual(secret.properties.updated_on, updated_secret.updated_on)
            return updated_secret

        # update secret with version
        if self.is_live:
            # wait a second to ensure the secret's update time won't equal its creation time
            await asyncio.sleep(1)

        updated = await _update_secret(created)

        # delete secret
        deleted = await client.delete_secret(updated.name)
        self.assertIsNotNone(deleted)

    @KeyVaultPreparer()
    async def test_secret_list(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        max_secrets = self.list_test_size
        expected = {}

        # create many secrets
        for x in range(0, max_secrets):
            secret_name = self.get_resource_name("sec{}".format(x))
            secret_value = "secVal{}".format(x)
            secret = None
            while not secret:
                secret = await client.set_secret(secret_name, secret_value)
                expected[secret_name] = secret

        # list secrets
        result = client.list_properties_of_secrets(max_page_size=max_secrets - 1)
        await self._validate_secret_list(result, expected)

    @KeyVaultPreparer()
    async def test_list_deleted_secrets(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        expected = {}

        # create secrets
        for i in range(self.list_test_size):
            secret_name = self.get_resource_name("secret{}".format(i))
            secret_value = "value{}".format(i)
            expected[secret_name] = await client.set_secret(secret_name, secret_value)

        # delete them
        for secret_name in expected.keys():
            await client.delete_secret(secret_name)

        # validate list deleted secrets with attributes
        async for deleted_secret in client.list_deleted_secrets():
            self.assertIsNotNone(deleted_secret.deleted_date)
            self.assertIsNotNone(deleted_secret.scheduled_purge_date)
            self.assertIsNotNone(deleted_secret.recovery_id)
            if deleted_secret.name in expected:
                expected_secret = expected[deleted_secret.name]
                self._assert_secret_attributes_equal(expected_secret.properties, deleted_secret.properties)

    @KeyVaultPreparer()
    async def test_list_versions(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        secret_name = self.get_resource_name("sec")
        secret_value = "secVal"

        max_secrets = self.list_test_size
        expected = {}

        # create many secret versions
        for _ in range(0, max_secrets):
            secret = None
            while not secret:
                secret = await client.set_secret(secret_name, secret_value)
                expected[secret.id] = secret

        # list secret versions
        result = client.list_properties_of_secret_versions(secret_name, max_page_size=max_secrets - 1)

        # validate list secret versions with attributes
        async for secret in result:
            if secret.id in expected.keys():
                expected_secret = expected[secret.id]
                del expected[secret.id]
                self._assert_secret_attributes_equal(expected_secret.properties, secret)
        self.assertEqual(len(expected), 0)

    @KeyVaultPreparer()
    async def test_backup_restore(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        secret_name = self.get_resource_name("secbak")
        secret_value = "secVal"

        # create secret
        created_bundle = await client.set_secret(secret_name, secret_value)

        # backup secret
        secret_backup = await client.backup_secret(created_bundle.name)
        self.assertIsNotNone(secret_backup, "secret_backup")

        # delete secret
        await client.delete_secret(created_bundle.name)

        # purge secret
        await client.purge_deleted_secret(created_bundle.name)

        # restore secret
        restore_function = functools.partial(client.restore_secret_backup, secret_backup)
        restored_secret = await self._poll_until_no_exception(restore_function, expected_exception=ResourceExistsError)
        self._assert_secret_attributes_equal(created_bundle.properties, restored_secret)

    @KeyVaultPreparer()
    async def test_recover(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        secrets = {}

        # create secrets to recover
        for i in range(self.list_test_size):
            secret_name = self.get_resource_name("secret{}".format(i))
            secret_value = "value{}".format(i)
            secrets[secret_name] = await client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            await client.delete_secret(secret_name)

        # validate all our deleted secrets are returned by list_deleted_secrets
        async for deleted_secret in client.list_deleted_secrets():
            if deleted_secret.name in secrets:
                secrets.pop(deleted_secret.name)
        assert len(secrets.keys()) == 0

        # recover select secrets
        for secret_name in secrets.keys():
            await client.recover_deleted_secret(secret_name)

        # validate the recovered secrets exist
        for secret in secrets.keys():
            get_function = functools.partial(client.get_secret, secret)
            await self._poll_until_no_exception(get_function, expected_exception=ResourceNotFoundError)

    @KeyVaultPreparer()
    async def test_purge(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        secrets = {}

        # create secrets to purge
        for i in range(self.list_test_size):
            secret_name = self.get_resource_name("secret{}".format(i))
            secret_value = "value{}".format(i)
            secrets[secret_name] = await client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            await client.delete_secret(secret_name)

        # validate all our deleted secrets are returned by list_deleted_secrets
        async for deleted_secret in client.list_deleted_secrets():
            if deleted_secret.name in secrets:
                secrets.pop(deleted_secret.name)
        assert len(secrets.keys()) == 0

        # purge secrets
        for secret_name in secrets.keys():
            await client.purge_deleted_secret(secret_name)

    @KeyVaultPreparer()
    async def test_logging_enabled(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, logging_enable=True)
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        secret_name = self.get_resource_name("secret-name")
        await client.set_secret(secret_name, "secret-value")

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                try:
                    body = json.loads(message.message)
                    if body["value"] == "secret-value":
                        return
                except (ValueError, KeyError):
                    # this means the message is not JSON or has no kty property
                    pass

        assert False, "Expected request body wasn't logged"

    @KeyVaultPreparer()
    async def test_logging_disabled(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, logging_enable=False)
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        secret_name = self.get_resource_name("secret-name")
        await client.set_secret(secret_name, "secret-value")

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                try:
                    body = json.loads(message.message)
                    assert body["value"] != "secret-value", "Client request body was logged"
                except (ValueError, KeyError):
                    # this means the message is not JSON or has no kty property
                    pass


def test_service_headers_allowed_in_logs():
    service_headers = {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
    client = SecretClient("...", object())
    assert service_headers.issubset(client._client._config.http_logging_policy.allowed_header_names)


def test_custom_hook_policy():
    class CustomHookPolicy(SansIOHTTPPolicy):
        pass

    client = SecretClient("...", object(), custom_hook_policy=CustomHookPolicy())
    assert isinstance(client._client._config.custom_hook_policy, CustomHookPolicy)
