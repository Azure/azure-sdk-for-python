# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
import os

from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer
from keys_preparer import VaultClientPreparer
from keys_test_case import KeyVaultTestCase


class TestCryptoExamples(KeyVaultTestCase):
    # pylint:disable=unused-variable

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_encrypt_decrypt(self, vault_client, **kwargs):
        key_client = vault_client.keys
        key_name = self.get_resource_name("crypto-test-encrypt-key")
        key = key_client.create_rsa_key(key_name)
        client = vault_client.get_cryptography_client(key)

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

        pass

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_wrap_unwrap(self, vault_client, **kwargs):
        key_client = vault_client.keys
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = key_client.create_rsa_key(key_name)
        client = vault_client.get_cryptography_client(key)

        key_bytes = b"5063e6aaa845f150200547944fd199679c98ed6f99da0a0b2dafeaf1f4684496fd532c1c229968cb9dee44957fcef7ccef59ceda0b362e56bcd78fd3faee5781c623c0bb22b35beabde0664fd30e0e824aba3dd1b0afffc4a3d955ede20cf6a854d52cfd"

        # [START wrap]

        from azure.keyvault.keys.crypto import KeyWrapAlgorithm

        # the result holds the encrypted key and identifies the encryption key and algorithm used
        result = client.wrap_key(KeyWrapAlgorithm.rsa_oaep, key_bytes)
        encrypted_key = result.encrypted_key
        print(result.key_id)
        print(result.algorithm)

        # [END wrap]

        # [START unwrap]
        from azure.keyvault.keys.crypto import KeyWrapAlgorithm

        result = client.unwrap_key(KeyWrapAlgorithm.rsa_oaep, encrypted_key)
        key = result.key

        # [END unwrap]

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @VaultClientPreparer()
    def test_sign_verify(self, vault_client, **kwargs):
        key_client = vault_client.keys
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = key_client.create_rsa_key(key_name)
        client = vault_client.get_cryptography_client(key)

        # [START sign]

        import hashlib
        from azure.keyvault.keys.crypto import SignatureAlgorithm

        digest = hashlib.sha256(b"plaintext").digest()

        # sign returns a tuple with the signature and the metadata required to verify it
        result = client.sign(SignatureAlgorithm.rs256, digest)

        # the result contains the signature and identifies the key and algorithm used
        print(result.key_id)
        print(result.algorithm)
        signature = result.signature

        # [END sign]

        # [START verify]

        from azure.keyvault.keys.crypto import SignatureAlgorithm

        verified = client.verify(SignatureAlgorithm.rs256, digest, signature)
        assert verified.is_valid

        # [END verify]
