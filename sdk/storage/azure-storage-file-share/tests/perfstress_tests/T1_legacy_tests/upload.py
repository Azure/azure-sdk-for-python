# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from devtools_testutils.perfstress_tests import RandomStream, get_random_bytes

from ._test_base import _LegacyShareTest


class LegacyUploadTest(_LegacyShareTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.file_name = "sharefiletest-" + str(uuid.uuid4())
        self.upload_stream = RandomStream(self.args.size)

    def run_sync(self):
        self.upload_stream.reset()
        self.service_client.create_file_from_stream(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            stream=self.upload_stream,
            count=self.args.size,
            max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")
