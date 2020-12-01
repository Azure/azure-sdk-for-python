# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _FileTest

from azure_devtools.perfstress_tests import RandomStream, get_random_bytes
from azure_devtools.perfstress_tests import AsyncRandomStream


class UploadTest(_FileTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.size)

    def run_sync(self):
        data = RandomStream(self.args.size) if self.args.stream else self.data
        self.sharefile_client.upload_file(
            data,
            length=self.args.size,
            max_concurrency=self.args.max_concurrency)

    async def run_async(self):
        data = AsyncRandomStream(self.args.size) if self.args.stream else self.data
        await self.async_sharefile_client.upload_file(
            data,
            length=self.args.size,
            max_concurrency=self.args.max_concurrency)

    @staticmethod
    def add_arguments(parser):
        super(UploadTest, UploadTest).add_arguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of blobs to upload.  Default is 10240.', default=10240)
        parser.add_argument('--stream', action='store_true', help='Upload stream instead of byte array.', default=False)
