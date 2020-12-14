# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azure_devtools.perfstress_tests import RandomStream, get_random_bytes

from ._test_base_legacy import _LegacyContainerTest


class LegacyUploadBlockTest(_LegacyContainerTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.blob_name = "blobblocktest-" + str(uuid.uuid4())

    def run_sync(self):
        self.service_client.put_block(
            container_name=self.container_name,
            blob_name=self.blob_name,
            block=get_random_bytes(self.args.size),
            block_id=str(uuid.uuid4()))

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")
