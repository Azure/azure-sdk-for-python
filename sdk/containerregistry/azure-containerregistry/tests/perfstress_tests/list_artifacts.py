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

        endpoint = self.get_from_env("CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT")
        audience = "https://management.azure.com"
        self.anon_client = ContainerRegistryClient(endpoint=endpoint, credential=None, audience=audience)
        self.async_anon_client = AsyncContainerRegistryClient(endpoint=endpoint, credential=None, audience=audience)       
        self.repository = "node"

    async def close(self):
        await self.async_anon_client.close()
        await super().close()

    def run_sync(self):
        for _ in self.anon_client.list_manifest_properties(self.repository):
            pass

    async def run_async(self):
        async for _ in self.async_anon_client.list_manifest_properties(self.repository):
            pass
