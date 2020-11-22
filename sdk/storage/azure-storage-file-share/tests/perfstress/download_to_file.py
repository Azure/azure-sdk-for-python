
import os
import tempfile

from ._test_base import _ShareTest


class DownloadToFileTest(_ShareTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        file_name = "downloadtest"
        self.sharefile_client = self.share_client.get_file_client(file_name)
        self.async_sharefile_client = self.async_share_client.get_file_client(file_name)

    async def GlobalSetupAsync(self):
        await super().GlobalSetupAsync()
        data = b'a' * self.Arguments.size
        await self.async_sharefile_client.upload_file(data)

    def Run(self):
        with tempfile.TemporaryFile() as fp:
            stream = self.sharefile_client.download_file(max_concurrency=self.Arguments.parallel)
            stream.readinto(fp)

    async def RunAsync(self):
        with tempfile.TemporaryFile() as fp:
            stream = await self.async_sharefile_client.download_file(max_concurrency=self.Arguments.parallel)
            await stream.readinto(fp)

    async def CloseAsync(self):
        await self.async_sharefile_client.close()
        await super().CloseAsync()

    @staticmethod
    def AddArguments(parser):
        super(DownloadToFileTest, DownloadToFileTest).AddArguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of files to download.  Default is 10240.', default=10240)
