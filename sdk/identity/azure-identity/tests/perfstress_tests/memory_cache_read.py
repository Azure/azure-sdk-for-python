# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure_devtools.perfstress_tests import PerfStressTest

from azure.identity import ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class MemoryCacheRead(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        client_id = self.get_from_env("AZURE_CLIENT_ID")
        tenant_id = self.get_from_env("AZURE_TENANT_ID")
        secret = self.get_from_env("AZURE_CLIENT_SECRET")
        self.credential = ClientSecretCredential(tenant_id, client_id, secret)
        self.async_credential = AsyncClientSecretCredential(tenant_id, client_id, secret)
        self.scope = "https://vault.azure.net/.default"

    async def global_setup(self):
        """Cache an access token"""

        await super().global_setup()
        self.credential.get_token(self.scope)
        await self.async_credential.get_token(self.scope)

    def run_sync(self):
        self.credential.get_token(self.scope)

    async def run_async(self):
        await self.async_credential.get_token(self.scope)

    async def close(self):
        await self.async_credential.close()
        await super().close()
