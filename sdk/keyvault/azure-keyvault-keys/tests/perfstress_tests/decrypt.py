# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure_devtools.perfstress_tests import PerfStressTest
from azure.identity import EnvironmentCredential
from azure.identity.aio import EnvironmentCredential as AsyncEnvironmentCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.aio import KeyClient as AsyncKeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
from azure.keyvault.keys.crypto.aio import CryptographyClient as AsyncCryptographyClient


class DecryptTest(PerfStressTest):

    def __init__(self, arguments):
        super().__init__(arguments)

        # Auth configuration
        self.credential = EnvironmentCredential()
        self.async_credential = AsyncEnvironmentCredential()

        # Create clients
        vault_url = self.get_from_env("AZURE_KEYVAULT_URL")
        self.client = KeyClient(vault_url, self.credential)
        self.async_client = AsyncKeyClient(vault_url, self.async_credential)

    async def global_setup(self):
        """The global setup is run only once."""
        await super().global_setup()
        rsa_key = await self.async_client.create_rsa_key("livekvtestdecryptperfkey")
        self.crypto_client = CryptographyClient(rsa_key, self.credential)
        self.async_crypto_client = AsyncCryptographyClient(rsa_key, self.async_credential)

        self.test_algorithm = EncryptionAlgorithm.rsa_oaep_256
        plaintext = os.urandom(32)
        self.ciphertext = self.crypto_client.encrypt(self.test_algorithm, plaintext).ciphertext
        

    async def global_cleanup(self):
        """The global cleanup is run only once."""
        await self.async_client.delete_key("livekvtestdecryptperfkey")
        await self.async_client.purge_deleted_key("livekvtestdecryptperfkey")
        await super().global_cleanup()

    async def close(self):
        """This is run after cleanup."""
        await self.async_client.close()
        await self.async_crypto_client.close()
        await self.async_credential.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        self.crypto_client.decrypt(self.test_algorithm, self.ciphertext)

    async def run_async(self):
        """The asynchronous perf test."""
        await self.async_crypto_client.decrypt(self.test_algorithm, self.ciphertext)
