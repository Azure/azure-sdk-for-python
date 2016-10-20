# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import binascii
import datetime
import hashlib
import os
import time
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from azure.keyvault import \
    (create_object_id, parse_object_id,
     create_key_id, parse_key_id,
     create_secret_id, parse_secret_id,
     create_certificate_id, parse_certificate_id,
     create_certificate_operation_id, parse_certificate_operation_id,
     create_certificate_issuer_id, parse_certificate_issuer_id,
     HttpBearerChallenge)
from azure.keyvault.http_bearer_challenge_cache import \
    (_cache as challenge_cache, get_challenge_for_url, set_challenge_for_url, clear,
     remove_challenge_for_url)
from azure.keyvault.generated.models import \
    (CertificatePolicy, KeyProperties, SecretProperties, IssuerParameters,
     X509CertificateProperties, IssuerBundle, IssuerCredentials, OrganizationDetails,
     AdministratorDetails, Contact, Contacts, KeyVaultError)

from testutils.common_recordingtestcase import record
from tests.keyvault_testcase import HttpStatusCode, AzureKeyVaultTestCase

# TODO: Implement or remove as appropriate
#var series = KvUtils.series;
#var assertExactly = KvUtils.assertExactly;
#var compareObjects = KvUtils.compareObjects;
#var validateRsaKeyBundle = KvUtils.validateRsaKeyBundle;
#var validateKeyList = KvUtils.validateKeyList;
#var getTestKey = KvUtils.getTestKey;
#var setRsaParameters = KvUtils.setRsaParameters;
#var random = KvUtils.getRandom();

#KEY_VAULT_URI = os.environ.get('AZURE_KV_VAULT', 'https://sdktestvault0511.vault.azure.net')
KEY_VAULT_URI = "https://keyvault-tjp.vault.azure.net"

class KeyVaultCustomLayerTest(unittest.TestCase):

    def _get_expected(self, collection, vault, name, version=None):
        return {
            'vault': 'https://{}.vault.azure.net'.format(vault),
            'name': name,
            'version': version,
            'id': 'https://{}.vault.azure.net/{}/{}{}'.format(
                vault, collection, name,
                '' if not version else '/{}'.format(version)),
            'base_id': 'https://{}.vault.azure.net/{}/{}'.format(vault, collection, name)
        }

    def test_create_object_id(self):
        # success scenarios
        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = create_object_id('keys', 'https://myvault.vault.azure.net', ' mykey', None)
        self.assertEqual(res.__dict__, expected)

        res = create_object_id('keys', 'https://myvault.vault.azure.net', ' mykey', ' ')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = create_object_id(' keys ', 'https://myvault.vault.azure.net', ' mykey ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)
        
        # failure scenarios
        with self.assertRaises(TypeError):
            create_object_id('keys', 'https://myvault.vault.azure.net', ['stuff'], '')
        with self.assertRaises(ValueError):
            create_object_id('keys', 'https://myvault.vault.azure.net', ' ', '')
        with self.assertRaises(ValueError):
            create_object_id('keys', 'myvault.vault.azure.net', 'mykey', '')

    def test_parse_object_id(self):
        # success scenarios
        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey')
        self.assertEqual(res.__dict__, expected)

        # failure scenarios
        with self.assertRaises(ValueError):
            parse_object_id('secret', 'https://myvault.vault.azure.net/keys/mykey/abc123')
        with self.assertRaises(ValueError):
            parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey/abc123/extra')
        with self.assertRaises(ValueError):
            parse_object_id('keys', 'https://myvault.vault.azure.net')

    def test_create_key_id(self):
        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = create_key_id('https://myvault.vault.azure.net', ' mykey', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = create_key_id('https://myvault.vault.azure.net', ' mykey ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)

    def test_parse_key_id(self):
        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = parse_key_id('https://myvault.vault.azure.net/keys/mykey/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = parse_key_id('https://myvault.vault.azure.net/keys/mykey')
        self.assertEqual(res.__dict__, expected)

    def test_create_secret_id(self):
        expected = self._get_expected('secrets', 'myvault', 'mysecret')
        res = create_secret_id('https://myvault.vault.azure.net', ' mysecret', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('secrets', 'myvault', 'mysecret', 'abc123')
        res = create_secret_id('https://myvault.vault.azure.net', ' mysecret ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)

    def test_parse_secret_id(self):
        expected = self._get_expected('secrets', 'myvault', 'mysecret', 'abc123')
        res = parse_secret_id('https://myvault.vault.azure.net/secrets/mysecret/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('secrets', 'myvault', 'mysecret')
        res = parse_secret_id('https://myvault.vault.azure.net/secrets/mysecret')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert')
        res = create_certificate_id('https://myvault.vault.azure.net', ' mycert', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('certificates', 'myvault', 'mycert', 'abc123')
        res = create_certificate_id('https://myvault.vault.azure.net', 'mycert', ' abc123')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'abc123')
        res = parse_certificate_id('https://myvault.vault.azure.net/certificates/mycert/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('certificates', 'myvault', 'mycert')
        res = parse_certificate_id('https://myvault.vault.azure.net/certificates/mycert')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_operation_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'pending')
        expected['base_id'] = expected['id']
        expected['version'] = None
        res = create_certificate_operation_id('https://myvault.vault.azure.net', ' mycert')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_operation_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'pending')
        expected['base_id'] = expected['id']
        expected['version'] = None
        res = parse_certificate_operation_id('https://myvault.vault.azure.net/certificates/mycert/pending')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_issuer_id(self):
        expected = self._get_expected('certificates/issuers', 'myvault', 'myissuer')
        res = create_certificate_issuer_id('https://myvault.vault.azure.net', 'myissuer')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_issuer_id(self):
        expected = self._get_expected('certificates/issuers', 'myvault', 'myissuer')
        res = parse_certificate_issuer_id('https://myvault.vault.azure.net/certificates/issuers/myissuer')
        self.assertEqual(res.__dict__, expected)

    def test_bearer_challenge_cache(self):
        test_challenges = []
        for x in range(0, 3):
            challenge = MagicMock()
            challenge.source_authority = 'mytest{}.url.com'.format(x)
            url = 'https://mytest{}.url.com'.format(x)
            test_challenges.append({
                'url': url,
                'challenge': challenge
            })
            set_challenge_for_url(url, challenge)

        self.assertEqual(len(challenge_cache), 3)

        cached_challenge = get_challenge_for_url(test_challenges[1]['url'])
        self.assertTrue(cached_challenge.source_authority in test_challenges[1]['url'])

        # test remove
        remove_challenge_for_url(test_challenges[0]['url'])
        self.assertIsNone(get_challenge_for_url(test_challenges[0]['url']))

        # test clear
        self.assertEqual(len(challenge_cache), 2)
        clear()
        self.assertEqual(len(challenge_cache), 0)

        with self.assertRaises(ValueError):
            set_challenge_for_url('https://diffurl.com', test_challenges[0]['challenge'])

    def test_bearer_challenge(self):
        mock_bearer_challenge = '  Bearer authorization="https://login.windows.net/mock-id", resource="https://vault.azure.net"'

        self.assertTrue(HttpBearerChallenge.is_bearer_challenge(mock_bearer_challenge))
        self.assertFalse(HttpBearerChallenge.is_bearer_challenge('Some other string'))

        with self.assertRaises(ValueError):
            HttpBearerChallenge('https://test.uri.com', 'Non bearer string')

        with self.assertRaises(ValueError):
            HttpBearerChallenge('ftp://test.ftp.com', mock_bearer_challenge)

        challenge = HttpBearerChallenge('https://test.uri.com', mock_bearer_challenge)
        self.assertEqual(challenge.get_authorization_server(), 'https://login.windows.net/mock-id')
        self.assertEqual(challenge.get_resource(), 'https://vault.azure.net')
        self.assertEqual(challenge.get_value('resource'), 'https://vault.azure.net')
        self.assertEqual(challenge.get_scope(), '')

        mock_bearer_challenge = '  Bearer authorization_uri="https://login.windows.net/mock-id", resource="https://vault.azure.net"'
        challenge = HttpBearerChallenge('https://test.uri.com', mock_bearer_challenge)
        self.assertEqual(challenge.get_authorization_server(), 'https://login.windows.net/mock-id')

#class KeyVaultKeyTest(AzureKeyVaultTestCase):

#    def setUp(self):
#        super(KeyVaultKeyTest, self).setUp()
#        standard_vault_only = str(os.environ.get('AZURE_KV_STANDARD_VAULT_ONLY', False)).lower() \
#            == 'true'
#        self.client = KeyVaultClient(KeyVaultAuthentication(auth_callback))
#        self.key_name = 'pythonKey'
#        self.list_test_size = 2
#        if not self.is_playback():
#            self.create_resource_group()

#    def import_test_key(self, key_id, import_to_hardware=False):
#        key = {
#            'kty': 'RSA',
#            'keyOps': ['encrypt', 'decrypt', 'sign', 'verify', 'wrapKey', 'unwrapKey']
#        }
#        set_rsa_parameters(key, get_test_key(suite_util))
#        imported_key = self.client.import_key(key_id.vault, key_id.name, key, import_to_hardware)
#        validate_rsa_key_bundle(imported_key, KEY_VAULT_URI, key_id.name,
#                                'RSA-HSM' if import_to_hardware else 'RSA', key['keyOps'])
#        return imported_key

#    def cleanup_created_keys(self):
#        if not self.is_playback():
#            for key in self.client.get_keys(KEY_VAULT_URI):
#                id = KeyVaultClient.parse_key_id(key.kid)
#                self.client.delete_key(id.vault, id.name)

#    @record
#    def test_key_crud_operations(self):

#        created_bundle = None
#        key_id = None

#        def create_key(self):
#            created_bundle = self.client.create_key(KEY_VAULT_URI, self.key_name, 'RSA')
#            validate_rsa_key_bundle(created_bundle, KEY_VAULT_URI, self.key_name, 'RSA')
#            key_id = KeyVaultClient.parse_key_id(created_bundle.key.kid)

#        def get_key_without_version(self):
#            retrieved_bundle = self.client.get_key(key_id.base_id)
#            compare_objects(created_bundle, retrieved_bundle)

#        def get_key_with_version(self):
#            retrieved_bundle = self.client.get_key(key_id.id)
#            compare_objects(created_bundle, retrieved_bundle)

#        def update_key(self, key_uri):
#            updating_bundle = clone(created_bundle)
#            updating_bundle.attributes.expires = datetime('2050-02-02T08:00:00.000Z')
#            updating_bundle.key.key_ops = ['encrypt', 'decrypt']
#            updating_bundle.tags = { foo: binascii.b2a_hex(os.urandom(100)) }
#            key_bundle = self.client.update_key(
#                key_uri, updating_bundle.key.key_ops, updating_bundle.attributes, updating_bundle.tags)
#            updating_bundle.attributes.updated = key_bundle.attributes.updated
#            compare_objects(updating_bundle, key_bundle)
#            created_bundle = key_bundle

#        def update_key_without_version(self):
#            return update_key(key_id.base_id)

#        def update_key_with_version(self):
#            return update_key(key_id.id)

#        def delete_key(self):
#            key_bundle = self.client.delete_key(key_id.vault, key_id.name)
#            compare_objects(created_bundle, key_bundle)

#        def get_key_returns_not_found(self):
#            try:
#                self.client.get_key(key_id.base_id)
#            except Exception as ex:
#                # TODO:         if (!err || !err.code || err.code !== 'KeyNotFound' || !err.statusCode || err.statusCode !== 404) {
#                #            throw new Error('Unexpected error object: ' + JSON.stringify(err, null, ' '));
#                print(ex)

#        self.create_key()
#        self.get_key_without_version()
#        self.get_key_with_version()
#        self.update_key_without_version()
#        self.update_key_with_version()
#        self.delete_key()
#        self.get_key_returns_not_found()

#    @record
#    def test_key_import(self):

#        def import_to_software(self):
#            import_test_key(False)

#        def import_to_hardware(self):
#            import_test_key(not self.standard_vault_only)

#        self.import_to_software()
#        self.import_to_hardware()

#    @record
#    def test_key_list(self):
        
#        max_keys = self.list_test_size
#        expected = {}

#        def create_many_keys():
#            for x in range(0, max_keys):
#                key_name = '{}{}'.format(self.key_name, x + 1)
#                key_bundle = None
#                error_count = 0
#                while not key_bundle:
#                    try:
#                        key_bundle = self.client.create_key(KEY_VAULT_URI, key_name, 'RSA')
#                        kid = KeyVaultClient.parse_key_id(key_bundle.key.kid).base_id
#                        expected[kid] = key_bundle.attributes
#                    except Exception as ex: # TODO: check for err.code == 'Throttled'
#                        error_count += 1
#                        time.sleep(2.5 * error_count)
#                        continue

#        def list_keys(self):
#            current_result = None
#            result = list(self.client.get_keys(KEY_VAULT_URI, self.list_test_size))
#            self.assertTrue(len(result) >= 0 and len(result) < self.list_test_size)
#            validate_key_list(result, expected)
#            current_result = result

#        self.create_many_keys()
#        self.list_keys()

#    @record
#    def test_key_list_versions(self):
        
#        max_keys = self.list_test_size
#        key_name = '{}-versioned'.format(self.key_name)
#        expected = {}

#        def create_many_key_versions(self):
#            for x in range(0, max_keys):                
#                key_bundle = None
#                error_count = 0
#                while not key_bundle:
#                    try:
#                        key_bundle = self.client.create_key(KEY_VAULT_URI, key_name, 'RSA')
#                        kid = KeyVaultClient.parse_key_id(key_bundle.key.kid).base_id
#                        expected[kid] = key_bundle.attributes
#                    except Exception as ex: # TODO: check for err.code == 'Throttled'
#                        error_count += 1
#                        time.sleep(2.5 * error_count)
#                        continue

#        def list_key_versions(self):
#            current_result = None
#            result = list(self.client.get_key_versions(KEY_VAULT_URI, key_name))
#            validate_key_list(result, expected)
#            current_result = result

#        self.create_many_key_versions()
#        self.list_key_versions()

#    @record
#    def test_key_backup_and_restore(self):
        
#        key_name = '{}forBkp'.format(self.key_name)
#        created_bundle = None
#        key_id = None
#        key_backup = None

#        def create_key(self):
#            created_bundle = self.client.create_key(KEY_VAULT_URI, key_name, 'RSA')
#            key_id = KeyVaultClient.parse_key_id(created_bundle.key.kid)

#        def backup_key(self):
#            key_backup = self.client.backup_key(key_id.vault, key_id.name).value

#        def delete_key(self):
#            self.client.delete_key(key_id.vault, key_id.name)

#        def restore_key(self):
#            restored_bundle = self.client.restore_key(KEY_VAULT_URI, key_backup)
#            compare_objects(created_bundle, restored_bundle)

#        self.create_key()
#        self.backup_key()
#        self.delete_key()
#        self.restore_key()

#    @record
#    def test_key_encrypt_and_decrypt(self):

#        key_id = KeyVaultClient.create_key_id(KEY_VAULT_URI, self.key_name)
#        plain_text = binascii.b2a_hex(os.urandom(200))
#        cipher_text = None

#        def import_key(self):
#            imported_key = import_test_key(key_id)
#            key_id = KeyVaultClient.parse_key_id(imported_key.key.kid)

#        def encrypt_with_version(self):
#            result = self.client.encrypt(key_id.base_id, 'RSA-OAEP', plain_text)
#            cipher_text = result.result

#        def decrypt_with_version(self):
#            result = self.client.decrypt(key_id.base_id, 'RSA-OAEP', cipher_text)
#            compare_objects(plain_text, result.result)


#        def encrypt_with_version(self):
#            result = self.client.encrypt(key_id.id, 'RSA-OAEP', plain_text)
#            cipher_text = result.result

#        def decrypt_with_version(self):
#            result = self.client.decrypt(key_id.id, 'RSA-OAEP', cipher_text)
#            compare_objects(plain_text, result.result)

#        self.import_key()
#        self.encrypt_without_version()
#        self.decrypt_without_version()
#        self.encrypt_with_version()
#        self.decrypt_with_version()

#    @record
#    def test_key_wrap_and_unwrap(self):

#        key_id = KeyVaultClient.create_key_id(KEY_VAULT_URI, self.key_name)
#        plain_text = binascii.b2a_hex(os.urandom(200))
#        cipher_text = None

#        def import_key(self):
#            imported_key = self.client.import_test_key(key_id)
#            key_id = KeyVaultClient.parse_key_id(imported_key.key.kid)

#        def wrap_without_version(self):
#            result = self.client.wrap_key(key_id.base_id, 'RSA-OAEP', plain_text)
#            cipher_text = result.result

#        def unwrap_without_version(self):
#            result = self.client.unwrap_key(key_id.base_id, 'RSA-OAEP', cipher_text)
#            compare_objects(plain_text, result.result)

#        def wrap_with_version(self):
#            result = self.client.wrap_key(key_id.id, 'RSA-OAEP', plain_text)
#            cipher_text = result.result

#        def unwrap_with_version(self):
#            result = self.client.unwrap_key(key_id.id, 'RSA-OAEP', cipher_text)
#            compare_objects(plain_text, result.result)

#        self.import_key()
#        self.wrap_without_version()
#        self.unwrap_without_version()
#        self.wrap_with_version()
#        self.unwrap_with_version()

#    @record
#    def test_key_sign_and_verify(self):

#        key_id = KeyVaultClient.create_key_id(KEY_VAULT_URI, self.key_name)
#        plain_text = binascii.b2a_hex(os.urandom(200))
#        md = hashlib.sha256()
#        md.update(plainText);
#        digest = md.digest();
#        signature = None

#        def import_key(self):
#            imported_key = import_test_key(key_id)
#            key_id = KeyVaultClient.parse_key_id(imported_key.key.kid)

#        def sign_without_version(self):
#            signature = self.client.sign(key_id.base_id, 'RS256', digest).result

#        def verify_without_version(self):
#            result = self.client.verify(key_id.base_id, 'RS256', digest, signature)
#            self.assertTrue(result.value)

#        def sign_with_version(self):
#            signature = self.client.sign(key_id.base_id, 'RS256', digest).result

#        def verify_with_version(self):
#            result = self.client.verify(key_id.id, 'RS256', digest, signature)
#            self.assertTrue(result.value)

#        self.import_key()
#        self.sign_without_version()
#        self.verify_without_version()
#        self.sign_with_version()
#        self.verify_with_version()

#class KeyVaultSecretTest(AzureKeyVaultTestCase):

#    def setUp(self):
#        super(KeyVaultSecretTest, self).setUp()
#        self.client = KeyVaultClient(KeyVaultAuthentication(auth_callback))
#        self.secret_name = 'pythonSecret'
#        self.secret_value = 'Pa$$w0rd'
#        self.list_test_size = 2
#        if not self.is_playback():
#            self.create_resource_group()

#    def cleanup_created_secrets(self):
#        if not self.is_playback():
#            for secret in self.client.get_secrets(KEY_VAULT_URI):
#                id = KeyVaultClient.parse_secret_id(secret.id)
#                self.client.delete_secret(id.vault, id.name)

#    @record
#    def test_secret_crud_operations(self):
        
#        created_bundle = None
#        secret_id = None

#        def create_secret(self):
#            secret_bundle = self.client.set_secret(KEY_VAULT_URI, self.secret_name, self.secret_value)
#            validate_secret_bundle(secret_bundle, KEY_VAULT_URI, self.secret_name, self.secret_value)
#            created_bundle = secret_bundle
#            secret_id = KeyVaultClient.parse_secret_id(created_bundle.id)

#        def get_secret_without_version(self):
#            secret_bundle = self.client.get_secret(secret_id.base_id)
#            compare_objects(created_bundle, secret_bundle)

#        def get_secret_with_version(self):
#            secret_bundle = self.client.get_secret(secret_id.id)
#            compare_objects(created_bundle, secret_bundle)

#        def update_secret(self, secret_uri):
#            updating_bundle = clone(created_bundle)
#            updating_bundle.content_type = 'text/plain'
#            updating_bundle.attributes.expires = datetime('2050-02-02T08:00:00.000Z')
#            updating_bundle.tags = { foo: binascii.b2a_hex(os.urandom(100)) }
#            secret_bundle = self.client.update_secret(
#                secret_uri, updating_bundle.content_type, updating_bundle.attributes,
#                updating_bundle.tags)
#            del updating_bundle.value
#            updating_bundle.attributes.updated = secret_bundle.attributes.updated
#            compare_objects(updating_bundle, secret_bundle)
#            created_bundle = secret_bundle

#        def update_secret_without_version(self):
#            return update_secret(secret_id.base_id)

#        def update_secret_with_version(self):
#            return update_secret(secret_id.id)

#        def delete_secret(self):
#            secret_bundle = self.client.delete_secret(secret_id.vault, secret_id.name)
#            compare_objects(created_bundle, secret_bundle)

#        def get_secret_returns_not_found(self):
#            try:
#                self.client.get_secret(secret_id.base_id)
#            except Exception as ex:
#                # TODO:         if (!err || !err.code || err.code !== 'KeyNotFound' || !err.statusCode || err.statusCode !== 404) {
#                #            throw new Error('Unexpected error object: ' + JSON.stringify(err, null, ' '));
#                print(ex)

#        self.create_secret()
#        self.get_secret_without_version()
#        self.get_secret_with_version()
#        self.update_secret_without_version()
#        self.update_secret_with_version()
#        self.delete_secret()
#        self.get_secret_returns_not_found()

#    @record
#    def test_secret_list(self):

#        max_secrets = self.list_test_size
#        expected = {}

#        def create_many_secrets():
#            for x in range(0, max_secrets):
#                secret_name = '{}{}'.format(self.secret_name, x + 1)
#                secret_bundle = None
#                error_count = 0
#                while not secret_bundle:
#                    try:
#                        secret_bundle = self.client.create_secret(KEY_VAULT_URI, secret_name, self.secret_value)
#                        sid = KeyVaultClient.parse_secret_id(secret_bundle.id).base_id
#                        expected[sid] = secret_bundle.attributes
#                    except Exception as ex: # TODO: check for err.code == 'Throttled'
#                        error_count += 1
#                        time.sleep(2.5 * error_count)
#                        continue

#        def list_secrets():
#            current_result = None
#            result = list(self.client.get_secrets(KEY_VAULT_URI, self.list_test_size))
#            self.assertTrue(len(result) >= 0 and len(result) < self.list_test_size)
#            validate_secret_list(result, expected)
#            current_result = result

#        create_many_secrets()
#        list_secrets()

#    @record
#    def test_secret_list_versions(self):
        
#        max_secrets = self.list_test_size
#        secret_name = '{}-versioned'.format(self.secret_name)
#        expected = {}

#        def create_many_secret_versions(self):
#            for x in range(0, max_secrets):
#                secret_bundle = None
#                error_count = 0
#                while not secret_bundle:
#                    try:
#                        secret_bundle = self.client.create_secret(KEY_VAULT_URI, secret_name, self.secret_value)
#                        sid = KeyVaultClient.parse_secret_id(secret_bundle.id).base_id
#                        expected[sid] = secret_bundle.attributes
#                    except Exception as ex: # TODO: check for err.code == 'Throttled'
#                        error_count += 1
#                        time.sleep(2.5 * error_count)
#                        continue

#        def list_secret_versions(self):
#            current_result = None
#            result = list(self.client.get_secret_versions(KEY_VAULT_URI, secret_name))
#            validate_secret_list(result, expected)
#            current_result = result

#        self.cscreate_many_secret_versions()
#        self.list_secret_versions()

#class KeyVaultCertificateTest(AzureKeyVaultTestCase):

#    def setUp(self):
#        super(KeyVaultCertificateTest, self).setUp()
#        self.client = KeyVaultClient(KeyVaultAuthentication(auth_callback))
#        self.cert_name = 'pythonCertificate'
#        self.issuer_name = 'pythonIssuer'
#        self.list_test_size = 2
#        if not self.is_playback():
#            self.create_resource_group()

#    def import_common_certificate(self, cert_name):
#        cert_content = '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'
#        cert_password = '123'
#        cert_policy = CertificatePolicy(
#            KeyProperties(True, 'RSA', 2048, False),
#            SecretProperties('application/x-pkcs12'))
#        return (
#            self.client.import_certificate(KEY_VAULT_URI, cert_name, cert_content, cert_password, cert_policy),
#            cert_policy
#        )

#    def cleanup_created_certificates(self):
#        if not self.is_playback():
#            for cert in self.client.get_certificates(KEY_VAULT_URI):
#                id = KeyVaultClient.parse_certificate_id(cert.id)
#                self.client.delete_certificate(id.vault, id.name)

#    @record
#    def test_certificate_crud_operations(self):

#        created_bundle = None
#        cert_id = None
#        cert_policy = CertificatePolicy(
#            KeyProperties(True, 'RSA', 2048, False),
#            SecretProperties('application/x-pkcs12'),
#            issuer_parameters=IssuerParameters('Self'),
#            x509_certificate_properties=X509CertificateProperties(
#                subject='CN=*.microsoft.com',
#                subject_alternative_names=['onedrive.microsoft.com', 'xbox.microsoft.com'],
#                validate_in_months=24
#            ))

#        def create_certificate():
#            interval_time = 5 if not self.is_playback() else 0
#            cert_operation = self.client.create_certificate(KEY_VAULT_URI, self.cert_name, cert_policy)
#            while True:
#                pending_cert = self.client.get_certificate_operation(KEY_VAULT_URI, self.cert_name)
#                validate_certificate_opeartion(pending_cert, KEY_VAULT_URI, self.cert_name, cert_policy)
#                if pending_cert.status.lower() == 'completed':
#                    cert_id = pending_cert.target
#                    break
#                elif pending_cert.status.lower() != 'inprogress':
#                    raise Exception('Unknown status code for pending certificate: {}'.format(pending_cert))
#                time.sleep(interval_time)

#        def get_certificate():
#            cert_bundle = self.client.get_certificate(cert_id.base_id)
#            validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

#            # get certificate as secret
#            secret_bundle = self.client.get_secret(cert_bundle.sid)

#        def update_certificate():
#            cert_policy.tags = {'tag1': 'value1'}
#            cert_bundle = self.client.update_certificate(cert_id, cert_policy)
#            validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

#        def delete_certificate():
#            cert_bundle = self.client.delete_certificate(KEY_VAULT_URI, self.cert_name)
#            validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

#        def get_certificate_returns_not_found():
#            try:
#                self.client.get_certificate(cert_id)
#            except Exception as ex:
#                # TODO:         if (!err || !err.code || err.code !== 'KeyNotFound' || !err.statusCode || err.statusCode !== 404) {
#                #            throw new Error('Unexpected error object: ' + JSON.stringify(err, null, ' '));
#                print(ex)

#        create_certificate()
#        update_certificate()
#        get_certificate()
#        delete_certificate()
#        get_certificate_returns_not_found()

#    @record
#    def test_certificate_import(self):

#        cert_name = 'pythonImportCert'

#        def import_certificate(self):
#            (cert_bundle, cert_policy) = import_common_certificate(cert_name)
#            validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, cert_name, cert_policy)

#        self.import_certificate()

#    @record
#    def test_certificate_list(self):

#        max_certificates = self.list_test_size
#        expected = {}

#        def import_some_certificates():
#            for x in range(0, max_certificates):
#                cert_name = '{}{}'.format(self.cert_name, x + 1)
#                cert_bundle = None
#                error_count = 0
#                while not cert_bundle:
#                    try:
#                        cert_bundle = import_common_certificate(cert_name)
#                        cid = KeyVaultClient.parse_certificate_id(cert_bundle.id).base_id
#                        expected[cid] = cert_bundle.attributes
#                    except Exception as ex: # TODO: check for err.code == 'Throttled'
#                        error_count += 1
#                        time.sleep(2.5 * error_count)
#                        continue

#        def list_certificates(self):
#            result = list(self.client.get_certificates(KEY_VAULT_URI, self.list_test_size))
#            self.assertTrue(len(result) >= 0 and len(result) < self.list_test_size)
#            validate_certificate_list(result, expected)

#        self.import_some_certificates()
#        self.list_certificates()

#    @record
#    def test_certificate_list_versions(self):

#        max_certificates = self.list_test_size
#        cert_name = '{}-versioned'.format(self.cert_name)
#        expected = {}

#        def import_same_certificates(self):
#            for x in range(0, max_certificates):
#                cert_bundle = None
#                error_count = 0
#                while not cert_bundle:
#                    try:
#                        cert_bundle = import_common_certificate(cert_name)
#                        cid = KeyVaultClient.parse_certificate_id(cert_bundle.id).base_id
#                        expected[cid] = cert_bundle.attributes
#                    except Exception as ex: # TODO: check for err.code == 'Throttled'
#                        error_count += 1
#                        time.sleep(2.5 * error_count)
#                        continue

#        def list_certificate_versions(self):
#            current_result = None
#            result = list(self.client.get_certificate_versions(KEY_VAULT_URI, cert_name))
#            validate_certificate_list(result, expected)
#            current_result = result

#        self.import_same_certificates()
#        self.list_certificate_versions()

#    @record
#    def test_certificate_crud_issuer(self):

#        issuer_name = 'pythonIssuer'
#        issuer_credentials = IssuerCredentials('keyvaultuser', 'password')
#        organization_details = OrganizationDetails(
#            admin_details=[AdministrationDetails('Jane', 'Doe', 'admin@contoso.com', '4256666666')])

#        def create_certificate_issuer(self):
#            issuer_bundle = self.client.set_certificate_issuer(KEY_VAULT_URI, issuer_name, 'test', issuer_credentials, organization_details)
#            validate_issuer_bundle(issuer_bundle, KEY_VAULT_URI, issuer_name, 'test', issuer_credentials, organization_details)

#        def get_certificate_issuer(self):
#            issuer_bundle = self.client.get_certificate_issuer(KEY_VAULT_URI, issuer_name)
#            validate_issuer_bundle(issuer_bundle, KEY_VAULT_URI, issuer_name, 'test', issuer_credentials, organization_details)

#        def update_certificate_issuer(self):
#            new_credentials = IssuerCredentials('xboxuser', 'security')
#            new_org_details = OrganizationDetails(
#                admin_details=[AdministrationDetails('Jane II', 'Doe', 'admin@contoso.com', '1111111111')])
#            issuer_bundle = self.client.update_certificate_issuer(KEY_VAULT_URI, issuer_name, 'test', new_credentials, new_org_details)
#            validate_issuer_bundle(issuer_bundle, KEY_VAULT_URI, issuer_name, 'test', new_credentials, new_org_details)

#        def delete_certificate_issuer(self):
#            self.client.delete_certificate_issuer(KEY_VAULT_URI, issuer_name)

#        def get_certificate_issuer_returns_not_found(self):
#            try:
#                self.client.get_certificate_issuer(KEY_VAULT_URI, issuer_name)
#            except Exception as ex:
#                # TODO:         if (!err || !err.code || err.code !== 'KeyNotFound' || !err.statusCode || err.statusCode !== 404) {
#                #            throw new Error('Unexpected error object: ' + JSON.stringify(err, null, ' '));
#                print(ex)

#        self.create_certificate_issuer()
#        self.get_certificate_issuer()
#        self.update_certificate_issuer()
#        self.delete_certificate_issuer()
#        self.get_certificate_issuer_returns_not_found()    

#    @record
#    def test_certificate_list_issuers(self):

#        max_issuers = self.list_test_size
#        expected = {}

#        def create_some_certificate_issuers(self):
#            for x in range(0, max_issuers):
#                issuer_name = 'pythonIssuer{}'.format(x + 1)
#                issuer_credentials = IssuerCredentials('keyvaultuser', 'password')
#                organization_details = OrganizationDetails(
#                    admin_details=[AdministrationDetails('Jane', 'Doe', 'admin@contoso.com', '4256666666')])
#                error_count = 0
#                issuer_bundle = None
#                while not issuer_bundle:
#                    try:
#                        issuer_bundle = self.client.set_certificate_issuer(KEY_VAULT_URI, issuer_name, 'test', issuer_credentials, organization_details)
#                        expected[issuer_bundle.id] = issuer_bundle.provider
#                    except Exception as ex: # TODO: check for err.code == 'Throttled'
#                        error_count += 1
#                        time.sleep(2.5 * error_count)
#                        continue

#        def list_certificate_issuers(self):
#            result = list(self.client.get_certificate_issuers(KEY_VAULT_URI, self.list_test_size))
#            self.assertTrue(len(result) >= 0 and len(result) < self.list_test_size)
#            validate_certificate_issuers_list(result, expected)

#        self.create_some_certificate_issuers()
#        self.list_certificate_issuers()

#    @record
#    def test_certificate_async_request_cancellation_and_deletion(self):
        
#        cert_name = 'asyncCanceledDeletedCert'
#        cert_policy = CertificatePolicy(
#            KeyProperties(True, 'RSA', 2048, False),
#            SecretProperties('application/x-pkcs12'),
#            issuer_parameters=IssuerParameters('Self'),
#            x509_certificate_properties=X509CertificateProperties(
#                subject='CN=*.microsoft.com',
#                subject_alternative_names=['onedrive.microsoft.com', 'xbox.microsoft.com'],
#                validity_in_months=24
#            ))
        
#        def create_certificate(self):
#            self.client.create_certificate(KEY_VAULT_URI, cert_name, cert_policy)

#        def cancel_certificate_operation(self):
#            cancel_operation = self.client.update_certificate_operation(KEY_VAULT_URI, cert_name, True)
#            self.assertTrue(hasattr(cancel_operation, 'cancellation_requested'))
#            self.assertTrue(cancel_operation.cancellation_requested)
#            validate_certificate_operation(cancel_operation, KEY_VAULT_URI, cert_name, cert_policy)

#            retrieved_operation = self.client.get_certificate_operation(KEY_VAULT_URI, cert_name)
#            self.assertTrue(hasattr(retrieved_operation, 'cancellation_requested'))
#            self.assertTrue(retrieved_operation.cancellation_requested)
#            validate_certificate_operation(retrieved_operation, KEY_VAULT_URI, cert_name, cert_policy)

#        def delete_certificate_operation(self):
#            deleted_operation = self.client.delete_certificate_operation(KEY_VAULT_URI, cert_name)
#            self.assertIsNotNone(deleted_operation)
#            validate_certificate_operation(deleted_operation, KEY_VAULT_URI, cert_name, cert_policy)

#            try:
#                self.client.get_certificate_operation(KEY_VAULT_URI, cert_name)
#            except Exception as ex:
##            if (!err || !err.code || err.code !== 'PendingCertificateNotFound' || !err.statusCode || err.statusCode !== 404) {
##              throw new Error('Unexpected error object: ' + JSON.stringify(err, null, ' '));
##            }
#                pass

#        def delete_cancelled_certificate_operation(self):
#            self.client.delete_certificate(KEY_VAULT_URI, cert_name)

#        self.create_certificate()
#        self.cancel_certificate_operation()
#        self.delete_certificate_operation()
#        self.delete_cancelled_certificate_operation()

#    @record
#    def test_certificate_crud_contacts(self):
        
#        contact_list = Contacts([
#            Contact('admin@contoso.com', 'John Doe', '1111111111'),
#            Contact('admin2@contoso.com', 'John Doe2', '2222222222')
#        ])

#        def create_certificate_contacts(self):
#            contacts = self.client.set_certificate_contacts(KEY_VAULT_URI, contact_list)
#            validate_certificate_contacts(contacts, KEY_VAULT_URI, contact_list)

#        def get_certificate_contacts(self):
#            contacts = self.client.get_certificate_contacts(KEY_VAULT_URI)
#            validate_certificate_contacts(contacts, KEY_VAULT_URI, contact_list)

#        def delete_certificate_contacts(self):
#            contacts = self.client.delete_certificate_contacts(KEY_VAULT_URI)
#            validate_certificate_contacts(contacts, KEY_VAULT_URI, contact_list)

#        def get_certificate_contacts_returns_not_found(self):
#            try:
#                contacts = self.client.get_certificate_contacts(KEY_VAULT_URI)
#            except Exception as ex:
##          if (!err || !err.code || err.code !== 'ContactsNotFound' || !err.statusCode || err.statusCode !== 404) {
##            throw new Error('Unexpected error object: ' + JSON.stringify(err, null, ' '));
##          }
#                pass

#        self.create_certificate_contacts()
#        self.get_certificate_contacts()
#        self.delete_certificate_contacts()
#        self.get_certificate_contacts_returns_not_found()

#    @record
#    def test_certificate_policy(self):

#        cert_name = 'policyCertificate'

#        def get_certificate_policy(self):
#            (cert_bundle, cert_policy) = import_common_certificate(cert_name)
#            retrieved_policy = self.client.get_certificate_policy(KEY_VAULT_URI, cert_name)
#            self.assertIsNotNone(retrieved_policy)

#        def update_certificate_policy(self):
#            cert_policy = CertificatePolicy(
#                KeyProperties(True, 'RSA', 2048, False),
#                SecretProperties('application/x-pkcs12'),
#                issuer_parameters=IssuerParameters('Self')
#            )

#            (cert_bundle, cert_policy) = self.client.update_certificate_policy(KEY_VAULT_URI, cert_name, cert_policy)
#            updated_cert_policy = self.client.get_certificate_policy(KEY_VAULT_URI, cert_name)
#            self.assertIsNotNone(updated_cert_policy)

#        self.get_certificate_policy()
#        self.update_certificate_policy()

#    @record
#    def test_certificate_manual_enrolled(self):

#        cert_name = 'unknownIssuerCert'
#        cert_policy = CertificatePolicy(
#            KeyProperties(True, 'RSA', 2048, False),
#            SecretProperties('application/x-pkcs12'),
#            issuer_parameters=IssuerParameters('Unknown'),
#            x509_certificate_properties=X509CertificateProperties(
#                subject='CN=*.microsoft.com',
#                subject_alternative_names=['onedrive.microsoft.com', 'xbox.microsoft.com'],
#                validate_in_months=24
#            ))

#        def get_pending_certificate_signing_request(self):

#            cert_operation = self.client.create_certificate(KEY_VAULT_URI, cert_name, cert_policy)
#            pending_version_csr = self.client.get_pending_certificate_signing_request(KEY_VAULT_URI, cert_name)
#            try:
#                self.assertEqual(cert_operation.csr, pending_version_csr)
#            except Exception as ex:
#                pass
#            finally:
#                self.client.delete_certificate(KEY_VAULT_URI, cert_name)

#        self.get_pending_certificate_signing_request()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()