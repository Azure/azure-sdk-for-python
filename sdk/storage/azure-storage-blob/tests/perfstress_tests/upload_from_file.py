# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile

from azure_devtools.perfstress_tests import get_random_bytes

from ._test_base import _BlobTest


class UploadFromFileTest(_BlobTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.temp_file = None
        self.data = get_random_bytes(self.args.size)

    async def global_setup(self):
        await super().global_setup()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            self.temp_file = temp_file.name
            temp_file.write(self.data)

    async def global_cleanup(self):
        os.remove(self.temp_file)
        await super().global_cleanup()

    def run_sync(self):
        with open(self.temp_file) as fp:
            self.blob_client.upload_blob(fp, max_concurrency=self.args.max_concurrency)

    async def run_async(self):
        with open(self.temp_file) as fp:
            await self.async_blob_client.upload_blob(fp, max_concurrency=self.args.max_concurrency)
