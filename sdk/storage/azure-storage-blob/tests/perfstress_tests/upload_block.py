# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid

from ._test_base import _BlobTest

from azure_devtools.perfstress_tests import get_random_bytes


class UploadBlockTest(_BlobTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.blob_name = "blobblocktest-" + str(uuid.uuid4())

    def run_sync(self):
        data = get_random_bytes(self.args.size)
        self.blob_client.stage_block(
            block_id=str(uuid.uuid4()),
            data=data)

    async def run_async(self):
        data = get_random_bytes(self.args.size)
        await self.async_blob_client.stage_block(
            block_id=str(uuid.uuid4()),
            data=data)
