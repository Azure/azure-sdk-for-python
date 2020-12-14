# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _BlobTest

from azure_devtools.perfstress_tests import RandomStream, get_random_bytes
from azure_devtools.perfstress_tests import AsyncRandomStream


class UploadTest(_BlobTest):

    def run_sync(self):
        data = RandomStream(self.args.size)
        self.blob_client.upload_blob(
            data,
            length=self.args.size,
            overwrite=True,
            max_concurrency=self.args.max_concurrency)

    async def run_async(self):
        data = AsyncRandomStream(self.args.size)
        await self.async_blob_client.upload_blob(
            data,
            length=self.args.size,
            overwrite=True,
            max_concurrency=self.args.max_concurrency)
