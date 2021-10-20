# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure_devtools.perfstress_tests import PerfStressTest
from azure.containerregistry import ContainerRegistryClient
from azure.containerregistry.aio import ContainerRegistryClient as AsyncContainerRegistryClient


class ListArtifactsTest(PerfStressTest):

    def __init__(self, arguments):
        super().__init__(arguments)

        # Create clients
        account_url = self.get_from_env("CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT")
        audience = "https://management.azure.com"
        self.anon_client = ContainerRegistryClient(endpoint=account_url, credential=None, audience=audience)
        self.async_anon_client = AsyncContainerRegistryClient(endpoint=account_url, credential=None, audience=audience)       
        self.repository = "node"

    async def global_setup(self):
        await super().global_setup()

    async def close(self):
        await self.async_anon_client.close()
        await super().close()

    def run_sync(self):
        for manifest in self.anon_client.list_manifest_properties(self.repository):
            self.anon_client.get_manifest_properties(self.repository, manifest.digest)

    async def run_async(self):
        async for manifest in self.async_anon_client.list_manifest_properties(self.repository):
            await self.async_anon_client.get_manifest_properties(self.repository, manifest.digest)
