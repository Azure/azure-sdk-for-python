# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.keyvault.keys.crypto.aio import CryptographyClient
from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer
from _shared.test_case_async import KeyVaultTestCase
from crypto_client_preparer_async import CryptoClientPreparer


class TestCryptoExamples(KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        kwargs["match_body"] = False
        super(TestCryptoExamples, self).__init__(*args, **kwargs)

    # pylint:disable=unused-variable

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @CryptoClientPreparer()
    async def test_encrypt_decrypt_async(self, key_client, credential, **kwargs):
        key_name = self.get_resource_name("crypto-test-encrypt-key")
        await key_client.create_rsa_key(key_name)

        # [START create_client]
        # create a CryptographyClient using a KeyVaultKey instance
        key = await key_client.get_key(key_name)
        crypto_client = CryptographyClient(key, credential)

        # or a key's id, which must include a version
        key_id = "https://<your vault>.vault.azure.net/keys/<key name>/fe4fdcab688c479a9aa80f01ffeac26"
        crypto_client = CryptographyClient(key_id, credential)
        # [END create_client]

        client = CryptographyClient(key, credential)

        # [START encrypt]
        from azure.keyvault.keys.crypto import EncryptionAlgorithm

        # the result holds the ciphertext and identifies the encryption key and algorithm used
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

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @CryptoClientPreparer()
    async def test_wrap_unwrap_async(self, key_client, credential, **kwargs):
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = await key_client.create_rsa_key(key_name)
        client = CryptographyClient(key, credential)

        key_bytes = b"5063e6aaa845f150200547944fd199679c98ed6f99da0a0b2dafeaf1f4684496fd532c1c229968cb9dee44957fcef7ccef59ceda0b362e56bcd78fd3faee5781c623c0bb22b35beabde0664fd30e0e824aba3dd1b0afffc4a3d955ede20cf6a854d52cfd"

        # [START wrap_key]
        from azure.keyvault.keys.crypto import KeyWrapAlgorithm

        # wrap returns a tuple with the wrapped bytes and the metadata required to unwrap the key
        result = await client.wrap_key(KeyWrapAlgorithm.rsa_oaep, key_bytes)
        print(result.key_id)
        print(result.algorithm)
        encrypted_key = result.encrypted_key
        # [END wrap_key]

        # [START unwrap_key]
        from azure.keyvault.keys.crypto import KeyWrapAlgorithm

        result = await client.unwrap_key(KeyWrapAlgorithm.rsa_oaep, encrypted_key)
        # [END unwrap_key]

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @CryptoClientPreparer()
    async def test_sign_verify_async(self, key_client, credential, **kwargs):
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = await key_client.create_rsa_key(key_name)
        client = CryptographyClient(key, credential)

        # [START sign]
        import hashlib
        from azure.keyvault.keys.crypto import SignatureAlgorithm

        digest = hashlib.sha256(b"plaintext").digest()

        # sign returns the signature and the metadata required to verify it
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
