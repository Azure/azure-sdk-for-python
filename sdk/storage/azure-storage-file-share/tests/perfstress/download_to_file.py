# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile

from ._test_base import _ShareTest


class DownloadToFileTest(_ShareTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        file_name = "downloadtest"
        self.sharefile_client = self.share_client.get_file_client(file_name)
        self.async_sharefile_client = self.async_share_client.get_file_client(file_name)

    async def global_setup(self):
        await super().global_setup()
        data = b'a' * self.args.size
        await self.async_sharefile_client.upload_file(data)

    def run_sync(self):
        with tempfile.TemporaryFile() as fp:
            stream = self.sharefile_client.download_file(max_concurrency=self.args.parallel)
            stream.readinto(fp)

    async def run_async(self):
        with tempfile.TemporaryFile() as fp:
            stream = await self.async_sharefile_client.download_file(max_concurrency=self.args.parallel)
            await stream.readinto(fp)

    async def close(self):
        await self.async_sharefile_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(DownloadToFileTest, DownloadToFileTest).add_arguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of files to download.  Default is 10240.', default=10240)
