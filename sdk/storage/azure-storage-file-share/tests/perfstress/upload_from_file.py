import os
import tempfile

from ._test_base import _FileTest

from azure_devtools.perfstress_tests import RandomStream
from azure_devtools.perfstress_tests import AsyncRandomStream


class UploadFromFileTest(_FileTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.temp_file = None
        self.data = b'a' * self.Arguments.size

    async def GlobalSetupAsync(self):
        await super().GlobalSetupAsync()
        self.temp_file = tempfile.TemporaryFile()
        self.temp_file.write(self.data)
        self.temp_file.seek(0)

    async def GlobalCleanupAsync(self):
        self.temp_file.close()
        await super().GlobalCleanupAsync()

    def Run(self):
        self.sharefile_client.upload_file(self.temp_file)

    async def RunAsync(self):
        await self.async_sharefile_client.upload_file(self.temp_file)

    @staticmethod
    def AddArguments(parser):
        super(UploadFromFileTest, UploadFromFileTest).AddArguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of blobs to upload.  Default is 10240.', default=10240)
        parser.add_argument('--stream', action='store_true', help='Upload stream instead of byte array.', default=False)
