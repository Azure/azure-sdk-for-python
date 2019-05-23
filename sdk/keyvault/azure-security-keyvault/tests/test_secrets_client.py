# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from devtools_testutils import ResourceGroupPreparer
from preparer import VaultClientPreparer
from test_case import KeyVaultTestCase
from azure.core.exceptions import HttpResponseError

from dateutil import parser as date_parse
import time


class SecretClientTests(KeyVaultTestCase):
    def _assert_secret_attributes_equal(self, s1, s2):
        self.assertEqual(s1.id, s2.id)
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

    def _validate_secret_list(self, secrets, expected):
        for secret in secrets:
            if secret.name in expected.keys():
                del expected[secret.name]
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
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
            expires=expires,
            tags=tags,
        )
        self._validate_secret_bundle(created, vault_client.vault_url, secret_name, secret_value)
        self.assertEqual(content_type, created.content_type)
        self.assertEqual(enabled, created.enabled)
        self.assertEqual(not_before, created.not_before)
        self.assertEqual(expires, created.expires)
        self.assertEqual(tags, created.tags)

        # get secret without version
        self._assert_secret_attributes_equal(created, client.get_secret(created.name, ""))

        # get secret with version
        self._assert_secret_attributes_equal(created, client.get_secret(created.name, created.version))

        def _update_secret(secret):
            content_type = "text/plain"
            expires = date_parse.parse("2050-01-02T08:00:00.000Z")
            tags = {"foo": "updated tag"}
            secret_bundle = client.update_secret_attributes(
                secret.name, secret.version, content_type=content_type, expires=expires, tags=tags
            )
            self.assertEqual(tags, secret_bundle.tags)
            self.assertEqual(secret.id, secret_bundle.id)
            self.assertNotEqual(secret.updated, secret_bundle.updated)
            return secret_bundle

        # update secret with version
        if self.is_live:
            # wait to ensure the secret's update time won't equal its creation time
            time.sleep(1)
        updated = _update_secret(created)

        # delete secret
        deleted = client.delete_secret(updated.name)
        self.assertIsNotNone(deleted)

        if self.is_live:
            # wait to ensure the secret has been deleted
            # TODO: replace sleeps with polling (client won't do it by default because 404 isn't retryable)
            time.sleep(30)

        # get the deleted secret
        deleted_secret = client.get_deleted_secret(deleted.name)
        self.assertIsNotNone(deleted_secret)

        # TestCase.assertRaisesRegexp was deprecated in 3.2
        if hasattr(self, "assertRaisesRegex"):
            assertRaises = self.assertRaisesRegex
        else:
            assertRaises = self.assertRaisesRegexp

        # deleted secret isn't found
        with assertRaises(HttpResponseError, r"(?i)not found"):
            client.get_secret(deleted.name, "")

    @ResourceGroupPreparer()
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
        result = list(client.list_secrets(max_page_size=max_secrets))
        self._validate_secret_list(result, expected)

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_list_versions(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.secrets
        secret_name = self.get_resource_name("secVer")
        secret_value = self.get_resource_name("secVal")

        max_secrets = self.list_test_size
        max_page_size = 2
        expected = {}

        # create many secret versions
        for _ in range(0, max_secrets):
            secret = None
            while not secret:
                secret = client.set_secret(secret_name, secret_value)
                expected[secret.id] = secret

        result = client.list_secret_versions(secret_name, max_page_size=max_page_size)

        # validate list secret versions with attributes
        for secret in result:
            if secret.id in expected.keys():
                expected_secret = expected[secret.id]
                del expected[secret.id]
                self._assert_secret_attributes_equal(expected_secret, secret)
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_list_deleted_secrets(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.secrets

        secret_name = self.get_resource_name("sec")
        secret_value = self.get_resource_name("secval")
        expected = {}

        # create secrets to delete
        for _ in range(0, self.list_test_size):
            expected[secret_name] = client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in expected.keys():
            client.delete_secret(secret_name)

        if not self.is_playback():
            time.sleep(20)

        # validate all our deleted secrets are returned by list_deleted_secrets
        self._validate_secret_list(list(client.list_deleted_secrets()), expected)

    @ResourceGroupPreparer()
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
        client.delete_secret(created_bundle.name)

        # restore secret
        restored = client.restore_secret(secret_backup)
        self._assert_secret_attributes_equal(created_bundle, restored)

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_recover_purge(self, vault_client, **kwargs):
        self.assertIsNotNone(vault_client)
        client = vault_client.secrets

        secrets = {}

        # create secrets to recover
        for i in range(0, self.list_test_size):
            secret_name = self.get_resource_name("secrec{}".format(str(i)))
            secret_value = self.get_resource_name("secval{}".format(str(i)))
            secrets[secret_name] = client.set_secret(secret_name, secret_value)

        # create secrets to purge
        for i in range(0, self.list_test_size):
            secret_name = self.get_resource_name("secprg{}".format(str(i)))
            secret_value = self.get_resource_name("secval{}".format(str(i)))
            secrets[secret_name] = client.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            client.delete_secret(secret_name)

        if not self.is_playback():
            time.sleep(20)

        # validate all our deleted secrets are returned by list_deleted_secrets
        deleted = [s.name for s in client.list_deleted_secrets()]

        self.assertTrue(all(s in deleted for s in secrets.keys()))

        # recover select secrets
        for secret_name in [s for s in secrets.keys() if s.startswith("secrec")]:
            client.recover_deleted_secret(secret_name)

        # purge select secrets
        for secret_name in [s for s in secrets.keys() if s.startswith("secprg")]:
            client.purge_deleted_secret(secret_name)

        if not self.is_playback():
            time.sleep(20)

        # validate none of our purged secrets are returned by list_deleted_secrets
        deleted = [s.name for s in client.list_deleted_secrets()]
        self.assertTrue(not any(s in deleted for s in secrets.keys()))

        # validate the recovered secrets
        expected = {k: v for k, v in secrets.items() if k.startswith("secrec")}
        actual = {k: client.get_secret(k, "") for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))
