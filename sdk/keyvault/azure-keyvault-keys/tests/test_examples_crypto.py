# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.keyvault.keys.crypto import CryptographyClient
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher

from _shared.test_case import KeyVaultTestCase
from _test_case import KeysClientPreparer, get_decorator
from _keys_test_case import KeysTestCase

all_api_versions = get_decorator(only_vault=True)

class TestCryptoExamples(KeyVaultTestCase, KeysTestCase):
    @pytest.mark.parametrize("api_version,is_hsm", all_api_versions)
    @KeysClientPreparer()
    @recorded_by_proxy
    def test_encrypt_decrypt(self, key_client, **kwargs):
        set_bodiless_matcher()
        credential = self.get_credential(CryptographyClient)
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

        client = CryptographyClient(key, credential, api_version=key_client.api_version)

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

    @pytest.mark.parametrize("api_version,is_hsm", all_api_versions)
    @KeysClientPreparer()
    @recorded_by_proxy
    def test_wrap_unwrap(self, key_client, **kwargs):
        set_bodiless_matcher()
        credential = self.get_credential(CryptographyClient)
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = key_client.create_rsa_key(key_name)
        client = CryptographyClient(key, credential, api_version=key_client.api_version)

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

    @pytest.mark.parametrize("api_version,is_hsm", all_api_versions)
    @KeysClientPreparer()
    @recorded_by_proxy
    def test_sign_verify(self, key_client, **kwargs):
        set_bodiless_matcher()
        credential = self.get_credential(CryptographyClient)
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = key_client.create_rsa_key(key_name)
        client = CryptographyClient(key, credential, api_version=key_client.api_version)

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
