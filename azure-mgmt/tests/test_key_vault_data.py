# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import binascii
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

import azure.keyvault.key_vault_id as keyvaultid
from azure.keyvault import HttpBearerChallenge
from azure.keyvault.http_bearer_challenge_cache import \
    (_cache as challenge_cache, get_challenge_for_url, set_challenge_for_url, clear,
     remove_challenge_for_url)
from azure.keyvault.generated.models import \
    (CertificatePolicy, KeyProperties, SecretProperties, IssuerParameters,
     X509CertificateProperties, IssuerBundle, IssuerCredentials, OrganizationDetails,
     AdministratorDetails, Contact, KeyVaultError, SubjectAlternativeNames)

from testutils.common_recordingtestcase import record
from tests.keyvault_testcase import HttpStatusCode, AzureKeyVaultTestCase

KEY_VAULT_URI = os.environ.get('AZURE_KV_VAULT', 'https://python-sdk-test-keyvault.vault.azure.net')

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
        res = keyvaultid.create_object_id('keys', 'https://myvault.vault.azure.net', ' mykey', None)
        self.assertEqual(res.__dict__, expected)

        res = keyvaultid.create_object_id('keys', 'https://myvault.vault.azure.net', ' mykey', ' ')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = keyvaultid.create_object_id(' keys ', 'https://myvault.vault.azure.net', ' mykey ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)
        
        # failure scenarios
        with self.assertRaises(TypeError):
            keyvaultid.create_object_id('keys', 'https://myvault.vault.azure.net', ['stuff'], '')
        with self.assertRaises(ValueError):
            keyvaultid.create_object_id('keys', 'https://myvault.vault.azure.net', ' ', '')
        with self.assertRaises(ValueError):
            keyvaultid.create_object_id('keys', 'myvault.vault.azure.net', 'mykey', '')

    def test_parse_object_id(self):
        # success scenarios
        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = keyvaultid.parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = keyvaultid.parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey')
        self.assertEqual(res.__dict__, expected)

        # failure scenarios
        with self.assertRaises(ValueError):
            keyvaultid.parse_object_id('secret', 'https://myvault.vault.azure.net/keys/mykey/abc123')
        with self.assertRaises(ValueError):
            keyvaultid.parse_object_id('keys', 'https://myvault.vault.azure.net/keys/mykey/abc123/extra')
        with self.assertRaises(ValueError):
            keyvaultid.parse_object_id('keys', 'https://myvault.vault.azure.net')

    def test_create_key_id(self):
        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = keyvaultid.create_key_id('https://myvault.vault.azure.net', ' mykey', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = keyvaultid.create_key_id('https://myvault.vault.azure.net', ' mykey ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)

    def test_parse_key_id(self):
        expected = self._get_expected('keys', 'myvault', 'mykey', 'abc123')
        res = keyvaultid.parse_key_id('https://myvault.vault.azure.net/keys/mykey/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('keys', 'myvault', 'mykey')
        res = keyvaultid.parse_key_id('https://myvault.vault.azure.net/keys/mykey')
        self.assertEqual(res.__dict__, expected)

    def test_create_secret_id(self):
        expected = self._get_expected('secrets', 'myvault', 'mysecret')
        res = keyvaultid.create_secret_id('https://myvault.vault.azure.net', ' mysecret', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('secrets', 'myvault', 'mysecret', 'abc123')
        res = keyvaultid.create_secret_id('https://myvault.vault.azure.net', ' mysecret ', ' abc123 ')
        self.assertEqual(res.__dict__, expected)

    def test_parse_secret_id(self):
        expected = self._get_expected('secrets', 'myvault', 'mysecret', 'abc123')
        res = keyvaultid.parse_secret_id('https://myvault.vault.azure.net/secrets/mysecret/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('secrets', 'myvault', 'mysecret')
        res = keyvaultid.parse_secret_id('https://myvault.vault.azure.net/secrets/mysecret')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert')
        res = keyvaultid.create_certificate_id('https://myvault.vault.azure.net', ' mycert', None)
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('certificates', 'myvault', 'mycert', 'abc123')
        res = keyvaultid.create_certificate_id('https://myvault.vault.azure.net', 'mycert', ' abc123')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'abc123')
        res = keyvaultid.parse_certificate_id('https://myvault.vault.azure.net/certificates/mycert/abc123')
        self.assertEqual(res.__dict__, expected)

        expected = self._get_expected('certificates', 'myvault', 'mycert')
        res = keyvaultid.parse_certificate_id('https://myvault.vault.azure.net/certificates/mycert')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_operation_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'pending')
        expected['base_id'] = expected['id']
        expected['version'] = None
        res = keyvaultid.create_certificate_operation_id('https://myvault.vault.azure.net', ' mycert')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_operation_id(self):
        expected = self._get_expected('certificates', 'myvault', 'mycert', 'pending')
        expected['base_id'] = expected['id']
        expected['version'] = None
        res = keyvaultid.parse_certificate_operation_id('https://myvault.vault.azure.net/certificates/mycert/pending')
        self.assertEqual(res.__dict__, expected)

    def test_create_certificate_issuer_id(self):
        expected = self._get_expected('certificates/issuers', 'myvault', 'myissuer')
        res = keyvaultid.create_certificate_issuer_id('https://myvault.vault.azure.net', 'myissuer')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_issuer_id(self):
        expected = self._get_expected('certificates/issuers', 'myvault', 'myissuer')
        res = keyvaultid.parse_certificate_issuer_id('https://myvault.vault.azure.net/certificates/issuers/myissuer')
        self.assertEqual(res.__dict__, expected)

    def test_bearer_challenge_cache(self):
        test_challenges = []
        clear()
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

class KeyVaultKeyTest(AzureKeyVaultTestCase):

    def setUp(self):
        super(KeyVaultKeyTest, self).setUp()
        standard_vault_only = str(os.environ.get('AZURE_KV_STANDARD_VAULT_ONLY', False)).lower() \
            == 'true'
        self.key_name = 'pythonKey'
        self.list_test_size = 2
        if not self.is_playback():
            self.create_resource_group()

    def tearDown(self):
        super(KeyVaultKeyTest, self).tearDown()
        self.cleanup_created_keys()

    def _get_test_key(self):
        return {
            'n': { 'data': [31403165, 173515265, 63388853, 41445484, 28572798, 41983158, 179892955, 184539795, 195496834, 186371485, 105099914, 124126195, 220355614, 62597291, 211257834, 180260588, 50093174, 71664730, 168573911, 132471092, 92855735, 240596985, 236098769, 173925533, 21038343, 184422189, 50979118, 214529292, 171289383, 178021279, 227518712, 217740520, 81983906, 73408747, 267914051, 229529180, 16559719, 5537837, 68640078, 173929251, 81539991, 237912588, 235382838, 104343409, 52196777, 197367866, 158395070, 117971489, 160834890, 231935437, 38538604, 134498263, 37612848, 134625325, 50358689, 235472466, 72917894, 703321, 50980314, 120571588, 214503569, 14882466, 71451463, 38484115, 211379782, 199265141, 167739796, 236529689, 110194265, 252283980, 242275601, 45048505, 139306567, 13], 't': 74, 's': 0 },
            'e': { 'data':[65537], 't': 1, 's': 0 },
            'd': { 'data': [45687901, 82912839, 136844883, 32867876, 209589627, 114760643, 188378503, 262495278, 145440185, 65785046, 86798789, 62386434, 50560554, 61549169, 202839320, 47223801, 16345679, 183718797, 215606790, 260736332, 152310689, 243692743, 252563899, 55901901, 20486148, 164420346, 116855152, 217658322, 158370826, 94231438, 27528988, 67335341, 174899203, 109090394, 250630291, 9002457, 203943974, 156578180, 115625150, 114683304, 26974288, 508888, 171821311, 128703059, 7667499, 75449693, 176959654, 55586600, 67092631, 147722039, 47625305, 179087115, 68335990, 160396405, 27300777, 218451174, 232237402, 237108697, 210447563, 20554934, 167197589, 83310674, 139749301, 41733981, 16245554, 49622864, 194380346, 105816513, 256316339, 38893666, 192649829, 99609567, 117074140, 6], 't': 74, 's': 0 },
            'p': { 'data': [33083239, 162132243, 220369741, 45039546, 222307487, 179206041, 256947704, 245855772, 249899507, 28771428, 14980020, 148159943, 19126604, 110980923, 232620253, 200804176, 193146776, 1849395, 38163760, 205096501, 123623920, 77315574, 131394591, 41619980, 234834515, 7977638, 258636778, 44457951, 40027731, 226143479, 195688366, 19044599, 23412006, 147023142, 222017947, 33779866, 62482], 't': 37, 's': 0 },
            'q': { 'data': [252056923, 84721184, 208820342, 98257526, 257711757, 170210495, 211611252, 70482129, 164129480, 138844182, 56855320, 236397981, 200230378, 1345179, 23830734, 224624556, 110311189, 37776986, 172599799, 192572556, 60025524, 221499009, 261656032, 138834403, 207844105, 22896659, 40314333, 65995283, 96406231, 167203684, 62595788, 200386123, 90252701, 140191004, 267133432, 24172080, 58080], 't': 37, 's': 0 },
            'dP': { 'data': [201993265, 47821091, 261789604, 27756464, 81622509, 134233349, 251725677, 237658138, 151857794, 249347443, 31788651, 33789622, 253087540, 158289247, 259273148, 65044487, 113510107, 172257746, 130321730, 75880872, 243610460, 176804584, 222782578, 136118430, 32479779, 88296461, 45617733, 83305291, 97037456, 67918464, 97435219, 168410452, 234985976, 238394001, 22331653, 267371287, 1349, 199116946, 123989676, 107034094, 192688242, 85537734, 173262414, 44240895, 113520276, 236524933, 161774153, 174144730, 191215545, 62177699, 80851160, 134899343, 259263575, 121357616, 156648819, 255499481, 103280063, 231493924, 4634332, 236843526, 156104816, 246744594, 112844480, 42556164, 94418795, 254142946, 8374346, 95569210, 181034034, 47641170, 125752615, 266787505, 241003275, 27650, 0], 't': 37, 's': 0 },
            'dQ': { 'data': [84475683, 45186766, 37599068, 34522187, 265058634, 129988009, 226913475, 58582850, 115308212, 131964294, 196466844, 151174458, 225261037, 207233351, 84725934, 141546365, 163838731, 202239901, 154853708, 175227927, 184335942, 133762496, 92997640, 33570977, 56137749, 74033413, 88232389, 177734406, 169854856, 216277089, 160231444, 28162890, 96721484, 49993185, 259099732, 107900074, 52851, 234929, 97512319, 179816523, 203072779, 220703111, 150012141, 44886341, 59462775, 130019454, 227743067, 161683730, 153831298, 165320796, 152113376, 151476367, 167450232, 129591314, 57629678, 84105489, 206226099, 235738210, 119902853, 113106688, 22829142, 208571155, 244917660, 74554550, 255318099, 233351844, 215611320, 259557115, 139301223, 196032562, 41364499, 212828041, 168778543, 29746, 0], 't': 37, 's': 0 },
            'qInv': { 'data': [257191369, 24789324, 179088888, 4877263, 229824703, 180005485, 140588854, 162932877, 148164403, 251171427, 37629294, 154026114, 253932472, 64590117, 134661418, 36207596, 237045424, 88285250, 196080720, 103392332, 203915656, 113894996, 31803101, 103603699, 98869410, 182818866, 105506928, 66214245, 239517111, 197997650, 218541095, 255370546, 25288449, 253555509, 158329635, 150487361, 51171], 't': 37, 's':0 }
        }

    def _import_test_key(self, key_id, import_to_hardware=False):

        def _set_rsa_parameters(dest, key):

            def _big_integer_to_buffer(n):
                # TODO: need to convert JS BigInteger to a Python integer
                return n

            dest['n'] = _big_integer_to_buffer(key['n'])
            dest['e'] = _big_integer_to_buffer(key['e'])
            dest['d'] = _big_integer_to_buffer(key['d'])
            dest['p'] = _big_integer_to_buffer(key['p'])
            dest['q'] = _big_integer_to_buffer(key['q'])
            dest['dp'] = _big_integer_to_buffer(key['dP'])
            dest['dq'] = _big_integer_to_buffer(key['dQ'])
            dest['qi'] = _big_integer_to_buffer(key['qInv'])

        key = {
            'kty': 'RSA',
            'keyOps': ['encrypt', 'decrypt', 'sign', 'verify', 'wrapKey', 'unwrapKey']
        }
        _set_rsa_parameters(key, self._get_test_key())
        imported_key = self.client.import_key(key_id.vault, key_id.name, key, import_to_hardware)
        self._validate_rsa_key_bundle(imported_key, KEY_VAULT_URI, key_id.name,
                                'RSA-HSM' if import_to_hardware else 'RSA', key['keyOps'])
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
            keyvaultid.parse_key_id(key.kid)
            attributes = expected[key.kid]
            self.assertEqual(attributes, key.attributes)
            del expected[key.kid]

    def cleanup_created_keys(self):
        if not self.is_playback():
            for key in self.client.get_keys(KEY_VAULT_URI):
                id = keyvaultid.parse_key_id(key.kid)
                self.client.delete_key(id.vault, id.name)

    @record
    def test_key_crud_operations(self):

        # create key
        created_bundle = self.client.create_key(KEY_VAULT_URI, self.key_name, 'RSA')
        self._validate_rsa_key_bundle(created_bundle, KEY_VAULT_URI, self.key_name, 'RSA')
        key_id = keyvaultid.parse_key_id(created_bundle.key.kid)

        # get key without version
        self.assertEqual(created_bundle, self.client.get_key(key_id.base_id))

        # get key with version
        self.assertEqual(created_bundle, self.client.get_key(key_id.id))

        def _update_key(key_uri):
            updating_bundle = copy.deepcopy(created_bundle)
            updating_bundle.attributes.expires = date_parse.parse('2050-02-02T08:00:00.000Z')
            updating_bundle.key.key_ops = ['encrypt', 'decrypt']
            updating_bundle.tags = { 'foo': binascii.b2a_hex(os.urandom(100)) }
            key_bundle = self.client.update_key(
                key_uri, updating_bundle.key.key_ops, updating_bundle.attributes, updating_bundle.tags)
            updating_bundle.attributes.updated = key_bundle.attributes.updated
            self.assertEqual(updating_bundle, key_bundle)
            return key_bundle

        # update key without version
        created_bundle = _update_key(key_id.base_id)

        # update key with version
        created_bundle = _update_key(key_id.id)

        # delete key
        self.assertEqual(created_bundle, self.client.delete_key(key_id.vault, key_id.name))

        # get key returns not found
        try:
            self.client.get_key(key_id.base_id)
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
                    kid = keyvaultid.parse_key_id(key_bundle.key.kid).base_id
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
                    kid = keyvaultid.parse_key_id(key_bundle.key.kid).id
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
        key_id = keyvaultid.parse_key_id(created_bundle.key.kid)

        # backup key
        key_backup = self.client.backup_key(key_id.vault, key_id.name).value

        # delete key
        self.client.delete_key(key_id.vault, key_id.name)

        # restore key
        self.assertEqual(created_bundle, self.client.restore_key(KEY_VAULT_URI, key_backup))

    # TODO Fix import issues
    #@record
    #def test_key_import(self):

    #    # import to software
    #    self._import_test_key(False)

    #    # import to hardware
    #    self._import_test_key(not self.standard_vault_only)

    #@record
    #def test_key_encrypt_and_decrypt(self):

    #    key_id = keyvaultid.create_key_id(KEY_VAULT_URI, self.key_name)
    #    plain_text = binascii.b2a_hex(os.urandom(200))

    #    # import key
    #    imported_key = self._import_test_key(key_id)
    #    key_id = keyvaultid.parse_key_id(imported_key.key.kid)

    #    # encrypt with version
    #    result = self.client.encrypt(key_id.base_id, 'RSA-OAEP', plain_text)
    #    cipher_text = result.result

    #    # decrypt with version
    #    result = self.client.decrypt(key_id.base_id, 'RSA-OAEP', cipher_text)
    #    self.assertEqual(plain_text, result.result)

    #    # encrypt with version
    #    result = self.client.encrypt(key_id.id, 'RSA-OAEP', plain_text)
    #    cipher_text = result.result

    #    # decrypt with version
    #    result = self.client.decrypt(key_id.id, 'RSA-OAEP', cipher_text)
    #    self.assertEqual(plain_text, result.result)

    #@record
    #def test_key_wrap_and_unwrap(self):

    #    key_id = keyvaultid.create_key_id(KEY_VAULT_URI, self.key_name)
    #    plain_text = binascii.b2a_hex(os.urandom(200))

    #    # import key
    #    imported_key = self._import_test_key(key_id)
    #    key_id = keyvaultid.parse_key_id(imported_key.key.kid)

    #    # wrap without version
    #    result = self.client.wrap_key(key_id.base_id, 'RSA-OAEP', plain_text)
    #    cipher_text = result.result

    #    # unwrap without version
    #    result = self.client.unwrap_key(key_id.base_id, 'RSA-OAEP', cipher_text)
    #    self.assertEqual(plain_text, result.result)

    #    # wrap with version
    #    result = self.client.wrap_key(key_id.id, 'RSA-OAEP', plain_text)
    #    cipher_text = result.result

    #    # unwrap with version
    #    result = self.client.unwrap_key(key_id.id, 'RSA-OAEP', cipher_text)
    #    self.assertEqual(plain_text, result.result)

    #@record
    #def test_key_sign_and_verify(self):

    #    key_id = keyvaultid.create_key_id(KEY_VAULT_URI, self.key_name)
    #    plain_text = binascii.b2a_hex(os.urandom(200))
    #    md = hashlib.sha256()
    #    md.update(plainText);
    #    digest = md.digest();

    #    # import key
    #    imported_key = self._import_test_key(key_id)
    #    key_id = keyvaultid.parse_key_id(imported_key.key.kid)

    #    # sign without version
    #    signature = self.client.sign(key_id.base_id, 'RS256', digest).result

    #    # verify without version
    #    result = self.client.verify(key_id.base_id, 'RS256', digest, signature)
    #    self.assertTrue(result.value)

    #    # sign with version
    #    signature = self.client.sign(key_id.base_id, 'RS256', digest).result

    #    # verify with version
    #    result = self.client.verify(key_id.id, 'RS256', digest, signature)
    #    self.assertTrue(result.value)

class KeyVaultSecretTest(AzureKeyVaultTestCase):

    def setUp(self):
        super(KeyVaultSecretTest, self).setUp()
        self.secret_name = 'pythonSecret'
        self.secret_value = 'Pa$$w0rd'
        self.list_test_size = 2
        if not self.is_playback():
            self.create_resource_group()

    def tearDown(self):
        super(KeyVaultSecretTest, self).tearDown()
        self.cleanup_created_secrets()

    def cleanup_created_secrets(self):
        if not self.is_playback():
            for secret in self.client.get_secrets(KEY_VAULT_URI):
                id = keyvaultid.parse_secret_id(secret.id)
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
            keyvaultid.parse_secret_id(secret.id)
            attributes = expected[secret.id]
            self.assertEqual(attributes, secret.attributes)
            del expected[secret.id]

    @record
    def test_secret_crud_operations(self):
        
        # create secret
        secret_bundle = self.client.set_secret(KEY_VAULT_URI, self.secret_name, self.secret_value)
        self._validate_secret_bundle(secret_bundle, KEY_VAULT_URI, self.secret_name, self.secret_value)
        created_bundle = secret_bundle
        secret_id = keyvaultid.parse_secret_id(created_bundle.id)

        # get secret without version
        self.assertEqual(created_bundle, self.client.get_secret(secret_id.base_id))

        # get secret with version
        self.assertEqual(created_bundle, self.client.get_secret(secret_id.id))

        def _update_secret(secret_uri):
            updating_bundle = copy.deepcopy(created_bundle)
            updating_bundle.content_type = 'text/plain'
            updating_bundle.attributes.expires = date_parse.parse('2050-02-02T08:00:00.000Z')
            updating_bundle.tags = { 'foo': binascii.b2a_hex(os.urandom(100)) }
            secret_bundle = self.client.update_secret(
                secret_uri, updating_bundle.content_type, updating_bundle.attributes,
                updating_bundle.tags)
            del updating_bundle.value
            updating_bundle.attributes.updated = secret_bundle.attributes.updated
            self.assertEqual(updating_bundle, secret_bundle)
            return secret_bundle

        # update secret without version
        secret_bundle = _update_secret(secret_id.base_id)

        # update secret with version
        secret_bundle = _update_secret(secret_id.id)

        # delete secret
        self.assertEqual(created_bundle, self.client.delete_secret(secret_id.vault, secret_id.name))

        # get secret returns not found
        try:
            self.client.get_secret(secret_id.base_id)
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
                    sid = keyvaultid.parse_secret_id(secret_bundle.id).base_id
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
                    sid = keyvaultid.parse_secret_id(secret_bundle.id).id
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
        if not self.is_playback():
            self.create_resource_group()

    def tearDown(self):
        super(KeyVaultCertificateTest, self).tearDown()
        self.cleanup_created_certificates()

    def cleanup_created_certificates(self):
        if not self.is_playback():
            for cert in self.client.get_certificates(KEY_VAULT_URI):
                id = keyvaultid.parse_certificate_id(cert.id)
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
        pending_id = keyvaultid.parse_certificate_operation_id(pending_cert.id)
        self.assertEqual(pending_id.vault, vault)
        self.assertEqual(pending_id.name, cert_name)

    def _validate_certificate_bundle(self, cert, vault, cert_name, cert_policy):
        cert_id = keyvaultid.parse_certificate_id(cert.id)
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
        keyvaultid.parse_secret_id(cert.sid)
        keyvaultid.parse_key_id(cert.kid)

    def _validate_certificate_list(self, certificates, expected):
        for cert in certificates:
            keyvaultid.parse_certificate_id(cert.id)
            attributes = expected[cert.id]
            self.assertEqual(attributes, cert.attributes)
            del expected[cert.id]

    def _validate_issuer_bundle(self, bundle, vault, name, provider, credentials, org_details):
        self.assertIsNotNone(bundle)
        self.assertIsNotNone(bundle.attributes)
        self.assertIsNotNone(bundle.organization_details)
        self.assertEqual(bundle.provider, provider)

        issuer_id = keyvaultid.parse_certificate_issuer_id(bundle.id)
        self.assertEqual(issuer_id.vault, vault)
        self.assertEqual(issuer_id.name, name)

        if credentials:
            self.assertEqual(bundle.credentials.account_id, credentials.account_id)
        if org_details:
            self.assertEqual(bundle.organization_details, org_details)

    def _validate_certificate_issuer_list(self, issuers, expected):
        for issuer in issuers:
            keyvaultid.parse_certificate_issuer_id(issuer.id)
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
                cert_id = keyvaultid.parse_certificate_operation_id(pending_cert.target)
                break
            elif pending_cert.status.lower() != 'inprogress':
                raise Exception('Unknown status code for pending certificate: {}'.format(pending_cert))
            time.sleep(interval_time)

        # get certificate
        cert_bundle = self.client.get_certificate(cert_id.base_id)
        self._validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

        # get certificate as secret
        secret_bundle = self.client.get_secret(cert_bundle.sid)

        # update certificate
        cert_policy.tags = {'tag1': 'value1'}
        cert_bundle = self.client.update_certificate(cert_id.id, cert_policy)
        self._validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

        # delete certificate
        cert_bundle = self.client.delete_certificate(KEY_VAULT_URI, self.cert_name)
        self._validate_certificate_bundle(cert_bundle, KEY_VAULT_URI, self.cert_name, cert_policy)

        # get certificate returns not found
        try:
            self.client.get_certificate(cert_id.base_id)
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
                    cid = keyvaultid.parse_certificate_id(cert_bundle.id).base_id
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
                    cid = keyvaultid.parse_certificate_id(cert_bundle.id).id
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

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
