# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import uuid

from ._test_base_legacy import _LegacyShareTest


class LegacyUploadFromFileTest(_LegacyShareTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.file_name = "sharefiletest-" + str(uuid.uuid4())
        self.data = b'a' * self.Arguments.size

    async def GlobalSetupAsync(self):
        await super().GlobalSetupAsync()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            self.temp_file = temp_file.name
            temp_file.write(self.data)

    async def GlobalCleanupAsync(self):
        os.remove(self.temp_file)
        await super().GlobalCleanupAsync()

    def Run(self):
        self.service_client.create_file_from_path(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            local_file_path=self.temp_file)

    async def RunAsync(self):
        raise NotImplementedError("Async not supported for legacy tests.")

    @staticmethod
    def AddArguments(parser):
        super(LegacyUploadFromFileTest, LegacyUploadFromFileTest).AddArguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of blobs to upload.  Default is 10240.', default=10240)
        parser.add_argument('--stream', action='store_true', help='Upload stream instead of byte array.', default=False)
