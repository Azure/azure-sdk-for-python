import os

from ._test_base import _FileTest

from azure_devtools.perfstress_tests import RandomStream
from azure_devtools.perfstress_tests import AsyncRandomStream


class UploadTest(_FileTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = b'a' * self.Arguments.size

    def Run(self):
        data = RandomStream(self.Arguments.size) if self.Arguments.stream else self.data
        self.sharefile_client.upload_file(data, length=self.Arguments.size)

    async def RunAsync(self):
        data = AsyncRandomStream(self.Arguments.size) if self.Arguments.stream else self.data
        await self.async_sharefile_client.upload_file(data, length=self.Arguments.size)

    @staticmethod
    def AddArguments(parser):
        super(UploadTest, UploadTest).AddArguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of blobs to upload.  Default is 10240.', default=10240)
        parser.add_argument('--stream', action='store_true', help='Upload stream instead of byte array.', default=False)
