# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
import os

from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer
from keys_async_preparer import AsyncVaultClientPreparer
from keys_async_test_case import AsyncKeyVaultTestCase


class TestCryptoExamples(AsyncKeyVaultTestCase):
    # pylint:disable=unused-variable

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_encrypt_decrypt_async(self, vault_client, **kwargs):
        key_client = vault_client.keys
        key_name = self.get_resource_name("crypto-test-encrypt-key")
        key = await key_client.create_rsa_key(key_name)
        client = vault_client.get_cryptography_client(key)

        # [START encrypt]

        from azure.keyvault.keys.crypto import EncryptionAlgorithm

        # encrypt returns a tuple with the ciphertext and the metadata required to decrypt it
        result = await client.encrypt(EncryptionAlgorithm.rsa_oaep, b"plaintext")
        print(result.key_id)
        print(result.algorithm)
        ciphertext = result.ciphertext

        # [END encrypt]

        # [START decrypt]

        from azure.keyvault.keys.crypto import EncryptionAlgorithm

        result = await client.decrypt(EncryptionAlgorithm.rsa_oaep, ciphertext)
        print(result.plaintext)

        # [END decrypt]

        pass

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_wrap_unwrap_async(self, vault_client, **kwargs):
        key_client = vault_client.keys
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = await key_client.create_rsa_key(key_name)
        client = vault_client.get_cryptography_client(key)

        key_bytes = b"5063e6aaa845f150200547944fd199679c98ed6f99da0a0b2dafeaf1f4684496fd532c1c229968cb9dee44957fcef7ccef59ceda0b362e56bcd78fd3faee5781c623c0bb22b35beabde0664fd30e0e824aba3dd1b0afffc4a3d955ede20cf6a854d52cfd"

        # [START wrap]

        from azure.keyvault.keys.crypto import KeyWrapAlgorithm

        # wrap returns a tuple with the wrapped bytes and the metadata required to unwrap the key
        result = await client.wrap_key(KeyWrapAlgorithm.rsa_oaep, key_bytes)
        print(result.key_id)
        print(result.algorithm)
        encrypted_key = result.encrypted_key

        # [END wrap]

        # [START unwrap]
        from azure.keyvault.keys.crypto import KeyWrapAlgorithm

        result = await client.unwrap_key(KeyWrapAlgorithm.rsa_oaep, encrypted_key)

        # [END unwrap]

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_sign_verify_async(self, vault_client, **kwargs):
        key_client = vault_client.keys
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = await key_client.create_rsa_key(key_name)
        client = vault_client.get_cryptography_client(key)

        # [START sign]

        import hashlib
        from azure.keyvault.keys.crypto import SignatureAlgorithm

        digest = hashlib.sha256(b"plaintext").digest()

        # sign returns a tuple with the signature and the metadata required to verify it
        result = await client.sign(SignatureAlgorithm.rs256, digest)
        print(result.key_id)
        print(result.algorithm)
        signature = result.signature

        # [END sign]

        # [START verify]

        from azure.keyvault.keys.crypto import SignatureAlgorithm

        verified = await client.verify(SignatureAlgorithm.rs256, digest, signature)
        assert verified.is_valid

        # [END verify]
