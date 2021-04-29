# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid

from azure_devtools.perfstress_tests import PerfStressTest

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.filedatalake import DataLakeServiceClient as SyncDataLakeServiceClient
from azure.storage.filedatalake.aio import DataLakeServiceClient as AsyncDataLakeServiceClient


class _ServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")
        if not _ServiceTest.service_client or self.args.no_client_share:
            _ServiceTest.service_client = SyncDataLakeServiceClient.from_connection_string(conn_str=connection_string)
            _ServiceTest.async_service_client = AsyncDataLakeServiceClient.from_connection_string(conn_str=connection_string)
        self.service_client = _ServiceTest.service_client
        self.async_service_client =_ServiceTest.async_service_client

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument('-c', '--max-concurrency', nargs='?', type=int, help='Maximum number of concurrent threads used for data transfer. Defaults to 1', default=1)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)


class _FileSystemTest(_ServiceTest):
    fs_name = "perfstress-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)
        self.fs_client = self.service_client.get_file_system_client(self.fs_name)
        self.async_fs_client = self.async_service_client.get_file_system_client(self.fs_name)

    async def global_setup(self):
        await super().global_setup()
        await self.async_fs_client.create_file_system()

    async def global_cleanup(self):
        await self.async_fs_client.delete_file_system()
        await super().global_cleanup()

    async def close(self):
        await self.async_fs_client.close()
        await super().close()


class _FileTest(_FileSystemTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        file_name = "sharefiletest-" + str(uuid.uuid4())
        self.file_client = self.fs_client.get_file_client(file_name)
        self.async_file_client = self.async_fs_client.get_file_client(file_name)

    async def close(self):
        await self.async_file_client.close()
        await super().close()
