# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import binascii
import codecs
import copy
from dateutil import parser as date_parse
import hashlib
import os
import time
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from azure.keyvault import KeyVaultId
from azure.keyvault import HttpBearerChallenge
from azure.keyvault import HttpBearerChallengeCache
from azure.keyvault.generated.models import \
    (CertificatePolicy, KeyProperties, SecretProperties, IssuerParameters,
     X509CertificateProperties, IssuerBundle, IssuerCredentials, OrganizationDetails,
     AdministratorDetails, Contact, KeyVaultError, SubjectAlternativeNames, JsonWebKey)

from testutils.common_recordingtestcase import record
from tests.keyvault_testcase import HttpStatusCode, AzureKeyVaultTestCase

# To record tests or run them live, you should create a keyvault accessible within your
# subscription using the following CLI commands:
#
# az keyvault create -g {resource-group}  -n python-sdk-test-keyvault --sku premium -l westus
# az keyvault set-policy -g {resource-group}  -n python-sdk-test-keyvault --object-id {obtain from keyvault create response} --spn {tenantId from keyvault create response} --key-permissions all
#
# You must use a premium keyvault to allow importing keys to hardware and you must update the
# key permissions to 'all' to permit testing of encrypt/decrypt/wrap/unwrap/sign/verify commands

KEY_VAULT_URI = os.environ.get('AZURE_KV_VAULT', 'https://python-sdk-test-keyvault.vault.azure.net')

class KeyVaultCustomLayerTest(unittest.TestCase):

    def _get_expected(self, collection, vault, name, version=None):
        return {
            'vault': 'https://{}.vault.azure.net'.format(vault),
            'collection': collection,
            'name': name,
            'version': version or KeyVaultId.version_none
        }

    def test_create_object_id(self):
        # success scenarios
        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = KeyVaultId.create_object_id('keys', 'https://myvault.vault.azure.net', ' mykey', None)
        self.assertEqual(res.__dict__, expected)

        res = KeyVaultId.create_object_id('keys', 'https://myvault.vault.azure.net', ' mykey', ' ')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = KeyVaultId.create_object_id(' keys ', 'https://myvault.vault.azure.net', ' mykey ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)
        
        # failure scenarios
        with self.assertRaises(TypeError):
            KeyVaultId.create_object_id('keys', 'https://myvault.vault.azure.net', ['stuff'], '')
        with self.assertRaises(ValueError):
            KeyVaultId.create_object_id('keys', 'https://myvault.vault.azure.net', ' ', '')
        with self.assertRaises(ValueError):
            KeyVaultId.create_object_id('keys', 'myvault.vault.azure.net', 'mykey', '')

    def test_parse_object_id(self):
        # success scenarios
        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = KeyVaultId.parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = KeyVaultId.parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey')
        self.assertEqual(res.__dict__, expected)

        # failure scenarios
        with self.assertRaises(ValueError):
            KeyVaultId.parse_object_id('secret', 'https://myvault.vault.azure.net/keys/mykey/abc123')
        with self.assertRaises(ValueError):
            KeyVaultId.parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey/abc123/extra')
        with self.assertRaises(ValueError):
            KeyVaultId.parse_object_id('keys', 'https://myvault.vault.azure.net')

    def test_create_key_id(self):
        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = KeyVaultId.create_key_id('https://myvault.vault.azure.net', ' mykey', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = KeyVaultId.create_key_id('https://myvault.vault.azure.net', ' mykey ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)

    def test_parse_key_id(self):
        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = KeyVaultId.parse_key_id('https://myvault.vault.azure.net/keys/mykey/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = KeyVaultId.parse_key_id('https://myvault.vault.azure.net/keys/mykey')
        self.assertEqual(res.__dict__, expected)

    def test_create_secret_id(self):
        expected = self._get_expected('secrets', 'myvault', 'mysecret')
        res = KeyVaultId.create_secret_id('https://myvault.vault.azure.net', ' mysecret', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('secrets', 'myvault', 'mysecret', 'abc123')
        res = KeyVaultId.create_secret_id('https://myvault.vault.azure.net', ' mysecret ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)

    def test_parse_secret_id(self):
        expected = self._get_expected('secrets', 'myvault', 'mysecret', 'abc123')
        res = KeyVaultId.parse_secret_id('https://myvault.vault.azure.net/secrets/mysecret/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('secrets', 'myvault', 'mysecret')
        res = KeyVaultId.parse_secret_id('https://myvault.vault.azure.net/secrets/mysecret')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert')
        res = KeyVaultId.create_certificate_id('https://myvault.vault.azure.net', ' mycert', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('certificates', 'myvault', 'mycert', 'abc123')
        res = KeyVaultId.create_certificate_id('https://myvault.vault.azure.net', 'mycert', ' abc123')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'abc123')
        res = KeyVaultId.parse_certificate_id('https://myvault.vault.azure.net/certificates/mycert/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('certificates', 'myvault', 'mycert')
        res = KeyVaultId.parse_certificate_id('https://myvault.vault.azure.net/certificates/mycert')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_operation_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'pending')
        res = KeyVaultId.create_certificate_operation_id('https://myvault.vault.azure.net', ' mycert')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_operation_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'pending')
        res = KeyVaultId.parse_certificate_operation_id('https://myvault.vault.azure.net/certificates/mycert/pending')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_issuer_id(self):
        expected = self._get_expected('certificates/issuers', 'myvault', 'myissuer')
        res = KeyVaultId.create_certificate_issuer_id('https://myvault.vault.azure.net', 'myissuer')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_issuer_id(self):
        expected = self._get_expected('certificates/issuers', 'myvault', 'myissuer')
        res = KeyVaultId.parse_certificate_issuer_id('https://myvault.vault.azure.net/certificates/issuers/myissuer')
        self.assertEqual(res.__dict__, expected)

    def test_bearer_challenge_cache(self):
        test_challenges = []
        HttpBearerChallengeCache.clear()
        for x in range(0, 3):
            challenge = MagicMock()
            challenge.source_authority = 'mytest{}.url.com'.format(x)
            url = 'https://mytest{}.url.com'.format(x)
            test_challenges.append({
                'url': url,
                'challenge': challenge
            })
            HttpBearerChallengeCache.set_challenge_for_url(url, challenge)

        self.assertEqual(len(HttpBearerChallengeCache._cache), 3)

        cached_challenge = HttpBearerChallengeCache.get_challenge_for_url(test_challenges[1]['url'])
        self.assertTrue(cached_challenge.source_authority in test_challenges[1]['url'])

        # test remove
        HttpBearerChallengeCache.remove_challenge_for_url(test_challenges[0]['url'])
        self.assertIsNone(HttpBearerChallengeCache.get_challenge_for_url(test_challenges[0]['url']))

        # test clear
        self.assertEqual(len(HttpBearerChallengeCache._cache), 2)
        HttpBearerChallengeCache.clear()
        self.assertEqual(len(HttpBearerChallengeCache._cache), 0)

        with self.assertRaises(ValueError):
            HttpBearerChallengeCache.set_challenge_for_url('https://diffurl.com', test_challenges[0]['challenge'])

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

class KeyVaultKeyTest(AzureKeyVaultTestCase):

    def setUp(self):
        super(KeyVaultKeyTest, self).setUp()
        self.standard_vault_only = str(os.environ.get('AZURE_KV_STANDARD_VAULT_ONLY', False)).lower() \
            == 'true'
        self.key_name = 'pythonKey'
        self.plain_text = binascii.b2a_hex(os.urandom(100))
        self.list_test_size = 2

    def tearDown(self):
        super(KeyVaultKeyTest, self).tearDown()
        self.cleanup_created_keys()

    def _import_test_key(self, key_id, import_to_hardware=False):

        def _to_bytes(hex):
            if len(hex) % 2:
                hex = '0{}'.format(hex)
            return codecs.decode(hex, 'hex_codec')
        
        key = JsonWebKey(
            kty='RSA',
            key_ops= ['encrypt', 'decrypt', 'sign', 'verify', 'wrapKey', 'unwrapKey'],
            n=_to_bytes('00a0914d00234ac683b21b4c15d5bed887bdc959c2e57af54ae734e8f00720d775d275e455207e3784ceeb60a50a4655dd72a7a94d271e8ee8f7959a669ca6e775bf0e23badae991b4529d978528b4bd90521d32dd2656796ba82b6bbfc7668c8f5eeb5053747fd199319d29a8440d08f4412d527ff9311eda71825920b47b1c46b11ab3e91d7316407e89c7f340f7b85a34042ce51743b27d4718403d34c7b438af6181be05e4d11eb985d38253d7fe9bf53fc2f1b002d22d2d793fa79a504b6ab42d0492804d7071d727a06cf3a8893aa542b1503f832b296371b6707d4dc6e372f8fe67d8ded1c908fde45ce03bc086a71487fa75e43aa0e0679aa0d20efe35'),
            e=_to_bytes('10001'),
            d=_to_bytes('627c7d24668148fe2252c7fa649ea8a5a9ed44d75c766cda42b29b660e99404f0e862d4561a6c95af6a83d213e0a2244b03cd28576473215073785fb067f015da19084ade9f475e08b040a9a2c7ba00253bb8125508c9df140b75161d266be347a5e0f6900fe1d8bbf78ccc25eeb37e0c9d188d6e1fc15169ba4fe12276193d77790d2326928bd60d0d01d6ead8d6ac4861abadceec95358fd6689c50a1671a4a936d2376440a41445501da4e74bfb98f823bd19c45b94eb01d98fc0d2f284507f018ebd929b8180dbe6381fdd434bffb7800aaabdd973d55f9eaf9bb88a6ea7b28c2a80231e72de1ad244826d665582c2362761019de2e9f10cb8bcc2625649'),
            p=_to_bytes('00d1deac8d68ddd2c1fd52d5999655b2cf1565260de5269e43fd2a85f39280e1708ffff0682166cb6106ee5ea5e9ffd9f98d0becc9ff2cda2febc97259215ad84b9051e563e14a051dce438bc6541a24ac4f014cf9732d36ebfc1e61a00d82cbe412090f7793cfbd4b7605be133dfc3991f7e1bed5786f337de5036fc1e2df4cf3'),
            q=_to_bytes('00c3dc66b641a9b73cd833bc439cd34fc6574465ab5b7e8a92d32595a224d56d911e74624225b48c15a670282a51c40d1dad4bc2e9a3c8dab0c76f10052dfb053bc6ed42c65288a8e8bace7a8881184323f94d7db17ea6dfba651218f931a93b8f738f3d8fd3f6ba218d35b96861a0f584b0ab88ddcf446b9815f4d287d83a3237'),
            dp=_to_bytes('00c9a159be7265cbbabc9afcc4967eb74fe58a4c4945431902d1142da599b760e03838f8cbd26b64324fea6bdc9338503f459793636e59b5361d1e6951e08ddb089e1b507be952a81fbeaf7e76890ea4f536e25505c3f648b1e88377dfc19b4c304e738dfca07211b792286a392a704d0f444c0a802539110b7f1f121c00cff0a9'),
            dq=_to_bytes('00a0bd4c0a3d9f64436a082374b5caf2488bac1568696153a6a5e4cd85d186db31e2f58f024c617d29f37b4e6b54c97a1e25efec59c4d1fd3061ac33509ce8cae5c11f4cd2e83f41a8264f785e78dc0996076ee23dfdfc43d67c463afaa0180c4a718357f9a6f270d542479a0f213870e661fb950abca4a14ca290570ba7983347'),
            qi=_to_bytes('009fe7ae42e92bc04fcd5780464bd21d0c8ac0c599f9af020fde6ab0a7e7d1d39902f5d8fb6c614184c4c1b103fb46e94cd10a6c8a40f9991a1f28269f326435b6c50276fda6493353c650a833f724d80c7d522ba16c79f0eb61f672736b68fb8be3243d10943c4ab7028d09e76cfb5892222e38bc4d35585bf35a88cd68c73b07')
        )
        imported_key = self.client.import_key(key_id.vault, key_id.name, key, import_to_hardware)
        self._validate_rsa_key_bundle(imported_key, KEY_VAULT_URI, key_id.name,
                                'RSA-HSM' if import_to_hardware else 'RSA', key.key_ops)
        return imported_key

    def _validate_rsa_key_bundle(self, bundle, vault, key_name, kty, key_ops=None):
        prefix = '{}/keys/{}/'.format(vault, key_name)
        key_ops = key_ops or ['encrypt', 'decrypt', 'sign', 'verify', 'wrapKey', 'unwrapKey']
        key = bundle.key
        kid = key.kid
        self.assertTrue(kid.index(prefix) == 0, 
            "String should start with '{}', but value is '{}'".format(prefix, kid))
        self.assertEqual(key.kty, kty, "kty should by '{}', but is '{}'".format(key, key.kty))
        self.assertTrue(key.n and key.e, 'Bad RSA public material.')
        self.assertEqual(key_ops, key.key_ops,
            "keyOps should be '{}', but is '{}'".format(key_ops, key.key_ops))
        self.assertTrue(bundle.attributes.created and bundle.attributes.updated,
            'Missing required date attributes.')

    def _validate_key_list(self, keys, expected):
        for key in keys:
            KeyVaultId.parse_key_id(key.kid)
            attributes = expected[key.kid]
            self.assertEqual(attributes, key.attributes)
            del expected[key.kid]

    def cleanup_created_keys(self):
        if not self.is_playback():
            for key in self.client.get_keys(KEY_VAULT_URI):
                id = KeyVaultId.parse_key_id(key.kid)
                self.client.delete_key(id.vault, id.name)

    @record
    def test_key_crud_operations(self):

        # create key
        created_bundle = self.client.create_key(KEY_VAULT_URI, self.key_name, 'RSA')
        self._validate_rsa_key_bundle(created_bundle, KEY_VAULT_URI, self.key_name, 'RSA')
        key_id = KeyVaultId.parse_key_id(created_bundle.key.kid)

        # get key without version
        self.assertEqual(created_bundle, self.client.get_key(key_id.vault, key_id.name, ''))

        # get key with version
        self.assertEqual(created_bundle, self.client.get_key(key_id.vault, key_id.name, key_id.version))

        def _update_key(key_uri):
            updating_bundle = copy.deepcopy(created_bundle)
            updating_bundle.attributes.expires = date_parse.parse('2050-02-02T08:00:00.000Z')
            updating_bundle.key.key_ops = ['encrypt', 'decrypt']
            updating_bundle.tags = { 'foo': 'updated tag' }
            kid = KeyVaultId.parse_key_id(key_uri)
            key_bundle = self.client.update_key(
                kid.vault, kid.name, kid.version, updating_bundle.key.key_ops, updating_bundle.attributes, updating_bundle.tags)
            self.assertEqual(updating_bundle.tags, key_bundle.tags)
            self.assertEqual(updating_bundle.key.kid, key_bundle.key.kid)
            self.assertNotEqual(str(updating_bundle.attributes.updated), str(key_bundle.attributes.updated))
            return key_bundle

        # update key without version
        created_bundle = _update_key(key_id.base_id)

        # update key with version
        created_bundle = _update_key(key_id.id)

        # delete key
        self.client.delete_key(key_id.vault, key_id.name)

        # get key returns not found
        try:
            self.client.get_key(key_id.vault, key_id.name, '')
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'Not Found' not in ex.message:
                raise ex

    @record
    def test_key_list(self):
        
        max_keys = self.list_test_size
        expected = {}

        # create many keys
        for x in range(0, max_keys):
            key_name = '{}{}'.format(self.key_name, x + 1)
            key_bundle = None
            error_count = 0
            while not key_bundle:
                try:
                    key_bundle = self.client.create_key(KEY_VAULT_URI, key_name, 'RSA')
                    kid = KeyVaultId.parse_key_id(key_bundle.key.kid).base_id
                    expected[kid] = key_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex                    

        # list keys
        result = list(self.client.get_keys(KEY_VAULT_URI, self.list_test_size))
        self.assertEqual(len(result), self.list_test_size)
        self._validate_key_list(result, expected)

    @record
    def test_key_list_versions(self):
        
        max_keys = self.list_test_size
        key_name = '{}-versioned'.format(self.key_name)
        expected = {}

        # create many key versions
        for x in range(0, max_keys):
            key_bundle = None
            error_count = 0
            while not key_bundle:
                try:
                    key_bundle = self.client.create_key(KEY_VAULT_URI, key_name, 'RSA')
                    kid = KeyVaultId.parse_key_id(key_bundle.key.kid).id
                    expected[kid] = key_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list key versions
        self._validate_key_list(list(self.client.get_key_versions(KEY_VAULT_URI, key_name)), expected)

    @record
    def test_key_backup_and_restore(self):
        
        key_name = '{}forBkp'.format(self.key_name)

        # create key
        created_bundle = self.client.create_key(KEY_VAULT_URI, key_name, 'RSA')
        key_id = KeyVaultId.parse_key_id(created_bundle.key.kid)

        # backup key
        key_backup = self.client.backup_key(key_id.vault, key_id.name).value

        # delete key
        self.client.delete_key(key_id.vault, key_id.name)

        # restore key
        self.assertEqual(created_bundle, self.client.restore_key(KEY_VAULT_URI, key_backup))

    @record
    def test_key_import(self):

        key_id = KeyVaultId.create_key_id(KEY_VAULT_URI, 'importedKey')

        # import to software
        self._import_test_key(key_id, False)

        # import to hardware
        self._import_test_key(key_id, not self.standard_vault_only)

    @record
    def test_key_encrypt_and_decrypt(self):

        key_id = KeyVaultId.create_key_id(KEY_VAULT_URI, self.key_name)
        plain_text = self.plain_text

        # import key
        imported_key = self._import_test_key(key_id)
        key_id = KeyVaultId.parse_key_id(imported_key.key.kid)

        # encrypt without version
        result = self.client.encrypt(key_id.vault, key_id.name, '', 'RSA-OAEP', plain_text)
        cipher_text = result.result

        # decrypt without version
        result = self.client.decrypt(key_id.vault, key_id.name, '', 'RSA-OAEP', cipher_text)
        if not self.is_playback():
            self.assertEqual(plain_text, result.result)

        # encrypt with version
        result = self.client.encrypt(key_id.vault, key_id.name, key_id.version, 'RSA-OAEP', plain_text)
        cipher_text = result.result

        # decrypt with version
        result = self.client.decrypt(key_id.vault, key_id.name, key_id.version, 'RSA-OAEP', cipher_text)
        if not self.is_playback():
            self.assertEqual(plain_text, result.result)

    @record
    def test_key_wrap_and_unwrap(self):

        key_id = KeyVaultId.create_key_id(KEY_VAULT_URI, self.key_name)
        plain_text = self.plain_text

        # import key
        imported_key = self._import_test_key(key_id)
        key_id = KeyVaultId.parse_key_id(imported_key.key.kid)

        # wrap without version
        result = self.client.wrap_key(key_id.vault, key_id.name, '', 'RSA-OAEP', plain_text)
        cipher_text = result.result

        # unwrap without version
        result = self.client.unwrap_key(key_id.vault, key_id.name, '', 'RSA-OAEP', cipher_text)
        if not self.is_playback():
            self.assertEqual(plain_text, result.result)

        # wrap with version
        result = self.client.wrap_key(key_id.vault, key_id.name, key_id.version, 'RSA-OAEP', plain_text)
        cipher_text = result.result

        # unwrap with version
        result = self.client.unwrap_key(key_id.vault, key_id.name, key_id.version, 'RSA-OAEP', cipher_text)
        if not self.is_playback():
            self.assertEqual(plain_text, result.result)

    @record
    def test_key_sign_and_verify(self):

        key_id = KeyVaultId.create_key_id(KEY_VAULT_URI, self.key_name)
        plain_text = self.plain_text
        md = hashlib.sha256()
        md.update(plain_text);
        digest = md.digest();

        # import key
        imported_key = self._import_test_key(key_id)
        key_id = KeyVaultId.parse_key_id(imported_key.key.kid)

        # sign without version
        signature = self.client.sign(key_id.vault, key_id.name, '', 'RS256', digest).result

        # verify without version
        result = self.client.verify(key_id.vault, key_id.name, '', 'RS256', digest, signature)
        self.assertTrue(result.value)

        # sign with version
        signature = self.client.sign(key_id.vault, key_id.name, '', 'RS256', digest).result

        # verify with version
        result = self.client.verify(key_id.vault, key_id.name, key_id.version, 'RS256', digest, signature)
        self.assertTrue(result.value)

class KeyVaultSecretTest(AzureKeyVaultTestCase):

    def setUp(self):
        super(KeyVaultSecretTest, self).setUp()
        self.secret_name = 'pythonSecret'
        self.secret_value = 'Pa$$w0rd'
        self.list_test_size = 2

    def tearDown(self):
        super(KeyVaultSecretTest, self).tearDown()
        self.cleanup_created_secrets()

    def cleanup_created_secrets(self):
        if not self.is_playback():
            for secret in self.client.get_secrets(KEY_VAULT_URI):
                id = KeyVaultId.parse_secret_id(secret.id)
                self.client.delete_secret(id.vault, id.name)

    def _validate_secret_bundle(self, bundle, vault, secret_name, secret_value):
        prefix = '{}/secrets/{}/'.format(vault, secret_name)
        id = bundle.id
        self.assertTrue(id.index(prefix) == 0, 
            "String should start with '{}', but value is '{}'".format(prefix, id))
        self.assertEqual(bundle.value, secret_value, "value should be '{}', but is '{}'".format(secret_value, bundle.value))
        self.assertTrue(bundle.attributes.created and bundle.attributes.updated,
            'Missing required date attributes.')

    def _validate_secret_list(self, secrets, expected):
        for secret in secrets:
            KeyVaultId.parse_secret_id(secret.id)
            attributes = expected[secret.id]
            self.assertEqual(attributes, secret.attributes)
            del expected[secret.id]

    @record
    def test_secret_crud_operations(self):
        
        # create secret
        secret_bundle = self.client.set_secret(KEY_VAULT_URI, self.secret_name, self.secret_value)
        self._validate_secret_bundle(secret_bundle, KEY_VAULT_URI, self.secret_name, self.secret_value)
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
            updating_bundle.tags = { 'foo': 'updated tag' }
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
            if not hasattr(ex, 'message') or 'Not Found' not in ex.message:
                raise ex

    @record
    def test_secret_list(self):

        max_secrets = self.list_test_size
        expected = {}

        # create many secrets
        for x in range(0, max_secrets):
            secret_name = '{}{}'.format(self.secret_name, x + 1)
            secret_bundle = None
            error_count = 0
            while not secret_bundle:
                try:
                    secret_bundle = self.client.set_secret(KEY_VAULT_URI, secret_name, self.secret_value)
                    sid = KeyVaultId.parse_secret_id(secret_bundle.id).base_id
                    expected[sid] = secret_bundle.attributes
                except Exception as ex:
                    self.fail()
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex
        
        # list secrets
        result = list(self.client.get_secrets(KEY_VAULT_URI, self.list_test_size))
        self.assertEqual(len(result), self.list_test_size)
        self._validate_secret_list(result, expected)

    @record
    def test_secret_list_versions(self):
        
        max_secrets = self.list_test_size
        secret_name = '{}-versioned'.format(self.secret_name)
        expected = {}

        # create many secret versions
        for x in range(0, max_secrets):
            secret_bundle = None
            error_count = 0
            while not secret_bundle:
                try:
                    secret_bundle = self.client.set_secret(KEY_VAULT_URI, secret_name, self.secret_value)
                    sid = KeyVaultId.parse_secret_id(secret_bundle.id).id
                    expected[sid] = secret_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list secret versions
        self._validate_secret_list(list(self.client.get_secret_versions(KEY_VAULT_URI, secret_name)), expected)

class KeyVaultCertificateTest(AzureKeyVaultTestCase):

    def setUp(self):
        super(KeyVaultCertificateTest, self).setUp()
        self.cert_name = 'pythonCertificate'
        self.issuer_name = 'pythonIssuer'
        self.list_test_size = 2

    def tearDown(self):
        super(KeyVaultCertificateTest, self).tearDown()
        self.cleanup_created_certificates()

    def cleanup_created_certificates(self):
        if not self.is_playback():
            for cert in self.client.get_certificates(KEY_VAULT_URI):
                id = KeyVaultId.parse_certificate_id(cert.id)
                self.client.delete_certificate(id.vault, id.name)

    def _import_common_certificate(self, cert_name):
        cert_content = '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'
        cert_password = '123'
        cert_policy = CertificatePolicy(
            KeyProperties(True, 'RSA', 2048, False),
            SecretProperties('application/x-pkcs12'))
        return (
            self.client.import_certificate(KEY_VAULT_URI, cert_name, cert_content, cert_password, cert_policy),
            cert_policy
        )

    def _validate_certificate_operation(self, pending_cert, vault, cert_name, cert_policy):
        self.assertIsNotNone(pending_cert)
        self.assertIsNotNone(pending_cert.csr)
        self.assertEqual(cert_policy.issuer_parameters.name, pending_cert.issuer_parameters.name)
        pending_id = KeyVaultId.parse_certificate_operation_id(pending_cert.id)
        self.assertEqual(pending_id.vault, vault)
        self.assertEqual(pending_id.name, cert_name)

    def _validate_certificate_bundle(self, cert, vault, cert_name, cert_policy):
        cert_id = KeyVaultId.parse_certificate_id(cert.id)
        self.assertEqual(cert_id.vault, vault)
        self.assertEqual(cert_id.name, cert_name)
        self.assertIsNotNone(cert)
        self.assertIsNotNone(cert.x509_thumbprint)
        self.assertIsNotNone(cert.cer)
        self.assertIsNotNone(cert.attributes)
        self.assertIsNotNone(cert.policy)
        self.assertIsNotNone(cert.policy.id)
        self.assertIsNotNone(cert.policy.issuer_parameters)
        self.assertIsNotNone(cert.policy.lifetime_actions)
        self.assertEqual(cert.policy.key_properties, cert_policy.key_properties)
        self.assertEqual(cert.policy.secret_properties, cert_policy.secret_properties)
        self.assertIsNotNone(cert.policy.x509_certificate_properties)
        if cert_policy.x509_certificate_properties:
            self.assertEqual(cert.policy.x509_certificate_properties.validity_in_months,
                             cert_policy.x509_certificate_properties.validity_in_months)
        KeyVaultId.parse_secret_id(cert.sid)
        KeyVaultId.parse_key_id(cert.kid)

    def _validate_certificate_list(self, certificates, expected):
        for cert in certificates:
            KeyVaultId.parse_certificate_id(cert.id)
            attributes = expected[cert.id]
            self.assertEqual(attributes, cert.attributes)
            del expected[cert.id]

    def _validate_issuer_bundle(self, bundle, vault, name, provider, credentials, org_details):
        self.assertIsNotNone(bundle)
        self.assertIsNotNone(bundle.attributes)
        self.assertIsNotNone(bundle.organization_details)
        self.assertEqual(bundle.provider, provider)

        issuer_id = KeyVaultId.parse_certificate_issuer_id(bundle.id)
        self.assertEqual(issuer_id.vault, vault)
        self.assertEqual(issuer_id.name, name)

        if credentials:
            self.assertEqual(bundle.credentials.account_id, credentials.account_id)
        if org_details:
            self.assertEqual(bundle.organization_details, org_details)

    def _validate_certificate_issuer_list(self, issuers, expected):
        for issuer in issuers:
            KeyVaultId.parse_certificate_issuer_id(issuer.id)
            provider = expected[issuer.id]
            if provider:
                self.assertEqual(provider, issuer.provider)
                del expected[issuer.id]

    def _validate_certificate_contacts(self, contacts, vault, expected):
        contact_id = '{}/certificates/contacts'.format(vault)
        self.assertEqual(contact_id, contacts.id)
        self.assertEqual(len(contacts.contact_list), len(expected))

        for contact in contacts.contact_list:
            exp_contact = next(x for x in expected if x.email_address == contact.email_address)
            self.assertEqual(contact, exp_contact)

    @record
    def test_certificate_crud_operations(self):

        cert_policy = CertificatePolicy(
            KeyProperties(True, 'RSA', 2048, False),
            SecretProperties('application/x-pkcs12'),
            issuer_parameters=IssuerParameters('Self'),
            x509_certificate_properties=X509CertificateProperties(
                subject='CN=*.microsoft.com',
                subject_alternative_names=SubjectAlternativeNames(
                    dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com']
                ),
                validity_in_months=24
            ))

        # create certificate
        interval_time = 5 if not self.is_playback() else 0
        cert_operation = self.client.create_certificate(KEY_VAULT_URI, self.cert_name, cert_policy)
        while True:
            pending_cert = self.client.get_certificate_operation(KEY_VAULT_URI, self.cert_name)
            self._validate_certificate_operation(pending_cert, KEY_VAULT_URI, self.cert_name, cert_policy)
            if pending_cert.status.lower() == 'completed':
                cert_id = KeyVaultId.parse_certificate_operation_id(pending_cert.target)
                break
            elif pending_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_cert))
            time.sleep(interval_time)

        # get certificate
        cert_bundle = self.client.get_certificate(cert_id.vault, cert_id.name, '')
        self._validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

        # get certificate as secret
        secret_id = KeyVaultId.parse_secret_id(cert_bundle.sid)
        secret_bundle = self.client.get_secret(secret_id.vault, secret_id.name, secret_id.version)

        # update certificate
        cert_policy.tags = {'tag1': 'value1'}
        cert_bundle = self.client.update_certificate(cert_id.vault, cert_id.name, cert_id.version, cert_policy)
        self._validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

        # delete certificate
        cert_bundle = self.client.delete_certificate(KEY_VAULT_URI, self.cert_name)
        self._validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

        # get certificate returns not found
        try:
            self.client.get_certificate(cert_id.vault, cert_id.name, '')
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'Not Found' not in ex.message:
                raise ex

    @record
    def test_certificate_import(self):

        cert_name = 'pythonImportCert'

        # import certificate(
        (cert_bundle, cert_policy) = self._import_common_certificate(cert_name)
        self._validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, cert_name, cert_policy)

    @record
    def test_certificate_list(self):

        max_certificates = self.list_test_size
        expected = {}

        # import some certificates
        for x in range(0, max_certificates):
            cert_name = '{}{}'.format(self.cert_name, x + 1)
            cert_bundle = None
            error_count = 0
            while not cert_bundle:
                try:
                    cert_bundle = self._import_common_certificate(cert_name)[0]
                    cid = KeyVaultId.parse_certificate_id(cert_bundle.id).base_id
                    expected[cid] = cert_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list certificates
        result = list(self.client.get_certificates(KEY_VAULT_URI, self.list_test_size))
        self.assertEqual(len(result), self.list_test_size)
        self._validate_certificate_list(result, expected)

    @record
    def test_certificate_list_versions(self):

        max_certificates = self.list_test_size
        cert_name = '{}-versioned'.format(self.cert_name)
        expected = {}

        # import same certificates as different versions
        for x in range(0, max_certificates):
            cert_bundle = None
            error_count = 0
            while not cert_bundle:
                try:
                    cert_bundle = self._import_common_certificate(cert_name)[0]
                    cid = KeyVaultId.parse_certificate_id(cert_bundle.id).id
                    expected[cid] = cert_bundle.attributes
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list certificate versions
        self._validate_certificate_list(list(self.client.get_certificate_versions(KEY_VAULT_URI, cert_name)), expected)

    @record
    def test_certificate_crud_issuer(self):

        issuer_name = 'pythonIssuer'
        issuer_credentials = IssuerCredentials('keyvaultuser', 'password')
        organization_details = OrganizationDetails(
            admin_details=[AdministratorDetails('Jane', 'Doe', 'admin@contoso.com', '4256666666')])

        # create certificate issuer
        issuer_bundle = self.client.set_certificate_issuer(KEY_VAULT_URI, issuer_name, 'test', issuer_credentials, organization_details)
        self._validate_issuer_bundle(issuer_bundle, KEY_VAULT_URI, issuer_name, 'test', issuer_credentials, organization_details)

        # get certificate issuer
        issuer_bundle = self.client.get_certificate_issuer(KEY_VAULT_URI, issuer_name)
        self._validate_issuer_bundle(issuer_bundle, KEY_VAULT_URI, issuer_name, 'test', issuer_credentials, organization_details)

        # update certificate issue
        new_credentials = IssuerCredentials('xboxuser', 'security')
        new_org_details = OrganizationDetails(
            admin_details=[AdministratorDetails('Jane II', 'Doe', 'admin@contoso.com', '1111111111')])
        issuer_bundle = self.client.update_certificate_issuer(KEY_VAULT_URI, issuer_name, 'test', new_credentials, new_org_details)
        self._validate_issuer_bundle(issuer_bundle, KEY_VAULT_URI, issuer_name, 'test', new_credentials, new_org_details)

        # delete certificate issuer(
        self.client.delete_certificate_issuer(KEY_VAULT_URI, issuer_name)

        # get certificate issuer returns not found
        try:
            self.client.get_certificate_issuer(KEY_VAULT_URI, issuer_name)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'Not Found' not in ex.message:
                raise ex

    @record
    def test_certificate_list_issuers(self):

        max_issuers = self.list_test_size
        expected = {}

        # create some certificate issuers(
        for x in range(0, max_issuers):
            issuer_name = 'pythonIssuer{}'.format(x + 1)
            issuer_credentials = IssuerCredentials('keyvaultuser', 'password')
            organization_details = OrganizationDetails(
                admin_details=[AdministratorDetails('Jane', 'Doe', 'admin@contoso.com', '4256666666')])
            error_count = 0
            issuer_bundle = None
            while not issuer_bundle:
                try:
                    issuer_bundle = self.client.set_certificate_issuer(KEY_VAULT_URI, issuer_name, 'test', issuer_credentials, organization_details)
                    expected[issuer_bundle.id] = issuer_bundle.provider
                except Exception as ex:
                    if hasattr(ex, 'message') and 'Throttled' in ex.message:
                        error_count += 1
                        time.sleep(2.5 * error_count)
                        continue
                    else:
                        raise ex

        # list certificate issuers
        result = list(self.client.get_certificate_issuers(KEY_VAULT_URI, self.list_test_size))
        self.assertEqual(len(result), self.list_test_size)
        self._validate_certificate_issuer_list(result, expected)

    @record
    def test_certificate_async_request_cancellation_and_deletion(self):
        
        cert_name = 'asyncCanceledDeletedCert'
        cert_policy = CertificatePolicy(
            KeyProperties(True, 'RSA', 2048, False),
            SecretProperties('application/x-pkcs12'),
            issuer_parameters=IssuerParameters('Self'),
            x509_certificate_properties=X509CertificateProperties(
                subject='CN=*.microsoft.com',
                subject_alternative_names=SubjectAlternativeNames(
                    dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com']
                ),
                validity_in_months=24
            ))
        
        # create certificate
        self.client.create_certificate(KEY_VAULT_URI, cert_name, cert_policy)

        # cancel certificate operation
        cancel_operation = self.client.update_certificate_operation(KEY_VAULT_URI, cert_name, True)
        self.assertTrue(hasattr(cancel_operation, 'cancellation_requested'))
        self.assertTrue(cancel_operation.cancellation_requested)
        self._validate_certificate_operation(cancel_operation, KEY_VAULT_URI, cert_name, cert_policy)

        retrieved_operation = self.client.get_certificate_operation(KEY_VAULT_URI, cert_name)
        self.assertTrue(hasattr(retrieved_operation, 'cancellation_requested'))
        self.assertTrue(retrieved_operation.cancellation_requested)
        self._validate_certificate_operation(retrieved_operation, KEY_VAULT_URI, cert_name, cert_policy)

        # delete certificate operation
        deleted_operation = self.client.delete_certificate_operation(KEY_VAULT_URI, cert_name)
        self.assertIsNotNone(deleted_operation)
        self._validate_certificate_operation(deleted_operation, KEY_VAULT_URI, cert_name, cert_policy)

        try:
            self.client.get_certificate_operation(KEY_VAULT_URI, cert_name)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'Not Found' not in ex.message:
                raise ex

        # delete cancelled certificate operation
        self.client.delete_certificate(KEY_VAULT_URI, cert_name)

    @record
    def test_certificate_crud_contacts(self):
        
        contact_list = [
            Contact('admin@contoso.com', 'John Doe', '1111111111'),
            Contact('admin2@contoso.com', 'John Doe2', '2222222222')
        ]

        # create certificate contacts
        contacts = self.client.set_certificate_contacts(KEY_VAULT_URI, contact_list)
        self._validate_certificate_contacts(contacts, KEY_VAULT_URI, contact_list)

        # get certificate contacts
        contacts = self.client.get_certificate_contacts(KEY_VAULT_URI)
        self._validate_certificate_contacts(contacts, KEY_VAULT_URI, contact_list)

        # delete certificate contacts
        contacts = self.client.delete_certificate_contacts(KEY_VAULT_URI)
        self._validate_certificate_contacts(contacts, KEY_VAULT_URI, contact_list)

        # get certificate contacts returns not found
        try:
            contacts = self.client.get_certificate_contacts(KEY_VAULT_URI)
            self.fail('Get should fail')
        except Exception as ex:
            if not hasattr(ex, 'message') or 'Not Found' not in ex.message:
                raise ex

    @record
    def test_certificate_policy(self):

        cert_name = 'policyCertificate'

        # get certificate policy
        (cert_bundle, cert_policy) = self._import_common_certificate(cert_name)
        retrieved_policy = self.client.get_certificate_policy(KEY_VAULT_URI, cert_name)
        self.assertIsNotNone(retrieved_policy)

        # update certificate policy
        cert_policy = CertificatePolicy(
            KeyProperties(True, 'RSA', 2048, False),
            SecretProperties('application/x-pkcs12'),
            issuer_parameters=IssuerParameters('Self')
        )

        self.client.update_certificate_policy(KEY_VAULT_URI, cert_name, cert_policy)
        updated_cert_policy = self.client.get_certificate_policy(KEY_VAULT_URI, cert_name)
        self.assertIsNotNone(updated_cert_policy)

    @record
    def test_certificate_manual_enrolled(self):

        cert_name = 'unknownIssuerCert'
        cert_policy = CertificatePolicy(
            KeyProperties(True, 'RSA', 2048, False),
            SecretProperties('application/x-pkcs12'),
            issuer_parameters=IssuerParameters('Unknown'),
            x509_certificate_properties=X509CertificateProperties(
                subject='CN=*.microsoft.com',
                subject_alternative_names=SubjectAlternativeNames(
                    dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com']
                ),
                validity_in_months=24
            ))

        # get pending certificate signing request
        cert_operation = self.client.create_certificate(KEY_VAULT_URI, cert_name, cert_policy)
        pending_version_csr = self.client.get_pending_certificate_signing_request(KEY_VAULT_URI, cert_name)
        try:
            self.assertEqual(cert_operation.csr, pending_version_csr)
        except Exception as ex:
            pass
        finally:
            self.client.delete_certificate(KEY_VAULT_URI, cert_name)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
