# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient
from azure.keyvault.keys._shared import HttpChallengeCache
from devtools_testutils import PowerShellPreparer

from _shared.test_case import KeyVaultTestCase

KeyVaultPreparer = functools.partial(
    PowerShellPreparer,
    "keyvault",
    azure_keyvault_url="https://vaultname.vault.azure.net"
)


class TestCryptoExamples(KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        kwargs["match_body"] = False
        super(TestCryptoExamples, self).__init__(*args, **kwargs)

    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(TestCryptoExamples, self).tearDown()

    def create_key_client(self, vault_uri, **kwargs):
        credential = self.get_credential(KeyClient)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs)

    def get_crypto_client_credential(self):
        return self.get_credential(CryptographyClient)

    # pylint:disable=unused-variable

    @KeyVaultPreparer()
    def test_encrypt_decrypt(self, azure_keyvault_url, **kwargs):
        key_client = self.create_key_client(azure_keyvault_url)
        credential = self.get_crypto_client_credential()
        key_name = self.get_resource_name("crypto-test-encrypt-key")
        key_client.create_rsa_key(key_name)

        # [START create_client]
        # create a CryptographyClient using a KeyVaultKey instance
        key = key_client.get_key(key_name)
        crypto_client = CryptographyClient(key, credential)

        # or a key's id, which must include a version
        key_id = "https://<your vault>.vault.azure.net/keys/<key name>/fe4fdcab688c479a9aa80f01ffeac26"
        crypto_client = CryptographyClient(key_id, credential)
        # [END create_client]

        client = CryptographyClient(key, credential)

        # [START encrypt]
        from azure.keyvault.keys.crypto import EncryptionAlgorithm

        # the result holds the ciphertext and identifies the encryption key and algorithm used
        result = client.encrypt(EncryptionAlgorithm.rsa_oaep, b"plaintext")
        ciphertext = result.ciphertext
        print(result.key_id)
        print(result.algorithm)
        # [END encrypt]

        # [START decrypt]
        from azure.keyvault.keys.crypto import EncryptionAlgorithm

        result = client.decrypt(EncryptionAlgorithm.rsa_oaep, ciphertext)
        print(result.plaintext)
        # [END decrypt]

    @KeyVaultPreparer()
    def test_wrap_unwrap(self, azure_keyvault_url, **kwargs):
        key_client = self.create_key_client(azure_keyvault_url)
        credential = self.get_crypto_client_credential()
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = key_client.create_rsa_key(key_name)
        client = CryptographyClient(key, credential)

        key_bytes = b"5063e6aaa845f150200547944fd199679c98ed6f99da0a0b2dafeaf1f4684496fd532c1c229968cb9dee44957fcef7ccef59ceda0b362e56bcd78fd3faee5781c623c0bb22b35beabde0664fd30e0e824aba3dd1b0afffc4a3d955ede20cf6a854d52cfd"

        # [START wrap_key]
        from azure.keyvault.keys.crypto import KeyWrapAlgorithm

        # the result holds the encrypted key and identifies the encryption key and algorithm used
        result = client.wrap_key(KeyWrapAlgorithm.rsa_oaep, key_bytes)
        encrypted_key = result.encrypted_key
        print(result.key_id)
        print(result.algorithm)
        # [END wrap_key]

        # [START unwrap_key]
        from azure.keyvault.keys.crypto import KeyWrapAlgorithm

        result = client.unwrap_key(KeyWrapAlgorithm.rsa_oaep, encrypted_key)
        key = result.key
        # [END unwrap_key]

    @KeyVaultPreparer()
    def test_sign_verify(self, azure_keyvault_url, **kwargs):
        key_client = self.create_key_client(azure_keyvault_url)
        credential = self.get_crypto_client_credential()
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = key_client.create_rsa_key(key_name)
        client = CryptographyClient(key, credential)

        # [START sign]
        import hashlib
        from azure.keyvault.keys.crypto import SignatureAlgorithm

        digest = hashlib.sha256(b"plaintext").digest()

        # sign returns the signature and the metadata required to verify it
        result = client.sign(SignatureAlgorithm.rs256, digest)
        print(result.key_id)
        print(result.algorithm)
        signature = result.signature
        # [END sign]

        # [START verify]
        from azure.keyvault.keys.crypto import SignatureAlgorithm

        result = client.verify(SignatureAlgorithm.rs256, digest, signature)
        assert result.is_valid
        # [END verify]
