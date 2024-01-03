# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from devtools_testutils.perfstress_tests import PerfStressTest, get_random_bytes

from azure.core import PipelineClient, AsyncPipelineClient
from azure.core.pipeline.transport import (
    RequestsTransport,
    AioHttpTransport,
    AsyncioRequestsTransport,
)

from azure.storage.blob._shared.authentication import SharedKeyCredentialPolicy
from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient

from .key_wrapper import KeyWrapper


class _ServiceTest(PerfStressTest):
    transport = None
    async_transport = None

    def __init__(self, arguments):
        super().__init__(arguments)
        self.account_endpoint = self.get_from_env("AZURE_STORAGE_ACCOUNT_ENDPOINT")
        self.account_name = self.get_from_env("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = self.get_from_env("AZURE_STORAGE_ACCOUNT_KEY")
        self.container_name = self.get_from_env("AZURE_STORAGE_CONTAINER_NAME")
        if self.args.transport_type == 0:
            transport = RequestsTransport()
            async_transport = AioHttpTransport()
        elif self.args.transport_type == 1:
            pass    # TODO
            # for corehttp
            #if self.args.sync == "httpx":
            #    transport = HttpXTransport
        self.pipeline_client = PipelineClient(
            self.account_endpoint, transport=transport, policies=[
                SharedKeyCredentialPolicy(self.account_name, self.account_key)
            ]
        )
        self.async_pipeline_client = AsyncPipelineClient(async_transport, policies=[])

    async def close(self):
        self.pipeline_client.close()
        await self.async_pipeline_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument('--transport-type', nargs='?', type=int, help='Underlying HttpTransport type. Defaults to 0 (AioHttpTransport if async, RequestsTransport if sync).', default=0)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)


#class _ContainerTest(_ServiceTest):
#    container_name = "perfstress-" + str(uuid.uuid4())
#
#    def __init__(self, arguments):
#        super().__init__(arguments)
#        self.container_client = self.service_client.get_container_client(self.container_name)
#        self.async_container_client = self.async_service_client.get_container_client(self.container_name)
#
#    async def global_setup(self):
#        await super().global_setup()
#        await self.async_container_client.create_container()
#
#    async def global_cleanup(self):
#        await self.async_container_client.delete_container()
#        await super().global_cleanup()
#
#    async def close(self):
#        await self.async_container_client.close()
#        await super().close()


#class _BlobTest(_ContainerTest):
#    def __init__(self, arguments):
#        super().__init__(arguments)
#        blob_name = "blobtest-" + str(uuid.uuid4())
#        self.blob_client = self.container_client.get_blob_client(blob_name)
#        self.async_blob_client = self.async_container_client.get_blob_client(blob_name)
#
#    async def close(self):
#        await self.async_blob_client.close()
#        await super().close()
