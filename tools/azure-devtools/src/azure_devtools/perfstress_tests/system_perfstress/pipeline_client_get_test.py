# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.core import PipelineClient
from azure.core import AsyncPipelineClient
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse

from azure_devtools.perfstress_tests import PerfStressTest


class PipelineClientGetTest(PerfStressTest):
    pipeline_client: PipelineClient = None
    async_pipeline_client: AsyncPipelineClient = None
    _first_run = True

    def __init__(self, arguments):
        super().__init__(arguments)
        self.pipeline_client = PipelineClient(base_url=self.args.url, **self._client_kwargs)
        self.async_pipeline_client = AsyncPipelineClient(base_url=self.args.url, **self._client_kwargs)

    def run_sync(self):
        if self._first_run:
            for _ in range(self.args.first_run_extra_requests):
                self._send_request_sync()
            self._first_run = False
        self._send_request_sync()

    async def run_async(self):
        if self._first_run:
            for _ in range(self.args.first_run_extra_requests):
                await self._send_request_async()
            self._first_run = False
        await self._send_request_async()

    def _send_request_sync(self):
        request = self.pipeline_client.get(self.args.url)
        response: PipelineResponse = self.pipeline_client._pipeline.run(request)
        # Consume response body
        http_response: HttpResponse = response.http_response
        data = http_response.body()

    async def _send_request_async(self):
        request = self.async_pipeline_client.get(self.args.url)
        response: PipelineResponse = await self.async_pipeline_client._pipeline.run(request)
        # Consume response body
        http_response: HttpResponse = response.http_response
        data = http_response.body()

    async def close(self):
        await self.async_pipeline_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("--first-run-extra-requests", type=int, default=0, help='Extra requests to send on first run. ' +
            'Simulates SDKs which require extra requests (like authentication) on first API call.')
        parser.add_argument("-u", "--url", required=True)
