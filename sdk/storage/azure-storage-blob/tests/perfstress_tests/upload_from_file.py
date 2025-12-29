# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import shutil
import tempfile
from typing import Optional

from devtools_testutils.perfstress_tests import RandomStream

from ._test_base import _BlobTest


class UploadFromFileTest(_BlobTest):
    _temp_file: Optional[str] = None

    async def global_setup(self):
        await super().global_setup()
        data_stream = RandomStream(self.args.size)
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self._temp_file = tf.name
            shutil.copyfileobj(data_stream, tf)

    async def global_cleanup(self):
        if self._temp_file and os.path.exists(self._temp_file):
            os.remove(self._temp_file)
        await super().global_cleanup()

    def run_sync(self):
        with open(self._temp_file, 'rb') as fp:
            self.blob_client.upload_blob(fp, max_concurrency=self.args.max_concurrency, overwrite=True)

    async def run_async(self):
        with open(self._temp_file, 'rb') as fp:
            await self.async_blob_client.upload_blob(
                fp,
                max_concurrency=self.args.max_concurrency,
                overwrite=True)
