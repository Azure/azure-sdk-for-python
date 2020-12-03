# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azure_devtools.perfstress_tests import RandomStream, get_random_bytes

from ._test_base_legacy import _LegacyShareTest


class LegacyUploadTest(_LegacyShareTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.file_name = "sharefiletest-" + str(uuid.uuid4())
        self.data = get_random_bytes(self.args.size)

    def run_sync(self):
        if self.args.stream:
            data = RandomStream(self.args.size)
            self.service_client.create_file_from_stream(
                share_name=self.share_name,
                directory_name=None,
                file_name=self.file_name,
                stream=data,
                max_connections=self.args.max_concurrency)
        else:
            self.service_client.create_file_from_bytes(
                share_name=self.share_name,
                directory_name=None,
                file_name=self.file_name,
                file=self.data,
                max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")

    @staticmethod
    def add_arguments(parser):
        super(LegacyUploadTest, LegacyUploadTest).add_arguments(parser)
        parser.add_argument('--stream', action='store_true', help='Upload stream instead of byte array.', default=False)
