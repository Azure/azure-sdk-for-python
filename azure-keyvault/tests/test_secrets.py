from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase
from azure.keyvault.secrets import SecretClient

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

    def _get_keyvault_credentials(self):
        creds = self.settings.get_keyvault_credentials()
        return creds

    def _assert_secrets_equal(self, s1, s2):
        self.assertEqual(s1.value, s2.value)
        self.assertEqual(s1.id , s2.id)
        self.assertEqual(s1.content_type, s2.content_type)
        self.assertEqual(s1.attributes.enabled, s2.attributes.enabled)
        self.assertEqual(s1.attributes.not_before, s2.attributes.not_before)
        self.assertEqual(s1.attributes.expires, s2.attributes.expires)
        self.assertEqual(s1.attributes.created, s2.attributes.created)
        self.assertEqual(s1.attributes.updated, s2.attributes.updated)
        self.assertEqual(s1.attributes.recovery_level, s2.attributes.recovery_level)
        self.assertEqual(s1.key_id, s2.key_id)

    @ResourceGroupPreparer()
    @KeyVaultPreparer()
    def test_secret_crud_operations(self, vault, **kwargs):
        vault_url = vault.properties.vault_uri
        print(vault_url)
        secrets = SecretClient(credentials=self._get_keyvault_credentials(), vault_url=vault_url)
        s1 = secrets.set_secret('crudsecret1', 'crudsecret1value')
        s2 = secrets.get_secret('crudsecret1')
        self._assert_secrets_equal(s1, s2)

        # list secrets
        for i in range(10):
            secrets.set_secret('listsecret' + str(i), 'some_value')

        list_secrets = [s for s in secrets.list_secrets() if s.name.startswith('listsecret')]

        self.assertTrue(len(list_secrets) == 10)


