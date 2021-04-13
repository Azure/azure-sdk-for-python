# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import itertools
import asyncio

from ._test_base import _ContainerTest


class ListBlobsTest(_ContainerTest):

    async def global_setup(self):
        await super().global_setup()
        pending = (asyncio.ensure_future(self.async_container_client.upload_blob("listtest" + str(i), data=b"")) for i in range(self.args.count))
        running = list(itertools.islice(pending, 16))
        while True:
            # Wait for some upload to finish before adding a new one
            done, running = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
            try:
                for _ in range(0, len(done)):
                    next_upload = next(pending)
                    running.add(next_upload)
            except StopIteration:
                if running:
                    await asyncio.wait(running, return_when=asyncio.ALL_COMPLETED)
                break

    def run_sync(self):
        for _ in self.container_client.list_blobs():
            pass

    async def run_async(self):
        async for _ in self.async_container_client.list_blobs():
            pass

    @staticmethod
    def add_arguments(parser):
        super(ListBlobsTest, ListBlobsTest).add_arguments(parser)
        parser.add_argument('-c', '--count', nargs='?', type=int, help='Number of blobs to list. Defaults to 100', default=100)
