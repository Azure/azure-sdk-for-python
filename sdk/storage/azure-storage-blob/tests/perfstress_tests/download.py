# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from devtools_testutils.perfstress_tests import RandomStream, WriteStream

from ._test_base import _BlobTest


class DownloadTest(_BlobTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.download_stream = WriteStream()

    async def setup(self):
        await super().setup()
        data = RandomStream(self.args.size)
        await self.async_blob_client.upload_blob(data)

    def run_sync(self):
        self.download_stream.reset()
        stream = self.blob_client.download_blob(max_concurrency=self.args.max_concurrency)
        stream.readinto(self.download_stream)

    async def run_async(self):
        self.download_stream.reset()
        stream = await self.async_blob_client.download_blob(max_concurrency=self.args.max_concurrency)
        await stream.readinto(self.download_stream)
