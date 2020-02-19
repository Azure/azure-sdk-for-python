# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
from dateutil import parser as date_parse
import time
import hashlib
import os
import logging
import json

from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer
from secrets_preparer import VaultClientPreparer
from secrets_test_case import KeyVaultTestCase
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError


# used for logging tests
class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []
    def emit(self, record):
        self.messages.append(record)


class SecretClientTests(KeyVaultTestCase):
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

    def _validate_secret_list(self, secrets, expected):
        for secret in secrets:
            if secret.name in expected.keys():
                expected_secret = expected[secret.name]
                self._assert_secret_attributes_equal(expected_secret.properties, secret)
                del expected[secret.name]
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_secret_crud_operations(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.secrets
        secret_name = "crud-secret"
        secret_value = self.get_resource_name("crud_secret_value")

        # create secret
        created = client.set_secret(secret_name, secret_value)
        self._validate_secret_bundle(created, vault_client.vault_url, secret_name, secret_value)

        # set secret with optional arguments
        expires = date_parse.parse("2050-02-02T08:00:00.000Z")
        not_before = date_parse.parse("2015-02-02T08:00:00.000Z")
        content_type = "password"
        enabled = True
        tags = {"foo": "created tag"}
        created = client.set_secret(
            secret_name,
            secret_value,
            enabled=enabled,
            content_type=content_type,
            not_before=not_before,
            expires_on=expires,
            tags=tags,
        )
        self._validate_secret_bundle(created, vault_client.vault_url, secret_name, secret_value)
        self.assertEqual(content_type, created.properties.content_type)
        self.assertEqual(enabled, created.properties.enabled)
        self.assertEqual(not_before, created.properties.not_before)
        self.assertEqual(expires, created.properties.expires_on)
        self.assertEqual(tags, created.properties.tags)

        self._assert_secret_attributes_equal(created.properties, client.get_secret(created.name).properties)
        self._assert_secret_attributes_equal(
            created.properties, client.get_secret(created.name, created.properties.version).properties
        )

        def _update_secret(secret):
            content_type = "text/plain"
            expires = date_parse.parse("2050-01-02T08:00:00.000Z")
            tags = {"foo": "updated tag"}
            enabled = not secret.properties.enabled
            updated_secret = client.update_secret_properties(
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

        if self.is_live:
            # wait to ensure the secret's update time won't equal its creation time
            time.sleep(1)

        updated = _update_secret(created)

        # delete secret
        deleted = client.begin_delete_secret(updated.name).result()
        self.assertIsNotNone(deleted)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_secret_list(self, vault_client, **kwargs):

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
                secret = client.set_secret(secret_name, secret_value)
                expected[secret.name] = secret

        # list secrets
        result = list(client.list_properties_of_secrets(max_page_size=max_secrets - 1))
        self._validate_secret_list(result, expected)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_list_versions(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.secrets
        secret_name = self.get_resource_name("secVer")
        secret_value = self.get_resource_name("secVal")

        max_secrets = self.list_test_size
        expected = {}

        # create many secret versions
        for _ in range(0, max_secrets):
            secret = None
            while not secret:
                secret = client.set_secret(secret_name, secret_value)
                expected[secret.id] = secret

        result = client.list_properties_of_secret_versions(secret_name, max_page_size=max_secrets - 1)

        # validate list secret versions with attributes
        for secret in result:
            if secret.id in expected.keys():
                expected_secret = expected[secret.id]
                del expected[secret.id]
                self._assert_secret_attributes_equal(expected_secret.properties, secret)
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_list_deleted_secrets(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets

        expected = {}

        # create secrets
        for i in range(self.list_test_size):
            secret_name = "secret{}".format(i)
            secret_value = "value{}".format(i)
            expected[secret_name] = client.set_secret(secret_name, secret_value)

        # delete them
        for secret_name in expected.keys():
            client.begin_delete_secret(secret_name).wait()

        # validate list deleted secrets with attributes
        for deleted_secret in client.list_deleted_secrets():
            self.assertIsNotNone(deleted_secret.deleted_date)
            self.assertIsNotNone(deleted_secret.scheduled_purge_date)
            self.assertIsNotNone(deleted_secret.recovery_id)
            expected_secret = expected[deleted_secret.name]
            self._assert_secret_attributes_equal(expected_secret.properties, deleted_secret.properties)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer(enable_soft_delete=False)
    @VaultClientPreparer()
    def test_backup_restore(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets
        secret_name = self.get_resource_name("secbak")
        secret_value = self.get_resource_name("secVal")

        # create secret
        created_bundle = client.set_secret(secret_name, secret_value)

        # backup secret
        secret_backup = client.backup_secret(created_bundle.name)
        self.assertIsNotNone(secret_backup, "secret_backup")

        # delete secret
        client.begin_delete_secret(created_bundle.name).wait()

        # restore secret
        restored = client.restore_secret_backup(secret_backup)
        self._assert_secret_attributes_equal(created_bundle.properties, restored)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_recover(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets

        secrets = {}

        # create secrets to recover
        for i in range(self.list_test_size):
            secret_name = "secret{}".format(i)
            secret_value = "value{}".format(i)
            secrets[secret_name] = client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            client.begin_delete_secret(secret_name).wait()

        # validate all our deleted secrets are returned by list_deleted_secrets
        deleted = [s.name for s in client.list_deleted_secrets()]
        self.assertTrue(all(s in deleted for s in secrets.keys()))

        # recover select secrets
        for secret_name in secrets.keys():
            client.begin_recover_deleted_secret(secret_name).wait()

        # validate the recovered secrets exist
        for secret_name in secrets.keys():
            secret = client.get_secret(name=secret_name)
            self._assert_secret_attributes_equal(secret.properties, secrets[secret.name].properties)

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_purge(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets

        secrets = {}

        # create secrets to purge
        for i in range(self.list_test_size):
            secret_name = "secret{}".format(i)
            secret_value = "value{}".format(i)
            secrets[secret_name] = client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            client.begin_delete_secret(secret_name).wait()

        # validate all our deleted secrets are returned by list_deleted_secrets
        deleted = [s.name for s in client.list_deleted_secrets()]
        self.assertTrue(all(s in deleted for s in secrets.keys()))

        # purge secrets
        for secret_name in secrets.keys():
            client.purge_deleted_secret(secret_name)
        for secret_name in secrets.keys():
            self._poll_until_exception(functools.partial(client.get_deleted_secret, secret_name), ResourceNotFoundError)

        deleted = [s.name for s in client.list_deleted_secrets()]
        self.assertTrue(not any(s in deleted for s in secrets.keys()))

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer(client_kwargs={'logging_enable': True})
    def test_logging_enabled(self, vault_client, **kwargs):
        client = vault_client.secrets
        mock_handler = MockHandler()

        logger = logging.getLogger('azure')
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        client.set_secret("secret-name", "secret-value")

        for message in mock_handler.messages:
            if message.levelname == 'DEBUG' and message.funcName == 'on_request':
                try:
                    body = json.loads(message.message)
                    if body['value'] == 'secret-value':
                        return
                except (ValueError, KeyError):
                    # this means the message is not JSON or has no kty property
                    pass

        assert False, "Expected request body wasn't logged"

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_logging_disabled(self, vault_client, **kwargs):
        client = vault_client.secrets
        mock_handler = MockHandler()

        logger = logging.getLogger('azure')
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        client.set_secret("secret-name", "secret-value")

        for message in mock_handler.messages:
            if message.levelname == 'DEBUG' and message.funcName == 'on_request':
                try:
                    body = json.loads(message.message)
                    assert body["value"] != "secret-value", "Client request body was logged"
                except (ValueError, KeyError):
                    # this means the message is not JSON or has no kty property
                    pass
