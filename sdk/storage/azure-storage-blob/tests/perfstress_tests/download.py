# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import get_random_bytes, WriteStream

from ._test_base import _ContainerTest


class DownloadTest(_ContainerTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        blob_name = "downloadtest"
        self.blob_client = self.container_client.get_blob_client(blob_name)
        self.async_blob_client = self.async_container_client.get_blob_client(blob_name)
        self.download_stream = WriteStream()

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        await self.async_blob_client.upload_blob(data)

    def run_sync(self):
        self.download_stream.reset()
        stream = self.blob_client.download_blob(max_concurrency=self.args.max_concurrency)
        stream.readinto(self.download_stream)

    async def run_async(self):
        self.download_stream.reset()
        stream = await self.async_blob_client.download_blob(max_concurrency=self.args.max_concurrency)
        await stream.readinto(self.download_stream)

    async def close(self):
        await self.async_blob_client.close()
        await super().close()
