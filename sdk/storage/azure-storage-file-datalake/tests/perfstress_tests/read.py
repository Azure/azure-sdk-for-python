# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from devtools_testutils.perfstress_tests import get_random_bytes, WriteStream

from ._test_base import _FileSystemTest


class DownloadTest(_FileSystemTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        file_name = "downloadtest"
        self.file_client = self.fs_client.get_file_client(file_name)
        self.async_file_client = self.async_fs_client.get_file_client(file_name)
        self.download_stream = WriteStream()

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        await self.async_file_client.create_file()
        await self.async_file_client.upload_data(data, overwrite=True)

    def run_sync(self):
        self.download_stream.reset()
        stream = self.file_client.download_file(max_concurrency=self.args.max_concurrency)
        stream.readinto(self.download_stream)

    async def run_async(self):
        self.download_stream.reset()
        stream = await self.async_file_client.download_file(max_concurrency=self.args.max_concurrency)
        await stream.readinto(self.download_stream)

    async def close(self):
        await self.async_file_client.close()
        await super().close()
