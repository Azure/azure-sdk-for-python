# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import get_random_bytes

from ._test_base import _ContainerTest


class ListBlobsTest(_ContainerTest):

    async def global_setup(self):
        await super().global_setup()
        for i in range(self.args.num_blobs):
            await self.async_container_client.upload_blob("listtest" + str(i), data=b"")

    def run_sync(self):
        list(self.container_client.list_blobs())

    async def run_async(self):
        _ = [b async for b in self.async_container_client.list_blobs()]

    @staticmethod
    def add_arguments(parser):
        super(ListBlobsTest, ListBlobsTest).add_arguments(parser)
        parser.add_argument('--num-blobs', nargs='?', type=int, help='Number of blobs to list. Defaults to 100', default=100)
