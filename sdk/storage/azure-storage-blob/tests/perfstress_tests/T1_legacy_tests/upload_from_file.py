# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import uuid

from azure_devtools.perfstress_tests import get_random_bytes

from ._test_base_legacy import _LegacyContainerTest


class LegacyUploadFromFileTest(_LegacyContainerTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.blob_name = "containertest-" + str(uuid.uuid4())
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
        self.service_client.create_blob_from_path(
            container_name=self.container_name,
            blob_name=self.blob_name,
            file_path=self.temp_file,
            max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")
