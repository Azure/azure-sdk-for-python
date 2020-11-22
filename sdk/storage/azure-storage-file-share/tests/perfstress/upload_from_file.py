# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile

from ._test_base import _FileTest


class UploadFromFileTest(_FileTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.temp_file = None
        self.data = b'a' * self.args.size

    async def global_setup(self):
        await super().global_setup()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            self.temp_file = temp_file.name
            temp_file.write(self.data)

    async def global_cleanup(self):
        os.remove(self.temp_file)
        await super().global_cleanup()

    def run_sync(self):
        with open(self.temp_file) as fp:
            self.sharefile_client.upload_file(fp)

    async def run_async(self):
        await self.async_sharefile_client.upload_file(self.temp_file)

    @staticmethod
    def add_arguments(parser):
        super(UploadFromFileTest, UploadFromFileTest).add_arguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of blobs to upload.  Default is 10240.', default=10240)
