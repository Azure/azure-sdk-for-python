# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid

from devtools_testutils.perfstress_tests import PerfStressTest

from azure.storage.fileshare import ShareServiceClient as SyncShareServiceClient
from azure.storage.fileshare.aio import ShareServiceClient as AsyncShareServiceClient


class _ServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")
        kwargs = {}
        if self.args.max_range_size:
            kwargs['max_range_size'] = self.args.max_range_size
        if not _ServiceTest.service_client or self.args.no_client_share:
            _ServiceTest.service_client = SyncShareServiceClient.from_connection_string(conn_str=connection_string, **kwargs)
            _ServiceTest.async_service_client = AsyncShareServiceClient.from_connection_string(conn_str=connection_string, **kwargs)
        self.service_client = _ServiceTest.service_client
        self.async_service_client =_ServiceTest.async_service_client

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument('-r', '--max-range-size', nargs='?', type=int, help='Maximum size of data uploading in single HTTP PUT. Defaults to 4*1024*1024', default=4*1024*1024)
        parser.add_argument('-c', '--max-concurrency', nargs='?', type=int, help='Maximum number of concurrent threads used for data transfer. Defaults to 1', default=1)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)


class _ShareTest(_ServiceTest):
    share_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        self.share_client = self.service_client.get_share_client(self.share_name)
        self.async_share_client = self.async_service_client.get_share_client(self.share_name)

    async def global_setup(self):
        await super().global_setup()
        self.share_client.create_share()

    async def global_cleanup(self):
        self.share_client.delete_share()
        await super().global_cleanup()

    async def close(self):
        await self.async_share_client.close()
        await super().close()


class _FileTest(_ShareTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        file_name = "sharefiletest-" + str(uuid.uuid4())
        self.sharefile_client = self.share_client.get_file_client(file_name)
        self.async_sharefile_client = self.async_share_client.get_file_client(file_name)

    async def close(self):
        await self.async_sharefile_client.close()
        await super().close()
