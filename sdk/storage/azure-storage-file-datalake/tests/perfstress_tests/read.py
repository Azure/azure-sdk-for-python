# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import get_random_bytes

from ._test_base import _FileSystemTest


class DownloadTest(_FileSystemTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        file_name = "downloadtest"
        self.file_client = self.fs_client.get_file_client(file_name)
        self.async_file_client = self.async_fs_client.get_file_client(file_name)

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        await self.async_file_client.upload_data(data)

    def run_sync(self):
        stream = self.file_client.download_file(max_concurrency=self.args.max_concurrency)
        stream.readall()

    async def run_async(self):
        stream = await self.async_file_client.download_file(max_concurrency=self.args.max_concurrency)
        await stream.readall()

    async def close(self):
        await self.async_file_client.close()
        await super().close()
