# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import uuid

from devtools_testutils.perfstress_tests import get_random_bytes

from ._test_base import _LegacyShareTest


class LegacyUploadFromFileTest(_LegacyShareTest):
    temp_file = None

    def __init__(self, arguments):
        super().__init__(arguments)
        self.file_name = "sharefiletest-" + str(uuid.uuid4())

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            LegacyUploadFromFileTest.temp_file = temp_file.name
            temp_file.write(data)

    async def global_cleanup(self):
        os.remove(LegacyUploadFromFileTest.temp_file)
        await super().global_cleanup()

    def run_sync(self):
        self.service_client.create_file_from_path(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            local_file_path=LegacyUploadFromFileTest.temp_file,
            max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")
