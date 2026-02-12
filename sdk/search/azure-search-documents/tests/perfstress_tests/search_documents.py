# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from devtools_testutils.perfstress_tests import PerfStressTest

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient as SyncClient
from azure.search.documents.aio import SearchClient as AsyncClient


class SearchDocumentsTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        api_key = self.get_from_env("AZURE_SEARCH_API_KEY")
        service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        key = os.getenv("AZURE_SEARCH_API_KEY")
        self.service_client = SyncClient(service_endpoint, index_name, AzureKeyCredential(api_key))
        self.async_service_client = AsyncClient(service_endpoint, index_name, AzureKeyCredential(api_key))

    @staticmethod
    def add_arguments(parser):
        super(SearchDocumentsTest, SearchDocumentsTest).add_arguments(parser)
        parser.add_argument(
            "--num-documents",
            nargs="?",
            type=int,
            help="The number of results expect to be returned.",
            default=-1,
        )

    async def global_setup(self):
        await super().global_setup()

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    def run_sync(self):
        if self.args.num_documents == -1:
            results = len(self.service_client.search(search_text="luxury"))
        else:
            results = len(self.service_client.search(search_text="luxury", top=self.args.num_documents))

    async def run_async(self):
        if self.args.num_documents == -1:
            results = await self.async_service_client.search(search_text="luxury")
        else:
            results = await self.async_service_client.search(search_text="luxury", top=self.args.num_documents)
        count = 0
        async for result in results:
            count += count
