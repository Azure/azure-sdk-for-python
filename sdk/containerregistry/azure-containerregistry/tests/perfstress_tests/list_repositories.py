# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure_devtools.perfstress_tests import PerfStressTest
from azure.containerregistry import ContainerRegistryClient
from azure.containerregistry.aio import ContainerRegistryClient as AsyncContainerRegistryClient


class ListRepositoriesTest(PerfStressTest):

    def __init__(self, arguments):
        super().__init__(arguments)

        # Create clients
        account_url = self.get_from_env("CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT")
        audience = "https://management.azure.com"
        self.anon_client = ContainerRegistryClient(endpoint=account_url, credential=None, audience=audience)
        self.async_anon_client = AsyncContainerRegistryClient(endpoint=account_url, credential=None, audience=audience)

    async def close(self):
        await self.async_anon_client.close()
        await super().close()

    def run_sync(self):
        for repository_name in self.anon_client.list_repository_names():
            self.anon_client.get_repository_properties(repository_name)

    async def run_async(self):
        async for repository_name in self.async_anon_client.list_repository_names():
            await self.async_anon_client.get_repository_properties(repository_name)
