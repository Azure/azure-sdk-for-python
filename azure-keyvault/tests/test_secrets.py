from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase
from azure.keyvault import KeyVaultId, KeyVaultClient, KeyVaultAuthentication, AccessToken

import copy
from dateutil import parser as date_parse
import time
import unittest


class KeyVaultSecretTest(KeyvaultTestCase):


    def _validate_secret_bundle(self, bundle, vault, secret_name, secret_value):
        prefix = '{}secrets/{}/'.format(vault, secret_name)
        id = bundle.id
        self.assertTrue(id.index(prefix) == 0,
                        "String should start with '{}', but value is '{}'".format(prefix, id))
        self.assertEqual(bundle.value, secret_value,
                         "value should be '{}', but is '{}'".format(secret_value, bundle.value))
        self.assertTrue(bundle.attributes.created and bundle.attributes.updated,
                        'Missing required date attributes.')

    def _validate_secret_list(self, secrets, expected):
        for secret in secrets:
            if secret.id in expected.keys():
                attributes = expected[secret.id]
                self.assertEqual(attributes, secret.attributes)
                del expected[secret.id]

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_secret_crud_operations(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        secret_name = 'crud-secret'
        secret_value = self.get_resource_name('crud_secret_value')

        # create secret
        secret_bundle = self.client.set_secret(vault_uri, secret_name, secret_value)
        self._validate_secret_bundle(secret_bundle, vault_uri, secret_name, secret_value)
        created_bundle = secret_bundle
        secret_id = KeyVaultId.parse_secret_id(created_bundle.id)

        # get secret without version
        self.assertEqual(created_bundle, self.client.get_secret(secret_id.vault, secret_id.name, ''))

        # get secret with version
        self.assertEqual(created_bundle, self.client.get_secret(secret_id.vault, secret_id.name, secret_id.version))

        def _update_secret(secret_uri):
            updating_bundle = copy.deepcopy(created_bundle)
            updating_bundle.content_type = 'text/plain'
            updating_bundle.attributes.expires = date_parse.parse('2050-02-02T08:00:00.000Z')
            updating_bundle.tags = {'foo': 'updated tag'}
            sid = KeyVaultId.parse_secret_id(secret_uri)
            secret_bundle = self.client.update_secret(
                sid.vault, sid.name, sid.version, updating_bundle.content_type, updating_bundle.attributes,
                updating_bundle.tags)
            self.assertEqual(updating_bundle.tags, secret_bundle.tags)
            self.assertEqual(updating_bundle.id, secret_bundle.id)
            self.assertNotEqual(str(updating_bundle.attributes.updated), str(secret_bundle.attributes.updated))
            return secret_bundle

        # update secret without version
        secret_bundle = _update_secret(secret_id.base_id)

        # update secret with version
        secret_bundle = _update_secret(secret_id.id)

        # delete secret
        self.client.delete_secret(secret_id.vault, secret_id.name)

        # get secret returns not found
        try:
            self.client.get_secret(secret_id.vault, secret_id.name, '')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
                raise ex

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_secret_list(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        max_secrets = self.list_test_size
        expected = {}

        # create many secrets
        for x in range(0, max_secrets):
            secret_name = 'sec{}'.format(x)
            secret_value = self.get_resource_name('secVal{}'.format(x))
            secret_bundle = None
            error_count = 0
            while not secret_bundle:
                try:
                    secret_bundle = self.client.set_secret(vault_uri, secret_name, secret_value)
                    sid = KeyVaultId.parse_secret_id(secret_bundle.id).base_id.strip('/')
                    expected[sid] = secret_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list secrets
        result = list(self.client.get_secrets(vault_uri, self.list_test_size))
        self._validate_secret_list(result, expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_list_versions(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        secret_name = self.get_resource_name('sec')
        secret_value = self.get_resource_name('secVal')

        max_secrets = self.list_test_size
        expected = {}

        # create many secret versions
        for x in range(0, max_secrets):
            secret_bundle = None
            error_count = 0
            while not secret_bundle:
                try:
                    secret_bundle = self.client.set_secret(vault_uri, secret_name, secret_value)
                    sid = KeyVaultId.parse_secret_id(secret_bundle.id).id.strip('/')
                    expected[sid] = secret_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list secret versions
        self._validate_secret_list(list(self.client.get_secret_versions(vault_uri, secret_name)), expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_backup_restore(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri
        secret_name = self.get_resource_name('secbak')
        secret_value = self.get_resource_name('secVal')

        # create secret
        created_bundle = self.client.set_secret(vault_uri, secret_name, secret_value)
        secret_id = KeyVaultId.parse_secret_id(created_bundle.id)

        # backup secret
        secret_backup = self.client.backup_secret(secret_id.vault, secret_id.name).value

        # delete secret
        self.client.delete_secret(secret_id.vault, secret_id.name)

        # restore secret
        self.assertEqual(created_bundle.attributes, self.client.restore_secret(vault_uri, secret_backup).attributes)

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_recover_purge(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        vault_uri = vault.properties.vault_uri

        secrets = {}

        # create secrets to recover
        for i in range(0, self.list_test_size):
            secret_name = self.get_resource_name('secrec{}'.format(str(i)))
            secret_value = self.get_resource_name('secval{}'.format((str(i))))
            secrets[secret_name] = self.client.set_secret(vault_uri, secret_name, secret_value)

        # create secrets to purge
        for i in range(0, self.list_test_size):
            secret_name = self.get_resource_name('secprg{}'.format(str(i)))
            secret_value = self.get_resource_name('secval{}'.format((str(i))))
            secrets[secret_name] = self.client.set_secret(vault_uri, secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            self.client.delete_secret(vault_uri, secret_name)

        if not self.is_playback():
            time.sleep(20)

        # validate all our deleted secrets are returned by get_deleted_secrets
        deleted = [KeyVaultId.parse_secret_id(s.id).name for s in self.client.get_deleted_secrets(vault_uri)]
        self.assertTrue(all(s in deleted for s in secrets.keys()))

        # recover select secrets
        for secret_name in [s for s in secrets.keys() if s.startswith('secrec')]:
            self.client.recover_deleted_secret(vault_uri, secret_name)

        # purge select secrets
        for secret_name in [s for s in secrets.keys() if s.startswith('secprg')]:
            self.client.purge_deleted_secret(vault_uri, secret_name)

        if not self.is_playback():
            time.sleep(20)

        # validate none of our deleted secrets are returned by get_deleted_secrets
        deleted = [KeyVaultId.parse_secret_id(s.id).name for s in self.client.get_deleted_secrets(vault_uri)]
        self.assertTrue(not any(s in deleted for s in secrets.keys()))

        # validate the recovered secrets
        expected = {k: v for k, v in secrets.items() if k.startswith('secrec')}
        actual = {k: self.client.get_secret(vault_uri, k, KeyVaultId.version_none) for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))