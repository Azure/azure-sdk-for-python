# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid

from azure_devtools.perfstress_tests import PerfStressTest

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient


class _ServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")
        kwargs = {}
        kwargs['max_single_put_size'] = self.args.max_put_size
        kwargs['max_block_size'] = self.args.max_block_size
        kwargs['min_large_block_upload_threshold'] = self.args.buffer_threshold
        if not _ServiceTest.service_client or self.args.no_client_share:
            _ServiceTest.service_client = SyncBlobServiceClient.from_connection_string(conn_str=connection_string, **kwargs)
            _ServiceTest.async_service_client = AsyncBlobServiceClient.from_connection_string(conn_str=connection_string, **kwargs)
        self.service_client = _ServiceTest.service_client
        self.async_service_client =_ServiceTest.async_service_client

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument('--max-put-size', nargs='?', type=int, help='Maximum size of data uploading in single HTTP PUT. Defaults to 64*1024*1024', default=64*1024*1024)
        parser.add_argument('--max-block-size', nargs='?', type=int, help='Maximum size of data in a block within a blob. Defaults to 4*1024*1024', default=4*1024*1024)
        parser.add_argument('--buffer-threshold', nargs='?', type=int, help='Minimum block size to prevent full block buffering. Defaults to 4*1024*1024+1', default=4*1024*1024+1)
        parser.add_argument('--max-concurrency', nargs='?', type=int, help='Maximum number of concurrent threads used for data transfer. Defaults to 1', default=1)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)


class _ContainerTest(_ServiceTest):
    container_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        self.container_client = self.service_client.get_container_client(self.container_name)
        self.async_container_client = self.async_service_client.get_container_client(self.container_name)

    async def global_setup(self):
        await super().global_setup()
        await self.async_container_client.create_container()

    async def global_cleanup(self):
        await self.async_container_client.delete_container()
        await super().global_cleanup()

    async def close(self):
        await self.async_container_client.close()
        await super().close()


class _BlobTest(_ContainerTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        blob_name = "blobtest-" + str(uuid.uuid4())
        self.blob_client = self.container_client.get_blob_client(blob_name)
        self.async_blob_client = self.async_container_client.get_blob_client(blob_name)

    async def close(self):
        await self.async_blob_client.close()
        await super().close()
