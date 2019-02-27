import unittest
from azure.keyvault import KeyVaultId, HttpBearerChallengeCache, HttpBearerChallenge
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

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
        expected = self._get_expected('certificates', 'myvault', 'myissuer')
        res = KeyVaultId.create_certificate_issuer_id('https://myvault.vault.azure.net', 'myissuer')
        self.assertEqual(res.__dict__, expected)

    def test_parse_certificate_issuer_id(self):
        expected = self._get_expected('certificates', 'myvault', 'myissuer')
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
