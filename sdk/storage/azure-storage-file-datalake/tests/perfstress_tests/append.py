# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azure_devtools.perfstress_tests import get_random_bytes, RandomStream, AsyncRandomStream

from ._test_base import _FileSystemTest


class AppendTest(_FileSystemTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.size)
        file_name = "filetest-" + str(uuid.uuid4())
        self.file_client = self.fs_client.get_file_client(file_name)
        self.async_file_client = self.async_fs_client.get_file_client(file_name)

    async def setup(self):
        await self.async_file_client.create_file()

    def run_sync(self):
        data = RandomStream(self.args.size) if self.args.stream else self.data
        self.file_client.append_data(
            data,
            length=self.args.size,
            offset=0,
            max_concurrency=self.args.max_concurrency)

    async def run_async(self):
        data = AsyncRandomStream(self.args.size) if self.args.stream else self.data
        await self.async_file_client.append_data(
            data,
            length=self.args.size,
            offset=0,
            max_concurrency=self.args.max_concurrency)

    @staticmethod
    def add_arguments(parser):
        super(AppendTest, AppendTest).add_arguments(parser)
        parser.add_argument('--stream', action='store_true', help='Upload stream instead of byte array.', default=False)
