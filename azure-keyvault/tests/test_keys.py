# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from devtools_testutils import ResourceGroupPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase
from dateutil import parser as date_parse

import time


class KeyVaultKeyTest(KeyvaultTestCase):

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

    def _validate_rsa_key_bundle(self, key_attributes, vault, key_name, kty, key_ops=None):
        prefix = "/".join(s.strip("/") for s in [vault, "keys", key_name])
        key_ops = key_ops or ['encrypt', 'decrypt',
                              'sign', 'verify', 'wrapKey', 'unwrapKey']
        key = key_attributes.key_material
        kid = key_attributes.id
        self.assertTrue(kid.index(prefix) == 0,
                        "Key Id should start with '{}', but value is '{}'".format(prefix, kid))
        self.assertEqual(
            key.kty, kty, "kty should by '{}', but is '{}'".format(key, key.kty))
        self.assertTrue(key.n and key.e, 'Bad RSA public material.')
        self.assertEqual(key_ops, key.key_ops,
                         "keyOps should be '{}', but is '{}'".format(key_ops, key.key_ops))
        self.assertTrue(key_attributes.created and key_attributes.updated,
                        'Missing required date attributes.')

    def _update_key(self, client, key):
        expires = date_parse.parse('2050-01-02T08:00:00.000Z')
        tags = {'foo': 'updated tag'}
        key_bundle = client.update_key(
            key.name, key.version,
            expires=expires,
            tags=tags)
        self.assertEqual(tags, key_bundle.tags)
        self.assertEqual(key.id, key_bundle.id)
        self.assertNotEqual(key.updated, key_bundle.updated)
        return key_bundle

    def _validate_key_list(self, keys, expected):
        for key in keys:
            if key.name in expected.keys():
                del expected[key.name]
        self.assertEqual(len(expected), 0)

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_key_crud_operations(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.keys
        key_name = 'crud-test-key'

        # create key
        created_key = client.create_key(key_name, 'RSA')
        self.assertIsNotNone(created_key.version)
        self._validate_rsa_key_bundle(
            created_key, vault_client.vault_url, key_name, 'RSA')
        # assert it creates a version on creation of the key
        self.assertTrue(len(list(client.list_key_versions(key_name))) == 1)

        # create key with optional arguments
        key_size = 2048
        key_ops = [
            "encrypt",
            "decrypt",
            "sign",
            "verify",
            "wrapKey",
            "unwrapKey"
        ]
        tags = {"purpose": "unit test", "test name ": "CreateGetDeleteKeyTest"}
        created_key = client.create_key(
            key_name, 'RSA', size=key_size, key_ops=key_ops, tags=tags)
        self.assertTrue(created_key.version and created_key.tags,
                        'Missing the optional key attributes.')
        self.assertEqual(tags, created_key.tags)
        self._validate_rsa_key_bundle(
            created_key, vault_client.vault_url, key_name, 'RSA')

        # get the created key with version
        key = client.get_key(key_name, created_key.version)
        self.assertEqual(key.version, created_key.version)
        self._assert_key_attributes_equal(created_key, key)

        # get key without version
        self._assert_key_attributes_equal(
            created_key, client.get_key(created_key.name, ''))

        # update key with version
        if self.is_live:
            # wait to ensure the key's update time won't equal its creation time
            time.sleep(1)
        self._update_key(client, created_key)

        # delete the new key
        deleted_key = client.delete_key(key_name)
        self.assertIsNotNone(deleted_key)
        self.assertEqual(created_key.key_material, deleted_key.key_material)
        self.assertEqual(deleted_key.id, created_key.id)
        self.assertTrue(deleted_key.recovery_id and deleted_key.deleted_date and deleted_key.scheduled_purge_date,
                        'Missing required deleted key attributes.')

        if self.is_live:
            # wait to ensure the key has been deleted
            time.sleep(20)
        # get the deleted key when soft deleted enabled
        deleted_key = client.get_deleted_key(deleted_key.name)
        self.assertIsNotNone(deleted_key)
        self.assertEqual(created_key.id, deleted_key.id)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_backup_restore(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.keys
        key_name = self.get_resource_name('keybak')
        key_type = 'RSA'

        # create key
        created_bundle = client.create_key(key_name, key_type)

        # backup key
        key_backup = client.backup_key(created_bundle.name)
        self.assertIsNotNone(key_backup, 'key_backup')

        # delete key
        client.delete_key(created_bundle.name)

        # restore key
        restored = client.restore_key(key_backup)
        self._assert_key_attributes_equal(created_bundle, restored)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_key_list(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.keys

        max_keys = self.list_test_size
        expected = {}

        # create many keys
        for x in range(0, max_keys):
            key_name = 'key{}'.format(x)
            key = client.create_key(key_name, 'RSA')
            expected[key.name] = key

        # list keys
        result = list(client.list_keys(max_page_size=max_keys))
        self._validate_key_list(result, expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_list_versions(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.keys
        key_name = self.get_resource_name('testKey')

        max_keys = self.list_test_size
        max_page_size = 2
        expected = {}

        # create many key versions
        for _ in range(0, max_keys):
            key = client.create_key(key_name, 'RSA')
            expected[key.id] = key

        result = client.list_key_versions(
            key_name, max_page_size=max_page_size)

        # validate list key versions with attributes
        for key in result:
            if key.id in expected.keys():
                expected_key = expected[key.id]
                del expected[key.id]
                self._assert_key_attributes_equal(expected_key, key)
        self.assertEqual(0, len(expected))

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_recover_purge(self, vault_client, **kwargs):

        self.assertIsNotNone(vault_client)
        client = vault_client.keys
        keys = {}

        # create keys to recover
        for i in range(0, self.list_test_size):
            key_name = self.get_resource_name('keyrec{}'.format(str(i)))
            keys[key_name] = client.create_key(key_name, 'RSA')

        # create keys to purge
        for i in range(0, self.list_test_size):
            key_name = self.get_resource_name('keyprg{}'.format(str(i)))
            keys[key_name] = client.create_key(key_name, 'RSA')

        # delete all keys
        for key_name in keys.keys():
            client.delete_key(key_name)

        if self.is_live:
            time.sleep(20)

        # validate all our deleted keys are returned by list_deleted_keys
        deleted = [s.name for s in client.list_deleted_keys()]

        self.assertTrue(all(s in deleted for s in keys.keys()))

        # recover select keys
        for key_name in [s for s in keys.keys() if s.startswith('keyrec')]:
            recovered_key = client.recover_deleted_key(key_name)
            expected_key = keys[key_name]
            self._assert_key_attributes_equal(expected_key, recovered_key)

        # purge select keys
        for key_name in [s for s in keys.keys() if s.startswith('keyprg')]:
            client.purge_deleted_key(key_name)

        if not self.is_playback():
            time.sleep(20)

        # validate none of our purged keys are returned by list_deleted_keys
        deleted = [s.name for s in client.list_deleted_keys()]
        self.assertTrue(not any(s in deleted for s in keys.keys()))

        # validate the recovered keys
        expected = {k: v for k, v in keys.items() if k.startswith('keyrec')}
        actual = {k: client.get_key(k, "") for k in expected.keys()}
        self.assertEqual(
            len(set(expected.keys()) & set(actual.keys())), len(expected))
