# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure_devtools.perfstress_tests import PerfStressTest

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient as SyncAppConfigClient
from azure.search.documents.aio import SearchClient as AsyncAppConfigClient


class SuggestTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        api_key = self.get_from_env("AZURE_SEARCH_API_KEY")
        service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        key = os.getenv("AZURE_SEARCH_API_KEY")
        self.service_client = SyncAppConfigClient(service_endpoint, index_name, AzureKeyCredential(api_key))
        self.async_service_client = AsyncAppConfigClient(service_endpoint, index_name, AzureKeyCredential(api_key))

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    def run_sync(self):
        self.service_client.suggest(search_text="mot", suggester_name="sg")

    async def run_async(self):
        await self.async_service_client.suggest(search_text="mot", suggester_name="sg")
