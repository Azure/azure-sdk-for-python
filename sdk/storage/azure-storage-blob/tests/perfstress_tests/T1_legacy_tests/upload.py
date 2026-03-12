# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from devtools_testutils.perfstress_tests import RandomStream

from ._test_base_legacy import _LegacyContainerTest


class LegacyUploadTest(_LegacyContainerTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.blob_name = "blobtest-" + str(uuid.uuid4())
        self.upload_stream = RandomStream(self.args.size)
    
    def run_sync(self):
        self.upload_stream.reset()
        self.service_client.create_blob_from_stream(
            container_name=self.container_name,
            blob_name=self.blob_name,
            stream=self.upload_stream,
            max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")
