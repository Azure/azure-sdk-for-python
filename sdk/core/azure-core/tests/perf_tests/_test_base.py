# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from devtools_testutils.perfstress_tests import PerfStressTest

from azure.core import PipelineClient, AsyncPipelineClient
from azure.core.pipeline.transport import (
    RequestsTransport,
    AioHttpTransport,
    AsyncioRequestsTransport,
)

from azure.storage.blob._shared.authentication import SharedKeyCredentialPolicy


class _ServiceTest(PerfStressTest):
    transport = None
    async_transport = None

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_endpoint = self.get_from_env("AZURE_STORAGE_ACCOUNT_ENDPOINT")
        self.account_name = self.get_from_env("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = self.get_from_env("AZURE_STORAGE_ACCOUNT_KEY")
        self.container_name = self.get_from_env("AZURE_STORAGE_CONTAINER_NAME")
        async_transport_types = {"aiohttp": AioHttpTransport, "requests": AsyncioRequestsTransport}
        sync_transport_types = {"requests": RequestsTransport}

        # defaults transports
        sync_transport = RequestsTransport
        async_transport = AioHttpTransport

        # if transport is specified, use that
        if self.args.transport:
            # if sync, override sync default
            if self.args.sync:
                try:
                    sync_transport = sync_transport_types[self.args.transport]
                except:
                    raise ValueError(f"Invalid sync transport:{self.args.transport}\n Valid options are:\n- requests\n")
            # if async, override async default
            else:
                try:
                    async_transport = async_transport_types[self.args.transport]
                except:
                    raise ValueError(f"Invalid async transport:{self.args.transport}\n Valid options are:\n- aiohttp\n- requests\n")

        self.pipeline_client = PipelineClient(
            self.account_endpoint, transport=sync_transport(), policies=[
                SharedKeyCredentialPolicy(self.account_name, self.account_key)
            ]
        )
        self.async_pipeline_client = AsyncPipelineClient(self.account_endpoint, transport=async_transport(), policies=[
                SharedKeyCredentialPolicy(self.account_name, self.account_key)
            ]
        )

    async def close(self):
        self.pipeline_client.close()
        await self.async_pipeline_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument(
            '--transport',
            nargs='?',
            type=str,
            help="""Underlying HttpTransport type. Defaults to `aiohttp` if async, `requests` if sync. Other possible values for async:\n"""
                 """ - `requests`\n""",
            default=None
        )
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)
