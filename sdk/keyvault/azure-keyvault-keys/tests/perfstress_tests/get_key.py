# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure_devtools.perfstress_tests import PerfStressTest
from azure.identity import EnvironmentCredential
from azure.identity.aio import EnvironmentCredential as AsyncEnvironmentCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.aio import KeyClient as AsyncKeyClient


class GetKeyTest(PerfStressTest):

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
        await self.async_client.create_rsa_key("livekvtestperfkey")

    async def global_cleanup(self):
        """The global cleanup is run only once."""
        await self.async_client.delete_key("livekvtestperfkey")
        await self.async_client.purge_deleted_key("livekvtestperfkey")
        await super().global_cleanup()

    async def close(self):
        """This is run after cleanup."""
        await self.async_client.close()
        await self.async_credential.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        self.client.get_key("livekvtestperfkey")

    async def run_async(self):
        """The asynchronous perf test."""
        await self.async_client.get_key("livekvtestperfkey")
