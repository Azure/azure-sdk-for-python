# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _FileTest

from devtools_testutils.perfstress_tests import RandomStream
from devtools_testutils.perfstress_tests import AsyncRandomStream


class UploadTest(_FileTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.upload_stream = RandomStream(self.args.size)
        self.upload_stream_async = AsyncRandomStream(self.args.size)

    def run_sync(self):
        self.upload_stream.reset()
        self.file_client.upload_data(
            self.upload_stream,
            length=self.args.size,
            overwrite=True,
            max_concurrency=self.args.max_concurrency)

    async def run_async(self):
        self.upload_stream_async.reset()
        await self.async_file_client.upload_data(
            self.upload_stream_async,
            length=self.args.size,
            overwrite=True,
            max_concurrency=self.args.max_concurrency)
