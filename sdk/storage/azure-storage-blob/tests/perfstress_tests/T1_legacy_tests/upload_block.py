# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from devtools_testutils.perfstress_tests import get_random_bytes

from ._test_base_legacy import _LegacyContainerTest


class LegacyUploadBlockTest(_LegacyContainerTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.blob_name = "blobblocktest-" + str(uuid.uuid4())
        self.block_id = str(uuid.uuid4())
        self.data = get_random_bytes(self.args.size)

    def run_sync(self):
        self.service_client.put_block(
            container_name=self.container_name,
            blob_name=self.blob_name,
            block=self.data,
            block_id=self.block_id)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")
