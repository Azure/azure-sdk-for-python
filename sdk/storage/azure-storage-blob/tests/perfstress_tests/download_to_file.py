# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
from typing import Optional

from devtools_testutils.perfstress_tests import RandomStream

from ._test_base import _BlobTest

class DownloadToFileTest(_BlobTest):
    _temp_file: str = ""

    async def setup(self):
        await super().setup()
        data = RandomStream(self.args.size)
        await self.async_blob_client.upload_blob(data)
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self._temp_file = tf.name

    async def cleanup(self):
        if self._temp_file and os.path.exists(self._temp_file):
            os.remove(self._temp_file)
        await super().cleanup()

    def run_sync(self):
        with open(self._temp_file, 'wb') as f:
            stream = self.blob_client.download_blob(max_concurrency=self.args.max_concurrency)
            stream.readinto(f)

    async def run_async(self):
        with open(self._temp_file, 'wb') as f:
            stream = await self.async_blob_client.download_blob(max_concurrency=self.args.max_concurrency)
            await stream.readinto(f)
