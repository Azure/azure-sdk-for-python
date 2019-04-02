from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase
from azure.keyvault import VaultClient

import copy
from dateutil import parser as date_parse
import time
import unittest

import pytest

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
        client = VaultClient(vault.properties.vault_uri, self.settings.get_credentials())
        secret_name = 'crud-secret'
        secret_value = self.get_resource_name('crud_secret_value')

        # create secret
        secret_bundle = client.secrets.set_secret(secret_name, secret_value)
        self._validate_secret_bundle(secret_bundle, vault.properties.vault_uri, secret_name, secret_value)
        created_bundle = secret_bundle

        # get secret without version
        self.assertEqual(created_bundle, client.secrets.get_secret(created_bundle.name, ''))

        # get secret with version
        self.assertEqual(created_bundle, client.secrets.get_secret(created_bundle.name, created_bundle.version))

        def _update_secret(secret):
            updating_bundle = copy.deepcopy(created_bundle)
            updating_bundle.content_type = 'text/plain'
            updating_bundle.attributes.expires = date_parse.parse('2050-02-02T08:00:00.000Z')
            updating_bundle.tags = {'foo': 'updated tag'}
            secret_bundle = client.secrets.update_secret(
                secret.name, secret.version, updating_bundle.content_type, updating_bundle.attributes,
                updating_bundle.tags)
            self.assertEqual(updating_bundle.tags, secret_bundle.tags)
            self.assertEqual(updating_bundle.id, secret_bundle.id)
            self.assertNotEqual(str(updating_bundle.attributes.updated), str(secret_bundle.attributes.updated))
            return secret_bundle

        # update secret with version
        secret_bundle = _update_secret(created_bundle)

        # delete secret
        client.secrets.delete_secret(secret_bundle.name)

        # get secret returns not found
        try:
            client.secrets.get_secret(secret_bundle.name, '')
        except Exception as ex:
            # TODO ClientRequestError doesn't surface message
            pass
            # if not hasattr(ex, 'message') or 'not found' not in ex.message.lower():
            #     raise ex

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_secret_list(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        client = VaultClient(vault.properties.vault_uri, self.settings.get_credentials())

        max_secrets = 2 #self.list_test_size
        expected = {}

        # create many secrets
        for x in range(0, max_secrets):
            secret_name = 'sec{}'.format(x)
            secret_value = self.get_resource_name('secVal{}'.format(x))
            secret_bundle = None
            error_count = 0
            while not secret_bundle:
                try:
                    secret_bundle = client.secrets.set_secret(secret_name, secret_value)
                    sid = secret_bundle.id
                    expected[sid] = secret_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list secrets
        result = list(client.secrets.list_secrets(max_secrets))
        self._validate_secret_list(result, expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_list_versions(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        client = VaultClient(vault.properties.vault_uri, self.settings.get_credentials())
        secret_name = self.get_resource_name('sec')
        secret_value = self.get_resource_name('secVal')

        max_secrets = 2 #self.list_test_size
        expected = {}

        # create many secret versions
        for x in range(0, max_secrets):
            secret_bundle = None
            error_count = 0
            while not secret_bundle:
                try:
                    secret_bundle = client.secrets.set_secret(secret_name, secret_value)
                    expected[secret_bundle.id] = secret_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list secret versions
        self._validate_secret_list(list(client.secrets.list_secret_versions(secret_name)), expected)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_backup_restore(self, vault, **kwargs):
        self.assertIsNotNone(vault)
        client = VaultClient(vault.properties.vault_uri, self.settings.get_credentials())
        secret_name = self.get_resource_name('secbak')
        secret_value = self.get_resource_name('secVal')

        # create secret
        created_bundle = client.secrets.set_secret(secret_name, secret_value)

        # backup secret
        secret_backup = client.secrets.backup_secret(created_bundle.name)

        # delete secret
        client.secrets.delete_secret(created_bundle.name)

        # restore secret
        self.assertEqual(created_bundle.attributes, client.secrets.restore_secret(secret_backup).attributes)

    @pytest.mark.skip("recover/purge not yet implemented")
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
            secrets[secret_name] = client.secrets.set_secret(secret_name, secret_value)

        # create secrets to purge
        for i in range(0, self.list_test_size):
            secret_name = self.get_resource_name('secprg{}'.format(str(i)))
            secret_value = self.get_resource_name('secval{}'.format((str(i))))
            secrets[secret_name] = client.secrets.set_secret(secret_name, secret_value)

        # delete all secrets
        for secret_name in secrets.keys():
            client.delete_secret(vault_uri, secret_name)

        if not self.is_playback():
            time.sleep(20)

        # validate all our deleted secrets are returned by get_deleted_secrets
        deleted = [KeyVaultId.parse_secret_id(s.id).name for s in client.get_deleted_secrets(vault_uri)]
        self.assertTrue(all(s in deleted for s in secrets.keys()))

        # recover select secrets
        for secret_name in [s for s in secrets.keys() if s.startswith('secrec')]:
            client.recover_deleted_secret(vault_uri, secret_name)

        # purge select secrets
        for secret_name in [s for s in secrets.keys() if s.startswith('secprg')]:
            client.purge_deleted_secret(vault_uri, secret_name)

        if not self.is_playback():
            time.sleep(20)

        # validate none of our deleted secrets are returned by get_deleted_secrets
        deleted = [KeyVaultId.parse_secret_id(s.id).name for s in client.get_deleted_secrets(vault_uri)]
        self.assertTrue(not any(s in deleted for s in secrets.keys()))

        # validate the recovered secrets
        expected = {k: v for k, v in secrets.items() if k.startswith('secrec')}
        actual = {k: client.secrets.get_secret(vault_uri, k, KeyVaultId.version_none) for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))