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
        self.upload_stream = RandomStream(self.args.size)
        self.upload_stream_async = AsyncRandomStream(self.args.size)

    def run_sync(self):
        self.upload_stream.reset()
        self.sharefile_client.upload_file(
            self.upload_stream,
            length=self.args.size,
            max_concurrency=self.args.max_concurrency)

    async def run_async(self):
        self.upload_stream_async.reset()
        await self.async_sharefile_client.upload_file(
            self.upload_stream_async,
            length=self.args.size,
            max_concurrency=self.args.max_concurrency)
