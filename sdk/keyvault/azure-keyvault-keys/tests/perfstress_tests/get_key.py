# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure_devtools.perfstress_tests import PerfStressTest
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.aio import KeyClient as AsyncKeyClient


class GetKeyTest(PerfStressTest):

    def __init__(self, arguments):
        super().__init__(arguments)

        # Auth configuration
        self.credential = DefaultAzureCredential()
        self.async_credential = AsyncDefaultAzureCredential()

        # Create clients
        vault_url = self.get_from_env("AZURE_KEYVAULT_URL")
        self.client = KeyClient(vault_url, self.credential, **self._client_kwargs)
        self.async_client = AsyncKeyClient(vault_url, self.async_credential, **self._client_kwargs)
        self.key_name = "livekvtestgetkeyperfkey"

    async def global_setup(self):
        """The global setup is run only once."""
        await super().global_setup()
        await self.async_client.create_rsa_key(self.key_name)

    async def global_cleanup(self):
        """The global cleanup is run only once."""
        await self.async_client.delete_key(self.key_name)
        await self.async_client.purge_deleted_key(self.key_name)
        await super().global_cleanup()

    async def close(self):
        """This is run after cleanup."""
        await self.async_client.close()
        await self.async_credential.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        self.client.get_key(self.key_name)

    async def run_async(self):
        """The asynchronous perf test."""
        await self.async_client.get_key(self.key_name)
