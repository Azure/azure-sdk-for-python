# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.keyvault.keys.crypto.aio import CryptographyClient
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import AsyncKeysClientPreparer, get_decorator
from _shared.test_case_async import KeyVaultTestCase

all_api_versions = get_decorator(is_async=True, only_vault=True)


class TestCryptoExamples(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",all_api_versions)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_encrypt_decrypt_async(self, **kwargs):
        key_client = kwargs.pop("key_client")
        set_bodiless_matcher()
        credential = self.get_credential(CryptographyClient, is_async=True)
        key_name = self.get_resource_name("crypto-test-encrypt-key")
        await key_client.create_rsa_key(key_name)

        # [START create_client]
        # create a CryptographyClient using a KeyVaultKey instance
        key = await key_client.get_key(key_name)
        crypto_client = CryptographyClient(key, credential)

        # or a key's id, which must include a version
        key_id = "https://<your vault>.vault.azure.net/keys/<key name>/fe4fdcab688c479a9aa80f01ffeac26"
        crypto_client = CryptographyClient(key_id, credential)

        # the client and credential should be closed when no longer needed
        # (both are also async context managers)
        await crypto_client.close()
        await credential.close()
        # [END create_client]

        client = CryptographyClient(key, credential, api_version=key_client.api_version)

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

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",all_api_versions)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_wrap_unwrap_async(self, **kwargs):
        key_client = kwargs.pop("key_client")
        set_bodiless_matcher()
        credential = self.get_credential(CryptographyClient, is_async=True)
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = await key_client.create_rsa_key(key_name)
        client = CryptographyClient(key, credential, api_version=key_client.api_version)

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

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",all_api_versions)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_sign_verify_async(self, **kwargs):
        key_client = kwargs.pop("key_client")
        credential = self.get_credential(CryptographyClient, is_async=True)
        key_name = self.get_resource_name("crypto-test-wrapping-key")
        key = await key_client.create_rsa_key(key_name)
        client = CryptographyClient(key, credential, api_version=key_client.api_version)

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
