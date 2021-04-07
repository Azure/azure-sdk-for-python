# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base_legacy import _LegacyContainerTest


class LegacyListBlobsTest(_LegacyContainerTest):

    async def global_setup(self):
        await super().global_setup()
        for i in range(self.args.count):
            self.service_client.create_blob_from_bytes(
                container_name=self.container_name,
                blob_name="listtest" + str(i),
                blob=b"")

    def run_sync(self):
        for _ in self.service_client.list_blobs(container_name=self.container_name):
            pass

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")

    @staticmethod
    def add_arguments(parser):
        super(LegacyListBlobsTest, LegacyListBlobsTest).add_arguments(parser)
        parser.add_argument('-c', '--count', nargs='?', type=int, help='Number of blobs to list. Defaults to 100', default=100)
