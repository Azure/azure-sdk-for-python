# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.core import PipelineClient
from azure.core import AsyncPipelineClient
from azure.core.pipeline import PipelineResponse

from azure_devtools.perfstress_tests import PerfStressTest


class PipelineClientGetTest(PerfStressTest):
    pipeline_client: PipelineClient = None
    async_pipeline_client: AsyncPipelineClient = None

    def __init__(self, arguments):
        super().__init__(arguments)
        self.pipeline_client = PipelineClient(base_url=self.args.url, **self._client_kwargs)
        self.async_pipeline_client = AsyncPipelineClient(base_url=self.args.url, **self._client_kwargs)

    def run_sync(self):
        # TODO: Should HttpRequest be created each time or reused?
        # TODO: Should self.args.url be set as base_url, passed to get(), or both?
        request = self.pipeline_client.get(self.args.url)
        response: PipelineResponse = self.pipeline_client._pipeline.run(request)
        # TODO: Consume response body

    async def run_async(self):
        # TODO: Should HttpRequest be created each time or reused?
        # TODO: Should self.args.url be set as base_url, passed to get(), or both?
        request = self.async_pipeline_client.get(self.args.url)
        response: PipelineResponse = await self.async_pipeline_client._pipeline.run(request)
        # TODO: Consume response body

    async def close(self):
        await self.async_pipeline_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("-u", "--url", required=True)
